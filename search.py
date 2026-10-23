from vector_store import get_vectorstore
from region import get_region_code

vectorstore = get_vectorstore()


def region_condition(user_code):
    """chromaDB에서 지역 조건 필터링하는 함수"""
    candidates = {user_code, user_code[:4] + "0", user_code[:2] + "000"}

    condition = []
    for c in candidates:
        condition.append({"region": {"$contains": c}})

    if len(condition) == 1: # 1개일 때
        return condition[0]
    return {"$or": condition}


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

if __name__ == "__main__":
    show(search_policies("청년농업인 교육", 32, "47840")) # 둘 다
    show(search_policies("청년농업인 교육", age=15))            # ② 나이만
    show(search_policies("청년농업인 교육", user_region_code="47840"))  # 지역만
    show(search_policies("청년농업인 교육"))                    # 없음