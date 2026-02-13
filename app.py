import streamlit as st
import xml.etree.ElementTree as ET
import os

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")
st.title("🐎 씨수말 닉 분석기 (표기법 최적화 완료)")

# --- 2. 데이터 로딩 (원본 보존 + 실시간 표기 변환) ---
@st.cache_data
def load_data_with_display_fix():
    if not os.path.exists('data.mm'): return None
    tree = ET.parse('data.mm')
    root = tree.getroot()
    nodes = {}
    for node in root.iter('node'):
        nid = node.get('ID')
        raw_text = node.get('TEXT', '').strip()
        if nid and raw_text:
            # ★ 선생님의 규칙: 원본은 놔두고, 표기만 "첫 글자만 대문자"로!
            # 예: "Storm Cat" -> "Storm cat", "CANDY RIDE" -> "Candy ride"
            display_text = raw_text.lower().capitalize()
            nodes[nid] = {'display': display_text, 'raw': raw_text}
    return nodes

all_data = load_data_with_display_fix()

# --- 3. 무적 검색 엔진 (대소문자 무시) ---
st.write("### 🔎 통합 검색")
query = st.text_input("마명을 입력하세요 (소문자로 편하게 치세요):", "").strip()

if query and all_data:
    q_low = query.lower()
    matched = []
    
    for info in all_data.values():
        # 사용자가 입력한 단어가 포함되어 있으면 무조건 찾음
        if q_low in info['raw'].lower():
            matched.append(info['display'])
    
    if not matched:
        st.warning(f"❌ '{query}' 결과가 없습니다.")
    else:
        # 중복 제거 후 가나다순 정렬
        final_list = sorted(list(set(matched)))
        selected = st.selectbox(f"🔍 {len(final_list)}마리 발견! 선택하세요:", final_list)
        st.success(f"✅ **{selected}** 분석 결과를 표시합니다.")
        
        # 여기서 분석 결과 표나 카드를 보여주는 코드를 추가하면 됩니다.
