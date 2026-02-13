import streamlit as st
import xml.etree.ElementTree as ET
import re
import os

# 스타일 설정: 선생님의 전문가용 레이아웃
st.set_page_config(page_title="버나디니 화살표 경로 분석기", layout="wide")
st.markdown("""
    <style>
    .male-box { background-color: #f1f8ff; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 6px solid #0077CC; }
    .female-box { background-color: #fff5f5; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 6px solid #C0392B; }
    .bms-text { color: #ff4b4b; font-weight: bold; font-size: 1.1em; }
    .header-info { background-color: #e6fffa; padding: 15px; border-radius: 10px; border: 1px solid #38b2ac; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def analyze_by_arrowlink(query):
    file_path = '우수한 경주마(수말, 암말).mm'
    if not os.path.exists(file_path): return None, "파일을 찾을 수 없습니다."

    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # 1. 고속 추적을 위한 ID 매핑 및 부모 관계도 생성
    id_map = {n.get('ID'): n for n in root.iter('node') if n.get('ID')}
    parent_map = {c: p for p in root.iter() for c in p}

    # 2. 씨수말(Bernardini) 특정
    target_sire = None
    for node in root.iter('node'):
        txt = node.get('TEXT', '')
        if query.lower() in txt.lower() and node.findall('node'):
            target_sire = node
            break
    if not target_sire: return None, "해당 씨수말을 찾을 수 없습니다."

    males, females = [], []

    # 3. 자마 중 arrowlink가 있는 노드만 발췌
    for foal in target_sire.findall('node'):
        arrow = foal.find('arrowlink')
        if arrow is None: continue # 화살표 없는 자마는 지시에 따라 제외

        f_text = foal.get('TEXT', '').strip()
        dest_id = arrow.get('DESTINATION')
        
        # 4. 화살표를 따라 모마 노드로 점프
        mom_node = id_map.get(dest_id)
        bms_info = "연결된 상위 정보 없음"
        
        if mom_node is not None:
            # 5. 모마의 물리적 부모(외조부) 정보 획득
            gs_node = parent_map.get(mom_node)
            if gs_node is not None:
                bms_info = gs_node.get('TEXT', '').strip()

        # 결과 조립 및 성별 분류
        display = f"<b>{f_text}</b><br><span class='bms-text'>⮕ {bms_info}</span>"
        
        if "암)" in f_text or "@" in f_text:
            females.append(display)
        else:
            males.append(display)
            
    return (males, females, target_sire.get('TEXT')), None

# --- UI 실행 ---
st.title("🐎 버나디니(Bernardini) 화살표 경로 추적기")
st.markdown("<div class='header-info'>지시사항 반영: 화살표(arrowlink)가 있는 자마만 발췌하여 수동 보완된 외조부 정보를 추적합니다.</div>", unsafe_allow_html=True)

search_name = st.text_input("씨수말 이름을 입력하세요:", "Bernardini")

if search_name:
    res, err = analyze_by_arrowlink(search_name)
    if err:
        st.error(err)
    else:
        m, f, s_name = res
        st.success(f"✅ {s_name} 분석 완료 (화살표 연결 자마: {len(m)+len(f)}두)")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"♂️ 아들 자마 ({len(m)})")
            for item in m: st.markdown(f'<div class="male-box">{item}</div>', unsafe_allow_html=True)
        with col2:
            st.subheader(f"♀️ 딸 자마 ({len(f)})")
            for item in f: st.markdown(f'<div class="female-box">{item}</div>', unsafe_allow_html=True)
