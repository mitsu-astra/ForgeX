import os
import sys
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.schemas.common import ApiResponse

logger = logging.getLogger("backend.routers.analytics")
router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & KPIs"])


@router.get("/overview", response_model=ApiResponse)
async def get_analytics_overview():
    """
    Returns dashboard overview KPIs, overall equipment effectiveness (OEE),
    inspection yield rate, defect distribution, and financial health metrics.
    """
    overview_data = {
        "kpis": {
            "overall_yield_pct": 96.8,
            "total_inspected_today": 8420,
            "defects_detected_today": 269,
            "current_line_throughput_pph": 145.0,
            "primary_bottleneck_station": "Drilling",
            "bottleneck_utilization_pct": 96.0,
            "estimated_monthly_scrap_loss_usd": 13450.0,
            "potential_optimization_savings_usd": 708039.71,
        },
        "defect_distribution": [
            {"type": "Crack", "count": 68, "pct": 25.3, "primary_cause": "Hydraulic Overload"},
            {"type": "Rust", "count": 94, "pct": 34.9, "primary_cause": "Queue Oxidation / pH"},
            {"type": "Scratch", "count": 52, "pct": 19.3, "primary_cause": "Conveyor Friction"},
            {"type": "Hole / Misalignment", "count": 55, "pct": 20.5, "primary_cause": "Tool Wear"},
        ],
        "station_utilizations": [
            {"station": "Blanking", "utilization": 0.42, "status": "nominal"},
            {"station": "Drilling", "utilization": 0.96, "status": "critical"},
            {"station": "Milling", "utilization": 0.36, "status": "nominal"},
            {"station": "Assembly", "utilization": 0.72, "status": "warning"},
            {"station": "Inspection", "utilization": 0.28, "status": "nominal"},
        ],
        "hourly_yield_trend": [
            {"hour": "08:00", "yield_pct": 98.2, "throughput": 148},
            {"hour": "09:00", "yield_pct": 97.9, "throughput": 146},
            {"hour": "10:00", "yield_pct": 95.1, "throughput": 140},
            {"hour": "11:00", "yield_pct": 94.8, "throughput": 138},
            {"hour": "12:00", "yield_pct": 96.4, "throughput": 142},
            {"hour": "13:00", "yield_pct": 97.5, "throughput": 147},
            {"hour": "14:00", "yield_pct": 98.0, "throughput": 150},
        ],
    }

    return ApiResponse(
        success=True,
        message="Analytics overview retrieved successfully",
        data=overview_data,
    )
