"""
Comprehensive Evaluation & Latency Benchmarking for Vision Model
Generates confusion matrix, per-class metrics, uncertainty distributions, and speed benchmarks.
"""

import os
import sys
import time
import json
from typing import Dict, Any, List
import numpy as np
import torch
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

# Ensure root directory in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.vision.dataset import get_dataloaders, CLASSES, CLASS_TO_IDX
from models.vision.model import DefectClassifier


def run_full_evaluation(
    data_dir: str = "/home/koushik_2109/Hackathons/CMR/train",
    weights_path: str = "/home/koushik_2109/Hackathons/CMR/models/weights/efficientnet_b4_defect.pth",
    batch_size: int = 32,
    device_name: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> Dict[str, Any]:
    """
    Runs complete evaluation on the test set.
    """
    device = torch.device(device_name)
    print(f"[*] Loading model from {weights_path} onto {device}...")

    model = DefectClassifier.load_checkpoint(weights_path, device=device)
    model.eval()

    _, _, test_loader, counts = get_dataloaders(
        data_dir=data_dir,
        batch_size=batch_size,
        num_workers=4,
    )

    all_preds: List[int] = []
    all_targets: List[int] = []
    all_probs: List[np.ndarray] = []
    all_uncertainties: List[float] = []

    print("[*] Running inference on test split (with Monte Carlo Dropout uncertainty)...")
    with torch.no_grad():
        for images, labels, _ in test_loader:
            images = images.to(device)
            # MC Dropout inference (5 samples for evaluation speed)
            mean_probs, preds, uncertainties = model.predict_with_uncertainty(images, n_samples=5)

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(labels.numpy())
            all_probs.append(mean_probs.cpu().numpy())
            all_uncertainties.extend(uncertainties.cpu().numpy())

    all_probs_arr = np.concatenate(all_probs, axis=0)
    all_preds_arr = np.array(all_preds)
    all_targets_arr = np.array(all_targets)
    all_unc_arr = np.array(all_uncertainties)

    # Metrics
    acc = float(accuracy_score(all_targets_arr, all_preds_arr))
    macro_f1 = float(f1_score(all_targets_arr, all_preds_arr, average="macro"))
    weighted_f1 = float(f1_score(all_targets_arr, all_preds_arr, average="weighted"))

    report = classification_report(
        all_targets_arr,
        all_preds_arr,
        target_names=CLASSES,
        output_dict=True,
        zero_division=0,
    )
    conf_matrix = confusion_matrix(all_targets_arr, all_preds_arr).tolist()

    # Latency Benchmark
    print("[*] Benchmarking inference latency...")
    if device.type == "cuda":
        torch.cuda.empty_cache()

    with torch.no_grad():
        dummy_input = torch.randn(1, 3, 224, 224, device=device)
        # Warmup
        for _ in range(10):
            _ = model(dummy_input)

        # Single-image latency
        single_latencies = []
        for _ in range(50):
            t0 = time.perf_counter()
            _ = model(dummy_input)
            if device.type == "cuda":
                torch.cuda.synchronize()
            single_latencies.append((time.perf_counter() - t0) * 1000.0)

        avg_single_latency_ms = float(np.mean(single_latencies))
        p95_single_latency_ms = float(np.percentile(single_latencies, 95))

        # Batch throughput (batch_size=16)
        bench_bs = 16
        dummy_batch = torch.randn(bench_bs, 3, 224, 224, device=device)
        batch_latencies = []
        for _ in range(20):
            t0 = time.perf_counter()
            _ = model(dummy_batch)
            if device.type == "cuda":
                torch.cuda.synchronize()
            batch_latencies.append(time.perf_counter() - t0)

        avg_batch_time_sec = float(np.mean(batch_latencies))
        throughput_fps = float(bench_bs / avg_batch_time_sec)

    results = {
        "overall": {
            "accuracy": round(acc, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "total_test_samples": len(all_targets_arr),
        },
        "per_class": {
            cls: {
                "precision": round(report[cls]["precision"], 4),
                "recall": round(report[cls]["recall"], 4),
                "f1_score": round(report[cls]["f1-score"], 4),
                "support": report[cls]["support"],
            }
            for cls in CLASSES
        },
        "confusion_matrix": conf_matrix,
        "classes": CLASSES,
        "uncertainty": {
            "mean_uncertainty": round(float(np.mean(all_unc_arr)), 4),
            "median_uncertainty": round(float(np.median(all_unc_arr)), 4),
            "p90_uncertainty": round(float(np.percentile(all_unc_arr, 90)), 4),
        },
        "latency_benchmark": {
            "single_image_avg_ms": round(avg_single_latency_ms, 2),
            "single_image_p95_ms": round(p95_single_latency_ms, 2),
            "throughput_images_per_sec": round(throughput_fps, 1),
            "device": str(device),
        },
    }

    return results


if __name__ == "__main__":
    metrics = run_full_evaluation()
    print(json.dumps(metrics, indent=2))
