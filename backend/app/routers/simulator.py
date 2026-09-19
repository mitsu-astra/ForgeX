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

from backend.app.services.model_service import ModelService, get_model_service
from backend.app.schemas.simulator import (
    SimulationRequest,
    SimulationResponse,
    ScenarioState,
    ScenarioDelta,
)
from backend.app.schemas.common import ApiResponse
from backend.app.db.db_service import DatabaseService

logger = logging.getLogger("backend.routers.simulator")
router = APIRouter(prefix="/api/v1/simulator", tags=["What-If Simulator"])


@router.post("/run", response_model=ApiResponse)
async def run_simulation(
    payload: SimulationRequest,
    model_service: ModelService = Depends(get_model_service),
):
    """
    Simulates operational parameter adjustments grounded in active material properties from PostgreSQL,
    forecasting predicted defect reduction %, throughput impact, and monthly scrap/rework savings ($).
    """
    if model_service.what_if_simulator is None:
        raise HTTPException(status_code=503, detail="What-If Simulator engine is not loaded.")

    try:
        # 1. Fetch active material and batch context from PostgreSQL
        active_batch = DatabaseService.get_active_batch()
        batch_id = active_batch.batch_id if active_batch else "BATCH-2026-001"
        active_mat = DatabaseService.get_active_material(batch_id)

        material_props = {
            "code": active_mat.code,
            "name": active_mat.name,
            "alloy_grade": active_mat.alloy_grade,
            "yield_strength_mpa": active_mat.yield_strength_mpa,
            "tensile_strength_mpa": active_mat.tensile_strength_mpa,
            "critical_hydraulic_pressure_bar": active_mat.critical_hydraulic_pressure_bar,
            "optimal_coolant_ph_min": active_mat.optimal_coolant_ph_min,
            "optimal_coolant_ph_max": active_mat.optimal_coolant_ph_max,
            "max_conveyor_speed_mps": active_mat.max_conveyor_speed_mps,
            "cost_per_kg_usd": active_mat.cost_per_kg_usd,
            "scrap_penalty_usd": active_mat.scrap_penalty_usd,
            "governing_physics": active_mat.governing_physics,
        }

        # 2. Run simulation with material metallurgical grounding
        sim_res = model_service.what_if_simulator.simulate_scenario(
            baseline_params=payload.baseline_params,
            modified_params=payload.modified_params,
            baseline_defect_rate=payload.baseline_defect_rate,
            baseline_throughput=payload.baseline_throughput,
            material_props=material_props,
        )

        b = sim_res["baseline"]
        s = sim_res["simulated"]
        d = sim_res["delta"]

        # 3. Persist scenario into PostgreSQL
        DatabaseService.record_simulation_scenario(
            batch_id=batch_id,
            material_code=active_mat.code,
            baseline_defect_pct=b["defect_rate_pct"],
            simulated_defect_pct=s["defect_rate_pct"],
            defect_reduction_pct=d["defect_reduction_pct"],
            throughput_change_pct=d["throughput_change_pct"],
            monthly_savings_usd=d["monthly_savings_usd"],
            recommendation_score=sim_res["recommendation_score"],
            risk_level=sim_res["risk_level"],
            parameters={"baseline": payload.baseline_params, "modified": payload.modified_params},
        )

        # 4. Cache latest simulation in PostgreSQL
        DatabaseService.set_cache("latest_simulation_result", sim_res)

        resp = SimulationResponse(
            baseline=ScenarioState(
                defect_rate_pct=b["defect_rate_pct"],
                throughput_per_hr=b["throughput_per_hr"],
                monthly_loss_usd=b["monthly_loss_usd"],
            ),
            simulated=ScenarioState(
                defect_rate_pct=s["defect_rate_pct"],
                throughput_per_hr=s["throughput_per_hr"],
                monthly_loss_usd=s["monthly_loss_usd"],
            ),
            delta=ScenarioDelta(
                defect_reduction_pct=d["defect_reduction_pct"],
                throughput_change_pct=d["throughput_change_pct"],
                monthly_savings_usd=d["monthly_savings_usd"],
            ),
            recommendation_score=sim_res["recommendation_score"],
            risk_level=sim_res["risk_level"],
            material=sim_res.get("material"),
        )

        return ApiResponse(
            success=True,
            message=f"What-If scenario simulation completed for {active_mat.name} [PostgreSQL Batch: {batch_id}]",
            data=resp.model_dump(),
        )

    except Exception as e:
        logger.error(f"Simulation execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")
