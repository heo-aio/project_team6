import json

with open("region_codes.json", "r", encoding="utf-8") as f:
    region_codes = json.load(f)

def get_sido_code(sido):
    """'대구광역시' -> '27000' (시도 단위 코드). 없으면 None"""
    for code, name in region_codes.items():
        if name.startswith(sido + " "):
            return code[:2] + "000"
    return None

def get_sido_list():
    """시도 이름 목록 (중복 없이, 등장 순서 유지)"""
    sidos = []
    for name in region_codes.values():
        sido = name.split(" ", 1)[0]
        if sido not in sidos:
            sidos.append(sido)
    return sidos


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