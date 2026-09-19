from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class BottleneckStation(BaseModel):
    station: str
    utilization: float
    queue_time_hrs: float
    severity: str  # "critical", "warning", "nominal"
    impact: str
    recommended_action: str


class EconomicImpact(BaseModel):
    hourly_throughput_loss_usd: float
    daily_throughput_loss_usd: float
    monthly_throughput_loss_usd: float


class BottleneckAnalysisResponse(BaseModel):
    primary_bottleneck: Optional[str]
    max_utilization: float
    line_efficiency_pct: float
    total_wip_units: float
    estimated_lead_time_hrs: float
    bottlenecks: List[BottleneckStation]
    economic_impact: EconomicImpact
    all_station_utilizations: Dict[str, float]
    all_station_queue_times: Dict[str, float]


class DriftAnalysisRequest(BaseModel):
    parameter_name: str
    values: List[float]
    threshold: float = 5.0


class DriftAnalysisResponse(BaseModel):
    parameter_name: str
    drift_detected: bool
    drift_start_index: Optional[int]
    positive_drift_detected: bool
    negative_drift_detected: bool
    max_cusum_statistic: float
    threshold: float
