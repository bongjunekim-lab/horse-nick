import streamlit as st
import xml.etree.ElementTree as ET
import os

# 페이지 설정 및 스타일 (박스 디자인 유지)
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; }
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; }
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 정밀 분석기")

# --- 1단계: 무조건 다 읽어오는 로더 (검색 실패 방지용) ---
@st.cache_data
def load_raw_data():
    if not os.path.exists('data.mm'): return {}
    tree = ET.parse('data.mm')
    root = tree.getroot()
    
    # 필터링 없이 일단 다 담습니다. (검색이 되어야 하니까요)
    # { '씨수말이름': [자마1 텍스트, 자마2 텍스트, ...] }
    db = {}
    for node in root.iter('node'):
        name = node.get('TEXT', '').strip()
        if name:
            # 자식 노드(자마)가 있으면 무조건 가져옵니다.
            children = [c.get('TEXT', '').strip() for c in node.findall('node') if c.get('TEXT')]
            if children:
                db[name] = children
    return db

# 데이터 로딩 (이제 "검색 결과 없음"은 안 뜰 겁니다)
horse_db = load_raw_data()

# --- 2단계: 검색 및 리스트 선택 ---
st.write("### 1. 씨수말 검색")
query = st.text_input("마명을 입력하세요 (예: storm, pulpit):", "").strip()

if query and horse_db:
    # 대소문자 무시하고 일단 이름이 비슷한 건 다 찾습니다.
    matches = [name for name in horse_db.keys() if query.lower() in name.lower()]
    
    if matches:
        # 검색된 리스트를 먼저 보여줍니다.
        selected = st.selectbox(f"✅ {len(matches)}두가 검색되었습니다. 분석할 말을 선택하세요:", sorted(matches))
        
        # --- 3단계: 선택 후 실시간 분석 (여기서만 필터링) ---
        if selected:
            st.markdown("---")
            st.write(f"### 2. {selected} 닉(Nick) 분석 결과")
            
            raw_children = horse_db[selected]
            
            # 여기서 선생님의 규칙(BMS/Sire)대로 분류합니다.
            males = []   # BMS 포함된 놈 (수말)
            females = [] # Sire 포함된 놈 (암말)
            others = []  # 연결고리가 없는 놈 (기타)
            
            for child in raw_children:
                if "BMS" in child or "bms" in child:
                    males.append(child)
                elif "Sire" in child or "sire" in child:
                    females.append(child)
                else:
                    others.append(child)
            
            # 분석 결과 요약 바
            total_valid = len(males) + len(females)
            st.markdown(f"""
            <div class="header-box">
                📊 분석 요약: 수말(BMS) {len(males)}두 / 암말(Sire) {len(females)}두 (유효 자마 총 {total_valid}두)
            </div>
            """, unsafe_allow_html=True)

            # 화면 분할 출력
            col1, col2 = st.columns(2)
            
            # 왼쪽: 수말
            with col1:
                st.info(f"🟦 **수말 (BMS 연결) - {len(males)}두**")
                if males:
                    for h in males:
                        st.markdown(f'<div class="male-box">{h}</div>', unsafe_allow_html=True)
                else:
                    st.write("데이터 없음")

            # 오른쪽: 암말
            with col2:
                st.error(f"🟥 **암말 (Sire 연결) - {len(females)}두**")
                if females:
                    for h in females:
                        st.markdown(f'<div class="female-box">{h}</div>', unsafe_allow_html=True)
                else:
                    st.write("데이터 없음")
            
            # (선택사항) 연결고리 없는 데이터 확인용 - 필요 없으면 지우셔도 됩니다.
            if others:
                with st.expander(f"⚠️ 족보 연결 정보(BMS/Sire)가 없는 자마 ({len(others)}두) 보기"):
                    st.write(others)
                    
    else:
        st.warning("🔍 검색된 이름이 없습니다. 철자를 확인해 주세요.")
