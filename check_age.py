import json
from collections import Counter

with open("policies_raw.json", "r", encoding="utf-8") as f:
    policies = json.load(f)["policies"]



counter = Counter(
    (p.get("sprtTrgtAgeLmtYn"), p.get("sprtTrgtMinAge"), p.get("sprtTrgtMaxAge"))
    for p in policies
)
