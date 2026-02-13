import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")
st.title("🐎 씨수말 닉 분석기 (무적 검색 모드)")

@st.cache_data
def load_data():
    if not os.path.exists('data.mm'): return None
    tree = ET.parse('data.mm')
    root = tree.getroot()
    # 원본 이름을 그대로 가져옵니다.
    nodes = {node.get('ID'): node.get('TEXT', '') for node in root.iter('node') if node.get('TEXT')}
    return nodes

all_horses = load_data()

st.write("### 🔎 통합 검색")
# 선생님이 어떤 대소문자로 치든 상관없게 만듭니다.
query = st.text_input("마명을 입력하세요 (소문자/대문자 상관없음):", "").strip()

if query and all_horses:
    # 1. 사용자가 입력한 단어를 소문자로 변환
    q_lower = query.lower()
    
    # 2. 원본 데이터도 소문자로 임시 변환해서 비교 (대소문자 무시 검색)
    matched = []
    for name in all_horses.values():
        if q_lower in name.lower():
            matched.append(name)
    
    if not matched:
        st.warning(f"❌ '{query}' 검색 결과가 없습니다.")
    else:
        # 중복 제거 후 가나다순 정렬
        final_list = sorted(list(set(matched)))
        selected = st.selectbox(f"🔍 {len(final_list)}마리 발견! 선택하세요:", final_list)
        st.success(f"✅ **{selected}** 분석 결과를 불러옵니다.")
