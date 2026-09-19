import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Model Weights Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    VISION_MODEL_WEIGHTS: str = os.path.join(BASE_DIR, "models", "weights", "efficientnet_b4_defect.pth")
    PROCESS_MODEL_WEIGHTS: str = os.path.join(BASE_DIR, "models", "weights", "xgboost_process.pkl")
    CORRELATION_MODEL_WEIGHTS: str = os.path.join(BASE_DIR, "models", "weights", "xgboost_correlation.pkl")

    # Upload & Storage Directories
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "backend", "data", "uploads")
    PROCESSED_DIR: str = os.path.join(BASE_DIR, "backend", "data", "processed")
    RESULTS_DIR: str = os.path.join(BASE_DIR, "backend", "data", "results")

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",
    ]

    # Economic Defaults (USD)
    DEFAULT_SCRAP_COST_PER_UNIT: float = 50.0
    DEFAULT_REWORK_COST_PER_UNIT: float = 30.0
    DEFAULT_CONTRIBUTION_MARGIN: float = 150.0

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("VISION_MODEL_WEIGHTS", "PROCESS_MODEL_WEIGHTS", "CORRELATION_MODEL_WEIGHTS", mode="before")
    @classmethod
    def resolve_weights_path(cls, v):
        if isinstance(v, str) and not os.path.isabs(v):
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            candidate1 = os.path.join(base, v)
            if os.path.exists(candidate1):
                return candidate1
            basename = os.path.basename(v)
            alias_map = {
                "efficientnet_b4_defect_classifier.pth": "efficientnet_b4_defect.pth",
                "xgboost_process_model.pkl": "xgboost_process.pkl",
                "xgboost_correlation_model.pkl": "xgboost_correlation.pkl",
            }
            target_name = alias_map.get(basename, basename)
            candidate2 = os.path.join(base, "models", "weights", target_name)
            if os.path.exists(candidate2):
                return candidate2
            return candidate1
        return v

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
