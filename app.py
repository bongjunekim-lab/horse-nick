import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기 (Line Trace)", layout="wide")

# 스타일 설정 (보기 좋게 디자인 유지)
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
        st.error("데이터 파일(data.mm)이 없습니다. 같은 폴더에 파일이 있는지 확인해주세요.")
    else:
        try:
            tree = ET.parse('data.mm')
            root = tree.getroot()
        except ET.ParseError:
            st.error("data.mm 파일 형식이 잘못되었습니다.")
            st.stop()
        
        # --- 1단계: '진짜 부모' 찾기 ---
        candidates = []
        for node in root.iter('node'):
            name = node.get('TEXT', '').strip()
            # 검색어가 포함된 노드 찾기 (대소문자 무시)
            if query.lower() in name.lower():
                children = node.findall('node')
                candidates.append((node, len(children), name))
        
        if not candidates:
            st.warning(f"❌ '{query}' 관련 데이터를 찾을 수 없습니다.")
        else:
            # 자식이 가장 많은 노드를 메인으로 선택
            best_node, max_children, best_name = max(candidates, key=lambda x: x[1])
            
            if max_children == 0:
                 st.warning(f"⚠️ '{best_name}'을(를) 찾았으나, 자마 데이터가 없습니다.")
            else:
                # --- 2단계: 자마 데이터 분류 및 수집 ---
                males = []   # 수말/거세 (왼쪽)
                females = [] # 암말 (오른쪽)
                
                # 자마들(Foals) 순회
                foals = best_node.findall('node')
                
                for foal in foals:
                    foal_name = foal.get('TEXT', '').strip()
                    
                    # 연결된 하위 노드(외조부마 등) 찾기
                    line_connections = foal.findall('node')
                    connected_text = ""
                    
                    if line_connections:
                        # 연결된 정보가 여러 개일 수 있으니 하나로 합침
                        connected_infos = [conn.get('TEXT', '').strip() for conn in line_connections]
                        connected_text = ", ".join(connected_infos)
                    
                    # [화면 표시용 텍스트] 자마명 + (연결정보)
                    # 연결 정보가 있으면 괄호 안에 넣어서 보여줌
                    conn_display = f"({connected_text})" if connected_text else ""
                    display_html = f"<b>{foal_name}</b> <span style='color:gray; font-size:0.9em;'>{conn_display}</span>"
                    
                    # ==========================================================
                    # [핵심 수정] 성별 분류 로직 (여기가 중요합니다!)
                    # ==========================================================
                    is_female = False
                    
                    # 조건 1: 자마 이름에 '암)' 또는 'Filly'가 있는가?
                    if "암)" in foal_name or "Filly" in foal_name or "Mare" in foal_name:
                        is_female = True
                    # 조건 2: 연결된 정보(하위노드)에 'Sire' 또는 '암' 관련 내용이 있는가?
                    elif "Sire" in connected_text or "Mare" in connected_text:
                        is_female = True
                    # 조건 3: Freeplane 속성상 왼쪽에 있으면 수말, 오른쪽에 있으면 암말인 경우 (POSITION 속성 활용)
                    elif foal.get('POSITION') == 'right': 
                        # 보통 마인드맵에서 오른쪽을 암말로 쓰는 경우가 많음 (데이터에 따라 다를 수 있음)
                        pass 

                    # 리스트에 추가
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
                
                # [왼쪽] 수말/BMS 라인
                with col1:
                    st.info(f"🟦 수말 / BMS 라인 ({len(males)})")
                    if males:
                        for item in males:
                            st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
                
                # [오른쪽] 암말/Sire 라인
                with col2:
                    st.error(f"🟥 암말 / Sire 라인 ({len(females)})")
                    if females:
                        for item in females:
                            st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
