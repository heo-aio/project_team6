from vector_store import get_vectorstore
from region import region_codes, SIDO_ALIAS

vectorstore = get_vectorstore()

def region_condition(user_code):
    """chromaDB에서 지역 조건 필터링하는 함수"""
    if user_code.endswith("000"): # 시도 단위 처리 (27000이면 대구)
        sido = user_code[:2]
        candidates = set()
        for c in region_codes:
            if c.startswith(sido):
                candidates.add(c)
    else:
        candidates = {user_code, user_code[:4] + "0", user_code[:2] + "000"} # 시군구 단위

    condition = []
    for c in candidates:
        condition.append({"region": {"$contains": c}})

    if len(condition) == 1: # 1개일 때
        return condition[0]
    return {"$or": condition}

# def sido_code_from_text(text):
#     for short, full in SIDO_ALIAS.items():
#         if short in text:
#             for code, name in region_codes.items():
#                 if name.startswith(full):
#                     return code[:2] + "000"
#     return None

def search_policies(query, age=None, user_region_code=None, top_k=3):
    condition = []

    # 조건
    if age is not None:
        condition.append({"min_age": {"$lte": age}})
        condition.append({"max_age": {"$gte": age}})

    if user_region_code is not None:
        condition.append(region_condition(user_region_code))

    if len(condition) == 0:
        where = None
    elif len(condition) == 1:
        where = condition[0]
    else:
        where = {"$and": condition}

    return vectorstore.similarity_search(query, k=top_k, filter=where)


# 테스트
def show(results):
    for doc in results:
        m = doc.metadata
        if m["ref_url"] == "":
            m["ref_url"] = "없음"
        if m["apply_url"] == "":
            m["apply_url"] = "공백"
        print(f"{m['plcy_name']} | 나이 {m['min_age']}~{m['max_age']} | 참고 URL: {m["ref_url"]}\n 신청 URL: {m["apply_url"]}")
    print("-" * 20)

# test
# if __name__ == "__main__":
#     # 1단계: 변환만 따로 확인
#     tests = [
#         "대구사는 20대중반 취업준비생입니다.",
#         "서울에 살고 있어요",
#         "광주에 살아요",
#         "전남 영암에 살아요",
#         "미국에 살아요",
#     ]
#     for t in tests:
#         print(t, "→", sido_code_from_text(t))
#
#     r = search_policies("대구 청년 취업 지원", age=25, user_region_code="27000")
#     print(len(r), [d.metadata["plcy_name"] for d in r])