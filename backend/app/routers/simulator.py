import os
import sys
import uuid
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.services.simulation_orchestrator import (
    SimulationOrchestrator,
    get_simulation_orchestrator,
)
from backend.app.schemas.simulator import (
    SimulationRequest,
    SimulationResponse,
    StageControlRequest,
)
from backend.app.schemas.common import ApiResponse
from backend.app.db.db_service import DatabaseService
from backend.app.db.session import SessionLocal
from backend.app.db.models import ControlAuditRecord

logger = logging.getLogger("backend.routers.simulator")
router = APIRouter(prefix="/api/v1/simulator", tags=["What-If Simulator"])


@router.get("/baseline", response_model=ApiResponse)
async def get_simulator_baseline(
    batch_id: Optional[str] = Query(None, description="Optional batch ID context"),
    orchestrator: SimulationOrchestrator = Depends(get_simulation_orchestrator),
):
    """
    Returns the active manufacturing baseline ground truth.
    Derived dynamically from live telemetry, analyzed batch records, or configured defaults,
    with explicit provenance tracking for each parameter.
    """
    try:
        baseline_data = orchestrator.get_active_baseline(batch_id=batch_id)
        return ApiResponse(
            success=True,
            message="Active manufacturing baseline resolved successfully",
            data=baseline_data,
        )
    except Exception as e:
        logger.error(f"[Simulator] Error retrieving active baseline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed retrieving baseline: {str(e)}")


@router.get("/history", response_model=ApiResponse)
async def get_simulation_history(
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    limit: int = Query(10, ge=1, le=50, description="Max scenarios to return"),
):
    """
    Retrieves the chronological audit history of saved What-If simulation scenarios from PostgreSQL/SQLite.
    """
    try:
        scenarios = DatabaseService.get_simulation_scenarios(batch_id=batch_id, limit=limit)
        return ApiResponse(
            success=True,
            message=f"Retrieved {len(scenarios)} saved simulation scenario(s)",
            data=scenarios,
        )
    except Exception as e:
        logger.error(f"[Simulator] Error querying scenario history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed querying scenario history: {str(e)}")


@router.post("/run", response_model=ApiResponse)
async def run_simulation(
    payload: SimulationRequest,
    orchestrator: SimulationOrchestrator = Depends(get_simulation_orchestrator),
):
    """
    Executes a unified What-If Decision Simulation.
    Simulates quality defect kinetics, discrete-event queue bottlenecking,
    line efficiency, and dual-currency financial impacts.
    Preserves full backward compatibility with legacy requests.
    """
    try:
        # Determine modified parameters from either unified or legacy payload
        target_params: Dict[str, float] = {}
        if payload.parameters:
            target_params.update(payload.parameters)
        elif payload.modified_params:
            target_params.update(payload.modified_params)
        else:
            # Default nominal scenario adjustment
            target_params = {
                "hydraulic_pressure_bar": 172.0,
                "coolant_ph": 7.7,
                "conveyor_speed_mps": 0.95,
                "demand": 7.0,
                "spindle_feed_rate": 280.0,
            }

        sim_res = orchestrator.run_simulation(
            parameters=target_params,
            material_code=payload.material,
            batch_id=payload.batch_id,
            baseline_params=payload.baseline_params,
            baseline_defect_rate=payload.baseline_defect_rate,
            baseline_throughput=payload.baseline_throughput,
        )

        mat_name = sim_res.get("material", {}).get("name", "Active Material")
        curr_batch = sim_res.get("batch_id", "ACTIVE")

        return ApiResponse(
            success=True,
            message=f"What-If scenario simulation completed for {mat_name} [Batch: {curr_batch}]",
            data=sim_res,
        )

    except Exception as e:
        logger.error(f"[Simulator] Simulation execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/stage-control", response_model=ApiResponse)
async def stage_simulator_to_control(
    payload: StageControlRequest,
    orchestrator: SimulationOrchestrator = Depends(get_simulation_orchestrator),
):
    """
    Prepares and stages a simulated scenario for machine controller review.
    Does NOT write directly to physical actuators.
    Strictly verifies safety envelope before logging to audit trail.
    """
    baseline_ctx = orchestrator.get_active_baseline(batch_id=payload.batch_id)
    mat_props = baseline_ctx["material"]

    # 1. Run safety validation
    safety_check = orchestrator.validate_safety(payload.parameters, mat_props)
    if safety_check["status"] == "BLOCKED":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot stage unsafe scenario to controller: {safety_check['reason']} Violations: {', '.join(safety_check['violations'])}",
        )

    # 2. Record staged simulation proposal into audit records table
    staged_records = []
    db = SessionLocal()
    try:
        event_group_id = str(uuid.uuid4())[:8]
        for param_name, target_val in payload.parameters.items():
            audit_entry = ControlAuditRecord(
                event_id=f"SIM-STAGE-{event_group_id}-{param_name[:10]}",
                parameter=param_name,
                parameter_name=param_name.replace("_", " ").title(),
                old_value=float(baseline_ctx["parameters"].get(param_name, {}).get("value", target_val)),
                requested_value=float(target_val),
                validated_value=float(target_val),
                applied_value=float(target_val),
                verified_value=float(target_val),
                unit=baseline_ctx["parameters"].get(param_name, {}).get("unit", ""),
                operator_id="SIMULATOR-STAGING",
                source="what_if_simulator",
                mode="simulation",
                validation_result=safety_check["status"].lower(),
                application_result="staged_simulation_only",
                verification_result="match",
                notes=f"{payload.notes} • Simulation only — controller integration not connected",
            )
            db.add(audit_entry)
            staged_records.append({
                "parameter": param_name,
                "value": target_val,
                "unit": audit_entry.unit,
            })
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"[Simulator] Could not persist audit trail: {e}")
    finally:
        db.close()

    return ApiResponse(
        success=True,
        message="Scenario successfully staged for controller review (Simulation mode only — physical integration not connected).",
        data={
            "staged_parameters": staged_records,
            "safety_status": safety_check["status"],
            "controller_status": "Simulation only — controller integration not connected",
        },
    )
