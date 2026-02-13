import streamlit as st
import xml.etree.ElementTree as ET
import os
from collections import defaultdict

# --- 1. 페이지 설정 ---
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
st.write("분석하고 싶은 **씨수말 이름**을 입력하세요.")

# --- 2. 데이터 로딩 (조용히 실행) ---
file_path = 'data.mm'

if not os.path.exists(file_path):
    st.error("🚨 데이터 파일(data.mm)이 없습니다.")
    st.stop()

try:
    # 특수문자 깨짐 방지하며 읽기
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml_content = f.read()
    root = ET.fromstring(xml_content)
except Exception as e:
    st.error(f"❌ 데이터 읽기 오류: {e}")
    st.stop()

# --- 3. 데이터 분석 ---
nodes = {}
arrows_in = defaultdict(list)
arrows_out = defaultdict(list)

def parse(node, parent_id=None):
    nid = node.get('ID')
    text = node.get('TEXT', '').strip()
    if nid:
        nodes[nid] = {'name': text, 'parent': parent_id}
        for arrow in node.findall('arrowlink'):
            dest = arrow.get('DESTINATION')
            if dest:
                arrows_out[nid].append(dest)
                arrows_in[dest].append(nid)
    for child in node.findall('node'):
        parse(child, nid)

parse(root)

# --- 4. 검색 및 결과 표시 ---
query = st.text_input("이름 입력 (예: Bernardini)", "")

if query:
    # ★ 스마트 검색: 대소문자 구분 없이, 이름의 일부만 맞아도 찾습니다!
    # 예: 'bernardini'라고 쳐도 '- - Bernardini 2003'을 찾아냅니다.
    target_ids = [nid for nid, info in nodes.items() if query.lower() in info['name'].lower()]
    
    if not target_ids:
        st.warning(f"❌ '{query}' 검색 결과가 없습니다.")
    else:
        # 검색된 말이 여러 마리일 경우 선택박스 표시 (가장 깔끔한 방법)
        found_names = [nodes[nid]['name'] for nid in target_ids]
        
        # 중복 제거 및 정렬
        found_names = sorted(list(set(found_names)))
        
        selected_name = st.selectbox(f"검색된 말 {len(found_names)}마리 중 선택하세요:", found_names)
        
        # 선택한 말의 ID 찾기 (첫 번째 일치하는 ID 사용)
        selected_id = next(nid for nid, info in nodes.items() if info['name'] == selected_name)
        
        # 자마 분석 로직
        colts = []; fillies = []; seen = set()
        children = [nid for nid, info in nodes.items() if info['parent'] == selected_id]
        
        for child_id in children:
            if child_id in seen: continue
            info = nodes[child_id]; name = info['name']; is_female = '암)' in name
            
            if not is_female: # 수말
                if child_id in arrows_in:
                    for mom_id in arrows_in[child_id]:
                        if mom_id in nodes:
                            bms_id = nodes[mom_id]['parent']
                            bms_name = nodes[bms_id]['name'] if bms_id in nodes else "?"
                            colts.append({'child': name, 'bms': bms_name, 'link_info': nodes[mom_id]['name']})
                            seen.add(child_id)
            else: # 암말
                if child_id in arrows_out:
                    for foal_id in arrows_out[child_id]:
                        if foal_id in nodes:
                            partner_id = nodes[foal_id]['parent']
                            partner_name = nodes[partner_id]['name'] if partner_id in nodes else "?"
                            fillies.append({'child': name, 'partner': partner_name, 'link_info': nodes[foal_id]['name']})
                            seen.add(child_id)

        # 결과 화면 출력
        st.success(f"✅ **{selected_name}** 분석 완료! (수말 {len(colts)}두 / 암말 {len(fillies)}두)")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='header' style='color:#2b6cb0;'>🟦 수말 자마 (Sons: {len(colts)})</div>", unsafe_allow_html=True)
            if colts:
                for c in colts:
                    # 보기 좋게 이름 정리
                    clean_child = c['child']
                    clean_bms = c['bms']
                    st.markdown(f"""
                    <div class='card male-card'>
                        <div class='main-text'>🐎 {clean_child}</div>
                        <div class='sub-text'>
                            어미: {c['link_info']}<br>
                            👉 <b>외조부(BMS): <span class='highlight'>{clean_bms}</span></b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("데이터 없음")

        with c2:
            st.markdown(f"<div class='header' style='color:#d53f8c;'>🩷 암말 자마 (Daughters: {len(fillies)})</div>", unsafe_allow_html=True)
            if fillies:
                for f in fillies:
                    clean_child = f['child']
                    clean_partner = f['partner']
                    st.markdown(f"""
                    <div class='card female-card'>
                        <div class='main-text'>🎀 {clean_child}</div>
                        <div class='sub-text'>
                            자마: {f['link_info']}<br>
                            👉 <b>교배 파트너(Sire): <span class='highlight'>{clean_partner}</span></b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("데이터 없음")
