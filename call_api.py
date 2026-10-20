import os
import requests
from dotenv import load_dotenv
import math
import json
from datetime import date

load_dotenv()
url = "https://www.youthcenter.go.kr/go/ythip/getPlcy"
params = {"apiKeyNm" : os.getenv("API_KEY"), "pageNum" : 1, "pageSize" : 100, "rtnType" : "json"}

res = requests.get(url, params=params)
# print(f"status : {res.status_code}")

"""
# plcyNm : 정책명, plcyKywdNm : 정책키워드, plcyExplnCn : 정책설명, plcySprtCn : 정책지원내용
# bizPrdBgngYmd : 시작일자, bizPrdEndYmd : 종료일자
# aplyUrlAddr : 신청URL, refUrlAddr1 : 참고URL, aplyYmd : 신청기간, plcyAplyMthdCn : 신청방법
"""

data = res.json() # 데이터 원본
# policies = data["result"]["pagging"]
# print(policies[0])
# print(data["result"]["youthPolicyList"][0]["plcyNm"])
print(data["result"]["pagging"]["totCount"])
# print(data)

totCount = data["result"]["pagging"]["totCount"]
page_size = 100
all_policies = []
last_page = math.ceil(totCount / page_size)

for page in range(1, last_page + 1):
    params['pageNum'] = page
    params['pageSize'] = page_size
    res = requests.get(url, params=params)
    item = res.json()["result"]["youthPolicyList"]

    all_policies.extend(item)

    print(f"page = {page}, 누적 총 데이터 {len(all_policies)}건")

# 중복되는 데이터 걸러내기
unique = {p["plcyNo"]: p for p in all_policies}
all_policies = list(unique.values())
print(f"중복 제거 후 {len(all_policies)}건")

with open("policies_raw.json", "w", encoding="utf-8") as f:
    json.dump(
        {"collected_at": str(date.today()), "totCount": totCount, "policies": all_policies},
        f, ensure_ascii=False, indent=2,
    )