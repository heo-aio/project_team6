from vector_store import get_vectorstore
from filters import age_pass, region_pass
from region import get_region_code

vectorstore = get_vectorstore()


def search_policies(query, age, user_region_code, top_k=3, fetch_k=100):
    candidates = vectorstore.similarity_search(query, k=fetch_k)

    passed = []
    for doc in candidates:
        md = doc.metadata
        if age_pass(md, age) and region_pass(md, user_region_code):
            passed.append(doc)

    return passed[:top_k]

def search_by_region_name(query, age, sido, sigungu, top_k=3, fetch_k=100):
    code = get_region_code(sido, sigungu)
    if code is None:
        raise ValueError(f"해당되는 지역이 없습니다.: {sido} {sigungu}")
    return search_policies(query, age, code, top_k=top_k, fetch_k=fetch_k)


if __name__ == "__main__":
    for code in ["47840", "11110"]: # 임의로 아무거나 넣음 47 : 경북 11 : 서울
        print(f"--- 지역 코드 {code} ---")
        # results = search_policies("창업 지원 받고 싶어요", age=32, user_region_code=code)
        results = search_policies("청년농업인 교육", age=32, user_region_code=code)
        for doc in results:
            m = doc.metadata
            print(f"{m['plcy_name']} | 나이 {m['min_age']}~{m['max_age']} | {m['ref_url']}")

    print("--- 이름으로 검색 ---")
    results = search_by_region_name("월세 지원", 27, "미국", "세종특별자치시")
    for doc in results:
        print(doc.metadata["plcy_name"])

# --- 지역 코드 47840 ---
# 창업성공패키지(청년창업사관학교) | 나이 1~39 | https://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=310&bcIdx=1065207&parentSeq=1065207
# 신월지역 청년점포 및 청년기업 육성사업 참여자 추가모집 공고 | 나이 19~39 | https://www.yangcheon.go.kr/site/yangcheon/ex/seol/seolContentDeailView.do?not_ancmt_mgt_no=44446
# 창업도약패키지(대기업협업형) 창업기업 모집 | 나이 0~0 |
# --- 지역 코드 11110 ---
# 창업성공패키지(청년창업사관학교) | 나이 1~39 | https://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=310&bcIdx=1065207&parentSeq=1065207
# 신월지역 청년점포 및 청년기업 육성사업 참여자 추가모집 공고 | 나이 19~39 | https://www.yangcheon.go.kr/site/yangcheon/ex/seol/seolContentDeailView.do?not_ancmt_mgt_no=44446
# 창업도약패키지(대기업협업형) 창업기업 모집 | 나이 0~0 |
# -> 47이 경북인데 양천구쪽 데이터가 나오는 이유 : 이 정책의 지역 코드에 전국 코드가 모두 들어 있음 (check_filter.py에서 확인)