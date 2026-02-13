import streamlit as st
import xml.etree.ElementTree as ET
import os

# 스타일 설정
st.set_page_config(page_title="엘리트 혈통 닉 분석 시스템", layout="wide")
st.markdown("""
    <style>
    .male-box { background-color: #e8f0fe; padding: 12px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #0077CC; }
    .female-box { background-color: #fce8e6; padding: 12px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #C0392B; }
    .bms-info { color: #d32f2f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 구조 분석기")
st.caption("대전제: 자마(중심) ──선──> 엄마 ──선──> 외할아버지(뿌리) 역추적 로직 적용")

@st.cache_data
def run_pedigree_backtrace(query):
    file_path = 'data.mm'
    if not os.path.exists(file_path): return None, "데이터 없음"
    
    tree = ET.parse(file_path)
    root = tree.getroot()
    id_map = {n.get('ID'): n.get('TEXT', '').strip() for n in root.iter('node') if n.get('ID')}

    # 1. 씨수말 노드 찾기
    for node in root.iter('node'):
        if query.lower() in node.get('TEXT', '').lower() and node.findall('node'):
            target_sire = node
            break
    else: return None, "검색 결과 없음"

    males, females = [], []
    
    # 2. 자마 순회 (대전제: 선이 연결된 것만 발췌)
    for foal in target_sire.findall('node'):
        foal_to_mom = foal.findall('node')
        if not foal_to_mom: continue # 선 없으면 패스
        
        # 3. 역추적: 자마 -> 엄마 -> 할아버지
        mom_node = foal_to_mom[0]
        mom_to_grand = mom_node.findall('node')
        
        # 할아버지 박스의 프로필 텍스트 추출
        bms_profile = id_map.get(mom_to_grand[0].get('ID'), "") if mom_to_grand else id_map.get(mom_node.get('ID'), "정보 없음")

        f_name = foal.get('TEXT', '').strip()
        display = f"<b>{f_name}</b> <span class='bms-info'>({bms_profile})</span>"

        if any(m in f_name for m in ["암)", "@", "Filly"]):
            females.append(display)
        else:
            males.append(display)
            
    return (males, females, target_sire.get('TEXT')), None

# 단 하나의 검색창
query_input = st.text_input("씨수말 이름을 입력하세요:", "").strip()

if query_input:
    res, err = run_pedigree_backtrace(query_input)
    if not err:
        m, f, name = res
        st.success(f"📊 {name} 분석 완료 (선 연결 정예 {len(m)+len(f)}두)")
        c1, c2 = st.columns(2)
        with c1:
            for item in m: st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
        with c2:
            for item in f: st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
