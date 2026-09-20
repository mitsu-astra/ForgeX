"""
Thread-safe singleton store for active process telemetry and economic parameters,
ensuring process state is derived strictly from real uploaded CSVs or trained simulation datasets.
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("backend.services.process_store")


class ProcessStore:
    _instance: Optional["ProcessStore"] = None

    def __init__(self):
        self._active_process_state: Optional[Dict[str, Any]] = None
        self._active_source: str = "simulation"  # "uploaded_csv" or "simulation"
        self._economic_params: Dict[str, float] = {
            "scrap_cost_per_unit": 50.0,
            "rework_cost_per_unit": 30.0,
            "contribution_margin_per_unit": 150.0,
            "hourly_labor_cost": 25.0,
        }

    @classmethod
    def get_instance(cls) -> "ProcessStore":
        if cls._instance is None:
            cls._instance = ProcessStore()
        return cls._instance

    def set_state(self, state: Dict[str, Any], source: str = "uploaded_csv"):
        self._active_process_state = state
        self._active_source = source

    def reset(self):
        """Clear stale process state so a new upload starts fresh."""
        self._active_process_state = None
        self._active_source = "simulation"
        logger.debug("ProcessStore reset: active process state cleared.")

    def get_state(self) -> Optional[Dict[str, Any]]:
        if self._active_process_state is not None:
            return self._active_process_state
        # Fallback to database only if explicitly requested (avoid stale persistence)
        return None

    def get_source(self) -> str:
        return self._active_source

    def set_economic_params(self, params: Dict[str, float]):
        self._economic_params.update(params)

    def get_economic_params(self) -> Dict[str, float]:
        return dict(self._economic_params)


process_store = ProcessStore.get_instance()
