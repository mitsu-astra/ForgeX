"use client";

import { useState, useEffect } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  RefreshCw,
  Sliders,
  DollarSign,
  Clock,
  Boxes,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { analyzeBottlenecks, analyzeDrift, BottleneckData, DriftData } from "@/lib/api";

const driftPresets: Record<string, number[]> = {
  "Hydraulic Pressure (bar)": [180.2, 181.5, 180.9, 182.1, 185.4, 189.2, 194.5, 201.3, 208.5, 212.0],
  "Spindle Vibration (mm/s)": [1.12, 1.15, 1.14, 1.18, 1.25, 1.42, 1.68, 2.05, 2.45, 2.82],
  "Coolant pH Level": [7.65, 7.62, 7.58, 7.50, 7.35, 7.18, 6.95, 6.82, 6.70, 6.55],
};

export default function ProcessPage() {
  const [stationUtils, setStationUtils] = useState<Record<string, number>>({
    Drilling: 0.96,
    Milling: 0.36,
    Assembly: 0.72,
    Deburring: 0.58,
    QualityCheck: 0.81,
  });

  const [stationQueues, setStationQueues] = useState<Record<string, number>>({
    Drilling: 4.12,
    Milling: 0.85,
    Assembly: 2.09,
    Deburring: 0.95,
    QualityCheck: 1.45,
  });

  const [bottleneckData, setBottleneckData] = useState<BottleneckData | null>(null);
  const [loading, setLoading] = useState(false);

  const [selectedDriftSensor, setSelectedDriftSensor] = useState("Hydraulic Pressure (bar)");
  const [driftResult, setDriftResult] = useState<DriftData | null>(null);
  const [loadingDrift, setLoadingDrift] = useState(false);

  const runDriftTest = async (sensorName: string) => {
    setSelectedDriftSensor(sensorName);
    setLoadingDrift(true);
    try {
      const vals = driftPresets[sensorName] || driftPresets["Hydraulic Pressure (bar)"];
      const res = await analyzeDrift(sensorName, vals, 5.0);
      if (res.success && res.data) {
        setDriftResult(res.data);
      }
    } finally {
      setLoadingDrift(false);
    }
  };

  const fetchBottleneckAnalysis = async () => {
    setLoading(true);
    try {
      const res = await analyzeBottlenecks(stationUtils, stationQueues);
      if (res.success && res.data) {
        setBottleneckData(res.data);
      }
    } catch {
      // Fallback offline state
      setBottleneckData({
        primary_bottleneck: "Drilling",
        max_utilization: 0.96,
        line_efficiency_pct: 71.4,
        total_wip_units: 141.9,
        estimated_lead_time_hrs: 10.66,
        bottlenecks: [
          {
            station: "Drilling",
            utilization: 0.96,
            queue_time_hrs: 4.12,
            severity: "high",
            impact: "Station at 96.0% capacity; limits line throughput",
            recommended_action: "Offload Drilling or increase station parallel buffer capacity",
          },
          {
            station: "QualityCheck",
            utilization: 0.81,
            queue_time_hrs: 1.45,
            severity: "medium",
            impact: "Station approaching capacity limit (81.0%)",
            recommended_action: "Monitor QualityCheck cycle times and rebalance line",
          },
        ],
        economic_impact: {
          hourly_throughput_loss_usd: 906.25,
          daily_throughput_loss_usd: 21750.0,
          monthly_throughput_loss_usd: 652500.0,
        },
        all_station_utilizations: {
          Drilling: 0.96,
          Milling: 0.36,
          Assembly: 0.72,
          Deburring: 0.58,
          QualityCheck: 0.81,
        },
        all_station_queue_times: {
          Drilling: 4.12,
          Milling: 0.85,
          Assembly: 2.09,
          Deburring: 0.95,
          QualityCheck: 1.45,
        },
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBottleneckAnalysis();
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Process Intelligence & Line Balance</h1>
          <p className="text-slate-600">
            Discrete-event line balance analysis, Little&apos;s Law lead time forecasting, and economic loss attribution
          </p>
        </div>
        <Button
          onClick={fetchBottleneckAnalysis}
          disabled={loading}
          className="gradient-brand text-white"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Recalculate Bottlenecks
        </Button>
      </div>

      {/* Financial & Operational Summary Cards */}
      {bottleneckData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="hover-lift border-slate-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Primary Constraint
                </span>
                <Badge className="bg-red-100 text-red-700 border-red-200">Critical</Badge>
              </div>
              <div className="text-2xl font-bold text-slate-900 mt-2">
                {bottleneckData.primary_bottleneck}
              </div>
              <div className="text-xs text-slate-500 mt-1">
                {(bottleneckData.max_utilization * 100).toFixed(1)}% Peak Utilization
              </div>
            </CardContent>
          </Card>

          <Card className="hover-lift border-slate-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Line Efficiency
                </span>
                <Activity className="h-4 w-4 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-blue-600 mt-2">
                {bottleneckData.line_efficiency_pct}%
              </div>
              <div className="text-xs text-slate-500 mt-1">Mean vs Peak Workload Balance</div>
            </CardContent>
          </Card>

          <Card className="hover-lift border-slate-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Estimated Lead Time
                </span>
                <Clock className="h-4 w-4 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-purple-600 mt-2">
                {bottleneckData.estimated_lead_time_hrs} hrs
              </div>
              <div className="text-xs text-slate-500 mt-1">
                WIP Buffer: {bottleneckData.total_wip_units} units
              </div>
            </CardContent>
          </Card>

          <Card className="hover-lift border-slate-200 bg-white">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Monthly Throughput Loss
                </span>
                <DollarSign className="h-4 w-4 text-red-600" />
              </div>
              <div className="text-2xl font-bold text-red-600 mt-2">
                ${(bottleneckData.economic_impact.monthly_throughput_loss_usd / 1000).toFixed(1)}K
              </div>
              <div className="text-xs text-slate-500 mt-1">
                ${bottleneckData.economic_impact.hourly_throughput_loss_usd.toFixed(0)}/hr bottleneck cost
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Production Flow Overview */}
      <Card className="hover-lift border-slate-200">
        <CardHeader>
          <CardTitle className="text-xl text-slate-900">Workstation Flow & Utilization Profile</CardTitle>
          <CardDescription className="text-slate-600">
            Real-time station capacity and buffer queue status across the manufacturing cell
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {Object.entries(stationUtils).map(([stName, util], idx) => {
              const utilPct = Math.round(util * 100);
              const queueHrs = stationQueues[stName] || 0;
              const isCrit = utilPct >= 85;
              const isWarn = utilPct >= 75 && utilPct < 85;

              return (
                <div
                  key={stName}
                  className={`p-4 rounded-xl border transition-all ${
                    isCrit
                      ? "border-red-300 bg-red-50/60 shadow-xs"
                      : isWarn
                      ? "border-yellow-300 bg-yellow-50/60 shadow-xs"
                      : "border-slate-200 bg-white"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-slate-500">Station {idx + 1}</span>
                    <Badge
                      className={
                        isCrit
                          ? "bg-red-100 text-red-700 border-red-200"
                          : isWarn
                          ? "bg-yellow-100 text-yellow-700 border-yellow-200"
                          : "bg-green-100 text-green-700 border-green-200"
                      }
                    >
                      {isCrit ? "Critical" : isWarn ? "Warning" : "Optimal"}
                    </Badge>
                  </div>
                  <div className="font-semibold text-slate-900 text-sm mb-2">{stName}</div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs text-slate-600">
                      <span>Util</span>
                      <span className="font-bold">{utilPct}%</span>
                    </div>
                    <Progress
                      value={utilPct}
                      className="h-1.5"
                    />
                    <div className="flex justify-between text-xs text-slate-500 pt-1">
                      <span>Queue Time</span>
                      <span className="font-mono font-medium">{queueHrs.toFixed(2)}h</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Identified Bottlenecks Table */}
      {bottleneckData && bottleneckData.bottlenecks.length > 0 && (
        <Card className="hover-lift border-slate-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-900">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Identified Operational Bottlenecks & Corrective Actions
            </CardTitle>
            <CardDescription className="text-slate-600">
              Ranked by severity and throughput degradation impact
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {bottleneckData.bottlenecks.map((b, i) => (
              <div
                key={i}
                className={`p-4 rounded-xl border space-y-2 ${
                  b.severity === "high"
                    ? "bg-red-50/50 border-red-200"
                    : "bg-yellow-50/50 border-yellow-200"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900">{b.station}</span>
                    <span className="text-xs text-slate-500">({(b.utilization * 100).toFixed(1)}% Load)</span>
                  </div>
                  <Badge
                    className={
                      b.severity === "high"
                        ? "bg-red-200 text-red-800 border-red-300"
                        : "bg-yellow-200 text-yellow-800 border-yellow-300"
                    }
                  >
                    {b.severity.toUpperCase()}
                  </Badge>
                </div>
                <p className="text-sm text-slate-700">{b.impact}</p>
                <div className="text-xs font-semibold text-blue-700 bg-blue-50/80 p-2.5 rounded-lg border border-blue-100 flex items-center gap-2">
                  <span>💡 Recommended Action:</span> {b.recommended_action}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* CUSUM Statistical Process Drift Control Chart Section */}
      <Card className="hover-lift border-slate-200 bg-white">
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <CardTitle className="text-xl text-slate-900 flex items-center gap-2">
                <Activity className="h-5 w-5 text-indigo-600" />
                Tabular CUSUM Statistical Process Drift Control
              </CardTitle>
              <CardDescription className="text-slate-600">
                Early-warning Page&apos;s CUSUM control chart detecting persistent physical parameter shifts before product defects manifest
              </CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              {Object.keys(driftPresets).map((s) => (
                <Button
                  key={s}
                  size="sm"
                  variant={selectedDriftSensor === s ? "default" : "outline"}
                  className={`text-xs font-semibold ${selectedDriftSensor === s ? "gradient-brand text-white" : "border-slate-200"}`}
                  onClick={() => runDriftTest(s)}
                >
                  {s.split(" ")[0]}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {loadingDrift ? (
            <div className="py-8 text-center text-slate-500 text-sm">Evaluating CUSUM cumulative sum statistics...</div>
          ) : driftResult ? (
            <div className="p-5 rounded-xl border border-slate-200 bg-slate-50/50 space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div>
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Monitored Parameter</span>
                  <div className="text-lg font-bold text-slate-900">{driftResult.parameter_name}</div>
                </div>
                <Badge
                  className={
                    driftResult.drift_detected
                      ? "bg-red-100 text-red-700 border-red-200 text-sm px-3 py-1"
                      : "bg-green-100 text-green-700 border-green-200 text-sm px-3 py-1"
                  }
                >
                  {driftResult.drift_detected ? "🚨 Statistical Drift Alarm Triggered" : "✓ In-Control (No Drift)"}
                </Badge>
              </div>

              <div className="grid md:grid-cols-4 gap-4 pt-2">
                <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs">
                  <div className="text-slate-500">Drift Start Timestep</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">
                    {driftResult.drift_start_index !== null ? `Cycle #${driftResult.drift_start_index}` : "None"}
                  </div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs">
                  <div className="text-slate-500">Max CUSUM Statistic</div>
                  <div className="text-base font-bold text-blue-600 mt-0.5">
                    {driftResult.max_cusum_statistic.toFixed(2)} σ
                  </div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs">
                  <div className="text-slate-500">Decision Threshold (h)</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">
                    {driftResult.threshold.toFixed(1)} σ
                  </div>
                </div>
                <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs">
                  <div className="text-slate-500">Shift Direction</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">
                    {driftResult.positive_drift_detected ? "Upper (+) Shift" : driftResult.negative_drift_detected ? "Lower (-) Shift" : "Stable"}
                  </div>
                </div>
              </div>

              <div className="text-xs text-slate-600 bg-white p-3 rounded-lg border border-slate-200">
                {driftResult.drift_detected ? (
                  <span className="text-red-700 font-medium">
                    ⚠️ Critical SPC Finding: Observations crossed decision threshold {driftResult.threshold}σ at cycle #{driftResult.drift_start_index}. Immediate recalibration recommended before batch yield drops.
                  </span>
                ) : (
                  <span className="text-green-700 font-medium">
                    ✓ Statistical parameter remains within nominal random variation boundary. No operator intervention required.
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div className="py-6 text-center text-slate-500 text-sm">
              Click a parameter above to run CUSUM control chart analysis
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
