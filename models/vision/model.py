"""
Vision Model Architecture for Industrial Visual Inspection
EfficientNet-B4 Classifier with MC Dropout for Uncertainty Quantification.
"""

import os
from typing import Tuple, Dict, Any, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models

CLASSES = ["crack", "hole", "normal", "rust", "scratch"]
NUM_CLASSES = len(CLASSES)


class DefectClassifier(nn.Module):
    """
    EfficientNet-B4 based industrial defect classification model.
    Includes Monte Carlo Dropout support for epistemic uncertainty quantification.
    """

    def __init__(
        self,
        num_classes: int = NUM_CLASSES,
        pretrained: bool = True,
        dropout_rate_1: float = 0.3,
        dropout_rate_2: float = 0.2,
        hidden_dim: int = 512,
    ):
        super().__init__()
        self.num_classes = num_classes

        # Load EfficientNet-B4 backbone
        if pretrained:
            weights = models.EfficientNet_B4_Weights.DEFAULT
            backbone = models.efficientnet_b4(weights=weights)
        else:
            backbone = models.efficientnet_b4(weights=None)

        # Feature extractor: keep all convolutional layers
        self.features = backbone.features
        self.avgpool = nn.AdaptiveAvgPool2d(1)

        # Get in_features from backbone classifier
        in_features = backbone.classifier[1].in_features  # 1792 for EfficientNet-B4

        # Custom Head with two-stage Dropout
        self.dropout1 = nn.Dropout(p=dropout_rate_1)
        self.fc1 = nn.Linear(in_features, hidden_dim)
        self.relu = nn.ReLU(inplace=True)
        self.dropout2 = nn.Dropout(p=dropout_rate_2)
        self.fc2 = nn.Linear(hidden_dim, num_classes)

        # Save target layer reference for Grad-CAM
        self.target_layer = self.features[-1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Standard forward pass returning class logits.
        """
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout1(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout2(x)
        logits = self.fc2(x)
        return logits

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extract spatial feature maps before pooling (for Grad-CAM).
        """
        return self.features(x)

    def predict_probabilities(self, x: torch.Tensor) -> torch.Tensor:
        """
        Returns softmax probabilities.
        """
        logits = self.forward(x)
        return F.softmax(logits, dim=1)

    def predict_with_uncertainty(
        self, x: torch.Tensor, n_samples: int = 20
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Monte Carlo Dropout inference:
        Forces dropout layers to stay active during eval to estimate predictive uncertainty.

        Returns:
            mean_probs: Mean softmax probability vector [batch_size, num_classes]
            predictions: Predicted class indices [batch_size]
            uncertainty: Standard deviation across MC samples (epistemic uncertainty) [batch_size]
        """
        self.eval()

        # Temporarily enable dropout modules
        def enable_mc_dropout(m):
            if type(m) == nn.Dropout:
                m.train()

        self.apply(enable_mc_dropout)

        mc_probs = []
        with torch.no_grad():
            for _ in range(n_samples):
                logits = self.forward(x)
                probs = F.softmax(logits, dim=1)
                mc_probs.append(probs.unsqueeze(0))

        # Shape: [n_samples, batch_size, num_classes]
        mc_probs = torch.cat(mc_probs, dim=0)

        # Mean and standard deviation across MC samples
        mean_probs = mc_probs.mean(dim=0)
        std_probs = mc_probs.std(dim=0)

        predictions = torch.argmax(mean_probs, dim=1)
        # Epistemic uncertainty = mean standard deviation across class probabilities
        uncertainty = std_probs.mean(dim=1)

        # Reset model to standard eval mode
        self.eval()

        return mean_probs, predictions, uncertainty

    def save_checkpoint(self, path: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Saves model weights and training metadata.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        checkpoint = {
            "state_dict": self.state_dict(),
            "num_classes": self.num_classes,
            "metadata": metadata or {},
        }
        torch.save(checkpoint, path)

    @classmethod
    def load_checkpoint(cls, path: str, device: torch.device = torch.device("cpu")) -> "DefectClassifier":
        """
        Loads model instance from saved checkpoint.
        """
        checkpoint = torch.load(path, map_location=device, weights_only=False)
        num_classes = checkpoint.get("num_classes", NUM_CLASSES)
        model = cls(num_classes=num_classes, pretrained=False)
        model.load_state_dict(checkpoint["state_dict"])
        model.to(device)
        model.eval()
        return model
