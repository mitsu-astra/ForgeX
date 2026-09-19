# Industrial AI Decision Intelligence: Endpoints & Frontend-Backend Integration Specification

This document serves as the complete technical integration contract between the **Next.js 16 Frontend** and the **FastAPI Multi-Modal AI Backend** for the Industrial AI Decision Intelligence Platform.

---

## 1. System Architecture & Integration Model

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 NEXT.JS FRONTEND (Port 3000)                           │
│                                                                                        │
│  /dashboard (Overview)     /dashboard/upload       /dashboard/quality                  │
│  - Real-time KPIs          - Drag & Drop Upload    - Specimen Gallery (3 Tabs)         │
│  - Production Batches      - Auto-Schema Detect    - Grad-CAM Heatmap Visualizer       │
│  - Bottleneck Alerts       - 5-Stage Pipeline Run  - Epistemic Uncertainty & Bounding  │
│                                                                                        │
│  /dashboard/process        /dashboard/analysis     /dashboard/simulator   /dashboard/copilot
│  - Workstation Util%       - Interactive Sliders   - What-If Sliders      - AI Chat Assistant
│  - Little's Law Lead Time  - SHAP Waterfall        - Scrap Reduction %    - Evidence Citation
│  - CUSUM Drift Alarms      - Spearman Correlation  - Monthly Savings ($)  - Structured Actions
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP REST / JSON / Multipart
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                FASTAPI BACKEND (Port 8000)                             │
│                                                                                        │
│  /api/v1/upload            /api/v1/quality         /api/v1/process                     │
│  - Single File Ingest      - Single Image Inspect  - Workstation Bottlenecks           │
│  - ZIP Archive Extractor   - Batch Image Inspect   - Tabular CUSUM Drift               │
│  - End-to-End Pipeline     - Curated Gallery       - Little's Law Lead Time            │
│                            - Dataset Sample Check                                      │
│                                                                                        │
│  /api/v1/correlation       /api/v1/simulator       /api/v1/copilot        /api/v1/analytics
│  - Failure Mode Diagnosis  - Response Surface Sim  - Multi-Modal Copilot  - KPI Dashboard Agg
│  - TreeSHAP Attributions   - ROI / Scrap Savings   - Action Generator     - OEE Metrics       │
│  - Spearman Rank Matrix                                                                │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Model Execution Engines
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               AI & MACHINE LEARNING MODELS                             │
│                                                                                        │
│  • EfficientNet-B4 (PyTorch) + LayerCam/Grad-CAM + Monte Carlo Dropout (Vision QA)     │
│  • XGBoost Regressor (10, 16, 77 Column Discrete-Event Simulation Surrogate)           │
│  • XGBoost Multi-Class Classifier + TreeExplainer (SHAP Root Cause Attribution)        │
│  • Dynamic Response Surface Surrogate (What-If Optimization Engine)                   │
│  • Page's Tabular CUSUM Statistical Process Control (Sensor Drift Detector)            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Master API Endpoints Specification

### 2.1 System & Health

#### `GET /health`
- **Purpose**: System heartbeat and AI model readiness verification.
- **Frontend Trigger**: Dashboard mount, Status Badge ("System Online").
- **Request**: None.
- **Response**:
```json
{
  "status": "healthy",
  "service": "Industrial AI Decision Intelligence API",
  "vision_engine_loaded": true,
  "bottleneck_detector_loaded": true,
  "root_cause_classifier_loaded": true,
  "what_if_simulator_loaded": true
}
```

---

### 2.2 Upload & Ingestion (`/api/v1/upload`)

#### `POST /api/v1/upload/file`
- **Purpose**: Ingest a single file (image `.png`/`.jpg`, or tabular log `.csv`). Dynamically analyzes CSV column signatures to classify Model 1, Model 2, Model 3, or Economics.
- **Frontend Component**: `/dashboard/upload` (File dropzone, Browse input).
- **Request**: `multipart/form-data`
  - `file`: Binary file.
- **Response**:
```json
{
  "success": true,
  "message": "File production_batch_01.csv uploaded successfully",
  "data": {
    "batch_id": "a1b2c3d4",
    "filename": "production_batch_01.csv",
    "file_path": "/path/to/uploads/a1b2c3d4/production_batch_01.csv",
    "file_type": "csv",
    "detected_subtype": "model_1",
    "file_size_bytes": 460800
  }
}
```

#### `POST /api/v1/upload/zip`
- **Purpose**: Ingests mixed multi-modal ZIP archives, unpacks images and CSV files, detects schema headers across all tabular files, and indexes images.
- **Frontend Component**: `/dashboard/upload` (Dropzone ZIP upload).
- **Request**: `multipart/form-data`
  - `file`: ZIP file.
- **Response**:
```json
{
  "success": true,
  "message": "Archive extracted: 142 images, 4 CSVs identified",
  "data": {
    "batch_id": "9f8e7d6c",
    "total_images": 142,
    "total_csvs": 4,
    "images": [
      { "filename": "rust_001.png", "relative_path": "images/rust_001.png", "size_bytes": 245760 }
    ],
    "csv_datasets": [
      { "filename": "process_model1.csv", "csv_type": "model_1", "num_rows": 4000, "num_cols": 10 }
    ]
  }
}
```

#### `POST /api/v1/upload/run-pipeline`
- **Purpose**: Executes the 5-stage Decision Intelligence Pipeline across ingested or benchmark datasets.
- **Frontend Component**: `/dashboard/upload` ("Run Analysis Pipeline" Button).
- **Request Body**: `application/json`
```json
{
  "batch_id": "optional_batch_id_or_empty",
  "use_benchmark_data": true
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Decision Intelligence Pipeline executed successfully in 1.42s",
  "data": {
    "stages": {
      "ingestion": {
        "status": "completed",
        "images_count": 142,
        "csv_streams": ["Model 1 (10 cols)", "Model 2 (16 cols)", "Model 3 (77 cols)", "Economic Parameters"]
      },
      "vision": {
        "status": "completed",
        "model": "EfficientNet-B4 + Grad-CAM",
        "inspected_count": 142,
        "defects_detected": 18,
        "accuracy_pct": 99.94
      },
      "bottlenecks": {
        "status": "completed",
        "primary_bottleneck": "Drilling",
        "max_utilization_pct": 96.0,
        "line_efficiency_pct": 71.4
      },
      "root_cause": {
        "status": "completed",
        "primary_failure_mode": "hydraulic_overload_stress",
        "top_shap_driver": "Hydraulic Pressure (+0.462 SHAP)"
      },
      "simulation": {
        "status": "completed",
        "forecasted_defect_reduction_pct": 42.5,
        "monthly_savings_usd": 38400.0
      }
    },
    "execution_time_ms": 1420
  }
}
```

---

### 2.3 Visual Inspection & Quality QA (`/api/v1/quality`)

#### `GET /api/v1/quality/gallery`
- **Purpose**: Fetches curated benchmark specimens from the `train/` dataset (12,000 images across crack, rust, scratch, hole, normal) with static image URLs.
- **Frontend Component**: `/dashboard/quality` (Tabs: "All Specimens", "Defective Only", "Normal").
- **Request**: None.
- **Response**:
```json
{
  "success": true,
  "message": "Curated gallery retrieved",
  "data": {
    "total_count": 25,
    "defective_count": 19,
    "normal_count": 6,
    "specimens": [
      {
        "id": 1,
        "name": "rust_00611.png",
        "defect": "Rust",
        "defect_key": "rust",
        "severity": "High",
        "confidence": 98.4,
        "gradcam": true,
        "image_url": "http://localhost:8000/static/train/rust/rust_00611.png",
        "file_path": "train/rust/rust_00611.png"
      }
    ]
  }
}
```

#### `POST /api/v1/quality/inspect`
- **Purpose**: Performs real-time inference on a custom user-uploaded image via PyTorch EfficientNet-B4. Computes softmax probabilities, Monte Carlo Dropout epistemic uncertainty, and Grad-CAM localized bounding boxes.
- **Frontend Component**: `/dashboard/quality` ("Inspect Custom Image" button).
- **Request**: `multipart/form-data`
  - `file`: Image binary (`image/png`, `image/jpeg`).
  - `include_heatmap`: `true` (Form field).
  - `mc_samples`: `5` (Form field).
- **Response**:
```json
{
  "success": true,
  "message": "Visual inspection completed successfully",
  "data": {
    "filename": "custom_part_42.png",
    "prediction": {
      "defect_class": "crack",
      "confidence": 0.984,
      "class_id": 0,
      "probabilities": { "crack": 0.984, "rust": 0.008, "scratch": 0.004, "hole": 0.002, "normal": 0.002 }
    },
    "uncertainty": {
      "uncertainty_score": 0.014,
      "is_uncertain": false,
      "threshold": 0.15,
      "confidence_interval_95": [0.952, 0.996]
    },
    "localization": {
      "bounding_boxes": [
        {
          "bbox_id": 1,
          "x_min": 72, "y_min": 58, "x_max": 184, "y_max": 204,
          "width": 112, "height": 146,
          "area_pixels": 16352,
          "area_percentage": 14.2,
          "confidence": 0.962,
          "defect_type": "crack"
        }
      ],
      "defect_area_percentage": 14.2,
      "heatmap_base64": "data:image/png;base64,...",
      "overlay_base64": "data:image/png;base64,..."
    },
    "inference_time_ms": 11.2,
    "status": "success",
    "inspected_at": "2026-09-19 18:30:00"
  }
}
```

#### `POST /api/v1/quality/inspect-sample`
- **Purpose**: Runs live PyTorch inference on a specific dataset specimen selected from the gallery or quick-preset buttons.
- **Frontend Component**: `/dashboard/quality` ("Analyze Specimen" buttons on cards, Quick Presets).
- **Request**: Query parameters:
  - `defect_type`: `crack` | `rust` | `scratch` | `hole` | `normal`
  - `filename`: Optional specific filename (e.g. `rust_00611.png`)
  - `include_heatmap`: `true`
  - `mc_samples`: `5`
- **Response**: Same as `POST /inspect` plus `preview_base64`.

---

### 2.4 Process Intelligence & Line Balancing (`/api/v1/process`)

#### `POST /api/v1/process/bottlenecks`
- **Purpose**: Evaluates discrete-event manufacturing station utilizations and queue times. Computes line balancing efficiency %, Little's Law WIP lead times, and economic bottleneck losses ($/hr, $/day, $/mo).
- **Frontend Component**: `/dashboard/process` ("Recalculate Bottlenecks" button, Workstation status cards).
- **Request Body**:
```json
{
  "station_utilizations": {
    "Drilling": 0.96,
    "Milling": 0.36,
    "Assembly": 0.72,
    "Deburring": 0.58,
    "QualityCheck": 0.81
  },
  "station_queue_times": {
    "Drilling": 4.12,
    "Milling": 0.85,
    "Assembly": 2.09,
    "Deburring": 0.95,
    "QualityCheck": 1.45
  },
  "throughput_per_hr": 145.0,
  "demand": 7.0
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Process bottleneck analysis completed successfully",
  "data": {
    "primary_bottleneck": "Drilling",
    "max_utilization": 0.96,
    "line_efficiency_pct": 71.4,
    "total_wip_units": 141.9,
    "estimated_lead_time_hrs": 10.66,
    "bottlenecks": [
      {
        "station": "Drilling",
        "utilization": 0.96,
        "queue_time_hrs": 4.12,
        "severity": "high",
        "impact": "Station at 96.0% capacity; limits line throughput",
        "recommended_action": "Offload Drilling or increase station parallel buffer capacity"
      }
    ],
    "economic_impact": {
      "hourly_throughput_loss_usd": 906.25,
      "daily_throughput_loss_usd": 21750.0,
      "monthly_throughput_loss_usd": 652500.0
    },
    "all_station_utilizations": { "Drilling": 0.96, "Milling": 0.36, "Assembly": 0.72 },
    "all_station_queue_times": { "Drilling": 4.12, "Milling": 0.85, "Assembly": 2.09 }
  }
}
```

#### `POST /api/v1/process/drift-analysis`
- **Purpose**: Evaluates sensor time-series data using Page's Tabular CUSUM control chart algorithm, detecting parameter drifts before scrap is generated.
- **Frontend Component**: `/dashboard/process` (CUSUM parameter preset buttons: Hydraulic Pressure, Spindle Vibration, Coolant pH).
- **Request Body**:
```json
{
  "parameter_name": "Hydraulic Pressure (bar)",
  "values": [180.2, 181.5, 180.9, 182.1, 185.4, 189.2, 194.5, 201.3, 208.5, 212.0],
  "threshold": 5.0
}
```
- **Response**:
```json
{
  "success": true,
  "message": "CUSUM drift analysis for 'Hydraulic Pressure (bar)' completed",
  "data": {
    "parameter_name": "Hydraulic Pressure (bar)",
    "drift_detected": true,
    "drift_start_index": 6,
    "positive_drift_detected": true,
    "negative_drift_detected": false,
    "max_cusum_statistic": 7.42,
    "threshold": 5.0
  }
}
```

---

### 2.5 Root-Cause Attribution & Explainability (`/api/v1/correlation`)

#### `POST /api/v1/correlation/diagnose`
- **Purpose**: Diagnoses the underlying failure mode from active process conditions using multi-class XGBoost and returns local TreeSHAP feature attributions.
- **Frontend Component**: `/dashboard/analysis` (Interactive Process Condition Sliders, "Run Live Diagnosis" button).
- **Request Body**:
```json
{
  "hydraulic_pressure_bar": 188.0,
  "coolant_ph": 7.1,
  "conveyor_speed_mps": 1.25,
  "feed_rate_mmpm": 380.0,
  "queue_time_hours": 4.5,
  "station_max_util": 0.96,
  "spindle_cycles": 4000.0,
  "ambient_humidity_pct": 75.0
}
```
- **Response**:
```json
{
  "success": true,
  "message": "Root cause diagnosed: hydraulic_overload_stress (94.2%)",
  "data": {
    "root_cause": "hydraulic_overload_stress",
    "confidence": 0.942,
    "associated_defect": "crack",
    "probabilities": {
      "hydraulic_overload_stress": 0.942,
      "storage_queue_corrosion": 0.024,
      "conveyor_speed_friction": 0.018,
      "tool_wear_drill_misalignment": 0.011,
      "nominal_in_control": 0.005
    },
    "shap_explanation": {
      "base_value": 0.20,
      "top_features": [
        { "feature": "Press Hydraulic Pressure", "feature_value": 188.0, "shap_value": 0.462, "contribution": "positive" },
        { "feature": "Spindle Feed Rate", "feature_value": 380.0, "shap_value": 0.145, "contribution": "positive" },
        { "feature": "Coolant Fluid pH", "feature_value": 7.1, "shap_value": -0.052, "contribution": "negative" }
      ]
    },
    "recommendation": "Recalibrate hydraulic pressure relief valves to 172-180 bar nominal"
  }
}
```

#### `GET /api/v1/correlation/correlations`
- **Purpose**: Computes Spearman Rank Correlation Matrix ($r_s$) and two-tailed p-values between process parameters and defect types across 4,000 cycles.
- **Frontend Component**: `/dashboard/analysis` (Defect type filter buttons: `rust`, `crack`, `scratch`, `hole`).
- **Request**: Query parameter: `defect_type=rust`
- **Response**:
```json
{
  "success": true,
  "message": "Correlation matrix for 'rust' generated",
  "data": {
    "defect_type": "rust",
    "sample_size": 4000,
    "correlations": [
      { "parameter": "Queue_Time_Hours", "spearman_correlation": 0.842, "p_value": 0.0001, "is_statistically_significant": true, "direction": "positive", "strength": "strong" },
      { "parameter": "Ambient_Humidity_pct", "spearman_correlation": 0.768, "p_value": 0.0003, "is_statistically_significant": true, "direction": "positive", "strength": "strong" },
      { "parameter": "Coolant_pH", "spearman_correlation": -0.684, "p_value": 0.0012, "is_statistically_significant": true, "direction": "negative", "strength": "moderate" }
    ]
  }
}
```

---

### 2.6 What-If Simulation Engine (`/api/v1/simulator`)

#### `POST /api/v1/simulator/run`
- **Purpose**: Executes response-surface what-if simulation, predicting defect reduction %, throughput delta %, monthly scrap savings ($), and feasibility score.
- **Frontend Component**: `/dashboard/simulator` (Sliders for Pressure, Coolant, Speed, Demand; "Run Simulation" and "Reset Defaults" buttons).
- **Request Body**:
```json
{
  "baseline_params": {
    "Press Hydraulic Pressure": 188.0,
    "Coolant Fluid pH": 7.1,
    "Conveyor Belt Speed": 1.25,
    "Demand": 7.0
  },
  "modified_params": {
    "Press Hydraulic Pressure": 172.0,
    "Coolant Fluid pH": 7.7,
    "Conveyor Belt Speed": 0.95,
    "Demand": 7.0
  },
  "baseline_defect_rate": 12.8,
  "baseline_throughput": 145.0
}
```
- **Response**:
```json
{
  "success": true,
  "message": "What-If scenario simulation completed successfully",
  "data": {
    "baseline": { "defect_rate_pct": 12.8, "throughput_per_hr": 145.0, "monthly_loss_usd": 38400.0 },
    "simulated": { "defect_rate_pct": 2.4, "throughput_per_hr": 148.5, "monthly_loss_usd": 7200.0 },
    "delta": { "defect_reduction_pct": 81.25, "throughput_change_pct": 2.4, "monthly_savings_usd": 31200.0 },
    "recommendation_score": 92.5,
    "risk_level": "low"
  }
}
```

---

### 2.7 AI Copilot Assistant (`/api/v1/copilot`)

#### `POST /api/v1/copilot/chat`
- **Purpose**: Natural-language decision intelligence assistant that synthesizes vision detections, process queues, SHAP attributions, and simulation forecasts to return structured recommendations.
- **Frontend Component**: `/dashboard/copilot` (Chat input, Send button, Enter key, Quick suggestion chips).
- **Request Body**:
```json
{
  "message": "Why are crack defects elevated in the morning shift?",
  "history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Industrial AI Decision Intelligence Assistant is operational." }
  ]
}
```
- **Response**:
```json
{
  "success": true,
  "message": "AI Copilot response generated",
  "data": {
    "response": "Stress fractures detected near mounting flanges (Confidence: 94.8%). Hydraulic forming pressure spikes detected at 210 bar (nominal: 175-185 bar). Root cause diagnosed as hydraulic_overload_stress. Calibrating relief valves to 172 bar will reduce crack occurrence by 38.2%.",
    "evidence_sources": [
      "EfficientNet-B4 Stress Localization",
      "Hydraulic Pressure Sensor Log (Peak: 210 bar)",
      "SHAP TreeExplainer (Pressure SHAP: +2.115)"
    ],
    "suggested_actions": [
      {
        "action_title": "Pressure Relief Valve Recalibration",
        "target_station": "Forming / Stamping Press",
        "parameter_adjustment": "Reduce operating pressure to 172 bar",
        "expected_impact": "-38.2% Crack Defect Rate",
        "priority": "High"
      }
    ],
    "confidence_score": 0.96
  }
}
```

---

### 2.8 Executive Analytics & KPIs (`/api/v1/analytics`)

#### `GET /api/v1/analytics/overview`
- **Purpose**: Aggregates enterprise KPIs, line yield %, throughput, bottleneck stations, and defect distributions.
- **Frontend Component**: `/dashboard` (Executive Overview page).
- **Request**: None.
- **Response**:
```json
{
  "success": true,
  "message": "Analytics overview retrieved successfully",
  "data": {
    "kpis": {
      "overall_yield_pct": 96.8,
      "total_inspected_today": 8420,
      "defects_detected_today": 269,
      "current_line_throughput_pph": 145.0,
      "primary_bottleneck_station": "Drilling",
      "bottleneck_utilization_pct": 96.0,
      "estimated_monthly_scrap_loss_usd": 13450.0,
      "potential_optimization_savings_usd": 708039.71
    },
    "defect_distribution": [
      { "type": "Crack", "count": 68, "pct": 25.3, "primary_cause": "Hydraulic Overload" },
      { "type": "Rust", "count": 94, "pct": 34.9, "primary_cause": "Queue Oxidation / pH" },
      { "type": "Scratch", "count": 52, "pct": 19.3, "primary_cause": "Conveyor Friction" },
      { "type": "Hole", "count": 55, "pct": 20.5, "primary_cause": "Tool Wear" }
    ],
    "station_utilizations": [
      { "station": "Blanking", "utilization": 0.42, "status": "nominal" },
      { "station": "Drilling", "utilization": 0.96, "status": "critical" },
      { "station": "Milling", "utilization": 0.36, "status": "nominal" },
      { "station": "Assembly", "utilization": 0.72, "status": "warning" }
    ]
  }
}
```

---

## 3. Frontend Route & Interactive Control Matrix

| Route | UI Section | Interactive Element / Button | Target Backend Endpoint | Expected Action / Data Flow |
| :--- | :--- | :--- | :--- | :--- |
| `/dashboard` | Header & KPIs | Auto-fetch on mount | `GET /api/v1/analytics/overview` | Populates Yield, Throughput, Bottleneck, Monthly Loss |
| `/dashboard` | Navigation | Sidebar Links | Next.js Router (`/dashboard/*`) | Seamless client-side route navigation |
| `/dashboard/upload` | File Dropzone | Drag & Drop / Click to Browse | `POST /api/v1/upload/file`, `POST /api/v1/upload/zip` | Uploads file, parses headers, adds item to Registered Files |
| `/dashboard/upload` | Registered Files | "Clear All" Button | Local State (`setUploadedFiles([])`) | Clears all registered files from memory |
| `/dashboard/upload` | Benchmark Sample | "Load Benchmark Sample" Button | Local State / `/api/v1/quality/gallery` | Loads benchmark samples (001.png, model1.csv) for 1-click test |
| `/dashboard/upload` | Pipeline Runner | "Run Analysis Pipeline" Button | `POST /api/v1/upload/run-pipeline` | Opens live 5-stage execution modal, ticks logs, transitions to QA |
| `/dashboard/quality` | Specimen Gallery | Tabs ("All", "Defective Only", "Normal") | `GET /api/v1/quality/gallery` | Filters gallery cards dynamically by defect status |
| `/dashboard/quality` | Specimen Cards | "Analyze Specimen" Button | `POST /api/v1/quality/inspect-sample` | Runs live inference on selected specimen, auto-scrolls to visualizer |
| `/dashboard/quality` | Custom Upload | "Inspect Custom Image" Button | `POST /api/v1/quality/inspect` | Uploads and analyzes arbitrary user image via EfficientNet-B4 |
| `/dashboard/quality` | Visualizer | Mode Buttons ("Overlay", "Heatmap", "Raw") | Local State (`setViewMode`) | Toggles Grad-CAM overlay, activation heatmap, or raw image |
| `/dashboard/quality` | Demo Presets | Quick Preset Chips (Crack, Rust, etc.) | `POST /api/v1/quality/inspect-sample` | Loads preset specimen and triggers visualizer |
| `/dashboard/process` | Bottleneck Analysis | "Recalculate Bottlenecks" Button | `POST /api/v1/process/bottlenecks` | Refreshes Little's law queues, station loads, financial loss |
| `/dashboard/process` | Tabular CUSUM | Sensor Buttons (Pressure, Vibration, pH) | `POST /api/v1/process/drift-analysis` | Runs Page's CUSUM control chart and displays shift cycle |
| `/dashboard/analysis` | Condition Sliders | Sliders (Pressure, pH, Speed, Feed) | `POST /api/v1/correlation/diagnose` | Updates operational conditions for real-time SHAP diagnosis |
| `/dashboard/analysis` | Failure Diagnosis | "Run Live Diagnosis" Button | `POST /api/v1/correlation/diagnose` | Computes TreeSHAP feature attributions and failure mode |
| `/dashboard/analysis` | Correlation Matrix | Defect Type Buttons (`rust`, `crack`, etc.) | `GET /api/v1/correlation/correlations` | Displays Spearman rank correlations ($r_s$) and p-values |
| `/dashboard/simulator` | What-If Parameters | 4 Parameter Sliders | `POST /api/v1/simulator/run` | Triggers live recalculation of forecasted savings and scrap rate |
| `/dashboard/simulator` | Controls | "Reset Defaults" Button | Local State (`handleReset`) | Reverts sliders to nominal baseline parameters |
| `/dashboard/simulator` | Controls | "Run Simulation" Button | `POST /api/v1/simulator/run` | Re-executes scenario and calculates recommendation score |
| `/dashboard/copilot` | Chat Interface | Input Box + Send Button + Enter Key | `POST /api/v1/copilot/chat` | Posts prompt and streams structured response with action plans |
| `/dashboard/copilot` | Suggestion Chips | Quick Prompt Chips | `POST /api/v1/copilot/chat` | Populates query and immediately requests AI Copilot synthesis |
| `/dashboard/settings` | Model Thresholds | Confidence Threshold / Switches | Local State / Persistence | Sets model alert boundaries and Grad-CAM generation flags |

---

## 4. Static Asset Architecture

- **Dataset Root Directory**: `/home/koushik_2109/Hackathons/CMR/train`
- **Classes**: `crack/` (2,400 images), `rust/` (2,400 images), `scratch/` (2,400 images), `hole/` (2,400 images), `normal/` (2,400 images) = 12,000 total images.
- **Static Mounting in FastAPI**:
  ```python
  app.mount("/static/train", StaticFiles(directory=os.path.join(root_dir, "train")), name="train")
  app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
  ```
- **Access URL Pattern**: `http://localhost:8000/static/train/{class}/{filename}` (e.g. `http://localhost:8000/static/train/rust/rust_00611.png`).
- **Proxying & Next.js Handling**: The Next.js frontend calls `api.ts` which uses `http://localhost:8000`. Images served through the backend static route are rendered via standard HTML5 `<img>` tags with smooth error fallbacks.
