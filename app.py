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
st.caption("자마 -> 엄마 -> 외조부(BMS) 순서로 선을 추적하여 정보를 가져옵니다.")

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
                # --- 2단계: 자마 순회 및 '외조부 추적' ---
                males = []
                females = []
                
                foals = best_node.findall('node')
                
                for foal in foals:
                    # 1. 자마 이름 가져오기
                    foal_name = foal.get('TEXT', '').strip()
                    
                    # 2. [핵심 로직] 선을 타고 2단계 내려가서 외조부 찾기
                    # 구조: 자마 -> 엄마(1단계) -> 외조부(2단계)
                    
                    bms_name = "" # 외조부 이름 초기화
                    
                    # (1단계) 엄마 노드 찾기
                    dam_nodes = foal.findall('node')
                    
                    if dam_nodes:
                        # 엄마가 여러 명일 리는 없으니 첫 번째 노드를 엄마로 간주
                        dam_node = dam_nodes[0]
                        
                        # (2단계) 엄마 밑에 있는 외조부 노드 찾기
                        grand_nodes = dam_node.findall('node')
                        
                        if grand_nodes:
                            # 엄마 밑에 달린 첫 번째 노드를 '외조부'로 판단!
                            grand_node = grand_nodes[0]
                            bms_name = grand_node.get('TEXT', '').strip()

                    # 3. 화면 표시용 텍스트 만들기
                    # 외조부를 찾았으면: 자마이름 (외조부)
                    # 못 찾았으면: 자마이름
                    if bms_name:
                        # 외조부 이름이 너무 길면(설명글이면) 괄호 안에 넣기 좀 그러니, 적당히 짧을 때만 표시
                        # 혹은 무조건 표시
                        display_html = f"<b>{foal_name}</b> <span style='color:gray; font-size:0.9em;'>({bms_name})</span>"
                    else:
                        display_html = f"<b>{foal_name}</b>"

                    # 4. 성별 분류 (이름에 '암)' 포함 여부)
                    is_female = False
                    if "암)" in foal_name or "Filly" in foal_name or "Mare" in foal_name:
                        is_female = True
                    
                    # 리스트 추가
                    if is_female:
                        females.append(display_html)
                    else:
                        males.append(display_html)

                # --- 3단계: 화면 출력 ---
                total = len(males) + len(females)
                
                st.markdown("---")
                st.markdown(f"""
                <div class="header-box">
                    📊 {best_name} 구조 분석 결과 (총 {total}두)
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
