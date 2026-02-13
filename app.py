import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기 (Direct)", layout="wide")

# 스타일: 선생님이 원하시는 박스 디자인 유지
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; }
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; }
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 다이렉트 분석기")
st.caption("선택 과정 없이, 검색어와 일치하는 모든 씨수말의 자마를 통합하여 보여줍니다.")

# --- 1. 데이터 로드 (필요할 때 읽기) ---
# 검색어가 입력되면 그때 파일을 엽니다.
query = st.text_input("분석할 씨수말 이름을 입력하세요 (예: Tapit, Pulpit):", "").strip()

if query:
    if not os.path.exists('data.mm'):
        st.error("데이터 파일(data.mm)이 없습니다.")
    else:
        tree = ET.parse('data.mm')
        root = tree.getroot()
        
        males = []   # BMS 연결된 수말 모음
        females = [] # Sire 연결된 암말 모음
        
        found_parents_count = 0
        
        # --- 2. [핵심] 통합 검색 로직 ---
        # 드롭다운 없이, 전체 데이터에서 이름이 매칭되는 모든 부모를 찾습니다.
        for node in root.iter('node'):
            parent_name = node.get('TEXT', '').strip()
            
            # 검색어가 이름에 포함되어 있으면 (대소문자 무시) 내 식구로 간주합니다.
            if query.lower() in parent_name.lower():
                # 자식이 있는지 확인
                children = node.findall('node')
                if children:
                    found_parents_count += 1
                    
                    for child in children:
                        text = child.get('TEXT', '').strip()
                        
                        # ★ 대 전제: 연결(Line) 확인
                        # 중복 방지 (이미 리스트에 있으면 넣지 않음)
                        
                        # 1. 수말 (BMS)
                        if ("BMS" in text or "bms" in text):
                            if text not in males:
                                males.append(text)
                        
                        # 2. 암말 (Sire)
                        elif ("Sire" in text or "sire" in text):
                            if text not in females:
                                females.append(text)
        
        # --- 3. 결과 출력 ---
        total = len(males) + len(females)
        
        st.markdown("---")
        
        if total > 0:
            # 통합 결과 요약
            st.markdown(f"""
            <div class="header-box">
                📊 '{query}' 통합 분석 결과: 수말(BMS) {len(males)}두 / 암말(Sire) {len(females)}두 (총 {total}두)
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # 왼쪽: 수말
            with col1:
                st.info(f"🟦 **수말 (BMS 연결)**")
                for h in males:
                    st.markdown(f'<div class="male-box">{h}</div>', unsafe_allow_html=True)

            # 오른쪽: 암말
            with col2:
                st.error(f"🟥 **암말 (Sire 연결)**")
                for h in females:
                    st.markdown(f'<div class="female-box">{h}</div>', unsafe_allow_html=True)
                    
        else:
            if found_parents_count > 0:
                st.warning(f"⚠️ '{query}' 이름의 말은 {found_parents_count}마리 찾았으나, BMS나 Sire로 연결된 자마가 하나도 없습니다.")
            else:
                st.warning(f"❌ '{query}' 검색 결과가 없습니다.")
