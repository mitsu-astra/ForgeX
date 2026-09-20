import os
import sys
import logging
from typing import List, Dict, Any, Optional
from collections import Counter
from fastapi import APIRouter, Depends

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.schemas.common import ApiResponse
from backend.app.services.process_store import process_store
from backend.app.services.inspection_store import inspection_store
from backend.app.db.session import SessionLocal
from backend.app.db.models import InspectionRecord, Batch
from backend.app.db.db_service import DatabaseService

logger = logging.getLogger("backend.routers.analytics")
router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & KPIs"])

DEFECT_CAUSE_MAP = {
    "crack": "Hydraulic Overload / Microstructural Stress",
    "rust": "Electrochemical Acidification / Queue Oxidation",
    "scratch": "Conveyor Belt Friction / Transfer Misalignment",
    "hole": "Excessive Drill Feed Rate / Tool Wear",
}


@router.get("/overview", response_model=ApiResponse)
async def get_analytics_overview():
    """
    Returns dynamically computed dashboard KPIs, inspection yield rate, defect distribution,
    process throughput, and recent production events derived EXCLUSIVELY from real analyzed data.
    If no batch or telemetry data has been uploaded yet, returns clean zero-state metrics.
    """
    # 1. Fetch real inspection records from DB
    records: List[Dict[str, Any]] = []
    try:
        db = SessionLocal()
        db_records = db.query(InspectionRecord).order_by(InspectionRecord.created_at.desc()).all()
        for r in db_records:
            records.append({
                "id": r.id,
                "filename": r.filename,
                "defect_class": r.defect_class.lower(),
                "confidence": r.confidence,
                "created_at": r.created_at.strftime("%H:%M:%S") if r.created_at else "Just now",
            })
        db.close()
    except Exception as e:
        logger.warning(f"Failed querying inspection records from DB: {e}")

    # Fall back to in-memory store if DB is empty but session has inspections
    if not records:
        store_items = inspection_store.get_all()
        for idx, item in enumerate(store_items):
            pred = item.get("prediction", {})
            records.append({
                "id": idx + 1,
                "filename": item.get("filename", f"Specimen_{idx}"),
                "defect_class": pred.get("defect_class", "normal").lower(),
                "confidence": pred.get("confidence", 0.0),
                "created_at": item.get("inspected_at", "Just now"),
            })

    total_inspected = len(records)
    defective_records = [r for r in records if r["defect_class"] != "normal"]
    defects_count = len(defective_records)

    if total_inspected > 0:
        yield_pct = round(((total_inspected - defects_count) / total_inspected) * 100.0, 1)
    else:
        yield_pct = 0.0

    # 2. Defect distribution from real specimens
    defect_distribution = []
    if defects_count > 0:
        counts = Counter(r["defect_class"] for r in defective_records)
        for d_type, cnt in counts.items():
            pct = round((cnt / defects_count) * 100.0, 1)
            primary_cause = DEFECT_CAUSE_MAP.get(d_type, "Operational Parameter Deviation")
            defect_distribution.append({
                "type": d_type.capitalize(),
                "count": cnt,
                "pct": pct,
                "primary_cause": primary_cause,
            })

    # 3. Process telemetry from real process_store
    proc_state = process_store.get_state()
    if proc_state is not None:
        throughput = round(float(proc_state.get("throughput_per_hr", 0.0)), 1)
        bottleneck_stn = proc_state.get("bottleneck_station", None)
        bottleneck_util = round(float(proc_state.get("bottleneck_utilization_pct", 0.0)), 1)
        monthly_loss = round(float(proc_state.get("monthly_financial_loss_usd", 0.0)), 2)
        potential_savings = round(float(proc_state.get("potential_savings_usd", 0.0)), 2)
        station_utils = proc_state.get("station_utilizations", [])
    else:
        throughput = 0.0
        bottleneck_stn = None
        bottleneck_util = 0.0
        monthly_loss = 0.0
        potential_savings = 0.0
        station_utils = []

    # 4. Recent production diagnostic events from real inspections
    recent_events = []
    for r in records[:6]:
        is_defect = r["defect_class"] != "normal"
        recent_events.append({
            "id": r["id"],
            "title": f"Surface {r['defect_class'].capitalize()} detected" if is_defect else "Specimen verified conforming",
            "station": f"Inspection Station 03 · {r['filename']}",
            "defect_class": r["defect_class"].capitalize(),
            "confidence_pct": round(r["confidence"] * 100.0, 1) if r.get("confidence") else 0.0,
            "is_defect": is_defect,
            "timestamp": r.get("created_at", "Just now"),
        })

    overview_data = {
        "kpis": {
            "overall_yield_pct": yield_pct if total_inspected > 0 else 0.0,
            "total_inspected_today": total_inspected,
            "defects_detected_today": defects_count,
            "current_line_throughput_pph": throughput,
            "primary_bottleneck_station": bottleneck_stn,
            "bottleneck_utilization_pct": bottleneck_util,
            "estimated_monthly_scrap_loss_usd": monthly_loss,
            "potential_optimization_savings_usd": potential_savings,
        },
        "defect_distribution": defect_distribution,
        "station_utilizations": station_utils,
        "hourly_yield_trend": [],
        "recent_events": recent_events,
    }

    return ApiResponse(
        success=True,
        message="Analytics overview retrieved successfully",
        data=overview_data,
    )
