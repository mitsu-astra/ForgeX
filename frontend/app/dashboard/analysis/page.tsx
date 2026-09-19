"use client";

import { useState, useEffect } from "react";
import { GitBranch, Zap, ArrowUpRight, BarChart2, ShieldCheck, Sparkles, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Slider } from "@/components/ui/slider";
import { diagnoseRootCause, getCorrelations, DiagnosisData, CorrelationData } from "@/lib/api";

export default function AnalysisPage() {
  const [pressure, setPressure] = useState([188]);
  const [coolant, setCoolant] = useState([7.1]);
  const [speed, setSpeed] = useState([1.25]);
  const [spindleFeed, setSpindleFeed] = useState([380]);
  const [diagnosis, setDiagnosis] = useState<DiagnosisData | null>(null);
  const [correlations, setCorrelations] = useState<CorrelationData | null>(null);
  const [selectedDefect, setSelectedDefect] = useState("rust");
  const [loading, setLoading] = useState(false);
  const [loadingCorr, setLoadingCorr] = useState(false);

  const fetchCorrelations = async (defect: string) => {
    setSelectedDefect(defect);
    setLoadingCorr(true);
    try {
      const res = await getCorrelations(defect);
      if (res.success && res.data) {
        setCorrelations(res.data);
      }
    } catch {
      // Fallback
    } finally {
      setLoadingCorr(false);
    }
  };

  const runDiagnosis = async () => {
    setLoading(true);
    try {
      const res = await diagnoseRootCause({
        hydraulic_pressure_bar: pressure[0],
        coolant_ph: coolant[0],
        conveyor_speed_mps: speed[0],
        feed_rate_mmpm: spindleFeed[0],
        queue_time_hours: 4.5,
        station_max_util: 0.96,
        spindle_cycles: 4000.0,
        ambient_humidity_pct: 75.0,
      });
      if (res.success && res.data) {
        setDiagnosis(res.data);
      }
    } catch {
      // Fallback offline mock state
      setDiagnosis({
        root_cause: "hydraulic_overload_stress",
        confidence: 0.942,
        associated_defect: "crack",
        probabilities: {
          hydraulic_overload_stress: 0.942,
          storage_queue_corrosion: 0.024,
          conveyor_speed_friction: 0.018,
          tool_wear_drill_misalignment: 0.011,
          nominal_in_control: 0.005,
        },
        shap_explanation: {
          base_value: 0.2,
          top_features: [
            {
              feature: "Press Hydraulic Pressure",
              feature_value: pressure[0],
              shap_value: 0.462,
              contribution: "positive",
            },
            {
              feature: "Spindle Feed Rate",
              feature_value: spindleFeed[0],
              shap_value: 0.145,
              contribution: "positive",
            },
            {
              feature: "Coolant Fluid pH",
              feature_value: coolant[0],
              shap_value: -0.052,
              contribution: "negative",
            },
            {
              feature: "Conveyor Belt Speed",
              feature_value: speed[0],
              shap_value: 0.038,
              contribution: "positive",
            },
          ],
        },
        recommendation: "Recalibrate hydraulic pressure relief valves to 172-180 bar nominal",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runDiagnosis();
    fetchCorrelations("rust");
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Root Cause Analysis & SHAP Attributions</h1>
          <p className="text-slate-600">
            Explainable AI correlating multi-modal inspection defects with discrete process parameters
          </p>
        </div>
        <Button onClick={runDiagnosis} disabled={loading} className="gradient-brand text-white">
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
          Run Live Diagnosis
        </Button>
      </div>

      {/* Interactive Process Condition Input Controls */}
      <Card className="hover-lift border-slate-200">
        <CardHeader>
          <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            Active Operating Parameter Conditions
          </CardTitle>
          <CardDescription className="text-slate-600">
            Adjust process sensor inputs to dynamically recalculate SHAP feature contributions and root-cause probabilities
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-700">Hydraulic Pressure</span>
                <span className="text-blue-600">{pressure[0]} bar</span>
              </div>
              <Slider
                value={pressure}
                onValueChange={(v) => setPressure(Array.isArray(v) ? [...v] : [v])}
                min={150}
                max={210}
                step={1}
              />
              <span className="text-[11px] text-slate-400">Nominal: 175 bar</span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-700">Coolant pH</span>
                <span className="text-blue-600">{coolant[0]} pH</span>
              </div>
              <Slider
                value={coolant}
                onValueChange={(v) => setCoolant(Array.isArray(v) ? [...v] : [v])}
                min={6.0}
                max={9.0}
                step={0.1}
              />
              <span className="text-[11px] text-slate-400">Nominal: 7.6-7.8</span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-700">Conveyor Speed</span>
                <span className="text-blue-600">{speed[0]} m/s</span>
              </div>
              <Slider
                value={speed}
                onValueChange={(v) => setSpeed(Array.isArray(v) ? [...v] : [v])}
                min={0.5}
                max={2.0}
                step={0.05}
              />
              <span className="text-[11px] text-slate-400">Nominal: 0.95 m/s</span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-slate-700">Spindle Feed Rate</span>
                <span className="text-blue-600">{spindleFeed[0]} mm/min</span>
              </div>
              <Slider
                value={spindleFeed}
                onValueChange={(v) => setSpindleFeed(Array.isArray(v) ? [...v] : [v])}
                min={200}
                max={500}
                step={10}
              />
              <span className="text-[11px] text-slate-400">Nominal: 320 mm/min</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Diagnosis & SHAP Explanation Results */}
      {diagnosis && (
        <div className="grid lg:grid-cols-3 gap-6 animate-fade-in">
          {/* Main Diagnosis Card */}
          <Card className="border-slate-200 lg:col-span-1 bg-white">
            <CardHeader>
              <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
                <Zap className="h-5 w-5 text-amber-500" />
                Root Cause Attribution
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div>
                <div className="text-xs text-slate-500 uppercase font-semibold">Primary Failure Mode</div>
                <div className="text-2xl font-bold text-slate-900 mt-1 capitalize">
                  {diagnosis.root_cause.replace(/_/g, " ")}
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Badge className="bg-red-100 text-red-700 border-red-200">
                    Defect: {diagnosis.associated_defect.toUpperCase()}
                  </Badge>
                  <Badge className="bg-blue-100 text-blue-700 border-blue-200">
                    {(diagnosis.confidence * 100).toFixed(1)}% Confidence
                  </Badge>
                </div>
              </div>

              <div className="p-4 bg-blue-50/80 border border-blue-100 rounded-xl space-y-1">
                <div className="text-xs font-bold text-blue-900">Engineering Recommendation</div>
                <div className="text-sm text-blue-800">{diagnosis.recommendation}</div>
              </div>

              {/* Class Probability Distribution */}
              <div className="space-y-2 pt-2">
                <div className="text-xs font-semibold text-slate-700">Failure Mode Probabilities</div>
                {Object.entries(diagnosis.probabilities || {}).map(([cause, prob]) => (
                  <div key={cause} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="capitalize text-slate-600">{cause.replace(/_/g, " ")}</span>
                      <span className="font-semibold text-slate-900">{(prob * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          cause === diagnosis.root_cause ? "bg-red-500" : "bg-slate-300"
                        }`}
                        style={{ width: `${Math.max(2, prob * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* SHAP Feature Contribution Waterfall */}
          <Card className="border-slate-200 lg:col-span-2 bg-white">
            <CardHeader>
              <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
                <BarChart2 className="h-5 w-5 text-purple-600" />
                SHAP Local Feature Attributions
              </CardTitle>
              <CardDescription className="text-slate-600">
                Shows exact mathematical contributions (+ pushes towards defect, - pushes towards nominal)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {diagnosis.shap_explanation.top_features.map((feat, idx) => {
                const isPositive = feat.shap_value > 0;
                const widthPct = Math.min(100, Math.abs(feat.shap_value) * 150);

                return (
                  <div key={idx} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-bold text-slate-900 text-sm">{feat.feature}</span>
                        <span className="text-xs text-slate-500 ml-2">(Value: {feat.feature_value})</span>
                      </div>
                      <Badge
                        className={
                          isPositive
                            ? "bg-red-100 text-red-700 border-red-200"
                            : "bg-green-100 text-green-700 border-green-200"
                        }
                      >
                        {isPositive ? `+${feat.shap_value.toFixed(3)} SHAP` : `${feat.shap_value.toFixed(3)} SHAP`}
                      </Badge>
                    </div>
                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden flex">
                      <div
                        className={`h-full ${isPositive ? "bg-red-500" : "bg-green-500"} rounded-full`}
                        style={{ width: `${Math.max(5, widthPct)}%` }}
                      />
                    </div>
                    <div className="text-xs text-slate-500">
                      {isPositive
                        ? `Elevated parameter directly amplifies ${diagnosis.associated_defect} defect likelihood.`
                        : "Parameter condition is operating in a stabilizing/protective range."}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Spearman Rank Correlation Matrix Section */}
      <Card className="border-slate-200 bg-white shadow-xs">
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <CardTitle className="text-xl text-slate-900 flex items-center gap-2">
                <BarChart2 className="h-5 w-5 text-blue-600" />
                Process-Defect Statistical Correlation Matrix
              </CardTitle>
              <CardDescription className="text-slate-600">
                Spearman rank correlations (r_s) and two-tailed p-values measuring monotonic associations across {correlations?.sample_size || 4000} production cycles
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {["rust", "crack", "scratch", "hole"].map((d) => (
                <Button
                  key={d}
                  size="sm"
                  variant={selectedDefect === d ? "default" : "outline"}
                  className={`capitalize text-xs font-semibold ${selectedDefect === d ? "gradient-brand text-white" : "border-slate-200"}`}
                  onClick={() => fetchCorrelations(d)}
                >
                  {d}
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loadingCorr ? (
            <div className="py-8 text-center text-slate-500 text-sm">Loading statistical correlations...</div>
          ) : correlations && correlations.correlations.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {correlations.correlations.map((c, i) => {
                const isSig = c.is_statistically_significant;
                const r = c.spearman_correlation;
                return (
                  <div
                    key={i}
                    className={`p-4 rounded-xl border space-y-2 ${
                      Math.abs(r) >= 0.7
                        ? "border-red-200 bg-red-50/40"
                        : Math.abs(r) >= 0.4
                        ? "border-amber-200 bg-amber-50/40"
                        : "border-slate-200 bg-slate-50/50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-900 text-sm">{c.parameter.replace(/_/g, " ")}</span>
                      <Badge
                        className={
                          Math.abs(r) >= 0.7
                            ? "bg-red-100 text-red-700 border-red-200"
                            : Math.abs(r) >= 0.4
                            ? "bg-amber-100 text-amber-700 border-amber-200"
                            : "bg-slate-100 text-slate-700 border-slate-200"
                        }
                      >
                        {c.strength.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="flex items-baseline justify-between pt-1">
                      <span className="text-2xl font-bold text-slate-900">
                        {r > 0 ? `+${r.toFixed(3)}` : r.toFixed(3)}
                      </span>
                      <span className="text-xs text-slate-500 font-mono">
                        p = {c.p_value < 0.001 ? "<0.001" : c.p_value.toFixed(4)}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 flex items-center justify-between">
                      <span>Direction: {c.direction}</span>
                      <span className={isSig ? "text-green-600 font-semibold" : "text-slate-400"}>
                        {isSig ? "✓ Significant (p<0.05)" : "Not Significant"}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="py-8 text-center text-slate-500 text-sm">Select a defect type to view correlation analysis</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
