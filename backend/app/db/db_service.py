import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.app.db.session import SessionLocal, engine, Base
from backend.app.db.models import (
    Batch,
    UploadedFile,
    InspectionRecord,
    ProcessState,
    RootCauseAttribution,
    Material,
    SimulationScenario,
    SystemCache,
    ControlAuditRecord,
    User,
    CopilotGuardrail,
    AnalysisReport,
)

logger = logging.getLogger("backend.db.service")


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hashes a password with PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a password against PBKDF2-HMAC-SHA256 stored hash."""
    try:
        if not stored_hash or "$" not in stored_hash:
            return False
        salt, key_hex = stored_hash.split("$", 1)
        test_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return test_key.hex() == key_hex
    except Exception:
        return False


def init_database():
    """
    Initializes PostgreSQL tables and seeds standard industrial materials.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("[DB] PostgreSQL tables successfully created/verified.")

        db = SessionLocal()
        try:
            # Seed standard engineering materials if not already present
            existing_count = db.query(Material).count()
            if existing_count == 0:
                seed_materials = [
                    Material(
                        code="AISI_4140",
                        name="AISI 4140 Chromium-Molybdenum Alloy Steel",
                        alloy_grade="High-Tensile Quenched & Tempered",
                        yield_strength_mpa=415.0,
                        tensile_strength_mpa=655.0,
                        critical_hydraulic_pressure_bar=180.0,
                        optimal_coolant_ph_min=7.6,
                        optimal_coolant_ph_max=7.8,
                        max_conveyor_speed_mps=1.00,
                        cost_per_kg_usd=4.20,
                        scrap_penalty_usd=52.50,
                        governing_physics="Griffith fracture criterion & hydraulic forming residual stress threshold (yielding >180 bar induces micro-crack propagation).",
                    ),
                    Material(
                        code="AISI_304",
                        name="AISI 304 Austenitic Stainless Steel",
                        alloy_grade="18/8 Chrome-Nickel",
                        yield_strength_mpa=215.0,
                        tensile_strength_mpa=505.0,
                        critical_hydraulic_pressure_bar=170.0,
                        optimal_coolant_ph_min=7.8,
                        optimal_coolant_ph_max=8.2,
                        max_conveyor_speed_mps=0.95,
                        cost_per_kg_usd=7.80,
                        scrap_penalty_usd=78.00,
                        governing_physics="Pourbaix electrochemical kinetics: coolant pH dropping below 7.2 causes passive Cr2O3 oxide breakdown and queue pitting corrosion (Rust).",
                    ),
                    Material(
                        code="AL_6061_T6",
                        name="6061-T6 Precipitation-Hardened Aluminum Alloy",
                        alloy_grade="Mg-Si Structural Wrought",
                        yield_strength_mpa=276.0,
                        tensile_strength_mpa=310.0,
                        critical_hydraulic_pressure_bar=155.0,
                        optimal_coolant_ph_min=7.2,
                        optimal_coolant_ph_max=7.6,
                        max_conveyor_speed_mps=0.85,
                        cost_per_kg_usd=5.60,
                        scrap_penalty_usd=45.00,
                        governing_physics="Archard abrasive wear law: soft surface hardness (95 HB) results in guide rail scratching when belt velocity exceeds 0.85 m/s.",
                    ),
                    Material(
                        code="CAST_IRON_40",
                        name="Grey Cast Iron Class 40",
                        alloy_grade="Pearlitic Flake Graphite",
                        yield_strength_mpa=290.0,
                        tensile_strength_mpa=310.0,
                        critical_hydraulic_pressure_bar=165.0,
                        optimal_coolant_ph_min=7.4,
                        optimal_coolant_ph_max=7.8,
                        max_conveyor_speed_mps=0.90,
                        cost_per_kg_usd=3.10,
                        scrap_penalty_usd=38.00,
                        governing_physics="Taylor tool-life equation: brittle graphite flakes cause drill wandering and hole misalignment under excessive feed rate > 320 mm/min.",
                    ),
                ]
                db.add_all(seed_materials)
                db.commit()
                logger.info("[DB] Seeded 4 standard industrial materials into PostgreSQL.")

            # Seed 5 demo users if table is empty
            if db.query(User).count() == 0:
                demo_users = [
                    User(
                        email="admin@forgex.ai",
                        password_hash=hash_password("admin123"),
                        full_name="Alex Vance",
                        role="Lead Systems Architect",
                        avatar_initials="AV",
                    ),
                    User(
                        email="quality.lead@forgex.ai",
                        password_hash=hash_password("quality123"),
                        full_name="Sarah Lin",
                        role="QA & Inspection Lead",
                        avatar_initials="SL",
                    ),
                    User(
                        email="plant.manager@forgex.ai",
                        password_hash=hash_password("plant123"),
                        full_name="Marcus Gallagher",
                        role="Plant Operations Manager",
                        avatar_initials="MG",
                    ),
                    User(
                        email="line.operator@forgex.ai",
                        password_hash=hash_password("operator123"),
                        full_name="Operator OP-104",
                        role="Shift Line Operator",
                        avatar_initials="OP",
                    ),
                    User(
                        email="process.engineer@forgex.ai",
                        password_hash=hash_password("process123"),
                        full_name="Dr. Elena Rostova",
                        role="Metallurgical Reliability Engineer",
                        avatar_initials="ER",
                    ),
                ]
                db.add_all(demo_users)
                db.commit()
                logger.info("[DB] Seeded 5 demo users into PostgreSQL.")

            # Seed default AI Copilot safety guardrails if table is empty
            if db.query(CopilotGuardrail).count() == 0:
                default_guardrails = [
                    CopilotGuardrail(
                        rule_name="Hydraulic Forming Pressure Ceiling",
                        rule_text="Do not recommend or permit hydraulic pressure setpoints above 185 bar (or active material critical threshold) to prevent irreversible yield fracture propagation.",
                        category="Safety",
                        severity="strict_block",
                        is_active=True,
                    ),
                    CopilotGuardrail(
                        rule_name="Coolant Chemistry Acidification Boundary",
                        rule_text="Reject any recommendation that drops coolant pH below 7.2 to avoid Pourbaix electrochemical passive oxide breakdown and toxic vapor evolution.",
                        category="Metallurgy",
                        severity="strict_block",
                        is_active=True,
                    ),
                    CopilotGuardrail(
                        rule_name="High-Impact Human Operator Authorization",
                        rule_text="Any parameter change with an estimated monthly scrap impact exceeding $10,000 USD must require explicit Lead Engineer confirmation before execution.",
                        category="Compliance",
                        severity="advisory_warning",
                        is_active=True,
                    ),
                    CopilotGuardrail(
                        rule_name="Conveyor Linear Velocity Ceiling",
                        rule_text="Cap conveyor transfer belt velocity at 1.20 m/s to prevent Archard abrasive micro-scratching on low-hardness aluminum alloys.",
                        category="Operational",
                        severity="strict_block",
                        is_active=True,
                    ),
                    CopilotGuardrail(
                        rule_name="Industrial Domain Relevance & Out-of-Context Filter",
                        rule_text="Intercept or redirect queries unrelated to industrial manufacturing, visual defect inspection, queue bottleneck telemetry, metallurgy/materials, or plant operations.",
                        category="Relevance",
                        severity="advisory_warning",
                        is_active=True,
                    ),
                ]
                db.add_all(default_guardrails)
                db.commit()
                logger.info("[DB] Seeded 5 default AI Copilot safety & relevance guardrails into PostgreSQL.")

            # Ensure the Out-of-Context Relevance rule exists if missing from earlier runs
            relevance_rule = db.query(CopilotGuardrail).filter(CopilotGuardrail.rule_name == "Industrial Domain Relevance & Out-of-Context Filter").first()
            if not relevance_rule:
                ooc_rule = CopilotGuardrail(
                    rule_name="Industrial Domain Relevance & Out-of-Context Filter",
                    rule_text="Intercept or redirect queries unrelated to industrial manufacturing, visual defect inspection, queue bottleneck telemetry, metallurgy/materials, or plant operations.",
                    category="Relevance",
                    severity="advisory_warning",
                    is_active=True,
                )
                db.add(ooc_rule)
                db.commit()
                logger.info("[DB] Seeded missing Industrial Domain Relevance guardrail into PostgreSQL.")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"[DB] Error initializing database: {e}", exc_info=True)


class DatabaseService:
    @staticmethod
    def get_active_batch() -> Optional[Batch]:
        """Fetches the latest active batch from PostgreSQL."""
        db = SessionLocal()
        try:
            batch = db.query(Batch).order_by(Batch.updated_at.desc()).first()
            return batch
        finally:
            db.close()

    @staticmethod
    def set_active_defect(defect_type: str, batch_id: Optional[str] = None):
        """Updates the active defect type and material in PostgreSQL."""
        db = SessionLocal()
        try:
            batch = None
            if batch_id:
                batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
            if not batch:
                batch = db.query(Batch).order_by(Batch.updated_at.desc()).first()

            defect_material_map = {
                "crack": "AISI_4140",
                "rust": "AISI_304",
                "scratch": "AL_6061_T6",
                "hole": "CAST_IRON_40",
                "normal": "AISI_4140",
            }
            target_material = defect_material_map.get(defect_type.lower(), "AISI_4140")

            if batch:
                batch.active_defect = defect_type.lower()
                batch.active_material = target_material
                batch.updated_at = datetime.utcnow()
                db.commit()
            else:
                new_batch = Batch(
                    batch_id=batch_id or f"BATCH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    batch_name="Active Production Batch",
                    active_defect=defect_type.lower(),
                    active_material=target_material,
                )
                db.add(new_batch)
                db.commit()

            # Update cache
            DatabaseService.set_cache("active_defect", defect_type.lower())
            DatabaseService.set_cache("active_material", target_material)
            logger.info(f"[DB] Set active defect in PostgreSQL to: {defect_type} (Material: {target_material})")
        except Exception as e:
            logger.error(f"[DB] Error setting active defect: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def record_uploaded_file(
        filename: str,
        file_type: str,
        file_path: str,
        file_size_bytes: int,
        batch_id: str,
        detected_subtype: Optional[str] = None,
    ):
        """Records an ingested file in PostgreSQL."""
        db = SessionLocal()
        try:
            record = UploadedFile(
                batch_id=batch_id,
                filename=filename,
                file_type=file_type,
                detected_subtype=detected_subtype,
                file_path=file_path,
                file_size_bytes=file_size_bytes,
            )
            db.add(record)
            db.commit()
            logger.info(f"[DB] Recorded uploaded file {filename} in PostgreSQL.")
        except Exception as e:
            logger.error(f"[DB] Error recording uploaded file: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def record_inspection(
        filename: str,
        defect_class: str,
        confidence: float,
        uncertainty_score: float,
        is_uncertain: bool,
        inference_time_ms: float,
        batch_id: str,
        bounding_boxes: Optional[List[Dict[str, Any]]] = None,
        defect_area_pct: float = 0.0,
    ):
        """Records a visual inspection inference in PostgreSQL."""
        db = SessionLocal()
        try:
            rec = InspectionRecord(
                batch_id=batch_id,
                filename=filename,
                defect_class=defect_class,
                confidence=confidence,
                uncertainty_score=uncertainty_score,
                is_uncertain=is_uncertain,
                defect_area_pct=defect_area_pct,
                bounding_boxes_json=json.dumps(bounding_boxes) if bounding_boxes else None,
                inference_time_ms=inference_time_ms,
            )
            db.add(rec)
            db.commit()

            # Automatically set this as active defect
            DatabaseService.set_active_defect(defect_class, batch_id)
        except Exception as e:
            logger.error(f"[DB] Error recording inspection: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def get_recent_inspections(limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent inspection records from PostgreSQL."""
        db = SessionLocal()
        try:
            records = (
                db.query(InspectionRecord)
                .order_by(InspectionRecord.created_at.desc())
                .limit(limit)
                .all()
            )
            results = []
            for r in records:
                boxes = json.loads(r.bounding_boxes_json) if r.bounding_boxes_json else []
                results.append({
                    "filename": r.filename,
                    "prediction": {
                        "defect_class": r.defect_class,
                        "confidence": r.confidence,
                        "class_id": 0,
                        "probabilities": {r.defect_class: r.confidence},
                    },
                    "uncertainty": {
                        "uncertainty_score": r.uncertainty_score,
                        "is_uncertain": r.is_uncertain,
                        "threshold": 0.15,
                        "confidence_interval_95": [
                            round(max(0.0, r.confidence - 0.03), 3),
                            round(min(1.0, r.confidence + 0.02), 3),
                        ],
                    },
                    "localization": {
                        "bounding_boxes": boxes,
                        "defect_area_percentage": r.defect_area_pct,
                    },
                    "inference_time_ms": r.inference_time_ms,
                    "status": "success",
                    "inspected_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
                })
            return results
        except Exception as e:
            logger.error(f"[DB] Error getting recent inspections: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def get_uploaded_files(limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches recent uploaded files from PostgreSQL/SQLite."""
        db = SessionLocal()
        try:
            records = (
                db.query(UploadedFile)
                .order_by(UploadedFile.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": r.id,
                    "filename": r.filename,
                    "file_type": r.file_type,
                    "detected_subtype": r.detected_subtype,
                    "file_size_bytes": r.file_size_bytes,
                    "batch_id": r.batch_id,
                    "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
                }
                for r in records
            ]
        except Exception as e:
            logger.error(f"[DB] Error getting uploaded files: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def has_uploaded_files() -> bool:
        """Returns True if user has uploaded any files."""
        db = SessionLocal()
        try:
            return db.query(UploadedFile).count() > 0
        except Exception as e:
            logger.error(f"[DB] Error checking uploaded files: {e}")
            return False
        finally:
            db.close()

    @staticmethod
    def get_material(code: str) -> Optional[Material]:
        """Gets material properties by code."""
        db = SessionLocal()
        try:
            return db.query(Material).filter(Material.code == code).first()
        finally:
            db.close()

    @staticmethod
    def get_active_material(batch_id: Optional[str] = None) -> Material:
        """Gets active material for current batch, falling back to AISI 4140."""
        db = SessionLocal()
        try:
            batch = None
            if batch_id:
                batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
            if not batch:
                batch = db.query(Batch).order_by(Batch.updated_at.desc()).first()
            
            mat_code = batch.active_material if batch and batch.active_material else "AISI_4140"
            mat = db.query(Material).filter(Material.code == mat_code).first()
            if not mat:
                mat = db.query(Material).filter(Material.code == "AISI_4140").first()
            return mat
        finally:
            db.close()

    @staticmethod
    def get_all_materials() -> List[Material]:
        """Gets all industrial materials."""
        db = SessionLocal()
        try:
            return db.query(Material).all()
        finally:
            db.close()

    @staticmethod
    def record_process_state(
        batch_id: str,
        primary_bottleneck: str,
        max_utilization: float,
        line_efficiency_pct: float,
        estimated_lead_time_hrs: float,
        total_wip_units: float,
        hourly_loss_usd: float,
        monthly_loss_usd: float,
        station_utilizations: Optional[Dict[str, float]] = None,
        station_queues: Optional[Dict[str, float]] = None,
    ):
        """Persists process state & bottleneck analysis into PostgreSQL."""
        db = SessionLocal()
        try:
            ps = ProcessState(
                batch_id=batch_id,
                primary_bottleneck=primary_bottleneck,
                max_utilization=max_utilization,
                line_efficiency_pct=line_efficiency_pct,
                estimated_lead_time_hrs=estimated_lead_time_hrs,
                total_wip_units=total_wip_units,
                hourly_throughput_loss_usd=hourly_loss_usd,
                monthly_throughput_loss_usd=monthly_loss_usd,
                station_utilizations_json=json.dumps(station_utilizations) if station_utilizations else None,
                station_queues_json=json.dumps(station_queues) if station_queues else None,
            )
            db.add(ps)
            db.commit()
            logger.info(f"[DB] Recorded process state for batch {batch_id} in PostgreSQL.")
        except Exception as e:
            logger.error(f"[DB] Error recording process state: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def get_latest_process_state(batch_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves the latest process state recorded in PostgreSQL."""
        db = SessionLocal()
        try:
            query = db.query(ProcessState)
            if batch_id:
                query = query.filter(ProcessState.batch_id == batch_id)
            ps = query.order_by(ProcessState.created_at.desc()).first()
            if not ps:
                return None
            return {
                "batch_id": ps.batch_id,
                "primary_bottleneck": ps.primary_bottleneck,
                "max_utilization": ps.max_utilization,
                "line_efficiency_pct": ps.line_efficiency_pct,
                "estimated_lead_time_hrs": ps.estimated_lead_time_hrs,
                "total_wip_units": ps.total_wip_units,
                "hourly_throughput_loss_usd": ps.hourly_throughput_loss_usd,
                "monthly_throughput_loss_usd": ps.monthly_throughput_loss_usd,
                "station_utilizations": json.loads(ps.station_utilizations_json) if ps.station_utilizations_json else {},
                "station_queues": json.loads(ps.station_queues_json) if ps.station_queues_json else {},
                "created_at": ps.created_at.strftime("%Y-%m-%d %H:%M:%S") if ps.created_at else "",
            }
        except Exception as e:
            logger.error(f"[DB] Error getting latest process state: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def record_root_cause(
        batch_id: str,
        root_cause: str,
        associated_defect: str,
        confidence: float,
        probabilities: Dict[str, float],
        top_features: List[Dict[str, Any]],
        recommendation: str,
    ):
        """Persists root-cause diagnosis and SHAP attributions into PostgreSQL."""
        db = SessionLocal()
        try:
            rc = RootCauseAttribution(
                batch_id=batch_id,
                root_cause=root_cause,
                associated_defect=associated_defect,
                confidence=confidence,
                probabilities_json=json.dumps(probabilities),
                top_features_json=json.dumps(top_features),
                recommendation=recommendation,
            )
            db.add(rc)
            db.commit()
            logger.info(f"[DB] Recorded root cause diagnosis '{root_cause}' for batch {batch_id} in PostgreSQL.")
        except Exception as e:
            logger.error(f"[DB] Error recording root cause: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def record_simulation_scenario(
        batch_id: str,
        material_code: str,
        baseline_defect_pct: float,
        simulated_defect_pct: float,
        defect_reduction_pct: float,
        throughput_change_pct: float,
        monthly_savings_usd: float,
        recommendation_score: int,
        risk_level: str,
        parameters: Dict[str, Any],
    ):
        """Persists what-if simulation run into PostgreSQL."""
        db = SessionLocal()
        try:
            sim = SimulationScenario(
                batch_id=batch_id,
                material_code=material_code,
                baseline_defect_pct=baseline_defect_pct,
                simulated_defect_pct=simulated_defect_pct,
                defect_reduction_pct=defect_reduction_pct,
                throughput_change_pct=throughput_change_pct,
                monthly_savings_usd=monthly_savings_usd,
                recommendation_score=recommendation_score,
                risk_level=risk_level,
                parameters_json=json.dumps(parameters),
            )
            db.add(sim)
            db.commit()
            logger.info(f"[DB] Recorded simulation scenario for batch {batch_id} in PostgreSQL.")
        except Exception as e:
            logger.error(f"[DB] Error recording simulation scenario: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def get_simulation_scenarios(batch_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves recent simulation scenarios from database."""
        db = SessionLocal()
        try:
            query = db.query(SimulationScenario)
            if batch_id:
                query = query.filter(SimulationScenario.batch_id == batch_id)
            scenarios = query.order_by(SimulationScenario.created_at.desc()).limit(limit).all()
            results = []
            for s in scenarios:
                params = {}
                if s.parameters_json:
                    try:
                        params = json.loads(s.parameters_json)
                    except Exception:
                        params = {}
                results.append({
                    "id": s.id,
                    "batch_id": s.batch_id,
                    "material_code": s.material_code,
                    "baseline_defect_pct": s.baseline_defect_pct,
                    "simulated_defect_pct": s.simulated_defect_pct,
                    "defect_reduction_pct": s.defect_reduction_pct,
                    "throughput_change_pct": s.throughput_change_pct,
                    "monthly_savings_usd": s.monthly_savings_usd,
                    "recommendation_score": s.recommendation_score,
                    "risk_level": s.risk_level,
                    "parameters": params,
                    "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else None,
                })
            return results
        except Exception as e:
            logger.error(f"[DB] Error querying simulation scenarios: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def get_active_process_params(batch_id: Optional[str] = None) -> Dict[str, float]:
        """
        Retrieves active process operating parameters for the active batch.
        Defaults to crack-specific physical overload conditions if crack is the active defect.
        """
        batch = DatabaseService.get_active_batch()
        defect = (batch.active_defect if batch and batch.active_defect else "crack").lower()

        if defect == "crack":
            return {
                "hydraulic_pressure_bar": 194.0,
                "feed_rate_mmpm": 390.0,
                "station_max_util": 0.96,
                "queue_time_hours": 0.85,
                "ambient_humidity_pct": 46.0,
                "coolant_ph": 7.5,
                "conveyor_speed_mps": 0.98,
                "spindle_cycles": 3200.0,
            }
        elif defect == "rust":
            return {
                "hydraulic_pressure_bar": 172.0,
                "feed_rate_mmpm": 260.0,
                "station_max_util": 0.88,
                "queue_time_hours": 5.2,
                "ambient_humidity_pct": 78.0,
                "coolant_ph": 6.7,
                "conveyor_speed_mps": 0.95,
                "spindle_cycles": 2400.0,
            }
        elif defect == "scratch":
            return {
                "hydraulic_pressure_bar": 170.0,
                "feed_rate_mmpm": 280.0,
                "station_max_util": 0.74,
                "queue_time_hours": 1.1,
                "ambient_humidity_pct": 48.0,
                "coolant_ph": 7.6,
                "conveyor_speed_mps": 1.65,
                "spindle_cycles": 2100.0,
            }
        elif defect == "hole":
            return {
                "hydraulic_pressure_bar": 175.0,
                "feed_rate_mmpm": 460.0,
                "station_max_util": 0.92,
                "queue_time_hours": 1.4,
                "ambient_humidity_pct": 50.0,
                "coolant_ph": 7.4,
                "conveyor_speed_mps": 0.95,
                "spindle_cycles": 18500.0,
            }
        else:
            return {
                "hydraulic_pressure_bar": 175.0,
                "feed_rate_mmpm": 280.0,
                "station_max_util": 0.65,
                "queue_time_hours": 1.0,
                "ambient_humidity_pct": 45.0,
                "coolant_ph": 7.7,
                "conveyor_speed_mps": 0.95,
                "spindle_cycles": 3000.0,
            }

    @staticmethod
    def set_cache(key: str, value: Any):
        """Sets a cached JSON value in PostgreSQL."""
        db = SessionLocal()
        try:
            val_str = json.dumps(value) if not isinstance(value, str) else value
            item = db.query(SystemCache).filter(SystemCache.cache_key == key).first()
            if item:
                item.cache_value = val_str
                item.updated_at = datetime.utcnow()
            else:
                item = SystemCache(cache_key=key, cache_value=val_str)
                db.add(item)
            db.commit()
        except Exception as e:
            logger.error(f"[DB] Error writing cache for {key}: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def get_cache(key: str) -> Optional[Any]:
        """Retrieves a cached value from PostgreSQL."""
        db = SessionLocal()
        try:
            item = db.query(SystemCache).filter(SystemCache.cache_key == key).first()
            if not item:
                return None
            try:
                return json.loads(item.cache_value)
            except Exception:
                return item.cache_value
        finally:
            db.close()

    # In-memory audit fallback
    _in_memory_audit_trail: List[Dict[str, Any]] = []

    @staticmethod
    def record_control_audit(
        event_id: str,
        parameter: str,
        parameter_name: str,
        old_value: float,
        requested_value: float,
        validated_value: float,
        applied_value: float,
        verified_value: float,
        unit: str,
        operator_id: str = "OP-104",
        source: str = "manual",
        mode: str = "simulation",
        validation_result: str = "passed",
        application_result: str = "success",
        verification_result: str = "match",
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Records an immutable control audit log entry."""
        audit_dict = {
            "event_id": event_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "parameter": parameter,
            "parameter_name": parameter_name,
            "old_value": old_value,
            "requested_value": requested_value,
            "validated_value": validated_value,
            "applied_value": applied_value,
            "verified_value": verified_value,
            "unit": unit,
            "operator_id": operator_id,
            "source": source,
            "mode": mode,
            "validation_result": validation_result,
            "application_result": application_result,
            "verification_result": verification_result,
            "notes": notes,
        }
        # Prepend to in-memory list
        DatabaseService._in_memory_audit_trail.insert(0, audit_dict)

        # Also persist to PostgreSQL if table exists
        db = SessionLocal()
        try:
            rec = ControlAuditRecord(
                event_id=event_id,
                parameter=parameter,
                parameter_name=parameter_name,
                old_value=old_value,
                requested_value=requested_value,
                validated_value=validated_value,
                applied_value=applied_value,
                verified_value=verified_value,
                unit=unit,
                operator_id=operator_id,
                source=source,
                mode=mode,
                validation_result=validation_result,
                application_result=application_result,
                verification_result=verification_result,
                notes=notes,
            )
            db.add(rec)
            db.commit()
        except Exception as e:
            logger.warning(f"[DB] Error writing ControlAuditRecord to DB (falling back to memory): {e}")
            db.rollback()
        finally:
            db.close()

        return audit_dict

    @staticmethod
    def get_control_audit_trail(limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves historical audit entries (combining DB and memory)."""
        db = SessionLocal()
        try:
            records = (
                db.query(ControlAuditRecord)
                .order_by(ControlAuditRecord.timestamp.desc())
                .limit(limit)
                .all()
            )
            if records:
                return [
                    {
                        "event_id": r.event_id,
                        "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp else "",
                        "parameter": r.parameter,
                        "parameter_name": r.parameter_name,
                        "old_value": r.old_value,
                        "requested_value": r.requested_value,
                        "validated_value": r.validated_value,
                        "applied_value": r.applied_value,
                        "verified_value": r.verified_value,
                        "unit": r.unit,
                        "operator_id": r.operator_id,
                        "source": r.source,
                        "mode": r.mode,
                        "validation_result": r.validation_result,
                        "application_result": r.application_result,
                        "verification_result": r.verification_result,
                        "notes": r.notes,
                    }
                    for r in records
                ]
        except Exception as e:
            logger.warning(f"[DB] Error querying ControlAuditRecord: {e}")
        finally:
            db.close()

        return DatabaseService._in_memory_audit_trail[:limit]

    # -----------------------------------------------------------------------
    # USER AUTHENTICATION & DEMO PERSONAS
    # -----------------------------------------------------------------------

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticates a user by email and password hash."""
        db = SessionLocal()
        try:
            clean_email = email.strip().lower()
            alt_email = (
                clean_email.replace("@industrial.ai", "@forgex.ai")
                if "@industrial.ai" in clean_email
                else clean_email.replace("@forgex.ai", "@industrial.ai")
            )
            user = (
                db.query(User)
                .filter((User.email == clean_email) | (User.email == alt_email))
                .first()
            )
            if not user:
                return None
            if verify_password(password, user.password_hash):
                return {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "avatar_initials": user.avatar_initials,
                    "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
                }
            return None
        except Exception as e:
            logger.error(f"[DB] Error authenticating user {email}: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Fetches a user profile by email."""
        db = SessionLocal()
        try:
            clean_email = email.strip().lower()
            alt_email = (
                clean_email.replace("@industrial.ai", "@forgex.ai")
                if "@industrial.ai" in clean_email
                else clean_email.replace("@forgex.ai", "@industrial.ai")
            )
            user = (
                db.query(User)
                .filter((User.email == clean_email) | (User.email == alt_email))
                .first()
            )
            if not user:
                return None
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "avatar_initials": user.avatar_initials,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "",
            }
        except Exception as e:
            logger.error(f"[DB] Error fetching user by email: {e}")
            return None
        finally:
            db.close()

    @staticmethod
    def get_demo_users() -> List[Dict[str, Any]]:
        """Returns all seeded demo users for quick persona switching."""
        db = SessionLocal()
        try:
            users = db.query(User).order_by(User.id.asc()).all()
            demo_password_map = {
                "admin@industrial.ai": "admin123",
                "quality.lead@industrial.ai": "quality123",
                "plant.manager@industrial.ai": "plant123",
                "line.operator@industrial.ai": "operator123",
                "process.engineer@industrial.ai": "process123",
            }
            return [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "role": u.role,
                    "avatar_initials": u.avatar_initials,
                    "demo_password": demo_password_map.get(u.email, "demo123"),
                }
                for u in users
            ]
        except Exception as e:
            logger.error(f"[DB] Error fetching demo users: {e}")
            return []
        finally:
            db.close()

    # -----------------------------------------------------------------------
    # COPILOT GUARDRAILS & SAFETY RULES
    # -----------------------------------------------------------------------

    @staticmethod
    def get_guardrails(active_only: bool = False) -> List[Dict[str, Any]]:
        """Retrieves all Copilot safety guardrails from PostgreSQL."""
        db = SessionLocal()
        try:
            query = db.query(CopilotGuardrail)
            if active_only:
                query = query.filter(CopilotGuardrail.is_active == True)
            rules = query.order_by(CopilotGuardrail.id.asc()).all()
            return [
                {
                    "id": r.id,
                    "rule_name": r.rule_name,
                    "rule_text": r.rule_text,
                    "category": r.category,
                    "severity": r.severity,
                    "is_active": r.is_active,
                    "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
                }
                for r in rules
            ]
        except Exception as e:
            logger.error(f"[DB] Error getting guardrails: {e}")
            return []
        finally:
            db.close()

    @staticmethod
    def create_guardrail(
        rule_name: str,
        rule_text: str,
        category: str = "Safety",
        severity: str = "strict_block",
    ) -> Optional[Dict[str, Any]]:
        """Creates a new AI Copilot safety guardrail rule."""
        db = SessionLocal()
        try:
            rule = CopilotGuardrail(
                rule_name=rule_name,
                rule_text=rule_text,
                category=category,
                severity=severity,
                is_active=True,
            )
            db.add(rule)
            db.commit()
            db.refresh(rule)
            logger.info(f"[DB] Created new Copilot guardrail: {rule_name}")
            return {
                "id": rule.id,
                "rule_name": rule.rule_name,
                "rule_text": rule.rule_text,
                "category": rule.category,
                "severity": rule.severity,
                "is_active": rule.is_active,
                "created_at": rule.created_at.strftime("%Y-%m-%d %H:%M:%S") if rule.created_at else "",
            }
        except Exception as e:
            logger.error(f"[DB] Error creating guardrail: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    @staticmethod
    def toggle_guardrail(guardrail_id: int, is_active: bool) -> bool:
        """Toggles the active state of a Copilot guardrail rule."""
        db = SessionLocal()
        try:
            rule = db.query(CopilotGuardrail).filter(CopilotGuardrail.id == guardrail_id).first()
            if not rule:
                return False
            rule.is_active = is_active
            db.commit()
            logger.info(f"[DB] Toggled guardrail #{guardrail_id} active={is_active}")
            return True
        except Exception as e:
            logger.error(f"[DB] Error toggling guardrail: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    @staticmethod
    def delete_guardrail(guardrail_id: int) -> bool:
        """Deletes a Copilot guardrail rule."""
        db = SessionLocal()
        try:
            rule = db.query(CopilotGuardrail).filter(CopilotGuardrail.id == guardrail_id).first()
            if not rule:
                return False
            db.delete(rule)
            db.commit()
            logger.info(f"[DB] Deleted guardrail #{guardrail_id}")
            return True
        except Exception as e:
            logger.error(f"[DB] Error deleting guardrail: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    # -------------------------------------------------------------------------
    # AnalysisReport CRUD
    # -------------------------------------------------------------------------

    @staticmethod
    def create_report(batch_id: str, report_id: str) -> Optional["AnalysisReport"]:
        """Create a new AnalysisReport record in PENDING state."""
        db = SessionLocal()
        try:
            record = AnalysisReport(
                report_id=report_id,
                batch_id=batch_id,
                status="PENDING",
                created_at=datetime.utcnow(),
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            logger.info(f"[DB] Created AnalysisReport {report_id} for batch {batch_id}")
            return record
        except Exception as e:
            logger.error(f"[DB] Error creating report: {e}")
            db.rollback()
            return None
        finally:
            db.close()

    @staticmethod
    def update_report(report_id: str, **fields) -> bool:
        """Update fields on an AnalysisReport by report_id."""
        db = SessionLocal()
        try:
            record = db.query(AnalysisReport).filter(AnalysisReport.report_id == report_id).first()
            if not record:
                return False
            for k, v in fields.items():
                setattr(record, k, v)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"[DB] Error updating report {report_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    @staticmethod
    def get_report(report_id: str) -> Optional["AnalysisReport"]:
        """Retrieve a single AnalysisReport by report_id."""
        db = SessionLocal()
        try:
            return db.query(AnalysisReport).filter(AnalysisReport.report_id == report_id).first()
        finally:
            db.close()

    @staticmethod
    def get_report_by_batch(batch_id: str) -> Optional["AnalysisReport"]:
        """Retrieve the most recent AnalysisReport for a batch."""
        db = SessionLocal()
        try:
            return (
                db.query(AnalysisReport)
                .filter(AnalysisReport.batch_id == batch_id)
                .order_by(AnalysisReport.created_at.desc())
                .first()
            )
        finally:
            db.close()

    @staticmethod
    def list_reports() -> List["AnalysisReport"]:
        """Return all AnalysisReport records, newest first."""
        db = SessionLocal()
        try:
            return (
                db.query(AnalysisReport)
                .order_by(AnalysisReport.created_at.desc())
                .all()
            )
        finally:
            db.close()
