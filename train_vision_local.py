"""
Local Vision Model Training Script
Trains EfficientNet-B4 defect classifier on the train/ folder using Apple MPS or CPU.
Adapted for local Mac execution from the existing models/vision pipeline.
"""

# Fix SSL certificate verification on macOS Python installations
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import os
import sys
import time
import json
import glob
from typing import Tuple, List, Dict, Any, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from PIL import Image

# ============================================================
# Configuration
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "train")
SAVE_DIR = os.path.join(SCRIPT_DIR, "models", "weights")
CLASSES = ["crack", "hole", "normal", "rust", "scratch"]
CLASS_TO_IDX = {cls_name: i for i, cls_name in enumerate(CLASSES)}
NUM_CLASSES = len(CLASSES)

# ImageNet normalization
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Training hyperparameters
EPOCHS = 10
BATCH_SIZE = 16  # Smaller batch for Mac memory
LR = 1e-4
WEIGHT_DECAY = 1e-4
IMG_SIZE = 224
SEED = 42
EARLY_STOPPING_PATIENCE = 5
NUM_WORKERS = 0  # 0 for macOS compatibility (avoids multiprocessing issues)


# ============================================================
# Dataset
# ============================================================
class DefectDataset(Dataset):
    def __init__(self, samples: List[Tuple[str, int]], transform=None):
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        with Image.open(path) as img:
            img_rgb = img.convert("RGB")
        if self.transform:
            tensor = self.transform(img_rgb)
        else:
            tensor = transforms.ToTensor()(img_rgb)
        return tensor, label


def build_datasets():
    """Scan train/ directory, create stratified train/val/test splits."""
    all_samples = []
    class_counts = {}

    for cls_name in CLASSES:
        cls_dir = os.path.join(DATA_DIR, cls_name)
        if not os.path.isdir(cls_dir):
            print(f"  WARNING: Class directory not found: {cls_dir}")
            continue
        files = sorted(glob.glob(os.path.join(cls_dir, "*.png")))
        files += sorted(glob.glob(os.path.join(cls_dir, "*.jpg")))
        files += sorted(glob.glob(os.path.join(cls_dir, "*.jpeg")))
        files = sorted(list(set(files)))
        class_counts[cls_name] = len(files)
        for f in files:
            all_samples.append((f, CLASS_TO_IDX[cls_name]))

    print(f"  Total images found: {len(all_samples)}")
    for cls, cnt in class_counts.items():
        print(f"    {cls}: {cnt}")

    paths = [s[0] for s in all_samples]
    labels = [s[1] for s in all_samples]

    # 70% train, 15% val, 15% test (stratified)
    train_paths, rest_paths, train_labels, rest_labels = train_test_split(
        paths, labels, test_size=0.30, random_state=SEED, stratify=labels
    )
    val_paths, test_paths, val_labels, test_labels = train_test_split(
        rest_paths, rest_labels, test_size=0.50, random_state=SEED, stratify=rest_labels
    )

    # Transforms
    train_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])
    val_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    train_ds = DefectDataset(list(zip(train_paths, train_labels)), transform=train_transform)
    val_ds = DefectDataset(list(zip(val_paths, val_labels)), transform=val_transform)
    test_ds = DefectDataset(list(zip(test_paths, test_labels)), transform=val_transform)

    return train_ds, val_ds, test_ds, class_counts


# ============================================================
# Model
# ============================================================
class DefectClassifier(nn.Module):
    def __init__(self, num_classes=NUM_CLASSES, pretrained=True):
        super().__init__()
        self.num_classes = num_classes
        if pretrained:
            weights = models.EfficientNet_B4_Weights.DEFAULT
            backbone = models.efficientnet_b4(weights=weights)
        else:
            backbone = models.efficientnet_b4(weights=None)

        self.features = backbone.features
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        in_features = backbone.classifier[1].in_features  # 1792

        self.dropout1 = nn.Dropout(p=0.3)
        self.fc1 = nn.Linear(in_features, 512)
        self.relu = nn.ReLU(inplace=True)
        self.dropout2 = nn.Dropout(p=0.2)
        self.fc2 = nn.Linear(512, num_classes)

        self.target_layer = self.features[-1]

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout1(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout2(x)
        return self.fc2(x)


# ============================================================
# Training Loop
# ============================================================
def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    all_preds, all_targets = [], []

    for batch_idx, (images, labels) in enumerate(loader):
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        preds = torch.argmax(logits, dim=1).detach().cpu().numpy()
        all_preds.extend(preds)
        all_targets.extend(labels.cpu().numpy())

        if (batch_idx + 1) % 50 == 0:
            print(f"    Batch {batch_idx+1}/{len(loader)} | Loss: {loss.item():.4f}")

    epoch_loss = total_loss / len(loader.dataset)
    epoch_acc = accuracy_score(all_targets, all_preds)
    return epoch_loss, float(epoch_acc)


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    all_preds, all_targets = [], []

    for images, labels in loader:
        images = images.to(device)
        labels = labels.to(device)
        logits = model(images)
        loss = criterion(logits, labels)

        total_loss += loss.item() * images.size(0)
        preds = torch.argmax(logits, dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_targets.extend(labels.cpu().numpy())

    return {
        "loss": total_loss / len(loader.dataset),
        "accuracy": float(accuracy_score(all_targets, all_preds)),
        "f1_macro": float(f1_score(all_targets, all_preds, average="macro")),
        "precision_macro": float(precision_score(all_targets, all_preds, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(all_targets, all_preds, average="macro", zero_division=0)),
        "all_preds": all_preds,
        "all_targets": all_targets,
    }


def main():
    print("=" * 70)
    print("  DEFECT CLASSIFIER TRAINING — EfficientNet-B4")
    print("  NEURAX Hackathon 3.0 — AI in Industry and Automation")
    print("=" * 70)

    torch.manual_seed(SEED)
    np.random.seed(SEED)

    # Select device: MPS (Apple Silicon) > CUDA > CPU
    if torch.cuda.is_available():
        device = torch.device("cuda")
        device_name = torch.cuda.get_device_name(0)
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        device_name = "Apple MPS (Metal)"
    else:
        device = torch.device("cpu")
        device_name = "CPU"

    print(f"\n[*] Device: {device} ({device_name})")
    print(f"[*] Data directory: {DATA_DIR}")
    print(f"[*] Save directory: {SAVE_DIR}")
    print(f"[*] Epochs: {EPOCHS}, Batch Size: {BATCH_SIZE}, LR: {LR}")

    os.makedirs(SAVE_DIR, exist_ok=True)
    checkpoint_path = os.path.join(SAVE_DIR, "efficientnet_b4_defect.pth")
    metrics_path = os.path.join(SAVE_DIR, "vision_metrics.json")

    # Build datasets
    print("\n[1/4] Loading and splitting dataset...")
    train_ds, val_ds, test_ds, class_counts = build_datasets()
    print(f"  Train: {len(train_ds)} | Val: {len(val_ds)} | Test: {len(test_ds)}")

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=False)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=False)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=False)

    # Initialize model
    print("\n[2/4] Initializing EfficientNet-B4 (ImageNet pretrained)...")
    model = DefectClassifier(num_classes=NUM_CLASSES, pretrained=True)
    model.to(device)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Total parameters: {total_params:,}")
    print(f"  Trainable parameters: {trainable_params:,}")

    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)
    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=1e-6)

    # Training loop
    print(f"\n[3/4] Training for {EPOCHS} epochs...\n")
    best_val_f1 = 0.0
    best_val_acc = 0.0
    patience_counter = 0
    history = []
    start_time = time.time()

    for epoch in range(1, EPOCHS + 1):
        epoch_start = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_metrics = evaluate(model, val_loader, criterion, device)
        scheduler.step()
        epoch_duration = time.time() - epoch_start

        record = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_metrics["loss"], 4),
            "val_acc": round(val_metrics["accuracy"], 4),
            "val_f1": round(val_metrics["f1_macro"], 4),
            "lr": round(optimizer.param_groups[0]["lr"], 6),
            "duration_sec": round(epoch_duration, 1),
        }
        history.append(record)

        print(
            f"Epoch [{epoch:02d}/{EPOCHS:02d}] "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.2f}% | "
            f"Val Loss: {val_metrics['loss']:.4f} | Val Acc: {val_metrics['accuracy']*100:.2f}% | "
            f"Val F1: {val_metrics['f1_macro']*100:.2f}% | "
            f"Time: {epoch_duration:.1f}s"
        )

        # Save best model
        if val_metrics["f1_macro"] > best_val_f1:
            best_val_f1 = val_metrics["f1_macro"]
            best_val_acc = val_metrics["accuracy"]
            patience_counter = 0
            checkpoint = {
                "state_dict": model.state_dict(),
                "num_classes": NUM_CLASSES,
                "metadata": {
                    "epoch": epoch,
                    "val_accuracy": best_val_acc,
                    "val_f1_macro": best_val_f1,
                    "classes": CLASSES,
                },
            }
            torch.save(checkpoint, checkpoint_path)
            print(f"  --> Saved best checkpoint (Val F1: {best_val_f1*100:.2f}%)")
        else:
            patience_counter += 1
            if patience_counter >= EARLY_STOPPING_PATIENCE:
                print(f"\n[*] Early stopping after {epoch} epochs (patience={EARLY_STOPPING_PATIENCE})")
                break

    total_time = time.time() - start_time
    print(f"\n[*] Training complete in {total_time/60:.1f} minutes.")

    # Final test evaluation
    print("\n[4/4] Evaluating best model on test set...")
    best_checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(best_checkpoint["state_dict"])
    model.to(device)

    test_metrics = evaluate(model, test_loader, criterion, device)

    print(f"\n{'='*70}")
    print(f"  FINAL TEST SET RESULTS")
    print(f"{'='*70}")
    print(f"  Accuracy:  {test_metrics['accuracy']*100:.2f}%")
    print(f"  Macro F1:  {test_metrics['f1_macro']*100:.2f}%")
    print(f"  Precision: {test_metrics['precision_macro']*100:.2f}%")
    print(f"  Recall:    {test_metrics['recall_macro']*100:.2f}%")
    print(f"  Loss:      {test_metrics['loss']:.4f}")
    print(f"{'='*70}")

    # Per-class accuracy
    preds_arr = np.array(test_metrics["all_preds"])
    targets_arr = np.array(test_metrics["all_targets"])
    print("\n  Per-Class Accuracy:")
    for cls_idx, cls_name in enumerate(CLASSES):
        mask = targets_arr == cls_idx
        if mask.sum() > 0:
            cls_acc = (preds_arr[mask] == cls_idx).mean()
            print(f"    {cls_name:>10}: {cls_acc*100:.2f}% ({mask.sum()} samples)")

    # Save metrics
    final_results = {
        "model_architecture": "EfficientNet-B4",
        "num_classes": NUM_CLASSES,
        "classes": CLASSES,
        "device": str(device),
        "best_val_accuracy": round(best_val_acc, 4),
        "best_val_f1": round(best_val_f1, 4),
        "test_metrics": {
            "loss": round(test_metrics["loss"], 4),
            "accuracy": round(test_metrics["accuracy"], 4),
            "f1_macro": round(test_metrics["f1_macro"], 4),
            "precision_macro": round(test_metrics["precision_macro"], 4),
            "recall_macro": round(test_metrics["recall_macro"], 4),
        },
        "total_training_time_sec": round(total_time, 1),
        "history": history,
        "checkpoint_path": checkpoint_path,
    }
    with open(metrics_path, "w") as f:
        json.dump(final_results, f, indent=2)
    print(f"\n[*] Metrics saved to: {metrics_path}")
    print(f"[*] Model saved to:   {checkpoint_path}")
    print(f"\nDone!")


if __name__ == "__main__":
    main()
