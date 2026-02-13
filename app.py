import streamlit as st
import xml.etree.ElementTree as ET
import os
from collections import defaultdict

st.set_page_config(page_title="씨수말 닉(Nick) 추적기", layout="wide")
st.title("🐎 씨수말 닉(Nick) 분석기")

# --- 데이터 로딩 ---
file_path = 'data.mm'

if not os.path.exists(file_path):
    st.error("🚨 데이터 파일이 없습니다.")
    st.stop()

try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml_content = f.read()
    if not xml_content.strip():
        st.error("🚨 파일 내용이 비어있습니다.")
        st.stop()
    root = ET.fromstring(xml_content)
except Exception as e:
    st.error(f"❌ 데이터 읽기 오류: {e}")
    st.stop()

# --- 데이터 분석 및 명단 수집 ---
nodes = {}
arrows_in = defaultdict(list)
arrows_out = defaultdict(list)
all_names = set() # 모든 말 이름을 저장할 곳

def parse(node, parent_id=None):
    nid = node.get('ID')
    text = node.get('TEXT', '').strip()
    
    if nid:
        nodes[nid] = {'name': text, 'parent': parent_id}
        if text: # 이름이 있으면 명단에 추가
            all_names.add(text)
            
        for arrow in node.findall('arrowlink'):
            dest = arrow.get('DESTINATION')
            if dest:
                arrows_out[nid].append(dest)
                arrows_in[dest].append(nid)
                
    for child in node.findall('node'):
        parse(child, nid)

parse(root)

# --- ★ 핵심 기능: 어떤 이름이 있는지 보여주기 ---
st.info(f"📂 현재 파일에 총 **{len(all_names)}마리**의 말이 등록되어 있습니다.")

with st.expander("📜 **여기를 눌러서 등록된 말 이름 확인하기 (복사해서 쓰세요)**"):
    # 이름 가나다순 정렬해서 보여주기
    sorted_names = sorted(list(all_names))
    st.write(sorted_names[:500]) # 너무 많으니 500개만 먼저 보여줌
    st.write("... (이하 생략)")

# --- 검색 기능 ---
query = st.text_input("위 목록에 있는 이름을 복사해서 넣어보세요 (예: Bernardini)", "")

if query:
    # 대소문자 구분 없이 검색 (Bernardini == bernardini)
    target_ids = [nid for nid, info in nodes.items() if query.lower() in info['name'].lower()]
    
    if not target_ids:
        st.warning(f"❌ '{query}'라는 이름을 찾을 수 없습니다. 위 목록을 확인해보세요.")
    else:
        colts = []; fillies = []; seen = set()

        for sire_id in target_ids:
            children = [nid for nid, info in nodes.items() if info['parent'] == sire_id]
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
        
        st.success(f"분석 완료! '{nodes[target_ids[0]]['name']}' 관련 데이터: 수말 {len(colts)}두 / 암말 {len(fillies)}두")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🟦 수말 (Sons)")
            for c in colts: st.info(f"🐎 {c['child']} (BMS: {c['bms']})")
        with c2:
            st.markdown("### 🩷 암말 (Daughters)")
            for f in fillies: st.error(f"🎀 {f['child']} (Sire: {f['partner']})")
