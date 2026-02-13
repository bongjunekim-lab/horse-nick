import streamlit as st
import xml.etree.ElementTree as ET
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")

st.title("🐎 씨수말 닉 분석기 (리스트 일괄 정리형)")

# --- 2. 데이터 로딩 (여기서 모든 이름을 'Pulpit' 형식으로 바꿉니다) ---
file_path = 'data.mm'

@st.cache_data
def load_and_standardize_data(path):
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
                # ★ 선생님의 핵심 아이디어 적용! 
                # 모든 단어를 '첫글자 대문자, 나머지 소문자'로 일괄 변환합니다.
                # 예: PULPIT -> Pulpit, pulpit -> Pulpit, pULpit -> Pulpit
                clean_name = text.capitalize() 
                nodes[nid] = {'name': clean_name}
        return nodes
    except: return None

# 앱 시작 시 리스트를 싹 청소해서 메모리에 올립니다.
nodes = load_and_standardize_data(file_path)

# --- 3. 검색 엔진 (선생님 입력값도 똑같이 변환해서 비교) ---
st.write("### 🔎 통합 검색")
st.info("💡 이제 소문자로 'pulpit'이라고 편하게 입력해 보세요. 앱이 알아서 찾아줍니다!")

query = st.text_input("마명을 입력하세요:", "").strip()

if query:
    # 선생님이 입력한 검색어도 똑같이 '첫글자 대문자'로 바꿔서 비교합니다.
    # 이렇게 하면 데이터와 입력값이 100% 일치하게 됩니다.
    search_key = query.capitalize()
    
    matched = []
    if nodes:
        for nid, info in nodes.items():
            # 리스트에 정리된 이름과 검색어를 비교합니다.
            if search_key in info['name']:
                matched.append(info['name'])
    
    if not matched:
        st.warning(f"❌ '{query}' 검색 결과가 없습니다.")
    else:
        # 중복 제거 후 가나다순 정렬
        final_list = sorted(list(set(matched)))
        selected = st.selectbox(f"🔍 {len(final_list)}마리 발견! 아래에서 선택하세요:", final_list)
        st.success(f"✅ **{selected}** 분석 결과입니다.")
