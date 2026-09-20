from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ParameterLimit(BaseModel):
    name: str
    unit: str
    min: float
    max: float
    warning_min: float
    warning_max: float
    default_setpoint: float
    max_rate_of_change_per_sec: float
    category: str
    description: str


class MachineParameterLive(BaseModel):
    key: str
    name: str
    unit: str
    measured_value: float
    setpoint_value: float
    status: str  # optimal, warning, critical
    min_limit: float
    max_limit: float
    category: str
    description: str


class MachineStateResponse(BaseModel):
    mode: str = "SIMULATION MODE"
    controller_status: str = "SIMULATED_ACTIVE"
    interlocks_engaged: bool = False
    validation_status: str = "NOT_VALIDATED_PLACEHOLDER"
    parameters: Dict[str, MachineParameterLive]
    timestamp: str


class ValidateSetpointRequest(BaseModel):
    parameter: str
    value: float


class ValidationResponse(BaseModel):
    parameter: str
    requested_value: float
    is_valid: bool
    status_level: str  # valid, warning, blocked
    reason: str
    min_limit: float
    max_limit: float
    unit: str


class ProposeChangeRequest(BaseModel):
    parameter: str
    value: float
    source: str = "manual"  # manual, ai_recommendation
    operator_id: str = "OP-104"
    notes: Optional[str] = None


class ProposeChangeResponse(BaseModel):
    proposal_id: str
    parameter: str
    old_value: float
    proposed_value: float
    unit: str
    is_valid: bool
    status_level: str
    reason: str
    requires_confirmation: bool = True
    confirmation_token: str
    timestamp: str


class ConfirmChangeRequest(BaseModel):
    proposal_id: str
    confirmation_token: str
    operator_confirmed: bool = True
    operator_id: str = "OP-104"


class ApplyChangeResponse(BaseModel):
    event_id: str
    parameter: str
    old_value: float
    applied_value: float
    verified_value: float
    unit: str
    status: str  # success, failed
    mode: str = "SIMULATION MODE"
    message: str
    timestamp: str


class AIControlRecommendation(BaseModel):
    recommendation_id: str
    parameter: str
    parameter_name: str
    current_value: float
    recommended_value: float
    unit: str
    source_model: str  # "Process Model + SHAP", "CUSUM Drift", etc.
    rationale: str
    expected_risk_reduction_pct: float
    projected_monthly_savings_usd: float
    confidence: float
    timestamp: str


class ControlAuditRecordItem(BaseModel):
    event_id: str
    timestamp: str
    parameter: str
    parameter_name: str
    old_value: float
    requested_value: float
    validated_value: float
    applied_value: float
    verified_value: float
    unit: str
    operator_id: str
    source: str  # manual, ai_recommendation, ai_accepted
    mode: str = "simulation"
    validation_result: str  # passed, warning, blocked
    application_result: str  # success, failed
    verification_result: str  # match, discrepancy
    notes: Optional[str] = None


class InterventionImpactRequest(BaseModel):
    parameter: str
    old_value: float
    new_value: float


class InterventionImpactResponse(BaseModel):
    parameter: str
    old_value: float
    new_value: float
    unit: str
    pre_intervention_defect_risk: float
    post_intervention_defect_risk: float
    risk_delta_pct: float
    observation_summary: str  # e.g., "Observed improvement following intervention."
    timestamp: str
