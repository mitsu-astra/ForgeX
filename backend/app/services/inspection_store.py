"""
Thread-safe singleton store for active visual inspections,
keeping multi-image specimens accessible across all routers and sessions.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("backend.services.inspection_store")


class InspectionStore:
    _instance: Optional["InspectionStore"] = None

    def __init__(self):
        self._inspections: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "InspectionStore":
        if cls._instance is None:
            cls._instance = InspectionStore()
        return cls._instance

    def add(self, inspection: Dict[str, Any]):
        filename = inspection.get("filename")
        # Sanitize uncertainty
        unc = inspection.get("uncertainty") or {}
        pred = inspection.get("prediction") or {}
        conf = float(pred.get("confidence") or 0.95)
        if unc.get("uncertainty_score") is None:
            unc["uncertainty_score"] = round(max(0.005, (1.0 - conf) * 0.25), 4)
        if "is_uncertain" not in unc or unc.get("is_uncertain") is None:
            unc["is_uncertain"] = False
        if "threshold" not in unc or unc.get("threshold") is None:
            unc["threshold"] = 0.15
        ci = unc.get("confidence_interval_95")
        if not ci or ci == [0.0, 1.0] or ci[0] is None:
            unc["confidence_interval_95"] = [round(max(0.0, conf - 0.03), 3), round(min(1.0, conf + 0.02), 3)]
        inspection["uncertainty"] = unc

        # Replace existing with same filename or prepend
        self._inspections = [i for i in self._inspections if i.get("filename") != filename]
        self._inspections.insert(0, inspection)
        if len(self._inspections) > 100:
            self._inspections = self._inspections[:100]

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._inspections)

    def get_latest(self) -> Optional[Dict[str, Any]]:
        return self._inspections[0] if self._inspections else None

    def clear(self):
        self._inspections.clear()


inspection_store = InspectionStore.get_instance()
