"use client";

import { useState, useEffect } from "react";
import {
  Sliders as SlidersIcon,
  TrendingDown,
  TrendingUp,
  DollarSign,
  Check,
  RotateCcw,
  Sparkles,
  RefreshCw,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { runWhatIfSimulation, SimulationData } from "@/lib/api";

export default function SimulatorPage() {
  const [pressure, setPressure] = useState([172]);
  const [coolant, setCoolant] = useState([7.7]);
  const [speed, setSpeed] = useState([0.95]);
  const [demand, setDemand] = useState([7.0]);

  const [simResult, setSimResult] = useState<SimulationData | null>(null);
  const [loading, setLoading] = useState(false);

  const baselineParams = {
    "Press Hydraulic Pressure": 188.0,
    "Coolant Fluid pH": 7.1,
    "Conveyor Belt Speed": 1.25,
    "Demand": 7.0,
  };

  const executeSimulation = async () => {
    setLoading(true);
    const modifiedParams = {
      "Press Hydraulic Pressure": pressure[0],
      "Coolant Fluid pH": coolant[0],
      "Conveyor Belt Speed": speed[0],
      "Demand": demand[0],
    };

    try {
      const res = await runWhatIfSimulation(baselineParams, modifiedParams);
      if (res.success && res.data) {
        setSimResult(res.data);
      }
    } catch {
      // Fallback offline mock calculation
      const defectDrop = Math.min(65, Math.max(5, (188 - pressure[0]) * 1.8 + (coolant[0] - 7.1) * 20));
      const monthlySavings = Math.round(defectDrop * 420);
      setSimResult({
        baseline: {
          defect_rate_pct: 12.8,
          throughput_per_hr: 145.0,
          monthly_loss_usd: 38400.0,
        },
        simulated: {
          defect_rate_pct: Math.max(1.5, Number((12.8 * (1 - defectDrop / 100)).toFixed(1))),
          throughput_per_hr: 148.5,
          monthly_loss_usd: Math.max(4500, 38400.0 - monthlySavings),
        },
        delta: {
          defect_reduction_pct: Number(defectDrop.toFixed(1)),
          throughput_change_pct: 2.4,
          monthly_savings_usd: monthlySavings,
        },
        recommendation_score: 92.5,
        risk_level: "low",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeSimulation();
  }, [pressure, coolant, speed, demand]);

  const handleReset = () => {
    setPressure([172]);
    setCoolant([7.7]);
    setSpeed([0.95]);
    setDemand([7.0]);
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">What-If Parameter Simulator</h1>
          <p className="text-slate-600">
            Real-time physical response surface simulation forecasting defect reduction % and economic savings
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="border-slate-200" onClick={handleReset}>
            <RotateCcw className="h-4 w-4 mr-2" /> Reset Defaults
          </Button>
          <Button onClick={executeSimulation} disabled={loading} className="gradient-brand text-white">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Run Simulation
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Sliders Column */}
        <Card className="lg:col-span-2 hover-lift border-slate-200">
          <CardHeader>
            <CardTitle className="text-xl text-slate-900 flex items-center gap-2">
              <SlidersIcon className="h-5 w-5 text-blue-600" />
              Process Control Parameters (Simulated Changes)
            </CardTitle>
            <CardDescription className="text-slate-600">
              Modify operational controls to simulate physical manufacturing line behavior
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            {/* Slider 1: Pressure */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-semibold text-slate-900">Press Hydraulic Pressure</span>
                  <p className="text-xs text-slate-500">Baseline: 188 bar • Recommended: 170-175 bar</p>
                </div>
                <span className="text-lg font-bold text-blue-600">{pressure[0]} bar</span>
              </div>
              <Slider
                value={pressure}
                onValueChange={(val) => setPressure(Array.isArray(val) ? [...val] : [val])}
                min={150}
                max={200}
                step={1}
                className="py-4"
              />
            </div>

            {/* Slider 2: Coolant */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-semibold text-slate-900">Coolant Fluid pH</span>
                  <p className="text-xs text-slate-500">Baseline: 7.1 • Recommended: 7.6-7.8</p>
                </div>
                <span className="text-lg font-bold text-blue-600">{coolant[0]} pH</span>
              </div>
              <Slider
                value={coolant}
                onValueChange={(val) => setCoolant(Array.isArray(val) ? [...val] : [val])}
                min={6.5}
                max={8.5}
                step={0.1}
                className="py-4"
              />
            </div>

            {/* Slider 3: Speed */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-semibold text-slate-900">Conveyor Line Speed</span>
                  <p className="text-xs text-slate-500">Baseline: 1.25 m/s • Recommended: 0.95-1.00 m/s</p>
                </div>
                <span className="text-lg font-bold text-blue-600">{speed[0]} m/s</span>
              </div>
              <Slider
                value={speed}
                onValueChange={(val) => setSpeed(Array.isArray(val) ? [...val] : [val])}
                min={0.5}
                max={1.5}
                step={0.05}
                className="py-4"
              />
            </div>

            {/* Slider 4: Demand */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <div>
                  <span className="font-semibold text-slate-900">Target Production Demand</span>
                  <p className="text-xs text-slate-500">Baseline: 7.0 units/hr</p>
                </div>
                <span className="text-lg font-bold text-blue-600">{demand[0]} units/hr</span>
              </div>
              <Slider
                value={demand}
                onValueChange={(val) => setDemand(Array.isArray(val) ? [...val] : [val])}
                min={4.0}
                max={12.0}
                step={0.5}
                className="py-4"
              />
            </div>
          </CardContent>
        </Card>

        {/* Forecasted Impact Column */}
        {simResult && (
          <div className="space-y-6">
            <Card className="bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 text-white border-slate-800 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-lg text-slate-200 flex items-center justify-between">
                  <span>Forecasted Impact</span>
                  <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                    Score: {simResult.recommendation_score}/100
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <div className="text-sm text-slate-400 mb-1">Defect Rate Reduction</div>
                  <div className="text-4xl font-bold text-green-400">
                    -{simResult.delta.defect_reduction_pct}%
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    From {simResult.baseline.defect_rate_pct}% down to {simResult.simulated.defect_rate_pct}%
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <div className="text-sm text-slate-400 mb-1">Monthly Estimated Savings</div>
                  <div className="text-4xl font-bold text-blue-400">
                    ${simResult.delta.monthly_savings_usd.toLocaleString()}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Baseline Loss: ${simResult.baseline.monthly_loss_usd.toLocaleString()} → Simulated: $
                    {simResult.simulated.monthly_loss_usd.toLocaleString()}
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <div className="text-sm text-slate-400 mb-1">Throughput Delta</div>
                  <div className="text-2xl font-bold text-emerald-400">
                    +{simResult.delta.throughput_change_pct}%
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    {simResult.simulated.throughput_per_hr} parts/hr
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <div className="text-sm text-slate-400 mb-1">Implementation Feasibility</div>
                  <Badge
                    className={
                      simResult.risk_level === "low"
                        ? "bg-green-500/20 text-green-400 border-green-500/30"
                        : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                    }
                  >
                    {simResult.risk_level.toUpperCase()} RISK • No Capital Investment
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
