import json

# 정책 json 데이터
with open("policies_raw.json", "r", encoding="utf-8") as f:
    policies = json.load(f)["policies"]

# build_region_codes에서 만들었음
with open("region_codes.json", "r", encoding="utf-8") as f:
    region_codes = json.load(f)

# 대조
data_codes = set()
for p in policies:
    for c in p["zipCd"].split(","):
        data_codes.add(c)

vworld_codes = set(region_codes.keys())

print("기존 정책 데이터에만 있는 코드:", sorted(data_codes - vworld_codes))
print("VWorld에만 있는 코드:", sorted(vworld_codes - data_codes)) # 값 없음 -> 모든 지역코드 데이터가 기존 정책 데이터에 쓰였다