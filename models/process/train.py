"""
Training Pipeline for XGBoost Manufacturing Process Surrogate Model
"""

import os
import sys
import json
from typing import Dict, Any
import numpy as np
import pandas as pd

# Ensure root directory in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.process.data_loader import load_all_simulation_datasets
from models.process.model import ProcessSurrogateModel
from models.process.feature_engineering import engineer_model1_features, engineer_model2_features


def train_process_models(
    base_dir: str = "/home/koushik_2109/Hackathons/CMR/Manufacturing Data Shared Facility - Discrete-Event Simulation",
    save_dir: str = "/home/koushik_2109/Hackathons/CMR/models/weights",
) -> Dict[str, Any]:
    """
    Loads all manufacturing datasets and trains the surrogate process models.
    """
    print(f"[*] Loading discrete-event simulation datasets from {base_dir}...")
    datasets = load_all_simulation_datasets(base_dir=base_dir)

    os.makedirs(save_dir, exist_ok=True)
    weights_path = os.path.join(save_dir, "xgboost_process.pkl")
    metrics_path = os.path.join(save_dir, "process_metrics.json")

    results: Dict[str, Any] = {}

    if "model_1" in datasets:
        print("[*] Training Process Surrogate Model for Model 1...")
        df1 = datasets["model_1"]
        df1_engineered = engineer_model1_features(df1)

        surrogate_m1 = ProcessSurrogateModel(model_type="model_1")
        m1_metrics = surrogate_m1.fit(df1_engineered)
        surrogate_m1.save(weights_path)

        importances = surrogate_m1.get_feature_importances()
        results["model_1"] = {
            "metrics": m1_metrics,
            "feature_importances": importances,
            "trained_samples": len(df1),
        }
        print(f"  --> Model 1 R2 Scores: {[f'{k}: {v['r2_score']}' for k, v in m1_metrics.items()]}")

    if "model_2" in datasets:
        print("[*] Training Process Surrogate Model for Model 2...")
        df2 = datasets["model_2"]
        df2_engineered = engineer_model2_features(df2)
        surrogate_m2 = ProcessSurrogateModel(model_type="model_2")
        m2_metrics = surrogate_m2.fit(df2_engineered)
        results["model_2"] = {
            "metrics": m2_metrics,
            "trained_samples": len(df2),
        }

    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[*] Process surrogate models saved to {weights_path}")
    print(f"[*] Metrics logged to {metrics_path}")
    return results


if __name__ == "__main__":
    train_process_models()
