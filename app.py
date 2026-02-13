import streamlit as st
import xml.etree.ElementTree as ET
import os
import re
from collections import defaultdict

# --- 1. 화면 설정 ---
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")

st.markdown("""
<style>
    .header { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
    .card { padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #ccc; background-color: #f9f9f9; }
    .male-card { border-left-color: #2b6cb0; }
    .female-card { border-left-color: #d53f8c; }
    .main-text { font-size: 1.1em; font-weight: bold; color: #333; }
    .sub-text { font-size: 0.9em; color: #666; margin-top: 5px; }
    .highlight { color: #c53030; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 분석기 (최종 강화형)")

# --- 2. 데이터 로딩 ---
file_path = 'data.mm'
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml_content = f.read()
    root = ET.fromstring(xml_content)
except Exception as e:
    st.error(f"데이터 로드 오류: {e}")
    st.stop()

# --- 3. 데이터 분석 ---
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

# --- 4. 강력한 이름 정제 함수 ---
def super_clean(text):
    # 대소문자 무시, 공백 무시, 모든 특수기호(', -, @, #, *, 암), 수)) 제거
    # 오직 순수한 '글자'와 '숫자'만 남깁니다.
    return re.sub(r'[^a-zA-Z0-9가-힣]', '', text).lower()

# --- 5. 검색창 구현 ---
st.write("### 🔎 스마트 검색")
st.info("💡 철자 일부만 입력해도 기호나 따옴표를 무시하고 찾아줍니다.")

query_input = st.text_input("마명 입력 (예: unbridled, medagl, prospector)", "").strip()

if query_input:
    clean_query = super_clean(query_input)
    
    # 정제된 이름끼리 비교하여 일치하는 목록 추출
    matched_names = []
    for name in sorted(list(all_horse_names)):
        if clean_query in super_clean(name):
            matched_names.append(name)
            
    if not matched_names:
        st.warning(f"❌ '{query_input}' 검색 결과가 없습니다.")
    else:
        # 검색된 결과 선택박스
        selected_name = st.selectbox(f"🔍 {len(matched_names)}마리 발견! 아래 목록에서 선택하세요:", matched_names)
        
        target_id = [nid for nid, info in nodes.items() if info['name'] == selected_name][0]
        
        # 자마 분석 실행
        colts = []; fillies = []; seen = set()
        children = [nid for nid, info in nodes.items() if info['parent'] == target_id]
        
        for c_id in children:
            if c_id in seen: continue
            info = nodes[c_id]; name = info['name']; is_female = '암)' in name
            if not is_female:
                if c_id in arrows_in:
                    for m_id in arrows_in[c_id]:
                        if m_id in nodes:
                            bms = nodes[nodes[m_id]['parent']]['name'] if nodes[m_id]['parent'] in nodes else "?"
                            colts.append({'child': name, 'bms': bms, 'mom': nodes[m_id]['name']})
                            seen.add(c_id)
            else:
                if c_id in arrows_out:
                    for f_id in arrows_out[c_id]:
                        if f_id in nodes:
                            sire = nodes[nodes[f_id]['parent']]['name'] if nodes[f_id]['parent'] in nodes else "?"
                            fillies.append({'child': name, 'sire': sire, 'foal': nodes[f_id]['name']})
                            seen.add(c_id)

        st.success(f"✅ **{selected_name}** 분석 결과")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### 🟦 수말 자마 (Sons: {len(colts)})")
            for c in colts:
                st.markdown(f"<div class='card male-card'><div class='main-text'>🐎 {c['child']}</div><div class='sub-text'>어미: {c['mom']}<br>👉 <b>BMS: <span class='highlight'>{c['bms']}</span></b></div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"### 🩷 암말 자마 (Daughters: {len(fillies)})")
            for f in fillies:
                st.markdown(f"<div class='card female-card'><div class='main-text'>🎀 {f['child']}</div><div class='sub-text'>자마: {f['foal']}<br>👉 <b>Sire: <span class='highlight'>{f['sire']}</span></b></div></div>", unsafe_allow_html=True)
