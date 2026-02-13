import streamlit as st
import xml.etree.ElementTree as ET
import os

# --- 1. 페이지 설정 및 캐시 삭제 ---
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")
st.cache_data.clear() # 매번 새로 읽도록 설정

st.title("🐎 씨수말 닉 분석기 (대소문자 자동 정리 버전)")

# --- 2. 데이터 로딩 (읽어올 때 대소문자 정리) ---
file_path = 'data.mm'

@st.cache_data
def load_data(path):
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
                # ★ 선생님의 아이디어: 파일 속 이름을 모두 '첫글자만 대문자'로 통일해서 기억
                clean_name = text.capitalize() 
                nodes[nid] = {'name': clean_name, 'original': text}
        return nodes, root
    except: return None

data = load_data(file_path)
if not data:
    st.error("데이터 파일을 읽을 수 없습니다.")
    st.stop()

nodes, root = data

# --- 3. 검색창 (선생님 입력값도 자동 정리) ---
st.write("### 🔎 통합 검색")
query = st.text_input("마명을 입력하세요 (예: pulpit, medagl):", "").strip()

if query:
    # ★ 사용자가 어떻게 입력하든 첫글자만 대문자로 바꿔서 비교
    search_key = query.capitalize()
    
    # 검색어와 일치하는 마명 찾기
    matched = [info['name'] for nid, info in nodes.items() if search_key in info['name']]
    
    if not matched:
        st.warning(f"❌ '{query}' 검색 결과가 없습니다.")
    else:
        selected = st.selectbox(f"🔍 {len(set(matched))}마리 발견! 선택하세요:", sorted(list(set(matched))))
        st.success(f"✅ **{selected}** 분석 중입니다...")
        # (이후 분석 로직 실행...)
