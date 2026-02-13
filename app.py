import streamlit as st
import xml.etree.ElementTree as ET
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")

st.title("🐎 씨수말 닉 분석기 (리스트 표준화 완료)")

# --- 2. 데이터 로딩 (선생님 규칙: 모든 단어 첫글자만 대문자, 나머지 소문자) ---
file_path = 'data.mm'

@st.cache_data
def load_and_fix_list(path):
    if not os.path.exists(path): return None
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            tree = ET.parse(f)
        root = tree.getroot()
        nodes = {}
        for node in root.iter('node'):
            nid = node.get('ID')
            text = node.get('TEXT', '').strip()
            if nid and text:
                # ★ 선생님의 핵심 규칙 적용!
                # 모든 글자를 소문자로 바꾼 뒤, 맨 앞글자만 대문자로 고정
                # 예: "Storm Cat" -> "Storm cat", "MEDAGLIA" -> "Medaglia"
                fixed_name = text.lower().capitalize()
                nodes[nid] = {'name': fixed_name}
        return nodes
    except: return None

nodes = load_and_fix_list(file_path)

# --- 3. 검색창 (선생님 입력값도 같은 규칙으로 변환) ---
st.write("### 🔎 통합 검색")
query = st.text_input("마명을 입력하세요 (소문자로 치셔도 됩니다):", "").strip()

if query:
    # 입력한 글자도 똑같은 규칙으로 변환해서 비교
    search_key = query.lower().capitalize()
    
    matched = []
    if nodes:
        for nid, info in nodes.items():
            if search_key in info['name']:
                matched.append(info['name'])
    
    if not matched:
        st.warning(f"❌ '{query}' 검색 결과가 없습니다.")
    else:
        final_list = sorted(list(set(matched)))
        selected = st.selectbox(f"🔍 {len(final_list)}마리 발견! 아래에서 선택하세요:", final_list)
        st.success(f"✅ **{selected}** 분석 중...")
