import xml.etree.ElementTree as ET
import os

def title_case_plus(text):
    # 단어별로 쪼개서 첫 글자만 대문자, 나머지는 소문자로 (예: KITTEN'S JOY -> Kitten's Joy)
    # 하지만 선생님의 요청대로 '첫 단어만 대문자'로 하려면 capitalize()가 좋습니다.
    # 여기서는 가장 검색이 잘 되는 '전체 소문자 후 첫 글자만 대문자' 방식을 씁니다.
    return text.lower().capitalize()

try:
    if os.path.exists('data.mm'):
        tree = ET.parse('data.mm')
        root = tree.getroot()

        for node in root.iter('node'):
            text = node.get('TEXT', '').strip()
            if text:
                # ★ 선생님의 규칙: "모든 마명을 '첫글자만 대문자'로 통일"
                # 예: "Storm Cat" -> "Storm cat", "Kitten's Joy" -> "Kitten's joy"
                fixed_text = text.lower().capitalize()
                node.set('TEXT', fixed_text)

        tree.write('data.mm', encoding='utf-8', xml_declaration=True)
        print("원본 데이터 표준화 성공!")
except Exception as e:
    print(f"오류: {e}")
