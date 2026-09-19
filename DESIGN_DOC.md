# System Design Document
## Visual Inspection & Defect Root-Cause Assistant
### NEURAX Hackathon 3.0 - Domain 2: AI in Industry and Automation

**Version**: 1.0  
**Date**: September 19, 2026  
**Status**: Design Phase

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Frontend Architecture](#3-frontend-architecture)
4. [Backend Architecture](#4-backend-architecture)
5. [Machine Learning Models](#5-machine-learning-models)
6. [Data Layer](#6-data-layer)
7. [API Specifications](#7-api-specifications)
8. [Input/Output Specifications](#8-inputoutput-specifications)
9. [Technology Stack](#9-technology-stack)
10. [Deployment Architecture](#10-deployment-architecture)
11. [Security & Performance](#11-security--performance)
12. [Implementation Timeline](#12-implementation-timeline)

---

## 1. Executive Summary

### 1.1 Project Goal
Build a unified industrial decision-support system that analyzes visual inspection images and manufacturing process data to:
- Detect and classify product defects (5 classes: normal, rust, crack, hole, scratch)
- Localize defects with spatial precision (heatmaps and bounding boxes)
- Identify manufacturing bottlenecks and root causes
- Predict economic impact (throughput loss, profitability)
- Generate evidence-based process recommendations

### 1.2 Key Features
- **Multi-input support**: 
  - **Inspection Data**: Single image, batch upload (ZIP), or drag-and-drop multiple PNG files
  - **Production Data**: CSV upload (Model 1/2/3 simulation data)
  - **Economic Data**: CSV upload (cost parameters, production metrics)
- **Real-time inference**: <3 seconds per image for defect detection
- **Interactive dashboard**: Visualize defects, process health, root causes, and recommendations
- **What-if simulator**: Test process parameter changes before implementation
- **AI Copilot**: Natural language Q&A for explanations

### 1.3 System Constraints
- **Software-only**: No hardware integration, live camera feeds, or PLC connections
- **Advisory mode**: All recommendations are simulated/advisory
- **Offline-capable**: Can process uploaded data without continuous data streams

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                              │
│                     (Next.js + React + TypeScript)                   │
├──────────────────┬──────────────────┬────────────────────────────────┤
│  Upload Module   │  Dashboard View  │  AI Copilot Chat              │
│  • Single Image  │  • Quality View  │  • Natural Language Q&A       │
│  • Batch Upload  │  • Process View  │  • Evidence Explanations      │
│  • ZIP Extract   │  • Root Cause    │                               │
│                  │  • What-if Sim   │                               │
└────────┬─────────┴────────┬─────────┴─────────────┬─────────────────┘
         │                  │                       │
         │     HTTPS/REST API (FastAPI)           │
         │                  │                       │
┌────────▼──────────────────▼───────────────────────▼─────────────────┐
│                        BACKEND SERVICES                              │
├─────────────────┬──────────────────────┬───────────────────────────┤
│  Image Service  │  Process Service     │  Analysis Service         │
│  • Validation   │  • CSV Processing    │  • Root Cause Engine      │
│  • Preprocessing│  • Bottleneck Detect │  • Impact Estimation      │
│  • Inference    │  • Simulation Run    │  • Recommendations        │
│  • Localization │  • Economic Calc     │  • SHAP Explanations      │
└────────┬────────┴──────────┬───────────┴──────────┬────────────────┘
         │                   │                      │
         │         ML MODEL LAYER                   │
         │                   │                      │
┌────────▼───────────────────▼──────────────────────▼────────────────┐
│                      INFERENCE ENGINES                              │
├──────────────────┬──────────────────────┬─────────────────────────┤
│  Vision Model    │  Process Model       │  Correlation Model      │
│  • EfficientNet  │  • XGBoost Regressor │  • XGBoost Classifier   │
│  • Grad-CAM      │  • CUSUM Detector    │  • SHAP Explainer       │
│  • MC Dropout    │  • Little's Law      │  • Statistical Tests    │
│  • OOD Detection │  • Utilization Calc  │                         │
└──────────────────┴──────────────────────┴─────────────────────────┘
         │                   │                      │
┌────────▼───────────────────▼──────────────────────▼────────────────┐
│                         DATA LAYER                                  │
├──────────────────┬──────────────────────┬─────────────────────────┤
│  PostgreSQL DB   │  File Storage        │  Cache Layer            │
│  • User sessions │  • Uploaded images   │  • Redis (optional)     │
│  • Batch results │  • Model weights     │  • Inference cache      │
│  • Process logs  │  • CSV datasets      │                         │
└──────────────────┴──────────────────────┴─────────────────────────┘
```

### 2.2 Data Flow

```
USER INPUT 
    ├─ Images (ZIP/PNG) → Inspection Data
    ├─ CSV (Model 1/2/3) → Production Data
    └─ CSV (Economic) → Cost/Economic Data
    ↓
FRONTEND: Upload & Extract
    ↓
API: /upload/* → File validation & routing
    ↓
    ├─ IMAGE SERVICE: Preprocess images
    │   ↓
    │   VISION MODEL: Classify + Localize (parallel)
    │
    └─ DATA SERVICE: Parse & validate CSVs
        ↓
        PROCESS SERVICE: Load simulation data + economic params
    ↓
ANALYSIS SERVICE: Correlate defects ↔ process ↔ economics
    ↓
RECOMMENDATION ENGINE: Generate actions
    ↓
FRONTEND: Display results + visualizations
```

---

## 3. Frontend Architecture

### 3.1 Technology Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.2
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand (lightweight, modern)
- **Charts**: Apache ECharts (high-performance industrial charts)
- **Diagrams**: React Flow (process flow graphs)
- **Animations**: Framer Motion
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form + Zod validation

### 3.2 Component Structure

```
app/
├── layout.tsx                      # Root layout
├── page.tsx                        # Home/landing page
├── dashboard/
│   ├── layout.tsx                  # Dashboard layout with nav
│   ├── page.tsx                    # Dashboard home
│   ├── upload/
│   │   └── page.tsx                # Upload interface
│   ├── quality/
│   │   └── page.tsx                # Quality monitoring view
│   ├── process/
│   │   └── page.tsx                # Process health view
│   ├── analysis/
│   │   └── page.tsx                # Root cause analysis
│   ├── simulator/
│   │   └── page.tsx                # What-if simulator
│   └── copilot/
│       └── page.tsx                # AI Copilot chat
├── api/                            # API route handlers (Next.js API routes)
│   └── proxy/
│       └── [...path].ts            # Proxy to FastAPI backend
└── globals.css

components/
├── ui/                             # shadcn/ui base components
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── input.tsx
│   ├── slider.tsx
│   └── ...
├── upload/
│   ├── ImageUploader.tsx           # Image drag-and-drop + file picker
│   ├── CSVUploader.tsx             # CSV file upload component
│   ├── BatchUploader.tsx           # ZIP file handler
│   ├── DatasetManager.tsx          # Manage all uploaded datasets
│   └── ProgressBar.tsx             # Upload progress
├── visualization/
│   ├── DefectHeatmap.tsx           # Grad-CAM overlay on image
│   ├── ConfusionMatrix.tsx         # Model performance
│   ├── ProcessFlowDiagram.tsx      # React Flow diagram
│   ├── UtilizationGauge.tsx        # Gauge charts
│   ├── TimelineChart.tsx           # CUSUM timeline
│   └── ShapWaterfall.tsx           # SHAP explanation chart
├── analysis/
│   ├── DefectCard.tsx              # Individual defect result
│   ├── BottleneckAlert.tsx         # Bottleneck warning card
│   ├── RootCauseGraph.tsx          # Correlation graph
│   └── RecommendationList.tsx      # Ranked recommendations
├── simulator/
│   ├── ParameterSlider.tsx         # Adjustable parameters
│   ├── ScenarioComparison.tsx      # Before/after comparison
│   └── ImpactPreview.tsx           # Estimated impact
└── copilot/
    ├── ChatInterface.tsx           # Chat UI
    ├── MessageBubble.tsx           # Message display
    └── EvidencePanel.tsx           # Supporting evidence display

lib/
├── api.ts                          # API client functions
├── types.ts                        # TypeScript types/interfaces
├── utils.ts                        # Utility functions
└── store.ts                        # Zustand state management

public/
├── icons/
└── sample-data/                    # Demo data for testing
```

### 3.3 Key Frontend Features

#### 3.3.1 Upload Module
```typescript
// Input handling modes
interface UploadOptions {
  dataType: 'inspection' | 'production' | 'economic';
  mode: 'single' | 'batch' | 'zip' | 'csv';
  maxFiles: number;        // Default: 100 for batch images
  maxSize: number;         // Default: 50MB per image, 20MB per CSV
  allowedTypes: string[];  // ['image/png'] or ['text/csv']
}

// === INSPECTION DATA (Images) ===

// Single image upload
POST /api/upload/inspection/single
  - Accepts: PNG image
  - Returns: { imageId, preview_url, status }

// Batch upload (multiple PNGs)
POST /api/upload/inspection/batch
  - Accepts: FormData with multiple PNG files
  - Returns: { batchId, images: [...], status }

// ZIP upload (extracts and processes images AND CSVs)
POST /api/upload/zip
  - Accepts: ZIP file containing:
      * PNG/JPG images (inspection data)
      * CSV files (production/economic data)
  - Extracts and routes files by type
  - Returns: { 
      batchId, 
      extracted: {
        images: { count, files },
        production_csv: { count, files, model_types },
        economic_csv: { count, files }
      },
      status 
    }

// === PRODUCTION DATA (CSV) ===

// Upload production/process data
POST /api/upload/production/csv
  - Accepts: CSV file (Model 1: 10 cols, Model 2: 16 cols, Model 3: 77 cols)
  - Validates: Column names, data types, row count
  - Returns: { datasetId, modelType, rowCount, columns, preview }

// === ECONOMIC DATA (CSV) ===

// Upload economic parameters
POST /api/upload/economic/csv
  - Accepts: CSV with cost parameters
  - Required columns: scrap_cost, rework_cost, contribution_margin, etc.
  - Returns: { economicDataId, parameters, status }

// === DATASET MANAGEMENT ===

// List all uploaded datasets
GET /api/datasets
  - Returns: { 
      inspection: [...], 
      production: [...], 
      economic: [...] 
    }

// Link datasets for analysis
POST /api/datasets/link
  - Body: { 
      inspectionBatchId, 
      productionDatasetId, 
      economicDataId 
    }
  - Returns: { analysisId, linkedDatasets }
```

#### 3.3.2 Dashboard Views

**Quality View**:
- Grid of uploaded images with classification labels
- Color-coded by defect type (red=defective, green=normal)
- Confidence score badges
- Click to view Grad-CAM heatmap

**Process View**:
- Station utilization gauges (0-100%)
- Queue time bar charts per station
- Throughput trend line (parts/hour)
- Bottleneck alerts (pulsing red indicators)

**Root Cause Analysis**:
- Correlation matrix heatmap (defects vs. process params)
- SHAP waterfall chart (feature importance)
- CUSUM timeline (process drift detection)
- Evidence strength indicators

**What-if Simulator**:
- Parameter sliders: Demand, Station Capacity, Queue Limits
- Side-by-side comparison: Current vs. Simulated
- Metrics: Throughput, Cost, Margin, Defect Rate
- "Apply Recommendation" quick actions

**AI Copilot**:
- Chat interface with message history
- Pre-computed Q&A retrieval (no hallucination)
- Evidence citations with links to data
- Export conversation as PDF

---

## 4. Backend Architecture

### 4.1 Technology Stack
- **Framework**: FastAPI 0.105+
- **Language**: Python 3.10
- **ASGI Server**: Uvicorn
- **Validation**: Pydantic v2
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Task Queue**: Celery + Redis (for long-running batch jobs)
- **File Storage**: Local filesystem (or AWS S3 for production)
- **Logging**: Loguru
- **Testing**: pytest

### 4.2 Project Structure

```
backend/
├── app/
│   ├── main.py                     # FastAPI app entry point
│   ├── config.py                   # Configuration settings
│   ├── database.py                 # Database connection
│   ├── dependencies.py             # Shared dependencies
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── upload.py       # Upload endpoints
│   │   │   │   ├── inference.py    # Inference endpoints
│   │   │   │   ├── process.py      # Process analysis endpoints
│   │   │   │   ├── analysis.py     # Root cause endpoints
│   │   │   │   ├── simulator.py    # What-if simulator
│   │   │   │   └── copilot.py      # AI Copilot endpoints
│   │   │   └── api.py              # API router aggregation
│   │   └── deps.py
│   │
│   ├── core/
│   │   ├── security.py             # Auth (if needed)
│   │   ├── logging.py              # Logging config
│   │   └── exceptions.py           # Custom exceptions
│   │
│   ├── models/                     # SQLAlchemy models
│   │   ├── batch.py
│   │   ├── image.py
│   │   ├── result.py
│   │   └── process_log.py
│   │
│   ├── schemas/                    # Pydantic schemas
│   │   ├── upload.py
│   │   ├── inference.py
│   │   ├── process.py
│   │   └── analysis.py
│   │
│   ├── services/                   # Business logic
│   │   ├── image_service.py        # Image handling
│   │   ├── csv_service.py          # CSV upload & validation
│   │   ├── data_integration_service.py  # Link datasets
│   │   ├── inference_service.py    # ML inference
│   │   ├── process_service.py      # Process analysis
│   │   ├── correlation_service.py  # Root cause analysis
│   │   ├── simulator_service.py    # What-if simulation
│   │   └── recommendation_service.py
│   │
│   ├── ml/                         # ML components
│   │   ├── models/
│   │   │   ├── vision_model.py     # EfficientNet wrapper
│   │   │   ├── process_model.py    # XGBoost wrapper
│   │   │   └── correlation_model.py
│   │   ├── preprocessing/
│   │   │   ├── image_transform.py
│   │   │   └── data_transform.py
│   │   ├── postprocessing/
│   │   │   ├── gradcam.py          # Grad-CAM implementation
│   │   │   ├── uncertainty.py      # MC Dropout
│   │   │   └── localization.py     # Bounding box extraction
│   │   ├── explainability/
│   │   │   ├── shap_explainer.py
│   │   │   └── feature_importance.py
│   │   └── utils/
│   │       ├── model_loader.py
│   │       └── device_utils.py
│   │
│   ├── utils/
│   │   ├── file_utils.py           # File I/O utilities
│   │   ├── zip_handler.py          # ZIP extraction
│   │   ├── validators.py           # Input validation
│   │   └── metrics.py              # Performance metrics
│   │
│   └── workers/                    # Background tasks
│       ├── batch_processor.py      # Celery tasks for batch
│       └── tasks.py
│
├── tests/
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_ml/
│
├── alembic/                        # Database migrations
│   ├── versions/
│   └── env.py
│
├── weights/                        # Model checkpoints
│   ├── efficientnet_b4_defect.pth
│   ├── xgboost_process.pkl
│   └── xgboost_correlation.pkl
│
├── data/
│   ├── uploads/                    # Uploaded files
│   ├── processed/                  # Processed data
│   └── results/                    # Inference results
│
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### 4.3 Core Services

#### 4.3.1 Image Service
```python
class ImageService:
    """Handles image upload, validation, and preprocessing"""
    
    async def upload_single(self, file: UploadFile) -> ImageMetadata:
        """
        Upload and validate single image
        Returns: ImageMetadata with ID, path, size, hash
        """
        pass
    
    async def upload_batch(self, files: List[UploadFile]) -> BatchMetadata:
        """
        Upload multiple images
        Returns: BatchMetadata with IDs and status
        """
        pass
    
    async def extract_zip(self, zip_file: UploadFile) -> BatchMetadata:
        """
        Extract PNG files from ZIP
        Also identifies and routes CSV files to CSVService
        Returns: BatchMetadata with extracted images
        """
        pass
    
    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """
        Preprocess image for model input
        - Resize to 224x224
        - Normalize
        - Convert to tensor
        """
        pass
```

#### 4.3.4 Inference Service
```python
class InferenceService:
    """ML model inference orchestration"""
    
    def __init__(self):
        self.vision_model = VisionModel()
        self.gradcam = GradCAM(self.vision_model)
    
    async def classify_single(self, image_id: str) -> DefectResult:
        """
        Classify single image
        Returns: class, confidence, is_uncertain
        """
        pass
    
    async def classify_batch(self, batch_id: str) -> List[DefectResult]:
        """
        Classify batch of images (parallel processing)
        """
        pass
    
    async def localize_defect(self, image_id: str, defect_class: str) -> Localization:
        """
        Generate Grad-CAM heatmap and bounding boxes
        Returns: heatmap_url, bboxes
        """
        pass
    
    def estimate_uncertainty(self, image_tensor: torch.Tensor) -> float:
        """
        Monte Carlo Dropout uncertainty estimation
        Returns: uncertainty score [0-1]
        """
        pass
```

#### 4.3.5 Process Service
```python
class ProcessService:
    """Manufacturing process analysis"""
    
    def __init__(self):
        self.process_model = ProcessModel()
    
    def load_simulation_data(self, model_type: str) -> pd.DataFrame:
        """
        Load Model 1/2/3 CSV data
        """
        pass
    
    def detect_bottlenecks(self, process_data: pd.DataFrame) -> List[Bottleneck]:
        """
        Identify bottlenecks using:
        - Utilization > 85%
        - Growing queue depth
        - CUSUM drift detection
        """
        pass
    
    def calculate_utilization(self, process_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate per-station utilization rates
        """
        pass
    
    def apply_littles_law(self, wip: float, throughput: float) -> float:
        """
        L = λW (WIP = Arrival Rate × Wait Time)
        """
        pass
    
    def calculate_economic_impact(self, defects: List[DefectResult], 
                                   process_state: Dict) -> EconomicImpact:
        """
        Calculate: scrap cost + rework cost + throughput loss
        """
        pass
```

#### 4.3.6 Correlation Service
```python
class CorrelationService:
    """Root-cause correlation analysis"""
    
    def __init__(self):
        self.correlation_model = CorrelationModel()
        self.shap_explainer = ShapExplainer(self.correlation_model)
    
    def correlate_defects_with_process(self, 
                                       defects: List[DefectResult],
                                       process_data: pd.DataFrame) -> CorrelationMatrix:
        """
        Statistical correlation:
        - Spearman rank correlation
        - Temporal alignment
        - PCA dimensionality reduction
        """
        pass
    
    def identify_root_causes(self, correlation_matrix: CorrelationMatrix) -> List[RootCause]:
        """
        Evidence-based root cause identification:
        - SHAP feature importance
        - Correlation strength
        - Temporal consistency
        """
        pass
    
    def explain_with_shap(self, defect_type: str, process_state: Dict) -> ShapExplanation:
        """
        Generate SHAP waterfall chart data
        """
        pass
```

#### 4.3.7 Simulator Service
```python
class SimulatorService:
    """What-if scenario simulation"""
    
    def simulate_scenario(self, 
                         baseline: ProcessState,
                         changes: Dict[str, float]) -> ScenarioResult:
        """
        Simulate process changes:
        - Adjust demand/capacity/resources
        - Propagate through process model
        - Calculate new throughput, cost, margin
        """
        pass
    
    def compare_scenarios(self, 
                         current: ScenarioResult,
                         proposed: ScenarioResult) -> Comparison:
        """
        Side-by-side comparison
        """
        pass
```

#### 4.3.8 Recommendation Service
```python
class RecommendationService:
    """Generate actionable recommendations"""
    
    def generate_recommendations(self, 
                                root_causes: List[RootCause],
                                bottlenecks: List[Bottleneck],
                                economic_impact: EconomicImpact) -> List[Recommendation]:
        """
        Rank recommendations by:
        - Impact (estimated improvement)
        - Feasibility (implementation difficulty)
        - Confidence (evidence strength)
        """
        pass
```

---

## 5. Machine Learning Models

### 5.1 Vision Model: Defect Classifier

#### 5.1.1 Architecture
```python
Model: EfficientNet-B4
Input: 224×224×3 RGB image
Output: 5-class softmax (normal, rust, crack, hole, scratch)

Architecture:
  - Pretrained EfficientNet-B4 backbone (ImageNet weights)
  - Global Average Pooling
  - Dropout(0.3)
  - Dense(512, ReLU)
  - Dropout(0.2)
  - Dense(5, Softmax)

Training:
  - Loss: CrossEntropyLoss
  - Optimizer: AdamW (lr=1e-4, weight_decay=1e-5)
  - LR Schedule: CosineAnnealingLR
  - Batch Size: 32
  - Epochs: 50 (with early stopping)
  - Data Split: 70/15/15 (train/val/test)
  - Augmentation: 
      * RandomRotation(±15°)
      * RandomHorizontalFlip(p=0.5)
      * ColorJitter(brightness=0.2, contrast=0.2)
      * RandomResizedCrop(224)
```

#### 5.1.2 Preprocessing Pipeline
```python
def preprocess_image(image_path: str) -> torch.Tensor:
    """
    1. Load image (PIL or cv2)
    2. Resize to 224×224
    3. Convert to RGB if grayscale
    4. Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    5. Convert to tensor
    """
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    return transform(image)
```

#### 5.1.3 Grad-CAM Implementation
```python
class GradCAM:
    """Gradient-weighted Class Activation Mapping"""
    
    def __init__(self, model: nn.Module, target_layer: str):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._register_hooks()
    
    def generate_heatmap(self, image: torch.Tensor, target_class: int) -> np.ndarray:
        """
        1. Forward pass → get activations
        2. Backward pass → get gradients
        3. Compute weights: α = GlobalAvgPool(gradients)
        4. Weighted sum: L_cam = ReLU(Σ α_k × A_k)
        5. Upsample to image size
        6. Normalize to [0, 1]
        """
        pass
```

#### 5.1.4 Uncertainty Quantification
```python
class MCDropout:
    """Monte Carlo Dropout for uncertainty estimation"""
    
    def predict_with_uncertainty(self, image: torch.Tensor, 
                                n_samples: int = 20) -> Tuple[int, float, float]:
        """
        1. Enable dropout at test time
        2. Run n_samples forward passes
        3. Collect predictions
        4. Mean prediction = mode of predictions
        5. Uncertainty = std of softmax probabilities
        """
        pass
```

### 5.2 Process Model: Bottleneck Predictor

#### 5.2.1 Architecture
```python
Model: XGBoost Regressor
Input: Process features (10/16/77 depending on model)
Output: Per-station utilization, queue times, throughput

Hyperparameters:
  - n_estimators: 200
  - max_depth: 6
  - learning_rate: 0.05
  - subsample: 0.8
  - colsample_bytree: 0.8

Training:
  - Loss: MSE (regression) or LogLoss (classification)
  - Cross-validation: 5-fold
  - Early stopping: 20 rounds
  - Feature importance: gain-based
```

#### 5.2.2 Feature Engineering
```python
def engineer_features(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    1. Utilization ratios
    2. Queue growth rate
    3. WIP levels
    4. Cycle time variance
    5. SKU mix percentages
    6. Time-based features (hour, shift)
    7. Rolling averages (window=10)
    8. Lag features (t-1, t-2)
    """
    pass
```

### 5.3 Correlation Model: Root-Cause Classifier

#### 5.3.1 Architecture
```python
Model: XGBoost Classifier
Input: Concatenated [defect_features, process_features]
Output: Root cause class (8 classes)

Root Cause Classes:
  1. High queue time → storage/waiting issue
  2. High utilization → overload/stress
  3. Tool wear → drilling/equipment issue
  4. Handling damage → transport issue
  5. Material quality → upstream supplier issue
  6. Process drift → parameter deviation
  7. Environmental → temperature/humidity
  8. Unknown → novel/uncertain

Training:
  - Synthetic labels generated from correlation rules
  - SMOTE for class imbalance
  - Class weights
```

#### 5.3.2 SHAP Explainer
```python
class ShapExplainer:
    """SHAP-based feature attribution"""
    
    def __init__(self, model: xgboost.Booster):
        self.explainer = shap.TreeExplainer(model)
    
    def explain(self, input_features: np.ndarray) -> shap.Explanation:
        """
        1. Compute SHAP values
        2. Rank features by |SHAP value|
        3. Generate waterfall chart data
        4. Return top-K contributing features
        """
        pass
```

### 5.4 Model Weights & Checkpoints

```
weights/
├── efficientnet_b4_defect_classifier.pth     # 77MB
│   ├── accuracy: 94.2%
│   ├── f1_score: 0.931
│   └── trained_on: 12,000 images
│
├── xgboost_process_model.pkl                 # 5MB
│   ├── r2_score: 0.87
│   └── trained_on: Model 1/2/3 CSVs
│
└── xgboost_correlation_model.pkl             # 3MB
    ├── accuracy: 81.3%
    └── synthetic_labels: True
```

---

## 6. Data Layer

### 6.1 Database Schema (PostgreSQL)

```sql
-- Batches
CREATE TABLE batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT NOW(),
    upload_type VARCHAR(10) CHECK (upload_type IN ('single', 'batch', 'zip')),
    total_images INT,
    status VARCHAR(20) DEFAULT 'pending',
    metadata JSONB
);

-- Images
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES batches(id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    file_path TEXT,
    file_size INT,
    file_hash VARCHAR(64),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Inference Results
CREATE TABLE defect_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_id UUID REFERENCES images(id) ON DELETE CASCADE,
    predicted_class VARCHAR(20),
    confidence FLOAT CHECK (confidence BETWEEN 0 AND 1),
    is_uncertain BOOLEAN,
    uncertainty_score FLOAT,
    heatmap_path TEXT,
    bboxes JSONB,
    inference_time_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Process Analysis Results
CREATE TABLE process_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES batches(id),
    model_type VARCHAR(10) CHECK (model_type IN ('model_1', 'model_2', 'model_3')),
    bottlenecks JSONB,
    utilization_rates JSONB,
    economic_impact JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Root Cause Analysis
CREATE TABLE root_causes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES batches(id),
    defect_type VARCHAR(20),
    root_cause_class VARCHAR(50),
    evidence JSONB,
    confidence FLOAT,
    shap_values JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recommendations
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES batches(id),
    title TEXT,
    description TEXT,
    impact_score FLOAT,
    feasibility_score FLOAT,
    priority INT,
    evidence_ids UUID[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_images_batch_id ON images(batch_id);
CREATE INDEX idx_defect_results_image_id ON defect_results(image_id);
CREATE INDEX idx_process_analysis_batch_id ON process_analysis(batch_id);
CREATE INDEX idx_root_causes_batch_id ON root_causes(batch_id);
CREATE INDEX idx_recommendations_batch_id ON recommendations(batch_id);
```

### 6.2 File Storage Structure

```
data/
├── uploads/
│   ├── {batch_id}/
│   │   ├── original/
│   │   │   ├── image_001.png
│   │   │   ├── image_002.png
│   │   │   └── ...
│   │   └── zip/
│   │       └── batch.zip
│
├── processed/
│   ├── {batch_id}/
│   │   ├── preprocessed/
│   │   │   ├── image_001_processed.pt
│   │   │   └── ...
│   │   └── heatmaps/
│   │       ├── image_001_gradcam.png
│   │       └── ...
│
├── results/
│   ├── {batch_id}/
│   │   ├── inference_results.json
│   │   ├── process_analysis.json
│   │   ├── root_causes.json
│   │   └── recommendations.json
│
└── cache/
    └── embeddings/                 # For AI Copilot retrieval
```

---

## 7. API Specifications

### 7.1 Upload Endpoints

#### POST /api/v1/upload/single
```typescript
Request:
  Content-Type: multipart/form-data
  Body: {
    file: File (PNG image)
  }

Response: {
  image_id: string,
  batch_id: string,
  file_name: string,
  file_size: number,
  preview_url: string,
  status: "uploaded" | "processing"
}

Errors:
  400: Invalid file type
  413: File too large (>50MB)
  500: Server error
```

#### POST /api/v1/upload/batch
```typescript
Request:
  Content-Type: multipart/form-data
  Body: {
    files: File[] (Multiple PNG images)
  }

Response: {
  batch_id: string,
  total_images: number,
  images: Array<{
    image_id: string,
    file_name: string,
    status: string
  }>,
  status: "uploaded" | "processing"
}
```

#### POST /api/v1/upload/zip
```typescript
Request:
  Content-Type: multipart/form-data
  Body: {
    file: File (ZIP archive)
  }

Response: {
  batch_id: string,
  extracted_count: number,
  images: Array<{
    image_id: string,
    file_name: string
  }>,
  status: "extracted" | "processing"
}
```

### 7.2 Inference Endpoints

#### POST /api/v1/inference/classify
```typescript
Request: {
  image_id: string,
  include_heatmap: boolean = false,
  uncertainty_estimation: boolean = true
}

Response: {
  image_id: string,
  prediction: {
    class: "normal" | "rust" | "crack" | "hole" | "scratch",
    confidence: number,        // 0-1
    probabilities: {
      normal: number,
      rust: number,
      crack: number,
      hole: number,
      scratch: number
    }
  },
  uncertainty: {
    is_uncertain: boolean,
    uncertainty_score: number  // 0-1
  },
  heatmap_url?: string,       // If include_heatmap=true
  inference_time_ms: number
}
```

#### POST /api/v1/inference/batch
```typescript
Request: {
  batch_id: string,
  options: {
    include_heatmaps: boolean,
    uncertainty_estimation: boolean
  }
}

Response: {
  batch_id: string,
  results: Array<{
    image_id: string,
    file_name: string,
    prediction: {...},
    uncertainty: {...}
  }>,
  summary: {
    total: number,
    normal: number,
    defective: number,
    uncertain: number
  },
  processing_time_ms: number
}
```

#### POST /api/v1/inference/localize
```typescript
Request: {
  image_id: string,
  defect_class: string
}

Response: {
  image_id: string,
  heatmap_url: string,
  bounding_boxes: Array<{
    x: number,
    y: number,
    width: number,
    height: number,
    confidence: number
  }>,
  overlay_url: string         // Original image + heatmap overlay
}
```

### 7.3 Process Analysis Endpoints

#### POST /api/v1/process/analyze
```typescript
Request: {
  batch_id: string,
  model_type: "model_1" | "model_2" | "model_3",
  process_data?: object       // Optional: custom process data
}

Response: {
  batch_id: string,
  model_type: string,
  bottlenecks: Array<{
    station: string,
    type: "capacity" | "queue" | "cycle_time",
    severity: "low" | "medium" | "high",
    utilization: number,
    queue_time: number,
    impact: string
  }>,
  utilization_rates: {
    [station: string]: number
  },
  throughput: {
    current: number,
    theoretical_max: number,
    efficiency: number
  },
  economic_impact: {
    scrap_cost: number,
    rework_cost: number,
    throughput_loss: number,
    total_loss: number
  }
}
```

### 7.4 Analysis Endpoints

#### POST /api/v1/analysis/root-cause
```typescript
Request: {
  batch_id: string,
  defect_type?: string        // Optional: filter by defect type
}

Response: {
  batch_id: string,
  root_causes: Array<{
    defect_type: string,
    root_cause_class: string,
    confidence: number,
    evidence: {
      correlations: Array<{
        parameter: string,
        correlation_coefficient: number,
        p_value: number
      }>,
      shap_values: Array<{
        feature: string,
        shap_value: number,
        feature_value: number
      }>,
      temporal_patterns: string
    },
    recommendation: string
  }>
}
```

#### POST /api/v1/analysis/impact
```typescript
Request: {
  batch_id: string
}

Response: {
  batch_id: string,
  economic_impact: {
    total_loss: number,
    breakdown: {
      scrap_cost: number,
      rework_cost: number,
      throughput_loss: number
    },
    by_defect_type: {
      [defect: string]: number
    },
    by_station: {
      [station: string]: number
    }
  },
  throughput_impact: {
    baseline_throughput: number,
    actual_throughput: number,
    loss_percentage: number
  }
}
```

### 7.5 Simulator Endpoints

#### POST /api/v1/simulator/scenario
```typescript
Request: {
  batch_id: string,
  baseline: {
    demand: number,
    capacity: {
      [station: string]: number
    },
    resources: {
      [resource: string]: number
    }
  },
  changes: {
    demand?: number,
    capacity?: {
      [station: string]: number
    },
    resources?: {
      [resource: string]: number
    }
  }
}

Response: {
  scenario_id: string,
  baseline: {
    throughput: number,
    cost: number,
    margin: number,
    defect_rate: number
  },
  simulated: {
    throughput: number,
    cost: number,
    margin: number,
    defect_rate: number
  },
  delta: {
    throughput_change: number,
    cost_change: number,
    margin_change: number,
    defect_rate_change: number
  },
  recommendation_score: number  // 0-100
}
```

### 7.6 Recommendation Endpoints

#### GET /api/v1/recommendations/{batch_id}
```typescript
Response: {
  batch_id: string,
  recommendations: Array<{
    id: string,
    title: string,
    description: string,
    category: "process" | "capacity" | "quality" | "maintenance",
    priority: number,           // 1-5
    impact: {
      score: number,            // 0-100
      estimated_improvement: string,
      affected_metrics: string[]
    },
    feasibility: {
      score: number,            // 0-100
      implementation_difficulty: "low" | "medium" | "high",
      estimated_cost: "low" | "medium" | "high",
      timeline: string
    },
    evidence: {
      confidence: number,
      supporting_data: string[],
      citations: string[]
    }
  }>,
  summary: {
    total_recommendations: number,
    high_priority: number,
    estimated_total_impact: number
  }
}
```

### 7.7 Copilot Endpoints

#### POST /api/v1/copilot/query
```typescript
Request: {
  batch_id: string,
  query: string,
  conversation_id?: string
}

Response: {
  conversation_id: string,
  answer: string,
  evidence: Array<{
    type: "defect_result" | "process_data" | "root_cause" | "recommendation",
    id: string,
    excerpt: string,
    relevance_score: number
  }>,
  confidence: number,
  follow_up_questions: string[]
}
```

---

## 8. Input/Output Specifications

### 8.1 Input Specifications

#### 8.1.1 Single Image Upload
```
Format: PNG
Size: ≤ 50MB
Dimensions: Any (will be resized to 224×224)
Color: RGB or Grayscale (converted to RGB)
Supported: JPEG, PNG, BMP (but PNG recommended)

Validation:
  ✓ File extension: .png, .jpg, .jpeg
  ✓ MIME type: image/png, image/jpeg
  ✓ Image loadable by PIL
  ✓ Min dimensions: 50×50 pixels
  ✓ Max dimensions: 10,000×10,000 pixels
```

#### 8.1.2 Batch Upload (Multiple Images)
```
Format: Multiple PNG files
Max files: 100 per batch
Total size: ≤ 500MB per batch
Same validation as single image

Frontend handling:
  - Drag-and-drop zone
  - File selector (multi-select)
  - Progress bar per file
  - Cancel individual uploads
```

#### 8.1.3 ZIP Upload (Mixed Content)
```
Format: ZIP archive
Max size: 500MB
Contents: PNG images AND/OR CSV files

Extraction rules:
  ✓ Extract PNG/JPG files → Inspection data
  ✓ Extract CSV files → Production/Economic data
  ✓ Auto-detect CSV type (Model 1/2/3 or Economic)
  ✓ Flatten subdirectories
  ✓ Skip files > 50MB (images) or > 20MB (CSVs)
  ✓ Skip hidden files (.DS_Store, __MACOSX)
  ✓ Remove duplicates (by hash)

Example structure 1 (Organized):
batch_complete_data.zip
  ├── images/
  │   ├── product_001.png        ✓ Extracted → Inspection data
  │   ├── product_002.png        ✓ Extracted → Inspection data
  │   └── product_003.png        ✓ Extracted → Inspection data
  ├── production/
  │   ├── model_1_data.csv       ✓ Extracted → Auto-detected as Model 1
  │   └── model_3_data.csv       ✓ Extracted → Auto-detected as Model 3
  ├── economic_costs.csv         ✓ Extracted → Auto-detected as Economic
  ├── readme.txt                 ✗ Skipped (unsupported type)
  └── .DS_Store                  ✗ Skipped (hidden file)

Example structure 2 (Flat):
batch_data.zip
  ├── img001.png                 ✓ Extracted → Inspection
  ├── img002.png                 ✓ Extracted → Inspection
  ├── process_data.csv           ✓ Extracted → Auto-detected
  ├── costs.csv                  ✓ Extracted → Auto-detected
  └── notes.txt                  ✗ Skipped

CSV Auto-Detection:
  - 10 columns + 'Demand', 'Drilling Util' → Model 1
  - 16 columns + 'Entities In Part 1' → Model 2
  - 77 columns + 'Time_Now', 'Blanking_Util' → Model 3
  - Contains 'scrap_cost', 'rework_cost' → Economic data

Response:
{
  "batch_id": "uuid-here",
  "extracted": {
    "images": {
      "count": 3,
      "files": ["product_001.png", "product_002.png", "product_003.png"]
    },
    "production_csvs": {
      "count": 2,
      "files": [
        {"name": "model_1_data.csv", "type": "model_1", "rows": 3000},
        {"name": "model_3_data.csv", "type": "model_3", "rows": 605620}
      ]
    },
    "economic_csvs": {
      "count": 1,
      "files": [{"name": "economic_costs.csv", "rows": 1}]
    }
  },
  "skipped": [
    {"name": "readme.txt", "reason": "unsupported_extension"},
    {"name": ".DS_Store", "reason": "hidden_file"}
  ],
  "status": "extracted"
}
```

#### 8.1.4 CSV Input (Production/Economic Data)
```
Upload methods:
  1. Direct CSV upload (via /api/upload/production/csv)
  2. Inside ZIP file (auto-extracted and categorized)

Format: CSV
Models supported:
  - Model 1: 10 features
  - Model 2: 16 features
  - Model 3: 77 features

CSV format:
  - First row: header (column names)
  - Subsequent rows: data
  - Comma-separated
  - Numeric values (floats/integers)
  - No missing values in key columns

Model 1 CSV (10 columns, 3000 rows):
Demand,Total parts,Parts per hour,VA Time,Drilling Waiting Time,Milling Waiting Time,Assembly Waiting Time,Drilling Util,Milling Util,Assembly Util
7,3472,145,8.998,0.412,0,2.094,0.482,0.360,0.719

Model 2 CSV (16 columns, 3000 rows):
Demand,Entities In Part 1,Part 1 VA Time,Drilling Queue Time,Part 1 Storage Time,Part 1 Stored,Entities In Part 2,Part 2 VA Time,Milling Queue Time,Part 2 Storage Time,Part 2 Stored,Entities Out,Assembly Time,Assembly Queue Time,Drilling Utilization,Milling Utilization,Assembly Utilization
7,4921,3.002,0.028,1.525,15,5138,3.002,0.002,32.318,232,4906,3.007,0.178,0.342,0.268,0.513

Model 3 CSV (77 columns, 605,620 rows):
Time_Now,Blanking_Util,Blanking_SKU1_Queue,Blanking_SKU2_Queue,Press1_Util,Press2_Util,...
24,0.846,0.046,0.056,0.410,0.435,...

Economic Data CSV (custom format):
parameter,value,unit
scrap_cost_per_unit,50.00,USD
rework_cost_per_unit,30.00,USD
contribution_margin_per_unit,150.00,USD
hourly_labor_cost,25.00,USD
overhead_rate,1.5,multiplier
```

### 8.2 Output Specifications

#### 8.2.1 Defect Classification Output
```json
{
  "image_id": "uuid-here",
  "file_name": "product_001.png",
  "prediction": {
    "class": "rust",
    "confidence": 0.94,
    "probabilities": {
      "normal": 0.02,
      "rust": 0.94,
      "crack": 0.01,
      "hole": 0.02,
      "scratch": 0.01
    }
  },
  "uncertainty": {
    "is_uncertain": false,
    "uncertainty_score": 0.08,
    "method": "mc_dropout"
  },
  "inference_time_ms": 124
}
```

#### 8.2.2 Defect Localization Output
```json
{
  "image_id": "uuid-here",
  "heatmap_url": "/api/results/uuid/heatmap.png",
  "overlay_url": "/api/results/uuid/overlay.png",
  "bounding_boxes": [
    {
      "x": 120,
      "y": 80,
      "width": 150,
      "height": 100,
      "confidence": 0.89
    }
  ],
  "defect_area_percentage": 12.5
}
```

#### 8.2.3 Batch Results Output
```json
{
  "batch_id": "uuid-here",
  "total_images": 45,
  "summary": {
    "normal": 32,
    "defective": 13,
    "uncertain": 3,
    "defect_breakdown": {
      "rust": 5,
      "crack": 3,
      "hole": 2,
      "scratch": 3
    }
  },
  "results": [...],  // Individual results
  "export_formats": {
    "csv": "/api/export/uuid/results.csv",
    "json": "/api/export/uuid/results.json",
    "pdf": "/api/export/uuid/report.pdf"
  }
}
```

#### 8.2.4 Process Analysis Output
```json
{
  "batch_id": "uuid-here",
  "model_type": "model_3",
  "timestamp": "2026-09-19T12:00:00Z",
  "bottlenecks": [
    {
      "station": "Press1",
      "type": "capacity",
      "severity": "high",
      "metrics": {
        "utilization": 0.96,
        "queue_time": 5.2,
        "queue_length": 42
      },
      "impact": "Throughput limited by 25%"
    }
  ],
  "utilization_rates": {
    "Blanking": 0.85,
    "Press1": 0.96,
    "Press2": 0.78,
    ...
  },
  "economic_impact": {
    "total_loss": 15420.50,
    "breakdown": {
      "scrap_cost": 5200.00,
      "rework_cost": 3100.00,
      "throughput_loss": 7120.50
    },
    "currency": "USD"
  }
}
```

#### 8.2.5 Root Cause Output
```json
{
  "defect_type": "rust",
  "root_cause": "High queue time causing extended storage exposure",
  "confidence": 0.82,
  "evidence": {
    "correlations": [
      {
        "parameter": "Assembly_Queue_Time",
        "correlation": 0.78,
        "p_value": 0.001,
        "strength": "strong"
      }
    ],
    "shap_explanation": [
      {
        "feature": "Assembly_Queue_Time",
        "shap_value": 0.45,
        "feature_value": 3.2,
        "contribution": "positive"
      }
    ],
    "temporal_pattern": "Defect rate increases 2-3 hours after queue buildup"
  },
  "recommendation": "Increase downstream capacity or implement dynamic scheduling"
}
```

#### 8.2.6 Recommendation Output
```json
{
  "id": "rec-uuid",
  "title": "Add second drilling station",
  "description": "Install parallel drilling station to reduce bottleneck",
  "category": "capacity",
  "priority": 1,
  "impact": {
    "score": 85,
    "estimated_improvement": "25% throughput increase",
    "affected_metrics": ["throughput", "queue_time", "utilization"],
    "roi": {
      "investment": 50000,
      "annual_savings": 85000,
      "payback_months": 7
    }
  },
  "feasibility": {
    "score": 70,
    "difficulty": "medium",
    "cost": "medium",
    "timeline": "3-4 weeks",
    "prerequisites": ["Space available", "Budget approved"]
  },
  "evidence": {
    "confidence": 0.85,
    "supporting_data": [
      "Drilling utilization at 96% (bottleneck threshold: 85%)",
      "Queue time 5.2 hours vs. target 1.0 hour",
      "Strong correlation (r=0.78) between drilling bottleneck and crack defects"
    ]
  }
}
```

### 8.3 Export Formats

#### CSV Export
```csv
image_id,file_name,predicted_class,confidence,is_uncertain,heatmap_url
uuid-1,img1.png,rust,0.94,false,/results/uuid-1/heatmap.png
uuid-2,img2.png,normal,0.98,false,
uuid-3,img3.png,crack,0.67,true,/results/uuid-3/heatmap.png
```

#### PDF Report Export
```
Sections:
1. Executive Summary
   - Total images analyzed
   - Defect rate
   - Top bottlenecks
   - Estimated economic impact

2. Visual Inspection Results
   - Defect gallery with heatmaps
   - Classification metrics
   - Uncertainty analysis

3. Process Analysis
   - Bottleneck charts
   - Utilization gauges
   - CUSUM timeline

4. Root Cause Analysis
   - Correlation matrix
   - SHAP waterfall charts
   - Evidence summary

5. Recommendations
   - Ranked list with impact/feasibility
   - Implementation roadmap

6. Appendix
   - Raw data tables
   - Model metrics
   - Glossary
```

---

## 9. Technology Stack

### 9.1 Complete Stack Summary

```yaml
Frontend:
  Framework: Next.js 14 (App Router)
  Language: TypeScript 5.2
  Styling: Tailwind CSS 3.4 + shadcn/ui
  State: Zustand 4.4
  Charts: Apache ECharts 5.4
  Diagrams: React Flow 11.10
  Animations: Framer Motion 10.16
  HTTP: Axios 1.6
  Forms: React Hook Form + Zod

Backend:
  Framework: FastAPI 0.105
  Language: Python 3.10
  Server: Uvicorn 0.25
  Validation: Pydantic 2.5
  Database: PostgreSQL 15
  ORM: SQLAlchemy 2.0
  Migrations: Alembic 1.13
  Tasks: Celery 5.3 + Redis 7.2
  Logging: Loguru 0.7

ML/AI:
  DL Framework: PyTorch 2.1
  Vision: torchvision 0.16, timm 0.9
  Tabular ML: XGBoost 2.0, scikit-learn 1.3
  Explainability: SHAP 0.43, pytorch-grad-cam 1.4
  Image Processing: OpenCV 4.8, Pillow 10.1
  Data: pandas 2.1, numpy 1.26, scipy 1.11
  Uncertainty: Monte Carlo Dropout

DevOps:
  Containerization: Docker 24.0 + Docker Compose
  Version Control: Git + GitHub
  CI/CD: GitHub Actions (optional)
  Monitoring: Prometheus + Grafana (optional)

Deployment:
  Frontend: Vercel (recommended) or Netlify
  Backend: Render / Railway / AWS EC2
  Database: Render Postgres / AWS RDS
  Storage: AWS S3 (production) / Local (dev)
```

### 9.2 Installation Commands

```bash
# Frontend
cd frontend
npm install next@14 react@18 react-dom@18 typescript@5
npm install @types/node @types/react @types/react-dom
npm install tailwindcss postcss autoprefixer
npm install zustand axios react-hook-form zod
npm install echarts echarts-for-react
npm install reactflow framer-motion
npm install @radix-ui/react-* # shadcn/ui dependencies

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi[all]==0.105.0
pip install uvicorn[standard]==0.25.0
pip install sqlalchemy==2.0.23 alembic==1.13.0
pip install psycopg2-binary==2.9.9
pip install celery[redis]==5.3.4
pip install torch==2.1.0 torchvision==0.16.0
pip install timm==0.9.12 opencv-python==4.8.1
pip install xgboost==2.0.2 scikit-learn==1.3.2
pip install shap==0.43.0 grad-cam==1.4.8
pip install pandas==2.1.3 numpy==1.26.2
pip install pydantic==2.5.2 pydantic-settings==2.1.0
pip install python-multipart==0.0.6 aiofiles==23.2.1
pip install loguru==0.7.2 python-dotenv==1.0.0
```

---

## 10. Deployment Architecture

### 10.1 Development Environment

```
┌─────────────────────────────────────────┐
│         Developer Machine                │
├─────────────────────────────────────────┤
│  Frontend (localhost:3000)              │
│    └─ Next.js dev server                │
│                                         │
│  Backend (localhost:8000)               │
│    └─ Uvicorn dev server                │
│                                         │
│  Database (localhost:5432)              │
│    └─ PostgreSQL (Docker)               │
│                                         │
│  Redis (localhost:6379)                 │
│    └─ Redis (Docker)                    │
└─────────────────────────────────────────┘
```

### 10.2 Production Architecture

```
                         ┌──────────────┐
                         │   Vercel     │
                         │  (Frontend)  │
                         │  Next.js App │
                         └──────┬───────┘
                                │ HTTPS
                                ▼
┌───────────────────────────────────────────────┐
│                    Internet                    │
└───────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────┐
                    │   Load Balancer   │
                    │    (NGINX/AWS)    │
                    └─────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌─────────────────┐           ┌─────────────────┐
    │  Backend Server │           │  Backend Server │
    │   (FastAPI)     │           │   (FastAPI)     │
    │   Render/AWS    │           │   Render/AWS    │
    └────────┬────────┘           └────────┬────────┘
             │                              │
             └──────────┬───────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
  ┌───────────┐  ┌───────────┐  ┌───────────┐
  │PostgreSQL │  │   Redis   │  │   AWS S3  │
  │ (Render)  │  │  (Redis   │  │  (File    │
  │           │  │   Cloud)  │  │  Storage) │
  └───────────┘  └───────────┘  └───────────┘
```

### 10.3 Docker Setup

#### docker-compose.yml
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/industrial_ai
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend/weights:/app/weights
      - ./backend/data:/app/data
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=industrial_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery_worker:
    build: ./backend
    command: celery -A app.workers.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/industrial_ai
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - backend
      - redis

volumes:
  postgres_data:
```

---

## 11. Security & Performance

### 11.1 Security Considerations

```yaml
Input Validation:
  - File type whitelist (PNG, JPG only)
  - File size limits (50MB per image, 500MB per batch)
  - Image content validation (prevent malicious files)
  - ZIP bomb protection (max extraction size)
  - Path traversal prevention

API Security:
  - Rate limiting (100 requests/minute per IP)
  - CORS configuration (whitelist frontend domain)
  - Input sanitization (prevent SQL injection)
  - Request size limits
  - Authentication (optional JWT for multi-user)

Data Security:
  - Database connection pooling with SSL
  - Secure file storage (private S3 bucket)
  - Environment variable management (.env)
  - Secrets rotation
  - No sensitive data in logs

Model Security:
  - Model weights integrity check (hash verification)
  - Input adversarial robustness (future enhancement)
  - Output validation
```

### 11.2 Performance Optimization

```yaml
Frontend:
  - Code splitting (Next.js automatic)
  - Image lazy loading
  - Infinite scroll for large batches
  - Debounced search/filter
  - React Query for caching
  - CDN for static assets

Backend:
  - Async endpoints (FastAPI async/await)
  - Connection pooling (SQLAlchemy)
  - Result caching (Redis)
  - Batch inference (parallel processing)
  - GPU utilization (CUDA)
  - Model quantization (INT8 for deployment)

Database:
  - Indexed queries
  - Query optimization
  - Connection pooling
  - Read replicas (production)

ML Models:
  - Model pruning (reduce size)
  - ONNX export (faster inference)
  - TorchScript compilation
  - Half-precision (FP16) inference
  - Batched predictions
```

### 11.3 Performance Targets

```yaml
Response Times:
  - Single image classification: <1 second
  - Single image with heatmap: <3 seconds
  - Batch (100 images): <60 seconds
  - Process analysis: <5 seconds
  - Root cause analysis: <10 seconds
  - Dashboard load: <2 seconds

Throughput:
  - Concurrent users: 50+
  - Images/hour: 10,000+
  - API requests/second: 100+

Resource Usage:
  - CPU: <80% average
  - Memory: <8GB per backend instance
  - GPU: <6GB VRAM
  - Disk I/O: <100MB/s
```

---

## 12. Implementation Timeline

### Week 1-2: Foundation & Setup
```
Day 1-2:
  ✓ Project structure setup
  ✓ Docker environment
  ✓ Database schema
  ✓ Basic FastAPI endpoints

Day 3-4:
  □ Dataset organization
  □ Data loaders
  □ Image preprocessing pipeline
  □ Basic frontend scaffold

Day 5-7:
  □ Train defect classifier (EfficientNet-B4)
  □ Implement Grad-CAM
  □ Uncertainty quantification
  □ Model evaluation

Day 8-10:
  □ Upload endpoints (single/batch/ZIP)
  □ Inference endpoints
  □ File storage system
  □ Frontend upload UI

Day 11-14:
  □ Dashboard layout
  □ Quality view page
  □ Defect visualization components
  □ Basic charts (ECharts integration)
```

### Week 3: Process Analysis
```
Day 15-17:
  □ Load and explore Model 1/2/3 CSVs
  □ Feature engineering
  □ Train XGBoost process model
  □ Bottleneck detection algorithm

Day 18-20:
  □ Process analysis endpoints
  □ Economic impact calculator
  □ CUSUM implementation
  □ Process view page

Day 21:
  □ Integration testing
  □ Bug fixes
```

### Week 4: Integration & Correlation
```
Day 22-24:
  □ Correlation engine
  □ SHAP explainer
  □ Root cause classification
  □ Statistical tests

Day 25-27:
  □ Root cause endpoints
  □ Analysis view page
  □ Correlation visualizations
  □ SHAP waterfall charts

Day 28:
  □ Integration testing
  □ Performance optimization
```

### Week 5: Simulator & Recommendations
```
Day 29-31:
  □ What-if simulator backend
  □ Scenario comparison
  □ Recommendation engine
  □ Priority ranking

Day 32-34:
  □ Simulator UI
  □ Recommendation page
  □ AI Copilot integration (optional)
  □ Export functionality

Day 35:
  □ End-to-end testing
  □ UI/UX refinement
```

### Week 6: Testing & Documentation
```
Day 36-38:
  □ Comprehensive testing (unit, integration, E2E)
  □ Performance testing
  □ Security audit
  □ Bug fixes

Day 39-41:
  □ Documentation (API docs, user guide)
  □ Code cleanup
  □ README updates
  □ Demo preparation

Day 42:
  □ Final presentation
  □ Project submission
```

---

## Appendix

### A. Glossary

```
Grad-CAM: Gradient-weighted Class Activation Mapping
SHAP: SHapley Additive exPlanations
CUSUM: Cumulative Sum Control Chart
OOD: Out-of-Distribution
WIP: Work-In-Process
VA Time: Value-Added Time
NVA Time: Non-Value-Added Time
IoU: Intersection over Union
F1: Harmonic mean of precision and recall
```

### B. Key Formulas

```python
# Little's Law
L = λ × W
# L: average WIP, λ: arrival rate, W: average wait time

# Utilization
ρ = λ / μ
# ρ: utilization, λ: arrival rate, μ: service rate

# Economic Loss
Total_Loss = (Scrap × Scrap_Cost) + (Rework × Rework_Cost) + 
             (Throughput_Loss × Contribution_Margin)

# Correlation
r = Cov(X, Y) / (σ_X × σ_Y)
```

### C. Sample API Calls

```bash
# Upload single image
curl -X POST http://localhost:8000/api/v1/upload/single \
  -F "file=@product_001.png"

# Classify image
curl -X POST http://localhost:8000/api/v1/inference/classify \
  -H "Content-Type: application/json" \
  -d '{"image_id": "uuid-here", "include_heatmap": true}'

# Get batch results
curl -X GET http://localhost:8000/api/v1/results/batch/uuid-here

# Run what-if simulation
curl -X POST http://localhost:8000/api/v1/simulator/scenario \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "uuid-here",
    "baseline": {...},
    "changes": {"demand": 1.2}
  }'
```

---

**Document Version**: 1.0  
**Last Updated**: September 19, 2026  
**Status**: Ready for Implementation  
**Next Review**: After Week 2 (Checkpoint 2)
