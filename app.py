import streamlit as st
import xml.etree.ElementTree as ET
import re
import os
from collections import defaultdict

# 1. 페이지 및 스타일 설정 (선생님의 전문가용 컬러 팔레트 유지)
st.set_page_config(page_title="엘리트 혈통 닉 분석 시스템", layout="wide")
st.markdown("""
    <style>
    .elite-mare { color: #0077CC !important; font-weight: bold; font-size: 1.25em; margin-top: 10px; }
    .progeny-item { margin-left: 30px; margin-bottom: 2px; color: #333333; font-size: 1.05em; }
    .bms-red { color: #C0392B !important; font-weight: bold; } /* 외조부 강조 */
    .nick-red { color: #C0392B !important; font-weight: bold; }
    .hr-line { margin: 10px 0; border-bottom: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 분석 엔진 (선생님의 기존 로직 100% 반영)
@st.cache_data
def load_and_trace_logic():
    file_path = '우수한 경주마(수말, 암말).mm'
    if not os.path.exists(file_path): return None, None, None, "파일 없음"

    tree = ET.parse(file_path)
    root = tree.getroot()
    
    id_to_text = {}
    id_to_parent_text = {}
    node_map = {}

    # 1차 순회: 모든 노드의 ID, 텍스트, 부모 텍스트 매핑 (선생님 방식)
    for parent in root.iter('node'):
        p_text = parent.get('TEXT', 'Unknown')
        for child in parent.findall('node'):
            c_id = child.get('ID')
            if c_id:
                id_to_text[c_id] = child.get('TEXT', '')
                id_to_parent_text[c_id] = p_text
                node_map[c_id] = child

    # 정규화 함수 (선생님 코드 그대로 사용)
    def normalize_name(text):
        clean = text.replace('@', '').replace('#', '').replace('*', '')
        clean = clean.replace('암)', '').replace('수)', '').replace('거)', '')
        clean = clean.split('(')[0]
        return clean.strip().lower()

    elite_sire_map = defaultdict(list)
    
    # 트래버스 로직 (선생님의 @ 종빈마 탐색 로직)
    def traverse(node, parent_text="Unknown"):
        my_text = node.get('TEXT', '')
        if my_text and '@' in my_text:
            mare_pure_name = normalize_name(my_text)
            seen_ids = set()
            progeny_data = []

            # 화살표(arrowlink)로 연결된 자마 추적
            for arrow in node.findall('arrowlink'):
                dest_id = arrow.get('DESTINATION')
                if dest_id in id_to_text and dest_id not in seen_ids:
                    child_raw_text = id_to_text[dest_id]
                    if mare_pure_name != normalize_name(child_raw_text):
                        # [핵심] 자마의 외조부(BMS)를 찾기 위해 자마 노드 내부의 연결 확인
                        child_node = node_map.get(dest_id)
                        bms_text = "미기재"
                        if child_node is not None:
                            # 자마 -> (화살표/선) -> 외조부 추적
                            g_arrows = child_node.findall('arrowlink')
                            g_nodes = child_node.findall('node')
                            if g_arrows: bms_text = id_to_text.get(g_arrows[0].get('DESTINATION'), "")
                            elif g_nodes: bms_text = g_nodes[0].get('TEXT', '')
                        
                        progeny_data.append({'id': dest_id, 'bms': bms_text})
                        seen_ids.add(dest_id)

            elite_sire_map[parent_text.strip()].append({
                'name': my_text.strip(),
                'progeny': progeny_data
            })
        
        for child in node.findall('node'):
            traverse(child, my_text)

    traverse(root)
    return elite_sire_map, id_to_text, id_to_parent_text, None

# --- 실행 및 출력 ---
st.title("🐎 엘리트 종빈마 기반 닉(Nick) 역순 분석 시스템")

elite_map, id_to_text, id_to_parent_text, err = load_and_trace_logic()
if err: st.error(err); st.stop()

query = st.text_input("씨수말 검색 (예: Bernardini):", "").strip()

if query:
    # 검색된 씨수말의 엘리트 종빈마들 출력
    results = {k: v for k, v in elite_map.items() if query.lower() in k.lower()}
    
    for sire, daughters in results.items():
        with st.expander(f"📊 {sire} (엘리트 종빈마 {len(daughters)}두 분석)", expanded=True):
            for d in daughters:
                st.markdown(f"<div class='elite-mare'>💎 {d['name']}</div>", unsafe_allow_html=True)
                for p in d['progeny']:
                    c_name = id_to_text.get(p['id'], "")
                    f_name = id_to_parent_text.get(p['id'], "미확인")
                    bms = p['bms'] # 선생님이 수동으로 보완하신 외조부 데이터
                    
                    # 최종 출력: 자마 이름 (외조부)
                    st.markdown(f"""
                        <div class='progeny-item'>
                            🔗 {c_name} <span class='bms-red'>({bms})</span> 
                            <span style='color:gray; font-size:0.8em;'>[부: {f_name}]</span>
                        </div>
                    """, unsafe_allow_html=True)
