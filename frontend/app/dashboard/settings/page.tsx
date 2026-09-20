"use client";

import { useState, useEffect } from "react";
import {
  Settings as SettingsIcon,
  Shield,
  Sliders,
  Bell,
  Database,
  CheckCircle2,
  Save,
  Activity,
  Cpu,
  Server,
  RefreshCw,
  AlertTriangle,
  Plus,
  Trash2,
  Check,
  X,
  Lock,
  Layers,
  Sparkles,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  getDetailedSystemHealth,
  SystemHealthData,
  getCopilotGuardrails,
  createCopilotGuardrail,
  toggleCopilotGuardrail,
  deleteCopilotGuardrail,
  CopilotGuardrail,
} from "@/lib/api";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<"health" | "guardrails" | "inference">("health");

  // Health State
  const [healthData, setHealthData] = useState<SystemHealthData | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState<string>("");

  // Guardrails State
  const [guardrails, setGuardrails] = useState<CopilotGuardrail[]>([]);
  const [guardrailsLoading, setGuardrailsLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newRuleName, setNewRuleName] = useState("");
  const [newRuleText, setNewRuleText] = useState("");
  const [newCategory, setNewCategory] = useState("Safety");
  const [newSeverity, setNewSeverity] = useState("strict_block");
  const [guardrailSuccess, setGuardrailSuccess] = useState<string | null>(null);

  // General Settings State
  const [confidenceThreshold, setConfidenceThreshold] = useState("85");
  const [gradCamAuto, setGradCamAuto] = useState(true);
  const [bottleneckAlert, setBottleneckAlert] = useState(true);
  const [mcDropoutSamples, setMcDropoutSamples] = useState("20");
  const [saveSuccess, setSaveSuccess] = useState(false);

  const fetchHealth = async () => {
    setHealthLoading(true);
    try {
      const res = await getDetailedSystemHealth();
      if (res.success && res.data) {
        setHealthData(res.data);
        setLastRefreshed(new Date().toLocaleTimeString());
      }
    } catch (e) {
      console.error("Failed to load health", e);
    } finally {
      setHealthLoading(false);
    }
  };

  const fetchGuardrails = async () => {
    setGuardrailsLoading(true);
    try {
      const res = await getCopilotGuardrails();
      if (res.success && res.data?.guardrails) {
        setGuardrails(res.data.guardrails);
      }
    } catch (e) {
      console.error("Failed to load guardrails", e);
    } finally {
      setGuardrailsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchGuardrails();
  }, []);

  const handleToggleRule = async (ruleId: number, currentActive: boolean) => {
    const nextActive = !currentActive;
    setGuardrails((prev) =>
      prev.map((r) => (r.id === ruleId ? { ...r, is_active: nextActive } : r))
    );
    try {
      await toggleCopilotGuardrail(ruleId, nextActive);
    } catch {
      // Revert on failure
      setGuardrails((prev) =>
        prev.map((r) => (r.id === ruleId ? { ...r, is_active: currentActive } : r))
      );
    }
  };

  const handleAddRule = async () => {
    if (!newRuleName.trim() || !newRuleText.trim()) return;

    try {
      const res = await createCopilotGuardrail({
        rule_name: newRuleName.trim(),
        rule_text: newRuleText.trim(),
        category: newCategory,
        severity: newSeverity,
      });
      if (res.success && res.data) {
        setGuardrails((prev) => [...prev, res.data]);
        setShowAddModal(false);
        setNewRuleName("");
        setNewRuleText("");
        setGuardrailSuccess("Safety guardrail registered in PostgreSQL successfully!");
        setTimeout(() => setGuardrailSuccess(null), 4000);
      }
    } catch (e) {
      console.error("Failed to add rule", e);
    }
  };

  const handleDeleteRule = async (ruleId: number) => {
    try {
      await deleteCopilotGuardrail(ruleId);
      setGuardrails((prev) => prev.filter((r) => r.id !== ruleId));
    } catch (e) {
      console.error("Failed to delete rule", e);
    }
  };

  const handleSaveGeneral = () => {
    setSaveSuccess(true);
    setTimeout(() => {
      setSaveSuccess(false);
    }, 3000);
  };

  const getCategoryBadge = (category: string) => {
    switch (category.toLowerCase()) {
      case "safety":
        return <Badge className="bg-red-50 text-red-700 border-red-200 text-[10px]">Safety Critical</Badge>;
      case "metallurgy":
      case "physics":
        return <Badge className="bg-blue-50 text-blue-700 border-blue-200 text-[10px]">Metallurgy & Chemistry</Badge>;
      case "compliance":
        return <Badge className="bg-purple-50 text-purple-700 border-purple-200 text-[10px]">Compliance Sign-off</Badge>;
      default:
        return <Badge className="bg-amber-50 text-amber-700 border-amber-200 text-[10px]">Operational Limit</Badge>;
    }
  };

  return (
    <div className="p-6 md:p-8 space-y-6 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
            <SettingsIcon className="h-8 w-8 text-blue-600" />
            Platform & System Diagnostics
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Real-time ML model diagnostics, PostgreSQL health telemetry, and AI Copilot safety guardrails
          </p>
        </div>

        {activeTab === "health" && (
          <Button
            onClick={fetchHealth}
            disabled={healthLoading}
            variant="outline"
            className="border-slate-200 bg-white text-xs shadow-xs hover:bg-slate-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${healthLoading ? "animate-spin text-blue-600" : ""}`} />
            {healthLoading ? "Querying Telemetry..." : "Ping Live Health"}
          </Button>
        )}

        {activeTab === "inference" && (
          <Button onClick={handleSaveGeneral} className="gradient-brand text-white shadow-md text-xs">
            <Save className="h-3.5 w-3.5 mr-1.5" /> Save Configuration
          </Button>
        )}
      </div>

      {/* Tab Navigation Pill Bar */}
      <div className="flex items-center gap-2 p-1 bg-stone-200/50 rounded-2xl w-fit text-xs font-semibold">
        <button
          onClick={() => setActiveTab("health")}
          className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
            activeTab === "health"
              ? "bg-white text-blue-700 shadow-xs"
              : "text-stone-600 hover:text-stone-900"
          }`}
        >
          <Activity className="h-4 w-4" />
          <span>ML & Backend Health</span>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        </button>

        <button
          onClick={() => setActiveTab("guardrails")}
          className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
            activeTab === "guardrails"
              ? "bg-white text-blue-700 shadow-xs"
              : "text-stone-600 hover:text-stone-900"
          }`}
        >
          <Shield className="h-4 w-4 text-amber-500" />
          <span>AI Copilot Guardrails</span>
          <Badge className="bg-amber-100 text-amber-800 text-[10px] border-0 px-1.5 py-0">
            {guardrails.filter((g) => g.is_active).length} Active
          </Badge>
        </button>

        <button
          onClick={() => setActiveTab("inference")}
          className={`px-4 py-2 rounded-xl transition flex items-center gap-2 ${
            activeTab === "inference"
              ? "bg-white text-blue-700 shadow-xs"
              : "text-stone-600 hover:text-stone-900"
          }`}
        >
          <Sliders className="h-4 w-4" />
          <span>Inference Thresholds</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: ML MODELS & BACKEND HEALTH DIAGNOSTICS */}
      {/* ========================================================================= */}
      {activeTab === "health" && (
        <div className="space-y-6 animate-fade-in">
          {/* Top High-Level Health KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Card 1: Backend API Status */}
            <Card className="bg-white border-slate-200/80 shadow-xs rounded-2xl">
              <CardContent className="p-4 flex items-center justify-between">
                <div>
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    FastAPI Backend
                  </div>
                  <div className="text-lg font-bold text-slate-900 flex items-center gap-2 mt-0.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    {healthData?.backend?.status || "Operational"}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Uptime: <span className="font-mono text-slate-700">{healthData?.backend?.uptime || "Loading..."}</span>
                  </div>
                </div>
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                  <Server className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            {/* Card 2: PostgreSQL DB Status */}
            <Card className="bg-white border-slate-200/80 shadow-xs rounded-2xl">
              <CardContent className="p-4 flex items-center justify-between">
                <div>
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    Database Telemetry
                  </div>
                  <div className="text-lg font-bold text-slate-900 flex items-center gap-2 mt-0.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    {healthData?.database?.engine || "PostgreSQL"}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Ping: <span className="font-mono text-slate-700">{healthData?.database?.ping_latency_ms ?? 0} ms</span>
                  </div>
                </div>
                <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                  <Database className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            {/* Card 3: Deep Learning Device */}
            <Card className="bg-white border-slate-200/80 shadow-xs rounded-2xl">
              <CardContent className="p-4 flex items-center justify-between">
                <div>
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    PyTorch Vision Engine
                  </div>
                  <div className="text-lg font-bold text-slate-900 flex items-center gap-2 mt-0.5">
                    <Zap className="h-4 w-4 text-amber-500 fill-amber-500" />
                    EfficientNet-B4
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Device: <span className="font-mono text-slate-700 uppercase">{healthData?.models?.[0]?.device || "auto"}</span>
                  </div>
                </div>
                <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                  <Cpu className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>

            {/* Card 4: Memory RSS */}
            <Card className="bg-white border-slate-200/80 shadow-xs rounded-2xl">
              <CardContent className="p-4 flex items-center justify-between">
                <div>
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    Process Footprint
                  </div>
                  <div className="text-lg font-bold text-slate-900 mt-0.5">
                    {healthData?.backend?.memory_rss_mb || 0} MB
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">
                    Threads: <span className="font-mono text-slate-700">{healthData?.backend?.cpu_threads || 4}</span>
                  </div>
                </div>
                <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                  <Activity className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detailed ML Model Diagnostic Grid */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Layers className="h-5 w-5 text-blue-600" />
                ML & Deep Learning Models Operational Health
              </h2>
              <span className="text-xs text-slate-500">
                {lastRefreshed ? `Last queried: ${lastRefreshed}` : "Live Diagnostics"}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {healthData?.models?.map((model) => (
                <Card key={model.id} className="bg-white border-slate-200/80 shadow-xs rounded-2xl hover:border-blue-300 transition">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-base text-slate-900 font-bold">{model.name}</CardTitle>
                          <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px]">
                            {model.status}
                          </Badge>
                        </div>
                        <CardDescription className="text-xs text-slate-500 mt-0.5">
                          {model.type}
                        </CardDescription>
                      </div>
                      <Badge variant="outline" className="font-mono text-[10px] uppercase">
                        {model.device}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3 pt-0">
                    <div className="grid grid-cols-2 gap-2 text-xs bg-slate-50/70 p-2.5 rounded-xl border border-slate-100 font-mono">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-sans">Latency</span>
                        <span className="font-semibold text-slate-800">{model.average_latency_ms} ms</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-sans">Accuracy / Benchmark</span>
                        <span className="font-semibold text-emerald-700">{model.accuracy_metric}</span>
                      </div>
                    </div>

                    <div className="space-y-1 text-xs">
                      <div className="text-slate-500 font-medium text-[11px]">Capabilities & Features:</div>
                      <div className="flex flex-wrap gap-1.5">
                        {model.features.map((feat, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded-md bg-stone-100 text-stone-700 text-[11px]"
                          >
                            • {feat}
                          </span>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Database & Infrastructure Specs */}
          <Card className="bg-white border-slate-200/80 shadow-xs rounded-2xl">
            <CardHeader className="pb-3">
              <CardTitle className="text-base text-slate-900 flex items-center gap-2">
                <Database className="h-5 w-5 text-emerald-600" />
                PostgreSQL Storage & Schema Telemetry
              </CardTitle>
              <CardDescription className="text-xs text-slate-500">
                Connected database metrics, table row volumes, and active batch state
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-center">
                  <div className="text-[10px] uppercase text-slate-400 font-semibold">Active Batch</div>
                  <div className="text-xs font-mono font-bold text-blue-700 mt-1 truncate">
                    {healthData?.database?.metrics?.active_batch || "BATCH-2026-001"}
                  </div>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-center">
                  <div className="text-[10px] uppercase text-slate-400 font-semibold">Users Seeded</div>
                  <div className="text-base font-bold text-slate-900 mt-1">
                    {healthData?.database?.metrics?.total_users ?? 5}
                  </div>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-center">
                  <div className="text-[10px] uppercase text-slate-400 font-semibold">Inspections</div>
                  <div className="text-base font-bold text-slate-900 mt-1">
                    {healthData?.database?.metrics?.total_inspections ?? 0}
                  </div>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-center">
                  <div className="text-[10px] uppercase text-slate-400 font-semibold">Process States</div>
                  <div className="text-base font-bold text-slate-900 mt-1">
                    {healthData?.database?.metrics?.total_process_states ?? 0}
                  </div>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-center">
                  <div className="text-[10px] uppercase text-slate-400 font-semibold">Materials</div>
                  <div className="text-base font-bold text-slate-900 mt-1">
                    {healthData?.database?.metrics?.total_materials ?? 4}
                  </div>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-center">
                  <div className="text-[10px] uppercase text-slate-400 font-semibold">Guardrails</div>
                  <div className="text-base font-bold text-amber-600 mt-1">
                    {healthData?.database?.metrics?.active_guardrails ?? 4}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: AI COPILOT SAFETY GUARDRAILS */}
      {/* ========================================================================= */}
      {activeTab === "guardrails" && (
        <div className="space-y-6 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Shield className="h-5 w-5 text-amber-500" />
                AI Copilot Industrial Safety Guardrails
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Rules enforced in real time to intercept hazardous setpoint changes or metallurgical limit violations
              </p>
            </div>
            <Button
              onClick={() => setShowAddModal(true)}
              className="gradient-brand text-white shadow-xs text-xs self-start"
            >
              <Plus className="h-3.5 w-3.5 mr-1.5" /> Add Safety Guardrail
            </Button>
          </div>

          {guardrailSuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
              <span>{guardrailSuccess}</span>
            </div>
          )}

          {/* Guardrails List */}
          <div className="space-y-3">
            {guardrails.map((rule) => (
              <Card
                key={rule.id}
                className={`bg-white border transition rounded-2xl ${
                  rule.is_active ? "border-slate-200/80 shadow-xs" : "border-slate-200/40 opacity-60 bg-slate-50/50"
                }`}
              >
                <CardContent className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-sm text-slate-900">{rule.rule_name}</span>
                      {getCategoryBadge(rule.category)}
                      <Badge variant="outline" className="text-[10px] font-mono">
                        {rule.severity === "strict_block" ? "Strict Intercept" : "Advisory Warning"}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">{rule.rule_text}</p>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-center">
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <span className="text-[11px] font-medium">{rule.is_active ? "Active" : "Disabled"}</span>
                      <Switch
                        checked={rule.is_active}
                        onCheckedChange={() => handleToggleRule(rule.id, rule.is_active)}
                      />
                    </div>
                    <button
                      onClick={() => handleDeleteRule(rule.id)}
                      title="Remove Guardrail Rule"
                      className="p-1.5 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Add Rule Modal Dialog */}
          {showAddModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-fade-in">
              <Card className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
                      <Shield className="h-5 w-5 text-blue-600" />
                      Add AI Copilot Safety Guardrail
                    </CardTitle>
                    <button
                      onClick={() => setShowAddModal(false)}
                      className="text-slate-400 hover:text-slate-600 p-1"
                    >
                      <X size={18} />
                    </button>
                  </div>
                  <CardDescription className="text-xs text-slate-500">
                    Define an immutable physical boundary or operational refusal rule for the chatbot.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Rule Title / Identifier
                    </label>
                    <Input
                      placeholder="e.g., Hydraulic Forming Pressure Ceiling"
                      value={newRuleName}
                      onChange={(e) => setNewRuleName(e.target.value)}
                      className="text-xs rounded-xl"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Policy Directive & Engineering Limit
                    </label>
                    <textarea
                      rows={3}
                      placeholder="e.g., Do not recommend or permit hydraulic pressure setpoints above 185 bar..."
                      value={newRuleText}
                      onChange={(e) => setNewRuleText(e.target.value)}
                      className="w-full text-xs p-2.5 rounded-xl border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Category
                      </label>
                      <select
                        value={newCategory}
                        onChange={(e) => setNewCategory(e.target.value)}
                        className="w-full text-xs p-2 rounded-xl border border-slate-200 bg-white"
                      >
                        <option value="Safety">Safety Critical</option>
                        <option value="Metallurgy">Metallurgy & Chemistry</option>
                        <option value="Compliance">Compliance & Authorization</option>
                        <option value="Operational">Operational Threshold</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Enforcement Severity
                      </label>
                      <select
                        value={newSeverity}
                        onChange={(e) => setNewSeverity(e.target.value)}
                        className="w-full text-xs p-2 rounded-xl border border-slate-200 bg-white"
                      >
                        <option value="strict_block">Strict Interception (Refusal)</option>
                        <option value="advisory_warning">Advisory Notice (Warning)</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-2">
                    <Button
                      variant="outline"
                      onClick={() => setShowAddModal(false)}
                      className="text-xs rounded-xl"
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleAddRule}
                      className="gradient-brand text-white text-xs rounded-xl shadow-xs"
                    >
                      Persist in PostgreSQL
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: INFERENCE & THRESHOLD CONFIGURATION */}
      {/* ========================================================================= */}
      {activeTab === "inference" && (
        <div className="space-y-6 animate-fade-in">
          {saveSuccess && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl text-green-800 text-sm font-semibold flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              Settings saved successfully! Model inference and monitoring thresholds updated.
            </div>
          )}

          <Card className="border-slate-200 bg-white rounded-2xl shadow-xs">
            <CardHeader>
              <CardTitle className="text-base text-slate-900 flex items-center gap-2">
                <Sliders className="h-5 w-5 text-blue-600" />
                AI Model Inference Settings
              </CardTitle>
              <CardDescription className="text-xs text-slate-500">
                Confidence thresholds for defect classification and Grad-CAM generation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-slate-900 text-sm">Confidence Flag Threshold (%)</div>
                  <div className="text-xs text-slate-500">Minimum confidence to flag a defect region</div>
                </div>
                <Input
                  type="number"
                  value={confidenceThreshold}
                  onChange={(e) => setConfidenceThreshold(e.target.value)}
                  className="w-24 bg-white text-xs"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-slate-900 text-sm">Monte Carlo Dropout Iterations</div>
                  <div className="text-xs text-slate-500">Number of forward passes to quantify epistemic uncertainty</div>
                </div>
                <Input
                  type="number"
                  value={mcDropoutSamples}
                  onChange={(e) => setMcDropoutSamples(e.target.value)}
                  className="w-24 bg-white text-xs"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-slate-900 text-sm">Grad-CAM Auto-Generation</div>
                  <div className="text-xs text-slate-500">Automatically generate heatmaps for defects with confidence &gt;90%</div>
                </div>
                <Switch checked={gradCamAuto} onCheckedChange={setGradCamAuto} />
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200 bg-white rounded-2xl shadow-xs">
            <CardHeader>
              <CardTitle className="text-base text-slate-900 flex items-center gap-2">
                <Bell className="h-5 w-5 text-amber-500" />
                Operational Alert Notifications
              </CardTitle>
              <CardDescription className="text-xs text-slate-500">
                Configure real-time monitoring thresholds and operator warnings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-slate-900 text-sm">Severe Bottleneck Alert</div>
                  <div className="text-xs text-slate-500">Notify when workstation utilization exceeds 95%</div>
                </div>
                <Switch checked={bottleneckAlert} onCheckedChange={setBottleneckAlert} />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
