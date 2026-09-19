# Visual Inspection & Defect Root-Cause Assistant
## NEURAX Hackathon 3.0 — Domain 2: AI in Industry and Automation

---

## Table of Contents
1. [Problem Statement](#1-problem-statement)
2. [System Architecture](#2-system-architecture)
3. [Datasets](#3-datasets)
4. [Approach & Methodology](#4-approach--methodology)
5. [Technology Stack](#5-technology-stack)
6. [Evaluation Criteria](#6-evaluation-criteria)
7. [Project Structure](#7-project-structure)
8. [References](#8-references)

---

## 1. Problem Statement

High-throughput manufacturing lines are difficult to optimize because product quality, process capacity, and economics interact. Defect signatures are subtle and easy to miss at production speed, while bottlenecks emerge from cycle-time imbalance, excess work-in-process (WIP), and varying station utilization.

The objective is to build a **unified industrial decision-support system** — not a standalone image classifier or KPI dashboard — that:

- Classifies products as acceptable or defective and localizes defect regions
- Flags uncertain or out-of-distribution defect types with calibrated confidence
- Detects production bottlenecks and estimates their effect on throughput
- Links defect patterns to process conditions through evidence-backed root-cause analysis
- Predicts profitability impact and generates actionable process recommendations

> All outputs are advisory. No hardware integration, live camera feed, PLC connection, or robotic control is required.

---

## 2. System Architecture

The system is a **unified multi-pipeline AI architecture** with four tightly integrated analytical layers:
Our system connects three normally isolated views of a factory: product quality, production flow, and economics. Vision AI tells us what defect occurred and where it is. Process AI tells us where the production flow is constrained. Economic analysis tells us what that defect or bottleneck is costing. We then align these signals through an integration layer using identifiers such as product, batch, station and timestamp. Our root-cause engine finds evidence-backed candidate contributing factors, the predictive engine identifies future risk, and the what-if simulator tests possible interventions before recommending an action. Finally, the AI Factory Copilot explains the complete evidence chain to the operator through the dashboard.
 
```
                          DATA SOURCES
                               |
          +--------------------+--------------------+
          |                    |                    |
          v                    v                    v
   INSPECTION DATA      PRODUCTION DATA       ECONOMIC DATA
   (Images: PNG)        (DES CSVs / .mat)     (Cost parameters)
          |                    |                    |
          v                    v                    |
  +---------------+   +----------------+           |
  |  VISION AI    |   |  PROCESS /     |           |
  |               |   |  FLOW AI       |           |
  | EfficientNet  |   | Bottleneck     |           |
  | Grad-CAM      |   | Throughput     |           |
  | SAM           |   | Utilization    |           |
  | MC Dropout    |   | Little's Law   |           |
  | OOD Detection |   | CUSUM          |           |
  +-------+-------+   +-------+--------+           |
          |                   |                    |
          +-------------------+--------------------+
                              |
                              v
              +-------------------------------+
              |        INTEGRATION LAYER      |
              |  Product ID · Batch ID        |
              |  Station ID · Timestamp       |
              +---------------+---------------+
                              |
                              v
              +-------------------------------+
              |      ROOT-CAUSE ENGINE        |
              |  Spearman / Pearson           |
              |  Temporal alignment           |
              |  SHAP attribution             |
              |  CUSUM drift detection        |
              |  Domain rules + evidence      |
              +---------------+---------------+
                              |
                              v
              +-------------------------------+
              |     KNOWLEDGE / EVIDENCE      |
              |  Historical defect patterns   |
              |  Station–process relations    |
              |  RCA evidence scoring         |
              +---------------+---------------+
                              |
                              v
              +-------------------------------+
              |      PREDICTIVE ENGINE        |
              |  Defect risk forecast         |
              |  Process drift (CUSUM)        |
              |  Throughput / capacity        |
              +---------------+---------------+
                              |
                              v
              +-------------------------------+
              |      WHAT-IF SIMULATOR        |
              |  Demand / capacity sliders    |
              |  Scenario vs current state    |
              |  Throughput, cost, margin     |
              +---------------+---------------+
                              |
                              v
              +-------------------------------+
              |    RECOMMENDATION ENGINE      |
              |  Evidence · Impact            |
              |  Feasibility · Confidence     |
              +---------------+---------------+
                              |
                              v
              +-------------------------------+
              |      AI FACTORY COPILOT       |
              |  Natural-language Q&A         |
              |  Evidence-backed explanations |
              +---------------+---------------+
                              |
                              v
              +-------------------------------+
              |   INDUSTRIAL DASHBOARD (UI)   |
              |  Next.js · React · ECharts    |
              +-------------------------------+
```

### Core Intelligence Chain

```
SEE → DETECT → LOCALIZE → CONNECT → EXPLAIN → PREDICT → SIMULATE → RECOMMEND
```

| Layer | Method |
|---|---|
| Computer Vision | Deep Learning (EfficientNet-B4, Grad-CAM, SAM) |
| Process Analysis | Statistics + Operations Research (Little's Law, CUSUM) |
| Root Cause | Statistical correlation + ML attribution (SHAP, XGBoost) |
| Economic Impact | Deterministic mathematical models |
| Forecasting | ML + time-series methods |
| Natural-language UX | LLM (explanation only, not root-cause generation) |

The LLM is strictly an **explanation and query layer** over pre-computed analytical evidence, not the primary reasoning engine.

---

## 3. Datasets

### 3.1 Surface Defect Image Dataset (`train/`)

| Class | Description | Count |
|---|---|---|
| `crack` | Surface crack defects | 2,400 |
| `hole` | Hole / puncture defects | 2,400 |
| `rust` | Rust / corrosion defects | 2,400 |
| `scratch` | Surface scratch defects | 2,400 |
| `normal` | Defect-free units | 2,400 |
| **Total** | | **12,000** |

- Format: PNG, RGB
- Balanced across all classes (2,400 images each)

### 3.2 Manufacturing DES Simulation Data

Three progressively complex Rockwell Arena Discrete-Event Simulation (DES) models representing a shared multi-station manufacturing facility:

| Model | Flow Description | Features |
|---|---|---|
| Model 1 | Drilling → Milling → Assembly | 10 |
| Model 2 | Two-part, two-stage (Part 1 / Part 2) | 16 |
| Model 3 | Full facility, 4-SKU, multi-station | 77 |

**Model 3 feature groups:**

| Group | Description |
|---|---|
| Utilization | Blanking, 4× Press, 4× Assembly, 2× Paint, Quality, Forklift |
| Queues | Station- and warehouse-level per SKU |
| Part counters | Per-cell, per-SKU production + totals |
| Value stream | VA, NVA, transport, wait, and other time per SKU |
| Cycle times | Per assembly cell |

`3000Samplesv3.mat`: 3,000-sample Design of Experiments (DoE) output for surrogate modelling and statistical analysis.

Each model directory contains: `.doe` (Arena model), `.pdf` (process flowchart), `.csv` (results), and `ParametersFile.xls` (Model 3 only).

---

## 4. Approach & Methodology

### Phase 1: Visual Defect Detection & Classification

Transfer learning on **EfficientNet-B4** [Tan & Le, 2019] pre-trained on ImageNet [Deng et al., 2009]:
- Stratified 70/15/15 train/val/test split; AdamW optimizer with cosine LR schedule
- **Grad-CAM** [Selvaraju et al., 2017] for class-discriminative localization heat maps
- Optional **Segment Anything Model (SAM)** [Kirillov et al., 2023] for precise defect masks
- **Monte Carlo Dropout** [Gal & Ghahramani, 2016] and temperature scaling [Guo et al., 2017] for calibrated uncertainty; units are flagged as novel/uncertain when max softmax confidence falls below a configurable threshold (out-of-distribution detection)
- Metrics: accuracy, macro-F1, per-class precision/recall, false-reject rate, false-accept rate

### Phase 2: Production Flow Analysis

Analytical bottleneck detection grounded in operations research:
- **Feature engineering** from Model 1/2/3 CSV data: utilization rates, queue growth, WIP, cycle times, SKU breakdowns
- **Bottleneck detection**: stations flagged at sustained utilization > 85% with monotonically growing queue depth
- **Little's Law** [Little, 1961] applied to estimate WIP-to-throughput relationships and capacity headroom
- **CUSUM control charts** [Page, 1954] for sequential detection of process drift
- **Economic model**: Total Loss = (Scrapped Units × Scrap Cost) + (Reworked Units × Rework Cost) + (Throughput Loss × Contribution Margin)

### Phase 3: Root-Cause Correlation

Cross-domain root-cause analysis linking visual inspection results to process states:
- **Temporal alignment**: batch ID maps inspection events to nearest simulation state snapshot
- **Spearman rank correlation** [Spearman, 1904] between defect-type prevalence and process parameters; PCA for dimensionality reduction
- **XGBoost** [Chen & Guestrin, 2016] with **SHAP** [Lundberg & Lee, 2017] for feature-importance attribution and transparent bottleneck severity prediction
- Evidence is scored (strength, consistency, confidence) and presented with explicit uncertainty — correlation is distinguished from causation

### Phase 4: Predictive Engine & What-if Simulator

- Defect risk, process drift, and throughput forecasts using XGBoost on engineered process features
- What-if simulator adjusts demand, station capacity, or resource allocation and propagates changes through the process and economic models (SciPy Optimize) to produce advisory scenario comparisons
- Recommendation engine combines root-cause evidence + economic impact + feasibility scoring to surface ranked, evidence-backed recommendations

### Phase 5: Decision-Support Dashboard

Interactive Next.js / React UI exposing:
- Defect image gallery with Grad-CAM overlays and confidence indicators
- Factory overview: OEE, throughput, yield rate, bottleneck KPI cards
- Root-cause graph (React Flow) with correlation matrix, SHAP waterfall, CUSUM timeline
- Economic impact breakdown (loss by defect class, station, batch)
- What-if scenario comparison with sliders
- AI Factory Copilot: natural-language Q&A backed by pre-computed analytical evidence (LLM for explanation only)

---

## 5. Technology Stack

| Layer | Technology |
|---|---|
| **Vision** | PyTorch, torchvision, timm, EfficientNet-B4, Grad-CAM, SAM |
| **Process Analytics** | Pandas, NumPy, SciPy, Statsmodels, Little's Law, CUSUM |
| **ML / Tabular** | XGBoost, scikit-learn |
| **Explainability** | SHAP, Grad-CAM |
| **Optimization** | SciPy Optimize |
| **Backend API** | FastAPI, Pydantic |
| **Database** | PostgreSQL (+ pgvector for semantic retrieval if needed) |
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui |
| **Visualization** | Apache ECharts, React Flow, Framer Motion |
| **AI Copilot** | GPT API (optional LangGraph for multi-step retrieval) |
| **Testing** | pytest, Postman |
| **DevOps** | Docker, Git, GitHub |
| **Deployment** | Vercel (frontend), Render/Railway (backend) |

---

## 6. Evaluation Criteria

### Checkpoint 1 — README (15 Marks)
| Criterion | Marks |
|---|---|
| Problem Understanding | 5 |
| Architecture | 5 |
| Approach | 5 |

### Checkpoint 2 — Partial Execution (25 Marks)
| Criterion | Marks |
|---|---|
| Features & Problem Relatability | 25 |

### Checkpoint 3 — Full System (60 Marks)
| Criterion | Marks |
|---|---|
| Defect detection & classification accuracy | 15 |
| Defect localization quality | 10 |
| Robustness to unseen conditions | 10 |
| False-reject / false-accept handling | 5 |
| Root-cause correlation quality | 5 |
| Explainability & confidence handling | 5 |
| Technical implementation | 5 |
| UI/UX & visualization | 5 |

---

## 7. Project Structure

```
CMR/
├── Round1.md                                        ← This file
├── ps Industries and automation.pdf                 ← Official problem statement
├── final_industrial_ai_system_design.md             ← Detailed system design
├── train/
│   ├── crack/         (2,400 PNG images)
│   ├── hole/          (2,400 PNG images)
│   ├── normal/        (2,400 PNG images)
│   ├── rust/          (2,400 PNG images)
│   └── scratch/       (2,400 PNG images)
├── Manufacturing Data Shared Facility - Discrete-Event Simulation/
│   ├── Readme.txt
│   ├── 3000Samplesv3.mat
│   ├── Model 1/  (Model_1.csv — 10 features)
│   ├── Model 2/  (Model_2.csv — 16 features)
│   └── Model 3/  (Model_3.csv — 77 features, ParametersFile.xls)
└── [source code — to be added at Checkpoint 2]
```

---

## 8. References

1. **Tan, M. & Le, Q. V.** (2019). EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks. *ICML 2019*. [arXiv:1905.11946](https://arxiv.org/abs/1905.11946)
2. **Selvaraju, R. R., et al.** (2017). Grad-CAM: Visual Explanations from Deep Networks via Gradient-Based Localization. *ICCV 2017*. [arXiv:1610.02391](https://arxiv.org/abs/1610.02391)
3. **Kirillov, A., et al.** (2023). Segment Anything. *ICCV 2023*. [arXiv:2304.02643](https://arxiv.org/abs/2304.02643)
4. **Gal, Y. & Ghahramani, Z.** (2016). Dropout as a Bayesian Approximation. *ICML 2016*. [arXiv:1506.02142](https://arxiv.org/abs/1506.02142)
5. **Guo, C., et al.** (2017). On Calibration of Modern Neural Networks. *ICML 2017*. [arXiv:1706.04599](https://arxiv.org/abs/1706.04599)
6. **Lundberg, S. M. & Lee, S.-I.** (2017). A Unified Approach to Interpreting Model Predictions (SHAP). *NeurIPS 2017*. [arXiv:1705.07874](https://arxiv.org/abs/1705.07874)
7. **Chen, T. & Guestrin, C.** (2016). XGBoost: A Scalable Tree Boosting System. *KDD 2016*. [arXiv:1603.02754](https://arxiv.org/abs/1603.02754)
8. **Little, J. D. C.** (1961). A proof for the queuing formula L = λW. *Operations Research, 9*(3), 383–387.
9. **Page, E. S.** (1954). Continuous inspection schemes. *Biometrika, 41*(1–2), 100–115.
10. **Spearman, C.** (1904). The proof and measurement of association between two things. *American Journal of Psychology, 15*(1), 72–101.
11. **Deng, J., et al.** (2009). ImageNet: A Large-Scale Hierarchical Image Database. *CVPR 2009*.
12. **He, K., et al.** (2016). Deep Residual Learning for Image Recognition. *CVPR 2016*. [arXiv:1512.03385](https://arxiv.org/abs/1512.03385)
13. **Law, A. M.** (2015). *Simulation Modeling and Analysis* (5th ed.). McGraw-Hill. *(Arena DES methodology)*
14. **Montgomery, D. C.** (2020). *Introduction to Statistical Quality Control* (8th ed.). Wiley. *(SPC, CUSUM)*
15. **Ribeiro, M. T., Singh, S., & Guestrin, C.** (2016). "Why Should I Trust You?": Explaining the Predictions of Any Classifier (LIME). *KDD 2016*. [arXiv:1602.04938](https://arxiv.org/abs/1602.04938)
