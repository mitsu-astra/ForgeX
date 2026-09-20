import sys
import os
from fastapi.testclient import TestClient

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.main import app

client = TestClient(app)

def test_control_pipeline():
    print("\n=======================================================")
    print(" TESTING MANUAL OPERATOR CONTROL LAYER (HITL & SIMULATOR)")
    print("=======================================================")

    # 1. Test GET /api/v1/control/state
    print("\n[1/7] Testing GET /api/v1/control/state...")
    res = client.get("/api/v1/control/state")
    assert res.status_code == 200, f"Failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    assert data["data"]["mode"] == "SIMULATION MODE"
    assert "hydraulic_pressure" in data["data"]["parameters"]
    curr_pressure = data["data"]["parameters"]["hydraulic_pressure"]["measured_value"]
    print(f"  [+] Machine Telemetry Status: {data['data']['mode']}")
    print(f"  [+] Hydraulic Pressure: Measured={curr_pressure} bar, Status={data['data']['parameters']['hydraulic_pressure']['status']}")

    # 2. Test Validation: Safe value
    print("\n[2/7] Testing POST /api/v1/control/validate (Safe value = 172.0 bar)...")
    res_val_safe = client.post("/api/v1/control/validate", json={"parameter": "hydraulic_pressure", "value": 172.0})
    assert res_val_safe.status_code == 200
    safe_data = res_val_safe.json()
    assert safe_data["success"] is True
    assert safe_data["data"]["is_valid"] is True
    print(f"  [+] Validation Passed: {safe_data['message']}")

    # 3. Test Validation: Unsafe value (exceeds 180 bar max limit)
    print("\n[3/7] Testing POST /api/v1/control/validate (Unsafe value = 215.0 bar)...")
    res_val_unsafe = client.post("/api/v1/control/validate", json={"parameter": "hydraulic_pressure", "value": 215.0})
    assert res_val_unsafe.status_code == 200
    unsafe_data = res_val_unsafe.json()
    assert unsafe_data["success"] is False
    assert unsafe_data["data"]["is_valid"] is False
    assert unsafe_data["data"]["status_level"] == "blocked"
    print(f"  [+] Correctly Blocked: {unsafe_data['message']}")

    # 4. Test Proposal Creation
    print("\n[4/7] Testing POST /api/v1/control/propose (Propose 172.0 bar)...")
    res_prop = client.post(
        "/api/v1/control/propose",
        json={
            "parameter": "hydraulic_pressure",
            "value": 172.0,
            "source": "manual",
            "operator_id": "OP-104",
            "notes": "Calibrating pressure to mitigate crack formation",
        },
    )
    assert res_prop.status_code == 200
    prop_data = res_prop.json()
    proposal_id = prop_data["data"]["proposal_id"]
    conf_token = prop_data["data"]["confirmation_token"]
    assert prop_data["data"]["is_valid"] is True
    assert prop_data["data"]["requires_confirmation"] is True
    print(f"  [+] Change Proposal Generated: ID={proposal_id}, Token={conf_token[:15]}...")

    # 5. Test Confirmation & Application
    print("\n[5/7] Testing POST /api/v1/control/apply (Confirm & Apply Change)...")
    res_apply = client.post(
        "/api/v1/control/apply",
        json={
            "proposal_id": proposal_id,
            "confirmation_token": conf_token,
            "operator_confirmed": True,
            "operator_id": "OP-104",
        },
    )
    assert res_apply.status_code == 200
    apply_data = res_apply.json()
    assert apply_data["success"] is True
    assert apply_data["data"]["applied_value"] == 172.0
    assert apply_data["data"]["verified_value"] == 172.0
    print(f"  [+] Change Successfully Applied & Verified: {apply_data['message']}")

    # 6. Test Audit Trail
    print("\n[6/7] Testing GET /api/v1/control/audit-trail...")
    res_audit = client.get("/api/v1/control/audit-trail?limit=5")
    assert res_audit.status_code == 200
    audit_data = res_audit.json()
    assert len(audit_data["data"]) > 0
    latest_event = audit_data["data"][0]
    assert latest_event["parameter"] == "hydraulic_pressure"
    assert latest_event["applied_value"] == 172.0
    assert latest_event["mode"] == "simulation"
    print(f"  [+] Verified Immutable Audit Entry: EventID={latest_event['event_id']}, Parameter={latest_event['parameter']}, {latest_event['old_value']} -> {latest_event['applied_value']} {latest_event['unit']}")

    # 7. Test Consensus Intervention Impact
    print("\n[7/7] Testing POST /api/v1/control/intervention-impact...")
    res_impact = client.post(
        "/api/v1/control/intervention-impact",
        json={
            "parameter": "hydraulic_pressure",
            "old_value": curr_pressure,
            "new_value": 172.0,
        },
    )
    assert res_impact.status_code == 200
    impact_data = res_impact.json()
    assert impact_data["success"] is True
    print(f"  [+] Consensus Impact Observation: {impact_data['data']['observation_summary']}")

    print("\n=======================================================")
    print(" ALL 7 CONTROL LAYER TESTS PASSED SUCCESSFULLY!")
    print("=======================================================\n")

if __name__ == "__main__":
    test_control_pipeline()
