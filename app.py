import streamlit as st
import xml.etree.ElementTree as ET
import re
import os

# 1. 전문가용 스타일 (선생님의 UI 가이드 반영)
st.set_page_config(page_title="엘리트 혈통 닉 분석 시스템", layout="wide")
st.markdown("""
    <style>
    .male-box { background-color: #f1f8ff; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #0077CC; }
    .female-box { background-color: #fff5f5; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #C0392B; }
    .bms-final { color: #ff4b4b; font-weight: bold; } /* 선생님이 찾으시는 최종 외조부 */
    .header-box { background-color: #f0fff4; padding: 15px; border-radius: 10px; border: 1px solid #48bb78; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# [핵심] 대시(-) 개수와 '암)' 기호를 분석하여 외조부를 찾는 함수
def trace_bms_by_dash(foal_node, root, parent_map):
    f_text = foal_node.get('TEXT', '').strip()
    # 자마의 대시(-) 개수 파악 (예: "- 암) 자마" -> 1개)
    f_dash_match = re.match(r'^(-+)', f_text)
    f_dash_count = len(f_dash_match.group(1)) if f_dash_match else 0

    curr = foal_node
    # 상위 계층으로 올라가며 모마(Dam) 탐색
    while curr in parent_map:
        curr = parent_map[curr]
        p_text = curr.get('TEXT', '').strip()
        p_dash_match = re.match(r'^(-+)', p_text)
        p_dash_count = len(p_dash_match.group(1)) if p_dash_match else 0
        
        # 조건: 대시가 자마보다 적고, '암)' 혹은 '@'가 포함된 노드가 모마(Dam)
        if p_dash_count < f_dash_count and ("암)" in p_text or "@" in p_text):
            # 모마를 찾았다면, 그 모마보다 대시가 더 적은 직계 상위 노드가 '외조부'
            grand_curr = curr
            while grand_curr in parent_map:
                grand_curr = parent_map[grand_curr]
                g_text = grand_curr.get('TEXT', '').strip()
                g_dash_match = re.match(r'^(-+)', g_text)
                g_dash_count = len(g_dash_match.group(1)) if g_dash_match else 0
                
                if g_dash_count < p_dash_count:
                    return g_text # 이것이 바로 선생님이 찾으시는 최종 외조부 데이터
            return p_text # 외조부가 없으면 모마 정보라도 반환
            
    return "연결 정보 없음"

@st.cache_data
def run_full_pedigree_system(query):
    file_path = 'data.mm' # 파일 경로
    if not os.path.exists(file_path): return None, "데이터 파일이 없습니다."

    tree = ET.parse(file_path)
    root = tree.getroot()
    parent_map = {c: p for p in root.iter() for c in p} # 전체 노드 부모 맵 생성

    # 1. 씨수말 특정 (검색)
    target_sire = None
    for node in root.iter('node'):
        txt = node.get('TEXT', '').strip()
        if query.lower() in txt.lower() and node.findall('node'):
            target_sire = node
            break
    if not target_sire: return None, f"'{query}' 씨수말을 찾을 수 없습니다."

    males, females = [], []

    # 2. 자마 순회 및 대시 논리 적용
    for foal in target_sire.findall('node'):
        f_text = foal.get('TEXT', '').strip()
        
        # 선생님 지시: 선(화살표나 하위 노드)이 있는 자마만 분석
        if not foal.findall('node') and not foal.findall('arrowlink'): continue
        
        # [핵심] 대시 기반 역추적 수행
        bms_info = trace_bms_by_dash(foal, root, parent_map)
        
        display = f"<b>{f_text}</b> <span class='bms-final'>({bms_info})</span>"
        
        if "암)" in f_text or "@" in f_text:
            females.append(display)
        else:
            males.append(display)
            
    return (males, females, target_sire.get('TEXT')), None

# 3. UI 메인 실행
st.title("🐎 씨수말 닉(Nick) 구조 분석기")
st.caption("대전제: 대시(-) 개수 비교 및 '암)' 기호 식별을 통한 세대 역추적 로직 적용")

query_input = st.text_input("분석할 씨수말 이름을 입력하세요 (예: Bernardini):", "").strip()

if query_input:
    res, err = run_full_pedigree_system(query_input)
    if err:
        st.warning(err)
    else:
        m, f, s_name = res
        st.markdown(f'<div class="header-box">📊 {s_name} 분석 완료 (대시 위계 추적 적용)</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🟦 수말 / BMS 라인 ({len(m)})")
            for item in m: st.markdown(f'<div class="male-box">🐎 {item}</div>', unsafe_allow_html=True)
        with col2:
            st.error(f"🟥 암말 / Sire 라인 ({len(f)})")
            for item in f: st.markdown(f'<div class="female-box">🐎 {item}</div>', unsafe_allow_html=True)
