# Model Weights

Due to GitHub file size limits, the large EfficientNet-B4 PyTorch checkpoint is not stored in this repository.

## Files NOT included in git (too large)
- `efficientnet_b4_defect.pth` — 71 MB (EfficientNet-B4 trained defect classifier)
- `efficientnet_b4_defect_snapshot.pth` — 71 MB (training snapshot)

## Files included
- `xgboost_correlation.pkl` — XGBoost Root Cause Classifier
- `xgboost_process.pkl` — XGBoost Process Surrogate Model
- `vision_metrics.json` — Training metrics for vision model
- `correlation_metrics.json` — Training metrics for correlation model
- `process_metrics.json` — Training metrics for process model

## How to get model weights
Train locally using:
```bash
# Vision model (EfficientNet-B4)
python train_vision_local.py

# Process + Correlation models
python train_process_and_correlation_local.py
```

Or contact the team for a direct download link to the pre-trained checkpoint.
