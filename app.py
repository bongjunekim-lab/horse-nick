import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기 (Final)", layout="wide")

# 스타일: 선생님이 "성공했다"고 하셨던 그 화면 디자인 (파랑/빨강 박스)
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; font-size: 14px; }
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; font-size: 14px; }
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 혈통 연결 분석기")
st.caption("가장 많은 자마와 연결된 '진짜 씨수말'을 찾아 BMS와 Sire 라인을 분석합니다.")

# 1. 검색창
query = st.text_input("분석할 씨수말 이름을 입력하세요 (예: Tapit, Street cry):", "").strip()

if query:
    if not os.path.exists('data.mm'):
        st.error("데이터 파일(data.mm)이 없습니다.")
    else:
        tree = ET.parse('data.mm')
        root = tree.getroot()
        
        # --- 1단계: '진짜 부모' 찾기 (자식이 제일 많은 놈이 범인입니다) ---
        candidates = []
        
        for node in root.iter('node'):
            name = node.get('TEXT', '').strip()
            # 이름이 비슷하면 일단 후보로 등록
            if query.lower() in name.lower():
                # 자식 수 확인
                child_count = len(node.findall('node'))
                candidates.append((node, child_count, name))
        
        if not candidates:
            st.warning(f"❌ '{query}'라는 이름의 말을 찾을 수 없습니다.")
        else:
            # ★ 핵심: 자식이 가장 많은 후보를 '진짜'로 선택 (자동 선택)
            # 이렇게 하면 자식 없는 껍데기 Tapit은 자연스럽게 탈락합니다.
            best_node, max_children, best_name = max(candidates, key=lambda x: x[1])
            
            if max_children == 0:
                 st.warning(f"⚠️ '{query}' 이름은 찾았으나, 연결된 자마(Line)가 하나도 없습니다.")
            else:
                # --- 2단계: 줄(Line)이 있는 자마만 분류 ---
                males = []   # BMS 라인
                females = [] # Sire 라인
                
                children = best_node.findall('node')
                for child in children:
                    text = child.get('TEXT', '').strip()
                    text_upper = text.upper() # 대소문자 무시용
                    
                    # 선생님 말씀대로 '선으로 연결된' 정보가 있는지 확인
                    
                    # 수말 조건: (BMS: ...) 가 붙어 있는가?
                    if "BMS" in text_upper:
                        males.append(text)
                    
                    # 암말 조건: (Sire: ...) 가 붙어 있는가?
                    elif "SIRE" in text_upper:
                        females.append(text)
                
                # --- 3단계: 결과 출력 ---
                total_valid = len(males) + len(females)
                
                st.markdown("---")
                # 초록색 요약 바
                st.markdown(f"""
                <div class="header-box">
                    📊 분석 대상: {best_name} <br>
                    ✅ 연결된 자마: 수말(BMS) {len(males)}두 / 암말(Sire) {len(females)}두 (총 {total_valid}두)
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                # 왼쪽: 수말 (파란색)
                with col1:
                    st.info(f"🟦 **수말 (Colts) - BMS(외조부) 연결**")
                    if males:
                        for h in males:
                            st.markdown(f'<div class="male-box">{h}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
                
                # 오른쪽: 암말 (빨간색)
                with col2:
                    st.error(f"🟥 **암말 (Fillies) - Sire(부마) 연결**")
                    if females:
                        for h in females:
                            st.markdown(f'<div class="female-box">{h}</div>', unsafe_allow_html=True)
                    else:
                        st.write("데이터 없음")
