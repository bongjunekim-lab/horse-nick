import streamlit as st
import xml.etree.ElementTree as ET
import os

# 1. 페이지 설정
st.set_page_config(page_title="씨수말 닉 분석기 (Line Trace)", layout="wide")

# 스타일 설정
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; font-family: "Malgun Gothic", sans-serif; font-size: 14px;}
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; font-family: "Malgun Gothic", sans-serif; font-size: 14px;}
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 구조 분석기")
st.caption("설계 준수: 자마 ──선──> 엄마 노드(아빠 프로필 포함) 정보를 역추적하여 한 줄로 조립합니다.")

# 2. 검색창
query = st.text_input("씨수말 이름을 입력하세요:", "").strip()

if query:
    if not os.path.exists('data.mm'):
        st.error("데이터 파일(data.mm)이 없습니다.")
    else:
        tree = ET.parse('data.mm')
        root = tree.getroot()
        
        # --- 1단계: 검색 대상 부마 찾기 ---
        candidates = []
        for node in root.iter('node'):
            name = node.get('TEXT', '').strip()
            if query.lower() in name.lower():
                child_nodes = node.findall('node')
                if child_nodes: # 자마가 있는 경우만 후보
                    candidates.append((node, len(child_nodes), name))
        
        if not candidates:
            st.warning(f"❌ '{query}' 관련 데이터를 찾을 수 없습니다.")
        else:
            # 자식이 가장 많은 노드 선택
            best_node, _, best_name = max(candidates, key=lambda x: x[1])
            
            males = []
            females = []
            foals = best_node.findall('node') 
            
            # --- 2단계: 자마 순회 및 설계 로직 적용 ---
            for foal in foals:
                foal_name = foal.get('TEXT', '').strip()
                
                # [설계 준수 1] 선(Line) 존재 여부 확인
                # 자마 노드 바로 아래에 연결된 노드(findall('node'))가 있는지 확인
                line_to_mom = foal.findall('node')
                
                if not line_to_mom:
                    # 선으로 연결되지 않은 것은 대전제에 따라 무시
                    continue 

                # [설계 준수 2] 선으로 연결된 바로 다음 단계 노드(엄마 노드) 딱 하나만 잡기
                mom_node = line_to_mom[0]
                
                # [설계 준수 3] 엄마 노드에 적힌 '아빠(외조부) 프로필'을 통째로 복사
                # 하부의 지저분한 데이터로 내려가지 않고, 그 노드의 TEXT만 가져옵니다.
                bms_profile = mom_node.get('TEXT', '').strip()

                # [설계 준수 4] 결과 조립: 자마이름 (가져온 프로필 텍스트)
                # 불필요한 split이나 가공 없이, 선생님 말씀대로 그 박스의 프로필을 그대로 괄호에 넣습니다.
                display_html = f"<b>{foal_name}</b> <span style='color:gray; font-size:0.85em;'>({bms_profile})</span>"

                # 성별 분류 (이름에 '암)' 글자 기준)
                if "암)" in foal_name or "Filly" in foal_name:
                    females.append(display_html)
                else:
                    males.append(display_html)

            # --- 3단계: 화면 출력 ---
            st.markdown(f'<div class="header-box">📊 {best_name} 닉 분석 결과 (총 {len(males)+len(females)}두)</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"🟦 수말 / BMS 라인 ({len(males)})")
                for item in males:
                    st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
            
            with col2:
                st.error(f"🟥 암말 / Sire 라인 ({len(females)})")
                for item in females:
                    st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
