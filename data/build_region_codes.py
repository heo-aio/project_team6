import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.vworld.kr/ned/data/admSiList"
sido_codes = ["11", "12", "26", "27", "28", "30", "31", "36",
              "41", "43", "44", "47", "48", "50", "51", "52"]

region_codes = {}

for sido in sido_codes:
    params = {
        "key": os.getenv("VWORLD_API_KEY"),
        "domain": "https://127.0.0.1:8000",
        "admCode": sido,
        "format": "json",
        "numOfRows": 1000,
        "pageNo": 1,
    }
    res = requests.get(URL, params=params, timeout=30)
    level1 = res.json()["admVOList"]

    print(f"시도: {sido} 키 목록 : {list(level1.keys())}")

    items = level1.get("admVOList")

    print(f"totalCount: {level1["totalCount"]} 받은 개수: {len(items)}")

    for item in items:
        # 지역코드 : 지역이름
        region_codes[item["admCode"]] = item["admCodeNm"]

print(f"총 시군구 수: {len(region_codes)}")

with open("region_codes.json", "w", encoding="utf-8") as f:
    json.dump(region_codes, f, ensure_ascii=False, indent=2)