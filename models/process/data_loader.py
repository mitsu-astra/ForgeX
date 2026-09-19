"""
Data Loader and CSV Parser for Manufacturing Simulation Data
Features header-based automatic dataset classification for Model 1, Model 2, Model 3, and Economic CSVs.
"""

import os
from typing import Tuple, Dict, Any, Optional, List
import pandas as pd
import numpy as np


class CSVTypeDetector:
    """
    Detects CSV data type strictly by inspecting column headers and contents.
    """

    @staticmethod
    def detect_type(df: pd.DataFrame) -> str:
        # Clean column names
        cols = [str(c).strip() for c in df.columns]
        cols_lower = [c.lower() for c in cols]

        # Check Economic CSV
        economic_keywords = ["scrap_cost", "rework_cost", "contribution_margin", "hourly_labor_cost", "parameter", "unit_cost"]
        if any(any(kw in c for kw in economic_keywords) for c in cols_lower):
            return "economic"

        # Check Model 1 (10 core columns, e.g., 'drilling waiting time', 'assembly waiting time', 'drilling util')
        if any("drilling waiting time" in c for c in cols_lower) or (
            "demand" in cols_lower and "parts per hour" in cols_lower and any("drilling util" in c for c in cols_lower)
        ):
            return "model_1"

        # Check Model 2 (16 core columns, e.g., 'entities in part 1', 'part 1 storage time')
        if any("entities in part 1" in c for c in cols_lower) or any("part 1 storage time" in c for c in cols_lower):
            return "model_2"

        # Check Model 3 (77-78 columns, e.g., 'blanking_util', 'time_now', 'press1_util')
        if any("blanking_util" in c for c in cols_lower) or any("time_now" in c for c in cols_lower) or len(cols) >= 50:
            return "model_3"

        # Fallback based on column count
        if len(cols) <= 12:
            return "model_1"
        elif len(cols) <= 25:
            return "model_2"
        else:
            return "model_3"


def load_and_clean_csv(file_path: str, nrows: Optional[int] = None) -> Tuple[pd.DataFrame, str]:
    """
    Loads CSV file, removes empty trailing columns, and identifies the simulation model type.
    """
    df = pd.read_csv(file_path, nrows=nrows)

    # Drop completely empty columns (e.g. Unnamed: 10, etc.)
    df = df.dropna(how="all", axis=1)
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed:\s*\d+", case=False)]

    model_type = CSVTypeDetector.detect_type(df)
    return df, model_type


def load_all_simulation_datasets(
    base_dir: str = "/home/koushik_2109/Hackathons/CMR/Manufacturing Data Shared Facility - Discrete-Event Simulation",
) -> Dict[str, pd.DataFrame]:
    """
    Loads Model 1, Model 2, and Model 3 simulation datasets.
    """
    datasets = {}

    m1_path = os.path.join(base_dir, "Model 1", "Model_1.csv")
    if os.path.exists(m1_path):
        df1, _ = load_and_clean_csv(m1_path)
        datasets["model_1"] = df1

    m2_path = os.path.join(base_dir, "Model 2", "Model_2.csv")
    if os.path.exists(m2_path):
        df2, _ = load_and_clean_csv(m2_path)
        datasets["model_2"] = df2

    m3_path = os.path.join(base_dir, "Model 3", "Model_3.csv")
    if os.path.exists(m3_path):
        # Load sample for rapid processing if dataset is massive (600k rows)
        df3, _ = load_and_clean_csv(m3_path, nrows=100000)
        datasets["model_3"] = df3

    return datasets
