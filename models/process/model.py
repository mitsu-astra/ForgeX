"""
Process Surrogate Model using XGBoost Regressors
Provides real-time what-if simulation response for throughput and utilization forecasting.
"""

import os
import joblib
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error


class ProcessSurrogateModel:
    """
    Surrogate regression model for discrete-event manufacturing simulation.
    """

    def __init__(self, model_type: str = "model_1"):
        self.model_type = model_type
        self.models: Dict[str, xgb.XGBRegressor] = {}
        self.feature_names: List[str] = []
        self.target_names: List[str] = []

    def fit(
        self,
        df: pd.DataFrame,
        feature_cols: Optional[List[str]] = None,
        target_cols: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Trains XGBoost regressors for each target column.
        """
        if self.model_type == "model_1":
            default_features = ["Demand"]
            default_targets = ["Parts per hour", "Drilling Util", "Milling Util", "Assembly Util", "Assembly Waiting Time"]
        elif self.model_type == "model_2":
            default_features = ["Demand", "Part 1 VA Time", "Part 2 VA Time"]
            default_targets = ["Entities Out", "Drilling Utilization", "Milling Utilization", "Assembly Utilization"]
        else:
            # Model 3
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            default_features = [c for c in num_cols if "time" in c.lower() or "demand" in c.lower() or "sku" in c.lower()][:10]
            default_targets = [c for c in num_cols if "util" in c.lower()][:5]

        self.feature_names = feature_cols or [c for c in default_features if c in df.columns]
        self.target_names = target_cols or [c for c in default_targets if c in df.columns]

        X = df[self.feature_names].values
        metrics = {}

        for target in self.target_names:
            y = df[target].values

            # Train XGBoost regressor
            reg = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
            )
            reg.fit(X, y)
            self.models[target] = reg

            # Compute train metrics
            preds = reg.predict(X)
            r2 = float(r2_score(y, preds))
            rmse = float(np.sqrt(mean_squared_error(y, preds)))
            mae = float(mean_absolute_error(y, preds))

            metrics[target] = {
                "r2_score": round(r2, 4),
                "rmse": round(rmse, 4),
                "mae": round(mae, 4),
            }

        return metrics

    def predict(self, input_dict: Dict[str, float]) -> Dict[str, float]:
        """
        Predicts simulation output metrics given an input dictionary of features.
        """
        row_vals = [input_dict.get(f, 0.0) for f in self.feature_names]
        X = np.array([row_vals])

        predictions = {}
        for target, model in self.models.items():
            pred_val = float(model.predict(X)[0])
            # Cap utilizations to sensible physical range [0, 1] if target is util
            if "util" in target.lower():
                pred_val = max(0.0, min(1.0, pred_val))
            else:
                pred_val = max(0.0, pred_val)
            predictions[target] = round(pred_val, 3)

        return predictions

    def get_feature_importances(self) -> Dict[str, Dict[str, float]]:
        """
        Returns feature importance scores for each target regressor.
        """
        importances = {}
        for target, model in self.models.items():
            scores = model.feature_importances_
            importances[target] = {
                f_name: round(float(score), 4)
                for f_name, score in zip(self.feature_names, scores)
            }
        return importances

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "model_type": self.model_type,
            "models": self.models,
            "feature_names": self.feature_names,
            "target_names": self.target_names,
        }, path)

    @classmethod
    def load(cls, path: str) -> "ProcessSurrogateModel":
        data = joblib.load(path)
        instance = cls(model_type=data["model_type"])
        instance.models = data["models"]
        instance.feature_names = data["feature_names"]
        instance.target_names = data["target_names"]
        return instance
