"""
reports.py — FastAPI router for industrial analysis report generation,
retrieval, history listing, and PDF download.

All report data is served from the AnalysisReport database table.
The canonical JSON payload is the single source of truth for both
the frontend report view and the PDF download endpoint.
"""
import os
import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.app.db.db_service import DatabaseService
from backend.app.schemas.common import ApiResponse

logger = logging.getLogger("backend.routers.reports")
router = APIRouter(prefix="/api/v1/reports", tags=["Analysis Reports"])


class GenerateReportRequest(BaseModel):
    batch_id: str


# ---------------------------------------------------------------------------
# POST /api/v1/reports/generate
# Runs synchronously — generation is fast (~1-2s for JSON, PDF is separate)
# ---------------------------------------------------------------------------
@router.post("/generate", response_model=ApiResponse)
async def generate_report_endpoint(payload: GenerateReportRequest):
    """
    Trigger report generation for a batch_id.

    If the requested batch_id has no data in the DB, automatically falls back
    to the current active batch so there is always a meaningful report.

    Runs synchronously — the router returns the report_id + status when done.
    NO pre-creation race condition: only the service creates the DB record.
    """
    requested_batch_id = payload.batch_id.strip()
    if not requested_batch_id:
        raise HTTPException(status_code=400, detail="batch_id is required.")

    # Resolve the real batch_id that actually has data
    batch_id = _resolve_batch_id(requested_batch_id)
    logger.info(f"[Reports] Generate request: requested={requested_batch_id}, resolved={batch_id}")

    # Import and run the service (creates its own single DB record)
    from backend.app.services.report_service import generate_report as svc_generate
    result = svc_generate(batch_id)

    return ApiResponse(
        success=result.get("status") in ("COMPLETED", "PARTIAL"),
        message=f"Report {result.get('status', 'UNKNOWN')} — report_id: {result.get('report_id')}",
        data={
            "report_id": result.get("report_id"),
            "batch_id": batch_id,
            "status": result.get("status"),
        },
    )


def _resolve_batch_id(requested: str) -> str:
    """
    Return the batch_id that actually has data in the DB.
    Priority:
      1. If requested batch has InspectionRecords, ProcessState, or UploadedFiles → use it
      2. Otherwise check active batch if it has data → use it
      3. Otherwise check the batch with the most inspection records in the DB
      4. Otherwise return requested as fallback
    """
    from sqlalchemy import text
    from backend.app.db.session import SessionLocal
    from backend.app.db.models import InspectionRecord, ProcessState, Batch, UploadedFile

    db = SessionLocal()
    try:
        # Check if requested batch has actual inspection, process, or file data
        has_inspection = db.query(InspectionRecord).filter(
            InspectionRecord.batch_id == requested
        ).first() is not None
        has_process = db.query(ProcessState).filter(
            ProcessState.batch_id == requested
        ).first() is not None
        has_files = db.query(UploadedFile).filter(
            UploadedFile.batch_id == requested
        ).first() is not None

        if has_inspection or has_process or has_files:
            return requested

        # Fall back: check if active batch has data
        active_batch = db.query(Batch).filter(Batch.status == "active").order_by(
            Batch.created_at.desc()
        ).first()
        if active_batch:
            act_has_data = (
                db.query(InspectionRecord).filter(InspectionRecord.batch_id == active_batch.batch_id).first() is not None
                or db.query(UploadedFile).filter(UploadedFile.batch_id == active_batch.batch_id).first() is not None
            )
            if act_has_data:
                return active_batch.batch_id

        # Batch with most inspection records
        try:
            row = db.execute(
                text("SELECT batch_id, COUNT(*) as cnt FROM inspection_records GROUP BY batch_id ORDER BY cnt DESC LIMIT 1")
            ).fetchone()
            if row and row[0]:
                return row[0]
        except Exception:
            pass

        if active_batch:
            return active_batch.batch_id

        return requested
    except Exception as e:
        logger.warning(f"[Reports] _resolve_batch_id error: {e}")
        return requested
    finally:
        db.close()


# ---------------------------------------------------------------------------
# GET /api/v1/reports/
# ---------------------------------------------------------------------------
@router.get("/", response_model=ApiResponse)
async def list_reports():
    """Return all analysis reports, newest first — used for the Reports History page."""
    reports = DatabaseService.list_reports()
    data = []
    for r in reports:
        data.append({
            "report_id": r.report_id,
            "batch_id": r.batch_id,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "has_pdf": bool(r.report_pdf_path and os.path.exists(r.report_pdf_path)),
            "error_message": r.error_message,
        })
    return ApiResponse(
        success=True,
        message=f"{len(data)} report(s) found.",
        data={"reports": data, "total": len(data)},
    )


# ---------------------------------------------------------------------------
# GET /api/v1/reports/batch/{batch_id}
# ---------------------------------------------------------------------------
@router.get("/batch/{batch_id}", response_model=ApiResponse)
async def get_report_by_batch(batch_id: str):
    """Get the most recent COMPLETED report for a batch_id."""
    from backend.app.db.session import SessionLocal
    from backend.app.db.models import AnalysisReport

    db = SessionLocal()
    try:
        report = (
            db.query(AnalysisReport)
            .filter(
                AnalysisReport.batch_id == batch_id,
                AnalysisReport.status.in_(["COMPLETED", "PARTIAL"])
            )
            .order_by(AnalysisReport.created_at.desc())
            .first()
        )
    finally:
        db.close()

    if not report:
        return ApiResponse(success=False, message=f"No completed report found for batch {batch_id}.", data=None)
    return _build_report_response(report)


# ---------------------------------------------------------------------------
# GET /api/v1/reports/{report_id}
# ---------------------------------------------------------------------------
@router.get("/{report_id}", response_model=ApiResponse)
async def get_report(report_id: str):
    """Get a specific report by report_id — returns the full canonical payload."""
    if report_id in ("list", "generate"):
        return await list_reports()

    report = DatabaseService.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")
    return _build_report_response(report)


# ---------------------------------------------------------------------------
# GET /api/v1/reports/{report_id}/download
# ---------------------------------------------------------------------------
@router.get("/{report_id}/download")
async def download_report_pdf(report_id: str):
    """
    Stream the PDF report for download.
    If the PDF file is missing, regenerate it from the stored canonical payload.
    """
    report = DatabaseService.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")

    if report.status not in ("COMPLETED", "PARTIAL"):
        raise HTTPException(
            status_code=409,
            detail=f"Report is not ready (status: {report.status}).",
        )

    pdf_path = report.report_pdf_path
    if not pdf_path or not os.path.exists(pdf_path):
        logger.info(f"[Reports] PDF missing for {report_id}, regenerating from stored payload.")
        payload = _reconstruct_payload(report)
        if payload:
            from backend.app.services.report_service import _generate_pdf
            pdf_path = _generate_pdf(report_id, report.batch_id, payload)
            if pdf_path:
                DatabaseService.update_report(report_id, report_pdf_path=pdf_path, status="COMPLETED")

    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=503, detail="PDF not available. Please re-generate the report.")

    filename = f"ForgeX_Report_{report.batch_id}_{report_id}.pdf"
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# POST /api/v1/reports/{report_id}/regenerate-pdf
# ---------------------------------------------------------------------------
@router.post("/{report_id}/regenerate-pdf", response_model=ApiResponse)
async def regenerate_report_pdf(report_id: str):
    """
    Force regeneration of PDF from the stored canonical payload.
    Updates report status to COMPLETED upon success.
    """
    report = DatabaseService.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")

    payload = _reconstruct_payload(report)
    if not payload:
        raise HTTPException(status_code=400, detail="Cannot reconstruct report payload for PDF generation.")

    from backend.app.services.report_service import _generate_pdf
    pdf_path = _generate_pdf(report_id, report.batch_id, payload)
    if pdf_path and os.path.exists(pdf_path):
        DatabaseService.update_report(report_id, report_pdf_path=pdf_path, status="COMPLETED", error_message=None)
        return ApiResponse(
            success=True,
            message="PDF regenerated successfully.",
            data={"report_id": report_id, "status": "COMPLETED", "pdf_path": pdf_path},
        )
    else:
        return ApiResponse(
            success=False,
            message="PDF generation failed. Please check server logs.",
            data={"report_id": report_id, "status": report.status},
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_json(text: Optional[str]) -> Optional[dict]:
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def _reconstruct_payload(report) -> Optional[dict]:
    try:
        return {
            "report_id": report.report_id,
            "batch_id": report.batch_id,
            "generated_at": report.created_at.isoformat() if report.created_at else "",
            "input_summary": _safe_json(report.input_summary_json) or {},
            "vision_summary": _safe_json(report.vision_summary_json) or {},
            "process_summary": _safe_json(report.process_summary_json) or {},
            "economic_summary": _safe_json(report.economic_summary_json) or {},
            "rca_summary": _safe_json(report.rca_summary_json) or {},
            "simulation_summary": _safe_json(report.simulation_summary_json) or {},
            "material_summary": _safe_json(report.material_json) or {},
            "recommendations": _safe_json(report.recommendations_json) or [],
        }
    except Exception as e:
        logger.error(f"[Reports] Failed to reconstruct payload: {e}")
        return None


def _build_report_response(report) -> ApiResponse:
    payload = _reconstruct_payload(report)
    meta = {
        "report_id": report.report_id,
        "batch_id": report.batch_id,
        "status": report.status,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "completed_at": report.completed_at.isoformat() if report.completed_at else None,
        "has_pdf": bool(report.report_pdf_path and os.path.exists(report.report_pdf_path or "")),
        "error_message": report.error_message,
    }
    return ApiResponse(
        success=True,
        message=f"Report {report.report_id} ({report.status})",
        data={"meta": meta, "payload": payload},
    )
