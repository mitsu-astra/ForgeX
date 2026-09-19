"""
What-If Scenario Simulator Engine with Material Metallurgy & Fracture Mechanics
Simulates process parameter adjustments grounded in physical alloy properties and economic unit costs.
"""

from typing import Dict, Any, Optional
import numpy as np


class WhatIfSimulatorEngine:
    """
    Simulates changes to operational parameters grounded in material metallurgy,
    yield strength, critical pressure limits, and economic scrap costs.
    """

    def __init__(
        self,
        default_scrap_cost: float = 50.0,
        default_rework_cost: float = 30.0,
        default_margin_per_unit: float = 150.0,
    ):
        self.default_scrap_cost = default_scrap_cost
        self.default_rework_cost = default_rework_cost
        self.default_margin_per_unit = default_margin_per_unit

    def simulate_scenario(
        self,
        baseline_params: Dict[str, float],
        modified_params: Dict[str, float],
        baseline_defect_rate: float = 0.123,  # 12.3% baseline
        baseline_throughput: float = 145.0,   # 145 parts/hr
        material_props: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calculates predicted outcomes when parameters are modified from baseline,
        grounded in material properties (yield strength, critical pressure limit, optimal pH).
        """
        # Default material: AISI 4140 High-Tensile Alloy Steel
        material = material_props or {
            "code": "AISI_4140",
            "name": "AISI 4140 Chromium-Molybdenum Alloy Steel",
            "alloy_grade": "High-Tensile Quenched & Tempered",
            "yield_strength_mpa": 415.0,
            "tensile_strength_mpa": 655.0,
            "critical_hydraulic_pressure_bar": 180.0,
            "optimal_coolant_ph_min": 7.6,
            "optimal_coolant_ph_max": 7.8,
            "max_conveyor_speed_mps": 1.00,
            "cost_per_kg_usd": 4.20,
            "scrap_penalty_usd": 52.50,
            "governing_physics": "Griffith fracture criterion & hydraulic forming residual stress threshold.",
        }

        # Normalize baseline defect rate if passed as percentage (e.g., 12.5 instead of 0.125)
        if baseline_defect_rate > 1.0:
            baseline_defect_rate = baseline_defect_rate / 100.0

        def get_param(params: Dict[str, float], keys: list, default: float) -> float:
            for k in keys:
                if k in params:
                    return float(params[k])
            for pk, pv in params.items():
                pk_norm = str(pk).lower().replace(" ", "").replace("_", "")
                for k in keys:
                    k_norm = str(k).lower().replace(" ", "").replace("_", "")
                    if k_norm in pk_norm or pk_norm in k_norm:
                        try:
                            return float(pv)
                        except (ValueError, TypeError):
                            pass
            return default

        # Parameter diffs with aliases support
        crit_p = float(material.get("critical_hydraulic_pressure_bar", 180.0))
        p_base = get_param(baseline_params, ["pressure_bar", "hydraulic_pressure_bar", "hydraulic_pressure", "pressure"], 188.0)
        p_mod = get_param(modified_params, ["pressure_bar", "hydraulic_pressure_bar", "hydraulic_pressure", "pressure"], 172.0)
        delta_pressure = p_mod - p_base

        ph_base = get_param(baseline_params, ["coolant_ph", "ph"], 7.1)
        ph_mod = get_param(modified_params, ["coolant_ph", "ph"], 7.7)
        delta_ph = ph_mod - ph_base

        spd_base = get_param(baseline_params, ["conveyor_speed_mps", "conveyor_speed", "speed"], 1.25)
        spd_mod = get_param(modified_params, ["conveyor_speed_mps", "conveyor_speed", "speed"], 0.95)
        delta_speed = spd_mod - spd_base

        q_base = get_param(baseline_params, ["queue_time", "queue_time_hours", "queue_time_hrs"], 3.5)
        q_mod = get_param(modified_params, ["queue_time", "queue_time_hours", "queue_time_hrs"], q_base)
        delta_queue = q_mod - q_base

        dem_base = get_param(baseline_params, ["demand", "demand_multiplier"], 7.0)
        dem_mod = get_param(modified_params, ["demand", "demand_multiplier"], dem_base)
        delta_demand = dem_mod - dem_base

        # Defect impact modeling grounded in metallurgy and physical stress ratios:
        # 1. Forming Stress Fractures (Crack):
        # Above critical pressure (180 bar for AISI 4140), forming strain exceeds elastic limit.
        # Reducing pressure below critical threshold drops stress crack initiation probability significantly.
        p_excess_base = max(0.0, p_base - crit_p)
        p_excess_mod = max(0.0, p_mod - crit_p)
        if p_excess_base > 0:
            crack_reduction_pct = min(85.0, max(0.0, ((p_excess_base - p_excess_mod) / p_excess_base) * 75.0 + max(0.0, -delta_pressure) * 1.8))
        else:
            crack_reduction_pct = max(-15.0, min(50.0, -delta_pressure * 2.0))

        # 2. Pourbaix Corrosion Kinetics (Rust):
        # Bringing coolant pH from 7.1 into optimal zone (7.6-7.8) prevents active acid attack on ferrous alloys.
        target_ph_min = float(material.get("optimal_coolant_ph_min", 7.6))
        target_ph_max = float(material.get("optimal_coolant_ph_max", 7.8))
        ph_improvement = max(0.0, min(ph_mod, target_ph_max) - min(ph_base, target_ph_min))
        rust_reduction_pct = max(-10.0, min(60.0, ph_improvement * 40.0 - delta_queue * 6.0))

        # 3. Archard Abrasive Wear (Scratch):
        # Lowering conveyor speed below max speed limits guide-rail friction.
        max_speed = float(material.get("max_conveyor_speed_mps", 1.0))
        speed_excess_base = max(0.0, spd_base - max_speed)
        speed_excess_mod = max(0.0, spd_mod - max_speed)
        scratch_reduction_pct = max(-10.0, min(55.0, (speed_excess_base - speed_excess_mod) * 70.0 - delta_speed * 45.0))

        # Composite defect rate reduction % based on active material defect sensitivity
        # For AISI 4140 steel, crack is the dominant failure mode under press overload
        composite_reduction_pct = float(np.clip(
            (0.55 * crack_reduction_pct + 0.30 * rust_reduction_pct + 0.15 * scratch_reduction_pct),
            -20.0,
            88.0,
        ))

        new_defect_rate = max(0.005, baseline_defect_rate * (1.0 - composite_reduction_pct / 100.0))
        defect_rate_delta_pct = (new_defect_rate - baseline_defect_rate) * 100.0

        # Throughput changes
        # Demand multiplier + slight efficiency gain from fewer reworks
        throughput_multiplier = 1.0 + (delta_demand * 0.02) + (composite_reduction_pct * 0.0015)
        simulated_throughput = round(baseline_throughput * throughput_multiplier, 1)
        throughput_change_pct = round(((simulated_throughput - baseline_throughput) / baseline_throughput) * 100.0, 1)

        # Economic calculation with material unit cost from PostgreSQL
        unit_scrap_cost = float(material.get("scrap_penalty_usd", self.default_scrap_cost))
        monthly_parts_baseline = baseline_throughput * 720
        monthly_defects_baseline = monthly_parts_baseline * baseline_defect_rate

        monthly_parts_sim = simulated_throughput * 720
        monthly_defects_sim = monthly_parts_sim * new_defect_rate

        saved_defective_units = max(0.0, monthly_defects_baseline - monthly_defects_sim)
        monthly_scrap_savings = saved_defective_units * unit_scrap_cost
        monthly_throughput_gain = max(0.0, (monthly_parts_sim - monthly_parts_baseline) * self.default_margin_per_unit)
        total_monthly_benefit = round(monthly_scrap_savings + monthly_throughput_gain, 2)

        # Recommendation feasibility score (0 - 100)
        risk_penalty = max(0.0, abs(delta_pressure) * 0.15 + abs(delta_speed) * 8.0)
        recommendation_score = int(np.clip(88.0 + composite_reduction_pct * 0.4 - risk_penalty, 20.0, 98.0))

        return {
            "material": {
                "code": material.get("code", "AISI_4140"),
                "name": material.get("name", "AISI 4140 Chromium-Molybdenum Alloy Steel"),
                "alloy_grade": material.get("alloy_grade", "High-Tensile Quenched & Tempered"),
                "yield_strength_mpa": material.get("yield_strength_mpa", 415.0),
                "critical_pressure_bar": crit_p,
                "optimal_coolant_ph": f"{target_ph_min} - {target_ph_max}",
                "unit_scrap_penalty_usd": unit_scrap_cost,
                "governing_physics": material.get("governing_physics", "Griffith fracture criterion & hydraulic forming residual stress threshold."),
            },
            "baseline": {
                "defect_rate_pct": round(baseline_defect_rate * 100.0, 2),
                "throughput_per_hr": round(baseline_throughput, 1),
                "monthly_loss_usd": round(monthly_defects_baseline * unit_scrap_cost, 2),
            },
            "simulated": {
                "defect_rate_pct": round(new_defect_rate * 100.0, 2),
                "throughput_per_hr": simulated_throughput,
                "monthly_loss_usd": round(monthly_defects_sim * unit_scrap_cost, 2),
            },
            "delta": {
                "defect_reduction_pct": round(composite_reduction_pct, 1),
                "throughput_change_pct": throughput_change_pct,
                "monthly_savings_usd": total_monthly_benefit,
            },
            "recommendation_score": recommendation_score,
            "risk_level": "Low" if risk_penalty < 15 else "Medium",
        }

