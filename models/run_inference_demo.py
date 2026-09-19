"""
End-to-End Inference and Demonstration Script
Demonstrates Vision Inference, Grad-CAM, Process Bottleneck Analysis, Root Cause Explanations, and What-If Simulation.
"""

import os
import sys
import glob
import json

# Add root directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.vision.infer import VisionInferenceEngine
from models.process.bottleneck import BottleneckDetector
from models.process.model import ProcessSurrogateModel
from models.correlation.root_cause_classifier import RootCauseClassifier
from models.correlation.correlation_engine import CorrelationEngine
from models.simulator.what_if_engine import WhatIfSimulatorEngine


def run_demo():
    print("=" * 80)
    print(" INDUSTRIAL AI DECISION INTELLIGENCE - END-TO-END SYSTEM DEMO")
    print("=" * 80)

    # 1. VISION INFERENCE & LOCALIZATION DEMO
    print("\n--- 1. Testing Visual Inspection & Grad-CAM Localization ---")
    weights_path = os.path.join(root_dir, "models", "weights", "efficientnet_b4_defect.pth")
    if os.path.exists(weights_path):
        engine = VisionInferenceEngine(weights_path=weights_path)

        # Test on one sample of each defect class
        for defect_type in ["crack", "rust", "hole", "scratch", "normal"]:
            sample_files = glob.glob(os.path.join(root_dir, "train", defect_type, "*.*"))
            if sample_files:
                sample_img = sample_files[0]
                result = engine.predict_single(sample_img, include_heatmap=True)
                pred = result["prediction"]
                unc = result["uncertainty"]
                print(f"Sample: {os.path.basename(sample_img)} ({defect_type})")
                print(f"  -> Predicted: {pred['class'].upper()} (Confidence: {pred['confidence']*100:.1f}%)")
                print(f"  -> Uncertainty: {unc['uncertainty_score']:.3f} (Is Uncertain: {unc['is_uncertain']})")
                print(f"  -> Latency: {result['inference_time_ms']} ms")
                if "localization" in result:
                    loc = result["localization"]
                    print(f"  -> Grad-CAM BBoxes: {len(loc['bounding_boxes'])} box(es), Defect Area: {loc['defect_area_percentage']}%")
    else:
        print(f"[*] Vision weights not yet trained at {weights_path}")

    # 2. PROCESS ANALYSIS & BOTTLENECK DETECTION DEMO
    print("\n--- 2. Testing Process Health & Bottleneck Detection ---")
    detector = BottleneckDetector()
    sample_process_state = {
        "Demand": 7.0,
        "Total parts": 3472,
        "Parts per hour": 145.0,
        "VA Time": 8.998,
        "Drilling Waiting Time": 4.12,
        "Milling Waiting Time": 0.85,
        "Assembly Waiting Time": 2.09,
        "Drilling Util": 0.96,     # Severe bottleneck
        "Milling Util": 0.36,
        "Assembly Util": 0.72,
    }
    b_res = detector.analyze_process_state(sample_process_state)
    print(f"Primary Bottleneck Station: {b_res['primary_bottleneck']} (Utilization: {b_res['max_utilization']*100:.1f}%)")
    print(f"Line Balancing Efficiency: {b_res['line_efficiency_pct']}%")
    print(f"Active Bottlenecks: {len(b_res['bottlenecks'])} detected")
    for b in b_res["bottlenecks"]:
        print(f"  - [{b['severity'].upper()}] {b['station']}: Util {b['utilization']*100:.1f}%, Queue {b['queue_time_hrs']} hrs ({b['impact']})")
    print(f"Estimated Hourly Loss: ${b_res['economic_impact']['hourly_throughput_loss_usd']}")

    # 3. ROOT CAUSE CORRELATION & SHAP EXPLANATION DEMO
    print("\n--- 3. Testing Root Cause Correlation & SHAP Explanations ---")
    corr_weights = os.path.join(root_dir, "models", "weights", "xgboost_correlation.pkl")
    if os.path.exists(corr_weights):
        rc_clf = RootCauseClassifier.load(corr_weights)
        import numpy as np
        # Feature vector: [Queue_Time, Util, Speed, Spindle_Cycles, pH, Humidity, Pressure, Feed]
        sample_feature_vector = np.array([4.5, 0.96, 1.1, 4000, 6.8, 75.0, 210.0, 280.0])
        rc_res = rc_clf.predict(sample_feature_vector)
        print(f"Diagnosed Root Cause: {rc_res['root_cause']} (Confidence: {rc_res['confidence']*100:.1f}%)")
        print(f"Associated Defect Type: {rc_res['associated_defect'].upper()}")
        print("Top Driving Factors (SHAP Values):")
        for feat in rc_res["shap_explanation"]["top_features"]:
            print(f"  - {feat['feature']} = {feat['feature_value']} (Impact: {feat['shap_value']:+.4f})")

    # 4. WHAT-IF SCENARIO SIMULATOR DEMO
    print("\n--- 4. Testing What-If Scenario Simulator ---")
    sim = WhatIfSimulatorEngine()
    sim_res = sim.simulate_scenario(
        baseline_params={"pressure_bar": 185.0, "coolant_ph": 7.0, "conveyor_speed_mps": 1.2, "demand": 1.0},
        modified_params={"pressure_bar": 168.0, "coolant_ph": 7.6, "conveyor_speed_mps": 0.95, "demand": 1.0},
    )
    print(f"Forecasted Defect Rate Reduction: -{sim_res['delta']['defect_reduction_pct']}% (from {sim_res['baseline']['defect_rate_pct']}% to {sim_res['simulated']['defect_rate_pct']}%)")
    print(f"Estimated Monthly Savings: ${sim_res['delta']['monthly_savings_usd']:,.2f}")
    print(f"Recommendation Score: {sim_res['recommendation_score']}/100 ({sim_res['risk_level']} Risk)")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
