"""
Feature Engineering and Process Physics Calculations
Includes Little's Law, Line Balancing Ratios, and CUSUM Process Drift Detection.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd


def compute_littles_law(wip: float, throughput_per_hr: float) -> float:
    """
    Applies Little's Law: L = λ * W
    Calculates average Lead Time (hours) = WIP / Throughput.
    """
    if throughput_per_hr <= 0:
        return 0.0
    return wip / throughput_per_hr


def detect_cusum_drift(
    series: np.ndarray,
    target_mean: Optional[float] = None,
    target_std: Optional[float] = None,
    k_slack: float = 0.5,
    h_threshold: float = 4.0,
) -> Tuple[np.ndarray, np.ndarray, List[int]]:
    """
    Tabular CUSUM (Cumulative Sum Control Chart) for parameter drift and anomaly detection.

    Args:
        series: 1D numpy array of time-series observations.
        target_mean: In-control target mean (if None, uses series mean).
        target_std: In-control standard deviation (if None, uses series std).
        k_slack: Allowance (slack) factor (typically 0.5 sigma).
        h_threshold: Decision interval threshold (typically 4-5 sigma).

    Returns:
        (c_plus, c_minus, drift_alarm_indices)
    """
    n = len(series)
    if n == 0:
        return np.array([]), np.array([]), []

    mu = target_mean if target_mean is not None else float(np.mean(series[:max(3, n // 3)]))
    sigma = target_std if target_std is not None else float(np.std(series[:max(3, n // 3)]))
    if sigma < 1e-6:
        sigma = float(np.std(series)) if float(np.std(series)) > 1e-6 else 1.0

    c_plus = np.zeros(n)
    c_minus = np.zeros(n)
    alarms = []

    for i in range(1, n):
        z_i = (series[i] - mu) / sigma
        c_plus[i] = max(0.0, c_plus[i - 1] + z_i - k_slack)
        c_minus[i] = max(0.0, c_minus[i - 1] - z_i - k_slack)

        if c_plus[i] > h_threshold or c_minus[i] > h_threshold:
            alarms.append(i)

    return c_plus, c_minus, alarms


def engineer_model1_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering for Model 1 simulation data.
    """
    feats = df.copy()

    # Total waiting time
    wait_cols = [c for c in feats.columns if "waiting time" in c.lower()]
    if wait_cols:
        feats["Total_Wait_Time"] = feats[wait_cols].sum(axis=1)
        if "VA Time" in feats.columns:
            feats["Wait_to_VA_Ratio"] = feats["Total_Wait_Time"] / (feats["VA Time"] + 1e-5)

    # Utilization imbalance (Standard deviation across station utilizations)
    util_cols = [c for c in feats.columns if "util" in c.lower()]
    if len(util_cols) >= 2:
        feats["Max_Utilization"] = feats[util_cols].max(axis=1)
        feats["Mean_Utilization"] = feats[util_cols].mean(axis=1)
        feats["Util_Imbalance_Std"] = feats[util_cols].std(axis=1)

    return feats


def engineer_model2_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering for Model 2 simulation data.
    """
    feats = df.copy()

    # WIP accumulation
    if "Entities In Part 1" in feats.columns and "Entities Out" in feats.columns:
        feats["Total_WIP_Part1"] = feats["Entities In Part 1"] - feats["Entities Out"]

    if "Part 1 Stored" in feats.columns and "Part 2 Stored" in feats.columns:
        feats["Total_Buffer_Stored"] = feats["Part 1 Stored"] + feats["Part 2 Stored"]

    util_cols = [c for c in feats.columns if "utilization" in c.lower()]
    if util_cols:
        feats["Max_Utilization"] = feats[util_cols].max(axis=1)
        feats["Mean_Utilization"] = feats[util_cols].mean(axis=1)

    return feats
