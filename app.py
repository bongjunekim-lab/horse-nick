import streamlit as st
import xml.etree.ElementTree as ET
import os
import re
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

st.title("🐎 씨수말 닉(Nick) 분석기 (심도 검색 통합본)")

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

# --- 4. ★핵심: 대소문자/기호 완전 무시 함수 ---
def get_search_key(text):
    # 모든 특수기호, 공백, 숫자를 제거하고 순수 글자만 소문자로 반환
    return re.sub(r'[^a-zA-Z가-힣]', '', text).lower()

# --- 5. 검색창 구현 ---
st.write("### 🔎 심도 검색창")
st.info("💡 이제 대소문자나 따옴표 상관없이 **소문자로 이름만** 입력하세요.")

query_input = st.text_input("마명 입력 (예: medaglia, unbridled, pulpit, tiznow)", "").strip()

if query_input:
    # 사용자 입력값도 알맹이만 추출
    clean_query = get_search_key(query_input)
    
    # 알맹이 비교로 검색
    matched_names = []
    if clean_query:
        for name in sorted(list(all_horse_names)):
            if clean_query in get_search_key(name):
                matched_names.append(name)
            
    if not matched_names:
        st.warning(f"❌ '{query_input}' 검색 결과가 없습니다.")
    else:
        # 검색된 결과 선택
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
                            bms = nodes[nodes[mom_id]['parent']]['name'] if nodes[m_id]['parent'] in nodes else "?"
                            colts.append({'child': name, 'bms': bms, 'mom': nodes[mom_id]['name']})
                            seen.add(child_id)
            else:
                if child_id in arrows_out:
                    for foal_id in arrows_out[child_id]:
                        if foal_id in nodes:
                            sire = nodes[nodes[foal_id]['parent']]['name'] if nodes[f_id]['parent'] in nodes else "?"
                            fillies.append({'child': name, 'sire': sire, 'foal': nodes[foal_id]['name']})
                            seen.add(child_id)

        st.success(f"✅ **{selected_name}** 분석 완료")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### 🟦 수말 자마 (Sons)")
            for c in colts:
                st.markdown(f"<div class='card male-card'><div class='main-text'>🐎 {c['child']}</div><div class='sub-text'>BMS: <span class='highlight'>{c['bms']}</span></div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"### 🩷 암말 자마 (Daughters)")
            for f in fillies:
                st.markdown(f"<div class='card female-card'><div class='main-text'>🎀 {f['child']}</div><div class='sub-text'>Sire: <span class='highlight'>{f['sire']}</span></div></div>", unsafe_allow_html=True)
