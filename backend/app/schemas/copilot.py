from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class CopilotChatMessage(BaseModel):
    role: str  # "user" or "assistant" or "system"
    content: str
    timestamp: Optional[str] = None


class CopilotChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    history: Optional[List[CopilotChatMessage]] = None


class RecommendedAction(BaseModel):
    action_title: str
    target_station: str
    parameter_adjustment: str
    expected_impact: str
    priority: str  # "High", "Medium", "Low"


class CopilotChatResponse(BaseModel):
    response: str
    evidence_sources: List[str]
    suggested_actions: List[RecommendedAction]
    confidence_score: float
    guardrail_status: Optional[str] = "compliant"
    guardrail_rule_applied: Optional[str] = None
    guardrail_details: Optional[Dict[str, Any]] = None
