"""
Training Pipeline for Root Cause Classification and SHAP Explainer
"""

import os
import sys
import json
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd

# Ensure root directory in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.correlation.root_cause_classifier import RootCauseClassifier, ROOT_CAUSE_CLASSES
from models.process.data_loader import load_all_simulation_datasets


def generate_correlation_training_data(n_samples: int = 4000, seed: int = 42) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Synthesizes manufacturing operational records with physical domain rules for root cause learning.
    """
    np.random.seed(seed)

    feature_names = [
        "Queue_Time_Hours",
        "Station_Max_Util",
        "Conveyor_Speed_mps",
        "Spindle_Cycles",
        "Coolant_pH",
        "Ambient_Humidity_pct",
        "Forming_Pressure_bar",
        "Feed_Rate_mm_per_min",
    ]

    X = np.zeros((n_samples, len(feature_names)))
    y = np.zeros(n_samples, dtype=int)

    samples_per_class = n_samples // len(ROOT_CAUSE_CLASSES)

    for i in range(n_samples):
        cls_idx = i // samples_per_class
        if cls_idx >= len(ROOT_CAUSE_CLASSES):
            cls_idx = len(ROOT_CAUSE_CLASSES) - 1

        # Baselines
        queue = np.random.uniform(0.1, 1.5)
        util = np.random.uniform(0.4, 0.78)
        speed = np.random.uniform(0.8, 1.05)
        cycles = np.random.uniform(1000, 6000)
        ph = np.random.uniform(7.4, 8.0)
        humidity = np.random.uniform(35, 50)
        pressure = np.random.uniform(150, 175)
        feed = np.random.uniform(200, 300)

        # Inject class-specific physical anomaly signatures
        if cls_idx == 0:  # storage_queue_corrosion -> Rust
            queue = np.random.uniform(3.5, 8.0)
            humidity = np.random.uniform(65, 90)
            ph = np.random.uniform(6.2, 7.1)
        elif cls_idx == 1:  # hydraulic_overload_stress -> Crack
            pressure = np.random.uniform(190, 240)
            util = np.random.uniform(0.90, 0.99)
        elif cls_idx == 2:  # conveyor_speed_friction -> Scratch
            speed = np.random.uniform(1.3, 2.0)
        elif cls_idx == 3:  # tool_wear_drill_misalignment -> Hole
            cycles = np.random.uniform(12000, 25000)
            feed = np.random.uniform(380, 500)
        elif cls_idx == 4:  # nominal_in_control -> Normal
            pass

        X[i] = [queue, util, speed, cycles, ph, humidity, pressure, feed]
        y[i] = cls_idx

    # Shuffle
    perm = np.random.permutation(n_samples)
    X = X[perm]
    y = y[perm]

    return X, y, feature_names


def train_correlation_model(
    save_dir: str = "/home/koushik_2109/Hackathons/CMR/models/weights",
) -> Dict[str, Any]:
    """
    Trains the XGBoost root cause classifier and builds the SHAP explainer.
    """
    print("[*] Generating domain-grounded correlation dataset...")
    X, y, feature_names = generate_correlation_training_data(n_samples=5000)

    # Train/test split
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    print(f"[*] Training Root Cause Classifier on {len(X_train)} samples across {len(ROOT_CAUSE_CLASSES)} classes...")
    clf = RootCauseClassifier()
    train_metrics = clf.fit(X_train, y_train, feature_names=feature_names)

    # Test evaluation
    test_preds = clf.model.predict(X_test)
    from sklearn.metrics import accuracy_score, f1_score
    test_acc = float(accuracy_score(y_test, test_preds))
    test_f1 = float(f1_score(y_test, test_preds, average="macro"))

    os.makedirs(save_dir, exist_ok=True)
    weights_path = os.path.join(save_dir, "xgboost_correlation.pkl")
    metrics_path = os.path.join(save_dir, "correlation_metrics.json")

    clf.save(weights_path)

    results = {
        "model": "XGBoost Root Cause Classifier + SHAP TreeExplainer",
        "num_classes": len(ROOT_CAUSE_CLASSES),
        "classes": ROOT_CAUSE_CLASSES,
        "feature_names": feature_names,
        "train_accuracy": train_metrics["accuracy"],
        "train_macro_f1": train_metrics["macro_f1"],
        "test_accuracy": round(test_acc, 4),
        "test_macro_f1": round(test_f1, 4),
    }

    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"[*] Root cause classifier saved to {weights_path}")
    print(f"[*] Test Accuracy: {test_acc*100:.2f}% | Test Macro F1: {test_f1*100:.2f}%")
    return results


if __name__ == "__main__":
    train_correlation_model()
