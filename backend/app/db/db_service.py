"""
Database Service: Business Logic, State Persistence, and Multi-Modal Cache
"""

import json
import logging
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
)

logger = logging.getLogger("backend.db.service")


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

            # Seed default active batch if none exists
            if db.query(Batch).count() == 0:
                default_batch = Batch(
                    batch_id="BATCH-2026-001",
                    batch_name="Production Batch 2026-001",
                    active_defect="crack",
                    active_material="AISI_4140",
                    status="active",
                    total_images=142,
                    defects_count=18,
                    yield_pct=96.8,
                )
                db.add(default_batch)
                db.commit()
                logger.info("[DB] Seeded active batch BATCH-2026-001 into PostgreSQL.")

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
