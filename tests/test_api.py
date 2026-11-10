def test_full_flow(client):
    assert client.get("/health").json()["status"] == "ok"
    r = client.post("/scans", json={})
    assert r.status_code == 201
    s = r.json()
    assert s["initial_failures"] > 0 and s["remaining_failures"] == 0
    assert s["status"] == "pending_review" and s["patch_source"] in {"llm", "fallback"}
    assert {"matches_reference", "max_premium_cap", "discount_cap_20pct"} <= set(s["failures_by_rule"])
    sid = s["id"]
    assert client.get(f"/scans/{sid}").json()["id"] == sid
    d = client.post(f"/scans/{sid}/decision", json={"decision": "approved", "reason": "re-test clean"})
    assert d.status_code == 200
    assert client.post(f"/scans/{sid}/decision", json={"decision": "rejected"}).status_code == 409
    events = [a["event"] for a in client.get("/audit").json()]
    assert events == ["human_decision", "scan_completed"]

def test_not_found_and_validation(client):
    assert client.get("/scans/999").status_code == 404
    assert client.post("/scans/999/decision", json={"decision": "approved"}).status_code == 404
    assert client.post("/scans", json={"layers": ["nonsense"]}).status_code == 422
    assert client.post("/scans/1/decision", json={"decision": "maybe"}).status_code == 422

def test_ui_ablation_and_enriched_scan(client):
    assert "Flarre-Fuzz" in client.get("/").text
    s = client.post("/scans", json={}).json()
    assert s["repros"] and s["coverage"]["tested"] and "llm_configured" in client.get("/health").json()
    m = client.get("/ablation").json()
    assert m["bugs"]["mid_range_boundary"]["boundary only"] == 0
    assert set(m["false_alarms"].values()) == {0}
