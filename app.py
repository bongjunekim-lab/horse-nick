import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")
st.title("🐎 씨수말 닉 분석기 (자마 리스트 출력 수정본)")

# --- 1. 데이터 로드 및 구조 파악 ---
@st.cache_data
def load_full_structure():
    if not os.path.exists('data.mm'): return None, None
    tree = ET.parse('data.mm')
    root = tree.getroot()
    
    all_nodes = list(root.iter('node'))
    # 검색을 위한 딕셔너리 (ID: 노드객체)
    node_map = {n.get('ID'): n for n in all_nodes if n.get('TEXT')}
    return all_nodes, node_map

all_nodes, node_map = load_full_structure()

# --- 2. 통합 검색창 ---
st.write("### 🔎 씨수말 검색")
query = st.text_input("마명을 소문자로 입력하세요 (예: storm, candy):", "").strip()

if query and node_map:
    q_low = query.lower()
    # 검색어 포함된 말들 찾기
    matched_ids = [nid for nid, n in node_map.items() if q_low in n.get('TEXT', '').lower()]
    
    if not matched_ids:
        st.warning("❌ 검색 결과가 없습니다.")
    else:
        # 선택 박스에는 '표기용 이름' 표시
        options = {node_map[nid].get('TEXT'): nid for nid in matched_ids}
        selected_name = st.selectbox(f"🔍 {len(options)}두 발견! 분석할 말을 선택하세요:", sorted(options.keys()))
        
        # --- 3. 자마 리스트 추출 핵심 로직 ---
        selected_id = options[selected_name]
        parent_node = node_map[selected_id]
        
        # 선택된 노드 바로 아래에 있는 자식 노드(자마)들 수집
        children = parent_node.findall('node')
        
        st.divider()
        st.subheader(f"📊 {selected_name}의 자마 리스트")
        
        if not children:
            st.info("이 말의 하부 자마 데이터가 없습니다.")
        else:
            # 리스트를 표 형태로 출력
            child_data = []
            for i, child in enumerate(children):
                child_data.append({"번호": i+1, "자마명 및 정보": child.get('TEXT')})
            
            st.table(child_data) # 표로 깔끔하게 출력
            
            # 여기서 나중에 엑셀 저장 버튼이 들어갑니다.
            st.download_button("📥 현재 리스트 엑셀로 저장 (준비중)", "data", file_name="result.csv")
