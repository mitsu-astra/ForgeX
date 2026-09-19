# Visual Inspection & Defect Root-Cause Assistant
### NEURAX HACKATHON 3.0 - Domain 2: AI in Industry and Automation

**Date:** September 19, 2026

---

## ⚡ Quick Start & Execution

Launch the full system (FastAPI backend + Next.js interactive frontend) with a single command:

```bash
# Make the startup script executable and run
chmod +x run_app.sh
./run_app.sh
```

Or run the components in separate terminal windows:

### 1. Backend Server (FastAPI + Preloaded PyTorch / CUDA Models)
```bash
source venv/bin/activate
export PYTHONPATH="$PWD"
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```
- API Docs & Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Frontend Web Application (Next.js App Router + Tailwind CSS)
```bash
cd frontend
npm run dev
```
- Web Application: `http://localhost:3000`

---

## 🏆 Model Benchmarks & Results
- **Visual Defect Classifier (EfficientNet-B4)**: **99.94% Test Accuracy** across 1,800 test images (0.9994 Macro F1)
- **Grad-CAM Localization**: Spatial activation mapping with Otsu contour bounding box extraction
- **Epistemic Uncertainty**: Monte Carlo Dropout with 95% confidence intervals
- **GPU Inference Latency**: **11.33 ms / frame** (363.3 FPS) on NVIDIA GeForce RTX 4050 GPU
- **Process Surrogate & SHAP**: XGBoost regression + TreeExplainer local waterfall feature attributions

---

## 📋 Table of Contents
1. [Problem Understanding](#problem-understanding)
2. [Solution Overview](#solution-overview)
3. [System Architecture](#system-architecture)
4. [Datasets & Resources](#datasets--resources)
5. [Approach & Methodology](#approach--methodology)
6. [Technical Stack](#technical-stack)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Expected Outcomes](#expected-outcomes)

---

## 🎯 Problem Understanding

### Core Challenge
High-throughput manufacturing lines face a critical challenge: optimizing the delicate balance between **product quality**, **process capacity**, and **economic efficiency**. Bottlenecks can emerge from multiple sources:
- Cycle time imbalances
- Excess work-in-process inventory
- Equipment downtime
- Station changeovers
- Low utilization rates
- Scrap and rework

These bottlenecks often manifest as quality issues in the final product, but identifying the **root cause** requires correlating visual defects with complex, multi-stage manufacturing process data.

### Problem Statement Analysis
**What we are NOT building:**
- ❌ Generic image classifier
- ❌ Isolated KPI dashboard
- ❌ Simple labeling tool

**What we ARE building:**
- ✅ **Unified industrial decision-support system** that:
  - Analyzes organizer-provided inspection, production, and economic datasets
  - Produces continuously updated views of product quality, flow health, and expected profitability
  - Classifies units as acceptable or defective
  - Localizes defects with spatial precision
  - Flags uncertain or novel defect types
  - Identifies industrial bottlenecks
  - Estimates their effect on throughput and losses
  - Predicts profitability or margin
  - Generates evidence-based process recommendations

### Key Requirements

#### 1. **Visual Inspection Component**
- Classify defective vs. acceptable units
- Localize defects on product surfaces
- Detect and flag novel/uncertain defect patterns
- Control false-reject vs. false-accept balance

#### 2. **Root-Cause Analysis Component**
- Correlate defect patterns with process conditions
- Identify bottlenecks in multi-stage manufacturing
- Link process parameters (utilization, queue times, cycle times) to quality issues
- Provide evidence-based explanations

#### 3. **Impact Estimation Component**
- Predict effect on throughput
- Estimate production losses
- Calculate profitability/margin impact
- Support what-if scenario analysis

#### 4. **Recommendation Engine**
- Generate actionable process improvements
- Prioritize interventions by impact
- Provide evidence and confidence levels
- Acknowledge limitations and uncertainty

#### 5. **System Constraints**
- **Software-only**: No live camera feed, PLC connection, or hardware integration
- **Simulated/Advisory**: All recommendations remain simulated or advisory
- **Uncertainty handling**: Must handle unseen conditions gracefully

---

## 💡 Solution Overview

Our solution implements a **three-stage integrated pipeline**:

### Stage 1: Visual Defect Detection & Classification
Deep learning-based computer vision system that:
- Classifies products into 5 categories: Normal, Rust, Crack, Hole, Scratch
- Localizes defects using attention mechanisms (Grad-CAM)
- Quantifies prediction confidence
- Flags out-of-distribution samples

### Stage 2: Manufacturing Process Analysis
Multi-model manufacturing simulation system that:
- Analyzes 3 levels of process complexity (10, 16, and 77 features)
- Predicts resource utilization rates
- Identifies queue bottlenecks
- Calculates value-added vs. non-value-added time ratios

### Stage 3: Root-Cause Correlation & Decision Support
Hybrid analytical engine that:
- Correlates defect types with process anomalies
- Identifies causal relationships using statistical and ML methods
- Estimates economic impact (throughput loss, scrap cost)
- Generates ranked, evidence-based recommendations

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                                   │
├─────────────────────────────┬───────────────────────────────────────┤
│   Visual Inspection Data     │   Manufacturing Process Data          │
│   • Product Images (PNG)     │   • Model 1: 10 features (simple)     │
│   • 5 Defect Classes         │   • Model 2: 16 features (multi-SKU)  │
│   • 12,000 Training Samples  │   • Model 3: 77 features (complex)    │
└──────────────┬───────────────┴──────────────┬────────────────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐  ┌─────────────────────────────────┐
│   VISUAL ANALYSIS MODULE     │  │  PROCESS ANALYSIS MODULE        │
├──────────────────────────────┤  ├─────────────────────────────────┤
│ • CNN Backbone (ResNet/      │  │ • Neural Network Predictors     │
│   EfficientNet)              │  │   - Utilization forecasting     │
│ • Transfer Learning          │  │   - Queue time prediction       │
│ • 5-Class Classifier         │  │   - Throughput estimation       │
│                              │  │                                 │
│ • Grad-CAM Localization      │  │ • Feature Importance Analysis   │
│ • Bounding Box Generation    │  │ • Bottleneck Detection          │
│                              │  │ • Capacity Analysis             │
│ • Uncertainty Quantification │  │                                 │
│   - Monte Carlo Dropout      │  │ • Simulation Integration        │
│   - Ensemble Methods         │  │   - Model 1: Drilling/Milling   │
│   - OOD Detection            │  │   - Model 2: Assembly Lines     │
│                              │  │   - Model 3: Full Facility      │
└──────────────┬───────────────┘  └─────────────┬───────────────────┘
               │                                │
               │     ┌──────────────────────────┘
               │     │
               ▼     ▼
┌─────────────────────────────────────────────────────────────────────┐
│              CORRELATION & ROOT-CAUSE ENGINE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  • Defect-Process Correlation Matrix                                │
│    ├─ Statistical Analysis (Pearson, Spearman)                      │
│    ├─ Temporal Pattern Matching                                     │
│    └─ Causal Inference                                              │
│                                                                       │
│  • Rule-Based Expert System                                         │
│    ├─ Rust + High Queue Time → Storage/Waiting Issue               │
│    ├─ Crack + High Utilization → Overload/Stress                   │
│    ├─ Scratch + Low VA Time → Handling Problem                     │
│    └─ Hole + Drilling Bottleneck → Equipment Issue                 │
│                                                                       │
│  • Machine Learning Feature Attribution                             │
│    ├─ SHAP Values for Process Impact                               │
│    ├─ Feature Importance Ranking                                    │
│    └─ Interaction Effects                                           │
│                                                                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  IMPACT ESTIMATION MODULE                            │
├─────────────────────────────────────────────────────────────────────┤
│  • Throughput Impact Calculator                                     │
│  • Quality Loss Estimator                                           │
│  • Cost Analysis Engine                                             │
│  • Profitability Predictor                                          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│               RECOMMENDATION & DECISION MODULE                       │
├─────────────────────────────────────────────────────────────────────┤
│  • Action Generator                                                 │
│    ├─ Process Parameter Adjustments                                │
│    ├─ Resource Reallocation                                        │
│    ├─ Quality Control Interventions                                │
│    └─ Maintenance Scheduling                                       │
│                                                                       │
│  • Priority Ranking (by ROI, Urgency, Feasibility)                 │
│  • Evidence Compilation                                             │
│  • Confidence & Uncertainty Reporting                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│                    Interactive Dashboard (Streamlit/React)           │
├───────────────────┬──────────────────┬──────────────────────────────┤
│  Quality Monitor  │  Process Health  │  Decision Support            │
│  • Defect feed    │  • Utilization   │  • Root cause analysis       │
│  • Classification │  • Bottlenecks   │  • Impact estimates          │
│  • Localization   │  • Queue status  │  • Recommendations           │
│  • Confidence     │  • Throughput    │  • What-if scenarios         │
└───────────────────┴──────────────────┴──────────────────────────────┘
```

### Architecture Components

#### 1. **Visual Analysis Module**
- **Input**: 512x512 grayscale product images
- **Model**: Transfer learning with pretrained CNN (ResNet18/EfficientNet-B0)
- **Output**: 
  - Class prediction (5 categories)
  - Confidence score
  - Defect localization heatmap
  - Bounding boxes
  - Uncertainty flag

#### 2. **Process Analysis Module**
- **Input**: Manufacturing simulation data (CSV format)
- **Models**: 
  - Model 1: 10-feature simple bottleneck predictor
  - Model 2: 16-feature multi-product analyzer
  - Model 3: 77-feature comprehensive simulator
- **Output**:
  - Utilization predictions (Drilling, Milling, Assembly, etc.)
  - Queue time forecasts
  - Bottleneck identification
  - Throughput estimates

#### 3. **Correlation Engine**
- **Input**: Defect classifications + Process state vectors
- **Methods**:
  - Statistical correlation analysis
  - Time-series pattern matching
  - Causal inference algorithms
  - SHAP-based feature attribution
- **Output**:
  - Root cause hypotheses (ranked by likelihood)
  - Contributing factors
  - Evidence strength

#### 4. **Impact Estimation Module**
- **Input**: Defect rates + Process bottlenecks
- **Calculations**:
  - Throughput loss (parts/hour reduction)
  - Quality cost (scrap + rework)
  - Profitability impact ($/batch)
- **Output**: Economic impact dashboard

#### 5. **Recommendation Engine**
- **Input**: Root causes + Impact estimates
- **Logic**: Rule-based + optimization
- **Output**:
  - Ranked action items
  - Expected improvement
  - Implementation difficulty
  - Confidence level

---

## 📊 Datasets & Resources

### 1. Visual Inspection Dataset

**Location**: `/train` directory

| Class | Samples | Description |
|-------|---------|-------------|
| Normal | 2,400 | Defect-free products |
| Rust | 2,400 | Surface oxidation/corrosion |
| Crack | 2,400 | Linear fractures |
| Hole | 2,400 | Puncture defects |
| Scratch | 2,400 | Surface abrasions |
| **Total** | **12,000** | Balanced dataset |

**Image Properties**:
- Format: PNG (grayscale)
- Resolution: Variable (will normalize to 224x224 or 512x512)
- Quality: Moderate resolution, suitable for CNN training
- Distribution: Balanced across all classes (no class imbalance)

**Preprocessing Strategy**:
- Resize to fixed dimensions (224x224)
- Normalize pixel values [0, 1]
- Data augmentation: rotation (±15°), horizontal flip, brightness adjustment (±20%)
- Train/Val/Test split: 70/15/15

### 2. Manufacturing Simulation Datasets

**Location**: `/Manufacturing Data Shared Facility - Discrete-Event Simulation/`

#### Model 1: Simple Three-Stage Process
**File**: `Model 1/Model_1.csv`  
**Samples**: 3,000 rows  
**Features** (10):
1. `Demand` - Input demand rate
2. `Total parts` - Total parts processed
3. `Parts per hour` - Throughput rate
4. `VA Time` - Value-added time
5. `Drilling Waiting Time` - Queue time at drilling station
6. `Milling Waiting Time` - Queue time at milling station
7. `Assembly Waiting Time` - Queue time at assembly station
8. `Drilling Util` - Drilling resource utilization [0-1]
9. `Milling Util` - Milling resource utilization [0-1]
10. `Assembly Util` - Assembly resource utilization [0-1]

**Process Flow**: Raw Material → Drilling → Milling → Assembly → Storage

**Use Case**: Identify basic bottlenecks in sequential operations

#### Model 2: Multi-Product Assembly Line
**File**: `Model 2/Model_2.csv`  
**Samples**: 3,000 rows  
**Features** (16):
- Demand, Entities In/Out for Part 1 & Part 2
- VA Time, Queue Time, Storage Time per part type
- Utilization metrics for Drilling, Milling, Assembly stations

**Process Flow**: Two parallel part streams merging at assembly

**Use Case**: Multi-product scheduling and resource allocation

#### Model 3: Complex Manufacturing Facility
**File**: `Model 3/Model_3.csv`  
**Samples**: 3,000 rows  
**Features** (77):
- **Utilization Group**: Blanking, Press (1-4), Cell (1-4), Paint (1-2), Quality, Forklift
- **Queue Group**: Wait times at each station, by SKU type
- **Part Counters**: Cell counters by SKU (1-4), cycle counts, total products
- **Time Breakdown**: VA time, NVA time, transport time, wait time, other time per SKU
- **Warehouse**: Queue lengths at warehouses 1-4

**Process Flow**: Blanking → Pressing (4 stations) → Assembly Cells (4 cells) → Painting (2 lines) → Quality Check → Warehouse

**Use Case**: Enterprise-level process optimization with multiple SKUs and complex routing

#### Pre-trained MATLAB Models
**Location**: `/Matlab Models/`

Available pretrained neural networks:
- `Model1ANN.m` - Trained on Model 1 data
- `Model2ANNDrilling.m`, `Model2ANNMilling.m`, `Model2ANNAssembly.m` - Station-specific models
- Various configuration models (c1s2ANN.m, c2s4ANN.m, etc.)

**Implementation Options**:
1. Use MATLAB Engine API for Python to load `.m` files directly
2. Reverse-engineer network weights and implement in PyTorch/TensorFlow
3. Retrain from scratch using CSV data with scikit-learn/PyTorch

### 3. Additional Resources

- **3000Samplesv3.mat**: MATLAB workspace with extended training data
- **Model PDFs**: Process flow diagrams for each simulation model
- **ParametersFile.xls**: Configuration parameters for Model 3
- **Readme.txt**: Dataset documentation

---

## 🔬 Approach & Methodology

### Phase 1: Visual Defect Detection (Weeks 1-2)

#### Step 1.1: Data Preparation
- Load and organize image dataset
- Implement train/validation/test split (70/15/15)
- Create data loaders with augmentation pipeline
- Verify class distribution balance

#### Step 1.2: Model Development
- **Baseline**: Simple CNN (3 conv layers) for baseline performance
- **Primary Model**: Transfer learning with ResNet18 (pretrained on ImageNet)
  - Replace final FC layer for 5-class output
  - Freeze early layers, fine-tune later layers
- **Alternative**: EfficientNet-B0 for comparison
- **Training**:
  - Loss: Cross-entropy
  - Optimizer: Adam (lr=1e-4)
  - Batch size: 32
  - Epochs: 50 with early stopping
  - Metrics: Accuracy, F1-score, per-class precision/recall

#### Step 1.3: Defect Localization
- Implement Grad-CAM (Gradient-weighted Class Activation Mapping)
- Generate heatmaps highlighting discriminative regions
- Extract bounding boxes from high-activation areas
- Validate localization accuracy on test set

#### Step 1.4: Uncertainty Quantification
- **Method 1**: Monte Carlo Dropout (run 20 forward passes, measure variance)
- **Method 2**: Ensemble of 3-5 models with different initializations
- **Threshold tuning**: Flag predictions with confidence < 0.70 as uncertain
- **OOD Detection**: Train autoencoder to detect novel defect patterns

**Expected Outcomes**:
- Classification accuracy: >92%
- Localization IoU: >0.65
- Uncertainty detection AUROC: >0.85

### Phase 2: Process Analysis & Bottleneck Detection (Weeks 2-3)

#### Step 2.1: Data Exploration
- Load and analyze Model 1, 2, 3 CSV files
- Explore feature distributions and correlations
- Identify key bottleneck indicators:
  - Utilization > 0.95 → Resource constraint
  - Queue time > threshold → Bottleneck upstream
  - Low VA time ratio → Process inefficiency

#### Step 2.2: Process Prediction Models
- **Option A**: Retrain in Python
  - Use sklearn MLPRegressor for neural networks
  - Replicate MATLAB architecture (10 hidden units, tanh activation)
  - Train separate models for Model 1, 2, 3
- **Option B**: Port MATLAB models
  - Extract weights from .m files
  - Implement equivalent PyTorch/TensorFlow architecture
  
- **Targets**:
  - Predict utilization rates given demand
  - Forecast queue times under different scenarios
  - Estimate throughput capacity

#### Step 2.3: Bottleneck Identification Algorithm
```python
def identify_bottlenecks(process_data):
    bottlenecks = []
    
    # Rule 1: High utilization
    for station, util in process_data['utilization'].items():
        if util > 0.90:
            bottlenecks.append({
                'station': station,
                'type': 'Capacity Constraint',
                'severity': 'High' if util > 0.95 else 'Medium',
                'metric': f'Utilization: {util:.2%}'
            })
    
    # Rule 2: Queue buildup
    for station, queue_time in process_data['queue_times'].items():
        if queue_time > threshold:
            bottlenecks.append({
                'station': station,
                'type': 'Queue Buildup',
                'severity': calculate_severity(queue_time),
                'metric': f'Queue Time: {queue_time:.2f}h'
            })
    
    # Rule 3: Throughput mismatch
    if detect_cycle_time_imbalance(process_data):
        bottlenecks.append({...})
    
    return sorted(bottlenecks, key=lambda x: severity_score(x))
```

**Expected Outcomes**:
- Process prediction R²: >0.85
- Bottleneck detection accuracy: >80%
- Explain 90%+ of throughput variation

### Phase 3: Root-Cause Correlation (Week 3)

#### Step 3.1: Correlation Analysis

**Hypothesis-Driven Approach**:

| Defect Type | Likely Root Causes | Process Indicators |
|-------------|-------------------|-------------------|
| **Rust** | Long storage time, environmental exposure | High queue times, warehouse buildup |
| **Crack** | Mechanical stress, overload | High utilization at drilling/pressing |
| **Hole** | Tool wear, equipment failure | Drilling bottleneck, maintenance needed |
| **Scratch** | Handling damage, transport issues | High forklift utilization, material flow problems |
| **Normal** (baseline) | Optimal process conditions | Balanced utilization, low queues |

**Statistical Methods**:
1. Pearson correlation between defect rates and process metrics
2. Time-lagged correlation (defect appears N hours after process anomaly)
3. Multivariate regression: `Defect_Rate ~ f(Utilization, Queue_Time, Demand, ...)`

#### Step 3.2: Feature Importance Analysis
- Train gradient boosting model: Process Features → Defect Probability
- Calculate SHAP values for each feature
- Identify top-5 contributing factors per defect type
- Visualize feature importance rankings

#### Step 3.3: Rule-Based Expert System
Implement domain-knowledge rules:
```python
rules = {
    'rust_high_queue': {
        'condition': lambda d: d['defect'] == 'rust' and d['queue_time'] > 2.0,
        'root_cause': 'Excessive waiting time causing surface oxidation',
        'recommendation': 'Reduce queue buildup; increase downstream capacity',
        'confidence': 0.85
    },
    'crack_overload': {
        'condition': lambda d: d['defect'] == 'crack' and d['drilling_util'] > 0.95,
        'root_cause': 'Overloaded drilling station causing material stress',
        'recommendation': 'Add drilling capacity or reduce throughput rate',
        'confidence': 0.78
    },
    # ... more rules
}
```

**Expected Outcomes**:
- Identify root cause in >75% of defect cases
- Provide plausible explanation with evidence
- Confidence-weighted recommendations

### Phase 4: Impact Estimation (Week 4)

#### Step 4.1: Economic Model Development

**Throughput Impact**:
```
Throughput_Loss = Baseline_Throughput × (Defect_Rate - Target_Defect_Rate)
```

**Quality Cost**:
```
Quality_Cost = (Scrap_Cost × Scrapped_Units) + (Rework_Cost × Reworked_Units)
```

**Profitability Impact**:
```
Profit_Loss = Revenue_Loss - Cost_Savings_from_Reduced_Output
```

#### Step 4.2: Scenario Analysis
- Simulate impact of identified bottlenecks
- Compare current state vs. optimal state
- Estimate improvement potential from recommendations

**Expected Outcomes**:
- Quantify cost of each defect type
- Estimate ROI of recommended interventions
- Provide confidence intervals on estimates

### Phase 5: Decision Support System (Week 4-5)

#### Step 5.1: Recommendation Engine

**Action Generator**:
- Process parameter adjustments (e.g., "Reduce demand by 10%")
- Resource allocation (e.g., "Add second milling station")
- Quality interventions (e.g., "Increase inspection frequency at drilling")
- Maintenance (e.g., "Schedule preventive maintenance")

**Ranking Criteria**:
1. Expected impact (% improvement)
2. Implementation cost (Low/Medium/High)
3. Feasibility (timeline, resources)
4. Confidence level

#### Step 5.2: Dashboard Development

**Streamlit Dashboard Structure**:
```
├── Home: Executive Summary
│   ├── Overall defect rate trend
│   ├── Current bottlenecks
│   └── Top-3 recommendations
│
├── Visual Inspection
│   ├── Image upload widget
│   ├── Real-time classification
│   ├── Defect localization viewer
│   └── Confidence scores
│
├── Process Health
│   ├── Utilization gauges per station
│   ├── Queue time charts
│   ├── Throughput vs. target
│   └── Bottleneck alerts
│
├── Root Cause Analysis
│   ├── Defect-process correlation matrix
│   ├── Feature importance charts
│   ├── Timeline view (defect events + process events)
│   └── Evidence panel
│
├── Impact & Recommendations
│   ├── Economic impact dashboard
│   ├── Ranked recommendations list
│   ├── What-if scenario simulator
│   └── Action plan generator
│
└── Settings & Diagnostics
    ├── Model performance metrics
    ├── Confidence calibration
    ├── Data quality checks
    └── System logs
```

**Expected Outcomes**:
- User-friendly interface operational clarity score >4/5
- Real-time inference <3 seconds per image
- Interactive visualizations with drill-down capability

### Phase 6: Testing & Validation (Week 5-6)

#### Step 6.1: Component Testing
- Visual model: Test on held-out set, validate localization manually
- Process models: Cross-validate predictions against simulation ground truth
- Correlation engine: Validate on synthetic scenarios with known causes

#### Step 6.2: Integration Testing
- End-to-end pipeline test with realistic data
- Stress testing with edge cases (novel defects, extreme process states)
- Robustness testing (varied lighting, orientations for images)

#### Step 6.3: Validation Metrics

| Component | Metric | Target |
|-----------|--------|--------|
| Defect Classification | Accuracy | >92% |
| Defect Classification | F1-Score (weighted) | >0.90 |
| Localization | IoU | >0.65 |
| False-Reject Rate | % | <5% |
| Uncertainty Detection | AUROC | >0.85 |
| Process Prediction | R² | >0.85 |
| Bottleneck Detection | Precision | >80% |
| Root-Cause Accuracy | % correct | >75% |
| Recommendation Quality | Expert rating | >4/5 |

---

## 🛠️ Technical Stack

### Core Technologies

**Deep Learning & Computer Vision**:
- PyTorch 2.0+ (primary framework)
- torchvision (pretrained models, transforms)
- OpenCV (image processing)
- Pillow (image I/O)
- timm (PyTorch Image Models - for EfficientNet)

**Machine Learning & Analysis**:
- scikit-learn (preprocessing, classical ML, metrics)
- pandas (data manipulation)
- numpy (numerical operations)
- scipy (statistics, MATLAB file I/O)

**Explainability & Visualization**:
- SHAP (feature importance)
- matplotlib, seaborn (static plots)
- plotly (interactive charts)
- grad-cam (localization)

**Dashboard & UI**:
- Streamlit (rapid dashboard development)
- Gradio (alternative for simple interfaces)
- FastAPI (optional - for REST API backend)

**Development Tools**:
- Jupyter Notebook (experimentation)
- Docker (containerization)
- Git (version control)
- pytest (testing)

### Environment Setup

```bash
# Python 3.9+
pip install torch torchvision torchaudio
pip install opencv-python pillow
pip install pandas numpy scipy scikit-learn
pip install matplotlib seaborn plotly
pip install shap
pip install streamlit gradio
pip install timm grad-cam
pip install pytest black flake8
```

### Hardware Requirements

**Minimum**:
- CPU: 4+ cores
- RAM: 16GB
- Storage: 10GB

**Recommended**:
- GPU: NVIDIA GPU with 6GB+ VRAM (RTX 3060 or better)
- RAM: 32GB
- Storage: 20GB SSD

**Cloud Alternatives**:
- Google Colab (free GPU)
- Kaggle Notebooks
- AWS SageMaker / Azure ML Studio

---

## 📅 Implementation Roadmap

### Week 1-2: Foundation & Visual System
- [x] Dataset organization and exploration
- [ ] Implement data loaders with augmentation
- [ ] Train baseline CNN model
- [ ] Implement transfer learning (ResNet18)
- [ ] Add Grad-CAM localization
- [ ] Implement uncertainty quantification
- **Milestone**: Working defect classifier with >85% accuracy

### Week 3: Process Analysis
- [ ] Load and explore manufacturing simulation data
- [ ] Retrain/port process prediction models
- [ ] Implement bottleneck detection algorithm
- [ ] Validate process models against ground truth
- **Milestone**: Bottleneck identification system operational

### Week 4: Integration & Correlation
- [ ] Build correlation analysis module
- [ ] Implement rule-based expert system
- [ ] Train SHAP-based feature attribution
- [ ] Develop impact estimation models
- [ ] Create recommendation engine
- **Milestone**: End-to-end pipeline functional

### Week 5: Dashboard & Refinement
- [ ] Develop Streamlit dashboard (all tabs)
- [ ] Integrate all backend components
- [ ] Implement real-time inference
- [ ] Add what-if scenario simulator
- **Milestone**: Complete interactive system

### Week 6: Testing & Documentation
- [ ] Comprehensive testing (unit, integration, end-to-end)
- [ ] Performance optimization
- [ ] Documentation (code comments, API docs, user guide)
- [ ] Prepare presentation materials
- **Milestone**: Production-ready system

### Checkpoint Deliverables

| Checkpoint | Due | Deliverable | Marks |
|------------|-----|-------------|-------|
| **CP1** | Week 2 | README (this document) | 15 |
| **CP2** | Week 4 | Partial execution (visual OR process working) | 25 |
| **CP3** | Week 6 | Complete system with dashboard | 60 |

---

## 🎯 Expected Outcomes

### Technical Deliverables

1. **Trained Models**:
   - Defect classification CNN (>92% accuracy)
   - Process prediction models (R² >0.85)
   - Root-cause correlation model

2. **Software System**:
   - End-to-end Python pipeline
   - Interactive web dashboard
   - REST API (optional)
   - Docker container (optional)

3. **Documentation**:
   - This README
   - Code documentation (docstrings)
   - User guide
   - Technical report

### Business Value

1. **Quality Improvement**:
   - Reduce defect rate by identifying root causes early
   - Decrease false-reject rate (minimize unnecessary scrap)
   - Improve inspection consistency

2. **Operational Efficiency**:
   - Identify and resolve bottlenecks faster
   - Optimize resource utilization
   - Reduce work-in-process inventory

3. **Cost Savings**:
   - Reduce scrap and rework costs
   - Increase throughput without capital investment
   - Data-driven maintenance scheduling

4. **Decision Support**:
   - Evidence-based recommendations
   - What-if scenario planning
   - Continuous process improvement

### Key Performance Indicators

| KPI | Target | Measurement |
|-----|--------|-------------|
| Defect Detection Accuracy | >92% | Test set performance |
| False-Reject Rate | <5% | Specificity on normal class |
| Localization Precision | IoU >0.65 | Bounding box overlap |
| Bottleneck ID Accuracy | >80% | Validation against simulation |
| Root-Cause Explanation | >75% | Manual expert evaluation |
| System Response Time | <3s | End-to-end inference time |
| User Satisfaction | >4/5 | Usability survey |

---

## 🔒 Limitations & Future Work

### Current Limitations

1. **No Real-Time Hardware Integration**: System is software-only, advisory mode
2. **Synthetic Correlation**: Defect-process links are inferred/simulated, not from real production data
3. **Limited Defect Types**: Only 5 classes trained; novel categories require retraining
4. **Static Process Models**: Based on discrete-event simulation, not live data
5. **Uncertainty**: Confidence scores are estimates; human oversight recommended

### Future Enhancements

1. **Live Integration**: Connect to factory SCADA/MES systems for real-time data
2. **Expanded Defect Library**: Add more defect types via active learning
3. **Temporal Modeling**: Time-series forecasting for proactive alerts
4. **Multi-Site**: Scale to multiple production lines and facilities
5. **Reinforcement Learning**: Optimize process parameters automatically
6. **Mobile App**: Field inspector interface for on-the-go analysis

---

## 📚 References

### Datasets
- Manufacturing Data Shared Facility - Discrete-Event Simulation (provided)
- Synthetic Surface Defect Dataset (provided)

### Key Papers & Methods
- Grad-CAM: Visual Explanations from Deep Networks (Selvaraju et al., 2017)
- Transfer Learning for Image Classification (Yosinski et al., 2014)
- SHAP: A Unified Approach to Interpreting Model Predictions (Lundberg et al., 2017)
- Bottleneck Detection in Manufacturing (Roser et al., 2002)

### Tools & Libraries
- PyTorch: https://pytorch.org/
- Streamlit: https://streamlit.io/
- SHAP: https://github.com/slundberg/shap
- Grad-CAM: https://github.com/jacobgil/pytorch-grad-cam

---

## 👥 Team & Contact

**Team Name**: [Your Team Name]  
**Institution**: [Your Institution]  
**Contact**: [email@domain.com]

**Roles**:
- Computer Vision Lead: [Name]
- Process Analytics Lead: [Name]
- Full-Stack Developer: [Name]
- Domain Expert / PM: [Name]

---

## 📄 License

This project is developed for NEURAX Hackathon 3.0 educational purposes.

---

**Last Updated**: September 19, 2026  
**Version**: 1.0  
**Status**: Checkpoint 1 - Architecture & Planning Phase Complete ✅
