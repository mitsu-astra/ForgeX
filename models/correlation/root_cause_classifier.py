"""
Root Cause Classifier using XGBoost and Multi-Modal Feature Synthesis
Classifies industrial failure modes from combined visual inspection metrics and process parameters.
"""

import os
import joblib
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score, classification_report

from models.correlation.shap_explainer import ShapExplainerWrapper

ROOT_CAUSE_CLASSES = [
    "storage_queue_corrosion",        # Extended waiting/storage time causing oxidation (Rust)
    "hydraulic_overload_stress",      # Excessive press pressure or station overload (Crack)
    "conveyor_speed_friction",        # Material handling guide rail contact/speed (Scratch)
    "tool_wear_drill_misalignment",   # Tool degradation or high feed rate (Hole)
    "nominal_in_control",             # Process operating within normal tolerances
]

ROOT_CAUSE_TO_DEFECT = {
    "storage_queue_corrosion": "rust",
    "hydraulic_overload_stress": "crack",
    "conveyor_speed_friction": "scratch",
    "tool_wear_drill_misalignment": "hole",
    "nominal_in_control": "normal",
}


class RootCauseClassifier:
    """
    Classifies root causes and provides SHAP-based feature attributions.
    """

    def __init__(self):
        self.model: Optional[xgb.XGBClassifier] = None
        self.feature_names: List[str] = []
        self.shap_explainer: Optional[ShapExplainerWrapper] = None

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
    ) -> Dict[str, Any]:
        self.feature_names = feature_names

        self.model = xgb.XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="multi:softprob",
            num_class=len(ROOT_CAUSE_CLASSES),
            random_state=42,
            n_jobs=-1,
        )

        self.model.fit(X, y)
        preds = self.model.predict(X)

        acc = float(accuracy_score(y, preds))
        f1 = float(f1_score(y, preds, average="macro"))

        self.shap_explainer = ShapExplainerWrapper(self.model, self.feature_names)

        return {
            "accuracy": round(acc, 4),
            "macro_f1": round(f1, 4),
            "num_features": len(feature_names),
            "num_classes": len(ROOT_CAUSE_CLASSES),
        }

    def predict(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        if self.model is None or self.shap_explainer is None:
            raise RuntimeError("Model not trained or loaded.")

        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)

        probs = self.model.predict_proba(feature_vector)[0]
        pred_idx = int(np.argmax(probs))
        pred_class = ROOT_CAUSE_CLASSES[pred_idx]
        conf = float(probs[pred_idx])

        # Get SHAP explanations
        shap_res = self.shap_explainer.explain_instance(feature_vector, top_k=4)

        # Recommendation mapping
        recommendations = {
            "storage_queue_corrosion": "Buffer queue throttling and coolant pH conditioning (target 7.6-7.8)",
            "hydraulic_overload_stress": "Recalibrate hydraulic pressure relief valves to 172-180 bar nominal",
            "conveyor_speed_friction": "Reduce conveyor belt speed to 0.95 m/s and adjust side rail guides",
            "tool_wear_drill_misalignment": "Replace tool inserts / drill bits and verify spindle feed calibration",
            "nominal_in_control": "Process operating within normal tolerances. Maintain current parameters.",
        }

        probs_dict = {
            cls_name: round(float(p), 4) for cls_name, p in zip(ROOT_CAUSE_CLASSES, probs)
        }

        return {
            "root_cause": pred_class,
            "associated_defect": ROOT_CAUSE_TO_DEFECT.get(pred_class, "unknown"),
            "confidence": round(conf, 4),
            "probabilities": probs_dict,
            "class_probabilities": probs_dict,
            "shap_explanation": shap_res,
            "recommendation": recommendations.get(pred_class, "Investigate operating parameters"),
        }

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_names": self.feature_names,
            "classes": ROOT_CAUSE_CLASSES,
        }, path)

    @classmethod
    def load(cls, path: str) -> "RootCauseClassifier":
        data = joblib.load(path)
        instance = cls()
        instance.model = data["model"]
        instance.feature_names = data["feature_names"]
        instance.shap_explainer = ShapExplainerWrapper(instance.model, instance.feature_names)
        return instance
