"""
Training Pipeline for Industrial Defect Visual Inspection Model
Trains EfficientNet-B4 with AdamW, Cosine Annealing, AMP, and Checkpointing.
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Ensure root directory in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.vision.dataset import get_dataloaders, CLASSES
from models.vision.model import DefectClassifier


def train_one_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: torch.amp.GradScaler,
    device: torch.device,
    use_amp: bool = True,
) -> Tuple[float, float]:
    model.train()
    total_loss = 0.0
    all_preds: List[int] = []
    all_targets: List[int] = []

    for images, labels, _ in dataloader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        if use_amp and device.type == "cuda":
            with torch.amp.autocast('cuda'):
                logits = model(images)
                loss = criterion(logits, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

        total_loss += loss.item() * images.size(0)
        preds = torch.argmax(logits, dim=1).detach().cpu().numpy()
        all_preds.extend(preds)
        all_targets.extend(labels.cpu().numpy())

    epoch_loss = total_loss / len(dataloader.dataset)
    epoch_acc = accuracy_score(all_targets, all_preds)
    return epoch_loss, float(epoch_acc)


def evaluate(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Dict[str, float]:
    model.eval()
    total_loss = 0.0
    all_preds: List[int] = []
    all_targets: List[int] = []

    with torch.no_grad():
        for images, labels, _ in dataloader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            logits = model(images)
            loss = criterion(logits, labels)

            total_loss += loss.item() * images.size(0)
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_targets.extend(labels.cpu().numpy())

    val_loss = total_loss / len(dataloader.dataset)
    val_acc = float(accuracy_score(all_targets, all_preds))
    val_f1 = float(f1_score(all_targets, all_preds, average="macro"))
    val_prec = float(precision_score(all_targets, all_preds, average="macro", zero_division=0))
    val_rec = float(recall_score(all_targets, all_preds, average="macro", zero_division=0))

    return {
        "loss": float(val_loss),
        "accuracy": val_acc,
        "f1_macro": val_f1,
        "precision_macro": val_prec,
        "recall_macro": val_rec,
    }


def train_vision_model(
    data_dir: str = "/home/koushik_2109/Hackathons/CMR/train",
    save_dir: str = "/home/koushik_2109/Hackathons/CMR/models/weights",
    epochs: int = 15,
    batch_size: int = 32,
    lr: float = 1e-4,
    weight_decay: float = 1e-4,
    num_workers: int = 4,
    early_stopping_patience: int = 5,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Main training function for the visual defect classifier.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training Vision Model on device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    os.makedirs(save_dir, exist_ok=True)
    checkpoint_path = os.path.join(save_dir, "efficientnet_b4_defect.pth")
    metrics_path = os.path.join(save_dir, "vision_metrics.json")

    # Load data
    train_loader, val_loader, test_loader, counts = get_dataloaders(
        data_dir=data_dir,
        batch_size=batch_size,
        num_workers=num_workers,
        seed=seed,
    )
    print(f"[*] Dataset breakdown: {counts}")
    print(f"[*] Splits - Train: {len(train_loader.dataset)}, Val: {len(val_loader.dataset)}, Test: {len(test_loader.dataset)}")

    # Initialize model
    model = DefectClassifier(num_classes=len(CLASSES), pretrained=True)
    model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    scaler = torch.amp.GradScaler('cuda', enabled=(device.type == "cuda"))

    best_val_f1 = 0.0
    best_val_acc = 0.0
    patience_counter = 0
    history: List[Dict[str, Any]] = []

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        train_loss, train_acc = train_one_epoch(
            model=model,
            dataloader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            scaler=scaler,
            device=device,
            use_amp=True,
        )

        val_metrics = evaluate(
            model=model,
            dataloader=val_loader,
            criterion=criterion,
            device=device,
        )

        scheduler.step()
        epoch_duration = time.time() - epoch_start

        epoch_record = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_metrics["loss"], 4),
            "val_acc": round(val_metrics["accuracy"], 4),
            "val_f1": round(val_metrics["f1_macro"], 4),
            "lr": round(optimizer.param_groups[0]["lr"], 6),
            "duration_sec": round(epoch_duration, 1),
        }
        history.append(epoch_record)

        print(
            f"Epoch [{epoch:02d}/{epochs:02d}] "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.2f}% | "
            f"Val Loss: {val_metrics['loss']:.4f} | Val Acc: {val_metrics['accuracy']*100:.2f}% | "
            f"Val F1: {val_metrics['f1_macro']*100:.2f}% | Time: {epoch_duration:.1f}s"
        )

        # Save best model
        if val_metrics["f1_macro"] > best_val_f1:
            best_val_f1 = val_metrics["f1_macro"]
            best_val_acc = val_metrics["accuracy"]
            patience_counter = 0
            model.save_checkpoint(
                checkpoint_path,
                metadata={
                    "epoch": epoch,
                    "val_accuracy": best_val_acc,
                    "val_f1_macro": best_val_f1,
                    "classes": CLASSES,
                },
            )
            print(f"  --> Saved new best checkpoint to {checkpoint_path} (Val F1: {best_val_f1*100:.2f}%)")
        else:
            patience_counter += 1
            if patience_counter >= early_stopping_patience:
                print(f"[*] Early stopping triggered after {epoch} epochs (patience={early_stopping_patience}).")
                break

    total_time = time.time() - start_time
    print(f"[*] Training complete in {total_time/60:.2f} minutes.")

    # Evaluate best model on test set
    best_model = DefectClassifier.load_checkpoint(checkpoint_path, device=device)
    test_metrics = evaluate(best_model, test_loader, criterion, device)
    print(f"[*] Final Test Set Performance:")
    print(f"    - Accuracy: {test_metrics['accuracy']*100:.2f}%")
    print(f"    - Macro F1: {test_metrics['f1_macro']*100:.2f}%")
    print(f"    - Precision: {test_metrics['precision_macro']*100:.2f}%")
    print(f"    - Recall: {test_metrics['recall_macro']*100:.2f}%")

    final_results = {
        "model_architecture": "EfficientNet-B4",
        "num_classes": len(CLASSES),
        "classes": CLASSES,
        "best_val_accuracy": round(best_val_acc, 4),
        "best_val_f1": round(best_val_f1, 4),
        "test_metrics": {k: round(v, 4) for k, v in test_metrics.items()},
        "total_training_time_sec": round(total_time, 1),
        "history": history,
        "checkpoint_path": checkpoint_path,
    }

    with open(metrics_path, "w") as f:
        json.dump(final_results, f, indent=2)

    return final_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Defect Classifier")
    parser.add_argument("--epochs", type=int, default=12, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()

    train_vision_model(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr)
