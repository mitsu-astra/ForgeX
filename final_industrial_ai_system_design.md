# INDUSTRIAL AI VISUAL INSPECTION & MANUFACTURING ROOT-CAUSE SYSTEM
## Final System Design + Technology Stack
### NEURAX Hackathon 3.0 — Domain 2: AI in Industry and Automation

============================================================
1. EXECUTIVE DESIGN DECISION
============================================================

The final system should combine the strongest ideas from the two supplied
architectures and the additional proposed architecture.

The recommended design is a UNIFIED MULTI-PIPELINE DECISION-SUPPORT SYSTEM:

    Inspection Data
          |
          v
    Vision AI
          |
          +-------------------+
                              |
    Production Data            |
          |                   |
          v                   |
    Process / Flow AI         |
          |                   |
          +--------+----------+
                   |
    Economic Data  |
          |        |
          v        |
    Economic Engine
                   |
                   v
          INTEGRATION LAYER
                   |
                   v
          ROOT-CAUSE ENGINE
                   |
                   v
       KNOWLEDGE / EVIDENCE LAYER
                   |
                   v
          PREDICTIVE ENGINE
                   |
                   v
          WHAT-IF SIMULATOR
                   |
                   v
        RECOMMENDATION ENGINE
                   |
                   v
          AI FACTORY COPILOT
                   |
                   v
              DASHBOARD


The architecture deliberately uses different methods for different tasks:

    Computer Vision      -> Deep Learning
    Process Analysis     -> Statistics + ML + Operations Research
    Root Cause            -> Statistical + ML + Domain Rules
    Economic Impact       -> Deterministic mathematical models
    Forecasting           -> ML / time-series methods
    Optimization          -> Numerical optimization
    Natural-language UX   -> LLM

The LLM is NOT the primary root-cause engine. It explains evidence produced
by the analytical system.

============================================================
2. WHY THIS FINAL ARCHITECTURE
============================================================

The first supplied architecture is more modular and explicitly separates:

    Vision Analysis
    Process Analysis
    Root Cause
    Impact Estimation
    Recommendations
    Presentation

The second supplied architecture is more compact and directly aligned with
the supplied datasets:

    Vision Pipeline
    Simulation Pipeline
    Root-Cause Correlation
    Decision-Support Dashboard

The additional architecture introduces:

    Inspection / Production / Economic data separation
    Integration identifiers
    Novel Defect AI
    Knowledge Graph
    Predictive Engine
    What-if Simulator
    Recommendation Engine
    AI Factory Copilot

The final architecture combines these without unnecessarily turning every
component into an AI/agent system.

The result is:

    DATA INGESTION
          |
    DOMAIN-SPECIFIC AI
          |
    CROSS-DOMAIN INTEGRATION
          |
    ROOT-CAUSE + EVIDENCE
          |
    PREDICTION
          |
    SIMULATION / OPTIMIZATION
          |
    RECOMMENDATION
          |
    COPILOT
          |
    USER INTERFACE


============================================================
3. CORE REQUIREMENTS
============================================================

The system must support:

- Acceptable vs defective product classification
- Defect localization
- Novel / uncertain defect detection
- False-accept / false-reject awareness
- Manufacturing bottleneck detection
- Queue and utilization analysis
- Throughput estimation
- Quality and production impact
- Profitability / margin impact
- Root-cause evidence
- Process recommendations
- What-if scenarios
- Batch/process drift detection
- Confidence and uncertainty reporting
- Interactive decision-support visualization

The supplied challenge is software-only and advisory.

There is no requirement for:

- Live camera feed
- PLC connection
- Robotic control
- Hardware integration
- Automatic physical intervention


============================================================
4. FINAL HIGH-LEVEL SYSTEM ARCHITECTURE
============================================================

                            DATA SOURCES
                                 |
          +----------------------+----------------------+
          |                      |                      |
          v                      v                      v
   INSPECTION DATA       PRODUCTION DATA         ECONOMIC DATA
          |                      |                      |
          v                      v                      v
   +--------------+      +--------------+      +--------------+
   |  VISION AI   |      |  FLOW /      |      |  ECONOMIC    |
   |              |      |  PROCESS AI  |      |  ENGINE      |
   | Classification|     | Bottlenecks  |      | Margin       |
   | Localization |      | Throughput   |      | Scrap        |
   | Confidence   |      | Utilization  |      | Rework       |
   +------+-------+      +------+-------+      | Loss         |
          |                     |               +------+-------+
          v                     |                      |
   +--------------+             |                      |
   | NOVEL DEFECT |             |                      |
   | / UNCERTAINTY|             |                      |
   +------+-------+             |                      |
          |                     |                      |
          +---------------------+----------------------+
                                |
                                v
                    +--------------------------+
                    |    INTEGRATION LAYER     |
                    |                          |
                    | Product ID               |
                    | Batch ID                 |
                    | Station ID               |
                    | Timestamp                |
                    | Product Variant          |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |   ROOT-CAUSE ENGINE      |
                    |                          |
                    | Correlation              |
                    | Temporal Alignment       |
                    | SHAP                     |
                    | CUSUM                    |
                    | Domain Rules             |
                    | Evidence Scoring         |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    | KNOWLEDGE / EVIDENCE     |
                    | LAYER                    |
                    |                          |
                    | Historical Defects       |
                    | Machine Relations        |
                    | Process Relations        |
                    | RCA Evidence             |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |   PREDICTIVE ENGINE      |
                    |                          |
                    | Defect Risk              |
                    | Process Drift            |
                    | Throughput Forecast      |
                    | Capacity Forecast        |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |   WHAT-IF SIMULATOR      |
                    |                          |
                    | Demand Changes           |
                    | Capacity Changes         |
                    | Resource Changes         |
                    | Process Scenarios        |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    | RECOMMENDATION ENGINE    |
                    |                          |
                    | Evidence                 |
                    | Impact                   |
                    | Feasibility              |
                    | Confidence               |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |   AI FACTORY COPILOT     |
                    |                          |
                    | Explain findings         |
                    | Answer questions         |
                    | Summarize evidence      |
                    | Explain scenarios        |
                    +------------+-------------+
                                 |
                                 v
                    +--------------------------+
                    |   INDUSTRIAL DASHBOARD   |
                    +--------------------------+


============================================================
5. DATA SOURCES AND FILE HANDLING
============================================================

5.1 VISUAL INSPECTION DATA

Input:

    PNG product images
    5 defect classes + Normal
    12,000 images total

Classes:

    Normal
    Rust
    Crack
    Hole
    Scratch

Pipeline:

    PNG
      |
      v
    Pillow / OpenCV
      |
      v
    Resize + normalization + augmentation
      |
      v
    EfficientNet-B4
      |
      +----> Class
      +----> Confidence
      +----> Grad-CAM
      +----> Uncertainty
      +----> OOD flag
      |
      v
    Optional SAM refinement


5.2 PRODUCTION / SIMULATION DATA

Inputs:

    Model 1 CSV
    Model 2 CSV
    Model 3 CSV
    3000Samplesv3.mat
    ParametersFile.xls

Model complexity:

    Model 1 -> 10 features
    Model 2 -> 16 features
    Model 3 -> 77 features

The process engine extracts:

    Utilization
    Queue time
    Queue growth
    WIP
    Cycle time
    VA time
    NVA time
    Throughput
    SKU-level metrics
    Station-level metrics


5.3 .DOE FILES

The supplied README identifies the .doe files as Rockwell Arena
simulation models.

Therefore:

    .doe = simulation model/reference
    .csv = experimental simulation results

The .doe files should NOT be treated as ordinary tabular runtime data.

Use them primarily to understand or reproduce the simulation logic if
required.

The application runtime should primarily operate on the exported:

    CSV
    MAT
    XLS
    PNG

data.


============================================================
6. VISION AI ENGINE
============================================================

PURPOSE:

- Defect classification
- Defect localization
- Confidence estimation
- Novel/uncertain defect detection

PRIMARY MODEL:

    EfficientNet-B4

BASELINE:

    ResNet-50

FRAMEWORK:

    PyTorch
    torchvision
    timm

PREPROCESSING:

    OpenCV
    Pillow
    Resize
    Normalization
    CLAHE where appropriate
    Rotation
    Flip
    Controlled augmentation

LOCALIZATION:

    Grad-CAM

OPTIONAL PRECISION LOCALIZATION:

    Segment Anything Model (SAM)

UNCERTAINTY:

    Temperature Scaling
    Monte Carlo Dropout

NOVEL DEFECT:

    OOD / confidence-based detection

OUTPUT:

    {
      class,
      confidence,
      defect_heatmap,
      optional_mask,
      uncertainty,
      novelty_flag
    }


WHY THIS STACK?

PyTorch is preferred because:

- Strong pretrained computer-vision ecosystem
- Easy experimentation
- Excellent support through timm
- Easy integration with Grad-CAM
- Straightforward model debugging
- Good fit for research/hackathon development

TensorFlow/Keras is not required because the project does not need
TensorFlow-specific deployment capabilities.

YOLO is not the primary model because the supplied image dataset is
described as class-labelled images rather than a bounding-box-labelled
object-detection dataset.

Grad-CAM is therefore a better starting point for localization.


============================================================
7. PROCESS / FLOW AI ENGINE
============================================================

PURPOSE:

- Bottleneck detection
- Capacity analysis
- Throughput analysis
- Queue analysis
- Utilization analysis
- Process prediction

PIPELINE:

    CSV / MAT
       |
       v
    Pandas
       |
       v
    Feature Engineering
       |
       +--> Utilization
       +--> Queue growth
       +--> WIP
       +--> Cycle time
       +--> Throughput
       +--> VA/NVA ratios
       |
       v
    Bottleneck Engine
       |
       +--> Utilization thresholds
       +--> Queue divergence
       +--> Cycle-time imbalance
       +--> Little's Law
       |
       v
    Process Prediction
       |
       +--> Throughput
       +--> Queue time
       +--> Capacity


TECHNOLOGIES:

    Pandas
    NumPy
    SciPy
    scikit-learn

Use operations-research logic where possible rather than using deep
learning for every process decision.

Example:

    High utilization
          +
    Growing queue
          +
    Downstream throughput constraint
          |
          v
    Potential bottleneck


WHY?

The process data is structured, relatively small, and simulation-derived.
Transparent analytical methods are easier to validate and explain than
unnecessary neural networks.


============================================================
8. ROOT-CAUSE ENGINE
============================================================

This is the central intelligence layer.

INPUTS:

    Vision results
    Process state
    Batch ID
    Product ID
    Station ID
    Product variant
    Timestamp
    Economic metrics

METHODS:

    1. Statistical correlation
       - Spearman
       - Pearson where appropriate

    2. Temporal analysis
       - Lag analysis
       - Batch alignment
       - Sliding windows

    3. Drift detection
       - CUSUM

    4. ML attribution
       - XGBoost
       - SHAP

    5. Domain rules
       - Defect-specific process hypotheses

    6. Evidence scoring
       - Strength
       - Consistency
       - Confidence


IMPORTANT:

Correlation must not automatically be presented as causation.

The UI should say:

    "Strong evidence suggests..."

rather than:

    "This parameter caused the defect."

unless the evidence supports a causal conclusion.


EXAMPLE:

    Rust
      |
      +--> High queue time
      +--> Long storage time
      +--> Warehouse buildup
      |
      v
    Root-cause hypothesis:
    Excessive waiting/storage exposure

The system should display the evidence supporting that hypothesis.


============================================================
9. KNOWLEDGE / EVIDENCE LAYER
============================================================

The additional architecture proposes a Knowledge Graph.

For the first implementation, do NOT introduce a dedicated graph database
unless the graph becomes large or complex.

Use PostgreSQL relational relationships first.

Entities:

    Product
    Batch
    Station
    Machine
    Defect
    Process Parameter
    Bottleneck
    Root Cause
    Recommendation
    Scenario

Relationships can be represented through IDs:

    Product -> Batch
    Batch -> Station
    Station -> Process State
    Process State -> Defect
    Defect -> Root Cause Evidence
    Root Cause -> Recommendation

OPTIONAL FUTURE:

    Neo4j

Use Neo4j only if the project evolves into a genuinely large,
multi-hop industrial knowledge graph.

For the hackathon:

    PostgreSQL is sufficient.


============================================================
10. PREDICTIVE ENGINE
============================================================

PURPOSE:

    Future defect risk
    Process drift
    Throughput forecast
    Capacity forecast

TOOLS:

    scikit-learn
    XGBoost
    SciPy
    CUSUM
    Optional time-series models

PREDICTIONS:

    Defect probability
    Bottleneck severity
    Expected throughput
    Future queue pressure
    Process drift risk


WHY XGBOOST?

For structured manufacturing data:

- Strong performance on tabular data
- Handles nonlinear interactions
- Works well on relatively small datasets
- Easy SHAP integration
- Faster and simpler than deep tabular networks


============================================================
11. ECONOMIC / PROFITABILITY ENGINE
============================================================

The economic layer should primarily be deterministic rather than
LLM-driven.

CALCULATIONS:

    Scrap Cost
      =
    Scrapped Units × Scrap Cost per Unit

    Rework Cost
      =
    Reworked Units × Rework Cost per Unit

    Throughput Loss
      =
    Baseline Throughput - Actual Throughput

    Throughput Loss Cost
      =
    Throughput Loss × Contribution Margin

    Total Impact
      =
    Scrap Cost
    + Rework Cost
    + Throughput Loss Cost


OUTPUT:

    Current economic loss
    Loss by defect
    Loss by station
    Loss by batch
    Potential savings
    Scenario impact


TECHNOLOGY:

    Python
    NumPy
    Pandas


============================================================
12. WHAT-IF SIMULATOR
============================================================

This is a major decision-support feature.

USER CHANGES:

    Demand
    Station capacity
    Resource allocation
    Process parameters
    Queue conditions

SYSTEM CALCULATES:

    Throughput
    Queue time
    Bottleneck severity
    Defect risk
    Scrap/rework
    Economic impact

FLOW:

    Current State
         |
         v
    User Scenario
         |
         v
    Process / Prediction Models
         |
         v
    Scenario State
         |
         v
    Compare
         |
         +--> Throughput
         +--> Quality
         +--> Cost
         +--> Profitability


TECHNOLOGY:

    SciPy Optimize
    Python analytical models
    XGBoost predictions where appropriate


IMPORTANT:

All scenario outputs are advisory/simulated, not automatic control actions.


============================================================
13. RECOMMENDATION ENGINE
============================================================

The recommendation engine combines:

    Root Cause
    +
    Economic Impact
    +
    Expected Improvement
    +
    Feasibility
    +
    Confidence

Example:

    Recommendation:
    Increase downstream milling capacity.

    Evidence:
    - High milling queue
    - High utilization
    - Throughput reduction
    - Defect correlation

    Expected effect:
    Reduced queue
    Increased throughput
    Lower expected loss

    Confidence:
    High / Medium / Low


RECOMMENDATION METHODS:

    Rule-based logic
    Analytical scoring
    Scenario simulation

Do not let the LLM independently generate operational recommendations.


============================================================
14. AI FACTORY COPILOT
============================================================

The Copilot is an EXPLANATION and QUERY layer above the analytical system.

Example questions:

    "Why did defects increase in Batch 4721?"

    "Which station is causing the largest throughput loss?"

    "What would happen if milling capacity increased by 10%?"

    "Which defect type has the highest economic impact?"

The Copilot retrieves already-computed evidence and explains it.

ARCHITECTURE:

    User Question
          |
          v
    AI Factory Copilot
          |
          +--> Data Retrieval
          +--> Analytics Retrieval
          +--> RCA Evidence
          +--> Scenario Results
          |
          v
    Evidence-backed Response


OPTIONAL TECHNOLOGY:

    GPT API
    LangGraph

LangGraph should be added only if the Copilot requires multi-step tool
or data retrieval.

The core manufacturing pipeline should NOT depend on LangGraph.


============================================================
15. BACKEND
============================================================

PRIMARY:

    FastAPI

RESPONSIBILITIES:

    /api/vision
    /api/process
    /api/bottlenecks
    /api/root-cause
    /api/economic-impact
    /api/predictions
    /api/simulation
    /api/recommendations
    /api/copilot

WHY FASTAPI?

- Native Python environment
- Direct access to ML models
- Easy REST API development
- Fast enough for the project
- Automatic OpenAPI documentation
- Clean separation between frontend and analytics


============================================================
16. FRONTEND
============================================================

PRIMARY:

    Next.js
    React
    TypeScript

UI:

    Tailwind CSS
    shadcn/ui

VISUALIZATION:

    Apache ECharts

PROCESS / RCA GRAPHS:

    React Flow

ANIMATION:

    Framer Motion

DASHBOARD MODULES:

    1. Factory Overview
    2. Visual Inspection
    3. Process Health
    4. Bottleneck Analysis
    5. Root-Cause Analysis
    6. Economic Impact
    7. What-if Simulator
    8. Recommendations
    9. AI Factory Copilot
    10. Diagnostics


WHY REACT / NEXT.JS OVER STREAMLIT?

Streamlit is excellent for rapid ML prototyping.

However, the final system requires:

    Interactive factory visualization
    Custom image inspection UI
    Root-cause graphs
    What-if sliders
    Drill-down interactions
    Multiple coordinated visualizations
    Polished hackathon UI

React provides substantially more control over these interactions.

Recommended workflow:

    Streamlit
        |
        v
    Internal model prototype

    Next.js
        |
        v
    Final product dashboard


============================================================
17. DATABASE
============================================================

PRIMARY DATABASE:

    PostgreSQL

TABLES:

    products
    batches
    stations
    machines
    inspection_results
    defects
    process_states
    bottlenecks
    root_cause_evidence
    economic_impacts
    predictions
    scenarios
    recommendations

OPTIONAL:

    pgvector

Use pgvector only if the Copilot needs document / semantic retrieval.


WHY POSTGRESQL?

- Structured relational manufacturing data
- Strong joins across Product / Batch / Station / Timestamp
- Reliable
- Easy Python integration
- Can support vector search through pgvector
- Avoids unnecessary multiple-database complexity


============================================================
18. COMPLETE TECHNOLOGY STACK
============================================================

DATA INGESTION
    Python
    Pandas
    NumPy
    SciPy
    Pillow
    OpenCV
    openpyxl

COMPUTER VISION
    PyTorch
    torchvision
    timm
    EfficientNet-B4
    ResNet-50
    Grad-CAM
    Optional SAM

MACHINE LEARNING
    scikit-learn
    XGBoost

STATISTICS
    SciPy
    Statsmodels

EXPLAINABILITY
    SHAP
    Grad-CAM

PROCESS ANALYTICS
    Pandas
    NumPy
    Little's Law
    CUSUM
    Rule-based bottleneck detection

OPTIMIZATION
    SciPy Optimize
    Optional Optuna

ECONOMIC MODEL
    Python
    NumPy
    Pandas

BACKEND
    FastAPI
    Pydantic

DATABASE
    PostgreSQL
    Optional pgvector

FRONTEND
    React
    TypeScript
    Tailwind CSS
    shadcn/ui

VISUALIZATION
    Apache ECharts
    React Flow
    Framer Motion

AI COPILOT
    GPT API
    Optional LangGraph

TESTING
    pytest
    Postman

DEVOPS
    Git
    GitHub
    Docker


============================================================
19. WHY THESE TECHNOLOGIES OVER ALTERNATIVES
============================================================

PYTORCH vs TENSORFLOW

Choose PyTorch because:

    - Strong vision ecosystem
    - timm support
    - Easy Grad-CAM integration
    - Easy experimentation
    - Good research/hackathon workflow

TENSORFLOW is not necessary for this project.


FASTAPI vs FLASK

Choose FastAPI because:

    - Automatic API documentation
    - Type validation through Pydantic
    - Async support
    - Cleaner API architecture
    - Strong fit for ML inference services

Flask would work, but FastAPI gives a better API foundation.


REACT/NEXT.JS vs STREAMLIT

Choose Next.js for the final interface because:

    - More control over UX
    - Better custom visualization
    - Better animation
    - Better complex dashboard interactions
    - Cleaner separation between frontend/backend

Use Streamlit only for rapid internal prototypes.


POSTGRESQL vs MONGODB

Choose PostgreSQL because:

    - Manufacturing data is relational
    - Product/Batch/Station relationships matter
    - Strong analytical SQL support
    - Easier cross-domain joins

MongoDB is unnecessary unless the data becomes highly document-oriented.


ECHARTS vs BASIC CHART LIBRARIES

Choose Apache ECharts because:

    - Rich industrial visualizations
    - Heatmaps
    - Gauges
    - Large interactive datasets
    - Custom tooltips
    - Multiple chart types


XGBOOST vs DEEP TABULAR NETWORKS

Choose XGBoost because:

    - Manufacturing datasets are tabular
    - Dataset size is relatively small
    - Strong nonlinear modelling
    - Easy SHAP integration
    - Lower training/deployment complexity


RULES + OPERATIONS RESEARCH vs AI FOR BOTTLENECKS

Use rules + operations research because:

    - Bottlenecks have interpretable operational definitions
    - Utilization and queues have direct meaning
    - Little's Law gives a defensible analytical basis
    - Easier to validate than a black-box model


DEDICATED GRAPH DATABASE vs POSTGRESQL

Use PostgreSQL initially.

Add Neo4j only if the knowledge graph becomes a major
multi-hop reasoning component.


LLM vs DETERMINISTIC ANALYTICS

Use deterministic analytics for:

    Root cause evidence
    Economic calculations
    Bottleneck detection
    Predictions
    Optimization

Use the LLM for:

    Explanation
    Natural-language querying
    Summarization
    Evidence presentation

This prevents hallucinated numerical or operational conclusions.


============================================================
20. FINAL DATA FLOW
============================================================

                 PNG IMAGES
                     |
                     v
              Vision Pipeline
                     |
          +----------+----------+
          |                     |
       Defect                 Confidence
          |                     |
          v                     v
    Localization          Novelty/OOD
          |                     |
          +----------+----------+
                     |
                     |
CSV / MAT ---------->+<--------- Economic Data
                     |
                     v
              Integration Layer
                     |
          +----------+----------+
          |                     |
          v                     v
    Process Analysis      Economic Analysis
          |                     |
          +----------+----------+
                     |
                     v
             Root-Cause Engine
                     |
        +------------+-------------+
        |            |             |
        v            v             v
      SHAP         CUSUM       Domain Rules
        |            |             |
        +------------+-------------+
                     |
                     v
             Evidence Layer
                     |
                     v
            Predictive Engine
                     |
                     v
            What-if Simulator
                     |
                     v
          Recommendation Engine
                     |
                     v
             AI Factory Copilot
                     |
                     v
              Next.js Dashboard


============================================================
21. DASHBOARD DESIGN
============================================================

HOME / FACTORY OVERVIEW

    Factory Health
    Defect Rate
    Throughput
    OEE
    Current Bottleneck
    Economic Loss
    Active Alerts
    Top Recommendations


VISUAL INSPECTION

    Upload Image
    Classification
    Confidence
    Grad-CAM
    Optional Mask
    Novelty Flag
    Historical Similar Cases


PROCESS HEALTH

    Production Flow
    Station Utilization
    Queue Times
    WIP
    Throughput
    Bottleneck Highlighting


ROOT-CAUSE ANALYSIS

    Defect Type
          |
          v
    Process Parameters
          |
          v
    Evidence Graph

    Correlation Matrix
    SHAP
    Timeline
    Batch Drift
    Evidence Strength


ECONOMIC IMPACT

    Scrap Cost
    Rework Cost
    Throughput Loss
    Margin Impact
    Loss by Station
    Loss by Defect


WHAT-IF SIMULATOR

    Demand Slider
    Capacity Slider
    Resource Allocation
    Scenario Comparison

    Current vs Scenario:

        Throughput
        Defect Rate
        Queue
        Cost
        Profitability


RECOMMENDATIONS

    Recommendation
    Evidence
    Expected Impact
    Cost
    Feasibility
    Confidence


AI FACTORY COPILOT

    Natural-language query interface

    "Why is Line 2 underperforming?"

    "What is the strongest evidence for the current bottleneck?"

    "What happens if assembly capacity increases by 15%?"


============================================================
22. MODEL / ENGINE OUTPUT CONTRACT
============================================================

Every analytical component should return structured results.

VISION:

    class
    confidence
    localization
    uncertainty
    novelty_flag

PROCESS:

    bottleneck_station
    bottleneck_score
    utilization
    queue_time
    throughput
    capacity

ROOT CAUSE:

    hypothesis
    contributing_factors
    evidence
    evidence_strength
    confidence

ECONOMIC:

    scrap_loss
    rework_loss
    throughput_loss
    total_loss
    potential_savings

RECOMMENDATION:

    action
    rationale
    evidence
    expected_impact
    feasibility
    confidence

This common output structure makes the modules easy to integrate.


============================================================
23. SECURITY / RELIABILITY
============================================================

Include:

    Input validation
    File type validation
    Model versioning
    Confidence thresholds
    Error handling
    API validation
    Logging
    Reproducible model configurations

The system must explicitly communicate uncertainty.

Example:

    "Insufficient evidence"

is preferable to:

    "Root cause: Machine failure"

when evidence is weak.


============================================================
24. DEVELOPMENT STRUCTURE
============================================================

Recommended repository:

    industrial-ai/
    |
    +-- frontend/
    |     +-- Next.js
    |     +-- components/
    |     +-- pages/
    |     +-- charts/
    |     +-- factory/
    |
    +-- backend/
    |     +-- FastAPI
    |     +-- routes/
    |     +-- services/
    |     +-- schemas/
    |
    +-- ai/
    |     +-- vision/
    |     +-- process/
    |     +-- root_cause/
    |     +-- prediction/
    |     +-- optimization/
    |
    +-- data/
    |     +-- images/
    |     +-- csv/
    |     +-- mat/
    |     +-- configuration/
    |
    +-- models/
    |     +-- vision/
    |     +-- process/
    |
    +-- database/
    |     +-- schemas/
    |
    +-- tests/
    |
    +-- notebooks/
    |
    +-- docker/
    |
    +-- README.md


============================================================
25. IMPLEMENTATION PRIORITY
============================================================

PHASE 1 — CORE AI

    1. Load image dataset
    2. Train EfficientNet-B4
    3. Add Grad-CAM
    4. Add confidence / OOD handling

PHASE 2 — PROCESS ANALYTICS

    1. Load Model 1/2/3 CSVs
    2. Feature engineering
    3. Bottleneck detection
    4. Throughput analysis

PHASE 3 — INTEGRATION

    1. Align product/batch/station/time information
    2. Connect vision + process outputs
    3. Build RCA engine
    4. Add SHAP
    5. Add CUSUM

PHASE 4 — ECONOMIC DECISION SUPPORT

    1. Cost model
    2. Throughput-loss model
    3. What-if simulator
    4. Recommendation engine

PHASE 5 — PRODUCT

    1. FastAPI
    2. PostgreSQL
    3. Next.js
    4. ECharts
    5. React Flow
    6. Factory visualization

PHASE 6 — COPILOT

    1. Add natural-language querying
    2. Connect to analytical outputs
    3. Add evidence-backed explanations

PHASE 7 — VALIDATION

    1. Vision metrics
    2. Bottleneck validation
    3. RCA validation
    4. Uncertainty validation
    5. Scenario validation
    6. End-to-end testing


============================================================
26. FINAL RECOMMENDED STACK — ONE-LINE VERSION
============================================================

Frontend:
    Next.js + React + TypeScript + Tailwind + shadcn/ui
    + Apache ECharts + React Flow + Framer Motion

Backend:
    FastAPI + Pydantic

AI / ML:
    PyTorch + EfficientNet-B4 + timm
    + scikit-learn + XGBoost

Vision:
    OpenCV + Pillow + Grad-CAM
    + optional SAM

Analytics:
    Pandas + NumPy + SciPy + Statsmodels

Root Cause:
    Spearman/Pearson + SHAP + CUSUM + domain rules

Process:
    Little's Law + queue/utilization analysis + ML prediction

Optimization:
    SciPy Optimize

Database:
    PostgreSQL + optional pgvector

Copilot:
    GPT API + optional LangGraph

Testing:
    pytest + Postman

Deployment:
    Docker + Vercel + Render/Railway + PostgreSQL hosting

Version Control:
    Git + GitHub


============================================================
27. FINAL ARCHITECTURE PRINCIPLE
============================================================

The system should not be presented as:

    "An AI that predicts defects."

It should be presented as:

    "An AI-powered industrial decision-support system that connects
     visual quality, production flow, process conditions and economics
     to identify evidence-backed root causes and evaluate the impact
     of corrective actions."

The core intelligence chain is:

    SEE
      |
      v
    DETECT
      |
      v
    LOCALIZE
      |
      v
    CONNECT
      |
      v
    EXPLAIN
      |
      v
    PREDICT
      |
      v
    SIMULATE
      |
      v
    RECOMMEND
      |
      v
    EXPLAIN TO THE USER


The most important architectural principle is:

    AI for perception
    +
    Analytics for evidence
    +
    Operations research for process reasoning
    +
    Mathematics for economics
    +
    Optimization for scenarios
    +
    LLM for human interaction

This keeps the system technically credible, explainable, implementable,
and aligned with the supplied challenge requirements.
