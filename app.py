import streamlit as st
import xml.etree.ElementTree as ET
import os
import re

# 1. 페이지 설정
st.set_page_config(page_title="씨수말 닉(Nick) 구조 분석기", layout="wide")

# CSS 설정 (제공해주신 코드의 전문가용 팔레트 적용)
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #0077CC; color: #333; font-size: 14px;}
    .female-box { background-color: #fce8e6; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #C0392B; color: #333; font-size: 14px;}
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    .bms-text { color: #555; font-size: 0.9em; font-weight: normal; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 구조 분석기")
st.caption("대전제: 자마 ──선──> 엄마 노드에서 '아빠(외조부) 프로필'을 역추적하여 가져옵니다.")

# 2. 데이터 분석 함수 (제공해주신 코드의 매핑 로직 응용)
def analyze_mm_structure(query):
    file_path = 'data.mm'
    if not os.path.exists(file_path):
        return None, "데이터 파일을 찾을 수 없습니다."

    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # [응용] 모든 노드를 ID 기반으로 매핑하여 선(Line) 추적 준비
    id_to_node = {node.get('ID'): node for node in root.iter('node') if node.get('ID')}
    
    # 대상 씨수말 찾기
    candidates = []
    for node in root.iter('node'):
        name = node.get('TEXT', '').strip()
        if query.lower() in name.lower():
            child_nodes = node.findall('node')
            if child_nodes:
                candidates.append((node, len(child_nodes), name))
    
    if not candidates:
        return None, f"'{query}' 관련 데이터를 찾을 수 없습니다."

    best_node, _, best_name = max(candidates, key=lambda x: x[1])
    
    males = []
    females = []
    
    # 3. 자마 순회 및 '선' 추적 로직 (선생님 설계 철학 반영)
    for foal in best_node.findall('node'):
        foal_name = foal.get('TEXT', '').strip()
        
        # [설계 준수] 자마 노드 바로 아래에 직접 연결된 '선(Line)' 확인
        # findall('node')는 시각적인 '선'으로 연결된 하위 박스를 의미합니다.
        direct_lines = foal.findall('node')
        
        if not direct_lines:
            continue # 선이 없는 자마는 대전제에 따라 제외

        # [역추적] 첫 번째 연결된 노드 = 엄마(Dam) 노드
        mom_node = direct_lines[0]
        
        # [프로필 복사] 엄마 박스에 적힌 아빠(BMS) 프로필 가져오기
        # 응용 코드의 normalize_name 로직을 참고하여, 박스의 핵심 TEXT만 추출
        raw_bms_info = mom_node.get('TEXT', '').strip()
        
        # 불필요한 공백이나 줄바꿈 정리
        bms_profile = " ".join(raw_bms_info.split())

        # 결과 조립: 자마이름 (아빠 프로필)
        display_text = f"<b>{foal_name}</b> <span class='bms-text'>({bms_profile})</span>"

        # 성별 분류 (이름 내 기호 기준)
        if "암)" in foal_name or "@" in foal_name or "Filly" in foal_name:
            females.append(display_text)
        else:
            males.append(display_text)
            
    return (males, females, best_name), None

# 4. 메인 UI
query = st.text_input("씨수말 이름을 입력하세요:", "").strip()

if query:
    data, err = analyze_mm_structure(query)
    
    if err:
        st.error(err)
    else:
        males, females, best_name = data
        total = len(males) + len(females)
        
        st.markdown(f'<div class="header-box">📊 {best_name} 분석 결과 (선으로 연결된 {total}두 추출)</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"🟦 수말 / BMS 라인 ({len(males)})")
            for item in males:
                st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
        
        with col2:
            st.error(f"🟥 암말 / Sire 라인 ({len(females)})")
            for item in females:
                st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
