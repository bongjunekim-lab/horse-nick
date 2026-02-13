import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기 (Line Trace)", layout="wide")

st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; font-size: 14px;}
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; font-size: 14px;}
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 구조 분석기")
st.caption("설계 준수: 자마 ──선──> 엄마 노드(아빠 프로필 포함) 정보를 역추적하여 조립합니다.")

query = st.text_input("씨수말 이름을 입력하세요:", "").strip()

if query:
    if not os.path.exists('data.mm'):
        st.error("데이터 파일(data.mm)이 없습니다.")
    else:
        tree = ET.parse('data.mm')
        root = tree.getroot()
        
        # 1. 부마 노드 찾기
        candidates = []
        for node in root.iter('node'):
            name = node.get('TEXT', '').strip()
            if query.lower() in name.lower():
                child_nodes = node.findall('node')
                if child_nodes: candidates.append((node, len(child_nodes), name))
        
        if not candidates:
            st.warning(f"❌ '{query}' 관련 데이터를 찾을 수 없습니다.")
        else:
            best_node, _, best_name = max(candidates, key=lambda x: x[1])
            males, females = [], []
            foals = best_node.findall('node') 
            
            # 2. 자마 순회 및 아빠 프로필 역추적
            for foal in foals:
                foal_name = foal.get('TEXT', '').strip()
                line_to_mom = foal.findall('node')
                
                if not line_to_mom: continue # 선으로 연결되지 않은 자마 무시

                # 자마와 선으로 연결된 바로 다음 단계 노드(엄마 노드) 딱 하나만 점유
                mom_node = line_to_mom[0]
                
                # 엄마 노드 박스에 적힌 '아빠 프로필' 텍스트만 통째로 복사
                # 하부의 하드 노드는 절대 건드리지 않습니다.
                bms_profile = mom_node.get('TEXT', '').strip()

                # 결과 조립: 자마이름 (가져온 아빠 프로필)
                display_html = f"<b>{foal_name}</b> <span style='color:gray; font-size:0.85em;'>({bms_profile})</span>"

                if "암)" in foal_name or "Filly" in foal_name:
                    females.append(display_html)
                else:
                    males.append(display_html)

            # 3. 화면 출력
            st.markdown(f'<div class="header-box">📊 {best_name} 닉 분석 결과 (총 {len(males)+len(females)}두)</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🟦 수말 / BMS 라인 ({len(males)})")
                for item in males: st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
            with col2:
                st.error(f"🟥 암말 / Sire 라인 ({len(females)})")
                for item in females: st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
