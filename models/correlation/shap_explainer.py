"""
SHAP (SHapley Additive exPlanations) Explainer Wrapper
Generates feature attributions and waterfall explanation data for root-cause diagnosis.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import shap
import xgboost as xgb


class ShapExplainerWrapper:
    """
    Computes local and global SHAP attributions for tree-based root cause models.
    """

    def __init__(self, model: xgb.XGBClassifier, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        # Create TreeExplainer
        self.explainer = shap.TreeExplainer(model)

    def explain_instance(self, feature_vector: np.ndarray, top_k: int = 5) -> Dict[str, Any]:
        """
        Generates local SHAP waterfall attribution for a single sample.

        Args:
            feature_vector: 1D array of feature values [num_features]
            top_k: Number of top driving factors to highlight

        Returns:
            Dictionary containing base value, prediction, top positive & negative contributions
        """
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)

        shap_values = self.explainer.shap_values(feature_vector)
        pred_class_idx = int(self.model.predict(feature_vector)[0])

        # Handle multiclass vs binary SHAP output formats
        if isinstance(shap_values, list):
            # List of arrays [num_classes][1, num_features]
            class_shap = shap_values[pred_class_idx][0]
            base_val = float(self.explainer.expected_value[pred_class_idx])
        elif shap_values.ndim == 3:
            # Shape: [1, num_features, num_classes]
            class_shap = shap_values[0, :, pred_class_idx]
            base_val = float(self.explainer.expected_value[pred_class_idx]) if hasattr(self.explainer.expected_value, "__len__") else float(self.explainer.expected_value)
        else:
            # Shape: [1, num_features]
            class_shap = shap_values[0]
            base_val = float(self.explainer.expected_value)

        feature_vals = feature_vector[0]

        attributions = []
        for f_name, f_val, s_val in zip(self.feature_names, feature_vals, class_shap):
            attributions.append({
                "feature": f_name,
                "feature_value": round(float(f_val), 3),
                "shap_value": round(float(s_val), 4),
                "contribution": "positive" if s_val > 0 else "negative",
                "abs_impact": abs(float(s_val)),
            })

        # Rank by absolute impact
        attributions.sort(key=lambda a: a["abs_impact"], reverse=True)

        return {
            "predicted_class_index": pred_class_idx,
            "base_value": round(base_val, 4),
            "top_features": attributions[:top_k],
            "all_attributions": attributions,
        }
