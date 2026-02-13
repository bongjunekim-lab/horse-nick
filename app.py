import streamlit as st
import xml.etree.ElementTree as ET
import os

st.set_page_config(page_title="씨수말 닉 분석기 Pro", layout="wide")

# --- 1. 데이터 로드 및 수말/암말 자동 분류 ---
@st.cache_data
def load_nick_data():
    if not os.path.exists('data.mm'): return {}
    tree = ET.parse('data.mm')
    root = tree.getroot()
    
    # { '씨수말이름': {'males': [], 'females': []} } 구조로 저장
    db = {}
    
    for node in root.iter('node'):
        parent_name = node.get('TEXT', '').strip()
        
        # 씨수말 이름이 있고 자식 노드가 있는 경우만 분석
        if parent_name:
            children = node.findall('node')
            if children:
                males = []
                females = []
                
                for child in children:
                    text = child.get('TEXT', '')
                    # ★ 핵심 로직: 텍스트 내용을 보고 수말/암말 분류
                    # BMS(외조부) 정보가 있으면 -> 수말 리스트로
                    # Sire(부마) 정보가 있거나 그 외 -> 암말 리스트로 (혹은 아이콘 속성 활용 가능)
                    if "BMS:" in text: 
                        males.append(text)
                    elif "Sire:" in text:
                        females.append(text)
                    else:
                        # 구분자가 명확하지 않은 경우 일단 수말 쪽에 포함 (데이터 확인 필요)
                        # 만약 데이터에 아이콘(icon) 정보가 있다면 그것을 쓰는 것이 더 정확합니다.
                        # 여기서는 선생님 설명대로 텍스트 패턴을 우선합니다.
                        if "Sire" in text: 
                            females.append(text)
                        else:
                            males.append(text)

                # 자마가 한 마리라도 있으면 DB에 등록
                if males or females:
                    if parent_name not in db:
                        db[parent_name] = {'males': males, 'females': females}
                    else:
                        # 이미 등록된 동명이마 처리 (기존 리스트에 추가)
                        db[parent_name]['males'].extend(males)
                        db[parent_name]['females'].extend(females)
    return db

# 데이터 로딩
horse_db = load_nick_data()

# --- 2. 검색 및 닉 분석 화면 구현 ---
st.title("🐎 씨수말 닉(Nick) 상세 분석기")
st.markdown("수말 자마는 **BMS(외조부)**, 암말 자마는 **Sire(부마)**를 기준으로 분석합니다.")

query = st.text_input("분석할 씨수말 이름을 입력하세요 (예: pulpit, bernardini):", "").strip()

if query and horse_db:
    # 대소문자 무시 검색
    q_low = query.lower()
    matches = [name for name in horse_db.keys() if q_low in name.lower()]
    
    if matches:
        selected = st.selectbox(f"✅ {len(matches)}두 검색됨. 선택하세요:", sorted(matches))
        
        # 선택된 말의 데이터 가져오기
        data = horse_db[selected]
        male_list = data['males']
        female_list = data['females']
        
        # --- 3. 화면 분할 (왼쪽: 수말 / 오른쪽: 암말) ---
        st.divider()
        st.subheader(f"📊 {selected}의 자마 분석 결과")
        
        # 상단 요약 바 (선생님 사진처럼 초록색 바 느낌)
        st.success(f"🐎 수말 {len(male_list)}두 / 🎀 암말 {len(female_list)}두 (총 {len(male_list)+len(female_list)}두)")

        col1, col2 = st.columns(2)
        
        # 왼쪽 컬럼: 수말 (Colts)
        with col1:
            st.info(f"🟦 **수말 (Colts) - BMS 연결 ({len(male_list)})**")
            if male_list:
                for horse in male_list:
                    # 사진처럼 카드 형태로 출력 (BMS 강조)
                    st.markdown(f"exam: {horse}")
            else:
                st.write("등록된 수말 자마가 없습니다.")
                
        # 오른쪽 컬럼: 암말 (Fillies)
        with col2:
            st.error(f"🟥 **암말 (Fillies) - Sire 연결 ({len(female_list)})**")
            if female_list:
                for horse in female_list:
                    # 사진처럼 카드 형태로 출력 (Sire 강조)
                    st.markdown(f"exam: {horse}")
            else:
                st.write("등록된 암말 자마가 없습니다.")
                
    else:
        st.warning(f"❌ '{query}'에 대한 데이터가 없습니다.")
