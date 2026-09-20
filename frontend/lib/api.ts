/**
 * API Client for ForgeX • Industrial Decision Intelligence Backend (FastAPI)
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
  errors?: string[];
}

export interface BoundingBox {
  bbox_id: number;
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  width: number;
  height: number;
  area_pixels: number;
  area_percentage: number;
  confidence: number;
  defect_type: string;
}

export interface InspectionData {
  filename: string;
  preview_base64?: string;
  prediction: {
    defect_class: string;
    confidence: number;
    class_id: number;
    probabilities: Record<string, number>;
  };
  uncertainty: {
    uncertainty_score: number;
    is_uncertain: boolean;
    threshold: number;
    confidence_interval_95: [number, number];
  };
  localization?: {
    bounding_boxes: BoundingBox[];
    defect_area_percentage: number;
    heatmap_base64?: string;
    overlay_base64?: string;
  };
  inference_time_ms: number;
  inspected_at: string;
}

export interface ActiveInspectionsData {
  latest: InspectionData | null;
  inspections: InspectionData[];
  total_inspected: number;
}

export interface BottleneckData {
  primary_bottleneck: string;
  max_utilization: number;
  line_efficiency_pct: number;
  total_wip_units: number;
  estimated_lead_time_hrs: number;
  bottlenecks: Array<{
    station: string;
    utilization: number;
    queue_time_hrs: number;
    severity: string;
    impact: string;
    recommended_action: string;
  }>;
  economic_impact: {
    hourly_throughput_loss_usd: number;
    daily_throughput_loss_usd: number;
    monthly_throughput_loss_usd: number;
  };
  all_station_utilizations: Record<string, number>;
  all_station_queue_times: Record<string, number>;
}

export interface DiagnosisData {
  root_cause: string;
  confidence: number;
  associated_defect: string;
  probabilities: Record<string, number>;
  shap_explanation: {
    base_value: number;
    top_features: Array<{
      feature: string;
      feature_value: number;
      shap_value: number;
      contribution: string;
    }>;
  };
  recommendation: string;
}

export interface ParameterProvenanceItem {
  value: number;
  unit: string;
  source: 'live' | 'stored' | 'configured' | 'fallback';
  min: number;
  max: number;
  warning_min: number;
  warning_max: number;
  step: number;
  description: string;
}

export interface MaterialProps {
  code: string;
  name: string;
  alloy_grade: string;
  yield_strength_mpa: number;
  tensile_strength_mpa: number;
  critical_hydraulic_pressure_bar: number;
  optimal_coolant_ph_min: number;
  optimal_coolant_ph_max: number;
  max_conveyor_speed_mps: number;
  cost_per_kg_usd: number;
  scrap_penalty_usd: number;
  governing_physics: string;
}

export interface SimulationBaselineData {
  batch_id: string;
  material: MaterialProps;
  available_materials: MaterialProps[];
  parameters: {
    hydraulic_pressure_bar: ParameterProvenanceItem;
    coolant_ph: ParameterProvenanceItem;
    conveyor_speed_mps: ParameterProvenanceItem;
    demand: ParameterProvenanceItem;
    spindle_feed_rate: ParameterProvenanceItem;
    [key: string]: ParameterProvenanceItem;
  };
  metrics: {
    defect_rate_pct: number;
    throughput_per_hr: number;
    peak_utilization_pct: number;
    line_efficiency_pct: number;
    wip_units: number;
    lead_time_hrs: number;
    primary_bottleneck: string;
    station_utilizations: Record<string, number>;
    fpy_pct: number;
    monthly_loss_usd: number;
    monthly_loss_inr: number;
    defect_source: string;
  };
}

export interface StationComparisonItem {
  station: string;
  baseline_utilization_pct: number;
  scenario_utilization_pct: number;
  delta_pct: number;
  is_bottleneck_baseline: boolean;
  is_bottleneck_scenario: boolean;
}

export interface SimulationScenarioHistoryItem {
  id: number;
  batch_id: string;
  material_code: string;
  baseline_defect_pct: number;
  simulated_defect_pct: number;
  defect_reduction_pct: number;
  throughput_change_pct: number;
  monthly_savings_usd: number;
  recommendation_score: number;
  risk_level: string;
  parameters: {
    baseline?: Record<string, number>;
    scenario?: Record<string, number>;
  };
  created_at: string | null;
}

export interface SimulationData {
  batch_id?: string;
  material?: MaterialProps;
  safety?: {
    status: 'SAFE' | 'WARNING' | 'BLOCKED';
    reason: string;
    violations: string[];
    warnings: string[];
    is_safe: boolean;
  };
  baseline: {
    defect_rate_pct: number;
    throughput_per_hr: number;
    monthly_loss_usd: number;
    monthly_loss_inr?: number;
    peak_utilization_pct?: number;
    line_efficiency_pct?: number;
    wip_units?: number;
    lead_time_hrs?: number;
    primary_bottleneck?: string;
    station_utilizations?: Record<string, number>;
    fpy_pct?: number;
  };
  scenario?: {
    defect_rate_pct: number;
    throughput_per_hr: number;
    monthly_loss_usd: number;
    monthly_loss_inr?: number;
    peak_utilization_pct?: number;
    line_efficiency_pct?: number;
    wip_units?: number;
    lead_time_hrs?: number;
    primary_bottleneck?: string;
    station_utilizations?: Record<string, number>;
    fpy_pct?: number;
  };
  simulated: {
    defect_rate_pct: number;
    throughput_per_hr: number;
    monthly_loss_usd: number;
    monthly_loss_inr?: number;
    peak_utilization_pct?: number;
    line_efficiency_pct?: number;
    wip_units?: number;
    lead_time_hrs?: number;
    primary_bottleneck?: string;
    station_utilizations?: Record<string, number>;
    fpy_pct?: number;
  };
  delta: {
    defect_reduction_pct: number;
    throughput_change_pct: number;
    monthly_savings_usd: number;
    monthly_savings_inr?: number;
    defect_rate_delta_pct?: number;
    throughput_delta_per_hr?: number;
    peak_utilization_delta_pct?: number;
    line_efficiency_delta_pct?: number;
    wip_delta_units?: number;
    lead_time_delta_hrs?: number;
  };
  quality_impact?: {
    crack_reduction_pct: number;
    rust_reduction_pct: number;
    scratch_reduction_pct: number;
    tool_wear_reduction_pct: number;
    composite_reduction_pct: number;
    fpy_baseline_pct: number;
    fpy_simulated_pct: number;
    governing_physics?: string;
  };
  bottleneck_impact?: {
    current_bottleneck: string;
    scenario_bottleneck: string;
    is_constraint_shifted: boolean;
    line_balance_status: string;
    station_comparison: StationComparisonItem[];
  };
  economics?: {
    monthly_scrap_savings_usd: number;
    monthly_throughput_gain_usd: number;
    total_monthly_benefit_usd: number;
    monthly_scrap_savings_inr: number;
    monthly_throughput_gain_inr: number;
    total_monthly_benefit_inr: number;
    exchange_rate: number;
    basis: string;
  };
  recommendation_score: number;
  risk_level: string;
  parameters?: {
    baseline: Record<string, number>;
    scenario: Record<string, number>;
  };
  metadata?: Record<string, string>;
}

export interface CopilotResponseData {
  response: string;
  evidence_sources: string[];
  suggested_actions: Array<{
    action_title: string;
    target_station: string;
    parameter_adjustment: string;
    expected_impact: string;
    priority: string;
  }>;
  confidence_score: number;
  guardrail_status?: 'compliant' | 'blocked' | 'warning';
  guardrail_rule_applied?: string;
  guardrail_details?: {
    rule_id?: number;
    rule_name?: string;
    category?: string;
    severity?: string;
    reason?: string;
    safe_alternative?: string;
    rules_checked?: number;
    compliant?: boolean;
  };
}

// 1. Health Check
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    const data = await res.json();
    return data.status === 'healthy';
  } catch {
    return false;
  }
}

// 2. Visual Inspection API
export async function inspectImage(
  file: File | Blob,
  includeHeatmap = true,
  mcSamples = 5
): Promise<ApiResponse<InspectionData>> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('include_heatmap', String(includeHeatmap));
  formData.append('mc_samples', String(mcSamples));

  const res = await fetch(`${API_BASE_URL}/api/v1/quality/inspect`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function getActiveInspections(): Promise<ApiResponse<ActiveInspectionsData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/quality/active-inspections`);
  return res.json();
}

export async function inspectBatchImages(
  files: File[],
  mcSamples = 1
): Promise<ApiResponse<any>> {
  const formData = new FormData();
  files.forEach((f) => formData.append('files', f));
  formData.append('mc_samples', String(mcSamples));

  const res = await fetch(`${API_BASE_URL}/api/v1/quality/batch-inspect`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

// 3. Process Bottleneck API
export async function analyzeBottlenecks(
  stationUtils?: Record<string, number>,
  stationQueues?: Record<string, number>
): Promise<ApiResponse<BottleneckData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/process/bottlenecks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      station_utilizations: stationUtils,
      station_queue_times: stationQueues,
    }),
  });
  return res.json();
}

export async function getCurrentProcessState(): Promise<ApiResponse<{
  source: string;
  has_uploaded_csv: boolean;
  state: BottleneckData;
  economic_params: Record<string, number>;
}>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/process/current-state`);
  return res.json();
}

export interface UserAnalysisMetrics {
  is_analysis_done: boolean;
  has_uploaded_csv: boolean;
  primary_defect?: string;
  inspected_count?: number;
  pass_count?: number;
  defect_count?: number;
  yield_pct?: number;
  scrap_rate_pct?: number;
  specimens_trajectory?: Array<{
    index: number;
    filename: string;
    defect_class: string;
    confidence_pct: number;
    is_pass: boolean;
    cumulative_yield_pct: number;
  }>;
  financials?: {
    gross_production_usd: number;
    baseline_scrap_loss_usd: number;
    ai_recovered_savings_usd: number;
    net_operating_profit_usd: number;
    cost_per_good_unit_before: number;
    cost_per_good_unit_after: number;
  };
  root_causes?: {
    primary_bottleneck_station: string;
    station_queue_hours: Record<string, number>;
    station_utilizations: Record<string, number>;
    top_shap_drivers: Array<{
      feature: string;
      current_value: string;
      shap_impact: number;
      impact_type: "critical" | "moderate" | "favorable";
      action: string;
    }>;
  };
}

export async function getUserAnalysisMetrics(): Promise<ApiResponse<UserAnalysisMetrics>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/process/user-analysis-metrics`);
  return res.json();
}

export async function selectSimulationStream(modelName: string): Promise<ApiResponse<any>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/process/select-simulation-stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_name: modelName }),
  });
  return res.json();
}

export async function getTelemetryStreams(): Promise<ApiResponse<any>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/process/telemetry-streams`);
  return res.json();
}

// 4. Root Cause Diagnosis & SHAP API
export async function diagnoseRootCause(
  params: Record<string, number>
): Promise<ApiResponse<DiagnosisData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/correlation/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return res.json();
}

// 5. What-If Simulation API
export async function getSimulationBaseline(
  batchId?: string
): Promise<ApiResponse<SimulationBaselineData>> {
  const url = batchId
    ? `${API_BASE_URL}/api/v1/simulator/baseline?batch_id=${encodeURIComponent(batchId)}`
    : `${API_BASE_URL}/api/v1/simulator/baseline`;
  const res = await fetch(url);
  return res.json();
}

export async function getSimulationHistory(
  batchId?: string,
  limit = 10
): Promise<ApiResponse<SimulationScenarioHistoryItem[]>> {
  let url = `${API_BASE_URL}/api/v1/simulator/history?limit=${limit}`;
  if (batchId) {
    url += `&batch_id=${encodeURIComponent(batchId)}`;
  }
  const res = await fetch(url);
  return res.json();
}

export async function stageSimulatorControl(payload: {
  batch_id?: string;
  material_code?: string;
  parameters: Record<string, number>;
  notes?: string;
}): Promise<ApiResponse<any>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/simulator/stage-control`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function runWhatIfSimulation(
  baselineParams?: Record<string, number>,
  modifiedParams?: Record<string, number>,
  options?: {
    parameters?: Record<string, number>;
    material?: string;
    batch_id?: string;
  }
): Promise<ApiResponse<SimulationData>> {
  const payload: any = {};
  if (options?.parameters) {
    payload.parameters = options.parameters;
    if (options.material) payload.material = options.material;
    if (options.batch_id) payload.batch_id = options.batch_id;
    if (baselineParams) payload.baseline_params = baselineParams;
  } else {
    payload.baseline_params = baselineParams;
    payload.modified_params = modifiedParams;
  }

  const res = await fetch(`${API_BASE_URL}/api/v1/simulator/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return res.json();
}

// 6. AI Copilot Chat API
export async function sendCopilotChat(
  message: string,
  history?: Array<{ role: string; content: string }>
): Promise<ApiResponse<CopilotResponseData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/copilot/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      history,
    }),
  });
  return res.json();
}

// 7. Analytics Overview API
export async function getAnalyticsOverview(): Promise<ApiResponse<any>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/overview`);
  return res.json();
}

// 8. ZIP Archive Upload API
export async function uploadZipArchive(file: File): Promise<ApiResponse<any>> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/api/v1/upload/zip`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export const API_BASE = API_BASE_URL;

export interface GallerySpecimen {
  id: number;
  name: string;
  defect: string;
  defect_key: string;
  severity: string;
  confidence: number;
  gradcam: boolean;
  image_url: string;
  file_path: string;
}

export interface GalleryData {
  total_count: number;
  defective_count: number;
  normal_count: number;
  specimens: GallerySpecimen[];
}

export interface PipelineRunData {
  stages: {
    ingestion: {
      status: string;
      images_count: number;
      csv_streams: string[];
      schema_signatures_matched: number;
    };
    vision: {
      status: string;
      model: string;
      inspected_count: number;
      defects_detected: number;
      defect_rate_pct: number;
      accuracy_pct: number;
      mean_inference_latency_ms: number;
      primary_defect?: string;
    };
    bottlenecks: {
      status: string;
      primary_bottleneck: string;
      max_utilization_pct: number;
      line_efficiency_pct: number;
      estimated_lead_time_hrs: number;
      total_wip_units: number;
      hourly_bottleneck_cost_usd: number;
    };
    root_cause: {
      status: string;
      primary_failure_mode: string;
      confidence_pct: number;
      associated_defect: string;
      top_shap_driver: string;
      secondary_driver: string;
    };
    simulation: {
      status: string;
      forecasted_defect_reduction_pct: number;
      monthly_savings_usd: number;
      throughput_change_pct: number;
      feasibility_score: number;
      risk_level: string;
    };
  };
  execution_time_ms: number;
  batch_id: string;
  report_id?: string;
  pdf_ready?: boolean;
}

// 9. Inspect Benchmark Sample from Dataset
export async function inspectSample(
  defectType: string,
  filename?: string,
  includeHeatmap = true,
  mcSamples = 5
): Promise<ApiResponse<InspectionData & { preview_base64?: string }>> {
  let url = `${API_BASE_URL}/api/v1/quality/inspect-sample?defect_type=${defectType}&include_heatmap=${includeHeatmap}&mc_samples=${mcSamples}`;
  if (filename) {
    url += `&filename=${encodeURIComponent(filename)}`;
  }
  const res = await fetch(url, {
    method: 'POST',
  });
  return res.json();
}

// 9b. Get Curated Benchmark Specimen Gallery
export async function getSpecimenGallery(): Promise<ApiResponse<GalleryData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/quality/gallery`);
  return res.json();
}

// 9c. Run End-to-End Decision Intelligence Pipeline
export async function runAnalysisPipeline(batchId?: string): Promise<ApiResponse<PipelineRunData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/upload/run-pipeline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batch_id: batchId, use_benchmark_data: true }),
  });
  return res.json();
}


// 10. Single File Upload
export async function uploadSingleFile(file: File): Promise<ApiResponse<any>> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE_URL}/api/v1/upload/file`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export interface DriftData {
  parameter_name: string;
  drift_detected: boolean;
  drift_start_index: number | null;
  positive_drift_detected: boolean;
  negative_drift_detected: boolean;
  max_cusum_statistic: number;
  threshold: number;
}

// 11. CUSUM Drift Analysis
export async function analyzeDrift(
  parameterName: string,
  values: number[],
  threshold = 5.0
): Promise<ApiResponse<DriftData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/process/drift-analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      parameter_name: parameterName,
      values,
      threshold,
    }),
  });
  return res.json();
}

export interface CorrelationData {
  defect_type: string;
  sample_size: number;
  correlations: Array<{
    parameter: string;
    spearman_correlation: number;
    p_value: number;
    is_statistically_significant: boolean;
    direction: string;
    strength: string;
  }>;
}

// 12. Spearman Correlations
export async function getCorrelations(
  defectType = 'rust'
): Promise<ApiResponse<CorrelationData>> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/correlation/correlations?defect_type=${defectType}`
  );
  return res.json();
}

// ==============================================================================
// 13. MANUAL OPERATOR CONTROLS (HITL & SIMULATION CONTROLLER)
// ==============================================================================

export interface MachineParameterLive {
  key: string;
  name: string;
  unit: string;
  measured_value: number;
  setpoint_value: number;
  status: "optimal" | "warning" | "critical";
  min_limit: number;
  max_limit: number;
  category: string;
  description: string;
}

export interface MachineStateData {
  mode: string;
  controller_status: string;
  interlocks_engaged: boolean;
  validation_status: string;
  parameters: Record<string, MachineParameterLive>;
  timestamp: string;
}

export interface ValidationResultData {
  parameter: string;
  requested_value: number;
  is_valid: boolean;
  status_level: "valid" | "warning" | "blocked";
  reason: string;
  min_limit: number;
  max_limit: number;
  unit: string;
}

export interface ProposalData {
  proposal_id: string;
  parameter: string;
  old_value: number;
  proposed_value: number;
  unit: string;
  is_valid: boolean;
  status_level: "valid" | "warning" | "blocked";
  reason: string;
  requires_confirmation: boolean;
  confirmation_token: string;
  timestamp: string;
}

export interface ApplyChangeData {
  event_id: string;
  parameter: string;
  old_value: number;
  applied_value: number;
  verified_value: number;
  unit: string;
  status: "success" | "warning" | "failed";
  mode: string;
  message: string;
  timestamp: string;
}

export interface AIRecommendationData {
  recommendation_id: string;
  parameter: string;
  parameter_name: string;
  current_value: number;
  recommended_value: number;
  unit: string;
  source_model: string;
  rationale: string;
  expected_risk_reduction_pct: number;
  projected_monthly_savings_usd: number;
  confidence: number;
  timestamp: string;
}

export interface AuditRecordData {
  event_id: string;
  timestamp: string;
  parameter: string;
  parameter_name: string;
  old_value: number;
  requested_value: number;
  validated_value: number;
  applied_value: number;
  verified_value: number;
  unit: string;
  operator_id: string;
  source: string;
  mode: string;
  validation_result: string;
  application_result: string;
  verification_result: string;
  notes?: string | null;
}

export interface InterventionImpactData {
  parameter: string;
  old_value: number;
  new_value: number;
  unit: string;
  pre_intervention_defect_risk: number;
  post_intervention_defect_risk: number;
  risk_delta_pct: number;
  observation_summary: string;
  timestamp: string;
}

export async function getMachineControlState(): Promise<ApiResponse<MachineStateData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/control/state`);
  return res.json();
}

export async function validateMachineSetpoint(
  parameter: string,
  value: number
): Promise<ApiResponse<ValidationResultData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/control/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ parameter, value }),
  });
  return res.json();
}

export async function proposeMachineChange(
  parameter: string,
  value: number,
  source = 'manual',
  operatorId = 'OP-104',
  notes?: string
): Promise<ApiResponse<ProposalData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/control/propose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      parameter,
      value,
      source,
      operator_id: operatorId,
      notes,
    }),
  });
  return res.json();
}

export async function applyMachineChange(
  proposalId: string,
  confirmationToken: string,
  operatorConfirmed = true,
  operatorId = 'OP-104'
): Promise<ApiResponse<ApplyChangeData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/control/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      proposal_id: proposalId,
      confirmation_token: confirmationToken,
      operator_confirmed: operatorConfirmed,
      operator_id: operatorId,
    }),
  });
  return res.json();
}

export async function getAIControlRecommendations(): Promise<ApiResponse<AIRecommendationData[]>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/control/recommendations`);
  return res.json();
}

export async function getControlAuditTrail(limit = 50): Promise<ApiResponse<AuditRecordData[]>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/control/audit-trail?limit=${limit}`);
  return res.json();
}

export async function evaluateInterventionImpact(
  parameter: string,
  oldValue: number,
  newValue: number
): Promise<ApiResponse<InterventionImpactData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/control/intervention-impact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      parameter,
      old_value: oldValue,
      new_value: newValue,
    }),
  });
  return res.json();
}

// ---------------------------------------------------------------------------
// AUTHENTICATION & DEMO PERSONAS
// ---------------------------------------------------------------------------

export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  role: string;
  avatar_initials: string;
  created_at?: string;
}

export interface DemoUser {
  id: number;
  email: string;
  full_name: string;
  role: string;
  avatar_initials: string;
  demo_password: string;
}

export async function loginUser(
  email: string,
  password: string
): Promise<ApiResponse<{ user: UserProfile; token: string }>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function getDemoUsers(): Promise<ApiResponse<{ users: DemoUser[] }>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/demo-users`);
  return res.json();
}

export async function getCurrentUser(token?: string): Promise<ApiResponse<UserProfile>> {
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, { headers });
  return res.json();
}

// ---------------------------------------------------------------------------
// SYSTEM & ML MODELS HEALTH DIAGNOSTICS
// ---------------------------------------------------------------------------

export interface SystemHealthData {
  timestamp: string;
  backend: {
    status: string;
    service_name: string;
    environment: string;
    uptime: string;
    uptime_seconds: number;
    host: string;
    python_version: string;
    platform: string;
    cpu_threads: number;
    memory_rss_mb: number;
    storage: {
      upload_dir: boolean;
      processed_dir: boolean;
      results_dir: boolean;
    };
    cors_allowed_origins: string[] | string;
  };
  database: {
    status: string;
    engine: string;
    ping_latency_ms: number;
    connection_pool: {
      size: number;
      max_overflow: number;
      pre_ping: boolean;
    };
    metrics: {
      active_batch?: string;
      total_users?: number;
      total_inspections?: number;
      total_process_states?: number;
      total_materials?: number;
      active_guardrails?: number;
    };
  };
  models: Array<{
    id: string;
    name: string;
    type: string;
    status: string;
    device: string;
    weights_path?: string;
    weights_size_mb?: number;
    input_resolution?: string;
    classes_count?: number;
    classes?: string[];
    monitored_stations?: number;
    stations_list?: string[];
    bottleneck_threshold_pct?: number;
    features_analyzed?: number;
    calibrated_materials?: number;
    governing_physics?: string[];
    features: string[];
    average_latency_ms: number;
    accuracy_metric: string;
  }>;
}

export async function getDetailedSystemHealth(): Promise<ApiResponse<SystemHealthData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/system/health`);
  return res.json();
}

// ---------------------------------------------------------------------------
// COPILOT GUARDRAILS & SAFETY RULES
// ---------------------------------------------------------------------------

export interface CopilotGuardrail {
  id: number;
  rule_name: string;
  rule_text: string;
  category: string;
  severity: string;
  is_active: boolean;
  created_at: string;
}

export async function getCopilotGuardrails(): Promise<ApiResponse<{ guardrails: CopilotGuardrail[] }>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/copilot/guardrails`);
  return res.json();
}

export async function createCopilotGuardrail(data: {
  rule_name: string;
  rule_text: string;
  category?: string;
  severity?: string;
}): Promise<ApiResponse<CopilotGuardrail>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/copilot/guardrails`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function toggleCopilotGuardrail(
  guardrailId: number,
  isActive: boolean
): Promise<ApiResponse<{ guardrail_id: number; is_active: boolean }>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/copilot/guardrails/${guardrailId}/toggle`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_active: isActive }),
  });
  return res.json();
}

export async function deleteCopilotGuardrail(guardrailId: number): Promise<ApiResponse<{ deleted: boolean }>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/copilot/guardrails/${guardrailId}`, {
    method: 'DELETE',
  });
  return res.json();
}


// =============================================================================
// System: Active Batch
// =============================================================================

export interface ActiveBatchInfo {
  batch_id: string;
  batch_name: string;
  active_material: string | null;
  active_defect: string | null;
  total_images: number;
}

/** Get the current active batch (the batch with real data in the DB). */
export async function getActiveBatch(): Promise<ApiResponse<ActiveBatchInfo>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/system/active-batch`);
  return res.json();
}

// =============================================================================
// Report API Functions
// =============================================================================

export interface ReportMeta {
  report_id: string;
  batch_id: string;
  status: string; // PENDING | GENERATING | COMPLETED | FAILED | PARTIAL
  created_at: string | null;
  completed_at: string | null;
  has_pdf: boolean;
  error_message: string | null;
}

export interface ReportPayload {
  report_id: string;
  batch_id: string;
  generated_at: string;
  input_summary: Record<string, any>;
  vision_summary: Record<string, any>;
  process_summary: Record<string, any>;
  economic_summary: Record<string, any>;
  rca_summary: Record<string, any>;
  simulation_summary: Record<string, any>;
  material_summary: Record<string, any>;
  recommendations: Array<Record<string, any>>;
}

/** Trigger report generation for a batch. Generation runs in the background. */
export async function generateReport(batchId: string): Promise<ApiResponse<any>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batch_id: batchId }),
  });
  return res.json();
}

/** List all reports (report history). */
export async function listReports(): Promise<ApiResponse<{ reports: ReportMeta[]; total: number }>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/`);
  return res.json();
}

/** Get the full canonical report payload by report_id. */
export async function getReport(reportId: string): Promise<ApiResponse<{ meta: ReportMeta; payload: ReportPayload }>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}`);
  return res.json();
}

/** Get the most recent report for a batch_id. */
export async function getReportByBatch(batchId: string): Promise<ApiResponse<{ meta: ReportMeta; payload: ReportPayload }>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/batch/${batchId}`);
  return res.json();
}

/**
 * Download the PDF report.
 * This fetches the PDF blob from the backend and triggers a browser save-as dialog,
 * which saves to the user's Downloads folder.
 */
export async function downloadReportPdf(reportId: string, batchId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}/download`);
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`PDF download failed: ${err}`);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ForgeX_Report_${batchId}_${reportId}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

/**
 * Force regeneration of a report's PDF from stored canonical payload.
 */
export async function regenerateReportPdf(reportId: string): Promise<ApiResponse<{ report_id: string; status: string; pdf_path?: string }>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}/regenerate-pdf`, {
    method: 'POST',
  });
  return res.json();
}

