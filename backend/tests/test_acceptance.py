import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            err_json = json.loads(content)
        except Exception:
            err_json = {"detail": content}
        return e.code, err_json

def run_tests():
    print("=" * 70)
    print("RUNNING ACCEPTANCE TEST SUITE — LIPTIS USA SALs APP")
    print("=" * 70)

    # 1. Health check
    status, res = request("/api/health")
    assert status == 200, f"Health check failed: {res}"
    print("[PASS] [TEST 0] Server Health")

    # 2. Test 1: Branding and PDF Structure
    status, event_data = request("/api/public/events/active")
    assert status == 200, "Active event fetch failed"
    assert event_data["date_display"] == "15-18 October 2026"
    
    status, details = request(f"/api/public/events/{event_data['id']}")
    assert status == 200
    sections = details["sections"]
    required_topics = [
        "welcome_letter", "umrah_rituals", "airport_arrival", "hotel_details",
        "distance_haram", "transportation", "finance_policy", "key_attractions",
        "weather", "local_time", "foreign_exchange", "electric_appliances",
        "vat_refund", "product_portfolio"
    ]
    for top in required_topics:
        assert top in sections, f"Missing PDF section: {top}"
    print(f"[PASS] [TEST 1] PDF Topics and Corporate Structure ({len(sections)} sections validated)")

    # 3. Test 2: Administrator Authentication & Editing
    status, login_res = request("/api/admin/login", method="POST", data={
        "username": "admin",
        "password": "AdminPassword2026!"
    })
    assert status == 200, f"Admin login failed: {login_res}"
    admin_token = login_res["token"]
    print("[PASS] [TEST 2.1] Administrator Authentication")

    # Test update
    status, update_res = request(f"/api/admin/events/{event_data['id']}", method="PUT", data={
        "subtitle": "Official LIPTIS Delegation 2026"
    }, token=admin_token)
    assert status == 200, f"Event update failed: {update_res}"

    # Verify unpublished changes flag
    status, full_admin_ev = request(f"/api/admin/events/{event_data['id']}", token=admin_token)
    assert full_admin_ev["event"]["has_unpublished_changes"] == 1, "Unpublished flag should be 1"

    # Publish
    status, pub_res = request(f"/api/admin/events/{event_data['id']}/publish", method="POST", token=admin_token)
    assert status == 200
    print("[PASS] [TEST 2.2] Administrator Editing & Draft-Publish Cycle")

    # 4. Test 3: Multiple Flights & Flight-Specific Itinerary Logic
    status, flights = request(f"/api/public/events/{event_data['id']}/flights")
    assert status == 200 and len(flights) >= 2, f"Expected at least 2 flight groups, got: {len(flights)}"
    
    fg1 = next(f for f in flights if "566" in f["outbound_flight_number"])
    fg2 = next(f for f in flights if "584" in f["outbound_flight_number"])

    status, itin1 = request(f"/api/public/events/{event_data['id']}/itinerary?flight_group_id={fg1['id']}")
    status, itin2 = request(f"/api/public/events/{event_data['id']}/itinerary?flight_group_id={fg2['id']}")

    d1_items_1 = itin1["dates"]["2026-10-15"]
    d1_items_2 = itin2["dates"]["2026-10-15"]

    # Verify Group 1 sees flight 566 at 09:25 AM
    has_flight_1 = any("566" in item["title"] and "9:25 AM" in item["start_time"] for item in d1_items_1)
    # Verify Group 2 sees flight 584 at 10:20 AM
    has_flight_2 = any("584" in item["title"] and "10:20 AM" in item["start_time"] for item in d1_items_2)

    assert has_flight_1, "Group 1 missing its 566 flight entry"
    assert has_flight_2, "Group 2 missing its 584 flight entry"
    # Ensure Group 1 does NOT see flight 584
    assert not any("584" in item["title"] for item in d1_items_1), "Isolation failure: Group 1 saw Group 2 flight"
    print("[PASS] [TEST 3] Multi-Flight Group Isolation & Mapping")

    # 5. Test 4: Shared Activities
    d2_items_1 = itin1["dates"]["2026-10-16"]
    d2_items_2 = itin2["dates"]["2026-10-16"]
    assert len(d2_items_1) == len(d2_items_2), "Shared day should match count"
    assert all(item["is_shared"] for item in d2_items_1), "Day 2 activities must all be marked is_shared"
    print("[PASS] [TEST 4] Shared Activity Chronological Merging")

    # 6. Test 5: Conflict Detection
    status, conflicts_res = request(f"/api/admin/events/{event_data['id']}/conflicts", token=admin_token)
    assert status == 200, "Conflict checking endpoint failed"
    print(f"[PASS] [TEST 5] Conflict Detection Engine (Identified {conflicts_res['conflict_count']} issues)")

    # 7. Test 6: Viewer Security (Strict Role-Based Access Control)
    status, unauth_res = request(f"/api/admin/events/{event_data['id']}", method="DELETE")
    assert status in [401, 403], f"Security vulnerability: Expected 401/403, got {status}"

    status, pub_hack = request("/api/public/events", method="POST", data={"title": "Hacked Event"})
    assert status in [404, 405], f"Public endpoint should not accept POST: {status}"
    print("[PASS] [TEST 6] Strict Viewer-Only RBAC & Write Protection")

    # 8. Test 7: PWA Assets (manifest.json and sw.js)
    req_man = urllib.request.Request(f"{BASE_URL}/manifest.json")
    with urllib.request.urlopen(req_man) as resp:
        manifest_json = json.loads(resp.read().decode("utf-8"))
        assert manifest_json["short_name"] == "LIPTIS SALs"

    req_sw = urllib.request.Request(f"{BASE_URL}/sw.js")
    with urllib.request.urlopen(req_sw) as resp:
        assert resp.status == 200
    print("[PASS] [TEST 7] PWA Manifest and Service Worker Assets")

    # 9. Test 8: Reusable Event Templates & Duplication
    status, dup_res = request(f"/api/admin/events/{event_data['id']}/duplicate", method="POST", token=admin_token)
    assert status == 200 and "new_event_id" in dup_res
    new_id = dup_res["new_event_id"]

    status, dup_detail = request(f"/api/admin/events/{new_id}", token=admin_token)
    assert dup_detail["event"]["title"].endswith("(Copy)")
    assert len(dup_detail["flights"]) == len(flights)
    
    status, del_res = request(f"/api/admin/events/{new_id}", method="DELETE", token=admin_token)
    assert status == 200
    print("[PASS] [TEST 8] Event Template Duplication & Isolation")

    # 10. Test 9: Contacts Verification (PDF Page 5)
    status, contacts = request(f"/api/public/events/{event_data['id']}")
    contact_list = contacts["contacts"]
    assert len(contact_list) == 10, f"Expected 10 contacts, got {len(contact_list)}"
    country_mgr = next((c for c in contact_list if "Ahmed Abd El-Mohsen" in c["name"]), None)
    assert country_mgr and country_mgr["phone"] == "+201028297898"
    print("[PASS] [TEST 9] 10 Guest Care Contacts & Verified Numbers")

    # 11. Test 10: JSON Backup Export
    status, export_data = request(f"/api/admin/events/{event_data['id']}/export", token=admin_token)
    assert status == 200 and "sections" in export_data and "itinerary" in export_data
    print("[PASS] [TEST 10] Disaster Recovery JSON Export")

    print("=" * 70)
    print("ALL 10 ACCEPTANCE TESTS PASSED SUCCESSFULLY! 100% COMPLIANT.")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
