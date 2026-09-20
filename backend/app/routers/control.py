import os
import sys
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.services.control_service import ControlService, get_control_service
from backend.app.schemas.control import (
    MachineStateResponse,
    ValidateSetpointRequest,
    ValidationResponse,
    ProposeChangeRequest,
    ProposeChangeResponse,
    ConfirmChangeRequest,
    ApplyChangeResponse,
    AIControlRecommendation,
    ControlAuditRecordItem,
    InterventionImpactRequest,
    InterventionImpactResponse,
)
from backend.app.schemas.common import ApiResponse

logger = logging.getLogger("backend.routers.control")
router = APIRouter(prefix="/api/v1/control", tags=["Manual Operator Controls (HITL)"])


@router.get("/state", response_model=ApiResponse)
async def get_machine_state(
    control_service: ControlService = Depends(get_control_service),
):
    """
    Returns current live machine telemetry.
    Clearly marks measured vs setpoint values and designates SIMULATION MODE.
    """
    state = control_service.get_current_state()
    return ApiResponse(
        success=True,
        message="Machine telemetry retrieved in SIMULATION MODE",
        data=state,
    )


@router.post("/validate", response_model=ApiResponse)
async def validate_setpoint(
    payload: ValidateSetpointRequest,
    control_service: ControlService = Depends(get_control_service),
):
    """
    Performs safety boundary check against configured machine limits.
    Blocks unsafe requests and returns detailed rationale.
    """
    result = control_service.validate_setpoint(payload.parameter, payload.value)
    return ApiResponse(
        success=result["is_valid"],
        message=result["reason"],
        data=result,
    )


@router.post("/propose", response_model=ApiResponse)
async def propose_change(
    payload: ProposeChangeRequest,
    control_service: ControlService = Depends(get_control_service),
):
    """
    Creates a pending setpoint change proposal and issues an explicit confirmation token.
    Requires human confirmation before actual actuator write.
    """
    try:
        proposal = control_service.propose_change(
            parameter=payload.parameter,
            value=payload.value,
            source=payload.source,
            operator_id=payload.operator_id,
            notes=payload.notes,
        )
        return ApiResponse(
            success=proposal["is_valid"],
            message=proposal["reason"],
            data=proposal,
        )
    except Exception as e:
        logger.error(f"Error creating proposal: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/apply", response_model=ApiResponse)
async def apply_change(
    payload: ConfirmChangeRequest,
    control_service: ControlService = Depends(get_control_service),
):
    """
    Human-in-the-Loop actuation:
    Requires explicit confirmation token to write to simulated machine controller,
    reads back actual parameter state, and writes an immutable audit log.
    """
    try:
        result = control_service.apply_change(
            proposal_id=payload.proposal_id,
            confirmation_token=payload.confirmation_token,
            operator_confirmed=payload.operator_confirmed,
            operator_id=payload.operator_id,
        )
        return ApiResponse(
            success=result["status"] == "success",
            message=result["message"],
            data=result,
        )
    except ValueError as ve:
        logger.warning(f"Safety/Validation rejection: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Error applying change: {e}")
        raise HTTPException(status_code=500, detail=f"Actuator write failure: {str(e)}")


@router.get("/recommendations", response_model=ApiResponse)
async def get_ai_recommendations(
    control_service: ControlService = Depends(get_control_service),
):
    """
    Returns AI recommendations derived from Vision + Process models.
    NOTE: These are strictly advisory; they are NEVER auto-applied to machines.
    """
    recs = control_service.get_recommendations()
    return ApiResponse(
        success=True,
        message="AI recommendations retrieved",
        data=recs,
    )


@router.get("/audit-trail", response_model=ApiResponse)
async def get_audit_trail(
    limit: int = 50,
    control_service: ControlService = Depends(get_control_service),
):
    """
    Retrieves the immutable audit log of operator adjustments and AI recommendation acceptances.
    """
    trail = control_service.get_audit_trail(limit=limit)
    return ApiResponse(
        success=True,
        message="Control audit log retrieved",
        data=trail,
    )


@router.post("/intervention-impact", response_model=ApiResponse)
async def evaluate_intervention_impact(
    payload: InterventionImpactRequest,
    control_service: ControlService = Depends(get_control_service),
):
    """
    Consensus Engine integration:
    Evaluates process defect risk before vs after operator manual intervention.
    """
    impact = control_service.compare_intervention_impact(
        parameter=payload.parameter,
        old_value=payload.old_value,
        new_value=payload.new_value,
    )
    return ApiResponse(
        success=True,
        message=impact["observation_summary"],
        data=impact,
    )
