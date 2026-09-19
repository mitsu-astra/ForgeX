import os
import sys
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import numpy as np
import pandas as pd

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.services.model_service import ModelService, get_model_service
from backend.app.schemas.process import (
    BottleneckAnalysisResponse,
    DriftAnalysisRequest,
    DriftAnalysisResponse,
    BottleneckStation,
    EconomicImpact,
)
from backend.app.schemas.common import ApiResponse
from models.process.feature_engineering import detect_cusum_drift

logger = logging.getLogger("backend.routers.process")
router = APIRouter(prefix="/api/v1/process", tags=["Process Intelligence"])


class ProcessStatePayload(BaseModel):
    station_utilizations: Optional[Dict[str, float]] = None
    station_queue_times: Optional[Dict[str, float]] = None
    throughput_per_hr: Optional[float] = 145.0
    demand: Optional[float] = 7.0


@router.post("/bottlenecks", response_model=ApiResponse)
async def analyze_bottlenecks(
    payload: Optional[ProcessStatePayload] = None,
    model_service: ModelService = Depends(get_model_service),
):
    """
    Analyzes current station utilizations and queue times to detect operational bottlenecks
    and estimate line balancing efficiency and financial loss.
    """
    if payload is None:
        payload = ProcessStatePayload()

    if model_service.bottleneck_detector is None:
        raise HTTPException(status_code=503, detail="Bottleneck Detector is not initialized.")

    # Flatten into dictionary format expected by BottleneckDetector
    state_dict = {}
    if payload.station_utilizations:
        for stn, u in payload.station_utilizations.items():
            state_dict[f"{stn} Util"] = u
    else:
        # Default representative state
        state_dict["Drilling Util"] = 0.96
        state_dict["Milling Util"] = 0.36
        state_dict["Assembly Util"] = 0.72

    if payload.station_queue_times:
        for stn, q in payload.station_queue_times.items():
            state_dict[f"{stn} Waiting Time"] = q
    else:
        state_dict["Drilling Waiting Time"] = 4.12
        state_dict["Milling Waiting Time"] = 0.85
        state_dict["Assembly Waiting Time"] = 2.09

    state_dict["Parts per hour"] = payload.throughput_per_hr or 145.0
    state_dict["Demand"] = payload.demand or 7.0

    analysis = model_service.bottleneck_detector.analyze_process_state(state_dict)

    bottleneck_list = [
        BottleneckStation(
            station=b["station"],
            utilization=b["utilization"],
            queue_time_hrs=b["queue_time_hrs"],
            severity=b["severity"],
            impact=b["impact"],
            recommended_action=b.get("recommended_action", "Optimize station capacity and balance workload"),
        )
        for b in analysis["bottlenecks"]
    ]

    econ = analysis["economic_impact"]
    econ_obj = EconomicImpact(
        hourly_throughput_loss_usd=econ["hourly_throughput_loss_usd"],
        daily_throughput_loss_usd=econ["daily_throughput_loss_usd"],
        monthly_throughput_loss_usd=econ["monthly_throughput_loss_usd"],
    )

    resp = BottleneckAnalysisResponse(
        primary_bottleneck=analysis["primary_bottleneck"],
        max_utilization=analysis["max_utilization"],
        line_efficiency_pct=analysis["line_efficiency_pct"],
        total_wip_units=analysis["total_wip_units"],
        estimated_lead_time_hrs=analysis["estimated_lead_time_hrs"],
        bottlenecks=bottleneck_list,
        economic_impact=econ_obj,
        all_station_utilizations=analysis["all_station_utilizations"],
        all_station_queue_times=analysis["all_station_queue_times"],
    )

    return ApiResponse(
        success=True,
        message="Process bottleneck analysis completed successfully",
        data=resp.model_dump(),
    )


@router.post("/drift-analysis", response_model=ApiResponse)
async def analyze_process_drift(
    payload: DriftAnalysisRequest,
):
    """
    Applies Tabular CUSUM control charting to detect drift in manufacturing process parameters.
    """
    values_arr = np.array(payload.values, dtype=float)
    if len(values_arr) < 5:
        raise HTTPException(status_code=400, detail="At least 5 time-series data points are required for CUSUM analysis.")

    c_plus, c_minus, alarms = detect_cusum_drift(values_arr, h_threshold=payload.threshold)
    drift_detected = len(alarms) > 0
    drift_start_idx = alarms[0] if drift_detected else None
    max_stat = float(max(np.max(c_plus) if len(c_plus) > 0 else 0.0, np.max(c_minus) if len(c_minus) > 0 else 0.0))

    resp = DriftAnalysisResponse(
        parameter_name=payload.parameter_name,
        drift_detected=drift_detected,
        drift_start_index=drift_start_idx,
        positive_drift_detected=bool(np.any(c_plus > payload.threshold)),
        negative_drift_detected=bool(np.any(c_minus > payload.threshold)),
        max_cusum_statistic=round(max_stat, 3),
        threshold=payload.threshold,
    )

    return ApiResponse(
        success=True,
        message=f"CUSUM drift analysis for '{payload.parameter_name}' completed",
        data=resp.model_dump(),
    )
