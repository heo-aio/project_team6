import json
from collections import Counter

with open("policies_raw.json", "r", encoding="utf-8") as f:
    policies = json.load(f)["policies"]

region_code = []

# 결측값 확인
for p in policies:
    region = p.get("zipCd", "").strip()
    region_code.append(region)

region_counter = Counter(region_code)

# print(f"region_code = {region_code}")
print(region_counter)

cnt = 0

for z in region_code:
    if not z:
        cnt += 1

total_region = len(region_code)

# print(f"결측값 = {cnt}개 \n총 갯수 = {total_region}개") # 결측값 = 0개 총 갯수 = 3378개 -> 일단 비어있는 지역코드 X

# 정책 당 지역 코드 개수 분포확인
num_code = Counter()

for z in region_code:
    n = len(z.split(","))
    # print(n)
    num_code[n] += 1

# 해당 지역코드가 몇 개의 정책에 있는지
length = Counter()
for z in region_code:
    for c in z.split(","):
        length[len(c)] += 1

# print(f"num_code : {num_code}")
print(sorted(num_code.items())[:10])
print(sorted(num_code.items())[-10:])
print(f"length : {length}") # 지역코드는 전부 5글자

def region_filter(md, user_code):
    return user_code in md['region'].split(",")

# 테스트
# print(region_filter({"region": "47111,47113"}, "47111")) # True
# print(region_filter({"region": "47111,47113"}, "11110")) # False
# print(region_filter({"region": "11110"}, "11110")) # True