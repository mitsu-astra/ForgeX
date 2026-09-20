from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ScenarioState(BaseModel):
    defect_rate_pct: float
    throughput_per_hr: float
    monthly_loss_usd: float
    monthly_loss_inr: Optional[float] = None
    peak_utilization_pct: Optional[float] = None
    line_efficiency_pct: Optional[float] = None
    wip_units: Optional[float] = None
    lead_time_hrs: Optional[float] = None
    primary_bottleneck: Optional[str] = None
    station_utilizations: Optional[Dict[str, float]] = None
    fpy_pct: Optional[float] = None


class ScenarioDelta(BaseModel):
    defect_reduction_pct: float
    throughput_change_pct: float
    monthly_savings_usd: float
    monthly_savings_inr: Optional[float] = None
    defect_rate_delta_pct: Optional[float] = None
    throughput_delta_per_hr: Optional[float] = None
    peak_utilization_delta_pct: Optional[float] = None
    line_efficiency_delta_pct: Optional[float] = None
    wip_delta_units: Optional[float] = None
    lead_time_delta_hrs: Optional[float] = None


class StationComparisonItem(BaseModel):
    station: str
    baseline_utilization_pct: float
    scenario_utilization_pct: float
    delta_pct: float
    is_bottleneck_baseline: bool
    is_bottleneck_scenario: bool


class QualityImpact(BaseModel):
    crack_reduction_pct: float
    rust_reduction_pct: float
    scratch_reduction_pct: float
    tool_wear_reduction_pct: float
    composite_reduction_pct: float
    fpy_baseline_pct: float
    fpy_simulated_pct: float
    governing_physics: Optional[str] = None


class BottleneckImpact(BaseModel):
    current_bottleneck: str
    scenario_bottleneck: str
    is_constraint_shifted: bool
    line_balance_status: str
    station_comparison: List[StationComparisonItem]


class EconomicImpact(BaseModel):
    monthly_scrap_savings_usd: float
    monthly_throughput_gain_usd: float
    total_monthly_benefit_usd: float
    monthly_scrap_savings_inr: float
    monthly_throughput_gain_inr: float
    total_monthly_benefit_inr: float
    exchange_rate: float = 83.50
    basis: str


class SafetyStatus(BaseModel):
    status: str  # SAFE, WARNING, BLOCKED
    reason: str
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    is_safe: bool = True


class SimulationRequest(BaseModel):
    """
    Unified Simulation Request.
    Supports both unified `parameters` and legacy `baseline_params`/`modified_params` for complete backward compatibility.
    """
    parameters: Optional[Dict[str, float]] = None
    material: Optional[str] = None
    batch_id: Optional[str] = None
    baseline_params: Optional[Dict[str, float]] = None
    modified_params: Optional[Dict[str, float]] = None
    baseline_defect_rate: Optional[float] = None
    baseline_throughput: Optional[float] = None


class SimulationResponse(BaseModel):
    baseline: ScenarioState
    scenario: ScenarioState
    simulated: ScenarioState  # Backward-compatible alias
    delta: ScenarioDelta
    safety: SafetyStatus
    quality_impact: QualityImpact
    bottleneck_impact: BottleneckImpact
    economics: EconomicImpact
    recommendation_score: int
    risk_level: str
    material: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class StageControlRequest(BaseModel):
    batch_id: Optional[str] = None
    material_code: Optional[str] = None
    parameters: Dict[str, float]
    notes: Optional[str] = "Simulation scenario staged from What-If Decision Simulator"
