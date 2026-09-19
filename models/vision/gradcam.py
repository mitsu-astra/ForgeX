"""
Grad-CAM (Gradient-weighted Class Activation Mapping) & Defect Localization
Generates spatial heatmaps and bounding boxes for visual defect explainability.
"""

from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F


class GradCAM:
    """
    Grad-CAM engine for convolutional defect classifiers.
    """

    def __init__(self, model: nn.Module, target_layer: Optional[nn.Module] = None):
        self.model = model
        self.target_layer = target_layer if target_layer is not None else getattr(model, "target_layer", None)
        if self.target_layer is None:
            # Default to last convolutional module in features
            self.target_layer = model.features[-1]

        self.activations: Optional[torch.Tensor] = None
        self.gradients: Optional[torch.Tensor] = None
        self.hooks = []
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        h1 = self.target_layer.register_forward_hook(forward_hook)
        h2 = self.target_layer.register_full_backward_hook(backward_hook)
        self.hooks = [h1, h2]

    def remove_hooks(self):
        for hook in self.hooks:
            hook.remove()

    def generate_heatmap(
        self,
        image_tensor: torch.Tensor,
        target_class: Optional[int] = None,
    ) -> np.ndarray:
        """
        Computes Grad-CAM activation heatmap for a single image tensor.

        Args:
            image_tensor: Tensor of shape [1, 3, H, W]
            target_class: Target class index. If None, uses top predicted class.

        Returns:
            heatmap: 2D numpy array [H, W] normalized to [0, 1]
        """
        self.model.eval()
        self.model.zero_grad()

        # Ensure batch dimension
        if image_tensor.dim() == 3:
            image_tensor = image_tensor.unsqueeze(0)

        image_tensor = image_tensor.requires_grad_(True)
        logits = self.model(image_tensor)

        if target_class is None:
            target_class = torch.argmax(logits, dim=1).item()

        target_score = logits[0, target_class]
        target_score.backward(retain_graph=True)

        if self.gradients is None or self.activations is None:
            raise RuntimeError("Gradients or activations not captured by GradCAM hooks.")

        # α_k = Global average pooling of gradients
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)  # [1, C, 1, 1]

        # L_CAM = ReLU(Σ α_k * A_k)
        cam = torch.sum(weights * self.activations, dim=1, keepdim=True)  # [1, 1, H', W']
        cam = F.relu(cam)

        # Upsample to image size
        cam = F.interpolate(
            cam,
            size=(image_tensor.shape[2], image_tensor.shape[3]),
            mode="bilinear",
            align_corners=False,
        )

        cam_np = cam.squeeze().cpu().numpy()

        # Min-max normalization
        min_val, max_val = np.min(cam_np), np.max(cam_np)
        if max_val - min_val > 1e-8:
            cam_np = (cam_np - min_val) / (max_val - min_val)
        else:
            cam_np = np.zeros_like(cam_np)

        return cam_np

    def overlay_heatmap(
        self,
        original_img: np.ndarray,
        heatmap: np.ndarray,
        alpha: float = 0.5,
        colormap: int = cv2.COLORMAP_JET,
    ) -> np.ndarray:
        """
        Overlays heatmap on top of original BGR or RGB image.

        Args:
            original_img: uint8 image [H, W, 3] in RGB
            heatmap: float32 heatmap [H, W] in range [0, 1]
            alpha: Heatmap blend weight

        Returns:
            overlay: uint8 RGB image [H, W, 3]
        """
        # Resize heatmap to match image dimensions
        h, w = original_img.shape[:2]
        heatmap_resized = cv2.resize(heatmap, (w, h))

        # Convert heatmap to uint8 colormap
        heatmap_uint8 = np.uint8(255 * heatmap_resized)
        heatmap_color = cv2.applyColorMap(heatmap_uint8, colormap)
        # OpenCV applyColorMap produces BGR, convert to RGB
        heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

        # Blend
        blended = np.clip(
            (1.0 - alpha) * original_img.astype(np.float32) + alpha * heatmap_color.astype(np.float32),
            0,
            255,
        ).astype(np.uint8)

        return blended

    def extract_bounding_boxes(
        self,
        heatmap: np.ndarray,
        threshold: float = 0.45,
        min_area_ratio: float = 0.01,
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Extracts bounding boxes around high-activation regions in the heatmap.

        Args:
            heatmap: 2D numpy array [H, W] in [0, 1]
            threshold: Activation threshold for binarization (0.0 - 1.0)
            min_area_ratio: Minimum box area relative to image area to filter noise

        Returns:
            bboxes: List of bounding box dicts {'x', 'y', 'width', 'height', 'confidence'}
            defect_area_pct: Total defect area as percentage of image area
        """
        h, w = heatmap.shape
        total_area = h * w

        # Threshold to create binary mask
        binary_mask = (heatmap >= threshold).astype(np.uint8) * 255

        # Morphological opening to remove small artifacts
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        cleaned_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        bboxes = []
        defect_pixels = np.count_nonzero(cleaned_mask)
        defect_area_pct = round((defect_pixels / total_area) * 100.0, 2)

        for idx, cnt in enumerate(contours, start=1):
            x, y, bw, bh = cv2.boundingRect(cnt)
            box_area = bw * bh
            if box_area / total_area < min_area_ratio:
                continue

            # Confidence is the mean activation within the bounding box
            box_region = heatmap[y : y + bh, x : x + bw]
            box_conf = float(np.mean(box_region)) if box_region.size > 0 else 0.0

            bboxes.append({
                "bbox_id": idx,
                "x_min": int(x),
                "y_min": int(y),
                "x_max": int(x + bw),
                "y_max": int(y + bh),
                "x": int(x),
                "y": int(y),
                "width": int(bw),
                "height": int(bh),
                "area_pixels": int(box_area),
                "area_percentage": round((box_area / total_area) * 100.0, 2),
                "confidence": round(box_conf, 3),
            })

        # Sort by confidence descending
        bboxes = sorted(bboxes, key=lambda b: b["confidence"], reverse=True)

        return bboxes, defect_area_pct
