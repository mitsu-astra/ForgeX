from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class TopFeatureAttribution(BaseModel):
    feature: str
    feature_value: float
    shap_value: float
    contribution: str  # "increases_defect_risk" or "decreases_defect_risk"


class ShapExplanation(BaseModel):
    base_value: float
    top_features: List[TopFeatureAttribution]


class DiagnosisResponse(BaseModel):
    root_cause: str
    confidence: float
    associated_defect: str
    probabilities: Dict[str, float]
    shap_explanation: ShapExplanation
    recommendation: str


class CorrelationItem(BaseModel):
    parameter: str
    spearman_correlation: float
    p_value: float
    is_statistically_significant: bool
    direction: str  # "positive" or "negative"
    strength: str   # "strong", "moderate", "weak"


class CorrelationMatrixResponse(BaseModel):
    defect_type: str
    sample_size: int
    correlations: List[CorrelationItem]
