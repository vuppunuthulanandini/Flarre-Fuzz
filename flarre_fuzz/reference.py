"""Trusted, correct implementation of data/spec.txt (the Referee's yardstick)."""

def premium(age: int, claims: int, safe_driver: bool, multi_policy: bool) -> float:
    base = 500.0
    if age < 25:
        base *= 1.5
    if age >= 70:
        base *= 1.3
    if 25 <= age <= 29 and claims >= 2:
        base *= 1.10
    base *= 1 + min(0.10 * claims, 0.50)
    discount = min((0.10 if safe_driver else 0) + (0.15 if multi_policy else 0), 0.20)
    base *= 1 - discount
    return round(base, 2)
