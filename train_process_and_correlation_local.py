"""
Training script for Manufacturing Process Surrogate Models and Root Cause Correlation
Using Discrete-Event Simulation CSVs from:
'Manufacturing Data Shared Facility - Discrete-Event Simulation'
"""

import os
import sys
import json
from typing import Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.process.data_loader import load_all_simulation_datasets
from models.process.model import ProcessSurrogateModel
from models.process.feature_engineering import engineer_model1_features, engineer_model2_features
from models.correlation.train import train_correlation_model


def train_all_process_data(
    base_dir: str = os.path.join(PROJECT_ROOT, "Manufacturing Data Shared Facility - Discrete-Event Simulation"),
    save_dir: str = os.path.join(PROJECT_ROOT, "models", "weights"),
) -> Dict[str, Any]:
    print("=" * 80)
    print(" TRAINING PROCESS SURROGATE MODELS (DISCRETE-EVENT SIMULATION CSVS)")
    print("=" * 80)
    print(f"[*] Loading CSV datasets from: {base_dir}")

    datasets = load_all_simulation_datasets(base_dir=base_dir)
    print(f"[*] Loaded datasets: {list(datasets.keys())}")

    os.makedirs(save_dir, exist_ok=True)
    weights_path = os.path.join(save_dir, "xgboost_process.pkl")
    metrics_path = os.path.join(save_dir, "process_metrics.json")

    results: Dict[str, Any] = {}

    if "model_1" in datasets:
        print("\n[*] [1/3] Training Process Surrogate Model for Model 1...")
        df1 = datasets["model_1"]
        print(f"    Raw samples: {len(df1)}, Columns: {list(df1.columns)}")
        df1_engineered = engineer_model1_features(df1)
        print(f"    Engineered features: {list(df1_engineered.columns)}")

        surrogate_m1 = ProcessSurrogateModel(model_type="model_1")
        m1_metrics = surrogate_m1.fit(df1_engineered)
        surrogate_m1.save(weights_path)

        importances = surrogate_m1.get_feature_importances()
        results["model_1"] = {
            "metrics": m1_metrics,
            "feature_importances": importances,
            "trained_samples": len(df1),
        }
        print(f"    --> Model 1 Fit Metrics (R2 / MAE):")
        for target, scores in m1_metrics.items():
            print(f"        {target}: R2 = {scores.get('r2_score', 'N/A')}, MAE = {scores.get('mae', 'N/A')}")

    if "model_2" in datasets:
        print("\n[*] [2/3] Training Process Surrogate Model for Model 2...")
        df2 = datasets["model_2"]
        print(f"    Raw samples: {len(df2)}, Columns: {list(df2.columns)}")
        df2_engineered = engineer_model2_features(df2)
        surrogate_m2 = ProcessSurrogateModel(model_type="model_2")
        m2_metrics = surrogate_m2.fit(df2_engineered)
        results["model_2"] = {
            "metrics": m2_metrics,
            "trained_samples": len(df2),
        }
        print(f"    --> Model 2 Fit Metrics:")
        for target, scores in m2_metrics.items():
            print(f"        {target}: R2 = {scores.get('r2_score', 'N/A')}, MAE = {scores.get('mae', 'N/A')}")

    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[*] Process surrogate models saved to {weights_path}")
    print(f"[*] Process metrics logged to {metrics_path}")

    # Root Cause Correlation Model
    print("\n" + "=" * 80)
    print(" TRAINING ROOT CAUSE CORRELATION & SHAP EXPLAINER")
    print("=" * 80)
    corr_results = train_correlation_model(save_dir=save_dir)

    print("\n" + "=" * 80)
    print(" CSV & PROCESS MODEL TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 80)

    return {
        "process_results": results,
        "correlation_results": corr_results,
    }


if __name__ == "__main__":
    train_all_process_data()
