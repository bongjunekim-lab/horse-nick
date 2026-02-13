import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기 (Final)", layout="wide")

# 스타일 설정 (선생님이 만족하신 박스 디자인)
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #4285f4; color: black; }
    .female-box { background-color: #fce8e6; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #ea4335; color: black; }
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 연결 분석기")

# --- 1. 이름 로딩 (검색용) ---
@st.cache_data
def load_names():
    if not os.path.exists('data.mm'): return []
    tree = ET.parse('data.mm')
    root = tree.getroot()
    names = set()
    for node in root.iter('node'):
        t = node.get('TEXT', '').strip()
        if t: names.add(t)
    return sorted(list(names))

all_names = load_names()

# --- 2. 검색창 ---
st.write("### 1. 씨수말 검색")
query = st.text_input("마명을 입력하세요 (예: northern dancer):", "").strip()

selected_horse = None
if query:
    matches = [n for n in all_names if query.lower() in n.lower()]
    if matches:
        selected_horse = st.selectbox(f"✅ {len(matches)}두 검색됨. 선택하세요:", matches)
    else:
        st.warning("검색 결과가 없습니다.")

# --- 3. [핵심] 전수 조사 및 연결(Line) 필터링 ---
if selected_horse:
    # 파일을 다시 엽니다.
    tree = ET.parse('data.mm')
    root = tree.getroot()
    
    # 1. 이름이 똑같은 노드를 '전부' 찾습니다. (가장이든, 자식이든 상관없이 다 찾음)
    target_nodes = []
    for node in root.iter('node'):
        if node.get('TEXT', '').strip() == selected_horse:
            target_nodes.append(node)
            
    if target_nodes:
        males = []   # BMS 연결
        females = [] # Sire 연결
        
        # 2. 찾아낸 모든 노드의 자식들을 하나하나 검사합니다.
        for parent in target_nodes:
            children = parent.findall('node')
            for child in children:
                text = child.get('TEXT', '').strip()
                
                # ★ 대 전제 적용: 연결(Line)이 없으면 가차 없이 버린다.
                # 중복 방지를 위해 이미 찾은 리스트에 없으면 추가
                
                # 수말 조건: BMS가 있어야 한다.
                if ("BMS" in text or "bms" in text) and (text not in males):
                    males.append(text)
                
                # 암말 조건: Sire가 있어야 한다.
                elif ("Sire" in text or "sire" in text) and (text not in females):
                    females.append(text)
        
        # --- 4. 결과 출력 ---
        st.markdown("---")
        
        total = len(males) + len(females)
        
        # 데이터가 하나라도 있으면 출력, 없으면 경고
        if total > 0:
            st.markdown(f"""
            <div class="header-box">
                📊 {selected_horse} 분석 결과: 수말(BMS) {len(males)}두 / 암말(Sire) {len(females)}두 (연결된 자마 총 {total}두)
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("🟦 **수말 (BMS 연결)**")
                if males:
                    for h in males:
                        st.markdown(f'<div class="male-box">{h}</div>', unsafe_allow_html=True)
                else:
                    st.write("데이터 없음")
                    
            with col2:
                st.error("🟥 **암말 (Sire 연결)**")
                if females:
                    for h in females:
                        st.markdown(f'<div class="female-box">{h}</div>', unsafe_allow_html=True)
                else:
                    st.write("데이터 없음")
        else:
            st.warning(f"⚠️ '{selected_horse}'의 이름은 찾았으나, BMS나 Sire로 연결된 자마 데이터가 하나도 없습니다.")
            st.write("Tip: 데이터 파일에 'BMS:'나 'Sire:' 정보가 정확히 기입되어 있는지 확인해주세요.")
            
    else:
        st.error("오류: 노드를 찾을 수 없습니다.")
