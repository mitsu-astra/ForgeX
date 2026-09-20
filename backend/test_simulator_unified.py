"""
Comprehensive Automated Test Suite for ForgeX Unified What-If Decision Simulator.
Tests:
1. Active baseline ground-truth resolution and parameter provenance.
2. Hydraulic pressure adjustment & Griffith fracture crack reduction.
3. Coolant pH adjustment & Pourbaix corrosion kinetics.
4. Conveyor belt speed adjustment & Archard abrasive wear.
5. Production demand adjustment & XGBoost surrogate line balancing (utilization & WIP).
6. Spindle feed rate adjustment & Taylor tool-life sensitivity.
7. Real-time safety validation: SAFE, WARNING, BLOCKED.
8. Engineering material switching (AISI 4140, AISI 304, AL 6061, Cast Iron 40).
9. Dual-currency economic evaluation (USD $ and INR ₹ at canonical 83.50 rate).
10. Controller staging interlock (simulation-mode audit logging & safety blocker).
11. Historical scenario persistence & query audit.
12. Backward compatibility with legacy simulation request/response schema.
"""

import sys
import os
import json
from fastapi.testclient import TestClient

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.main import app
from backend.app.services.simulation_orchestrator import USD_TO_INR_RATE

client = TestClient(app)


def test_01_baseline_ground_truth_and_provenance():
    """Verifies that baseline derives from active batch/telemetry with parameter provenance tags."""
    res = client.get("/api/v1/simulator/baseline")
    assert res.status_code == 200, f"Failed: {res.text}"
    body = res.json()
    assert body["success"] is True
    data = body["data"]

    # Parameter checks
    params = data["parameters"]
    assert "hydraulic_pressure_bar" in params
    assert "coolant_ph" in params
    assert "conveyor_speed_mps" in params
    assert "demand" in params
    assert "spindle_feed_rate" in params

    for p_name, p_obj in params.items():
        assert p_obj["source"] in ["live", "stored", "configured", "fallback"]
        assert p_obj["value"] > 0
        assert p_obj["unit"] != ""

    # Metric checks
    metrics = data["metrics"]
    assert metrics["defect_rate_pct"] > 0
    assert metrics["throughput_per_hr"] > 0
    assert metrics["primary_bottleneck"] != ""
    assert "Assembly" in metrics["station_utilizations"] or "Drilling" in metrics["station_utilizations"]
    print("  ✓ [1/12] Baseline ground-truth & parameter provenance verified.")


def test_02_hydraulic_pressure_griffith_crack_simulation():
    """Verifies pressure reduction reduces crack defect probability based on Griffith fracture mechanics."""
    res = client.post(
        "/api/v1/simulator/run",
        json={
            "baseline_params": {
                "hydraulic_pressure_bar": 188.0,
            },
            "parameters": {
                "hydraulic_pressure_bar": 168.0,
                "coolant_ph": 7.1,
                "conveyor_speed_mps": 1.25,
                "demand": 7.0,
                "spindle_feed_rate": 280.0,
            },
        },
    )
    assert res.status_code == 200
    data = res.json()["data"]

    quality = data["quality_impact"]
    assert quality["crack_reduction_pct"] > 20.0, f"Expected significant crack drop, got {quality['crack_reduction_pct']}"
    assert data["delta"]["defect_reduction_pct"] > 10.0
    assert data["scenario"]["defect_rate_pct"] < data["baseline"]["defect_rate_pct"]
    print("  ✓ [2/12] Hydraulic pressure & Griffith fracture crack reduction verified.")


def test_03_coolant_ph_pourbaix_rust_simulation():
    """Verifies coolant pH optimization into 7.6-7.8 passivation window reduces rust defects."""
    res = client.post(
        "/api/v1/simulator/run",
        json={
            "baseline_params": {
                "coolant_ph": 7.1,
            },
            "parameters": {
                "hydraulic_pressure_bar": 188.0,
                "coolant_ph": 7.7,
                "conveyor_speed_mps": 1.25,
                "demand": 7.0,
                "spindle_feed_rate": 280.0,
            },
        },
    )
    assert res.status_code == 200
    data = res.json()["data"]

    quality = data["quality_impact"]
    assert quality["rust_reduction_pct"] > 15.0, f"Expected rust reduction, got {quality['rust_reduction_pct']}"
    print("  ✓ [3/12] Coolant pH & Pourbaix rust passivation kinetics verified.")


def test_04_conveyor_speed_archard_scratch_simulation():
    """Verifies reducing belt speed below max threshold reduces guide-rail scratch wear."""
    res = client.post(
        "/api/v1/simulator/run",
        json={
            "baseline_params": {
                "conveyor_speed_mps": 1.25,
            },
            "parameters": {
                "hydraulic_pressure_bar": 188.0,
                "coolant_ph": 7.1,
                "conveyor_speed_mps": 0.90,
                "demand": 7.0,
                "spindle_feed_rate": 280.0,
            },
        },
    )
    assert res.status_code == 200
    data = res.json()["data"]

    quality = data["quality_impact"]
    assert quality["scratch_reduction_pct"] > 10.0, f"Expected scratch drop, got {quality['scratch_reduction_pct']}"
    print("  ✓ [4/12] Conveyor belt speed & Archard abrasive scratch wear verified.")


def test_05_demand_surrogate_and_bottleneck_recalculation():
    """Verifies that changing Demand drives XGBoost surrogate utilizations, line efficiency, WIP, and lead time."""
    # Baseline demand = 7.0 vs High demand = 11.0
    res = client.post(
        "/api/v1/simulator/run",
        json={
            "parameters": {
                "hydraulic_pressure_bar": 175.0,
                "coolant_ph": 7.6,
                "conveyor_speed_mps": 1.0,
                "demand": 11.0,
                "spindle_feed_rate": 280.0,
            }
        },
    )
    assert res.status_code == 200
    data = res.json()["data"]

    # Higher demand should increase throughput, peak utilization, WIP, and lead time
    assert data["delta"]["throughput_delta_per_hr"] > 0
    assert data["delta"]["wip_delta_units"] > 0
    assert data["delta"]["lead_time_delta_hrs"] > 0
    assert len(data["bottleneck_impact"]["station_comparison"]) >= 3
    print("  ✓ [5/12] Process surrogate model & discrete-event queue bottleneck recalculation verified.")


def test_06_spindle_feed_rate_taylor_tool_wear_sensitivity():
    """Verifies spindle feed rate sensitivity grounded in Taylor tool-life equation."""
    # High feed rate (390 mm/min) vs nominal (280 mm/min)
    res_high = client.post(
        "/api/v1/simulator/run",
        json={"parameters": {"spindle_feed_rate": 390.0}},
    )
    assert res_high.status_code == 200
    data_high = res_high.json()["data"]

    res_norm = client.post(
        "/api/v1/simulator/run",
        json={"parameters": {"spindle_feed_rate": 280.0}},
    )
    assert res_norm.status_code == 200
    data_norm = res_norm.json()["data"]

    assert data_norm["quality_impact"]["tool_wear_reduction_pct"] >= data_high["quality_impact"]["tool_wear_reduction_pct"]
    print("  ✓ [6/12] Spindle feed rate & Taylor tool-wear sensitivity verified.")


def test_07_safety_validation_levels():
    """Verifies that SAFE, WARNING, and BLOCKED envelopes are enforced correctly."""
    # 1. Safe setpoint
    res_safe = client.post(
        "/api/v1/simulator/run",
        json={"parameters": {"hydraulic_pressure_bar": 170.0, "coolant_ph": 7.7, "conveyor_speed_mps": 0.95}},
    )
    assert res_safe.status_code == 200
    assert res_safe.json()["data"]["safety"]["status"] == "SAFE"

    # 2. Warning setpoint (pressure in 176-180 warning envelope)
    res_warn = client.post(
        "/api/v1/simulator/run",
        json={"parameters": {"hydraulic_pressure_bar": 178.0}},
    )
    assert res_warn.status_code == 200
    assert res_warn.json()["data"]["safety"]["status"] == "WARNING"
    assert len(res_warn.json()["data"]["safety"]["warnings"]) > 0

    # 3. Blocked setpoint (pressure > 200 bar)
    res_blocked = client.post(
        "/api/v1/simulator/run",
        json={"parameters": {"hydraulic_pressure_bar": 215.0}},
    )
    assert res_blocked.status_code == 200
    assert res_blocked.json()["data"]["safety"]["status"] == "BLOCKED"
    assert len(res_blocked.json()["data"]["safety"]["violations"]) > 0
    print("  ✓ [7/12] Safety validation envelopes (SAFE, WARNING, BLOCKED) verified.")


def test_08_material_alloy_switching():
    """Verifies material switching adjusts critical pressure and yield strength grounding."""
    res_al = client.post(
        "/api/v1/simulator/run",
        json={"material": "AL_6061_T6", "parameters": {"hydraulic_pressure_bar": 160.0}},
    )
    assert res_al.status_code == 200
    mat = res_al.json()["data"]["material"]
    assert mat["code"] == "AL_6061_T6"
    assert mat["critical_hydraulic_pressure_bar"] == 155.0
    # Pressure 160 exceeds 155 critical pressure for Al 6061 -> warning generated
    assert res_al.json()["data"]["safety"]["status"] in ["WARNING", "BLOCKED"]
    print("  ✓ [8/12] Material alloy switching & physical yield limits verified.")


def test_09_dual_currency_economic_evaluation():
    """Verifies scrap savings and throughput gains are computed accurately in both USD and INR at 83.50 rate."""
    res = client.post(
        "/api/v1/simulator/run",
        json={"parameters": {"hydraulic_pressure_bar": 172.0, "coolant_ph": 7.7, "conveyor_speed_mps": 0.95}},
    )
    assert res.status_code == 200
    econ = res.json()["data"]["economics"]

    assert econ["total_monthly_benefit_usd"] > 0
    assert econ["total_monthly_benefit_inr"] > 0
    expected_inr = round(econ["total_monthly_benefit_usd"] * USD_TO_INR_RATE, 2)
    assert abs(econ["total_monthly_benefit_inr"] - expected_inr) < 1.0
    print(f"  ✓ [9/12] Dual-currency economics verified (Rate: {USD_TO_INR_RATE} INR/USD).")


def test_10_controller_staging_interlock():
    """Verifies safe scenarios can be staged to control audit records with simulation disclaimer, and unsafe ones are blocked."""
    # 1. Unsafe scenario staging should be rejected with HTTP 400
    res_blocked = client.post(
        "/api/v1/simulator/stage-control",
        json={"parameters": {"hydraulic_pressure_bar": 215.0}},
    )
    assert res_blocked.status_code == 400
    assert "Cannot stage unsafe scenario" in res_blocked.json()["detail"]

    # 2. Safe scenario staging succeeds
    res_safe = client.post(
        "/api/v1/simulator/stage-control",
        json={"parameters": {"hydraulic_pressure_bar": 172.0, "coolant_ph": 7.7}},
    )
    assert res_safe.status_code == 200
    staged = res_safe.json()["data"]
    assert staged["controller_status"] == "Simulation only — controller integration not connected"
    assert len(staged["staged_parameters"]) == 2
    print("  ✓ [10/12] Controller staging interlock & audit logging verified.")


def test_11_scenario_history_query():
    """Verifies persisted simulation scenarios are queryable chronologically."""
    res = client.get("/api/v1/simulator/history?limit=5")
    assert res.status_code == 200
    scenarios = res.json()["data"]
    assert len(scenarios) > 0
    latest = scenarios[0]
    assert "batch_id" in latest
    assert "defect_reduction_pct" in latest
    assert "monthly_savings_usd" in latest
    assert latest["parameters"] is not None
    print(f"  ✓ [11/12] Scenario persistence & history audit trail verified ({len(scenarios)} records returned).")


def test_12_legacy_simulation_request_backward_compatibility():
    """Verifies existing clients sending legacy baseline_params and modified_params continue to work seamlessly."""
    legacy_payload = {
        "baseline_params": {
            "Press Hydraulic Pressure": 188.0,
            "Coolant Fluid pH": 7.1,
            "Conveyor Belt Speed": 1.25,
            "Demand": 7.0,
        },
        "modified_params": {
            "Press Hydraulic Pressure": 172.0,
            "Coolant Fluid pH": 7.7,
            "Conveyor Belt Speed": 0.95,
            "Demand": 7.0,
        },
        "baseline_defect_rate": 0.123,
        "baseline_throughput": 145.0,
    }
    res = client.post("/api/v1/simulator/run", json=legacy_payload)
    assert res.status_code == 200
    data = res.json()["data"]

    # Must contain legacy fields
    assert "baseline" in data
    assert "simulated" in data
    assert "delta" in data
    assert data["baseline"]["defect_rate_pct"] > 0
    assert data["simulated"]["defect_rate_pct"] > 0
    assert data["delta"]["defect_reduction_pct"] > 0
    assert data["delta"]["monthly_savings_usd"] > 0
    assert "recommendation_score" in data
    assert "risk_level" in data
    print("  ✓ [12/12] Backward compatibility with legacy simulation contract verified.")


if __name__ == "__main__":
    print("=" * 70)
    print(" RUNNING FORGEX UNIFIED WHAT-IF SIMULATOR VERIFICATION SUITE")
    print("=" * 70)
    test_01_baseline_ground_truth_and_provenance()
    test_02_hydraulic_pressure_griffith_crack_simulation()
    test_03_coolant_ph_pourbaix_rust_simulation()
    test_04_conveyor_speed_archard_scratch_simulation()
    test_05_demand_surrogate_and_bottleneck_recalculation()
    test_06_spindle_feed_rate_taylor_tool_wear_sensitivity()
    test_07_safety_validation_levels()
    test_08_material_alloy_switching()
    test_09_dual_currency_economic_evaluation()
    test_10_controller_staging_interlock()
    test_11_scenario_history_query()
    test_12_legacy_simulation_request_backward_compatibility()
    print("=" * 70)
    print(" 🎉 ALL 12 WHAT-IF SIMULATOR VERIFICATION SUITES PASSED!")
    print("=" * 70)
