import streamlit as st
import xml.etree.ElementTree as ET
import os
from collections import defaultdict

# 페이지 설정
st.set_page_config(page_title="씨수말 닉(Nick) 추적기", layout="wide")
st.title("🧐 데이터 파일 엑스레이(X-Ray) 검사")

file_path = 'data.mm'

# 1. 파일 존재 여부 확인
if not os.path.exists(file_path):
    st.error("🚨 'data.mm' 파일이 앱에 없습니다! (깃허브에는 있어도 앱이 다운로드를 못한 상태)")
    st.stop()

# 2. 파일 내용 직접 읽어보기 (엑스레이)
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        # 앞부분 500글자만 읽어옵니다
        content_head = f.read(500)
        
    if len(content_head.strip()) == 0:
        st.error("🚨 파일은 있는데 **속이 텅 비어있습니다!**")
        st.info("해결책: GitHub에서 'data.mm'을 열고 내용을 다시 붙여넣으세요.")
        st.stop()
    else:
        st.success("✅ 파일 내용을 읽었습니다! 아래 파란 박스 내용을 확인해주세요.")
        st.info("👇 **파일의 첫 500글자 미리보기**")
        st.code(content_head) # 여기에 파일 앞부분이 그대로 나옵니다!

    # 3. XML 파싱 시도
    root = ET.fromstring(f.read()) if 'f' not in locals() else ET.parse(file_path).getroot()

except Exception as e:
    # 여기서 에러가 나면 파일 내용 문제입니다
    st.warning("⚠️ 내용은 있지만 XML 형식이 아닙니다. (아래 미리보기를 보면 원인을 알 수 있습니다)")
    st.error(f"에러 메시지: {e}")
    st.stop()

# --- 4. 검사 통과 시 정상 실행 ---
st.success("🎉 데이터 정상! 분석기를 실행합니다.")
st.divider()

# (기존 분석 로직)
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
    if not target_ids: st.error(f"'{query}' 없음")
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
        st.success(f"수말 {len(colts)} / 암말 {len(fillies)}")
        c1, c2 = st.columns(2)
        with c1: 
            for c in colts: st.info(f"🐎 {c['child']} (BMS: {c['bms']})")
        with c2: 
            for f in fillies: st.error(f"🎀 {f['child']} (Sire: {f['partner']})")
