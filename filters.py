def age_pass(md, age):
    low, high = md["min_age"], md["max_age"]
    if low and age < low:
        return False
    if high and age > high:
        return False
    return True


def region_pass(md, user_code):
    zips = set(md["region"].split(","))
    candidates = {
        user_code,  # 시군구 일치 (44131)
        user_code[:4] + "0",  # 시 단위 코드 (44130)
        user_code[:2] + "000", # 시도 단위 코드 (44000)
    }
    return bool(zips & candidates)