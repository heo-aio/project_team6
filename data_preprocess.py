import json

"""
plcyNo : 정책고유 ID
plcyNm : 정책명, plcyKywdNm : 정책키워드, plcyExplnCn : 정책설명, plcySprtCn : 정책지원내용
bizPrdBgngYmd : 시작일자, bizPrdEndYmd : 종료일자
aplyUrlAddr : 신청URL, refUrlAddr1 : 참고URL, aplyYmd : 신청기간, plcyAplyMthdCn : 신청방법
sprtTrgtMinAge, sprtTrgtMaxAge, sprtTrgtAgeLmtYn -> 나이제한관련
zipCd : 정책거주지역코드
lclsfNm : 정책대분류명, mclsfNm : 중분류명
sprvsnInstCdNm : 주관 기관 코드
"""

with open("policies_raw.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

policies = raw["policies"]
# print(type(raw))
# print(len(policies)) # 3378
# print(policies[0]["plcyNm"]) # 청년농업인양성아카데미

def build_text(p):
    name = p.get("plcyNm", "").strip()                          # 정책이름
    field = f"{p.get("lclsfNm", "")} - {p.get("mclsfNm", "")}"  # 정책대분류명 - 중분류명
    keyword = p.get("plcyKywdNm", "").strip()                   # 정책키워드
    explain = p.get("plcyExplnCn", "").strip()                  # 정책설명
    support = p.get("plcySprtCn", "").strip()                   # 정책지원 description

    return "\n".join([
        f"정책명 : {name}",
        f"정책 분야 : {field}",
        f"키워드 : {keyword}",
        f"정책 설명 : {explain}",
        f"정책 지원내용 : {support}"
    ])

# print(build_text(policies[0]))

def build_metadata(p):
    return {
        "plcy_no": p.get("plcyNo", "").strip(),
        "plcy_name": p.get("plcyNm", "").strip(),
        "min_age": int(p.get("sprtTrgtMinAge") or 0),
        "max_age": int(p.get("sprtTrgtMaxAge") or 0),
        "age_limit_yn": p.get("sprtTrgtAgeLmtYn", ""),
        "apply_period": p.get("aplyYmd", "").strip(),
        "apply_url": p.get("aplyUrlAddr", "").strip(),
        "ref_url": p.get("refUrlAddr1", "").strip(),
        "region": p.get("zipCd", "").strip(),
    }

result = []
for p in policies:
    result.append({
        "id" : p["plcyNo"],
        "text" : build_text(p),
        "metadata" : build_metadata(p)
    })

# 저장
with open("policies_clean.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"전처리 완료: {len(result)}건")
