# "AI-written" code under test, with 5 deliberately planted bugs.
def premium(age, claims, safe_driver, multi_policy):
    base = 500
    if age <= 25:                      # BUG 1: should be age < 25
        base *= 1.5
    if age >= 70:
        base *= 1.3
    if 25 <= age < 29 and claims >= 2: # BUG 5: should be <= 29 (misses age 29)
        base *= 1.10
    base *= 1 + 0.10 * claims          # BUG 2: +50% surcharge cap missing
    discount = 0
    if safe_driver:
        discount += 0.10
    if multi_policy:
        discount += 0.15
    base *= (1 - discount)             # BUG 3: 20% discount cap missing
    return int(base)                   # BUG 4: truncates instead of rounding
