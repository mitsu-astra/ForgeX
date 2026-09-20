"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Sliders,
  TrendingDown,
  TrendingUp,
  RotateCcw,
  RefreshCw,
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  Gauge,
  Factory,
  Layers,
  ArrowRight,
  History,
  CheckCircle2,
  DollarSign,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import {
  getSimulationBaseline,
  getSimulationHistory,
  runWhatIfSimulation,
  SimulationBaselineData,
  SimulationData,
  SimulationScenarioHistoryItem,
  MaterialProps,
} from "@/lib/api";
import { formatINR, formatINRDirect, USD_TO_INR_RATE } from "@/lib/currency";

export default function SimulatorPage() {
  // Baseline and Catalog State
  const [baselineData, setBaselineData] = useState<SimulationBaselineData | null>(null);
  const [availableMaterials, setAvailableMaterials] = useState<MaterialProps[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<string>("AISI_4140");

  // Controllable Parameters State
  const [pressure, setPressure] = useState<number>(188.0);
  const [coolant, setCoolant] = useState<number>(7.1);
  const [speed, setSpeed] = useState<number>(1.25);
  const [demand, setDemand] = useState<number>(7.0);
  const [feedRate, setFeedRate] = useState<number>(280.0);

  // String intermediary states so typing isn't interrupted mid-keystroke
  const [pressureStr, setPressureStr] = useState<string>("188.0");
  const [coolantStr, setCoolantStr] = useState<string>("7.1");
  const [speedStr, setSpeedStr] = useState<string>("1.25");
  const [demandStr, setDemandStr] = useState<string>("7.0");
  const [feedRateStr, setFeedRateStr] = useState<string>("280.0");

  // Simulation & Async States
  const [simResult, setSimResult] = useState<SimulationData | null>(null);
  const [history, setHistory] = useState<SimulationScenarioHistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [baselineLoading, setBaselineLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);



  // 1. Ingest Ground-Truth Active Baseline
  const fetchBaseline = useCallback(async () => {
    setBaselineLoading(true);
    setError(null);
    try {
      const res = await getSimulationBaseline();
      if (res.success && res.data) {
        const d = res.data;
        setBaselineData(d);
        if (d.available_materials && d.available_materials.length > 0) {
          setAvailableMaterials(d.available_materials);
        }
        if (d.material?.code) {
          setSelectedMaterial(d.material.code);
        }

        // Initialize parameter controls from active baseline
        const params = d.parameters;
        if (params.hydraulic_pressure_bar) { setPressure(params.hydraulic_pressure_bar.value); setPressureStr(String(params.hydraulic_pressure_bar.value)); }
        if (params.coolant_ph) { setCoolant(params.coolant_ph.value); setCoolantStr(String(params.coolant_ph.value)); }
        if (params.conveyor_speed_mps) { setSpeed(params.conveyor_speed_mps.value); setSpeedStr(String(params.conveyor_speed_mps.value)); }
        if (params.demand) { setDemand(params.demand.value); setDemandStr(String(params.demand.value)); }
        if (params.spindle_feed_rate) { setFeedRate(params.spindle_feed_rate.value); setFeedRateStr(String(params.spindle_feed_rate.value)); }
      } else {
        setError(res.message || "Could not retrieve live manufacturing baseline.");
      }
    } catch (err: any) {
      setError(err?.message || "Failed connecting to simulator baseline service.");
    } finally {
      setBaselineLoading(false);
    }
  }, []);

  // 2. Fetch Saved Scenarios History
  const fetchHistory = useCallback(async () => {
    try {
      const res = await getSimulationHistory(undefined, 8);
      if (res.success && res.data) {
        setHistory(res.data);
      }
    } catch {
      // Non-blocking history load error
    }
  }, []);

  // 3. Execute Unified Simulation
  const executeSimulation = async () => {
    setLoading(true);
    setError(null);

    const targetParameters = {
      hydraulic_pressure_bar: pressure,
      coolant_ph: coolant,
      conveyor_speed_mps: speed,
      demand: demand,
      spindle_feed_rate: feedRate,
    };

    try {
      const res = await runWhatIfSimulation(undefined, undefined, {
        parameters: targetParameters,
        material: selectedMaterial,
        batch_id: baselineData?.batch_id,
      });

      if (res.success && res.data) {
        setSimResult(res.data);
        fetchHistory(); // Refresh history with latest run
      } else {
        setError(res.message || "Simulation failed to compute.");
      }
    } catch (err: any) {
      setError(err?.message || "Simulation server error. Please verify backend service.");
    } finally {
      setLoading(false);
    }
  };

  // Run on mount
  useEffect(() => {
    fetchBaseline();
    fetchHistory();
  }, [fetchBaseline, fetchHistory]);

  // Automatically simulate when baseline is ready
  useEffect(() => {
    if (baselineData && !simResult && !loading) {
      executeSimulation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baselineData]);

  // 4. Reset to Active Baseline
  const handleResetToBaseline = () => {
    if (!baselineData) return;
    const p = baselineData.parameters;
    if (p.hydraulic_pressure_bar) { setPressure(p.hydraulic_pressure_bar.value); setPressureStr(String(p.hydraulic_pressure_bar.value)); }
    if (p.coolant_ph) { setCoolant(p.coolant_ph.value); setCoolantStr(String(p.coolant_ph.value)); }
    if (p.conveyor_speed_mps) { setSpeed(p.conveyor_speed_mps.value); setSpeedStr(String(p.conveyor_speed_mps.value)); }
    if (p.demand) { setDemand(p.demand.value); setDemandStr(String(p.demand.value)); }
    if (p.spindle_feed_rate) { setFeedRate(p.spindle_feed_rate.value); setFeedRateStr(String(p.spindle_feed_rate.value)); }
    if (baselineData.material?.code) setSelectedMaterial(baselineData.material.code);
  };

  // 5. Restore Past Scenario from History
  const handleRestoreScenario = (item: SimulationScenarioHistoryItem) => {
    const scen = item.parameters?.scenario || {};
    if (scen.hydraulic_pressure_bar != null) { setPressure(scen.hydraulic_pressure_bar); setPressureStr(String(scen.hydraulic_pressure_bar)); }
    if (scen.coolant_ph != null) { setCoolant(scen.coolant_ph); setCoolantStr(String(scen.coolant_ph)); }
    if (scen.conveyor_speed_mps != null) { setSpeed(scen.conveyor_speed_mps); setSpeedStr(String(scen.conveyor_speed_mps)); }
    if (scen.demand != null) { setDemand(scen.demand); setDemandStr(String(scen.demand)); }
    if (scen.spindle_feed_rate != null) { setFeedRate(scen.spindle_feed_rate); setFeedRateStr(String(scen.spindle_feed_rate)); }
    if (item.material_code) setSelectedMaterial(item.material_code);
  };



  const parseSliderVal = (val: number | readonly number[]): number => {
    return Array.isArray(val) ? val[0] : typeof val === "number" ? val : 0;
  };

  // Parameter Provenance Badge Renderer
  const renderProvenanceBadge = (source?: string) => {
    switch (source) {
      case "live":
        return <Badge className="bg-emerald-500/10 text-emerald-600 border-emerald-500/20 text-[10px] py-0">Live Telemetry</Badge>;
      case "stored":
        return <Badge className="bg-blue-500/10 text-blue-600 border-blue-500/20 text-[10px] py-0">Stored Batch</Badge>;
      case "configured":
        return <Badge className="bg-slate-500/10 text-slate-600 border-slate-500/20 text-[10px] py-0">Configured</Badge>;
      default:
        return <Badge className="bg-amber-500/10 text-amber-600 border-amber-500/20 text-[10px] py-0">Fallback</Badge>;
    }
  };

  // Active Material Helper
  const currentMaterial = availableMaterials.find((m) => m.code === selectedMaterial) || baselineData?.material;

  return (
    <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Header & Action Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">What-If Decision Simulator</h1>
            <Badge className="bg-blue-600 text-white font-mono text-xs">Unified Engine v2.0</Badge>
          </div>
          <p className="text-slate-600 text-sm mt-1">
            Grounded metallurgical response surfaces, discrete-event queue surrogates, line balancing, and dual-currency financial evaluation.
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <Button
            variant="outline"
            className="border-slate-300 text-slate-700 hover:bg-slate-50"
            onClick={handleResetToBaseline}
            disabled={loading || baselineLoading}
          >
            <RotateCcw className="h-4 w-4 mr-2 text-slate-500" />
            Reset to Current State
          </Button>
          <Button
            onClick={executeSimulation}
            disabled={loading || baselineLoading}
            className="gradient-brand text-white shadow-sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Simulating..." : "Run Scenario"}
          </Button>
        </div>
      </div>

      {/* Non-Blocking Error Alert */}
      {error && (
        <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 flex items-start gap-3 text-sm">
          <AlertTriangle className="h-5 w-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold">Simulator Warning:</span> {error}
          </div>
        </div>
      )}

      {/* 1. Current Production State Banner */}
      <Card className="border-slate-200 bg-slate-50/50 shadow-sm">
        <CardContent className="p-5">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Factory className="h-3.5 w-3.5 text-blue-600" /> Active Batch
              </span>
              <div className="font-mono text-base font-bold text-slate-900">
                {baselineData?.batch_id || "BATCH-2026-001"}
              </div>
              <div className="text-[11px] text-slate-500">
                Yield: {baselineData?.metrics.fpy_pct ?? "66.7"}% • Defect: {baselineData?.metrics.defect_rate_pct ?? "33.3"}%
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="h-3.5 w-3.5 text-blue-600" /> Active Material
              </span>
              <div className="font-bold text-slate-900 text-sm truncate" title={currentMaterial?.name}>
                {currentMaterial?.name || "AISI 4140 Alloy Steel"}
              </div>
              <div className="text-[11px] text-slate-500">
                Yield: {currentMaterial?.yield_strength_mpa || 415} MPa • Limit: {currentMaterial?.critical_hydraulic_pressure_bar || 180} bar
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <Gauge className="h-3.5 w-3.5 text-blue-600" /> Line Throughput
              </span>
              <div className="text-base font-bold text-slate-900">
                {baselineData?.metrics.throughput_per_hr ?? 181.6} <span className="text-xs font-normal text-slate-500">parts/hr</span>
              </div>
              <div className="text-[11px] text-slate-500">
                Line Efficiency: {baselineData?.metrics.line_efficiency_pct ?? 78.2}%
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <AlertOctagon className="h-3.5 w-3.5 text-amber-600" /> Current Bottleneck
              </span>
              <div className="text-base font-bold text-amber-700">
                {baselineData?.metrics.primary_bottleneck || "Assembly"}
              </div>
              <div className="text-[11px] text-slate-500">
                Peak Load: {baselineData?.metrics.peak_utilization_pct ?? 75.0}%
              </div>
            </div>

            <div className="space-y-1 col-span-2 md:col-span-1">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <DollarSign className="h-3.5 w-3.5 text-rose-600" /> Monthly Scrap Loss
              </span>
              <div className="text-base font-bold text-rose-600">
                {formatINR(baselineData?.metrics.monthly_loss_usd, { compact: true })}
              </div>
              <div className="text-[11px] text-slate-500">
                ${baselineData?.metrics.monthly_loss_usd?.toLocaleString() ?? "0"} USD
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Safety Status Banner */}
      {simResult?.safety && (
        <div
          className={`p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all ${
            simResult.safety.status === "SAFE"
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-900"
              : simResult.safety.status === "WARNING"
              ? "bg-amber-500/10 border-amber-500/20 text-amber-900"
              : "bg-rose-500/10 border-rose-500/20 text-rose-900"
          }`}
        >
          <div className="flex items-start gap-3">
            {simResult.safety.status === "SAFE" && <ShieldCheck className="h-6 w-6 text-emerald-600 shrink-0 mt-0.5" />}
            {simResult.safety.status === "WARNING" && <AlertTriangle className="h-6 w-6 text-amber-600 shrink-0 mt-0.5" />}
            {simResult.safety.status === "BLOCKED" && <AlertOctagon className="h-6 w-6 text-rose-600 shrink-0 mt-0.5" />}

            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm tracking-wide uppercase">
                  Safety Envelope Status:
                </span>
                <Badge
                  className={
                    simResult.safety.status === "SAFE"
                      ? "bg-emerald-600 text-white"
                      : simResult.safety.status === "WARNING"
                      ? "bg-amber-600 text-white"
                      : "bg-rose-600 text-white"
                  }
                >
                  {simResult.safety.status}
                </Badge>
                {simResult.recommendation_score > 0 && (
                  <Badge variant="outline" className="border-slate-300 text-xs">
                    Score: {simResult.recommendation_score}/100 • Risk: {simResult.risk_level}
                  </Badge>
                )}
              </div>
              <p className="text-xs mt-1 text-slate-700">{simResult.safety.reason}</p>

              {simResult.safety.violations.length > 0 && (
                <ul className="mt-2 text-xs space-y-1 font-mono text-rose-800 bg-rose-100/50 p-2 rounded">
                  {simResult.safety.violations.map((v, i) => (
                    <li key={i} className="flex items-center gap-1.5">
                      • {v}
                    </li>
                  ))}
                </ul>
              )}
              {simResult.safety.warnings.length > 0 && (
                <ul className="mt-2 text-xs space-y-1 text-amber-800 bg-amber-100/50 p-2 rounded">
                  {simResult.safety.warnings.map((w, i) => (
                    <li key={i} className="flex items-center gap-1.5">
                      ⚠️ {w}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>


        </div>
      )}



      {/* Main Grid: Controls + Impact Matrix */}
      <div className="grid lg:grid-cols-12 gap-8">
        {/* LEFT COLUMN: SCENARIO CONTROLS (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
                  <Sliders className="h-5 w-5 text-blue-600" />
                  Controllable Setpoints
                </CardTitle>
                <Badge variant="outline" className="text-[11px] text-slate-500">
                  Dual Interactive Controls
                </Badge>
              </div>
              <CardDescription className="text-xs text-slate-500">
                Adjust operational parameters via synchronized sliders or exact numeric inputs. Values are clamped to physical boundaries.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* Material Alloy Selector */}
              <div className="space-y-1.5 pb-4 border-b border-slate-100">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-semibold text-slate-800 uppercase tracking-wide">
                    Alloy Grade Specification
                  </label>
                  <span className="text-xs text-slate-500">Material Database</span>
                </div>
                <select
                  value={selectedMaterial}
                  onChange={(e) => setSelectedMaterial(e.target.value)}
                  className="w-full text-sm rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  {availableMaterials.map((mat) => (
                    <option key={mat.code} value={mat.code}>
                      {mat.name} ({mat.alloy_grade})
                    </option>
                  ))}
                </select>
                {currentMaterial && (
                  <p className="text-[11px] text-slate-500 italic mt-1">
                    Yield: {currentMaterial.yield_strength_mpa} MPa • Critical Press Limit: {currentMaterial.critical_hydraulic_pressure_bar} bar
                  </p>
                )}
              </div>

              {/* ── PARAM HELPER: renders one parameter row ── */}
              {[
                {
                  label: "Hydraulic Pressure",
                  badge: renderProvenanceBadge(baselineData?.parameters.hydraulic_pressure_bar?.source),
                  hint: `Baseline: ${baselineData?.parameters.hydraulic_pressure_bar?.value ?? 188} bar • Safe: 155–176 bar • Range: 140–220`,
                  unit: "bar",
                  value: pressure,
                  strValue: pressureStr,
                  min: 140, max: 220, step: 1,
                  accent: "#2563eb",
                  presets: [
                    { label: "Safe", value: 165 },
                    { label: "Nominal", value: 175 },
                    { label: "Overload", value: 194 },
                  ],
                  setVal: setPressure,
                  setStr: setPressureStr,
                  onRange: (v: number) => { setPressure(v); setPressureStr(String(v)); },
                  onStep: (dir: number) => {
                    const next = Math.max(140, Math.min(220, Math.round((pressure + dir * 1) * 10) / 10));
                    setPressure(next); setPressureStr(String(next));
                  },
                  onInput: (s: string) => {
                    setPressureStr(s);
                    const n = parseFloat(s);
                    if (!isNaN(n)) setPressure(n);
                  },
                  onBlur: () => {
                    const n = parseFloat(pressureStr);
                    const clamped = isNaN(n) ? (baselineData?.parameters.hydraulic_pressure_bar?.value ?? 188) : Math.max(140, Math.min(220, n));
                    setPressure(clamped); setPressureStr(String(clamped));
                  },
                },
                {
                  label: "Coolant Fluid pH",
                  badge: renderProvenanceBadge(baselineData?.parameters.coolant_ph?.source),
                  hint: `Baseline: ${baselineData?.parameters.coolant_ph?.value ?? 7.1} pH • Optimal: ${currentMaterial?.optimal_coolant_ph_min ?? 7.6}–${currentMaterial?.optimal_coolant_ph_max ?? 7.8} • Range: 6.0–9.0`,
                  unit: "pH",
                  value: coolant,
                  strValue: coolantStr,
                  min: 6.0, max: 9.0, step: 0.1,
                  accent: "#0891b2",
                  presets: [
                    { label: "Acidic", value: 6.8 },
                    { label: "Nominal", value: 7.4 },
                    { label: "Optimal", value: 7.7 },
                    { label: "Alkaline", value: 8.2 },
                  ],
                  setVal: setCoolant,
                  setStr: setCoolantStr,
                  onRange: (v: number) => { const r = Math.round(v * 10) / 10; setCoolant(r); setCoolantStr(String(r)); },
                  onStep: (dir: number) => {
                    const next = Math.max(6.0, Math.min(9.0, Math.round((coolant + dir * 0.1) * 10) / 10));
                    setCoolant(next); setCoolantStr(String(next));
                  },
                  onInput: (s: string) => {
                    setCoolantStr(s);
                    const n = parseFloat(s);
                    if (!isNaN(n)) setCoolant(n);
                  },
                  onBlur: () => {
                    const n = parseFloat(coolantStr);
                    const clamped = isNaN(n) ? (baselineData?.parameters.coolant_ph?.value ?? 7.1) : Math.max(6.0, Math.min(9.0, Math.round(n * 10) / 10));
                    setCoolant(clamped); setCoolantStr(String(clamped));
                  },
                },
                {
                  label: "Conveyor Line Speed",
                  badge: renderProvenanceBadge(baselineData?.parameters.conveyor_speed_mps?.source),
                  hint: `Baseline: ${baselineData?.parameters.conveyor_speed_mps?.value ?? 1.25} m/s • Max: ${currentMaterial?.max_conveyor_speed_mps ?? 1.0} m/s • Range: 0.4–2.5`,
                  unit: "m/s",
                  value: speed,
                  strValue: speedStr,
                  min: 0.4, max: 2.5, step: 0.05,
                  accent: "#7c3aed",
                  presets: [
                    { label: "Slow", value: 0.8 },
                    { label: "Nominal", value: 1.25 },
                    { label: "Fast", value: 1.8 },
                  ],
                  setVal: setSpeed,
                  setStr: setSpeedStr,
                  onRange: (v: number) => { const r = Math.round(v * 100) / 100; setSpeed(r); setSpeedStr(String(r)); },
                  onStep: (dir: number) => {
                    const next = Math.max(0.4, Math.min(2.5, Math.round((speed + dir * 0.05) * 100) / 100));
                    setSpeed(next); setSpeedStr(String(next));
                  },
                  onInput: (s: string) => {
                    setSpeedStr(s);
                    const n = parseFloat(s);
                    if (!isNaN(n)) setSpeed(n);
                  },
                  onBlur: () => {
                    const n = parseFloat(speedStr);
                    const clamped = isNaN(n) ? (baselineData?.parameters.conveyor_speed_mps?.value ?? 1.25) : Math.max(0.4, Math.min(2.5, Math.round(n * 100) / 100));
                    setSpeed(clamped); setSpeedStr(String(clamped));
                  },
                },
                {
                  label: "Target Demand (Arrivals)",
                  badge: renderProvenanceBadge(baselineData?.parameters.demand?.source),
                  hint: `Baseline: ${baselineData?.parameters.demand?.value ?? 7.0} units/hr • Range: 2–20`,
                  unit: "u/h",
                  value: demand,
                  strValue: demandStr,
                  min: 2, max: 20, step: 0.5,
                  accent: "#d97706",
                  presets: [
                    { label: "Low", value: 5.0 },
                    { label: "Nominal", value: 7.0 },
                    { label: "High", value: 10.0 },
                    { label: "Peak", value: 12.5 },
                  ],
                  setVal: setDemand,
                  setStr: setDemandStr,
                  onRange: (v: number) => { const r = Math.round(v * 2) / 2; setDemand(r); setDemandStr(String(r)); },
                  onStep: (dir: number) => {
                    const next = Math.max(2, Math.min(20, Math.round((demand + dir * 0.5) * 2) / 2));
                    setDemand(next); setDemandStr(String(next));
                  },
                  onInput: (s: string) => {
                    setDemandStr(s);
                    const n = parseFloat(s);
                    if (!isNaN(n)) setDemand(n);
                  },
                  onBlur: () => {
                    const n = parseFloat(demandStr);
                    const clamped = isNaN(n) ? (baselineData?.parameters.demand?.value ?? 7.0) : Math.max(2, Math.min(20, Math.round(n * 2) / 2));
                    setDemand(clamped); setDemandStr(String(clamped));
                  },
                },
                {
                  label: "Spindle Feed Rate",
                  badge: renderProvenanceBadge(baselineData?.parameters.spindle_feed_rate?.source),
                  hint: `Baseline: ${baselineData?.parameters.spindle_feed_rate?.value ?? 280} mm/min • Taylor Limit: 320 • Range: 150–550`,
                  unit: "mm/min",
                  value: feedRate,
                  strValue: feedRateStr,
                  min: 150, max: 550, step: 5,
                  accent: "#059669",
                  presets: [
                    { label: "Safe", value: 220 },
                    { label: "Nominal", value: 280 },
                    { label: "Taylor Limit", value: 320 },
                    { label: "High", value: 390 },
                    { label: "Hole Overload", value: 460 },
                  ],
                  setVal: setFeedRate,
                  setStr: setFeedRateStr,
                  onRange: (v: number) => { setFeedRate(v); setFeedRateStr(String(v)); },
                  onStep: (dir: number) => {
                    const next = Math.max(150, Math.min(550, feedRate + dir * 5));
                    setFeedRate(next); setFeedRateStr(String(next));
                  },
                  onInput: (s: string) => {
                    setFeedRateStr(s);
                    const n = parseFloat(s);
                    if (!isNaN(n)) setFeedRate(n);
                  },
                  onBlur: () => {
                    const n = parseFloat(feedRateStr);
                    const clamped = isNaN(n) ? (baselineData?.parameters.spindle_feed_rate?.value ?? 280) : Math.max(150, Math.min(550, Math.round(n / 5) * 5));
                    setFeedRate(clamped); setFeedRateStr(String(clamped));
                  },
                },
              ].map((p) => {
                const pct = Math.max(0, Math.min(100, ((p.value - p.min) / (p.max - p.min)) * 100));
                return (
                  <div key={p.label} className="space-y-2.5 pb-4 border-b border-slate-100 last:border-0 last:pb-0">
                    {/* Label row */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-semibold text-slate-800">{p.label}</span>
                          {p.badge}
                        </div>
                        <p className="text-[11px] text-slate-500 mt-0.5">{p.hint}</p>
                      </div>

                      {/* Precision Steppers + Value Input + Unit */}
                      <div className="flex items-center gap-1 shrink-0">
                        <button
                          type="button"
                          onClick={() => p.onStep(-1)}
                          className="w-7 h-8 flex items-center justify-center rounded border border-slate-300 bg-slate-50 hover:bg-slate-100 active:bg-slate-200 text-slate-700 font-bold text-sm select-none transition shadow-2xs"
                          title={`Decrease by ${p.step}`}
                        >
                          −
                        </button>
                        <input
                          type="text"
                          inputMode="decimal"
                          value={p.strValue}
                          onFocus={(e) => e.target.select()}
                          onChange={(e) => p.onInput(e.target.value)}
                          onBlur={p.onBlur}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              (e.target as HTMLInputElement).blur();
                            }
                          }}
                          style={{ borderColor: p.accent }}
                          className="w-[74px] h-8 px-1.5 text-right font-mono font-bold text-sm rounded border-2 bg-white text-slate-900 shadow-2xs focus:outline-none focus:ring-2 focus:ring-offset-1"
                        />
                        <button
                          type="button"
                          onClick={() => p.onStep(1)}
                          className="w-7 h-8 flex items-center justify-center rounded border border-slate-300 bg-slate-50 hover:bg-slate-100 active:bg-slate-200 text-slate-700 font-bold text-sm select-none transition shadow-2xs"
                          title={`Increase by ${p.step}`}
                        >
                          +
                        </button>
                        <span className="text-xs text-slate-500 font-mono w-12 text-left pl-1">{p.unit}</span>
                      </div>
                    </div>

                    {/* Native range slider with gradient fill and high-contrast thumb */}
                    <div className="relative flex items-center gap-3">
                      <button
                        type="button"
                        onClick={() => { p.setVal(p.min); p.setStr(String(p.min)); }}
                        className="text-[10px] text-slate-400 hover:text-slate-600 font-mono w-9 text-right shrink-0"
                        title={`Set to min: ${p.min}`}
                      >
                        {p.min}
                      </button>
                      <div className="relative flex-1">
                        <input
                          type="range"
                          min={p.min}
                          max={p.max}
                          step={p.step}
                          value={p.value}
                          onChange={(e) => p.onRange(parseFloat(e.target.value))}
                          style={{
                            "--thumb-color": p.accent,
                            accentColor: p.accent,
                            background: `linear-gradient(to right, ${p.accent} 0%, ${p.accent} ${pct}%, #e2e8f0 ${pct}%, #e2e8f0 100%)`,
                          } as React.CSSProperties}
                          className="sim-range w-full h-2 rounded-full appearance-none cursor-pointer"
                        />
                      </div>
                      <button
                        type="button"
                        onClick={() => { p.setVal(p.max); p.setStr(String(p.max)); }}
                        className="text-[10px] text-slate-400 hover:text-slate-600 font-mono w-9 shrink-0"
                        title={`Set to max: ${p.max}`}
                      >
                        {p.max}
                      </button>
                    </div>

                    {/* Convenient Quick Preset Buttons */}
                    <div className="flex items-center gap-1.5 flex-wrap pt-0.5">
                      <span className="text-[10px] text-slate-400 font-medium mr-0.5">Presets:</span>
                      {p.presets.map((pr) => {
                        const isSelected = Math.abs(p.value - pr.value) < 0.01;
                        return (
                          <button
                            key={pr.label}
                            type="button"
                            onClick={() => {
                              p.setVal(pr.value);
                              p.setStr(String(pr.value));
                            }}
                            className={`text-[10px] px-2 py-0.5 rounded-full border transition font-medium ${
                              isSelected
                                ? "bg-slate-900 text-white border-slate-900 shadow-2xs font-semibold"
                                : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100 hover:text-slate-900"
                            }`}
                          >
                            {pr.label} ({pr.value})
                          </button>
                        );
                      })}
                    </div>
                  </div>
                );
              })}

              {/* Quick Action Button */}
              <Button
                onClick={executeSimulation}
                disabled={loading}
                className="w-full gradient-brand text-white font-semibold py-2 text-sm shadow"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                {loading ? "Calculating Physics & Surrogate..." : "Recalculate Scenario"}
              </Button>
            </CardContent>

          </Card>
        </div>

        {/* RIGHT COLUMN: PREDICTED IMPACT & COMPARISON (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* BASELINE VS WHAT-IF MATRIX TABLE */}
          {simResult && (
            <Card className="border-slate-200 shadow-sm overflow-hidden">
              <CardHeader className="bg-slate-50/50 pb-3 border-b border-slate-200">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base text-slate-900 flex items-center gap-2">
                    <Gauge className="h-4 w-4 text-blue-600" />
                    Baseline vs. What-If Comparison Matrix
                  </CardTitle>
                  <Badge variant="outline" className="font-mono text-xs">
                    Batch: {simResult.batch_id}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-100/75 text-slate-600 font-semibold uppercase tracking-wider text-[11px] border-b border-slate-200">
                      <tr>
                        <th className="py-2.5 px-4">Manufacturing Metric</th>
                        <th className="py-2.5 px-4 text-right">Current Baseline</th>
                        <th className="py-2.5 px-4 text-right">What-If Scenario</th>
                        <th className="py-2.5 px-4 text-right">Net Delta</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-mono">
                      {/* Defect Rate */}
                      <tr className="hover:bg-slate-50/50">
                        <td className="py-2.5 px-4 font-sans font-medium text-slate-900 flex items-center gap-1.5">
                          Defect Rate (%)
                        </td>
                        <td className="py-2.5 px-4 text-right text-slate-700">
                          {simResult.baseline.defect_rate_pct}%
                        </td>
                        <td className="py-2.5 px-4 text-right font-bold text-slate-900">
                          {simResult.simulated.defect_rate_pct}%
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <span
                            className={`inline-flex items-center gap-1 font-bold ${
                              (simResult.delta.defect_rate_delta_pct ?? 0) <= 0
                                ? "text-emerald-600"
                                : "text-rose-600"
                            }`}
                          >
                            {(simResult.delta.defect_rate_delta_pct ?? 0) > 0 ? "+" : ""}
                            {simResult.delta.defect_rate_delta_pct}%
                          </span>
                        </td>
                      </tr>

                      {/* Throughput */}
                      <tr className="hover:bg-slate-50/50">
                        <td className="py-2.5 px-4 font-sans font-medium text-slate-900">
                          Throughput (parts/hr)
                        </td>
                        <td className="py-2.5 px-4 text-right text-slate-700">
                          {simResult.baseline.throughput_per_hr}
                        </td>
                        <td className="py-2.5 px-4 text-right font-bold text-slate-900">
                          {simResult.simulated.throughput_per_hr}
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <span
                            className={`inline-flex items-center gap-1 font-bold ${
                              (simResult.delta.throughput_delta_per_hr ?? 0) >= 0
                                ? "text-emerald-600"
                                : "text-rose-600"
                            }`}
                          >
                            {(simResult.delta.throughput_delta_per_hr ?? 0) > 0 ? "+" : ""}
                            {simResult.delta.throughput_delta_per_hr}
                          </span>
                        </td>
                      </tr>

                      {/* Peak Station Utilization */}
                      <tr className="hover:bg-slate-50/50">
                        <td className="py-2.5 px-4 font-sans font-medium text-slate-900">
                          Peak Station Utilization (%)
                        </td>
                        <td className="py-2.5 px-4 text-right text-slate-700">
                          {simResult.baseline.peak_utilization_pct}%
                        </td>
                        <td className="py-2.5 px-4 text-right font-bold text-slate-900">
                          {simResult.simulated.peak_utilization_pct}%
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <span
                            className={`inline-flex items-center gap-1 font-bold ${
                              (simResult.delta.peak_utilization_delta_pct ?? 0) <= 0
                                ? "text-emerald-600"
                                : "text-amber-600"
                            }`}
                          >
                            {(simResult.delta.peak_utilization_delta_pct ?? 0) > 0 ? "+" : ""}
                            {simResult.delta.peak_utilization_delta_pct}%
                          </span>
                        </td>
                      </tr>

                      {/* Line Efficiency */}
                      <tr className="hover:bg-slate-50/50">
                        <td className="py-2.5 px-4 font-sans font-medium text-slate-900">
                          Line Efficiency (%)
                        </td>
                        <td className="py-2.5 px-4 text-right text-slate-700">
                          {simResult.baseline.line_efficiency_pct}%
                        </td>
                        <td className="py-2.5 px-4 text-right font-bold text-slate-900">
                          {simResult.simulated.line_efficiency_pct}%
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <span
                            className={`inline-flex items-center gap-1 font-bold ${
                              (simResult.delta.line_efficiency_delta_pct ?? 0) >= 0
                                ? "text-emerald-600"
                                : "text-rose-600"
                            }`}
                          >
                            {(simResult.delta.line_efficiency_delta_pct ?? 0) > 0 ? "+" : ""}
                            {simResult.delta.line_efficiency_delta_pct}%
                          </span>
                        </td>
                      </tr>

                      {/* WIP Units */}
                      <tr className="hover:bg-slate-50/50">
                        <td className="py-2.5 px-4 font-sans font-medium text-slate-900">
                          Queue WIP Accumulation (units)
                        </td>
                        <td className="py-2.5 px-4 text-right text-slate-700">
                          {simResult.baseline.wip_units}
                        </td>
                        <td className="py-2.5 px-4 text-right font-bold text-slate-900">
                          {simResult.simulated.wip_units}
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <span
                            className={`inline-flex items-center gap-1 font-bold ${
                              (simResult.delta.wip_delta_units ?? 0) <= 0
                                ? "text-emerald-600"
                                : "text-amber-600"
                            }`}
                          >
                            {(simResult.delta.wip_delta_units ?? 0) > 0 ? "+" : ""}
                            {simResult.delta.wip_delta_units}
                          </span>
                        </td>
                      </tr>

                      {/* Estimated Lead Time */}
                      <tr className="hover:bg-slate-50/50">
                        <td className="py-2.5 px-4 font-sans font-medium text-slate-900">
                          Estimated Cycle Lead Time (hrs)
                        </td>
                        <td className="py-2.5 px-4 text-right text-slate-700">
                          {simResult.baseline.lead_time_hrs}h
                        </td>
                        <td className="py-2.5 px-4 text-right font-bold text-slate-900">
                          {simResult.simulated.lead_time_hrs}h
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <span
                            className={`inline-flex items-center gap-1 font-bold ${
                              (simResult.delta.lead_time_delta_hrs ?? 0) <= 0
                                ? "text-emerald-600"
                                : "text-amber-600"
                            }`}
                          >
                            {(simResult.delta.lead_time_delta_hrs ?? 0) > 0 ? "+" : ""}
                            {simResult.delta.lead_time_delta_hrs}h
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* DUAL-CURRENCY ECONOMIC IMPACT CARDS */}
          {simResult && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="border-slate-200 bg-emerald-50/50 shadow-sm">
                <CardContent className="p-4 space-y-1">
                  <span className="text-[11px] font-semibold text-emerald-800 uppercase tracking-wide">
                    Monthly Scrap Savings
                  </span>
                  <div className="text-xl font-bold text-emerald-700">
                    {formatINRDirect(simResult.economics?.monthly_scrap_savings_inr, true)}
                  </div>
                  <div className="text-xs text-slate-500 font-mono">
                    ${simResult.economics?.monthly_scrap_savings_usd.toLocaleString() ?? "0"} USD
                  </div>
                </CardContent>
              </Card>

              <Card className="border-slate-200 bg-blue-50/50 shadow-sm">
                <CardContent className="p-4 space-y-1">
                  <span className="text-[11px] font-semibold text-blue-800 uppercase tracking-wide">
                    Throughput Revenue Gain
                  </span>
                  <div className="text-xl font-bold text-blue-700">
                    {formatINRDirect(simResult.economics?.monthly_throughput_gain_inr, true)}
                  </div>
                  <div className="text-xs text-slate-500 font-mono">
                    ${simResult.economics?.monthly_throughput_gain_usd.toLocaleString() ?? "0"} USD
                  </div>
                </CardContent>
              </Card>

              <Card className="border-slate-200 bg-gradient-to-br from-slate-900 to-slate-800 text-white shadow-sm">
                <CardContent className="p-4 space-y-1">
                  <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wide flex items-center gap-1">
                    <Zap className="h-3 w-3" /> Total Monthly Benefit
                  </span>
                  <div className="text-xl font-bold text-emerald-400">
                    {formatINRDirect(simResult.economics?.total_monthly_benefit_inr, true)}
                  </div>
                  <div className="text-xs text-slate-300 font-mono">
                    ${simResult.delta.monthly_savings_usd.toLocaleString()} USD
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* BOTTLENECK & STATION UTILIZATIONS */}
          {simResult?.bottleneck_impact && (
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm text-slate-900 flex items-center gap-2">
                    <Layers className="h-4 w-4 text-blue-600" />
                    Station-by-Station Utilization & Bottleneck Shifts
                  </CardTitle>
                  <Badge
                    className={
                      simResult.bottleneck_impact.is_constraint_shifted
                        ? "bg-amber-500/10 text-amber-700 border-amber-500/20"
                        : "bg-emerald-500/10 text-emerald-700 border-emerald-500/20"
                    }
                  >
                    {simResult.bottleneck_impact.is_constraint_shifted
                      ? `Shifted: ${simResult.bottleneck_impact.current_bottleneck} → ${simResult.bottleneck_impact.scenario_bottleneck}`
                      : `Constraint Maintained: ${simResult.bottleneck_impact.current_bottleneck}`}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {simResult.bottleneck_impact.station_comparison.map((st) => (
                  <div key={st.station} className="space-y-1.5">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-semibold text-slate-800 flex items-center gap-1.5">
                        {st.station}
                        {st.is_bottleneck_scenario && (
                          <Badge className="bg-rose-500/10 text-rose-700 border-rose-500/20 text-[10px] py-0">
                            Primary Bottleneck
                          </Badge>
                        )}
                      </span>
                      <div className="flex items-center gap-3 font-mono">
                        <span className="text-slate-500">Base: {st.baseline_utilization_pct}%</span>
                        <ArrowRight className="h-3 w-3 text-slate-400" />
                        <span className="font-bold text-slate-900">What-If: {st.scenario_utilization_pct}%</span>
                        <span
                          className={`font-bold ${
                            st.delta_pct <= 0 ? "text-emerald-600" : "text-amber-600"
                          }`}
                        >
                          ({st.delta_pct > 0 ? "+" : ""}
                          {st.delta_pct}%)
                        </span>
                      </div>
                    </div>
                    <Progress value={st.scenario_utilization_pct} className="h-2" />
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* QUALITY DEFECT BREAKDOWN */}
          {simResult?.quality_impact && (
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-slate-900 flex items-center gap-2">
                  <TrendingDown className="h-4 w-4 text-emerald-600" />
                  Physical Defect Mode Reductions (Grounded Metallurgy)
                </CardTitle>
                <CardDescription className="text-xs text-slate-500">
                  {simResult.quality_impact.governing_physics || "Simulated via Griffith fracture, Pourbaix kinetics, Archard abrasion, and Taylor tool wear."}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[11px] text-slate-500 font-medium">Fracture Crack</div>
                    <div className="text-lg font-bold text-emerald-600 font-mono mt-1">
                      -{simResult.quality_impact.crack_reduction_pct}%
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[11px] text-slate-500 font-medium">Pourbaix Rust</div>
                    <div className="text-lg font-bold text-emerald-600 font-mono mt-1">
                      -{simResult.quality_impact.rust_reduction_pct}%
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[11px] text-slate-500 font-medium">Archard Scratch</div>
                    <div className="text-lg font-bold text-emerald-600 font-mono mt-1">
                      -{simResult.quality_impact.scratch_reduction_pct}%
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-[11px] text-slate-500 font-medium">Spindle Tool Wear</div>
                    <div className="text-lg font-bold text-emerald-600 font-mono mt-1">
                      {simResult.quality_impact.tool_wear_reduction_pct >= 0 ? "-" : "+"}
                      {Math.abs(simResult.quality_impact.tool_wear_reduction_pct)}%
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* 9. SCENARIO HISTORY TABLE */}
      <Card className="border-slate-200 shadow-sm">
        <CardHeader className="pb-3 border-b border-slate-200 bg-slate-50/50">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base text-slate-900 flex items-center gap-2">
              <History className="h-4 w-4 text-blue-600" />
              Recent What-If Scenarios History
            </CardTitle>
            <Badge variant="outline" className="text-xs font-mono">
              Audit Records ({history.length})
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {history.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No saved scenarios recorded yet. Adjust parameters and click &ldquo;Run Scenario&rdquo; to persist simulation evaluations.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100/75 text-slate-600 font-semibold uppercase tracking-wider text-[11px] border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-4">Timestamp</th>
                    <th className="py-2.5 px-4">Batch / Alloy</th>
                    <th className="py-2.5 px-4">Simulated Setpoints</th>
                    <th className="py-2.5 px-4 text-right">Defect Drop</th>
                    <th className="py-2.5 px-4 text-right">Throughput Δ</th>
                    <th className="py-2.5 px-4 text-right">Monthly Savings</th>
                    <th className="py-2.5 px-4 text-center">Safety</th>
                    <th className="py-2.5 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {history.map((item) => {
                    const p = item.parameters?.scenario || {};
                    return (
                      <tr key={item.id} className="hover:bg-slate-50/75">
                        <td className="py-2.5 px-4 text-slate-500 text-[11px]">
                          {item.created_at || "Recent"}
                        </td>
                        <td className="py-2.5 px-4 text-slate-900 font-sans">
                          <span className="font-semibold font-mono">{item.batch_id}</span>
                          <span className="text-xs text-slate-500 ml-1.5 font-sans">({item.material_code})</span>
                        </td>
                        <td className="py-2.5 px-4 text-[11px] text-slate-600">
                          {p.hydraulic_pressure_bar ? `${p.hydraulic_pressure_bar} bar` : ""}
                          {p.coolant_ph ? ` • ${p.coolant_ph} pH` : ""}
                          {p.demand ? ` • D:${p.demand}` : ""}
                        </td>
                        <td className="py-2.5 px-4 text-right font-bold text-emerald-600">
                          -{item.defect_reduction_pct}%
                        </td>
                        <td className="py-2.5 px-4 text-right text-slate-700">
                          +{item.throughput_change_pct}%
                        </td>
                        <td className="py-2.5 px-4 text-right font-bold text-blue-600">
                          {formatINR(item.monthly_savings_usd, { compact: true })}
                        </td>
                        <td className="py-2.5 px-4 text-center">
                          <Badge
                            variant="outline"
                            className={
                              item.risk_level.toLowerCase() === "low"
                                ? "border-emerald-500/30 text-emerald-600 bg-emerald-50 text-[10px]"
                                : "border-amber-500/30 text-amber-600 bg-amber-50 text-[10px]"
                            }
                          >
                            {item.risk_level.toUpperCase()}
                          </Badge>
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleRestoreScenario(item)}
                            className="h-7 text-xs text-blue-600 hover:text-blue-800 hover:bg-blue-50 font-sans"
                          >
                            Restore
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
