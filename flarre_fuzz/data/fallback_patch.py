def premium(age, claims, safe_driver, multi_policy):
    base = 500
    if age < 25:
        base *= 1.5
    if age >= 70:
        base *= 1.3
    if 25 <= age <= 29 and claims >= 2:
        base *= 1.10
    base *= 1 + min(0.10 * claims, 0.50)
    discount = 0
    if safe_driver:
        discount += 0.10
    if multi_policy:
        discount += 0.15
    base *= (1 - min(discount, 0.20))
    return round(base, 2)
