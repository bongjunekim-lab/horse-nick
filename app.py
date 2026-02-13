import streamlit as st
import xml.etree.ElementTree as ET
import os
from collections import defaultdict

# --- 1. 화면 설정 ---
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

st.title("🐎 씨수말 닉(Nick) 분석기 (대소문자 완전 무시 버전)")

# --- 2. 데이터 로딩 ---
file_path = 'data.mm'
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml_content = f.read()
    root = ET.fromstring(xml_content)
except Exception as e:
    st.error(f"데이터 파일 오류: {e}")
    st.stop()

# --- 3. 데이터 파싱 ---
nodes = {}; arrows_in = defaultdict(list); arrows_out = defaultdict(list)
all_horse_names = set()

def parse(node, parent_id=None):
    nid = node.get('ID'); text = node.get('TEXT', '').strip()
    if nid:
        nodes[nid] = {'name': text, 'parent': parent_id}
        if len(text) > 1: all_horse_names.add(text)
        for arrow in node.findall('arrowlink'):
            dest = arrow.get('DESTINATION')
            if dest: arrows_out[nid].append(dest); arrows_in[dest].append(nid)
    for child in node.findall('node'): parse(child, nid)
parse(root)

# --- 4. ★ 초강력 알맹이 추출 함수 (정규식 미사용) ---
def make_pure_key(text):
    """
    모든 기호, 공백, 따옴표를 버리고 
    오직 영문(소문자화)과 한글, 숫자만 남겨서 반환합니다.
    """
    pure = ""
    for char in text:
        if char.isalnum(): # 알파벳 또는 숫자인가?
            pure += char.lower()
    return pure

# --- 5. 검색창 구현 ---
st.write("### 🔎 통합 검색")
st.warning("이제 'medagl', 'pulpit', 'tiznow' 등 **무조건 소문자**로만 입력해보세요.")

query_input = st.text_input("마명 입력", "").strip()

if query_input:
    # 사용자 입력값 정제
    clean_query = make_pure_key(query_input)
    
    # 알맹이 비교로 검색 수행
    matched_names = []
    if clean_query:
        for name in sorted(list(all_horse_names)):
            # 파일 내 마명도 정제하여 비교
            if clean_query in make_pure_key(name):
                matched_names.append(name)
            
    if not matched_names:
        st.error(f"❌ '{query_input}' 검색 결과가 없습니다. (정제 키: {clean_query})")
    else:
        selected_name = st.selectbox(f"🔍 {len(matched_names)}마리 발견! 정확한 마명을 선택하세요:", matched_names)
        
        # 분석 실행
        target_ids = [nid for nid, info in nodes.items() if info['name'] == selected_name]
        sire_id = target_ids[0]
        
        colts = []; fillies = []; seen = set()
        children = [nid for nid, info in nodes.items() if info['parent'] == sire_id]
        
        for child_id in children:
            if child_id in seen: continue
            info = nodes[child_id]; name = info['name']; is_female = '암)' in name
            if not is_female:
                if child_id in arrows_in:
                    for mom_id in arrows_in[child_id]:
                        if mom_id in nodes:
                            bms_id = nodes[mom_id]['parent']
                            bms_name = nodes[bms_id]['name'] if bms_id in nodes else "?"
                            colts.append({'child': name, 'bms': bms_name, 'mom': nodes[mom_id]['name']})
                            seen.add(child_id)
            else:
                if child_id in arrows_out:
                    for foal_id in arrows_out[child_id]:
                        if foal_id in nodes:
                            partner_id = nodes[foal_id]['parent']
                            partner_name = nodes[partner_id]['name'] if partner_id in nodes else "?"
                            fillies.append({'child': name, 'sire': partner_name, 'foal': nodes[foal_id]['name']})
                            seen.add(child_id)

        st.success(f"✅ **{selected_name}** 분석 완료")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### 🟦 수말 자마 (Sons)")
            for c in colts:
                st.markdown(f"<div class='card male-card'><div class='main-text'>🐎 {c['child']}</div><div class='sub-text'>BMS: <span class='highlight'>{c['bms']}</span> (어미: {c['mom']})</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"### 🩷 암말 자마 (Daughters)")
            for f in fillies:
                st.markdown(f"<div class='card female-card'><div class='main-text'>🎀 {f['child']}</div><div class='sub-text'>Sire: <span class='highlight'>{f['sire']}</span> (자마: {f['foal']})</div></div>", unsafe_allow_html=True)
