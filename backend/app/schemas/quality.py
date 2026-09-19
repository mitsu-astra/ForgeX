from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class BoundingBox(BaseModel):
    bbox_id: int
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    width: int
    height: int
    area_pixels: int
    area_percentage: float
    confidence: float
    defect_type: str


class PredictionResult(BaseModel):
    defect_class: str
    confidence: float
    class_id: int
    probabilities: Dict[str, float]


class UncertaintyResult(BaseModel):
    uncertainty_score: float
    is_uncertain: bool
    threshold: float
    confidence_interval_95: List[float]


class LocalizationResult(BaseModel):
    bounding_boxes: List[BoundingBox]
    defect_area_percentage: float
    heatmap_base64: Optional[str] = None
    overlay_base64: Optional[str] = None


class InspectionResponse(BaseModel):
    filename: str
    prediction: PredictionResult
    uncertainty: UncertaintyResult
    localization: Optional[LocalizationResult] = None
    inference_time_ms: float
    status: str = "success"
    inspected_at: str


class BatchInspectionResponse(BaseModel):
    total_images: int
    successful_inspections: int
    defective_count: int
    defect_rate_pct: float
    class_distribution: Dict[str, int]
    avg_inference_time_ms: float
    results: List[InspectionResponse]
