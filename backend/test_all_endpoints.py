"""
Comprehensive Integration Test for all Backend Endpoints and Models
"""

import os
import sys
import io
import json
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.main import app
from backend.app.services.model_service import ModelService

def run_integration_tests():
    print("=" * 70)
    print("  RUNNING BACKEND & MODEL END-TO-END INTEGRATION TESTS")
    print("=" * 70)

    # Initialize model service in test context
    model_service = ModelService.get_instance()
    model_service.initialize()

    client = TestClient(app)

    # 1. Health Check
    print("\n[1/7] Testing GET /health...")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    data = res.json()
    print("  ✓ Status:", data.get("status"))
    print("  ✓ Models loaded:", data.get("models_loaded"))

    # 2. Visual Inspection
    print("\n[2/7] Testing POST /api/v1/quality/inspect...")
    # Create test image in memory
    img = Image.new("RGB", (256, 256), color=(120, 120, 120))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    files = {"file": ("test_defect.png", buf, "image/png")}
    data = {"include_heatmap": "true", "mc_samples": "5"}
    res = client.post("/api/v1/quality/inspect", files=files, data=data)
    assert res.status_code == 200, f"Quality inspect failed: {res.text}"
    q_data = res.json()
    assert q_data["success"] is True
    print("  ✓ Predicted class:", q_data["data"]["prediction"]["defect_class"])
    print("  ✓ Confidence:", q_data["data"]["prediction"]["confidence"])
    print("  ✓ Uncertainty score:", q_data["data"]["uncertainty"]["uncertainty_score"])
    print("  ✓ Latency (ms):", q_data["data"]["inference_time_ms"])
    assert "overlay_base64" in q_data["data"]["localization"]
    print("  ✓ Grad-CAM overlay generated (length):", len(q_data["data"]["localization"]["overlay_base64"]))

    # 3. Process Bottlenecks
    print("\n[3/7] Testing POST /api/v1/process/bottlenecks...")
    payload = {
        "station_utilizations": {"Drilling": 0.96, "Milling": 0.45, "Assembly": 0.72},
        "station_queue_times": {"Drilling": 4.5, "Milling": 0.8, "Assembly": 1.9},
        "throughput_per_hr": 145.0,
        "demand": 7.0
    }
    res = client.post("/api/v1/process/bottlenecks", json=payload)
    assert res.status_code == 200, f"Process bottlenecks failed: {res.text}"
    b_data = res.json()
    assert b_data["success"] is True
    print("  ✓ Primary Bottleneck:", b_data["data"]["primary_bottleneck"])
    print("  ✓ Line Efficiency %:", b_data["data"]["line_efficiency_pct"])
    print("  ✓ Monthly Loss USD:", b_data["data"]["economic_impact"]["monthly_throughput_loss_usd"])

    # 4. Process Drift (CUSUM)
    print("\n[4/7] Testing POST /api/v1/process/drift-analysis...")
    drift_payload = {
        "parameter_name": "Hydraulic Pressure",
        "values": [170.0, 171.2, 170.8, 172.0, 174.5, 178.0, 182.5, 188.0, 192.1],
        "threshold": 4.0
    }
    res = client.post("/api/v1/process/drift-analysis", json=drift_payload)
    assert res.status_code == 200, f"Drift analysis failed: {res.text}"
    d_data = res.json()
    assert d_data["success"] is True
    print("  ✓ Drift Detected:", d_data["data"]["drift_detected"])
    print("  ✓ Drift Start Index:", d_data["data"]["drift_start_index"])

    # 5. Correlation & SHAP Root Cause Diagnosis
    print("\n[5/7] Testing POST /api/v1/correlation/diagnose...")
    corr_payload = {
        "Press Hydraulic Pressure": 192.0,
        "Coolant Fluid pH": 7.0,
        "Conveyor Belt Speed": 1.3,
        "Spindle Feed Rate": 390.0
    }
    res = client.post("/api/v1/correlation/diagnose", json=corr_payload)
    assert res.status_code == 200, f"Correlation diagnose failed: {res.text}"
    c_data = res.json()
    assert c_data["success"] is True
    print("  ✓ Diagnosed Root Cause:", c_data["data"]["root_cause"])
    print("  ✓ Associated Defect:", c_data["data"]["associated_defect"])
    print("  ✓ Top SHAP Feature:", c_data["data"]["shap_explanation"]["top_features"][0]["feature"])
    print("  ✓ Top SHAP Value:", c_data["data"]["shap_explanation"]["top_features"][0]["shap_value"])

    # 6. What-If Simulator
    print("\n[6/7] Testing POST /api/v1/simulator/run...")
    sim_payload = {
        "baseline_params": {
            "Press Hydraulic Pressure": 188.0,
            "Coolant Fluid pH": 7.1,
            "Conveyor Belt Speed": 1.25,
            "Demand": 7.0
        },
        "modified_params": {
            "Press Hydraulic Pressure": 172.0,
            "Coolant Fluid pH": 7.7,
            "Conveyor Belt Speed": 0.95,
            "Demand": 7.0
        }
    }
    res = client.post("/api/v1/simulator/run", json=sim_payload)
    assert res.status_code == 200, f"Simulator run failed: {res.text}"
    s_data = res.json()
    assert s_data["success"] is True
    print("  ✓ Defect Reduction %:", s_data["data"]["delta"]["defect_reduction_pct"])
    print("  ✓ Monthly Savings USD:", s_data["data"]["delta"]["monthly_savings_usd"])
    print("  ✓ Recommendation Score:", s_data["data"]["recommendation_score"])

    # 7. AI Copilot Chat
    print("\n[7/7] Testing POST /api/v1/copilot/chat...")
    chat_payload = {
        "message": "Why are we seeing high crack defect rates at Press Station 1?",
        "history": []
    }
    res = client.post("/api/v1/copilot/chat", json=chat_payload)
    assert res.status_code == 200, f"Copilot chat failed: {res.text}"
    chat_data = res.json()
    assert chat_data["success"] is True
    print("  ✓ Copilot Response Preview:", chat_data["data"]["response"][:100], "...")
    print("  ✓ Actions Generated:", len(chat_data["data"]["suggested_actions"]))

    print("\n" + "=" * 70)
    print("  🎉 ALL 7 BACKEND API ENDPOINTS & ML MODELS VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_integration_tests()
