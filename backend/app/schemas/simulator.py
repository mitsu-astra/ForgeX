from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ScenarioState(BaseModel):
    defect_rate_pct: float
    throughput_per_hr: float
    monthly_loss_usd: float


class ScenarioDelta(BaseModel):
    defect_reduction_pct: float
    throughput_change_pct: float
    monthly_savings_usd: float


class SimulationRequest(BaseModel):
    baseline_params: Dict[str, float] = Field(
        default_factory=lambda: {
            "pressure_bar": 185.0,
            "coolant_ph": 7.0,
            "conveyor_speed_mps": 1.2,
            "demand": 1.0,
        }
    )
    modified_params: Dict[str, float] = Field(
        default_factory=lambda: {
            "pressure_bar": 168.0,
            "coolant_ph": 7.6,
            "conveyor_speed_mps": 0.95,
            "demand": 1.0,
        }
    )
    baseline_defect_rate: float = 0.123
    baseline_throughput: float = 145.0


class SimulationResponse(BaseModel):
    baseline: ScenarioState
    simulated: ScenarioState
    delta: ScenarioDelta
    recommendation_score: int
    risk_level: str
    material: Optional[Dict[str, Any]] = None
