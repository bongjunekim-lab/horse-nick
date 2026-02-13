import streamlit as st
import xml.etree.ElementTree as ET
import os

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="씨수말 닉 분석기 (Line Trace)", layout="wide")
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; font-family: "Malgun Gothic", sans-serif; font-size: 14px;}
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; font-family: "Malgun Gothic", sans-serif; font-size: 14px;}
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 구조 분석기")
st.caption("대전제: 선으로 연결된 자마만 추출하며, 하부 노드 전체가 아닌 직계 연결 정보만 가져옵니다.")

# 2. 검색창
query = st.text_input("씨수말 이름을 입력하세요 (예: Bernardini):", "").strip()

if query:
    if not os.path.exists('data.mm'):
        st.error("데이터 파일(data.mm)이 없습니다.")
    else:
        tree = ET.parse('data.mm')
        root = tree.getroot()
        
        # --- 1단계: 검색 대상(부마) 찾기 ---
        candidates = []
        for node in root.iter('node'):
            name = node.get('TEXT', '').strip()
            if query.lower() in name.lower():
                children = node.findall('node')
                candidates.append((node, len(children), name))
        
        if not candidates:
            st.warning(f"❌ '{query}' 관련 데이터를 찾을 수 없습니다.")
        else:
            best_node, _, best_name = max(candidates, key=lambda x: x[1])
            
            # --- 2단계: 자마 순회 (대전제 로직 적용) ---
            males = []
            females = []
            foals = best_node.findall('node')
            
            for foal in foals:
                foal_name = foal.get('TEXT', '').strip()
                
                # [대전제 1] 선으로 연결된 하위 노드(엄마/외조부 프로필)가 있는지 확인
                line_connections = foal.findall('node')
                
                # 선이 없는 자마는 무시 (대전제 준수)
                if not line_connections:
                    continue 

                # [대전제 2] 하부 로드를 다 따라가지 않고, '직계 선'의 텍스트만 챙김
                # 자마와 바로 맞닿은 첫 번째 하위 노드의 정보가 '엄마/외조부' 프로필입니다.
                profile_node = line_connections[0]
                profile_text = profile_node.get('TEXT', '').strip()

                # 화면 표시용 텍스트 조립: 자마이름 (직계 프로필)
                display_html = f"<b>{foal_name}</b> <span style='color:gray; font-size:0.85em;'>({profile_text})</span>"

                # [대전제 3] 성별에 따른 좌우 분리
                if "암)" in foal_name or "Filly" in foal_name:
                    females.append(display_html)
                else:
                    males.append(display_html)

            # --- 3단계: 화면 출력 ---
            st.markdown(f'<div class="header-box">📊 {best_name} 분석 결과 (선으로 연결된 {len(males)+len(females)}두 추출)</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"🟦 수말 / BMS 라인 ({len(males)})")
                for item in males:
                    st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
            
            with col2:
                st.error(f"🟥 암말 / Sire 라인 ({len(females)})")
                for item in females:
                    st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
