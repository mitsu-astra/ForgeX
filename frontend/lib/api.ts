/**
 * API Client for Industrial AI Decision Intelligence Backend (FastAPI)
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

export interface SimulationData {
  baseline: {
    defect_rate_pct: number;
    throughput_per_hr: number;
    monthly_loss_usd: number;
  };
  simulated: {
    defect_rate_pct: number;
    throughput_per_hr: number;
    monthly_loss_usd: number;
  };
  delta: {
    defect_reduction_pct: number;
    throughput_change_pct: number;
    monthly_savings_usd: number;
  };
  recommendation_score: number;
  risk_level: string;
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
export async function runWhatIfSimulation(
  baselineParams: Record<string, number>,
  modifiedParams: Record<string, number>
): Promise<ApiResponse<SimulationData>> {
  const res = await fetch(`${API_BASE_URL}/api/v1/simulator/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      baseline_params: baselineParams,
      modified_params: modifiedParams,
    }),
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
