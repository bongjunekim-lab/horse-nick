import streamlit as st
import xml.etree.ElementTree as ET
import os
from collections import defaultdict

st.set_page_config(page_title="씨수말 닉(Nick) 추적기", layout="wide")

# --- 범인 색출 코드 (디버깅) ---
current_files = os.listdir('.') # 현재 폴더에 있는 파일 목록을 가져옵니다
file_path = 'data.mm' # 우리가 찾는 파일 이름

st.title("🐎 씨수말 닉(Nick) 분석기 (성공!)")

# 파일이 진짜로 있는지 검사!
if not os.path.exists(file_path):
    st.error("🚨 **비상! 파일을 찾을 수 없습니다.**")
    st.warning("현재 깃허브 저장소에 있는 파일 목록은 아래와 같습니다. 눈 크게 뜨고 확인해 보세요! 👇")
    st.code(current_files) # 여기에 파일 목록이 쫙 뜹니다!
    st.info("""
    **[해결 힌트]**
    1. 목록에 'data.mm'이 아예 없다면? 👉 **파일이 안 만들어진 겁니다.**
    2. 'data.mm.txt'라고 되어 있다면? 👉 **뒤에 .txt가 붙은 겁니다.** (이름 수정 필요)
    3. 'Data.mm' (대문자)라면? 👉 **소문자로 고쳐야 합니다.**
    """)
    st.stop() # 파일 없으면 여기서 멈춤

# --- 파일이 있으면 아래 로직 실행 ---
try:
    tree = ET.parse(file_path)
    root = tree.getroot()
except Exception as e:
    st.error(f"📂 파일은 찾았는데, 내용을 읽을 수 없습니다! (내용이 비어있을 수 있음)\n에러 메시지: {e}")
    st.stop()

# (아래는 기존 분석 로직과 동일합니다)
st.write("특정 씨수말의 자마들을 **성별에 따라 다르게(BMS vs Sire)** 분석합니다.")
nodes = {}; arrows_in = defaultdict(list); arrows_out = defaultdict(list)

def parse(node, parent_id=None):
    nid = node.get('ID'); text = node.get('TEXT', '').strip()
    if nid:
        nodes[nid] = {'name': text, 'parent': parent_id}
        for arrow in node.findall('arrowlink'):
            dest = arrow.get('DESTINATION')
            if dest: arrows_out[nid].append(dest); arrows_in[dest].append(nid)
    for child in node.findall('node'): parse(child, nid)
parse(root)

query = st.text_input("씨수말 이름을 입력하세요 (예: Bernardini)", "")

if query:
    target_ids = [nid for nid, info in nodes.items() if query in info['name']]
    if not target_ids: st.error(f"'{query}' 이름을 가진 말을 찾을 수 없습니다.")
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
                                bms_name = nodes[bms_id]['name'] if bms_id in nodes else "정보 없음"
                                colts.append({'child': name, 'bms': bms_name, 'link_info': nodes[mom_id]['name']})
                                seen.add(child_id)
                else:
                    if child_id in arrows_out:
                        for foal_id in arrows_out[child_id]:
                            if foal_id in nodes:
                                partner_id = nodes[foal_id]['parent']
                                partner_name = nodes[partner_id]['name'] if partner_id in nodes else "정보 없음"
                                fillies.append({'child': name, 'partner': partner_name, 'link_info': nodes[foal_id]['name']})
                                seen.add(child_id)
        
        st.success(f"분석 완료! 수말 {len(colts)}두 / 암말 {len(fillies)}두")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div style='color:#2b6cb0; font-weight:bold'>🟦 수말 (Sons)</div>", unsafe_allow_html=True)
            for c in colts: st.info(f"🐎 {c['child'].split('(')[0]} (BMS: {c['bms'].split('(')[0]})")
        with c2:
            st.markdown("<div style='color:#d53f8c; font-weight:bold'>🩷 암말 (Daughters)</div>", unsafe_allow_html=True)
            for f in fillies: st.error(f"🎀 {f['child'].split('(')[0]} (Sire: {f['partner'].split('(')[0]})")
