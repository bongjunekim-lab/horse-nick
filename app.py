import streamlit as st
import xml.etree.ElementTree as ET
import os

# 페이지 설정
st.set_page_config(page_title="씨수말 닉 분석기 (Speed)", layout="wide")
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; }
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; }
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 분석기 (초고속 모드)")

# --- 1단계: 이름만 빨리 가져오기 (가볍게!) ---
@st.cache_data
def get_horse_names_only():
    if not os.path.exists('data.mm'): return []
    # 파일을 엽니다.
    tree = ET.parse('data.mm')
    root = tree.getroot()
    
    # 자마 정보는 무시하고, '씨수말 이름'만 쏙쏙 뽑아냅니다.
    names = set()
    for node in root.iter('node'):
        text = node.get('TEXT', '').strip()
        if text:
            names.add(text)
    return sorted(list(names))

# 로딩 시작 (이젠 금방 끝날 겁니다)
all_names = get_horse_names_only()

# --- 2단계: 검색창 ---
st.write("### 1. 씨수말 검색")
# 검색어 입력 전에는 전체 리스트를 보여주지 않아 속도를 더 높입니다.
query = st.text_input("마명을 입력하세요 (예: pulpit):", "").strip()

selected_horse = None

if query:
    # 입력한 글자가 포함된 이름만 찾습니다.
    matches = [name for name in all_names if query.lower() in name.lower()]
    
    if matches:
        selected_horse = st.selectbox(f"✅ {len(matches)}두 검색됨. 선택하세요:", matches)
    else:
        st.warning("검색 결과가 없습니다.")

# --- 3단계: 선택했을 때만! 정밀 분석 시작 (On-Demand) ---
if selected_horse:
    # ★ 여기서 파일을 다시 열어서 '그 말'의 정보만 쏙 빼옵니다.
    # 전체를 다 외우는 것보다, 필요할 때 책을 펴서 찾는 게 훨씬 빠릅니다.
    tree = ET.parse('data.mm')
    root = tree.getroot()
    
    target_node = None
    # 2만 개 중 선택한 말의 위치를 찾습니다.
    for node in root.iter('node'):
        if node.get('TEXT', '').strip() == selected_horse:
            target_node = node
            break
            
    if target_node:
        st.markdown("---")
        st.write(f"### 2. {selected_horse} 상세 분석 결과")
        
        # 자마들 수집 및 분류 (선생님의 핵심 로직)
        males = []
        females = []
        
        children = target_node.findall('node')
        for child in children:
            text = child.get('TEXT', '').strip()
            
            # 족보 연결(Line) 필터링
            if "BMS" in text or "bms" in text:
                males.append(text)
            elif "Sire" in text or "sire" in text:
                females.append(text)
            # 족보 없는 껍데기는 버림
            
        # 결과 출력
        total = len(males) + len(females)
        
        st.markdown(f"""
        <div class="header-box">
            📊 분석 요약: 수말(BMS) {len(males)}두 / 암말(Sire) {len(females)}두 (유효 자마 총 {total}두)
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"🟦 **수말 (BMS 연결)**")
            if males:
                for h in males:
                    st.markdown(f'<div class="male-box">{h}</div>', unsafe_allow_html=True)
            else:
                st.write("데이터 없음")
                
        with col2:
            st.error(f"🟥 **암말 (Sire 연결)**")
            if females:
                for h in females:
                    st.markdown(f'<div class="female-box">{h}</div>', unsafe_allow_html=True)
            else:
                st.write("데이터 없음")
