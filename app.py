import streamlit as st
import xml.etree.ElementTree as ET
import os

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
st.caption("대전제: 자마 ──선──> 엄마 노드에서 오직 '아빠(외조부) 프로필'만 역추적하여 가져옵니다.")

query = st.text_input("씨수말 이름을 입력하세요:", "").strip()

if query:
    if not os.path.exists('data.mm'):
        st.error("데이터 파일(data.mm)이 없습니다.")
    else:
        tree = ET.parse('data.mm')
        root = tree.getroot()
        
        candidates = []
        for node in root.iter('node'):
            name = node.get('TEXT', '').strip()
            if query.lower() in name.lower():
                child_nodes = node.findall('node')
                if child_nodes:
                    candidates.append((node, len(child_nodes), name))
        
        if not candidates:
            st.warning(f"❌ '{query}' 관련 데이터를 찾을 수 없습니다.")
        else:
            best_node, _, best_name = max(candidates, key=lambda x: x[1])
            
            males = []
            females = []
            foals = best_node.findall('node') 
            
            for foal in foals:
                foal_name = foal.get('TEXT', '').strip()
                
                # [대전제] 자마 노드 밑에 선(엄마 노드)이 있는지 확인
                line_connections = foal.findall('node')
                if not line_connections:
                    continue 

                # [역추적 로직] 자마 ──선──> 엄마 노드 도착
                mom_node = line_connections[0]
                mom_full_text = mom_node.get('TEXT', '').strip()

                # [프로필 추출] 엄마 노드 텍스트에서 '아빠(외조부)' 정보만 분리
                # 보통 "BMS이름 / 엄마이름" 혹은 "BMS이름 (연도) ..." 형식이므로 
                # 가장 앞부분의 핵심 이름/프로필만 가져오도록 처리합니다.
                # 여기서는 쉼표(,)나 슬래시(/) 기준 앞부분 혹은 전체 텍스트 중 불필요한 하드데이터 제외
                bms_profile = mom_full_text.split(',')[0].split('/')[0].strip()

                # 결과 조립: 자마이름 (아빠 프로필)
                display_html = f"<b>{foal_name}</b> <span style='color:gray; font-size:0.85em;'>({bms_profile})</span>"

                if "암)" in foal_name or "Filly" in foal_name:
                    females.append(display_html)
                else:
                    males.append(display_html)

            # --- 화면 출력 ---
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
