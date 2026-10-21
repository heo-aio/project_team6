import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.vworld.kr/ned/data/admSiList"

# 정책 데이터에 등장한 시도 앞 2자리
sido_codes = ["11", "12", "26", "27", "28", "30", "31", "36",
              "41", "43", "44", "47", "48", "50", "51", "52"]

raw = {}
for sido in sido_codes:
    params = {
        "key": os.getenv("VWORLD_API_KEY"),
        "domain": "https://127.0.0.1:8000",
        "admCode": sido,
        "format": "json",
        "numOfRows": 1000,
        "pageNo": 1,
    }

res = requests.get(url, params=params, timeout=30)

data = res.json()
# print(type(data))
# print(list(data.keys()))

level1 = data["admVOList"]
# print(type(level1))
# print(list(level1.keys()))

items = level1["admVOList"]
# print(type(items))
# print(len(items))
# print(items[0])

# 지역코드 : 지역이름
region_codes = {}

for item in items:
    code = item["admCode"]
    name = item["admCodeNm"]
    region_codes[code] = name

print(len(region_codes))
print(region_codes)