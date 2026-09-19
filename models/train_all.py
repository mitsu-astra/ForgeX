"""
Unified Training Pipeline Orchestrator
Executes training and evaluation for Vision, Process, and Root-Cause Correlation models.
"""

import os
import sys
import time
import json

# Add root directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.vision.train import train_vision_model
from models.vision.evaluate import run_full_evaluation
from models.process.train import train_process_models
from models.correlation.train import train_correlation_model


def run_full_training_pipeline(
    vision_epochs: int = 5,
    batch_size: int = 32,
    save_dir: str = "/home/koushik_2109/Hackathons/CMR/models/weights",
):
    print("=" * 80)
    print(" INDUSTRIAL AI DECISION INTELLIGENCE - FULL MODEL TRAINING PIPELINE")
    print(" NEURAX Hackathon 3.0 - Domain 2: AI in Industry and Automation")
    print("=" * 80)

    total_start = time.time()
    os.makedirs(save_dir, exist_ok=True)

    # 1. PROCESS SURROGATE MODEL
    print("\n" + "#" * 60)
    print(" STAGE 1: Training Manufacturing Process Surrogate Models")
    print("#" * 60)
    process_results = train_process_models(save_dir=save_dir)

    # 2. CORRELATION & ROOT-CAUSE MODEL
    print("\n" + "#" * 60)
    print(" STAGE 2: Training Root Cause Classifier & SHAP Explainer")
    print("#" * 60)
    correlation_results = train_correlation_model(save_dir=save_dir)

    # 3. VISION DEFECT CLASSIFIER MODEL
    print("\n" + "#" * 60)
    print(" STAGE 3: Training EfficientNet-B4 Defect Classifier")
    print("#" * 60)
    vision_train_results = train_vision_model(
        data_dir="/home/koushik_2109/Hackathons/CMR/train",
        save_dir=save_dir,
        epochs=vision_epochs,
        batch_size=batch_size,
    )

    # 4. COMPREHENSIVE VISION BENCHMARKING
    print("\n" + "#" * 60)
    print(" STAGE 4: Evaluating Vision Model & Latency Benchmarks")
    print("#" * 60)
    vision_eval_results = run_full_evaluation(
        data_dir="/home/koushik_2109/Hackathons/CMR/train",
        weights_path=os.path.join(save_dir, "efficientnet_b4_defect.pth"),
        batch_size=batch_size,
    )

    # Save summary report
    summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_pipeline_time_minutes": round((time.time() - total_start) / 60.0, 2),
        "vision_model": {
            "architecture": "EfficientNet-B4 (Pretrained ImageNet)",
            "test_accuracy": vision_eval_results["overall"]["accuracy"],
            "test_macro_f1": vision_eval_results["overall"]["macro_f1"],
            "latency_ms": vision_eval_results["latency_benchmark"]["single_image_avg_ms"],
            "throughput_fps": vision_eval_results["latency_benchmark"]["throughput_images_per_sec"],
        },
        "process_model": {
            "architecture": "XGBoost Regressors",
            "model_1_r2": process_results.get("model_1", {}).get("metrics", {}),
        },
        "correlation_model": {
            "architecture": "XGBoost + SHAP TreeExplainer",
            "test_accuracy": correlation_results["test_accuracy"],
            "test_macro_f1": correlation_results["test_macro_f1"],
        },
    }

    summary_path = os.path.join(save_dir, "training_pipeline_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 80)
    print(" TRAINING PIPELINE SUCCESSFULLY COMPLETED")
    print(f" Summary Report saved to: {summary_path}")
    print(f" Total time: {summary['total_pipeline_time_minutes']} minutes")
    print(f" Vision Accuracy: {summary['vision_model']['test_accuracy']*100:.2f}% | Latency: {summary['vision_model']['latency_ms']} ms")
    print(f" Correlation Accuracy: {summary['correlation_model']['test_accuracy']*100:.2f}%")
    print("=" * 80)


if __name__ == "__main__":
    run_full_training_pipeline()
