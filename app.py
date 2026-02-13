import streamlit as st
import xml.etree.ElementTree as ET
import os
import re
from collections import defaultdict

st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")
st.title("🐎 씨수말 닉(Nick) 분석기 (심도 검색 버전)")

# --- 데이터 로드 ---
file_path = 'data.mm'
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml_content = f.read()
    root = ET.fromstring(xml_content)
except Exception as e:
    st.error(f"파일 로드 오류: {e}")
    st.stop()

# --- 데이터 파싱 ---
nodes = {}; arrows_in = defaultdict(list); arrows_out = defaultdict(list)
all_names = set()

def parse(node, parent_id=None):
    nid = node.get('ID'); text = node.get('TEXT', '').strip()
    if nid:
        nodes[nid] = {'name': text, 'parent': parent_id}
        if len(text) > 1: all_names.add(text)
        for arrow in node.findall('arrowlink'):
            dest = arrow.get('DESTINATION')
            if dest: arrows_out[nid].append(dest); arrows_in[dest].append(nid)
    for child in node.findall('node'): parse(child, nid)
parse(root)

# --- 🔍 핵심: 마명 정제 함수 ---
def get_clean_name(text):
    # 1. 앞부분의 모든 특수기호(-, @, #, *, 공백 등) 제거
    text = re.sub(r'^[^a-zA-Z0-9가-힣]+', '', text)
    # 2. 성별 표시(암), 수), 거)) 제거
    text = re.sub(r'^(암|수|거)\)\s*', '', text)
    # 3. 비교를 위해 소문자 변환 및 특수문자(') 제거
    return re.sub(r'[^a-zA-Z0-9가-힣]', '', text).lower()

# --- 화면 구현 ---
st.write("### 🔎 스마트 검색")
st.info("기호나 성별 표시(암, 수)를 제외한 **이름만** 입력하세요.")

query = st.text_input("마명 입력 (예: bernardini, medaglia, unbridled)", "").strip()

if query:
    clean_query = re.sub(r'[^a-zA-Z0-9가-힣]', '', query).lower()
    # 정제된 이름과 검색어 비교
    matched_results = [name for name in all_names if clean_query in get_clean_name(name)]
    
    if not matched_results:
        st.warning(f"❌ '{query}'와 일치하는 말을 찾을 수 없습니다.")
    else:
        # 검색된 결과 중 선택
        selected = st.selectbox(f"🔍 {len(matched_results)}마리 발견! 정확한 이름을 선택하세요:", sorted(matched_results))
        
        # 분석 로직 실행
        target_id = [nid for nid, info in nodes.items() if info['name'] == selected][0]
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

        st.success(f"✅ **{selected}** 분석 결과")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🟦 수말 (Sons)")
            for c in colts: st.info(f"🐎 {c['child']}\n\n어미: {c['mom']} / BMS: {c['bms']}")
        with c2:
            st.markdown("### 🩷 암말 (Daughters)")
            for f in fillies: st.error(f"🎀 {f['child']}\n\n자마: {f['foal']} / Sire: {f['sire']}")
