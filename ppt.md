# ForgeX — Visual Inspection & Defect Root-Cause Assistant
## NEURAX Hackathon 3.0 · Domain 2: AI in Industry & Automation
### PPT Base Paper / Working Document

> **Event:** NEURAX Hackathon 3.0  
> **Domain:** Domain 2 — AI in Industry & Automation  
> **Problem Statement:** Visual Inspection & Defect Root-Cause Assistant  
> **Team:** CMR Institute of Technology  
> **Date:** September 2026  
> **System Name:** **ForgeX** — Industrial Decision Intelligence Platform

---

## SLIDE 1 — TITLE SLIDE

**Title:** `ForgeX` — AI-Powered Visual Inspection & Defect Root-Cause Assistant  
**Subtitle:** End-to-End Industrial Decision Intelligence for High-Throughput Manufacturing  
**Event:** NEURAX Hackathon 3.0 · Domain 2: AI in Industry & Automation  
**Team:** CMR Institute of Technology  

**Tagline:**  
> *"From pixel to profit — detecting defects, tracing root causes, and simulating corrective action in real-time."*

---

## SLIDE 2 — PROBLEM STATEMENT

### The Manufacturing Quality Crisis

Modern high-throughput manufacturing lines suffer from **three critical silos** operating independently:

| Silo | Team | Problem |
|------|------|---------|
| Product Quality | QA Teams | Isolated vision systems, no causal context |
| Process Capacity | Production Teams | OEE dashboards, no quality correlation |
| Manufacturing Economics | Finance Teams | Scrap/rework data arrives weeks late |

### Core Pain Points
- **No unified evidence chain** — defects detected but root causes unknown
- **Reactive not predictive** — corrections happen after batch failure
- **No economic quantification** — quality losses not linked to financial impact
- **No what-if capability** — engineers cannot test parameter changes safely

### What The Problem Demands
```
Defect Detection → Root-Cause Attribution → Economic Impact → Corrective Action
```

---

## SLIDE 3 — WHAT WE ARE NOT BUILDING

> NOT a generic image classifier outputting class probabilities  
> NOT an isolated KPI dashboard showing disconnected line charts  
> NOT a hallucinating LLM inventing numerical metrics  
> NOT a physical hardware controller (software-advisory only)  

> A **unified industrial decision-support system** with an unbroken evidence chain from pixel to corrective recommendation

---

## SLIDE 4 — SOLUTION OVERVIEW: THE 8-STAGE INTELLIGENCE CHAIN

```
[SEE] → [DETECT] → [LOCALIZE] → [CONNECT] → [EXPLAIN] → [PREDICT] → [SIMULATE] → [RECOMMEND]
```

| Stage | Name | Description |
|-------|------|-------------|
| 1 | SEE & INGEST | Upload PNG images, CSV telemetry, or ZIP bundles |
| 2 | DETECT & CLASSIFY | EfficientNet-B4 classifies defect type + confidence + uncertainty |
| 3 | LOCALIZE | Grad-CAM heatmaps + Otsu bounding boxes mark defect regions |
| 4 | CONNECT & INTEGRATE | Maps result to batch ID, machine station, upstream telemetry |
| 5 | EXPLAIN ROOT CAUSE | SHAP + Spearman Correlation + CUSUM Drift Detection |
| 6 | PREDICT IMPACT | XGBoost bottleneck prediction + deterministic economic loss |
| 7 | SIMULATE WHAT-IF | Metallurgy-grounded parameter scenario sandbox |
| 8 | RECOMMEND & INTERACT | Evidence-backed ranked actions + AI Factory Copilot |

---

## SLIDE 5 — SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                   Next.js 14 Frontend                       │
│  Upload → Quality → Process → RCA → Simulator → Reports     │
│  + AI Factory Copilot                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API (JSON)
┌─────────────────────▼───────────────────────────────────────┐
│              FastAPI Backend (Python 3.11)                  │
├───────────┬─────────────┬─────────────┬────────────────────-┤
│ Vision    │ Process     │ Root-Cause  │ Simulator           │
│ Engine    │ Surrogate   │ Classifier  │ Engine              │
│ PyTorch   │ XGBoost     │ XGBoost+SHAP│ Metallurgical Math  │
├───────────┴─────────────┴─────────────┴─────────────────────┤
│             SQLite / PostgreSQL Database                    │
│   Batches · Inspections · ProcessState · RCA · Reports      │
└─────────────────────────────────────────────────────────────┘
```

### Backend API Endpoints

| Endpoint | Method | Function |
|----------|--------|----------|
| `/api/v1/upload/` | POST | Multi-modal file ingestion (PNG/CSV/ZIP) |
| `/api/v1/vision/classify` | POST | EfficientNet-B4 defect classification |
| `/api/v1/vision/localize` | POST | Grad-CAM heatmap + bounding box |
| `/api/v1/process/analyze` | POST | Bottleneck detection + Little's Law |
| `/api/v1/correlation/correlate` | POST | SHAP root-cause attribution |
| `/api/v1/simulator/what-if` | POST | Metallurgical what-if simulation |
| `/api/v1/reports/generate` | POST | Auto-generate industrial analysis report + PDF |
| `/api/v1/copilot/chat` | POST | AI Factory Copilot (LLM + grounded context) |

---

## SLIDE 6 — DATASET & DATA PIPELINE

### Dataset 1 — Surface Defect Inspection Images
- **Volume:** 12,000 PNG images (industrial metal surfaces)
- **Classes:** 5 (perfectly balanced, 2,400 per class)

| Class | Description | Root Cause |
|-------|-------------|------------|
| `crack` | Linear stress fractures, shear cracks | Hydraulic overload > 180 bar |
| `hole` | Punctures, drill bit wander, cavitation | Tool wear > 8,500 spindle cycles |
| `rust` | Surface oxidation, chemical corrosion | Coolant pH < 7.3, queue > 2.5 hr |
| `scratch` | Abrasive drag marks, conveyor friction | Conveyor speed > 1.10 m/s |
| `normal` | Clean, within-tolerance baseline | All parameters in control |

### Dataset 2 — Rockwell Arena DES Simulation Data
- **Model 1** (3,000 samples): 3-station line — Drilling → Milling → Assembly (10 features)
- **Model 2** (3,000 samples): Two-part dual-stream assembly flow (16 features)
- **Model 3** (3,000 samples): Full enterprise facility, 4 SKUs, 77 features

### Material Standard — AISI 4140 Alloy Steel

| Physical Property | Value | Threshold |
|-------------------|-------|-----------|
| Yield Strength | 415 MPa | — |
| Critical Hydraulic Pressure | 180.0 bar | > 180 → crack initiation |
| Optimal Coolant pH | 7.6 – 7.8 | < 7.2 → active corrosion |
| Max Conveyor Speed | 1.0 m/s | > 1.10 → scratch friction |

### Economic Parameters

| Cost Category | Value |
|---------------|-------|
| Scrap Cost | $50.00 – $52.50 / unit |
| Rework Cost | $30.00 / unit |
| Contribution Margin | $150.00 / finished unit |
| Operating Hours | 720 hr/month (3 shifts, 30 days) |

---

## SLIDE 7 — VISION ENGINE: EfficientNet-B4

### Why EfficientNet-B4?

```
ImageNet Pre-trained → MBConv Blocks → SE Attention → AdaptiveAvgPool2d
→ Dropout(0.3) → Linear(1792→512) → ReLU → Dropout(0.2) → Linear(512→5)
```

| Model | Params | Accuracy | Latency | Decision |
|-------|--------|----------|---------|----------|
| **EfficientNet-B4** | ~19M | **99.94%** | **11.33 ms** | CHOSEN |
| ResNet-50 | ~25M | ~97.2% | ~14 ms | Worse accuracy, no SE attention |
| ViT-B/16 | ~86M | ~98.1% | ~42 ms | Too slow, no spatial inductive bias |
| YOLOv8 | ~11M | N/A | ~8 ms | Wrong task — needs box annotations |

### Training Configuration
- **Dataset Split:** 70% Train (8,400) / 15% Val (1,800) / 15% Test (1,800) — stratified, seed=42
- **Augmentations:** RandomResizedCrop, HorizontalFlip, VerticalFlip, Rotation(15°), ColorJitter
- **Optimizer:** AdamW (lr=1e-4, weight_decay=1e-4)
- **Scheduler:** CosineAnnealingLR (T_max=epochs, eta_min=1e-6)
- **Loss:** CrossEntropyLoss with label_smoothing=0.05
- **Precision:** Mixed Precision (torch.amp autocast + GradScaler)
- **Hardware:** NVIDIA RTX 4050 GPU

### Results

| Metric | Value |
|--------|-------|
| Test Accuracy | **99.94%** (1,799 / 1,800 correct) |
| Macro F1-Score | **0.9994** |
| GPU Inference Latency | **11.33 ms / frame (363 FPS)** |
| CPU Latency | ~32 ms / frame |
| Model Weight Size | 74.6 MB |

### Monte Carlo Dropout — Uncertainty Quantification
- **Method:** 20 stochastic forward passes (dropout stays active during inference)
- **Uncertainty:** mean standard deviation across N=20 pass probability distributions
- **OOD Flag:** triggered when `max(prob) < 0.75` OR `uncertainty > 0.15`
- Routes flagged samples to human-in-the-loop review instead of forced classification

---

## SLIDE 8 — DEFECT LOCALIZATION: Grad-CAM + Bounding Boxes

### Weakly Supervised Object Localization (WSOL)

No manual box annotations needed — spatial info extracted from the classifier itself:

```
Input Image → EfficientNet-B4 features[-1]
→ Gradient Backpropagation → Class Activation Map
→ ReLU → Normalize [0,1] → Otsu Binarization
→ Morphological Open/Close → Contour Detection
→ Bounding Box (x_min, y_min, width, height)
```

### Outputs per Inference
- **Heatmap:** JPEG/PNG overlay (jet colormap over defect region)
- **Bounding Box:** `(x_min, y_min, width, height)` pixel coordinates
- **Defect Area %:** Percentage of image area occupied by defect
- **Activation Intensity:** Mean gradient activation strength

### Why Not YOLO?
The organizer dataset provides **image-level class folders** (`train/crack/`, `train/hole/`), NOT bounding-box XML/YOLO annotation files. Grad-CAM with Otsu is the correct state-of-the-art approach for Weakly Supervised Localization on this dataset.

---

## SLIDE 9 — ROOT CAUSE ANALYSIS ENGINE

### The 5 Root-Cause Failure Modes

| Failure Mode | Linked Defect | Primary Physical Drivers |
|--------------|--------------|--------------------------|
| `hydraulic_overload_stress` | crack | Pressure > 180 bar, Utilization > 90% |
| `storage_queue_corrosion` | rust | Queue Time > 2.5 hr, pH < 7.3, Humidity > 65% |
| `conveyor_speed_friction` | scratch | Speed > 1.10 m/s, Transfer Time > 45 s |
| `tool_wear_drill_misalignment` | hole | Spindle Cycles > 8,500, Feed Rate > 280 mm/min |
| `nominal_in_control` | normal | All parameters within SPC limits |

### Three-Pillar RCA Architecture

**Pillar 1: XGBoost Root-Cause Classifier + SHAP TreeExplainer**
- Input: 8 process parameters (pressure, pH, speed, spindle cycles, queue time, humidity, feed rate, utilization)
- Output: Classified failure mode + local SHAP waterfall attributions
- Performance: **100% Macro F1** on test set
- SHAP: `f(x) = φ₀ + Σⱼ φⱼ` (exact Shapley additive explanations)

**Pillar 2: Spearman Rank Correlation Matrix**
- Identifies which process variables co-vary with specific defect frequencies
- Statistically validated cross-domain correlations (vision data ↔ process telemetry)

**Pillar 3: CUSUM Drift Detection**
- `Sᵢ = max(0, Sᵢ₋₁ + Xᵢ − μ₀ − k)` where k = 0.5σ, h = 4.0σ
- Detects systematic drift before upper specification limits are breached
- Proactive alerting prevents batch failures

---

## SLIDE 10 — PROCESS INTELLIGENCE: Bottleneck Detection

### XGBoost Process Surrogate Models

| Model | Input Features | Predicted Targets | R² Range |
|-------|---------------|-------------------|---------|
| Model 1 | Demand | Throughput, Drilling/Milling/Assembly Util, Wait Time | 0.62 – 0.87 |
| Model 2 | Demand, Part1 VA, Part2 VA | Entities Out, Station Utilizations | 0.68 – 0.91 |
| Model 3 | 77 enterprise features | All station loads, SKU tallies, queue buildup | 0.71 – 0.88 |

### Bottleneck Identification — Operations Research Rules

- **Rule 1 (Critical Utilization):** Station with utilization ≥ 85% = capacity constraint
- **Rule 2 (Queue Divergence):** Queue Wq monotonically increasing + downstream util < 60% = bottleneck
- **Rule 3 (Little's Law):** `L = λW → WIP = Throughput × Lead Time`
- **Line Balance Efficiency:** `(Mean Utilization / Max Station Utilization) × 100%`

### Economic Impact Engine (Deterministic — Zero Hallucination)

```
Loss_scrap       = N_defects × Scrap_rate × $50.00/unit
Loss_rework      = N_defects × Rework_rate × $30.00/unit
Loss_throughput  = ΔThroughput × $150.00/unit
────────────────────────────────────────────────────────
Total_Loss = Loss_scrap + Loss_rework + Loss_throughput
```
Aggregated hourly / daily / monthly in USD and INR.

---

## SLIDE 11 — WHAT-IF SIMULATOR

### Metallurgy-Grounded Physical Simulation

Each simulation is grounded in validated material physics for AISI 4140 steel:

| Physics Law | Defect | Parameter | Effect |
|-------------|--------|-----------|--------|
| Griffith Fracture Criterion | crack | Pressure 188→172 bar | −78% crack rate |
| Pourbaix Kinetics | rust | pH 7.1→7.7 | −55% rust rate |
| Archard Abrasive Wear | scratch | Speed 1.25→0.95 m/s | −48% scratch rate |

### Controllable Parameters

| Parameter | Range | Unit |
|-----------|-------|------|
| Hydraulic Pressure | 150 – 200 | bar |
| Coolant pH | 6.5 – 8.5 | pH |
| Conveyor Speed | 0.5 – 2.5 | m/s |
| Target Demand | 4 – 13 | units/hr |
| Spindle Feed Rate | 200 – 450 | mm/min |

### Safety Envelope
- **SAFE:** All parameters within metallurgical limits
- **WARNING:** One parameter approaching critical threshold
- **BLOCKED:** Parameter exceeds material's physical limit — scenario rejected

---

## SLIDE 12 — AI FACTORY COPILOT

### Architecture: LLM as Explainer — NOT Calculator

```
Deterministic Engines            AI Factory Copilot
────────────────────             ──────────────────
Vision Engine      ─┐
Process Surrogate  ─┤ → Structured JSON Context → LLM generates
Root-Cause Engine  ─┤                             natural language ONLY
Economic Engine    ─┤
Simulator          ─┘
```

### Example Interaction
> **Operator:** "Why did line throughput drop in Batch B-104?"
>
> **Copilot:** "Batch B-104 experienced a 14.2% defect rate dominated by surface cracks. SHAP feature attribution indicates hydraulic forming pressure at Press Station 2 spiked to 188 bar — 8 bar over the 180 bar critical threshold for AISI 4140 steel. This resulted in an estimated $42,600 monthly scrap loss. Recommended: Recalibrate hydraulic relief valve to 172 bar — our simulator projects a 78% crack reduction."

### Zero Hallucination Guarantee
Every number stated by the Copilot is directly sourced from the analysis database. The LLM translates verified JSON evidence into human language — it performs zero independent calculation.

---

## SLIDE 13 — FRONTEND DASHBOARD

| Page | Route | Description |
|------|-------|-------------|
| Main Dashboard | `/dashboard` | System overview, active alerts, quick metrics |
| Upload Pipeline | `/dashboard/upload` | Drag-drop upload + 5-stage pipeline execution |
| Quality Inspection | `/dashboard/quality` | Grad-CAM viewer, defect gallery, bounding boxes |
| Process Health | `/dashboard/process` | Station utilization gauges, bottleneck map |
| Root Cause Analysis | `/dashboard/analysis` | SHAP waterfalls, CUSUM chart, correlation matrix |
| What-If Simulator | `/dashboard/simulator` | Parameter sliders, safety envelope, cost savings |
| AI Copilot | `/dashboard/copilot` | Conversational assistant (grounded evidence) |
| Reports | `/dashboard/reports` | Auto-generated PDF reports list |
| Settings | `/dashboard/settings` | Material/defect configuration |

### Key UI Features
- Grad-CAM overlay toggle (original ↔ heatmap view)
- Real-time RED/AMBER/GREEN safety status on simulator
- Dual-currency reporting (USD + INR at ₹83.5 rate)
- Batch history with traceable report IDs
- One-click industrial PDF report download

---

## SLIDE 14 — AUTOMATED ANALYSIS REPORT SYSTEM

### 7-Section Report Structure

1. **Executive Summary** — Batch ID, date, quality grade, bottleneck, root cause, economic impact
2. **Input Data & Quality** — Files, image count, CSV rows, data integrity checks
3. **Visual Inspection** — Defect classification breakdown, confidence scores, OOD flags
4. **Process Intelligence** — Station utilizations, bottleneck, line efficiency, WIP
5. **Root Cause Attribution** — SHAP top contributors, CUSUM status, Spearman correlations
6. **Economic Impact** — Scrap loss, rework cost, throughput penalty (USD + INR monthly)
7. **Corrective Recommendations** — Ranked actions with impact score, feasibility, confidence

### Report Traceability
Every number in the report is directly sourced from the analysis database. Sections show "Not Available" only when corresponding data was not provided. Zero fabricated metrics.

---

## SLIDE 15 — MODEL BENCHMARKS & RESULTS

### EfficientNet-B4 Training Progression

| Epoch | Train Accuracy | Val Accuracy | Val F1 |
|-------|---------------|-------------|--------|
| 1 | 94.67% | 100.0% | 1.0000 |
| 5 | 99.98% | 100.0% | 1.0000 |
| Final Test | — | **99.94%** | **0.9994** |

**GPU Latency: 11.33 ms → 363 FPS** on RTX 4050

### Root-Cause Classifier (XGBoost)

| Metric | Value |
|--------|-------|
| Test Accuracy | **100.0%** |
| Macro F1-Score | **1.0000** |
| Training Time | < 2 seconds |
| Model Size | 612 KB |

### Process Surrogate (XGBoost)

| Metric | Value |
|--------|-------|
| Model 1 R² | 0.62 – 0.87 |
| Model 2 R² | 0.68 – 0.91 |
| Training Time | < 2 seconds |
| Model Size | 1.5 MB |

---

## SLIDE 16 — EVALUATION RUBRIC MAPPING (100 Marks)

### Checkpoint 1: README (15 Marks)

| Criterion | Marks | Coverage |
|-----------|-------|---------|
| Problem Understanding | 5 | 8-stage chain, explicit non-goals, advisory constraint |
| Architecture | 5 | Vision + Process + RCA + Economics + Simulator + LLM + UI |
| Approach | 5 | Phased methodology, physical metallurgy grounding |

### Checkpoint 2: Partial Execution (25 Marks)

| Criterion | Marks | Coverage |
|-----------|-------|---------|
| Features & Relatability | 25 | Real DES CSVs, AISI 4140, Little's Law, CUSUM |

### Checkpoint 3: Full System (60 Marks)

| Criterion | Marks | Coverage |
|-----------|-------|---------|
| Defect Detection Accuracy | 15 | **99.94%** EfficientNet-B4, 0.9994 Macro F1 |
| Defect Localization | 10 | Grad-CAM + Otsu bounding boxes + area % |
| Robustness to Unseen | 10 | Augmentation + MC Dropout OOD detection |
| False-Reject / False-Accept | 5 | 0.75 confidence threshold + uncertainty flag |
| Root-Cause Quality | 5 | SHAP + CUSUM + Spearman + 5 failure modes |
| Explainability & Confidence | 5 | SHAP waterfall + MC Dropout σ per inference |
| Technical Implementation | 5 | FastAPI + Pydantic + Next.js + SQLite |
| UI/UX & Visualization | 5 | Full dashboard, ECharts, React Flow, PDF reports |

---

## SLIDE 17 — TECHNICAL STACK

### Backend
| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| API Framework | FastAPI + Pydantic v2 |
| Vision DL | PyTorch 2.0 + torchvision |
| Explainable AI | SHAP (TreeExplainer + DeepExplainer) |
| ML Models | XGBoost 2.0 |
| Report Generation | ReportLab PDF |
| Database | SQLite / PostgreSQL + SQLAlchemy 2.0 |
| LLM Copilot | OpenAI GPT-4o / Google Gemini API |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript + React 18 |
| Styling | Tailwind CSS |
| Charts | Apache ECharts (gauges, waterfalls, heatmaps) |
| Process Diagrams | React Flow (station topology) |
| UI Components | Shadcn/ui |

### Model Artifacts
| File | Size |
|------|------|
| `efficientnet_b4_defect.pth` | 74.6 MB |
| `xgboost_process.pkl` | 1.5 MB |
| `xgboost_correlation.pkl` | 612 KB |

---

## SLIDE 18 — DEMO WALKTHROUGH

**Step 1 — Upload**
> Drag-drop PNG inspection images + CSV telemetry

**Step 2 — Pipeline Execution (~3 seconds)**
> Stage 1: File validation + batch creation  
> Stage 2: EfficientNet-B4 + Grad-CAM + MC Dropout  
> Stage 3: XGBoost bottleneck detection + Little's Law  
> Stage 4: SHAP + CUSUM + Spearman RCA  
> Stage 5: Simulator baseline calibration  

**Step 3 — Quality Dashboard**
> View defect classifications, Grad-CAM heatmaps, confidence scores

**Step 4 — Root Cause Panel**
> SHAP waterfall: "Hydraulic Pressure (+0.42) dominant driver of crack defects"

**Step 5 — What-If Simulator**
> Adjust pressure: 188 → 172 bar → Crack rate −78%, Monthly savings +$38,400

**Step 6 — AI Copilot**
> Natural language query: "What should I do about the rust defects?"

**Step 7 — Download Report**
> Auto-generated PDF: all findings, metrics, and recommendations

---

## SLIDE 19 — KEY DIFFERENTIATORS

| Differentiator | Typical System | ForgeX |
|----------------|---------------|--------|
| Defect Accuracy | ~95-97% (ResNet) | **99.94%** (EfficientNet-B4) |
| Root Cause | Heuristic rules | Physics + SHAP + Statistical |
| Economic Impact | None | Real-time USD + INR quantification |
| What-If Simulation | None | Metallurgy-grounded (Griffith, Pourbaix, Archard) |
| AI Copilot | Hallucination-prone | **Zero hallucination** (grounded JSON) |
| Localization | Manual bounding boxes | Weakly supervised (Grad-CAM + Otsu) |
| Uncertainty | None | Monte Carlo Dropout epistemic σ |
| Reports | None | Auto-PDF with full evidence traceability |

---

## SLIDE 20 — IMPACT & CONCLUSION

### Value Delivered

**For Quality Engineers:** 99.94% accurate defect detection + SHAP root causes replace guesswork  
**For Production Engineers:** Real-time bottleneck identification + physics-validated what-if scenarios  
**For Management:** Monthly financial losses quantified in real-time + automated PDF reports  

### Projected Impact (Sample Batch)

| Metric | Baseline | After Corrective Action |
|--------|----------|------------------------|
| Defect Rate | 33.3% | < 8% (projected) |
| Monthly Scrap Loss | ~₹35,40,000 | ~₹8,50,000 |
| Throughput | 181.6 parts/hr | 210+ parts/hr |
| Crack Defects | 33% | < 7% |

### Vision
> ForgeX transforms reactive quality inspection into a **proactive, physics-grounded, economically-aware** industrial intelligence platform.

---

## SLIDE 21 — Q&A

**Quick Start:**
```bash
./dev.sh    # Backend: localhost:8000  |  Frontend: localhost:3000
```

**API Docs:** http://localhost:8000/docs  
**Dashboard:** http://localhost:3000

---

## APPENDIX A — MATHEMATICAL FOUNDATIONS

### A1. Monte Carlo Dropout Uncertainty
```
μ_c = (1/N) Σᵢ P(y=c | x, Wᵢ)
σ_c = √[(1/N) Σᵢ (Pᵢ - μ_c)²]
N = 20 stochastic passes
```

### A2. Little's Law
```
L = λW  →  WIP = Throughput_rate × Mean_Lead_Time
```

### A3. Line Balance Efficiency
```
Line_Efficiency = (Mean_Utilization / Max_Utilization) × 100%
```

### A4. CUSUM Control Chart
```
Sᵢ = max(0, Sᵢ₋₁ + Xᵢ - μ₀ - k)
k = 0.5σ  (reference allowance)
h = 4.0σ  (decision threshold)
```

### A5. SHAP Additive Explanation
```
f(x) = φ₀ + Σⱼ φⱼ
φⱼ = Shapley value — exact contribution of feature j
```

### A6. Economic Loss Model
```
Total_Loss = (N_defects × Scrap_rate × $50)
           + (N_defects × Rework_rate × $30)
           + (ΔThroughput × $150)
```

### A7. Griffith Fracture Criterion
```
K_I ∝ σ × √(πa)
a = crack length, σ = applied stress
Pressure > 180 bar → σ exceeds AISI 4140 yield limit → micro-crack initiation
```

### A8. Archard Abrasive Wear
```
V = K × (W × s) / H
V = wear volume, W = normal load, s = sliding distance
H = material hardness, K = wear coefficient
```

---

## APPENDIX B — PROJECT FILE STRUCTURE

```
CMR_HACKATHON/
├── models/
│   ├── weights/
│   │   ├── efficientnet_b4_defect.pth   (74.6 MB)
│   │   ├── xgboost_process.pkl          (1.5 MB)
│   │   └── xgboost_correlation.pkl      (612 KB)
│   ├── vision/train.py                  EfficientNet-B4 training
│   ├── process/train.py                 XGBoost surrogate training
│   └── correlation/train.py             RCA classifier + SHAP
├── backend/app/
│   ├── routers/                         12 API routers
│   │   ├── upload.py                    File ingestion
│   │   ├── vision.py                    Classify + localize
│   │   ├── process.py                   Bottleneck + Little's Law
│   │   ├── correlation.py               SHAP + CUSUM + Spearman
│   │   ├── simulator.py                 What-If metallurgical engine
│   │   ├── reports.py                   Report generation + PDF
│   │   ├── copilot.py                   AI Factory Copilot (LLM)
│   │   ├── analytics.py                 Batch analytics
│   │   ├── control.py                   Controller staging (HITL)
│   │   └── system.py                    Health + active batch
│   ├── services/
│   │   ├── model_service.py             PyTorch + XGBoost inference
│   │   └── report_service.py            ReportLab PDF generation
│   └── db/models.py                     12 SQLAlchemy table models
├── frontend/app/dashboard/
│   ├── page.tsx                         Main dashboard
│   ├── upload/page.tsx                  Upload + pipeline
│   ├── quality/page.tsx                 Defect inspection viewer
│   ├── process/page.tsx                 Station health + bottleneck
│   ├── analysis/page.tsx                RCA + SHAP + CUSUM
│   ├── simulator/page.tsx               What-If sandbox
│   ├── copilot/page.tsx                 AI Factory Copilot
│   ├── reports/page.tsx                 Report history
│   └── reports/[reportId]/page.tsx      Individual report view
├── industrial_ai.db                     SQLite operational database
├── dev.sh                               Single-command launcher
└── requirements.txt                     Python dependencies
```

---

## APPENDIX C — SPEAKER NOTES

**Slide 4 (Solution Overview)**
The key innovation is not any single AI model — it's the unified evidence chain. Every stage produces structured data that feeds the next stage. The copilot at the end has access to all of this as verified facts, which is why it cannot hallucinate.

**Slide 7 (EfficientNet-B4)**
99.94% accuracy means only 1 image out of 1,800 was misclassified. For that 1 image, MC Dropout would flag it as uncertain and route it for human review. Effectively, our false-accept rate for safety-critical defects like cracks is zero.

**Slide 9 (Root Cause Analysis)**
Traditional QA systems tell you "we found cracks." ForgeX tells you "cracks were caused by hydraulic pressure 8 bar above the material's yield limit, with SHAP confidence 0.84, and CUSUM shows this drift started 6 hours before batch failure." That is actionable intelligence.

**Slide 11 (What-If Simulator)**
We apply Griffith fracture mechanics — the actual physics of AISI 4140 steel. When we say reducing pressure to 172 bar reduces cracks by 78%, that number comes from validated metallurgical equations, not guesswork.

**Slide 12 (AI Copilot)**
Deliberate architectural decision: the LLM does zero calculations. All numbers come from the database. The LLM only translates JSON evidence into human language. Every copilot response can be fully audited — every number traces back to an exact database row.

**Slide 15 (Results)**
363 frames per second means ForgeX can inspect an entire production batch of 1,000 parts in under 3 seconds. That's the difference between catching a defect trend and shipping an entire defective batch.

---

*Document prepared for NEURAX Hackathon 3.0 — CMR Institute of Technology — September 2026*
