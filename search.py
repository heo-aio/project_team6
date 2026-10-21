from vector_store import get_vectorstore
from filters import age_pass, region_pass

vectorstore = get_vectorstore()


def search_policies(query, age, user_region_code, top_k=3, fetch_k=100):
    candidates = vectorstore.similarity_search(query, k=fetch_k)

    passed = []
    for doc in candidates:
        md = doc.metadata
        if age_pass(md, age) and region_pass(md, user_region_code):
            passed.append(doc)

    return passed[:top_k]


if __name__ == "__main__":
    for code in ["47840", "11110"]: # 임의로 아무거나 넣음
        print(f"--- 지역 코드 {code} ---")
        results = search_policies("창업 지원 받고 싶어요", age=32, user_region_code=code)
        for doc in results:
            m = doc.metadata
            print(f"{m['plcy_name']} | 나이 {m['min_age']}~{m['max_age']} | {m['ref_url']}")