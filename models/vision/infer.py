"""
Inference Engine for Industrial Defect Visual Inspection
Provides high-performance single and batch inference with Grad-CAM and MC Dropout uncertainty.
"""

import os
import io
import sys
import time
import base64
from typing import Union, List, Dict, Any, Optional, Tuple
from PIL import Image
import numpy as np
import cv2
import torch
from torchvision import transforms

# Ensure root directory in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.vision.dataset import CLASSES, IDX_TO_CLASS, IMAGENET_MEAN, IMAGENET_STD
from models.vision.model import DefectClassifier
from models.vision.gradcam import GradCAM


class VisionInferenceEngine:
    """
    End-to-end inference engine for visual inspection.
    """

    def __init__(
        self,
        weights_path: str = "/home/koushik_2109/Hackathons/CMR/models/weights/efficientnet_b4_defect.pth",
        device: Optional[str] = None,
    ):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Model weights not found at {weights_path}")

        self.model = DefectClassifier.load_checkpoint(weights_path, device=self.device)
        self.model.eval()

        self.gradcam = GradCAM(self.model)

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    def _load_and_preprocess(self, image_input: Union[str, bytes, bytearray, Image.Image, np.ndarray]) -> Tuple[torch.Tensor, np.ndarray, Image.Image]:
        """
        Loads image and produces both a normalized PyTorch tensor and an RGB uint8 array.
        """
        if isinstance(image_input, (bytes, bytearray)):
            pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
        elif isinstance(image_input, str):
            pil_img = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            if image_input.ndim == 2:
                pil_img = Image.fromarray(image_input).convert("RGB")
            else:
                pil_img = Image.fromarray(image_input)
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        rgb_np = np.array(pil_img)
        tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        return tensor, rgb_np, pil_img

    def predict_single(
        self,
        image_input: Union[str, bytes, bytearray, Image.Image, np.ndarray],
        include_heatmap: bool = True,
        uncertainty_samples: int = 10,
        uncertainty_threshold: float = 0.15,
    ) -> Dict[str, Any]:
        """
        Infers defect class, confidence, uncertainty, and localization for a single image.
        """
        t0 = time.perf_counter()
        tensor, rgb_np, _ = self._load_and_preprocess(image_input)

        # Run MC Dropout uncertainty prediction
        with torch.no_grad():
            mean_probs, pred_idx, uncertainty = self.model.predict_with_uncertainty(
                tensor, n_samples=uncertainty_samples
            )

        pred_class_idx = int(pred_idx.item())
        pred_class = IDX_TO_CLASS[pred_class_idx]
        confidence = float(mean_probs[0, pred_class_idx].item())
        unc_score = float(uncertainty.item())
        is_uncertain = unc_score > uncertainty_threshold

        probs_dict = {
            cls_name: round(float(mean_probs[0, i].item()), 4)
            for i, cls_name in enumerate(CLASSES)
        }

        # 95% Confidence interval estimation for predicted class
        ci_lower = max(0.0, confidence - 1.96 * unc_score)
        ci_upper = min(1.0, confidence + 1.96 * unc_score)

        result: Dict[str, Any] = {
            "prediction": {
                "class": pred_class,
                "confidence": round(confidence, 4),
                "class_id": pred_class_idx,
                "is_defect": pred_class != "normal",
                "probabilities": probs_dict,
            },
            "uncertainty": {
                "is_uncertain": is_uncertain,
                "uncertainty_score": round(unc_score, 4),
                "threshold": uncertainty_threshold,
                "confidence_interval_95": [round(ci_lower, 4), round(ci_upper, 4)],
                "method": "mc_dropout",
            },
        }

        # Generate localization if requested
        if include_heatmap:
            # Enable gradient computation for GradCAM
            heatmap = self.gradcam.generate_heatmap(tensor, target_class=pred_class_idx)
            overlay = self.gradcam.overlay_heatmap(rgb_np, heatmap)

            if pred_class != "normal":
                bboxes, defect_area_pct = self.gradcam.extract_bounding_boxes(heatmap)
                for b in bboxes:
                    b["defect_type"] = pred_class
            else:
                bboxes = []
                defect_area_pct = 0.0

            # Base64 encode heatmap and overlay for easy web/API transmission
            _, buffer_hm = cv2.imencode('.png', (heatmap * 255).astype(np.uint8))
            hm_b64 = f"data:image/png;base64,{base64.b64encode(buffer_hm).decode('utf-8')}"

            _, buffer_ov = cv2.imencode('.png', cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
            ov_b64 = f"data:image/png;base64,{base64.b64encode(buffer_ov).decode('utf-8')}"

            result["localization"] = {
                "heatmap": heatmap,
                "overlay_rgb": overlay,
                "heatmap_base64": hm_b64,
                "overlay_base64": ov_b64,
                "bounding_boxes": bboxes,
                "defect_area_percentage": defect_area_pct,
            }

        inference_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        result["inference_time_ms"] = inference_time_ms
        return result

    def predict_batch(
        self,
        image_inputs: List[Union[str, Image.Image, np.ndarray]],
        include_heatmaps: bool = False,
    ) -> Dict[str, Any]:
        """
        Infers defect predictions across a list of images.
        """
        t0 = time.perf_counter()
        results = []
        counts = {cls_name: 0 for cls_name in CLASSES}
        uncertain_count = 0

        for img in image_inputs:
            res = self.predict_single(img, include_heatmap=include_heatmaps)
            cls_name = res["prediction"]["class"]
            counts[cls_name] += 1
            if res["uncertainty"]["is_uncertain"]:
                uncertain_count += 1
            results.append(res)

        total = len(image_inputs)
        normal_count = counts.get("normal", 0)
        defective_count = total - normal_count

        total_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        return {
            "total_images": total,
            "summary": {
                "normal": normal_count,
                "defective": defective_count,
                "defect_rate_pct": round((defective_count / max(1, total)) * 100.0, 2),
                "uncertain": uncertain_count,
                "breakdown": counts,
            },
            "results": results,
            "batch_processing_time_ms": total_time_ms,
        }
