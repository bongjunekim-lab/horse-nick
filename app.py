import streamlit as st
import xml.etree.ElementTree as ET
import os
from collections import defaultdict

st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")
st.title("🐎 씨수말 닉(Nick) 분석기 (탐정 모드)")

# --- 데이터 로딩 ---
file_path = 'data.mm'
if not os.path.exists(file_path):
    st.error("🚨 데이터 파일이 없습니다.")
    st.stop()

try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml_content = f.read()
    root = ET.fromstring(xml_content)
except Exception as e:
    st.error(f"❌ 데이터 읽기 오류: {e}")
    st.stop()

# --- 데이터 분석 ---
nodes = {}
arrows_in = defaultdict(list)
arrows_out = defaultdict(list)
all_names = [] # 모든 이름을 저장할 리스트

def parse(node, parent_id=None):
    nid = node.get('ID')
    text = node.get('TEXT', '').strip()
    if nid:
        nodes[nid] = {'name': text, 'parent': parent_id}
        if text: # 이름이 비어있지 않으면 추가
            all_names.append(text)
            
        for arrow in node.findall('arrowlink'):
            dest = arrow.get('DESTINATION')
            if dest:
                arrows_out[nid].append(dest)
                arrows_in[dest].append(nid)
    for child in node.findall('node'):
        parse(child, nid)

parse(root)

# --- 🔍 탐정 기능: 이름 미리보기 ---
st.info("👇 **검색이 잘 안 되면 아래 목록에서 찾아서 복사하세요!**")

with st.expander("📜 **파일에 들어있는 말 이름 전체 명단 (클릭)**"):
    # 'ber' 같은 글자가 포함된 이름만 우선적으로 보여주기 위한 필터
    search_hint = st.text_input("찾고 싶은 이름의 일부를 영어로 적어보세요 (예: ber)", "")
    
    if search_hint:
        filtered_names = [name for name in all_names if search_hint.lower() in name.lower()]
        st.write(f"🔍 **'{search_hint}'가 포함된 말 {len(filtered_names)}마리 발견:**")
        st.write(filtered_names[:100]) # 100개만 보여줌
    else:
        st.write("아래는 무작위 100마리 샘플입니다:")
        st.write(all_names[:100])

st.divider()

# --- 메인 검색 기능 ---
st.write("### 🔎 분석할 씨수말 검색")
query = st.text_input("위 명단에서 확인한 이름을 정확히 입력하세요 (부분만 입력해도 됨)", "")

if query:
    # ★ 핵심: 대소문자 구분 없이, 부분 일치하면 다 찾습니다!
    target_ids = [nid for nid, info in nodes.items() if query.lower() in info['name'].lower()]
    
    if not target_ids:
        st.error(f"❌ '{query}'를 찾을 수 없습니다. 위 명단 확인 기능을 써보세요!")
    else:
        # 검색된 말이 여러 마리일 경우 선택하게 함 (동명이마 방지)
        found_names = [nodes[nid]['name'] for nid in target_ids]
        selected_name = st.selectbox("검색된 말 중 하나를 선택하세요:", found_names)
        
        # 선택한 말의 ID 찾기
        selected_id = target_ids[found_names.index(selected_name)]
        
        # 자마 분석 시작
        colts = []; fillies = []; seen = set()
        children = [nid for nid, info in nodes.items() if info['parent'] == selected_id]
        
        for child_id in children:
            if child_id in seen: continue
            info = nodes[child_id]; name = info['name']; is_female = '암)' in name
            
            if not is_female:
                if child_id in arrows_in:
                    for mom_id in arrows_in[child_id]:
                        if mom_id in nodes:
                            bms_id = nodes[mom_id]['parent']
                            bms_name = nodes[bms_id]['name'] if bms_id in nodes else "?"
                            colts.append({'child': name, 'bms': bms_name, 'link_info': nodes[mom_id]['name']})
                            seen.add(child_id)
            else:
                if child_id in arrows_out:
                    for foal_id in arrows_out[child_id]:
                        if foal_id in nodes:
                            partner_id = nodes[foal_id]['parent']
                            partner_name = nodes[partner_id]['name'] if partner_id in nodes else "?"
                            fillies.append({'child': name, 'partner': partner_name, 'link_info': nodes[foal_id]['name']})
                            seen.add(child_id)

        st.success(f"✅ **{selected_name}** 분석 결과: 수말 {len(colts)}두 / 암말 {len(fillies)}두")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🟦 수말 (Sons)")
            for c in colts: st.info(f"🐎 {c['child']} \n\n (BMS: {c['bms']})")
        with c2:
            st.markdown("### 🩷 암말 (Daughters)")
            for f in fillies: st.error(f"🎀 {f['child']} \n\n (Sire: {f['partner']})")
