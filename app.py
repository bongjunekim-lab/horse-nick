import streamlit as st
import xml.etree.ElementTree as ET
import re
import os
from collections import defaultdict

# 1. 페이지 설정 및 전문가용 스타일
st.set_page_config(page_title="엘리트 혈통 닉 분석 시스템", layout="wide")

st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 12px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #0077CC; }
    .female-box { background-color: #fce8e6; padding: 12px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #C0392B; }
    .bms-info { color: #d32f2f; font-weight: bold; font-size: 0.95em; }
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 분석 엔진 (선 + 화살표 통합 추적)
@st.cache_data
def analyze_pedigree_integrated(query):
    file_path = 'data.mm' # 파일명을 실제 파일명에 맞게 수정하세요.
    if not os.path.exists(file_path): return None, "데이터 파일을 찾을 수 없습니다."

    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # [핵심] 모든 노드 ID 매핑 (화살표 추적용)
    id_to_text = {n.get('ID'): n.get('TEXT', '').strip() for n in root.iter('node') if n.get('ID')}
    id_to_node = {n.get('ID'): n for n in root.iter('node') if n.get('ID')}

    # 검색 대상 씨수말 찾기
    candidates = []
    for node in root.iter('node'):
        name = node.get('TEXT', '').strip()
        if query.lower() in name.lower():
            if node.findall('node'): candidates.append((node, len(node.findall('node')), name))
    
    if not candidates: return None, "검색 결과가 없습니다."
    target_sire = max(candidates, key=lambda x: x[1])[0]
    
    males, females = [], []

    # 3. 자마 순회 및 역추적
    for foal in target_sire.findall('node'):
        foal_name = foal.get('TEXT', '').strip()
        
        # [대전제] 선(직계 노드 혹은 화살표)이 있는지 확인
        direct_children = foal.findall('node')
        arrows = foal.findall('arrowlink')
        
        if not direct_children and not arrows:
            continue # 선이 아예 없으면 분석 제외

        # [역추적 로직] 
        # 우선순위 1: 화살표(arrowlink)가 가리키는 대상 (엄마 노드)
        # 우선순위 2: 직계 하위 노드 (엄마 노드)
        mom_node = None
        if arrows:
            dest_id = arrows[0].get('DESTINATION')
            mom_node = id_to_node.get(dest_id)
        elif direct_children:
            mom_node = direct_children[0]

        # 엄마 노드를 찾았다면, 그 엄마를 존재하게 한 할아버지(BMS) 탐색
        bms_profile = "정보 없음"
        if mom_node is not None:
            # 엄마 박스에서 다시 선(노드)이나 화살표를 타고 할아버지로 이동
            grand_children = mom_node.findall('node')
            grand_arrows = mom_node.findall('arrowlink')
            
            if grand_arrows:
                g_dest_id = grand_arrows[0].get('DESTINATION')
                bms_profile = id_to_text.get(g_dest_id, "정보 없음")
            elif grand_children:
                bms_profile = grand_children[0].get('TEXT', '').strip()
            else:
                # 더 이상 선이 없으면 엄마 박스의 텍스트 자체가 할아버지 정보일 가능성 농후
                bms_profile = mom_node.get('TEXT', '').strip()

        # 결과 조립
        display_html = f"<b>{foal_name}</b> <span class='bms-info'>({bms_profile})</span>"

        if any(m in foal_name for m in ["암)", "@", "Filly"]):
            females.append(display_html)
        else:
            males.append(display_html)
            
    return (males, females, target_sire.get('TEXT')), None

# --- UI 실행부 ---
st.title("🐎 씨수말 닉(Nick) 구조 분석기")
query_input = st.text_input("분석할 씨수말 이름을 입력하세요 (예: Bernardini):", "").strip()

if query_input:
    res, err = analyze_pedigree_integrated(query_input)
    if err:
        st.warning(err)
    else:
        m, f, name = res
        st.markdown(f'<div class="header-box">📊 {name} 분석 완료 (선 연결 정예 {len(m)+len(f)}두 발췌)</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"🟦 수말 / BMS 라인 ({len(m)})")
            for item in m: st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
        with col2:
            st.error(f"🟥 암말 / Sire 라인 ({len(f)})")
            for item in f: st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
