import streamlit as st
import xml.etree.ElementTree as ET
import os
import re

# --- 1. 페이지 설정 및 캐시 삭제 ---
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")

# 이전 검색 결과가 남지 않도록 세션 상태 초기화
if 'search_reset' not in st.session_state:
    st.cache_data.clear()
    st.session_state['search_reset'] = True

st.title("🐎 씨수말 닉(Nick) 분석기 (최종 동기화)")

# --- 2. 데이터 로딩 ---
file_path = 'data.mm'
if not os.path.exists(file_path):
    st.error("🚨 data.mm 파일을 찾을 수 없습니다.")
    st.stop()

@st.cache_data
def load_and_parse_data(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            tree = ET.parse(f)
        root = tree.getroot()
        
        nodes = {}
        arrows_in = {}
        arrows_out = {}
        
        # 모든 노드 순회
        for node in root.iter('node'):
            nid = node.get('ID')
            text = node.get('TEXT', '').strip()
            if nid:
                nodes[nid] = {'name': text}
                # 화살표 정보 추출
                for arrow in node.findall('arrowlink'):
                    dest = arrow.get('DESTINATION')
                    if dest:
                        if nid not in arrows_out: arrows_out[nid] = []
                        arrows_out[nid].append(dest)
                        if dest not in arrows_in: arrows_in[dest] = []
                        arrows_in[dest].append(nid)
        
        # 부모-자식 관계 설정
        for parent in root.iter('node'):
            pid = parent.get('ID')
            for child in parent.findall('node'):
                cid = child.get('ID')
                if cid in nodes:
                    nodes[cid]['parent'] = pid
                    
        return nodes, arrows_in, arrows_out
    except Exception as e:
        return None, str(e), None

nodes, arrows_in, arrows_out = load_and_parse_data(file_path)

if nodes is None:
    st.error(f"❌ 데이터 로딩 실패: {arrows_in}")
    st.stop()

# --- 3. 검색 엔진 (강력한 소문자 비교) ---
st.write("### 🔎 통합 검색")
st.info("💡 이제 대문자를 섞지 말고 **소문자로만** 입력해 보세요 (예: pulpit, medaglia, unbridled)")

# 검색어 입력 (캐시 방지를 위해 고유 key 사용)
query_raw = st.text_input("씨수말 이름 입력:", key="horse_search_input").strip()

if query_raw:
    # 비교를 위해 입력값을 소문자로 변환 및 공백 제거
    q = re.sub(r'[^a-zA-Z0-9가-힣]', '', query_raw).lower()
    
    matched_list = []
    for nid, info in nodes.items():
        original_name = info['name']
        # 파일 내 이름도 동일한 방식으로 정제하여 비교
        target = re.sub(r'[^a-zA-Z0-9가-힣]', '', original_name).lower()
        
        if q in target and len(original_name) > 1:
            if original_name not in matched_list:
                matched_list.append(original_name)
    
    if not matched_list:
        st.warning(f"❌ '{query_raw}' 검색 결과가 없습니다.")
    else:
        # 검색 결과 선택박스
        selected_name = st.selectbox(
            f"🔍 {len(matched_list)}마리 발견! 정확한 마명을 선택하세요:", 
            sorted(matched_list),
            key="selected_horse"
        )
        
        # 분석 실행
        target_nid = next(nid for nid, info in nodes.items() if info['name'] == selected_name)
        
        colts = []; fillies = []
        # 자식 노드 찾기
        children_ids = [nid for nid, info in nodes.items() if info.get('parent') == target_nid]
        
        for cid in children_ids:
            c_name = nodes[cid]['name']
            is_female = '암)' in c_name
            
            if not is_female: # 수말 (BMS 분석)
                if cid in arrows_in:
                    for mom_id in arrows_in[cid]:
                        mom_node = nodes.get(mom_id)
                        if mom_node:
                            bms_id = mom_node.get('parent')
                            bms_name = nodes[bms_id]['name'] if bms_id in nodes else "알 수 없음"
                            colts.append({"child": c_name, "bms": bms_name, "mom": mom_node['name']})
            else: # 암말 (Sire 분석)
                if cid in arrows_out:
                    for foal_id in arrows_out[cid]:
                        foal_node = nodes.get(foal_id)
                        if foal_node:
                            sire_id = foal_node.get('parent')
                            sire_name = nodes[sire_id]['name'] if sire_id in nodes else "알 수 없음"
                            fillies.append({"child": c_name, "sire": sire_name, "foal": foal_node['name']})

        # 결과 표시
        st.success(f"✅ {selected_name} 분석 결과")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🟦 수말 (Sons)")
            for c in colts:
                st.info(f"🐎 **{c['child']}**\n\nBMS: {c['bms']} (어미: {c['mom']})")
        with c2:
            st.markdown("### 🩷 암말 (Daughters)")
            for f in fillies:
                st.error(f"🎀 **{f['child']}**\n\nSire: {f['sire']} (자마: {f['foal']})")
