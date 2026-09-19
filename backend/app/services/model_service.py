import os
import sys
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger("backend.services.model_service")

# Root directory bootstrap
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.vision.infer import VisionInferenceEngine
from models.process.bottleneck import BottleneckDetector
from models.process.model import ProcessSurrogateModel
from models.correlation.root_cause_classifier import RootCauseClassifier
from models.correlation.correlation_engine import CorrelationEngine
from models.simulator.what_if_engine import WhatIfSimulatorEngine


class ModelService:
    """
    Central singleton service holding preloaded AI models.
    """
    _instance: Optional["ModelService"] = None

    def __init__(self):
        self.vision_engine: Optional[VisionInferenceEngine] = None
        self.bottleneck_detector: Optional[BottleneckDetector] = None
        self.root_cause_classifier: Optional[RootCauseClassifier] = None
        self.correlation_engine: Optional[CorrelationEngine] = None
        self.what_if_simulator: Optional[WhatIfSimulatorEngine] = None
        self.is_initialized: bool = False

    @classmethod
    def get_instance(cls) -> "ModelService":
        if cls._instance is None:
            cls._instance = ModelService()
        return cls._instance

    def initialize(
        self,
        vision_weights: Optional[str] = None,
        correlation_weights: Optional[str] = None,
    ):
        """
        Initializes and preloads all AI/ML models.
        """
        if vision_weights is None:
            vision_weights = os.path.join(root_dir, "models", "weights", "efficientnet_b4_defect.pth")
        if correlation_weights is None:
            correlation_weights = os.path.join(root_dir, "models", "weights", "xgboost_correlation.pkl")
        logger.info("[*] Initializing Industrial AI Decision Intelligence models...")

        # 1. Bottleneck Detector
        self.bottleneck_detector = BottleneckDetector()

        # 2. Correlation & Root Cause Engine
        self.correlation_engine = CorrelationEngine()
        if os.path.exists(correlation_weights):
            try:
                self.root_cause_classifier = RootCauseClassifier.load(correlation_weights)
                logger.info(f"[+] Loaded Root Cause Classifier from {correlation_weights}")
            except Exception as e:
                logger.warning(f"[-] Could not load Root Cause Classifier: {e}")

        # 3. What-If Simulator
        self.what_if_simulator = WhatIfSimulatorEngine()

        # 4. Vision Model
        if os.path.exists(vision_weights):
            try:
                self.vision_engine = VisionInferenceEngine(weights_path=vision_weights)
                logger.info(f"[+] Loaded Vision Inference Engine from {vision_weights}")
            except Exception as e:
                logger.warning(f"[-] Could not load Vision Engine: {e}")

        self.is_initialized = True
        logger.info("[*] All model services successfully initialized.")


def get_model_service() -> ModelService:
    return ModelService.get_instance()
