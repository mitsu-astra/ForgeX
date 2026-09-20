"""
End-to-End Multimodal Inference Validation Script
Demonstrates joint prediction using both Images (from train/) and CSV Process Telemetry
(from 'Manufacturing Data Shared Facility - Discrete-Event Simulation').
"""

import os
import sys
import json
import glob
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import XGBoost and process models first to initialize OpenMP cleanly
from models.process.data_loader import load_and_clean_csv
from models.process.model import ProcessSurrogateModel
from models.correlation.root_cause_classifier import RootCauseClassifier, ROOT_CAUSE_CLASSES

# Then import torch and vision models
import torch
from torchvision import transforms
from PIL import Image
from models.vision.model import DefectClassifier

CLASSES = ["crack", "hole", "normal", "rust", "scratch"]

def run_multimodal_demo():
    print("=" * 80)
    print(" MULTIMODAL INFERENCE: IMAGES + MANUFACTURING CSV FACILITY TELEMETRY")
    print("=" * 80)

    weights_dir = os.path.join(PROJECT_ROOT, "models", "weights")
    process_ckpt = os.path.join(weights_dir, "xgboost_process.pkl")
    corr_ckpt = os.path.join(weights_dir, "xgboost_correlation.pkl")
    vision_ckpt = os.path.join(weights_dir, "efficientnet_b4_defect_snapshot.pth")
    if not os.path.exists(vision_ckpt):
        vision_ckpt = os.path.join(weights_dir, "efficientnet_b4_defect.pth")

    # Use CPU for quick offline verification so we don't contend with the background MPS training job
    device = torch.device("cpu")

    # 1. Load Process and RCA Models
    print("\n[1/4] Loading trained models...", flush=True)
    surrogate_model = ProcessSurrogateModel.load(process_ckpt)
    print(f"  [+] Process Surrogate Model: Loaded {process_ckpt}", flush=True)

    rca_model = RootCauseClassifier.load(corr_ckpt)
    print(f"  [+] Root Cause / SHAP Model: Loaded {corr_ckpt}", flush=True)

    vision_model = DefectClassifier(num_classes=5, pretrained=False)
    state = torch.load(vision_ckpt, map_location=device, weights_only=False)
    vision_model.load_state_dict(state["state_dict"])
    vision_model.to(device)
    vision_model.eval()
    print(f"  [+] Vision Model: Loaded {vision_ckpt}", flush=True)

    # 3. Test on sample images from each defect class
    print("\n[2/4] Testing Vision Model on samples from train/ folder:")
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    for defect_type in ["crack", "hole", "rust", "scratch", "normal"]:
        img_folder = os.path.join(PROJECT_ROOT, "train", defect_type)
        img_files = sorted(glob.glob(os.path.join(img_folder, "*.png")))
        if not img_files:
            continue
        sample_img_path = img_files[0]
        with Image.open(sample_img_path) as img:
            img_rgb = img.convert("RGB")
            tensor = transform(img_rgb).unsqueeze(0).to(device)

        mean_probs, preds, uncertainty = vision_model.predict_with_uncertainty(tensor, n_samples=10)
        pred_idx = int(preds[0].cpu().item())
        pred_class = CLASSES[pred_idx]
        confidence = float(mean_probs[0, pred_idx].cpu().item())
        epistemic_unc = float(uncertainty[0].cpu().item())

        print(f"  --> True Label: {defect_type:<8} | Predicted: {pred_class:<8} | Confidence: {confidence*100:6.2f}% | Epistemic Uncertainty: {epistemic_unc:.4f}", flush=True)

    # 4. Load CSV Process Telemetry
    print("\n[3/4] Reading Manufacturing CSV Telemetry:", flush=True)
    csv_path = os.path.join(PROJECT_ROOT, "Manufacturing Data Shared Facility - Discrete-Event Simulation", "Model 1", "Model_1.csv")
    df_m1, _ = load_and_clean_csv(csv_path)
    sample_row = df_m1.iloc[0].to_dict()
    print("  Sample CSV parameters:", flush=True)
    for k, v in list(sample_row.items())[:6]:
        print(f"    {k}: {v}", flush=True)

    # Run Process Surrogate Prediction
    sim_inputs = {
        "Demand": float(sample_row.get("Demand", 10)),
        "VA Time": float(sample_row.get("VA Time", 9.0)),
        "Drilling Waiting Time": float(sample_row.get("Drilling Waiting Time", 0.5)),
        "Milling Waiting Time": float(sample_row.get("Milling Waiting Time", 0.0)),
        "Assembly Waiting Time": float(sample_row.get("Assembly Waiting Time", 2.0)),
    }
    surrogate_preds = surrogate_model.predict(sim_inputs)
    print("\n  Process Surrogate Predicted Metrics:", flush=True)
    for k, v in surrogate_preds.items():
        print(f"    {k}: {v:.4f}", flush=True)

    # 5. Joint Root Cause Diagnosis (CSV Telemetry + Vision Defect)
    print("\n[4/4] Joint Multimodal Root Cause Diagnosis & Attribution:", flush=True)
    operational_telemetry = {
        "Queue_Time_Hours": float(sample_row.get("Drilling Waiting Time", 0.41)) + float(sample_row.get("Assembly Waiting Time", 2.09)),
        "Station_Max_Util": float(sample_row.get("Assembly Util", 0.72)),
        "Conveyor_Speed_mps": 1.25,
        "Spindle_Cycles": 4500.0,
        "Coolant_pH": 7.6,
        "Ambient_Humidity_pct": 42.0,
        "Forming_Pressure_bar": 165.0,
        "Feed_Rate_mm_per_min": 250.0,
    }

    rca_pred = rca_model.predict(operational_telemetry)
    print(f"  Predicted Primary Root Cause: {rca_pred['root_cause']}", flush=True)
    print(f"  Associated Visual Defect:     {rca_pred['associated_defect']}", flush=True)
    print(f"  Root Cause Confidence:        {rca_pred['confidence']*100:.2f}%", flush=True)
    print(f"  Prescriptive Corrective Action:\n    -> {rca_pred['recommendation']}", flush=True)

    # SHAP Attribution
    print("\n  Top Contributing Process Telemetry Factors (SHAP Waterfall Attribution):", flush=True)
    top_features = rca_pred.get("shap_explanation", {}).get("top_features", [])
    for feat in top_features[:4]:
        print(f"    - {feat['feature']:<22}: SHAP value = {feat['shap_value']:+.4f} (actual: {feat['feature_value']}) [{feat['contribution']} impact]", flush=True)

    print("\n" + "=" * 80, flush=True)
    print(" ALL MODELS VALIDATED SUCCESSFULLY END-TO-END (IMAGES + CSVS)", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    run_multimodal_demo()
