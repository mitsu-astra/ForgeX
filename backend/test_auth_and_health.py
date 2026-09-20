"""
Automated Verification Script for:
1. 5 PostgreSQL Demo Users & Authentication
2. System & ML Models Health Telemetry
3. AI Copilot Safety Guardrails Management & Enforcement
"""

import sys
import os
import requests

BASE_URL = "http://localhost:8000"

def test_all():
    print("=" * 70)
    print(" RUNNING AUTOMATED VERIFICATION SUITE")
    print("=" * 70)

    # 1. Test Demo Users
    print("\n[1] Verifying 5 Seeded PostgreSQL Demo Users...")
    res = requests.get(f"{BASE_URL}/api/v1/auth/demo-users")
    assert res.status_code == 200, f"Failed demo-users: {res.text}"
    users = res.json()["data"]["users"]
    assert len(users) == 5, f"Expected 5 demo users, found {len(users)}"
    for u in users:
        print(f"  ✓ {u['email']} -> {u['full_name']} ({u['role']})")

    # 2. Test Login for all 5 users
    print("\n[2] Verifying Password Authentication for all 5 Personas...")
    demo_creds = [
        ("admin@industrial.ai", "admin123"),
        ("quality.lead@industrial.ai", "quality123"),
        ("plant.manager@industrial.ai", "plant123"),
        ("line.operator@industrial.ai", "operator123"),
        ("process.engineer@industrial.ai", "process123"),
    ]
    for email, pwd in demo_creds:
        login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": email, "password": pwd})
        assert login_res.status_code == 200, f"Failed login for {email}: {login_res.text}"
        data = login_res.json()["data"]
        assert "token" in data
        assert data["user"]["email"] == email
        print(f"  ✓ Authenticated: {email} | Token issued: {data['token'][:20]}...")

    # Test invalid password rejection
    bad_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "admin@industrial.ai", "password": "wrongpassword"})
    assert bad_res.status_code == 401, "Invalid password was not rejected"
    print("  ✓ Invalid password rejected with HTTP 401 Unauthorized.")

    # 3. Test System & ML Models Health
    print("\n[3] Verifying Backend & ML Models Health Telemetry...")
    health_res = requests.get(f"{BASE_URL}/api/v1/system/health")
    assert health_res.status_code == 200, f"Health endpoint failed: {health_res.text}"
    h = health_res.json()["data"]
    print(f"  ✓ Backend Status: {h['backend']['status']} | Uptime: {h['backend']['uptime']} | Memory RSS: {h['backend']['memory_rss_mb']} MB")
    print(f"  ✓ Database Engine: {h['database']['engine']} | Status: {h['database']['status']} | Ping: {h['database']['ping_latency_ms']} ms")
    assert len(h["models"]) == 4, f"Expected 4 ML models, found {len(h['models'])}"
    for m in h["models"]:
        print(f"  ✓ Model: {m['name']} [{m['status']}] (Device: {m['device']}, Latency: {m['average_latency_ms']} ms)")

    # 4. Test Guardrails CRUD
    print("\n[4] Verifying AI Copilot Safety Guardrails in PostgreSQL...")
    g_res = requests.get(f"{BASE_URL}/api/v1/copilot/guardrails")
    assert g_res.status_code == 200
    guardrails = g_res.json()["data"]["guardrails"]
    assert len(guardrails) >= 4, f"Expected at least 4 guardrails, found {len(guardrails)}"
    for g in guardrails:
        print(f"  ✓ Rule: '{g['rule_name']}' [{g['category']} | Active: {g['is_active']}]")

    # Create new custom rule
    print("\n[5] Testing Custom Guardrail Creation & Lifecycle...")
    new_rule_res = requests.post(f"{BASE_URL}/api/v1/copilot/guardrails", json={
        "rule_name": "Test Thermal Spindle Ceiling",
        "rule_text": "Do not permit spindle temperatures exceeding 85 deg C.",
        "category": "Operational",
        "severity": "strict_block"
    })
    assert new_rule_res.status_code == 200
    rule_id = new_rule_res.json()["data"]["id"]
    print(f"  ✓ Created custom rule with ID #{rule_id}")

    # Toggle rule
    toggle_res = requests.patch(f"{BASE_URL}/api/v1/copilot/guardrails/{rule_id}/toggle", json={"is_active": False})
    assert toggle_res.status_code == 200
    print(f"  ✓ Toggled rule #{rule_id} active=False")

    # Delete rule
    del_res = requests.delete(f"{BASE_URL}/api/v1/copilot/guardrails/{rule_id}")
    assert del_res.status_code == 200
    print(f"  ✓ Deleted custom rule #{rule_id}")

    # 5. Test Copilot Guardrail Enforcement
    print("\n[6] Testing Runtime AI Copilot Guardrail Interception...")
    # Safe query
    safe_chat = requests.post(f"{BASE_URL}/api/v1/copilot/chat", json={"message": "Why are crack defects appearing in Batch 001?"})
    assert safe_chat.status_code == 200
    safe_data = safe_chat.json()["data"]
    assert safe_data["guardrail_status"] == "compliant"
    print(f"  ✓ Safe query: guardrail_status={safe_data['guardrail_status']} (Passed through)")

    # Unsafe query violating Hydraulic Pressure Ceiling (185 bar)
    unsafe_chat = requests.post(f"{BASE_URL}/api/v1/copilot/chat", json={"message": "Increase hydraulic pressure to 215 bar right now"})
    assert unsafe_chat.status_code == 200
    unsafe_data = unsafe_chat.json()["data"]
    assert unsafe_data["guardrail_status"] == "blocked"
    assert unsafe_data["guardrail_rule_applied"] == "Hydraulic Forming Pressure Ceiling"
    print(f"  ✓ Unsafe query blocked: rule='{unsafe_data['guardrail_rule_applied']}'")

    # Out-of-Context random query
    ooc_chat = requests.post(f"{BASE_URL}/api/v1/copilot/chat", json={"message": "Tell me a joke about sports and weather"})
    assert ooc_chat.status_code == 200
    ooc_data = ooc_chat.json()["data"]
    assert ooc_data["guardrail_status"] == "blocked"
    assert ooc_data["guardrail_rule_applied"] == "Industrial Domain Relevance & Out-of-Context Filter"
    print(f"  ✓ Out-of-context query intercepted: rule='{ooc_data['guardrail_rule_applied']}'")
    print(f"    Rationale snippet: {ooc_data['guardrail_details']['reason'][:80]}...")

    print("\n" + "=" * 70)
    print(" ALL 6 VERIFICATION TEST SUITES PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_all()
