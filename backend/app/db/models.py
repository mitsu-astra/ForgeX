"""
SQLAlchemy Database Models for ForgeX • Industrial Decision Intelligence
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
)
from backend.app.db.session import Base


class Batch(Base):
    __tablename__ = "batches"

    batch_id = Column(String(64), primary_key=True, index=True)
    batch_name = Column(String(128), nullable=False)
    active_defect = Column(String(32), default="crack")
    active_material = Column(String(64), default="AISI_4140")
    status = Column(String(32), default="active")
    total_images = Column(Integer, default=0)
    defects_count = Column(Integer, default=0)
    yield_pct = Column(Float, default=96.8)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(64), index=True)
    filename = Column(String(256), nullable=False)
    file_type = Column(String(32), nullable=False)  # image, csv, zip, other
    detected_subtype = Column(String(64), nullable=True)  # model_1, model_2, crack_image, etc.
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(64), index=True)
    filename = Column(String(256), nullable=False)
    defect_class = Column(String(32), nullable=False)  # crack, rust, scratch, hole, normal
    confidence = Column(Float, nullable=False)
    uncertainty_score = Column(Float, default=0.0)
    is_uncertain = Column(Boolean, default=False)
    defect_area_pct = Column(Float, default=0.0)
    bounding_boxes_json = Column(Text, nullable=True)
    inference_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProcessState(Base):
    __tablename__ = "process_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(64), index=True)
    primary_bottleneck = Column(String(64), nullable=False)
    max_utilization = Column(Float, nullable=False)
    line_efficiency_pct = Column(Float, default=71.4)
    estimated_lead_time_hrs = Column(Float, default=10.66)
    total_wip_units = Column(Float, default=141.9)
    hourly_throughput_loss_usd = Column(Float, default=906.25)
    monthly_throughput_loss_usd = Column(Float, default=652500.0)
    station_utilizations_json = Column(Text, nullable=True)
    station_queues_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RootCauseAttribution(Base):
    __tablename__ = "root_cause_attributions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(64), index=True)
    associated_defect = Column(String(32), nullable=False)  # crack, rust, scratch, hole
    root_cause = Column(String(64), nullable=False)  # hydraulic_overload_stress, storage_queue_corrosion, etc.
    confidence = Column(Float, nullable=False)
    probabilities_json = Column(Text, nullable=True)
    top_features_json = Column(Text, nullable=True)  # SHAP attributions
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, index=True)
    name = Column(String(128), nullable=False)
    alloy_grade = Column(String(64), nullable=False)
    yield_strength_mpa = Column(Float, nullable=False)
    tensile_strength_mpa = Column(Float, nullable=False)
    critical_hydraulic_pressure_bar = Column(Float, nullable=False)
    optimal_coolant_ph_min = Column(Float, nullable=False)
    optimal_coolant_ph_max = Column(Float, nullable=False)
    max_conveyor_speed_mps = Column(Float, nullable=False)
    cost_per_kg_usd = Column(Float, nullable=False)
    scrap_penalty_usd = Column(Float, nullable=False)
    governing_physics = Column(Text, nullable=True)


class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(64), index=True)
    material_code = Column(String(64), nullable=False)
    baseline_defect_pct = Column(Float, nullable=False)
    simulated_defect_pct = Column(Float, nullable=False)
    defect_reduction_pct = Column(Float, nullable=False)
    throughput_change_pct = Column(Float, nullable=False)
    monthly_savings_usd = Column(Float, nullable=False)
    recommendation_score = Column(Integer, default=90)
    risk_level = Column(String(32), default="Low")
    parameters_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemCache(Base):
    __tablename__ = "system_cache"

    cache_key = Column(String(128), primary_key=True, index=True)
    cache_value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ControlAuditRecord(Base):
    __tablename__ = "control_audit_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    parameter = Column(String(64), nullable=False)
    parameter_name = Column(String(128), nullable=False)
    old_value = Column(Float, nullable=False)
    requested_value = Column(Float, nullable=False)
    validated_value = Column(Float, nullable=False)
    applied_value = Column(Float, nullable=False)
    verified_value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=False)
    operator_id = Column(String(64), default="OP-104")
    source = Column(String(32), default="manual")  # manual, ai_recommendation, ai_accepted
    mode = Column(String(32), default="simulation")
    validation_result = Column(String(32), default="passed")  # passed, warning, blocked
    application_result = Column(String(32), default="success")  # success, failed
    verification_result = Column(String(32), default="match")  # match, discrepancy
    notes = Column(Text, nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    full_name = Column(String(128), nullable=False)
    role = Column(String(64), nullable=False)  # Admin, QA Lead, Plant Manager, Operator, Engineer
    avatar_initials = Column(String(4), default="U")
    created_at = Column(DateTime, default=datetime.utcnow)


class CopilotGuardrail(Base):
    __tablename__ = "copilot_guardrails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(128), nullable=False)
    rule_text = Column(Text, nullable=False)
    category = Column(String(64), default="Safety")  # Safety, Metallurgy, Compliance, Operational
    severity = Column(String(32), default="strict_block")  # strict_block, advisory_warning
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisReport(Base):
    """
    Persisted per-batch industrial analysis report.
    The canonical JSON payload stored here is the single source of truth
    consumed by both the frontend report view and the PDF download.
    No values are re-calculated at render time.
    """
    __tablename__ = "analysis_reports"

    report_id = Column(String(64), primary_key=True, index=True)      # UUID
    batch_id = Column(String(64), index=True, nullable=False)
    status = Column(String(32), default="PENDING")                     # PENDING | GENERATING | COMPLETED | FAILED | PARTIAL
    # Input metadata
    input_summary_json = Column(Text, nullable=True)                   # files, types, counts, columns
    # Section payloads — all sourced from existing DB tables
    vision_summary_json = Column(Text, nullable=True)                  # InspectionRecord aggregation
    process_summary_json = Column(Text, nullable=True)                 # ProcessState aggregation
    rca_summary_json = Column(Text, nullable=True)                     # RootCauseAttribution aggregation
    economic_summary_json = Column(Text, nullable=True)                # Economic metrics from ProcessState
    simulation_summary_json = Column(Text, nullable=True)              # SimulationScenario results
    recommendations_json = Column(Text, nullable=True)                 # Derived action items
    material_json = Column(Text, nullable=True)                        # Active material properties
    # PDF
    report_pdf_path = Column(String(512), nullable=True)               # Absolute path to generated PDF
    error_message = Column(Text, nullable=True)                        # If FAILED, why
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

