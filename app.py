import streamlit as st
import xml.etree.ElementTree as ET
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")

st.markdown("""
<style>
    .card { padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #ccc; background-color: #f9f9f9; }
    .male-card { border-left-color: #2b6cb0; }
    .female-card { border-left-color: #d53f8c; }
    .main-text { font-size: 1.1em; font-weight: bold; }
    .highlight { color: #c53030; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 분석기 (대소문자 무시 완성형)")

# --- 2. 데이터 로딩 ---
file_path = 'data.mm'

@st.cache_data
def get_cleaned_data(path):
    if not os.path.exists(path): return None, "파일을 찾을 수 없습니다."
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            tree = ET.parse(f)
        root = tree.getroot()
        nodes = {}; in_arr = {}; out_arr = {}
        for node in root.iter('node'):
            nid = node.get('ID'); text = node.get('TEXT', '').strip()
            if nid:
                nodes[nid] = {'name': text}
                for arrow in node.findall('arrowlink'):
                    dest = arrow.get('DESTINATION')
                    if dest:
                        out_arr.setdefault(nid, []).append(dest)
                        in_arr.setdefault(dest, []).append(nid)
        for parent in root.iter('node'):
            pid = parent.get('ID')
            for child in parent.findall('node'):
                cid = child.get('ID')
                if cid in nodes: nodes[cid]['parent'] = pid
        return nodes, in_arr, out_arr
    except Exception as e: return None, str(e)

nodes, in_arr, out_arr = get_cleaned_data(file_path)

if nodes is None:
    st.error(f"❌ 데이터 오류: {in_arr}")
    st.stop()

# --- 3. 검색 로직 (대소문자/기호 100% 무시) ---
def make_pure(text):
    # 알파벳과 한글만 남기고 모두 소문자로 변환 (대소문자 구분 없애기)
    return "".join([char.lower() for char in text if char.isalnum() or '가' <= char <= '힣'])

st.write("### 🔎 씨수말 통합 검색")
query_raw = st.text_input("마명을 입력하세요 (예: pulpit, unbridled, medaglia):", "").strip()

if query_raw:
    q = make_pure(query_raw)
    # 파일 내 모든 마명을 정제해서 비교
    matched = [name for nid, info in nodes.items() if (name := info['name']) and q in make_pure(name) and len(name) > 1]
    
    if not matched:
        st.warning(f"❌ '{query_raw}' 검색 결과가 없습니다.")
    else:
        # 중복 제거 후 가나다순 정렬
        final_list = sorted(list(set(matched)))
        selected = st.selectbox(f"🔍 {len(final_list)}마리 발견! 아래에서 선택하세요:", final_list)
        
        # 분석 실행
        t_id = next(nid for nid, info in nodes.items() if info['name'] == selected)
        colts = []; fillies = []
        c_ids = [nid for nid, info in nodes.items() if info.get('parent') == t_id]
        
        for cid in c_ids:
            c_name = nodes[cid]['name']; is_f = '암)' in c_name
            if not is_f: # 수말 (BMS)
                for m_id in in_arr.get(cid, []):
                    mom = nodes.get(m_id)
                    if mom and mom.get('parent') in nodes:
                        colts.append({"n": c_name, "b": nodes[mom['parent']]['name'], "m": mom['name']})
            else: # 암말 (Sire)
                for f_id in out_arr.get(cid, []):
                    foal = nodes.get(f_id)
                    if foal and foal.get('parent') in nodes:
                        fillies.append({"n": c_name, "s": nodes[foal['parent']]['name'], "f": foal['name']})

        st.success(f"✅ {selected} 분석 완료")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🟦 수말 (Sons)")
            for c in colts: st.info(f"🐎 **{c['n']}**\n\nBMS: {c['b']} (어미: {c['m']})")
        with col2:
            st.markdown("#### 🩷 암말 (Daughters)")
            for f in fillies: st.error(f"🎀 **{f['n']}**\n\nSire: {f['s']} (자마: {f['f']})")
