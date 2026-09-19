# Visual Inspection & Defect Root-Cause Assistant
### NEURAX Hackathon 3.0 - Domain 2: AI in Industry and Automation

---

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Objective](#objective)
3. [System Architecture](#system-architecture)
4. [Datasets](#datasets)
5. [Approach](#approach)
6. [Evaluation Criteria](#evaluation-criteria)
7. [Project Structure](#project-structure)
8. [Setup and Installation](#setup-and-installation)

---

## Problem Statement

High-throughput manufacturing lines are difficult to optimize because **product quality, process capacity, and economics interact**. Defect signatures can be subtle and easy to miss at production speed, while bottlenecks may emerge from:

- Cycle-time imbalance
- Excess work-in-process (WIP)
- Downtime and changeovers
- Low resource utilization
- Scrap or rework

The challenge demands a **multi-stage manufacturing environment** that handles:
- Mixed product variants
- Changing inspection conditions
- Recurring defect families
- Batch-to-batch process drift
- Varying station capacity

The objective is **NOT** to build another image classifier, generic labeling tool, or isolated KPI dashboard.

---

## Objective

Build a **software-only AI system** that analyzes organizer-provided inspection, production, and economic datasets to produce a **continuously updated view** of:

| Capability | Description |
|---|---|
| Quality Assessment | Classify units as acceptable or defective |
| Defect Localization | Localize defects where data supports it |
| Uncertainty Handling | Flag uncertain/novel defect types instead of forcing a guess |
| Bottleneck Detection | Identify industrial bottlenecks in production flow |
| Throughput Estimation | Estimate bottleneck effects on throughput and losses |
| Profitability Prediction | Predict profitability or margin impacts |
| Process Recommendations | Generate evidence-based process recommendations |

All recommendations, bottleneck interventions, and profitability estimates must remain **simulated or advisory**. No live camera feed, PLC connection, robotic sorting, or hardware access is required or permitted.

---

## System Architecture

The system follows a **unified multi-pipeline AI architecture** composed of four tightly integrated modules:

```
+-----------------------------------------------------------------------+
|                    NEURAX Visual Inspection System                    |
|                                                                       |
|  +-----------------+    +-----------------+                           |
|  |  Vision          |    |  Simulation      |                           |
|  |  Pipeline        |    |  Data Pipeline   |                           |
|  |                 |    |                 |                           |
|  | Image Ingestion  |    | Model 1 CSV     |                           |
|  | Preprocessing   |    | Model 2 CSV     |                           |
|  | Augmentation    |    | Model 3 CSV     |                           |
|  | CNN/ViT Model   |    | .mat Data       |                           |
|  | Defect Classify |    | Feature Extract |                           |
|  | Grad-CAM / SAM  |    | Time-series     |                           |
|  +-------+---------+    +-------+---------+                           |
|          |                      |                                     |
|          v                      v                                     |
|  +------------------------------------------+                        |
|  |       Root-Cause Correlation Engine       |                        |
|  |                                          |                        |
|  |  Defect <-> Process Parameter Mapping    |                        |
|  |  Statistical correlation (Spearman/PCA)  |                        |
|  |  Bottleneck detection (Little Law)       |                        |
|  |  Batch drift detection (CUSUM)           |                        |
|  |  Profitability / margin estimation       |                        |
|  |  Explainability (SHAP / attention maps)  |                        |
|  +-------------------+----------------------+                        |
|                      |                                               |
|                      v                                               |
|  +------------------------------------------+                        |
|  |    Decision-Support Dashboard (UI)        |                        |
|  |                                          |                        |
|  |  Real-time defect classification display |                        |
|  |  Heatmap / bounding-box overlay          |                        |
|  |  Bottleneck KPI cards                    |                        |
|  |  Root-cause evidence panel               |                        |
|  |  Profitability trend charts              |                        |
|  |  Process recommendation feed            |                        |
|  +------------------------------------------+                        |
+-----------------------------------------------------------------------+
```

### Data Flow

```
Raw Inspection Images          DES Simulation CSVs / .mat
       |                                |
       v                                v
 Vision Pipeline              Simulation Pipeline
 (EfficientNet-B4)            (Feature Engineering)
       |                                |
 Defect labels +               Process KPIs +
 Confidence scores             Bottleneck flags
       |                                |
       +----------> Root-Cause <--------+
                    Correlation Engine
                          |
            Process Recommendations +
            Profitability Estimates
                          |
                   Dashboard (UI)
```

### Module Breakdown

#### 1. Vision Pipeline
- **Input:** PNG images from five defect classes + normal
- **Preprocessing:** Normalization, CLAHE contrast enhancement, augmentation (flip, rotate, color jitter)
- **Model:** CNN backbone (EfficientNet-B4 / ResNet-50) + optionally a Vision Transformer (ViT) head
- **Output:** Per-image class probabilities + confidence score
- **Localization:** Grad-CAM heat maps + Segment Anything Model (SAM) for mask-level defect boundary detection
- **Uncertainty:** Monte Carlo Dropout / Deep Ensemble; unknown/novel defects flagged if max confidence falls below threshold

#### 2. Simulation Data Pipeline
- **Input:** Rockwell Arena DES outputs (Model 1/2/3 CSV files, 3000Samples.mat)
- **Processing:** Tabular feature engineering: utilization rates, queue lengths, WIP, cycle times, SKU breakdowns
- **Bottleneck Detection:** Utilization > 0.85 threshold, queue divergence, WIP-to-throughput ratio via Little's Law
- **Economic Model:** scrap/rework cost x defect rate + throughput loss x unit margin = estimated profitability delta

#### 3. Root-Cause Correlation Engine
- **Cross-domain linkage:** Batch ID aligns vision defect events to simulation process states
- **Correlation methods:** Spearman rank correlation, PCA to surface dominant process drivers
- **Drift Detection:** Sliding window comparison of defect rate per batch
- **Explainability:** SHAP values for tabular process features; attention maps for image decisions

#### 4. Decision-Support Dashboard
- Interactive web UI (Streamlit / Gradio / React)
- Defect image gallery with heatmap overlays
- KPI cards: OEE, throughput, yield rate, bottleneck station
- Root-cause waterfall chart
- Profitability scenario tool (what-if sliders)
- Process recommendation list with evidence citations

---

## Datasets

### Dataset 1: Surface Defect Image Dataset (train/)

A labelled image classification dataset with **5 defect classes + 1 normal class**, each containing **2,400 PNG images** (12,000 total).

| Class | Description | Image Count |
|---|---|---|
| crack | Surface crack defects | 2,400 |
| hole | Hole / puncture defects | 2,400 |
| rust | Rust / corrosion defects | 2,400 |
| scratch | Surface scratch defects | 2,400 |
| normal | Defect-free / acceptable units | 2,400 |
| **Total** | | **12,000** |

- **Format:** PNG, RGB
- **Naming convention:** class_NNNNN.png (e.g., crack_00042.png)

### Dataset 2: Manufacturing DES Simulation Data

Three progressively complex Rockwell Arena Discrete-Event Simulation (DES) models:

#### Model 1: Simple 3-Station Flow (10 Features)
Models a basic Drilling -> Milling -> Assembly production flow.

| Column | Description |
|---|---|
| Demand | Input demand rate |
| Total parts | Total parts produced |
| Parts per hour | Throughput |
| VA Time | Value-added time per part |
| Drilling/Milling/Assembly Waiting Time | Queue wait time per station |
| Drilling/Milling/Assembly Util | Station utilization (0-1) |

#### Model 2: Two-Part, Two-Stage Flow (16 Features)
Extends Model 1 with part type segmentation (Part 1 / Part 2), separate storage queues, and per-part WIP tracking across Drilling -> Assembly pipeline.

#### Model 3: Full Facility (77 Features)
Comprehensive multi-SKU (SKU 1-4), multi-station model including:

| Feature Group | Description |
|---|---|
| Utilization | Blanking, 4x Press cells, 4x Assembly cells, 2x Paint stations, Quality, Forklift |
| Queues | Station-level and warehouse-level queue lengths per SKU |
| Part counters | Per-cell, per-SKU production counts + total products |
| Value stream | VA time, NVA time, transport time, wait time, other time per SKU |
| Cycle times | Per assembly cell |

`3000Samplesv3.mat`: MATLAB data file with 3,000 simulation experiment samples for statistical analysis.

#### Model Files
| File | Description |
|---|---|
| .doe | Rockwell Arena simulation model (v15) |
| .pdf | Process model flowchart with logic description |
| .csv | Experimental results dataset |
| ParametersFile.xls | Simulation parameter settings (Model 3 only) |

---

## Approach

### Phase 1: Visual Defect Detection and Classification
1. **Data preparation:** Stratified train/val/test split (70/15/15), verify class balance
2. **Model training:** Transfer learning on EfficientNet-B4 (ImageNet pre-trained); fine-tune with AdamW + cosine LR schedule
3. **Localization:** Generate Grad-CAM saliency maps; optionally refine with SAM zero-shot masks for precise defect boundaries
4. **Confidence calibration:** Temperature scaling post-processing; flag "unknown" if max softmax confidence is below configurable threshold
5. **Metrics:** Accuracy, macro F1, per-class precision/recall, false-reject rate, false-accept rate

### Phase 2: Production Flow Analysis
1. **Feature engineering** from Model 1/2/3 CSV data (utilization deltas, queue growth rates, WIP ratios)
2. **Bottleneck identification:** Flag stations with utilization > 85% and growing queue depth
3. **Throughput impact modeling:** Apply queuing theory (Little's Law) to estimate capacity release if bottleneck is resolved
4. **Cost estimation:** Defect rate x rework cost + throughput loss x contribution margin = profitability delta

### Phase 3: Root-Cause Correlation
1. **Alignment:** Map image inspection batch IDs to nearest simulation state snapshot
2. **Correlation analysis:** Spearman rank coefficients between defect type prevalence and process parameters; PCA to reduce feature space
3. **SHAP explainability:** Feature importance for bottleneck severity predictions
4. **Batch drift detection:** CUSUM control chart on defect rate per production batch

### Phase 4: Dashboard and Recommendations
1. Build interactive Streamlit / React dashboard surfacing all outputs
2. Surface top-3 process recommendations per defect cluster with supporting correlation evidence
3. What-if simulator: adjust demand or station capacity to observe simulated profitability delta

---

## Evaluation Criteria

### Checkpoint 1: README (15 Marks)
| Sub-criterion | Marks |
|---|---|
| Problem Understanding | 5 |
| Architecture | 5 |
| Approach | 5 |

### Checkpoint 2: Partial Execution (25 Marks)
| Sub-criterion | Marks |
|---|---|
| Features and Problem Relatability | 25 |

### Checkpoint 3: Full System (60 Marks)
| Criterion | Marks | Judge Focus |
|---|---|---|
| Defect detection and classification accuracy | 15 | Correctly identify defective units; control false rejects |
| Defect localization quality | 10 | Precision of bounding boxes, masks, or heatmaps on unseen samples |
| Robustness to unseen conditions | 10 | Performance under lighting/orientation/batch changes and novel variants |
| False-reject / false-accept handling | 5 | Balance between missed defects and unnecessary rejections |
| Root-cause correlation quality | 5 | Validity of links between defect patterns and process/batch data |
| Explainability and confidence handling | 5 | Evidence, calibrated confidence, uncertainty disclosure |
| Technical implementation | 5 | Architecture quality, reproducibility, runtime reliability |
| UI/UX and visualization | 5 | Operational clarity of dashboard, trends, and evidence |

Total: 100 Marks

---

## Project Structure

```
CMR/
|-- READMECMR.md
|-- ps Industries and automation.pdf
|-- train/
|   |-- crack/        (2,400 PNG images)
|   |-- hole/         (2,400 PNG images)
|   |-- normal/       (2,400 PNG images)
|   |-- rust/         (2,400 PNG images)
|   +-- scratch/      (2,400 PNG images)
|-- Manufacturing Data Shared Facility - Discrete-Event Simulation/
|   |-- Readme.txt
|   |-- 3000Samplesv3.mat
|   |-- Model 1/
|   |   |-- Model 1.doe
|   |   |-- Model 1.pdf
|   |   +-- Model_1.csv
|   |-- Model 2/
|   |   |-- Model 2.doe
|   |   |-- Model 2.pdf
|   |   +-- Model_2.csv
|   +-- Model 3/
|       |-- Model 3.doe
|       |-- Model 3.pdf
|       |-- Model_3.csv
|       +-- ParametersFile.xls
|-- train.zip
+-- Manufacturing Data Shared Facility - Discrete-Event Simulation.zip
```

---

## Setup and Installation

Full installation instructions will be finalized at Checkpoint 2 once model training code is complete.

### Prerequisites
- Python 3.9+
- CUDA-capable GPU (recommended for model training)

### Quick Start (planned)
```bash
git clone <repo-url>
cd CMR
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Key Dependencies (planned)
| Library | Purpose |
|---|---|
| torch / torchvision | Deep learning backbone (EfficientNet, ViT) |
| timm | Pretrained vision model library |
| pytorch-grad-cam | Grad-CAM saliency visualization |
| segment-anything | SAM for defect masking |
| shap | SHAP explainability for tabular models |
| scikit-learn | Classical ML, correlation analysis |
| scipy | Statistical tests, MATLAB .mat data loading |
| pandas / numpy | Data manipulation |
| streamlit | Interactive dashboard UI |
| plotly | Interactive charts and visualizations |

---

Event: NEURAX Hackathon 3.0 - Domain 2: AI in Industry and Automation
