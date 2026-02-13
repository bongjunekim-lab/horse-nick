import streamlit as st
import xml.etree.ElementTree as ET
import os
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

st.title("🐎 씨수말 닉(Nick) 분석기")

# --- 2. 데이터 로딩 ---
file_path = 'data.mm'
if not os.path.exists(file_path):
    st.error("🚨 'data.mm' 파일이 없습니다.")
    st.stop()

try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml_content = f.read()
    root = ET.fromstring(xml_content)
except Exception as e:
    st.error(f"❌ 데이터 읽기 오류: {e}")
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

# --- 4. 스마트 검색창 (여기가 핵심) ---
st.write("### 🔎 씨수말 검색")
search_input = st.text_input("말 이름의 일부를 입력하세요 (예: bernardini 또는 ber)", "").strip()

if search_input:
    # ★ 대소문자 가리지 않고 이름 중간에 글자가 포함되면 다 찾기
    matched_names = [name for name in sorted(list(all_horse_names)) if search_input.lower() in name.lower()]
    
    if not matched_names:
        st.warning(f"❌ '{search_input}'이(가) 포함된 이름을 찾을 수 없습니다.")
    else:
        # 검색된 결과가 있으면 선택박스로 보여주기
        selected_name = st.selectbox(f"🔍 {len(matched_names)}마리가 검색되었습니다. 아래에서 선택하세요:", matched_names)
        
        # 선택된 말 분석 시작
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
                            colts.append({'child': name, 'bms': bms_name, 'link_info': nodes[mom_id]['name']})
                            seen.add(child_id)
            else:
                if child_id in arrows_out:
                    for foal_id in arrows_out[child_id]:
                        if foal_id in nodes:
                            partner_id = nodes[foal_id]['parent']
                            partner_name = nodes[partner_id]['name'] if partner_id in nodes else "?"
                            fillies.append({'child': name, 'partner': partner_name, 'link_info': nodes[foal_id]['name']})
                            seen.add(child_id)
        
        st.success(f"✅ **{selected_name}** 분석 결과")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='header' style='color:#2b6cb0;'>🟦 수말 자마 (Sons: {len(colts)})</div>", unsafe_allow_html=True)
            for c in colts:
                st.markdown(f"<div class='card male-card'><div class='main-text'>🐎 {c['child']}</div><div class='sub-text'>어미: {c['link_info']}<br>👉 <b>BMS: <span class='highlight'>{c['bms']}</span></b></div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='header' style='color:#d53f8c;'>🩷 암말 자마 (Daughters: {len(fillies)})</div>", unsafe_allow_html=True)
            for f in fillies:
                st.markdown(f"<div class='card female-card'><div class='main-text'>🎀 {f['child']}</div><div class='sub-text'>자마: {f['link_info']}<br>👉 <b>Sire: <span class='highlight'>{f['partner']}</span></b></div></div>", unsafe_allow_html=True)
