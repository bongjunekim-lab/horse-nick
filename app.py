import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기 Pro", layout="wide")

# 스타일: 선생님이 원하시는 박스 디자인(초록/파랑/빨강)을 위해 CSS를 살짝 입힙니다.
st.markdown("""
    <style>
    .stAlert { padding: 10px; border-radius: 10px; }
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; }
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; }
    .header-box { background-color: #e6fffa; padding: 15px; border-radius: 10px; border: 1px solid #4fd1c5; color: #234e52; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 정밀 분석기")

# --- 1. 데이터 로드 및 "연결고리" 필터링 ---
@st.cache_data
def load_filtered_data():
    if not os.path.exists('data.mm'): return {}
    tree = ET.parse('data.mm')
    root = tree.getroot()
    
    db = {}
    
    for node in root.iter('node'):
        parent_name = node.get('TEXT', '').strip()
        
        if parent_name:
            children = node.findall('node')
            if children:
                males = []   # BMS 연결된 수말
                females = [] # Sire 연결된 암말
                
                for child in children:
                    text = child.get('TEXT', '').strip()
                    
                    # ★ 핵심: "선으로 연결된 자마만 발췌" (조건부 필터링)
                    # 조건 1: BMS(외조부) 정보가 있으면 -> 수말 리스트
                    if "BMS" in text or "bms" in text:
                        males.append(text)
                    # 조건 2: Sire(부마) 정보가 있으면 -> 암말 리스트
                    elif "Sire" in text or "sire" in text:
                        females.append(text)
                    # 조건 3: 둘 다 없으면? -> 과감히 버립니다 (선생님 요청사항)
                
                # 유효한 자마가 하나라도 있을 때만 등록
                if males or females:
                    if parent_name in db:
                        db[parent_name]['males'].extend(males)
                        db[parent_name]['females'].extend(females)
                    else:
                        db[parent_name] = {'males': males, 'females': females}
    return db

horse_db = load_filtered_data()

# --- 2. 검색창 ---
query = st.text_input("분석할 씨수말 이름을 입력하세요 (예: Bernardini):", "").strip()

if query and horse_db:
    # 대소문자 무시 검색
    matches = [name for name in horse_db.keys() if query.lower() in name.lower()]
    
    if matches:
        selected = st.selectbox(f"✅ {len(matches)}두 검색됨. 선택하세요:", sorted(matches))
        
        data = horse_db[selected]
        male_list = data['males']
        female_list = data['females']
        total_count = len(male_list) + len(female_list)
        
        st.markdown("---")
        
        # --- 3. 선생님이 원하시는 "초록색 요약 바" 구현 ---
        st.markdown(f"""
        <div class="header-box">
            📊 {selected} 분석 결과: 수말 {len(male_list)}두 / 암말 {len(female_list)}두 (총 {total_count}두)
        </div>
        """, unsafe_allow_html=True)
        
        # --- 4. 좌우 분할 및 박스형 리스트 출력 ---
        col1, col2 = st.columns(2)
        
        # [왼쪽] 수말 (BMS 연결)
        with col1:
            st.info(f"🟦 **수말 (Colts) - 외조부(BMS) 연결**")
            if male_list:
                for horse in male_list:
                    # 그냥 글자만 뿌리는 게 아니라, 예쁜 박스에 담습니다.
                    st.markdown(f'<div class="male-box">🐎 {horse}</div>', unsafe_allow_html=True)
            else:
                st.write("📌 BMS 정보가 연결된 수말이 없습니다.")
        
        # [오른쪽] 암말 (Sire 연결)
        with col2:
            st.error(f"🟥 **암말 (Fillies) - 부마(Sire) 연결**")
            if female_list:
                for horse in female_list:
                    # 빨간색 계열 박스에 담습니다.
                    st.markdown(f'<div class="female-box">🎀 {horse}</div>', unsafe_allow_html=True)
            else:
                st.write("📌 Sire 정보가 연결된 암말이 없습니다.")

    else:
        st.warning("검색 결과가 없습니다. (족보 연결 정보가 없는 말일 수 있습니다)")
