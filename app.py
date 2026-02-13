import streamlit as st
import xml.etree.ElementTree as ET
import os

# 1. 전문가용 스타일 설정
st.set_page_config(page_title="엘리트 혈통 닉 분석 시스템", layout="wide")

st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 12px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #0077CC; color: #333; font-size: 14px; }
    .female-box { background-color: #fce8e6; padding: 12px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #C0392B; color: #333; font-size: 14px; }
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px; }
    .bms-profile { color: #666; font-size: 0.95em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 타이틀 및 "단 하나의 검색창"
st.title("🐎 씨수말 닉(Nick) 구조 분석기")
query_input = st.text_input("분석할 씨수말 이름을 입력하세요 (예: Bernardini):", "").strip()

# 3. 족보 역추적 엔진 (검증된 로직 적용)
@st.cache_data
def run_pedigree_engine(query):
    file_path = 'data.mm'
    if not os.path.exists(file_path): return None, "데이터 파일을 찾을 수 없습니다."

    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # ID 매핑 (할아버지 박스 텍스트를 즉시 가져오기 위함)
    id_map = {n.get('ID'): n.get('TEXT', '').strip() for n in root.iter('node') if n.get('ID')}
    
    # 1. 씨수말 찾기
    candidates = []
    for node in root.iter('node'):
        if query.lower() in node.get('TEXT', '').lower():
            if node.findall('node'): candidates.append((node, len(node.findall('node')), node.get('TEXT')))
    
    if not candidates: return None, "검색 결과가 없습니다."
    target_sire_node = max(candidates, key=lambda x: x[1])[0]
    
    males, females = [], []
    
    # 2. 자마 순회 (대전제: 선이 있는 것만!)
    for foal in target_sire_node.findall('node'):
        # [대전제] 옆으로 뻗은 선(자식 노드) 확인
        child_links = foal.findall('node')
        if not child_links: continue # 선 없으면 발췌 제외 (전기 절약)

        f_name = foal.get('TEXT', '').strip()
        
        # [역추적] 자마 -> 선 -> 엄마 -> 선 -> 할아버지
        mom_node = child_links[0]
        grand_links = mom_node.findall('node')
        
        # 할아버지 박스 텍스트 가져오기 (없으면 엄마 박스)
        if grand_lines := grand_links:
            bms_text = id_map.get(grand_lines[0].get('ID'), "")
        else:
            bms_text = id_map.get(mom_node.get('ID'), "")

        # 3. 결과 조립 (한 줄 요약)
        display_html = f"<b>{f_name}</b> <span class='bms-profile'>({bms_text})</span>"

        # 4. 성별 자동 분류
        if any(m in f_name for m in ["암)", "@", "Filly", "Mare"]):
            females.append(display_html)
        else:
            males.append(display_html)
            
    return (males, females, target_sire_node.get('TEXT')), None

# 4. 결과 출력
if query_input:
    res, err = run_pedigree_engine(query_input)
    if err:
        st.warning(err)
    else:
        m, f, sire_name = res
        st.markdown(f'<div class="header-box">📊 {sire_name} 닉 분석 완료 (선 연결 정예 {len(m)+len(f)}두 발췌)</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🟦 수말 / BMS 라인 ({len(m)})")
            for item in m: st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
        with col2:
            st.error(f"🟥 암말 / Sire 라인 ({len(f)})")
            for item in f: st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
