import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기 (Final)", layout="wide")

# 선생님이 "성공했다"고 하셨던 그 깔끔한 디자인 (파랑/빨강 박스)
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; font-size: 14px; font-family: "Malgun Gothic", sans-serif; }
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; font-size: 14px; font-family: "Malgun Gothic", sans-serif; }
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 분석기")
st.caption("선(Line)으로 연결된 자마의 정보를 있는 그대로 가져와 분류합니다.")

# 1. 검색창
query = st.text_input("씨수말 이름을 입력하세요 (예: Bernardini):", "").strip()

if query:
    if not os.path.exists('data.mm'):
        st.error("데이터 파일(data.mm)이 없습니다.")
    else:
        tree = ET.parse('data.mm')
        root = tree.getroot()
        
        # --- 1단계: '진짜 부모' 찾기 ---
        # 이름이 같은 놈들 중 '선(Line)이 가장 많이 연결된(자식이 많은)' 놈을 찾습니다.
        candidates = []
        for node in root.iter('node'):
            name = node.get('TEXT', '').strip()
            # 검색어가 포함된 이름이면 후보 등록
            if query.lower() in name.lower():
                child_count = len(node.findall('node'))
                candidates.append((node, child_count, name))
        
        if not candidates:
            st.warning(f"❌ '{query}' 관련 데이터를 찾을 수 없습니다.")
        else:
            # 자식이 제일 많은 놈이 진짜 '씨수말'입니다.
            best_node, max_children, best_name = max(candidates, key=lambda x: x[1])
            
            if max_children == 0:
                 st.warning(f"⚠️ '{best_name}'을(를) 찾았으나, 연결된 자마(Line)가 하나도 없습니다.")
            else:
                # --- 2단계: 선(Line) 따라가서 그대로 복사해오기 ---
                males = []   # BMS 글자가 있는 줄
                females = [] # Sire 글자가 있는 줄
                
                # 자식 노드(선으로 연결된 것들)를 하나씩 다 가져옵니다.
                children = best_node.findall('node')
                
                for child in children:
                    # ★ 선생님의 지시: "전부 복사해서 와서 보여주면 되자나"
                    raw_text = child.get('TEXT', '').strip()
                    
                    # 분류 기준: 텍스트 안에 BMS가 있냐, Sire가 있냐
                    text_upper = raw_text.upper()
                    
                    if "BMS" in text_upper:
                        males.append(raw_text) # 있는 그대로 저장
                    elif "SIRE" in text_upper:
                        females.append(raw_text) # 있는 그대로 저장
                    # 둘 다 없으면? 굳이 화면에 안 띄웁니다 (선생님 화면처럼 깔끔하게)

                # --- 3단계: 화면에 뿌리기 (버너디니 그림처럼) ---
                total = len(males) + len(females)
                
                st.markdown("---")
                # 초록색 요약 바
                st.markdown(f"""
                <div class="header-box">
                    📊 {best_name} 자마 분석 결과 <br>
                    수말(BMS) {len(males)}두 / 암말(Sire) {len(females)}두 (총 {total}두)
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                # 왼쪽: 수말
                with col1:
                    st.info(f"🟦 **수말 (Colts) - BMS 연결 ({len(males)})**")
                    if males:
                        for text in males:
                            # 텍스트를 가공하지 않고 박스에 그대로 넣습니다.
                            st.markdown(f'<div class="male-box">{text}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
                
                # 오른쪽: 암말
                with col2:
                    st.error(f"🟥 **암말 (Fillies) - Sire 연결 ({len(females)})**")
                    if females:
                        for text in females:
                            # 텍스트를 가공하지 않고 박스에 그대로 넣습니다.
                            st.markdown(f'<div class="female-box">{text}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
