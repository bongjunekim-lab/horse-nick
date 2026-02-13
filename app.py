import streamlit as st
import xml.etree.ElementTree as ET
import os
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="2만두 통합 분석기", layout="wide")
st.title("🐎 씨수말 & 자마 통합 분석 시스템 (2만두 최적화)")

# 2. 고속 데이터 로더 (2만두 계보 분석용)
@st.cache_data
def load_pedigree_data():
    if not os.path.exists('data.mm'):
        return {}
    
    # XML 파일을 읽어 계통 지도를 그립니다.
    tree = ET.parse('data.mm')
    root = tree.getroot()
    
    # {씨수말이름: [자마리스트]} 구조로 저장
    db = {}
    for node in root.iter('node'):
        parent_name = node.get('TEXT', '').strip()
        if parent_name:
            # 해당 노드 바로 아래에 있는 자마(node)들만 수집
            children = [c.get('TEXT') for c in node.findall('node') if c.get('TEXT')]
            if children:
                # 같은 이름의 말이 있을 경우를 대비해 리스트를 합침
                if parent_name in db:
                    db[parent_name].extend(children)
                else:
                    db[parent_name] = children
    return db

# 데이터 로딩 시작
with st.spinner('2만 마리의 계보를 분석 중입니다. 잠시만 기다려 주세요...'):
    horse_db = load_pedigree_data()

# 3. 검색 및 결과 출력 섹션
st.write("---")
query = st.text_input("🔍 검색할 씨수말 이름을 입력하세요 (소문자 가능):", "").strip()

if query and horse_db:
    q_low = query.lower()
    # 2만 개 데이터 중 검색어가 포함된 말들을 찾습니다.
    matches = [name for name in horse_db.keys() if q_low in name.lower()]
    
    if matches:
        # 검색된 결과 중 하나를 선택
        selected = st.selectbox(f"✅ {len(matches)}두가 발견되었습니다. 분석할 말을 선택하세요:", sorted(list(set(matches))))
        
        # 선택된 말의 자마 리스트 가져오기
        offspring_list = horse_db[selected]
        
        st.subheader(f"📊 {selected}의 자마 목록 (총 {len(offspring_list)}두)")
        
        # 표 데이터 생성 (Pandas 사용)
        df = pd.DataFrame({
            "순번": range(1, len(offspring_list) + 1),
            "자마 및 상세 정보": offspring_list
        })
        
        # 화면에 표 출력
        st.table(df)
        
        # 4. 엑셀(CSV) 다운로드 버튼
        # 한글 깨짐 방지를 위해 utf-8-sig 사용
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 현재 자마 리스트를 엑셀로 저장하기",
            data=csv_data,
            file_name=f"{selected}_자마리스트.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"❌ '{query}'와(과) 일치하는 씨수말 데이터가 없습니다.")

elif not query:
    st.info("왼쪽 검색창에 마명을 입력하면 분석이 시작됩니다.")
