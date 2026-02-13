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
st.caption("자마 이름 자체가 아니라, 자마와 '선(Line)'으로 연결된 하위 정보를 찾아옵니다.")

# 1. 검색창
query = st.text_input("씨수말 이름을 입력하세요 (예: Bernardini):", "").strip()

if query:
    if not os.path.exists('data.mm'):
        st.error("데이터 파일(data.mm)이 없습니다.")
    else:
        tree = ET.parse('data.mm')
        root = tree.getroot()
        
        # --- 1단계: '진짜 부모' 찾기 (자식이 제일 많은 놈) ---
        candidates = []
        for node in root.iter('node'):
            name = node.get('TEXT', '').strip()
            if query.lower() in name.lower():
                # 자식 수 카운트
                children = node.findall('node')
                candidates.append((node, len(children), name))
        
        if not candidates:
            st.warning(f"❌ '{query}' 관련 데이터를 찾을 수 없습니다.")
        else:
            # 자식이 가장 많은 노드를 진짜로 간주
            best_node, max_children, best_name = max(candidates, key=lambda x: x[1])
            
            if max_children == 0:
                 st.warning(f"⚠️ '{best_name}'을(를) 찾았으나, 자마가 하나도 없습니다.")
            else:
                # --- 2단계: 자마의 '하위 노드(Line)' 추적 ---
                males = []   # 왼쪽 (BMS 추정)
                females = [] # 오른쪽 (Sire 추정)
                
                # 자마들(Foals) 순회
                foals = best_node.findall('node')
                
                for foal in foals:
                    foal_name = foal.get('TEXT', '').strip()
                    
                    # ★ 핵심: 자마의 이름이 아니라, 자마 밑에 달린 '하위 노드'를 찾습니다.
                    # 선생님 말씀: "선으로 연결된 곳이 엄마고, 그 위가 외조부다. 그걸 복사해와라."
                    line_connections = foal.findall('node')
                    
                    if line_connections:
                        # 연결된 선이 있다면, 그 내용을 가져옵니다.
                        for connection in line_connections:
                            connected_text = connection.get('TEXT', '').strip()
                            
                            # 화면에 보여줄 최종 텍스트: "자마이름 + [연결된 정보]"
                            display_text = f"🐎 {foal_name} <br>&nbsp;&nbsp; └─ 🔗 {connected_text}"
                            
                            # 분류 로직: 연결된 텍스트 내용으로 판단
                            # (BMS나 Sire 글자가 있다면 그걸로 구분, 없다면 위치 정보나 기타 단서가 필요함)
                            # 우선 선생님의 성공 예시 사진에는 (BMS:...) (Sire:...)가 있었으므로 그걸 1순위로 봅니다.
                            
                            conn_upper = connected_text.upper()
                            
                            if "BMS" in conn_upper:
                                males.append(display_text)
                            elif "SIRE" in conn_upper:
                                females.append(display_text)
                            else:
                                # BMS/Sire 글자가 아예 없는 경우 -> 일단 왼쪽에 다 몰아서 보여줍니다. (확인용)
                                # 혹은 Freeplane의 POSITION 속성(left/right)을 쓸 수도 있습니다.
                                # 여기서는 안전하게 다 보여주기 위해 '기타' 혹은 '왼쪽'에 넣습니다.
                                males.append(display_text) 

                # --- 3단계: 화면 출력 ---
                total = len(males) + len(females)
                
                st.markdown("---")
                st.markdown(f"""
                <div class="header-box">
                    📊 {best_name} 구조 분석 결과 (총 {total}두 연결 확인)
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"🟦 **수말 / BMS 라인 ({len(males)})**")
                    if males:
                        for item in males:
                            st.markdown(f'<div class="male-box">{item}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
                
                with col2:
                    st.error(f"🟥 **암말 / Sire 라인 ({len(females)})**")
                    if females:
                        for item in females:
                            st.markdown(f'<div class="female-box">{item}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
