import xml.etree.ElementTree as ET
import os

def force_clean():
    file_path = 'data.mm'
    if not os.path.exists(file_path):
        print("파일이 없습니다.")
        return

    try:
        # 1. 파일 읽기
        tree = ET.parse(file_path)
        root = tree.getroot()

        # 2. 모든 텍스트를 "첫 글자만 대문자, 나머지는 소문자"로 강제 통일
        # 예: "Candy Ride" -> "Candy ride", "Storm Cat" -> "Storm cat"
        for node in root.iter('node'):
            text = node.get('TEXT', '').strip()
            if text:
                # 전체를 소문자로 만든 뒤, 맨 앞글자만 대문자로!
                clean_text = text.lower().capitalize()
                node.set('TEXT', clean_text)

        # 3. 원본 파일에 덮어쓰기 (강력하게 저장)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        print("원본 파일 청소 완료!")
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    force_clean()
