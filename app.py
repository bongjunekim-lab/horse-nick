import streamlit as st
import xml.etree.ElementTree as ET
import os

# 페이지 기본 설정
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
st.caption("자마 -> 엄마 -> 외조부(BMS) 순서로 선을 끝까지 추적합니다.")

# 1. 검색창
query = st.text_input("씨수말 이름을 입력하세요 (예: Bernardini):", "").strip()

if query:
    if not os.path.exists('data.mm'):
        st.error("데이터 파일(data.mm)이 없습니다. 같은 폴더에 파일이 있는지 확인해주세요.")
    else:
        try:
            tree = ET.parse('data.mm')
            root = tree.getroot()
        except ET.ParseError:
            st.error("data.mm 파일 형식이 잘못되었습니다.")
            st.stop()
        
        # --- 1단계: 메인 씨수말 찾기 ---
        candidates = []
        for node in root.iter('node'):
            name = node.get('TEXT', '').strip()
            if query.lower() in name.lower():
                children = node.findall('node')
                candidates.append((node, len(children), name))
        
        if not candidates:
            st.warning(f"❌ '{query}' 관련 데이터를 찾을 수 없습니다.")
        else:
            best_node, max_children, best_name = max(candidates, key=lambda x: x[1])
            
            if max_children == 0:
                 st.warning(f"⚠️ '{best_name}'을(를) 찾았으나, 자마가 없습니다.")
            else:
                # --- 2단계: 자마 순회 및 '강력한 외조부 추적' ---
                males = []
                females = []
                
                foals = best_node.findall('node')
                
                for foal in foals:
                    # 1. 자마 이름
                    foal_name = foal.get('TEXT', '').strip()
                    
                    # 2. 선(Line) 확인 - 연결된 게 없으면 제외
                    line_connections = foal.findall('node')
                    if not line_connections:
                        continue 

                    # ==========================================================
                    # [핵심 수정] 무조건 끝까지 파고들어 텍스트 가져오기
                    # ==========================================================
                    bms_text = ""
                    
                    # 첫 번째 연결된 노드 (보통 엄마)
                    first_node = line_connections[0]
                    first_text = first_node.get('TEXT', '').strip()
                    
                    # 그 밑에 또 연결된 노드가 있는지 확인 (보통 외조부)
                    second_nodes = first_node.findall('node')
                    
                    if second_nodes:
                        # 손자 노드(외조부)가 있으면 그 텍스트를 우선으로 씁니다.
                        second_text = second_nodes[0].get('TEXT', '').strip()
                        if second_text:
                            bms_text = second_text
                        else:
                            # 손자 노드는 있는데 글자가 비어있으면 엄마 노드 글자라도 가져옴
                            bms_text = first_text
                    else:
                        # 손자 노드가 없으면 엄마 노드 글자를 외조부 정보로 간주하고 가져옴
                        bms_text = first_text

                    # 글자가 너무 길면(설명문이면) 잘라서 보여주기 (옵션)
                    # if len(bms_text) > 20: bms_text = bms_text[:20] + "..."

                    # 3. 화면 표시용 (외조부 텍스트가 있을 때만 괄호 표시)
                    if bms_text:
                        display_html = f"<b>{foal_name}</b> <span style='color:gray; font-size:0.9em;'>({bms_text})</span>"
                    else:
                        display_html = f"<b>{foal_name}</b>"

                    # 4. 성별 분류 (이름에 '암)' 포함 여부)
                    is_female = False
                    if "암)" in foal_name or "Filly" in foal_name or "Mare" in foal_name:
                        is_female = True
                    
                    if is_female:
                        females.append(display_html)
                    else:
                        males.append(display_html)

                # --- 3단계: 화면 출력 ---
                total = len(males) + len(females)
                
                st.markdown("---")
                st.markdown(f"""
                <div class="header-box">
                    📊 {best_name} 구조 분석 결과 (선으로 연결된 자마 총 {total}두)
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"🟦 수말 (Colts/Geldings) - {len(males)}두")
                    if males:
                        for item in males:
                            st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
                
                with col2:
                    st.error(f"🟥 암말 (Fillies/Mares) - {len(females)}두")
                    if females:
                        for item in females:
                            st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
