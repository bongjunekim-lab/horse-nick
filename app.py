import streamlit as st
import xml.etree.ElementTree as ET
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")

st.title("🐎 씨수말 닉 분석기 (대소문자 자동 교정형)")

# --- 2. 데이터 로딩 ---
file_path = 'data.mm'

@st.cache_data
def load_data(path):
    if not os.path.exists(path): return None
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            tree = ET.parse(f)
        root = tree.getroot()
        nodes = {}
        # 모든 마명을 가져와서 비교용 '소문자 알맹이'를 만듭니다.
        for node in root.iter('node'):
            nid = node.get('ID'); text = node.get('TEXT', '').strip()
            if nid and text:
                nodes[nid] = {'name': text}
        return nodes
    except: return None

nodes = load_data(file_path)

# --- 3. 검색 엔진 (선생님의 아이디어 적용) ---
st.write("### 🔎 통합 검색")
st.info("💡 이제 소문자로 'pulpit'이라고 편하게 입력해 보세요!")

query = st.text_input("마명을 입력하세요:", "").strip()

if query:
    # ★ 핵심: 입력값과 파일값 모두 소문자로 바꿔서 비교 (대소문자 무시)
    q_low = query.lower()
    
    matched = []
    for nid, info in nodes.items():
        original_name = info['name']
        if q_low in original_name.lower(): # 둘 다 소문자로 바꿔서 비교!
            matched.append(original_name)
    
    if not matched:
        st.warning(f"❌ '{query}' 검색 결과가 없습니다.")
    else:
        # 중복 제거 후 선택창 표시
        selected = st.selectbox(f"🔍 {len(set(matched))}마리 발견! 선택하세요:", sorted(list(set(matched))))
        st.success(f"✅ **{selected}** 분석 결과를 불러옵니다.")
        
        # (이후 자마 분석 로직은 기존과 동일하게 작동합니다)
