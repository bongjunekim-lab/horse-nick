import streamlit as st
import xml.etree.ElementTree as ET
import os

# 1. 전문가용 스타일 설정
st.set_page_config(page_title="엘리트 혈통 닉 분석 시스템", layout="wide")

st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 12px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #0077CC; color: #333; font-size: 14px; }
    .female-box { background-color: #fce8e6; padding: 12px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #C0392B; color: #333; font-size: 14px; }
    .bms-profile { color: #d32f2f; font-weight: bold; font-size: 0.92em; }
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; color: #2f855a; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 구조 분석기")
st.caption("대전제: 자마 → 엄마 → 할아버지 역순 추적 (Node 계층 및 Arrowlink 동시 지원)")

# 2. 통합 역순 추적 엔진
@st.cache_data
def run_integrated_backtrace(query):
    file_path = 'data.mm'
    if not os.path.exists(file_path): return None, "데이터 파일 없음"

    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # [핵심] 전 노드 ID 및 객체 매핑 (화살표 추적의 기반)
    id_map = {n.get('ID'): n.get('TEXT', '').strip() for n in root.iter('node') if n.get('ID')}
    node_map = {n.get('ID'): n for n in root.iter('node') if n.get('ID')}

    # 검색 대상 씨수말(Sire) 찾기
    candidates = []
    for node in root.iter('node'):
        txt = node.get('TEXT', '').strip()
        if query.lower() in txt.lower():
            if node.findall('node'): candidates.append((node, len(node.findall('node')), txt))
    
    if not candidates: return None, f"'{query}' 결과 없음"
    target_sire = max(candidates, key=lambda x: x[1])[0]
    
    males, females = [], []

    # 3. 자마 순회 및 역순 추적 시작
    for foal in target_sire.findall('node'):
        # [대전제] 선(Node) 혹은 화살표(Arrow)가 있는 자마만 발췌
        child_nodes = foal.findall('node')
        arrows = foal.findall('arrowlink')
        
        if not child_nodes and not arrows: continue

        f_name = foal.get('TEXT', '').strip()

        # --- 역순 추적 로직 (자마 -> 엄마 -> 할아버지) ---
        target_box = None
        
        # 1단계: 엄마 찾기 (화살표 우선, 그다음 계층)
        if arrows:
            target_box = node_map.get(arrows[0].get('DESTINATION'))
        elif child_nodes:
            target_box = child_nodes[0]

        # 2단계: 할아버지 찾기 (엄마 노드에서 다시 한번 추적)
        bms_info = "정보 없음"
        if target_box is not None:
            grand_arrows = target_box.findall('arrowlink')
            grand_nodes = target_box.findall('node')
            
            if grand_arrows:
                bms_info = id_map.get(grand_arrows[0].get('DESTINATION'), "정보 없음")
            elif grand_nodes:
                bms_info = grand_nodes[0].get('TEXT', '').strip()
            else:
                # 더 이상 선이 없으면 해당 박스 자체가 혈통의 끝(BMS)
                bms_info = target_box.get('TEXT', '').strip()

        # 결과 조립 및 분류
        display = f"<b>{f_name}</b> <span class='bms-profile'>({bms_info})</span>"
        if any(m in f_name for m in ["암)", "@", "Filly"]):
            females.append(display)
        else:
            males.append(display)
            
    return (males, females, target_sire.get('TEXT')), None

# 4. 단 하나의 검색창
query_input = st.text_input("분석할 씨수말 이름을 입력하세요:", "").strip()

if query_input:
    res, err = run_integrated_backtrace(query_input)
    if err:
        st.warning(err)
    else:
        m, f, name = res
        st.markdown(f'<div class="header-box">📊 {name} 분석 완료 (정예 {len(m)+len(f)}두 발췌)</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🟦 수말 / BMS 라인 ({len(m)})")
            for item in m: st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
        with col2:
            st.error(f"🟥 암말 / Sire 라인 ({len(f)})")
            for item in f: st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
