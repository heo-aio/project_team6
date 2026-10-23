import json

with open("region_codes.json", "r", encoding="utf-8") as f:
    region_codes = json.load(f)

SIDO_ALIAS = {
    "서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시",
    "인천": "인천광역시", "대전": "대전광역시", "울산": "울산광역시",
    "세종": "세종특별자치시", "경기": "경기도", "강원": "강원특별자치도",
    "충북": "충청북도", "충남": "충청남도", "전북": "전북특별자치도",
    "경북": "경상북도", "경남": "경상남도", "제주": "제주특별자치도",
    "광주": "전남광주통합특별시", "전남": "전남광주통합특별시",
}

def get_sido_list():
    """시도 이름 목록 (중복 없이, 등장 순서 유지)"""
    sidos = []
    for name in region_codes.values():
        sido = name.split(" ", 1)[0]
        if sido not in sidos:
            sidos.append(sido)
    return sidos


def get_sigungu_list(sido):
    """해당 시도의 시군구 이름 목록"""
    result = []
    for name in region_codes.values():
        parts = name.split(" ", 1)
        if parts[0] == sido and len(parts) == 2:
            result.append(parts[1])
    return result


def get_region_code(sido, sigungu):
    """('서울특별시', '강남구') -> '11680'. 없으면 None으로 반환"""
    full_name = f"{sido} {sigungu}"
    for code, name in region_codes.items():
        if name == full_name:
            return code
    return None

# 테스트
# if __name__ == "__main__":
    # print(get_sido_list())
    # print(get_sigungu_list("서울특별시")[:5])
    # print(get_region_code("서울특별시", "강남구")) # 11680
    # print(get_region_code("전남광주통합특별시", "북구")) # 12300
    # print(get_region_code("없는시", "없는구")) # None