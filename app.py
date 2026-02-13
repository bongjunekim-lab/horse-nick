import streamlit as st
import xml.etree.ElementTree as ET
import os
from collections import defaultdict

# --- 1. 화면 설정 ---
st.set_page_config(page_title="씨수말 닉 분석기", layout="wide")

st.markdown("""
<style>
    .header { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
    .card { padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #ccc; background-color: #f9f9f9; }
    .male-card { border-left-color: #2b6cb0; }
    .female-card { border-left-color: #d53f8c; }
    .main-text { font-size: 1.1em; font-weight: bold; color: #333; }
    .sub-text { font-size: 0.9em; color: #666; margin-top: 5px; }
    .highlight { color: #c53030; font-weight: bold; }
    /* 파란 박스(st.info) 같은 건 이제 안 나오게 스타일 조정 */
</style>
""", unsafe_allow_html=True)

st.title("🐎 씨수말 닉(Nick) 분석기")

# --- 2. 데이터 로딩 (파란 박스 X-ray 화면 제거함) ---
file_path = 'data.mm'

if not os.path.exists(file_path):
    st.error("🚨 데이터 파일(data.mm)이 없습니다.")
    st.stop()

try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        xml_content = f.read()
    root = ET.fromstring(xml_content)
except Exception as e:
    st.error(f"❌ 데이터 읽기 오류: {e}")
    st.stop()

# --- 3. 데이터 분석 및 명단 확보 ---
nodes = {}
arrows_in = defaultdict(list)
arrows_out = defaultdict(list)
all_horse_names = set() 

def parse(node, parent_id=None):
    nid = node.get('ID')
    text = node.get('TEXT', '').strip()
    
    if nid:
        nodes[nid] = {'name': text, 'parent': parent_id}
        # 이름이 너무 짧거나(1글자) 이상한 건 명단에서 제외
        if len(text) > 1 and "굵게" not in text and "sansserif" not in text.lower(): 
            all_horse_names.add(text)
            
        for arrow in node.findall('arrowlink'):
            dest = arrow.get('DESTINATION')
            if dest:
                arrows_out[nid].append(dest)
                arrows_in[dest].append(nid)
                
    for child in node.findall('node'):
        parse(child, nid)

parse(root)

# 명단 가나다순 정렬 (찾기 쉽게)
sorted_names = sorted(list(all_horse_names))

# --- 4. 검색 화면 (여기가 핵심!) ---
st.write("👇 아래 상자를 클릭하고 **'ber'**나 **'버나'**라고 타이핑해보세요. 목록이 자동으로 뜹니다.")

# ★ 검색창을 '선택 상자(Selectbox)'로 만들었습니다.
# 이제 타이핑하면 목록 중에서 찾아줍니다.
selected_name = st.selectbox(
    label="검색할 말을 선택하세요:", 
    options=["(여기를 클릭해서 입력하세요)"] + sorted_names, 
    index=0
)

# --- 5. 결과 보여주기 ---
if selected_name == "(여기를 클릭해서 입력하세요)":
    st.info("👆 위 칸에 씨수말 이름을 입력하면 결과가 나옵니다.")
else:
    # 선택된 이름으로 데이터 찾기
    target_ids = [nid for nid, info in nodes.items() if info['name'] == selected_name]
    
    if not target_ids:
        st.error("데이터 오류: 이름을 선택했는데 ID를 못 찾았습니다.")
    else:
        sire_id = target_ids[0] # 첫 번째 매칭되는 ID 사용
        
        colts = []; fillies = []; seen = set()
        children = [nid for nid, info in nodes.items() if info['parent'] == sire_id]
        
        for child_id in children:
            if child_id in seen: continue
            info = nodes[child_id]; name = info['name']; is_female = '암)' in name
            
            if not is_female: # 수말
                if child_id in arrows_in:
                    for mom_id in arrows_in[child_id]:
                        if mom_id in nodes:
                            bms_id = nodes[mom_id]['parent']
                            bms_name = nodes[bms_id]['name'] if bms_id in nodes else "?"
                            colts.append({'child': name, 'bms': bms_name, 'link_info': nodes[mom_id]['name']})
                            seen.add(child_id)
            else: # 암말
                if child_id in arrows_out:
                    for foal_id in arrows_out[child_id]:
                        if foal_id in nodes:
                            partner_id = nodes[foal_id]['parent']
                            partner_name = nodes[partner_id]['name'] if partner_id in nodes else "?"
                            fillies.append({'child': name, 'partner': partner_name, 'link_info': nodes[foal_id]['name']})
                            seen.add(child_id)
        
        st.success(f"✅ **{selected_name}** 분석 완료! (수말 {len(colts)}두 / 암말 {len(fillies)}두)")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='header' style='color:#2b6cb0;'>🟦 수말 자마 (Sons: {len(colts)})</div>", unsafe_allow_html=True)
            if colts:
                for c in colts:
                    st.markdown(f"""
                    <div class='card male-card'>
                        <div class='main-text'>🐎 {c['child']}</div>
                        <div class='sub-text'>
                            어미: {c['link_info']}<br>
                            👉 <b>외조부(BMS): <span class='highlight'>{c['bms']}</span></b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("데이터 없음")

        with c2:
            st.markdown(f"<div class='header' style='color:#d53f8c;'>🩷 암말 자마 (Daughters: {len(fillies)})</div>", unsafe_allow_html=True)
            if fillies:
                for f in fillies:
                    st.markdown(f"""
                    <div class='card female-card'>
                        <div class='main-text'>🎀 {c['child']}</div>
                        <div class='sub-text'>
                            자마: {f['link_info']}<br>
                            👉 <b>교배 파트너(Sire): <span class='highlight'>{c['partner']}</span></b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("데이터 없음")
