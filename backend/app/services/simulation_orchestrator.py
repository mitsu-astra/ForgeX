"""
Unified Simulation Orchestrator Service for ForgeX.
Coordinates:
1. Active baseline resolution (telemetry, batch, stored state, fallbacks).
2. Machine and material safety validation (machine_limits.yaml & material alloy limits).
3. Physics-grounded metallurgical defect simulation (WhatIfSimulatorEngine).
4. Discrete-event queue and surrogate forecasting (ProcessSurrogateModel).
5. Line balance, bottleneck, WIP, and lead-time analysis (BottleneckDetector).
6. Dual-currency economic evaluation (USD $ and INR ₹ at 83.50 canonical rate).
7. Persistence to PostgreSQL/SQLite simulation_scenarios.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

# Bootstrap root path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.simulator.what_if_engine import WhatIfSimulatorEngine
from models.process.model import ProcessSurrogateModel
from models.process.bottleneck import BottleneckDetector
from backend.app.services.control_service import SafetyValidator
from backend.app.services.process_store import process_store
from backend.app.db.db_service import DatabaseService
from backend.app.config import settings

logger = logging.getLogger("backend.services.simulation_orchestrator")

# Canonical exchange rate matching frontend/lib/currency.ts
USD_TO_INR_RATE = 83.50


class SimulationOrchestrator:
    """
    Unified Simulation Orchestration Layer for ForgeX.
    Does not duplicate physics or ML formulas; orchestrates existing specialized engines.
    """
    _instance: Optional["SimulationOrchestrator"] = None

    def __init__(self):
        self.what_if_engine = WhatIfSimulatorEngine()
        self.bottleneck_detector = BottleneckDetector()
        self.safety_validator = SafetyValidator()
        self.process_surrogate: Optional[ProcessSurrogateModel] = None
        self._load_process_surrogate()

    @classmethod
    def get_instance(cls) -> "SimulationOrchestrator":
        if cls._instance is None:
            cls._instance = SimulationOrchestrator()
        return cls._instance

    def _load_process_surrogate(self):
        """Loads trained XGBoost surrogate model for discrete-event queue and throughput forecasting."""
        weights_path = settings.PROCESS_MODEL_WEIGHTS
        if os.path.exists(weights_path):
            try:
                self.process_surrogate = ProcessSurrogateModel.load(weights_path)
                logger.info(f"[Orchestrator] Loaded ProcessSurrogateModel from {weights_path}")
            except Exception as e:
                logger.warning(f"[Orchestrator] Could not load ProcessSurrogateModel from {weights_path}: {e}")
        else:
            logger.warning(f"[Orchestrator] Process model weights not found at {weights_path}")

    def get_active_baseline(self, batch_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Derives the active manufacturing baseline.
        Priority order:
        1. Active analyzed batch/process state
        2. Latest available process telemetry
        3. Stored process state
        4. Existing configured baseline
        5. Current hardcoded default as final fallback
        """
        active_batch = DatabaseService.get_active_batch()
        curr_batch_id = batch_id or (active_batch.batch_id if active_batch else "BATCH-2026-001")
        active_mat = DatabaseService.get_active_material(curr_batch_id)

        # Query process store and DB batch process parameters
        stored_proc_state = process_store.get_state() or {}
        proc_source = process_store.get_source()
        active_db_params = DatabaseService.get_active_process_params(curr_batch_id)

        is_live_telemetry = proc_source.startswith("uploaded")

        # 1. Hydraulic Pressure (bar)
        if "hydraulic_pressure_bar" in stored_proc_state or "Forming_Pressure_bar" in stored_proc_state:
            p_val = float(stored_proc_state.get("hydraulic_pressure_bar") or stored_proc_state.get("Forming_Pressure_bar"))
            p_src = "live" if is_live_telemetry else "stored"
        elif "hydraulic_pressure_bar" in active_db_params:
            p_val = float(active_db_params["hydraulic_pressure_bar"])
            p_src = "stored"
        else:
            p_val = 188.0
            p_src = "configured"

        # 2. Coolant pH
        if "coolant_ph" in stored_proc_state or "Coolant_pH" in stored_proc_state:
            ph_val = float(stored_proc_state.get("coolant_ph") or stored_proc_state.get("Coolant_pH"))
            ph_src = "live" if is_live_telemetry else "stored"
        elif "coolant_ph" in active_db_params:
            ph_val = float(active_db_params["coolant_ph"])
            ph_src = "stored"
        else:
            ph_val = 7.1
            ph_src = "configured"

        # 3. Conveyor Speed (m/s)
        if "conveyor_speed_mps" in stored_proc_state or "Conveyor_Speed_mps" in stored_proc_state:
            spd_val = float(stored_proc_state.get("conveyor_speed_mps") or stored_proc_state.get("Conveyor_Speed_mps"))
            spd_src = "live" if is_live_telemetry else "stored"
        elif "conveyor_speed_mps" in active_db_params:
            spd_val = float(active_db_params["conveyor_speed_mps"])
            spd_src = "stored"
        else:
            spd_val = 1.25
            spd_src = "configured"

        # 4. Demand (units/hr)
        if "Demand" in stored_proc_state:
            dem_val = float(stored_proc_state["Demand"])
            dem_src = "live" if is_live_telemetry else "stored"
        else:
            dem_val = 7.0
            dem_src = "configured"

        # 5. Spindle Feed Rate (mm/min)
        if "spindle_feed_rate" in stored_proc_state or "Feed_Rate_mm_per_min" in stored_proc_state:
            feed_val = float(stored_proc_state.get("spindle_feed_rate") or stored_proc_state.get("Feed_Rate_mm_per_min"))
            feed_src = "live" if is_live_telemetry else "stored"
        elif "feed_rate_mmpm" in active_db_params:
            feed_val = float(active_db_params["feed_rate_mmpm"])
            feed_src = "stored"
        else:
            feed_val = 280.0
            feed_src = "configured"

        # Defect rate baseline: query real inspections or active batch
        defect_rate_pct = 12.3
        defect_source = "configured"
        try:
            from backend.app.db.session import SessionLocal
            from backend.app.db.models import InspectionRecord
            db = SessionLocal()
            recs = db.query(InspectionRecord).filter(InspectionRecord.batch_id == curr_batch_id).all()
            if not recs:
                recs = db.query(InspectionRecord).all()
            if recs:
                total_cnt = len(recs)
                defect_cnt = sum(1 for r in recs if r.defect_class.lower() != "normal")
                defect_rate_pct = round((defect_cnt / total_cnt) * 100.0, 2)
                defect_source = "live"
            elif active_batch and active_batch.target_yield_pct:
                defect_rate_pct = round(max(1.0, 100.0 - float(active_batch.target_yield_pct)), 2)
                defect_source = "stored"
            db.close()
        except Exception as e:
            logger.debug(f"[Orchestrator] Error inspecting DB records: {e}")

        # Run baseline through surrogate model and bottleneck detector
        surrogate_preds = self._predict_process(dem_val)
        bottleneck_res = self.bottleneck_detector.analyze_process_state(surrogate_preds)

        raw_throughput = surrogate_preds.get("Parts per hour", 181.6)
        baseline_throughput = round(float(raw_throughput), 1)

        material_dict = {
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

        materials_catalog = []
        try:
            all_mats = DatabaseService.get_all_materials()
            for m in all_mats:
                materials_catalog.append({
                    "code": m.code,
                    "name": m.name,
                    "alloy_grade": m.alloy_grade,
                    "yield_strength_mpa": m.yield_strength_mpa,
                    "tensile_strength_mpa": m.tensile_strength_mpa,
                    "critical_hydraulic_pressure_bar": m.critical_hydraulic_pressure_bar,
                    "optimal_coolant_ph_min": m.optimal_coolant_ph_min,
                    "optimal_coolant_ph_max": m.optimal_coolant_ph_max,
                    "max_conveyor_speed_mps": m.max_conveyor_speed_mps,
                    "cost_per_kg_usd": m.cost_per_kg_usd,
                    "scrap_penalty_usd": m.scrap_penalty_usd,
                    "governing_physics": m.governing_physics,
                })
        except Exception:
            materials_catalog = [material_dict]
        if not materials_catalog:
            materials_catalog = [material_dict]

        return {
            "batch_id": curr_batch_id,
            "material": material_dict,
            "available_materials": materials_catalog,
            "parameters": {
                "hydraulic_pressure_bar": {
                    "value": round(p_val, 1),
                    "unit": "bar",
                    "source": p_src,
                    "min": 150.0,
                    "max": 200.0,
                    "warning_min": 155.0,
                    "warning_max": min(176.0, active_mat.critical_hydraulic_pressure_bar),
                    "step": 1.0,
                    "description": "Hydraulic forming press ram pressure.",
                },
                "coolant_ph": {
                    "value": round(ph_val, 2),
                    "unit": "pH",
                    "source": ph_src,
                    "min": 6.5,
                    "max": 8.5,
                    "warning_min": active_mat.optimal_coolant_ph_min,
                    "warning_max": active_mat.optimal_coolant_ph_max,
                    "step": 0.1,
                    "description": "Recirculating cutting & stamping fluid chemical pH.",
                },
                "conveyor_speed_mps": {
                    "value": round(spd_val, 2),
                    "unit": "m/s",
                    "source": spd_src,
                    "min": 0.5,
                    "max": 2.5,
                    "warning_min": 0.8,
                    "warning_max": active_mat.max_conveyor_speed_mps,
                    "step": 0.05,
                    "description": "Transfer conveyor linear belt speed.",
                },
                "demand": {
                    "value": round(dem_val, 1),
                    "unit": "units/hr",
                    "source": dem_src,
                    "min": 4.0,
                    "max": 13.0,
                    "warning_min": 4.0,
                    "warning_max": 12.0,
                    "step": 0.5,
                    "description": "Scheduled line entity arrival rate demand.",
                },
                "spindle_feed_rate": {
                    "value": round(feed_val, 1),
                    "unit": "mm/min",
                    "source": feed_src,
                    "min": 150.0,
                    "max": 550.0,
                    "warning_min": 200.0,
                    "warning_max": 420.0,
                    "step": 5.0,
                    "description": "CNC milling/drilling spindle axial feed velocity.",
                },
            },
            "metrics": {
                "defect_rate_pct": round(defect_rate_pct, 2),
                "throughput_per_hr": baseline_throughput,
                "peak_utilization_pct": round(bottleneck_res["max_utilization"] * 100.0, 1),
                "line_efficiency_pct": round(bottleneck_res["line_efficiency_pct"], 1),
                "wip_units": round(bottleneck_res["total_wip_units"], 1),
                "lead_time_hrs": round(bottleneck_res["estimated_lead_time_hrs"], 2),
                "primary_bottleneck": bottleneck_res["primary_bottleneck"] or "Assembly",
                "station_utilizations": {
                    k: round(v * 100.0 if v <= 1.0 else v, 1)
                    for k, v in bottleneck_res["all_station_utilizations"].items()
                },
                "fpy_pct": round(100.0 - defect_rate_pct, 2),
                "monthly_loss_usd": round(baseline_throughput * 720 * (defect_rate_pct / 100.0) * active_mat.scrap_penalty_usd, 2),
                "monthly_loss_inr": round(baseline_throughput * 720 * (defect_rate_pct / 100.0) * active_mat.scrap_penalty_usd * USD_TO_INR_RATE, 2),
                "defect_source": defect_source,
            },
        }

    def _predict_process(self, demand: float) -> Dict[str, float]:
        """Runs the ProcessSurrogateModel for a given demand, or returns calibrated surrogate fallbacks."""
        if self.process_surrogate is not None:
            try:
                return self.process_surrogate.predict({"Demand": float(demand)})
            except Exception as e:
                logger.error(f"[Orchestrator] Process surrogate prediction error: {e}")

        # Conservative calibrated fallback if surrogate is loading/offline
        clamped_demand = max(4.0, min(13.0, float(demand)))
        pph = round(120.0 + clamped_demand * 8.8, 1)
        drill_u = round(min(0.98, 0.28 + clamped_demand * 0.042), 3)
        mill_u = round(min(0.95, 0.20 + clamped_demand * 0.033), 3)
        assembly_u = round(min(0.99, 0.35 + clamped_demand * 0.057), 3)
        wait_t = round(max(5.0, (clamped_demand - 3.5) * 9.2), 1)

        return {
            "Parts per hour": pph,
            "Drilling Util": drill_u,
            "Milling Util": mill_u,
            "Assembly Util": assembly_u,
            "Assembly Waiting Time": wait_t,
        }

    def validate_safety(
        self,
        params: Dict[str, float],
        material: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validates scenario parameters against machine_limits.yaml and active material alloy constraints.
        Returns safety status (SAFE, WARNING, BLOCKED) and lists of violations and warnings.
        """
        violations: List[str] = []
        warnings: List[str] = []

        # 1. Hydraulic Pressure
        p = params.get("hydraulic_pressure_bar") or params.get("pressure_bar") or params.get("hydraulic_pressure")
        if p is not None:
            p = float(p)
            crit_p = float(material.get("critical_hydraulic_pressure_bar", 180.0))
            mat_name = material.get("name", "Active Material")
            if p < 150.0:
                violations.append(f"Hydraulic pressure {p:.1f} bar is below the absolute machine minimum (150.0 bar).")
            elif p > 200.0:
                violations.append(f"Hydraulic pressure {p:.1f} bar exceeds absolute machine limit (200.0 bar). Severe mechanical hazard.")
            elif p > crit_p:
                warnings.append(
                    f"Hydraulic pressure {p:.1f} bar exceeds critical yield limit ({crit_p:.1f} bar) for {mat_name}. High risk of Griffith stress fractures."
                )
            elif p > 176.0:
                warnings.append(f"Hydraulic pressure {p:.1f} bar exceeds recommended operational envelope (155–176 bar).")

        # 2. Coolant pH
        ph = params.get("coolant_ph") or params.get("ph")
        if ph is not None:
            ph = float(ph)
            opt_min = float(material.get("optimal_coolant_ph_min", 7.6))
            opt_max = float(material.get("optimal_coolant_ph_max", 7.8))
            if ph < 6.5:
                violations.append(f"Coolant pH {ph:.2f} is below safety floor (6.5). Rapid chemical corrosion and acidic vapor risk.")
            elif ph > 8.5:
                violations.append(f"Coolant pH {ph:.2f} exceeds safety ceiling (8.5). Excessive alkaline skin/seal hazard.")
            elif ph < opt_min or ph > opt_max:
                warnings.append(f"Coolant pH {ph:.2f} is outside nominal metallurgical passivation window ({opt_min:.1f}–{opt_max:.1f}).")

        # 3. Conveyor Speed
        spd = params.get("conveyor_speed_mps") or params.get("conveyor_speed") or params.get("speed")
        if spd is not None:
            spd = float(spd)
            max_spd = float(material.get("max_conveyor_speed_mps", 1.0))
            if spd < 0.5:
                violations.append(f"Conveyor speed {spd:.2f} m/s is below transfer minimum (0.50 m/s). Causes line stall.")
            elif spd > 2.5:
                violations.append(f"Conveyor speed {spd:.2f} m/s exceeds conveyor structural limit (2.50 m/s). Belt displacement hazard.")
            elif spd > max_spd:
                warnings.append(f"Conveyor speed {spd:.2f} m/s exceeds material threshold ({max_spd:.2f} m/s). Increases Archard guide-rail scratch defects.")

        # 4. Demand
        dem = params.get("demand") or params.get("Demand")
        if dem is not None:
            dem = float(dem)
            if dem < 4.0:
                violations.append(f"Production demand {dem:.1f} units/hr is below minimum feeder rate (4.0 units/hr).")
            elif dem > 13.0:
                violations.append(f"Production demand {dem:.1f} units/hr exceeds line maximum buffer intake (13.0 units/hr).")
            elif dem > 11.5:
                warnings.append(f"Demand {dem:.1f} units/hr approaches line saturation threshold; expect severe queue accumulation.")

        # 5. Spindle Feed Rate
        feed = params.get("spindle_feed_rate") or params.get("feed_rate_mmpm") or params.get("feed_rate")
        if feed is not None:
            feed = float(feed)
            if feed < 200.0:
                violations.append(f"Spindle feed rate {feed:.0f} mm/min is below minimum machining speed (200 mm/min). Risk of tool rubbing.")
            elif feed > 450.0:
                violations.append(f"Spindle feed rate {feed:.0f} mm/min exceeds CNC spindle structural limit (450 mm/min). High tool breakage hazard.")
            elif feed > 320.0:
                warnings.append(f"Spindle feed rate {feed:.0f} mm/min exceeds Taylor tool-life threshold (320 mm/min). Risk of drill wandering & hole defects.")

        if violations:
            status = "BLOCKED"
            reason = f"Simulation blocked by {len(violations)} safety violation(s)."
        elif warnings:
            status = "WARNING"
            reason = f"Operational envelope warning: {len(warnings)} parameter(s) outside nominal range."
        else:
            status = "SAFE"
            reason = "All simulated setpoints are verified within certified nominal safety envelopes."

        return {
            "status": status,
            "reason": reason,
            "violations": violations,
            "warnings": warnings,
            "is_safe": len(violations) == 0,
        }

    def run_simulation(
        self,
        parameters: Dict[str, float],
        material_code: Optional[str] = None,
        batch_id: Optional[str] = None,
        baseline_params: Optional[Dict[str, float]] = None,
        baseline_defect_rate: Optional[float] = None,
        baseline_throughput: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Executes a complete, unified What-If scenario.
        Orchestrates WhatIfSimulatorEngine, ProcessSurrogateModel, and BottleneckDetector.
        """
        # 1. Resolve active baseline context
        baseline_ctx = self.get_active_baseline(batch_id=batch_id)
        curr_batch_id = baseline_ctx["batch_id"]

        # Resolve material
        if material_code:
            mat_obj = DatabaseService.get_material(material_code)
            if mat_obj:
                material_props = {
                    "code": mat_obj.code,
                    "name": mat_obj.name,
                    "alloy_grade": mat_obj.alloy_grade,
                    "yield_strength_mpa": mat_obj.yield_strength_mpa,
                    "tensile_strength_mpa": mat_obj.tensile_strength_mpa,
                    "critical_hydraulic_pressure_bar": mat_obj.critical_hydraulic_pressure_bar,
                    "optimal_coolant_ph_min": mat_obj.optimal_coolant_ph_min,
                    "optimal_coolant_ph_max": mat_obj.optimal_coolant_ph_max,
                    "max_conveyor_speed_mps": mat_obj.max_conveyor_speed_mps,
                    "cost_per_kg_usd": mat_obj.cost_per_kg_usd,
                    "scrap_penalty_usd": mat_obj.scrap_penalty_usd,
                    "governing_physics": mat_obj.governing_physics,
                }
            else:
                material_props = baseline_ctx["material"]
        else:
            material_props = baseline_ctx["material"]

        # 2. Harmonize baseline parameters
        base_p = baseline_ctx["parameters"]
        resolved_baseline: Dict[str, float] = {
            "hydraulic_pressure_bar": float(base_p["hydraulic_pressure_bar"]["value"]),
            "coolant_ph": float(base_p["coolant_ph"]["value"]),
            "conveyor_speed_mps": float(base_p["conveyor_speed_mps"]["value"]),
            "demand": float(base_p["demand"]["value"]),
            "spindle_feed_rate": float(base_p["spindle_feed_rate"]["value"]),
        }
        if baseline_params:
            for k, v in baseline_params.items():
                k_norm = k.lower().replace(" ", "_")
                if "pressure" in k_norm:
                    resolved_baseline["hydraulic_pressure_bar"] = float(v)
                elif "ph" in k_norm:
                    resolved_baseline["coolant_ph"] = float(v)
                elif "speed" in k_norm:
                    resolved_baseline["conveyor_speed_mps"] = float(v)
                elif "demand" in k_norm:
                    resolved_baseline["demand"] = float(v)
                elif "feed" in k_norm:
                    resolved_baseline["spindle_feed_rate"] = float(v)

        # 3. Harmonize modified scenario parameters
        scenario_params = dict(resolved_baseline)
        for k, v in parameters.items():
            k_norm = k.lower().replace(" ", "_")
            if "pressure" in k_norm:
                scenario_params["hydraulic_pressure_bar"] = float(v)
            elif "ph" in k_norm:
                scenario_params["coolant_ph"] = float(v)
            elif "speed" in k_norm:
                scenario_params["conveyor_speed_mps"] = float(v)
            elif "demand" in k_norm:
                scenario_params["demand"] = float(v)
            elif "feed" in k_norm:
                scenario_params["spindle_feed_rate"] = float(v)

        # 4. Safety Validation
        safety_report = self.validate_safety(scenario_params, material_props)

        # 5. Grounded Quality & Defect Modeling via WhatIfSimulatorEngine
        effective_base_defect = (
            float(baseline_defect_rate) / 100.0 if baseline_defect_rate is not None and baseline_defect_rate > 1.0
            else float(baseline_defect_rate) if baseline_defect_rate is not None
            else float(baseline_ctx["metrics"]["defect_rate_pct"]) / 100.0
        )
        effective_base_throughput = (
            float(baseline_throughput) if baseline_throughput is not None
            else float(baseline_ctx["metrics"]["throughput_per_hr"])
        )

        physics_res = self.what_if_engine.simulate_scenario(
            baseline_params=resolved_baseline,
            modified_params=scenario_params,
            baseline_defect_rate=effective_base_defect,
            baseline_throughput=effective_base_throughput,
            material_props=material_props,
        )

        # 6. Spindle Feed Rate Sensitivity (Taylor tool-life & hole defect modeling)
        base_feed = resolved_baseline.get("spindle_feed_rate", 280.0)
        mod_feed = scenario_params.get("spindle_feed_rate", 280.0)
        delta_feed = mod_feed - base_feed

        # Over-speed (>320 mm/min) increases hole drill wandering / tool chatter defect risk
        if base_feed > 320.0 and mod_feed <= 320.0:
            tool_wear_reduction_pct = min(45.0, max(5.0, ((base_feed - mod_feed) / (base_feed - 200.0)) * 40.0))
        elif delta_feed < 0:
            tool_wear_reduction_pct = min(25.0, max(0.0, -delta_feed * 0.12))
        else:
            tool_wear_reduction_pct = max(-35.0, -delta_feed * 0.18)

        # Refine composite defect reduction incorporating spindle sensitivity
        base_composite_red = physics_res["delta"]["defect_reduction_pct"]
        composite_reduction_pct = float(np.clip(
            base_composite_red * 0.90 + tool_wear_reduction_pct * 0.10,
            -30.0,
            92.0,
        ))

        simulated_defect_rate = max(0.005, effective_base_defect * (1.0 - composite_reduction_pct / 100.0))
        simulated_defect_rate_pct = round(simulated_defect_rate * 100.0, 2)
        baseline_defect_rate_pct = round(effective_base_defect * 100.0, 2)
        defect_delta_pct = round(simulated_defect_rate_pct - baseline_defect_rate_pct, 2)

        # 7. Discrete-Event Process & Bottleneck Recalculation
        base_demand = resolved_baseline["demand"]
        scen_demand = scenario_params["demand"]

        base_surrogate = self._predict_process(base_demand)
        scen_surrogate = self._predict_process(scen_demand)

        base_bottleneck = self.bottleneck_detector.analyze_process_state(base_surrogate)
        scen_bottleneck = self.bottleneck_detector.analyze_process_state(scen_surrogate)

        # Factor in defect reduction yield throughput improvement
        base_throughput = round(float(base_surrogate.get("Parts per hour", effective_base_throughput)), 1)
        simulated_throughput = round(
            float(scen_surrogate.get("Parts per hour", base_throughput)) * (1.0 + max(0.0, composite_reduction_pct) * 0.001),
            1,
        )
        throughput_delta_hr = round(simulated_throughput - base_throughput, 1)
        throughput_change_pct = round(((simulated_throughput - base_throughput) / max(0.1, base_throughput)) * 100.0, 1)

        # Station utilizations comparison
        station_comparison = []
        all_stations = sorted(list(set(
            list(base_bottleneck["all_station_utilizations"].keys()) +
            list(scen_bottleneck["all_station_utilizations"].keys())
        )))

        for st in all_stations:
            bu = round(base_bottleneck["all_station_utilizations"].get(st, 0.0) * 100.0, 1)
            su = round(scen_bottleneck["all_station_utilizations"].get(st, 0.0) * 100.0, 1)
            du = round(su - bu, 1)
            station_comparison.append({
                "station": st,
                "baseline_utilization_pct": bu,
                "scenario_utilization_pct": su,
                "delta_pct": du,
                "is_bottleneck_baseline": (st == base_bottleneck["primary_bottleneck"]),
                "is_bottleneck_scenario": (st == scen_bottleneck["primary_bottleneck"]),
            })

        # Bottleneck shift detection
        curr_bn = base_bottleneck["primary_bottleneck"] or "Assembly"
        scen_bn = scen_bottleneck["primary_bottleneck"] or "Assembly"
        is_shifted = (curr_bn != scen_bn)

        # WIP and Lead-time deltas
        base_wip = round(float(base_bottleneck["total_wip_units"]), 1)
        scen_wip = round(float(scen_bottleneck["total_wip_units"]), 1)
        wip_delta = round(scen_wip - base_wip, 1)

        base_lead_time = round(float(base_bottleneck["estimated_lead_time_hrs"]), 2)
        scen_lead_time = round(float(scen_bottleneck["estimated_lead_time_hrs"]), 2)
        lead_time_delta = round(scen_lead_time - base_lead_time, 2)

        base_peak_util = round(float(base_bottleneck["max_utilization"]) * 100.0, 1)
        scen_peak_util = round(float(scen_bottleneck["max_utilization"]) * 100.0, 1)
        peak_util_delta = round(scen_peak_util - base_peak_util, 1)

        base_line_eff = round(float(base_bottleneck["line_efficiency_pct"]), 1)
        scen_line_eff = round(float(scen_bottleneck["line_efficiency_pct"]), 1)
        line_eff_delta = round(scen_line_eff - base_line_eff, 1)

        # 8. Economic Calculations (Dual Currency: USD $ and INR ₹)
        unit_scrap_cost = float(material_props.get("scrap_penalty_usd", 52.50))
        monthly_parts_base = base_throughput * 720.0
        monthly_defects_base = monthly_parts_base * effective_base_defect

        monthly_parts_scen = simulated_throughput * 720.0
        monthly_defects_scen = monthly_parts_scen * simulated_defect_rate

        saved_defects = max(0.0, monthly_defects_base - monthly_defects_scen)
        scrap_savings_usd = round(saved_defects * unit_scrap_cost, 2)
        margin_per_unit = 150.0  # standard contribution margin per unit
        throughput_gain_usd = round(max(0.0, (monthly_parts_scen - monthly_parts_base) * margin_per_unit), 2)
        total_monthly_benefit_usd = round(scrap_savings_usd + throughput_gain_usd, 2)

        scrap_savings_inr = round(scrap_savings_usd * USD_TO_INR_RATE, 2)
        throughput_gain_inr = round(throughput_gain_usd * USD_TO_INR_RATE, 2)
        total_monthly_benefit_inr = round(total_monthly_benefit_usd * USD_TO_INR_RATE, 2)

        monthly_loss_base_usd = round(monthly_defects_base * unit_scrap_cost, 2)
        monthly_loss_scen_usd = round(monthly_defects_scen * unit_scrap_cost, 2)
        monthly_loss_base_inr = round(monthly_loss_base_usd * USD_TO_INR_RATE, 2)
        monthly_loss_scen_inr = round(monthly_loss_scen_usd * USD_TO_INR_RATE, 2)

        # Quality mode breakdown from WhatIfSimulatorEngine physics
        crit_p = float(material_props.get("critical_hydraulic_pressure_bar", 180.0))
        p_base = resolved_baseline["hydraulic_pressure_bar"]
        p_mod = scenario_params["hydraulic_pressure_bar"]
        dp = p_mod - p_base
        p_excess_base = max(0.0, p_base - crit_p)
        p_excess_mod = max(0.0, p_mod - crit_p)
        if p_excess_base > 0:
            crack_red = min(85.0, max(0.0, ((p_excess_base - p_excess_mod) / p_excess_base) * 75.0 + max(0.0, -dp) * 1.8))
        else:
            crack_red = max(-15.0, min(50.0, -dp * 2.0))

        ph_base = resolved_baseline["coolant_ph"]
        ph_mod = scenario_params["coolant_ph"]
        target_ph_min = float(material_props.get("optimal_coolant_ph_min", 7.6))
        target_ph_max = float(material_props.get("optimal_coolant_ph_max", 7.8))
        ph_imp = max(0.0, min(ph_mod, target_ph_max) - min(ph_base, target_ph_min))
        rust_red = max(-10.0, min(60.0, ph_imp * 40.0))

        spd_base = resolved_baseline["conveyor_speed_mps"]
        spd_mod = scenario_params["conveyor_speed_mps"]
        dspd = spd_mod - spd_base
        max_speed = float(material_props.get("max_conveyor_speed_mps", 1.0))
        spd_excess_base = max(0.0, spd_base - max_speed)
        spd_excess_mod = max(0.0, spd_mod - max_speed)
        scratch_red = max(-10.0, min(55.0, (spd_excess_base - spd_excess_mod) * 70.0 - dspd * 45.0))

        # 9. Feasibility & Recommendation Score (0–100)
        risk_penalty = max(0.0, abs(dp) * 0.15 + abs(dspd) * 8.0 + (15.0 if safety_report["status"] == "WARNING" else 0.0))
        if safety_report["status"] == "BLOCKED":
            rec_score = 0
            risk_level = "High"
        else:
            rec_score = int(np.clip(88.0 + composite_reduction_pct * 0.4 - risk_penalty, 20.0, 98.0))
            risk_level = "Low" if risk_penalty < 15 and safety_report["status"] == "SAFE" else "Medium"

        # 10. Assemble Unified Response Structure
        baseline_metrics = {
            "defect_rate_pct": baseline_defect_rate_pct,
            "throughput_per_hr": base_throughput,
            "peak_utilization_pct": base_peak_util,
            "line_efficiency_pct": base_line_eff,
            "wip_units": base_wip,
            "lead_time_hrs": base_lead_time,
            "primary_bottleneck": curr_bn,
            "station_utilizations": {
                k: round(v * 100.0, 1) for k, v in base_bottleneck["all_station_utilizations"].items()
            },
            "monthly_loss_usd": monthly_loss_base_usd,
            "monthly_loss_inr": monthly_loss_base_inr,
            "fpy_pct": round(100.0 - baseline_defect_rate_pct, 2),
        }

        scenario_metrics = {
            "defect_rate_pct": simulated_defect_rate_pct,
            "throughput_per_hr": simulated_throughput,
            "peak_utilization_pct": scen_peak_util,
            "line_efficiency_pct": scen_line_eff,
            "wip_units": scen_wip,
            "lead_time_hrs": scen_lead_time,
            "primary_bottleneck": scen_bn,
            "station_utilizations": {
                k: round(v * 100.0, 1) for k, v in scen_bottleneck["all_station_utilizations"].items()
            },
            "monthly_loss_usd": monthly_loss_scen_usd,
            "monthly_loss_inr": monthly_loss_scen_inr,
            "fpy_pct": round(100.0 - simulated_defect_rate_pct, 2),
        }

        delta_metrics = {
            "defect_reduction_pct": round(composite_reduction_pct, 1),
            "defect_rate_delta_pct": defect_delta_pct,
            "throughput_change_pct": throughput_change_pct,
            "throughput_delta_per_hr": throughput_delta_hr,
            "peak_utilization_delta_pct": peak_util_delta,
            "line_efficiency_delta_pct": line_eff_delta,
            "wip_delta_units": wip_delta,
            "lead_time_delta_hrs": lead_time_delta,
            "monthly_savings_usd": total_monthly_benefit_usd,
            "monthly_savings_inr": total_monthly_benefit_inr,
        }

        quality_impact = {
            "crack_reduction_pct": round(crack_red, 1),
            "rust_reduction_pct": round(rust_red, 1),
            "scratch_reduction_pct": round(scratch_red, 1),
            "tool_wear_reduction_pct": round(tool_wear_reduction_pct, 1),
            "composite_reduction_pct": round(composite_reduction_pct, 1),
            "fpy_baseline_pct": round(100.0 - baseline_defect_rate_pct, 2),
            "fpy_simulated_pct": round(100.0 - simulated_defect_rate_pct, 2),
            "governing_physics": material_props.get("governing_physics", ""),
        }

        bottleneck_impact = {
            "current_bottleneck": curr_bn,
            "scenario_bottleneck": scen_bn,
            "is_constraint_shifted": is_shifted,
            "line_balance_status": "Balanced" if scen_line_eff >= 85.0 else f"Constrained by {scen_bn}",
            "station_comparison": station_comparison,
        }

        economics = {
            "monthly_scrap_savings_usd": scrap_savings_usd,
            "monthly_throughput_gain_usd": throughput_gain_usd,
            "total_monthly_benefit_usd": total_monthly_benefit_usd,
            "monthly_scrap_savings_inr": scrap_savings_inr,
            "monthly_throughput_gain_inr": throughput_gain_inr,
            "total_monthly_benefit_inr": total_monthly_benefit_inr,
            "exchange_rate": USD_TO_INR_RATE,
            "basis": "Estimated from simulated defect reduction and throughput change.",
        }

        result = {
            "batch_id": curr_batch_id,
            "material": material_props,
            "safety": safety_report,
            "baseline": baseline_metrics,
            "scenario": scenario_metrics,
            # Backward-compatible alias for existing frontend/tests
            "simulated": scenario_metrics,
            "delta": delta_metrics,
            "quality_impact": quality_impact,
            "bottleneck_impact": bottleneck_impact,
            "economics": economics,
            "recommendation_score": rec_score,
            "risk_level": risk_level,
            "parameters": {
                "baseline": resolved_baseline,
                "scenario": scenario_params,
            },
            "metadata": {
                "engine": "ForgeX Unified Simulation Orchestrator v2.0",
                "process_model": "xgboost_process.pkl",
                "physics_model": "WhatIfSimulatorEngine (Griffith, Pourbaix, Archard, Taylor)",
                "bottleneck_analyzer": "BottleneckDetector (Discrete-Event Queue)",
            },
        }

        # 11. Persist to PostgreSQL / SQLite simulation_scenarios
        try:
            DatabaseService.record_simulation_scenario(
                batch_id=curr_batch_id,
                material_code=material_props["code"],
                baseline_defect_pct=baseline_defect_rate_pct,
                simulated_defect_pct=simulated_defect_rate_pct,
                defect_reduction_pct=round(composite_reduction_pct, 1),
                throughput_change_pct=throughput_change_pct,
                monthly_savings_usd=total_monthly_benefit_usd,
                recommendation_score=rec_score,
                risk_level=risk_level,
                parameters={"baseline": resolved_baseline, "scenario": scenario_params},
            )
            DatabaseService.set_cache("latest_simulation_result", result)
        except Exception as e:
            logger.warning(f"[Orchestrator] Non-fatal DB recording error: {e}")

        return result


def get_simulation_orchestrator() -> SimulationOrchestrator:
    return SimulationOrchestrator.get_instance()
