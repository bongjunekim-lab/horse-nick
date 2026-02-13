import streamlit as st
import xml.etree.ElementTree as ET
import os
from collections import defaultdict

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="씨수말 닉(Nick) 추적기", layout="wide")

st.markdown("""
<style>
    .header { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
    .card { padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #ccc; background-color: #f9f9f9; }
    .male-card { border-left-color: #2b6cb0; }
    .female-card { border-left-color: #d53f8c; }
    .main-text { font-size: 1.1em; font-weight: bold; color: #333; }
    .sub-text { font-size: 0.9em; color: #666; margin-top: 5px; }
    .highlight { color: #c53030; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. 데이터 분석 로직 ---
@st.cache_data
def analyze_pedigree(target_name):
    # ★ 수정 완료: 파일 이름을 'data.mm'으로 고정했습니다!
    file_path = 'data.mm'
    
    if not os.path.exists(file_path):
        return None, "❌ 'data.mm' 파일을 찾을 수 없습니다. (깃허브에 'data.mm' 파일을 만들고 내용을 붙여넣었는지 확인해주세요)"

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        nodes = {}       
        arrows_in = defaultdict(list)
        arrows_out = defaultdict(list)

        def parse(node, parent_id=None):
            nid = node.get('ID')
            text = node.get('TEXT', '').strip()
            if nid:
                nodes[nid] = {'name': text, 'parent': parent_id}
                for arrow in node.findall('arrowlink'):
                    dest = arrow.get('DESTINATION')
                    if dest:
                        arrows_out[nid].append(dest)
                        arrows_in[dest].append(nid) 
            for child in node.findall('node'):
                parse(child, nid)

        parse(root)

        target_ids = [nid for nid, info in nodes.items() if target_name in info['name']]
        
        if not target_ids:
            return None, f"'{target_name}' 이름을 가진 말을 찾을 수 없습니다."

        colts = []   
        fillies = [] 
        seen = set() 

        for sire_id in target_ids:
            children = [nid for nid, info in nodes.items() if info['parent'] == sire_id]
            
            for child_id in children:
                if child_id in seen: continue
                
                info = nodes[child_id]
                name = info['name']
                is_female = '암)' in name
                
                if not is_female:
                    if child_id in arrows_in:
                        mother_ids = arrows_in[child_id]
                        for mom_id in mother_ids:
                            if mom_id in nodes:
                                mom_name = nodes[mom_id]['name']
                                bms_id = nodes[mom_id]['parent']
                                bms_name = nodes[bms_id]['name'] if bms_id and bms_id in nodes else "정보 없음"
                                colts.append({'child': name, 'bms': bms_name, 'link_info': mom_name})
                                seen.add(child_id)
                else:
                    if child_id in arrows_out:
                        foal_ids = arrows_out[child_id]
                        for foal_id in foal_ids:
                            if foal_id in nodes:
                                foal_name = nodes[foal_id]['name']
                                partner_id = nodes[foal_id]['parent']
                                partner_name = nodes[partner_id]['name'] if partner_id and partner_id in nodes else "정보 없음"
                                fillies.append({'child': name, 'partner': partner_name, 'link_info': foal_name})
                                seen.add(child_id)
                                
        return (colts, fillies), None

    except Exception as e:
        return None, f"에러 발생: {e}"

# --- 3. 화면 표시 ---
st.title("🐎 씨수말 닉(Nick) 분석기")
st.write("특정 씨수말의 자마들을 **성별에 따라 다르게(BMS vs Sire)** 분석합니다.")

query = st.text_input("씨수말 이름을 입력하세요 (예: Bernardini)", "")

if query:
    result, err = analyze_pedigree(query)
    
    if err:
        st.error(err)
    else:
        colts, fillies = result
        st.success(f"분석 완료! 수말 {len(colts)}두 / 암말 {len(fillies)}두 발견")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("<div class='header' style='color:#2b6cb0;'>🟦 수말 자마 (Sons)</div>", unsafe_allow_html=True)
            if colts:
                for c in colts:
                    child_clean = c['child'].split('(')[0]
                    bms_clean = c['bms'].split('(')[0]
                    st.markdown(f"""<div class='card male-card'><div class='main-text'>🐎 {child_clean}</div><div class='sub-text'>어미: {c['link_info'].split('(')[0]}<br>👉 <b>외조부(BMS): <span class='highlight'>{bms_clean}</span></b></div></div>""", unsafe_allow_html=True)
            else:
                st.info("데이터 없음")
                
        with c2:
            st.markdown("<div class='header' style='color:#d53f8c;'>🩷 암말 자마 (Daughters)</div>", unsafe_allow_html=True)
            if fillies:
                for f in fillies:
                    child_clean = f['child'].split('(')[0]
                    partner_clean = f['partner'].split('(')[0]
                    st.markdown(f"""<div class='card female-card'><div class='main-text'>🎀 {child_clean}</div><div class='sub-text'>생산 자마: {f['link_info'].split('(')[0]}<br>👉 <b>교배 파트너(Sire): <span class='highlight'>{partner_clean}</span></b></div></div>""", unsafe_allow_html=True)
            else:
                st.info("데이터 없음")
