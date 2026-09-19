"""
Bottleneck Detection and Line Balance Analyzer
Identifies throughput constraints, station over-utilization, queue buildup, and economic impact.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


class BottleneckDetector:
    """
    Analyzes manufacturing process logs to identify operational bottlenecks and line imbalances.
    """

    def __init__(
        self,
        critical_util_threshold: float = 0.85,
        warning_util_threshold: float = 0.75,
    ):
        self.critical_util_threshold = critical_util_threshold
        self.warning_util_threshold = warning_util_threshold

    def analyze_process_state(
        self,
        process_row: Dict[str, Any],
        model_type: str = "model_1",
        economic_params: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Analyzes a single manufacturing state (e.g. from current batch or simulation point).
        """
        if economic_params is None:
            economic_params = {
                "scrap_cost_per_unit": 50.0,
                "rework_cost_per_unit": 30.0,
                "contribution_margin_per_unit": 150.0,
                "hourly_labor_cost": 25.0,
            }

        station_utils = {}
        station_queues = {}

        # Extract station utilization and queue times
        for k, v in process_row.items():
            k_lower = k.lower()
            try:
                val = float(v)
            except (ValueError, TypeError):
                continue

            if "util" in k_lower:
                clean_name = k.replace("Util", "").replace("utilization", "").replace("Utilization", "").strip("_ ")
                station_utils[clean_name if clean_name else k] = val

            elif "wait" in k_lower or "queue" in k_lower:
                clean_name = k.replace("Waiting Time", "").replace("Queue Time", "").strip("_ ")
                station_queues[clean_name if clean_name else k] = val

        # Detect bottlenecks
        bottlenecks: List[Dict[str, Any]] = []
        max_station = None
        max_util = -1.0

        for st_name, util in station_utils.items():
            # Standardize utilization scale (0 to 1)
            util_norm = util if util <= 1.0 else util / 100.0
            queue_val = station_queues.get(st_name, 0.0)

            if util_norm > max_util:
                max_util = util_norm
                max_station = st_name

            if util_norm >= self.critical_util_threshold:
                severity = "high"
                impact = f"Station at {round(util_norm*100, 1)}% capacity; limits line throughput"
            elif util_norm >= self.warning_util_threshold:
                severity = "medium"
                impact = f"Station approaching capacity limit ({round(util_norm*100, 1)}%)"
            else:
                severity = "low"
                impact = "Normal operating load"

            if severity in ["high", "medium"]:
                rec_act = f"Offload {st_name} or increase station parallel buffer capacity" if severity == "high" else f"Monitor {st_name} cycle times and rebalance line"
                bottlenecks.append({
                    "station": st_name,
                    "type": "capacity" if util_norm >= self.critical_util_threshold else "queue",
                    "severity": severity,
                    "utilization": round(util_norm, 3),
                    "queue_time_hrs": round(queue_val, 2),
                    "impact": impact,
                    "recommended_action": rec_act,
                })

        # Sort bottlenecks by severity
        severity_rank = {"high": 0, "medium": 1, "low": 2}
        bottlenecks.sort(key=lambda b: (severity_rank[b["severity"]], -b["utilization"]))

        # Calculate line efficiency (mean util / max util)
        utils_list = [u if u <= 1.0 else u / 100.0 for u in station_utils.values()]
        mean_util = float(np.mean(utils_list)) if utils_list else 0.0
        line_efficiency = round((mean_util / max(1e-5, max_util)) * 100.0, 1) if max_util > 0 else 100.0

        # Estimate economic loss
        throughput_parts_hr = float(process_row.get("Parts per hour", process_row.get("Entities Out", 100.0)))
        theoretical_max = throughput_parts_hr / max(0.5, max_util) if max_util > 0 else throughput_parts_hr
        throughput_loss_units = max(0.0, theoretical_max - throughput_parts_hr)
        throughput_loss_usd = round(throughput_loss_units * economic_params.get("contribution_margin_per_unit", 150.0), 2)

        hourly_loss = throughput_loss_usd
        daily_loss = round(hourly_loss * 24, 2)
        monthly_loss = round(hourly_loss * 720, 2)

        return {
            "primary_bottleneck": max_station,
            "max_utilization": round(max_util, 3),
            "line_efficiency_pct": min(100.0, line_efficiency),
            "total_wip_units": round(sum(station_queues.values()) * 15.0, 1),
            "estimated_lead_time_hrs": round(sum(station_queues.values()) + 1.2, 2),
            "bottlenecks": bottlenecks,
            "all_station_utilizations": {k: round(v if v <= 1.0 else v / 100.0, 3) for k, v in station_utils.items()},
            "all_station_queue_times": {k: round(v, 3) for k, v in station_queues.items()},
            "economic_impact": {
                "throughput_loss_units_per_hr": round(throughput_loss_units, 1),
                "hourly_throughput_loss_usd": hourly_loss,
                "daily_throughput_loss_usd": daily_loss,
                "monthly_throughput_loss_usd": monthly_loss,
                "monthly_estimated_loss_usd": monthly_loss,
            },
        }
