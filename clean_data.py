import xml.etree.ElementTree as ET
import os

# 원본 data.mm 파일을 읽어서 모든 마명을 'Storm cat' 형식으로 표준화합니다.
try:
    if os.path.exists('data.mm'):
        # 파일 읽기
        tree = ET.parse('data.mm')
        root = tree.getroot()

        # 모든 노드를 돌며 텍스트 수정
        for node in root.iter('node'):
            text = node.get('TEXT', '').strip()
            if text:
                # ★ 선생님의 규칙: 전체 소문자로 만든 뒤, 맨 앞글자만 대문자로!
                # 예: "Storm Cat" -> "Storm cat", "MEDAGLIA" -> "Medaglia"
                fixed_text = text.lower().capitalize()
                node.set('TEXT', fixed_text)

        # 수정된 내용을 원본 파일(data.mm)에 덮어쓰기
        tree.write('data.mm', encoding='utf-8', xml_declaration=True)
        print("성공! 모든 마명이 표준화되었습니다.")
    else:
        print("data.mm 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류 발생: {e}")
