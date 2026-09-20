"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { getReport, downloadReportPdf, regenerateReportPdf, ReportMeta, ReportPayload } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Download, RefreshCw, ArrowLeft, ChevronDown, ChevronUp,
  CheckCircle2, XCircle, AlertCircle, Loader2, Clock,
  Eye, BarChart3, Cpu, TrendingDown, ShieldCheck, Lightbulb,
  Activity, Database, Layers, FileText, Zap, Target, DollarSign,
} from "lucide-react";

const NA = "Not available — required data was not provided.";

// ---------------------------------------------------------------------------
// Status badge
// ---------------------------------------------------------------------------
function StatusBadge({ status }: { status: string }) {
  const m: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
    COMPLETED:  { color: "bg-emerald-100 text-emerald-700 border-emerald-200", icon: <CheckCircle2 className="h-3 w-3" />, label: "Completed" },
    PARTIAL:    { color: "bg-amber-100 text-amber-700 border-amber-200",       icon: <AlertCircle className="h-3 w-3" />,  label: "Partial" },
    GENERATING: { color: "bg-blue-100 text-blue-700 border-blue-200",          icon: <Loader2 className="h-3 w-3 animate-spin" />, label: "Generating" },
    FAILED:     { color: "bg-red-100 text-red-700 border-red-200",             icon: <XCircle className="h-3 w-3" />,      label: "Failed" },
    PENDING:    { color: "bg-slate-100 text-slate-600 border-slate-200",       icon: <Clock className="h-3 w-3" />,        label: "Pending" },
  };
  const cfg = m[status] ?? m["PENDING"];
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${cfg.color}`}>
      {cfg.icon}{cfg.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Collapsible section
// ---------------------------------------------------------------------------
function Section({
  icon, title, children, defaultOpen = true, accent = "blue",
}: {
  icon: React.ReactNode; title: string; children: React.ReactNode;
  defaultOpen?: boolean; accent?: string;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const accents: Record<string, string> = {
    blue: "bg-blue-600", emerald: "bg-emerald-600", amber: "bg-amber-500",
    purple: "bg-purple-600", red: "bg-red-600", slate: "bg-slate-600",
    teal: "bg-teal-600", orange: "bg-orange-500",
  };
  return (
    <Card className="border-slate-200 hover-lift">
      <button
        className="w-full text-left"
        onClick={() => setOpen(o => !o)}
      >
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center justify-between">
            <span className="flex items-center gap-2">
              <span className={`${accents[accent] ?? accents.blue} text-white p-1.5 rounded-lg`}>{icon}</span>
              {title}
            </span>
            {open ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
          </CardTitle>
        </CardHeader>
      </button>
      {open && <CardContent className="pt-0">{children}</CardContent>}
    </Card>
  );
}

// ---------------------------------------------------------------------------
// KV Row
// ---------------------------------------------------------------------------
function KVRow({ label, value, mono = false, accent }: { label: string; value: any; mono?: boolean; accent?: string }) {
  const v = value === null || value === undefined ? NA : String(value);
  const isNA = v === NA || v === "Not calculated — insufficient data.";
  return (
    <div className={`flex items-start gap-3 py-2.5 border-b border-slate-50 last:border-0`}>
      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide min-w-[180px] pt-0.5">{label}</span>
      <span className={`text-sm flex-1 ${isNA ? "text-slate-400 italic" : (accent ?? "text-slate-800")} ${mono ? "font-mono text-xs" : ""}`}>
        {v}
      </span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// NA Section
// ---------------------------------------------------------------------------
function NotAvailable({ reason }: { reason?: string }) {
  return (
    <div className="flex items-center gap-3 p-4 bg-slate-50 border border-dashed border-slate-200 rounded-xl text-slate-500 text-sm italic">
      <AlertCircle className="h-4 w-4 shrink-0 text-slate-400" />
      {reason ?? NA}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Priority colour
// ---------------------------------------------------------------------------
function PriorityBadge({ p }: { p: string }) {
  const m: Record<string, string> = {
    HIGH: "bg-red-100 text-red-700 border-red-200",
    MEDIUM: "bg-amber-100 text-amber-700 border-amber-200",
    LOW: "bg-emerald-100 text-emerald-700 border-emerald-200",
    INFO: "bg-blue-100 text-blue-700 border-blue-200",
  };
  return (
    <span className={`inline-flex px-2 py-0.5 rounded text-xs font-bold border ${m[p] ?? m.INFO}`}>{p}</span>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function ReportViewPage() {
  const params = useParams();
  const router = useRouter();
  const reportId = params.reportId as string;

  const [meta, setMeta] = useState<ReportMeta | null>(null);
  const [payload, setPayload] = useState<ReportPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getReport(reportId);
      if (res.success && res.data) {
        setMeta(res.data.meta);
        setPayload(res.data.payload);
      } else {
        setError(res.message ?? "Failed to load report.");
      }
    } catch {
      setError("Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  }, [reportId]);

  useEffect(() => { fetchReport(); }, [fetchReport]);

  // Auto-refresh while generating
  useEffect(() => {
    if (!meta || (meta.status !== "GENERATING" && meta.status !== "PENDING")) return;
    const t = setTimeout(fetchReport, 4000);
    return () => clearTimeout(t);
  }, [meta, fetchReport]);

  const handleDownload = async () => {
    if (!meta) return;
    setDownloading(true);
    try {
      await downloadReportPdf(meta.report_id, meta.batch_id);
    } catch (e: any) {
      alert(`Download failed: ${e.message}`);
    } finally {
      setDownloading(false);
    }
  };

  const handleRegeneratePdf = async () => {
    if (!meta) return;
    setRegenerating(true);
    try {
      const res = await regenerateReportPdf(meta.report_id);
      if (res.success) {
        await fetchReport();
      } else {
        alert(res.message || "Failed to regenerate PDF.");
      }
    } catch (e: any) {
      alert(`PDF generation failed: ${e.message}`);
    } finally {
      setRegenerating(false);
    }
  };

  const fmtDate = (s: string | null | undefined) =>
    s ? new Date(s).toLocaleString("en-IN", { dateStyle: "long", timeStyle: "medium" }) : "—";

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="h-10 w-10 animate-spin text-blue-500" />
        <p className="text-slate-500">Loading report…</p>
      </div>
    );
  }

  if (error || !meta) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <XCircle className="h-10 w-10 text-red-400" />
        <p className="text-slate-700 font-medium">{error ?? "Report not found."}</p>
        <Button variant="outline" onClick={() => router.back()}>← Back to Reports</Button>
      </div>
    );
  }

  const inp = payload?.input_summary ?? {};
  const vis = payload?.vision_summary ?? {};
  const proc = payload?.process_summary ?? {};
  const econ = payload?.economic_summary ?? {};
  const rca = payload?.rca_summary ?? {};
  const sim = payload?.simulation_summary ?? {};
  const mat = payload?.material_summary ?? {};
  const recs = payload?.recommendations ?? [];

  // Still generating?
  if (meta.status === "GENERATING" || meta.status === "PENDING") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
        <div className="h-16 w-16 rounded-full bg-blue-50 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        </div>
        <div className="text-center">
          <p className="text-lg font-semibold text-slate-800">Generating Report…</p>
          <p className="text-slate-500 text-sm mt-1">Aggregating analysis data and building PDF. This page will refresh automatically.</p>
        </div>
        <StatusBadge status={meta.status} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6 max-w-6xl mx-auto">

      {/* ── Report Header ── */}
      <div className="flex flex-col gap-3">
        <Button variant="ghost" className="w-fit -ml-2 text-slate-500 gap-1 text-sm" onClick={() => router.push("/dashboard/reports")}>
          <ArrowLeft className="h-4 w-4" /> Back to Reports
        </Button>
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-bold text-slate-900">Industrial Analysis Report</h1>
              <StatusBadge status={meta.status} />
            </div>
            <p className="text-slate-500 text-sm mt-1.5">
              <span className="font-mono text-xs bg-slate-100 px-2 py-0.5 rounded">{meta.report_id}</span>
              {" "}·{" "}
              Batch: <span className="font-mono text-xs bg-slate-100 px-2 py-0.5 rounded">{meta.batch_id}</span>
              {" "}·{" "}
              Generated: {fmtDate(meta.created_at)}
            </p>
          </div>
          <div className="flex gap-2 flex-wrap items-center">
            <Button variant="outline" onClick={fetchReport} className="gap-2 text-sm">
              <RefreshCw className="h-4 w-4" /> Refresh
            </Button>
            {meta.status === "PARTIAL" && (
              <Button
                variant="outline"
                onClick={handleRegeneratePdf}
                disabled={regenerating}
                className="gap-2 text-sm border-blue-300 text-blue-700 hover:bg-blue-50"
              >
                {regenerating ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                {regenerating ? "Generating PDF…" : "Generate PDF"}
              </Button>
            )}
            <Button
              onClick={handleDownload}
              disabled={downloading}
              className="gap-2 text-sm gradient-brand text-white"
            >
              {downloading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
              {downloading ? "Downloading…" : "Download PDF"}
            </Button>
          </div>
        </div>
        {meta.status === "PARTIAL" && meta.error_message && (
          <div className="flex items-center justify-between gap-3 p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-700 text-sm">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span><b>Partial Report:</b> {meta.error_message}</span>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={handleRegeneratePdf}
              disabled={regenerating}
              className="text-xs border-amber-300 text-amber-800 hover:bg-amber-100 shrink-0"
            >
              {regenerating ? "Building PDF…" : "Build PDF Now"}
            </Button>
          </div>
        )}
        <div className="h-1 w-full rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-emerald-500 opacity-60" />
      </div>

      {/* ── SEC 1: Executive Summary ── */}
      <Section icon={<FileText className="h-4 w-4" />} title="1 · Executive Summary" accent="blue">
        <div className="grid md:grid-cols-2 gap-x-8">
          <div>
            <KVRow label="Analysis Run ID"    value={meta.batch_id} mono />
            <KVRow label="Report ID"          value={meta.report_id} mono />
            <KVRow label="Date / Time"        value={fmtDate(meta.created_at)} />
            <KVRow label="Input Files"        value={`${inp.total_files ?? 0} files — ${inp.images_count ?? 0} images, ${inp.csv_count ?? 0} CSV`} />
            <KVRow label="Active Material"    value={inp.active_material} />
            <KVRow label="Active Defect"      value={inp.active_defect} />
          </div>
          <div>
            <KVRow label="Overall Quality"    value={vis.available ? `${vis.defect_rate_pct}% defect rate (${vis.total_images} images)` : NA} />
            <KVRow label="Primary Bottleneck" value={proc.available ? proc.primary_bottleneck : NA} />
            <KVRow label="Root Cause"         value={rca.available ? rca.root_cause?.replace(/_/g, " ") : NA} accent={rca.available ? "text-red-700 font-semibold" : undefined} />
            <KVRow label="RCA Confidence"     value={rca.available ? `${rca.confidence_pct}%` : NA} />
            <KVRow label="Hourly Economic Impact" value={econ.available ? `USD ${Number(econ.hourly_throughput_loss_usd ?? 0).toLocaleString("en-US", { minimumFractionDigits: 2 })}` : NA} />
            <KVRow label="Monthly Economic Impact" value={econ.available ? `USD ${Number(econ.monthly_throughput_loss_usd ?? 0).toLocaleString()}` : NA} />
          </div>
        </div>
        <div className="mt-4 p-3 bg-blue-50 border border-blue-100 rounded-xl text-xs text-blue-700">
          ℹ Every value in this report is sourced from the application database. Sections marked "{NA}" indicate that required input data was not provided for that analysis type.
        </div>
      </Section>

      {/* ── SEC 2: Input Data ── */}
      <Section icon={<Database className="h-4 w-4" />} title="2 · Input Data & Data Quality" accent="slate" defaultOpen={false}>
        <KVRow label="Batch Name"    value={inp.batch_name} />
        <KVRow label="Total Files"   value={inp.total_files} />
        <KVRow label="Images"        value={inp.images_count} />
        <KVRow label="CSV Files"     value={inp.csv_count} />
        <KVRow label="ZIP Archives"  value={inp.zip_count} />
        {(inp.files ?? []).length > 0 && (
          <div className="mt-4">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Uploaded Files</p>
            <div className="overflow-x-auto rounded-xl border border-slate-100">
              <table className="w-full text-xs">
                <thead className="bg-slate-100">
                  <tr>
                    {["Filename", "Type", "Subtype", "Size (bytes)"].map(h => (
                      <th key={h} className="px-3 py-2 text-left font-semibold text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(inp.files ?? []).map((f: any, i: number) => (
                    <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}>
                      <td className="px-3 py-2 font-mono text-slate-700">{f.filename}</td>
                      <td className="px-3 py-2 text-slate-600">{f.type}</td>
                      <td className="px-3 py-2 text-slate-500">{f.subtype}</td>
                      <td className="px-3 py-2 text-slate-500">{f.size_bytes?.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Section>

      {/* ── SEC 3: Visual Inspection ── */}
      <Section icon={<Eye className="h-4 w-4" />} title="3 · Visual Inspection (AI Vision)" accent="purple" defaultOpen={vis.available}>
        {vis.available ? (
          <>
            <div className="grid md:grid-cols-3 gap-4 mb-6">
              {[
                { label: "Total Images", value: vis.total_images, color: "bg-blue-50 border-blue-200 text-blue-700" },
                { label: "Defect Rate", value: `${vis.defect_rate_pct}%`, color: vis.defect_rate_pct > 10 ? "bg-red-50 border-red-200 text-red-700" : "bg-emerald-50 border-emerald-200 text-emerald-700" },
                { label: "Pass Rate", value: `${vis.pass_rate_pct}%`, color: "bg-emerald-50 border-emerald-200 text-emerald-700" },
                { label: "Avg Confidence", value: `${(vis.avg_confidence * 100).toFixed(1)}%`, color: "bg-purple-50 border-purple-200 text-purple-700" },
                { label: "Uncertain Specimens", value: vis.uncertain_specimens, color: vis.uncertain_specimens > 0 ? "bg-amber-50 border-amber-200 text-amber-700" : "bg-slate-50 border-slate-200 text-slate-600" },
                { label: "Defects Detected", value: vis.defects_detected, color: "bg-orange-50 border-orange-200 text-orange-700" },
              ].map(k => (
                <div key={k.label} className={`p-3 rounded-xl border ${k.color}`}>
                  <p className="text-xs font-semibold uppercase tracking-wide opacity-70">{k.label}</p>
                  <p className="text-xl font-bold mt-0.5">{k.value}</p>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-500 mb-3">Model: <b>{vis.model}</b> · Source: {vis.data_source}</p>

            {/* Defect Distribution */}
            {vis.defect_distribution && Object.keys(vis.defect_distribution).length > 0 && (
              <div className="mb-4">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Defect Distribution</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(vis.defect_distribution as Record<string, number>)
                    .sort(([, a], [, b]) => b - a)
                    .map(([cls, cnt]) => (
                      <div key={cls} className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-sm">
                        <span className="font-semibold text-slate-800 uppercase">{cls}</span>
                        <span className="text-slate-500">·</span>
                        <span className="font-mono text-slate-700">{String(cnt)}</span>
                        <span className="text-slate-400 text-xs">({((cnt as number) / vis.total_images * 100).toFixed(1)}%)</span>
                      </div>
                    ))
                  }
                </div>
              </div>
            )}

            {/* Specimen table */}
            {(vis.records ?? []).length > 0 && (
              <details className="mt-2">
                <summary className="text-xs font-semibold text-blue-600 cursor-pointer hover:underline">
                  Show all {vis.records.length} inspection record(s)
                </summary>
                <div className="mt-3 overflow-x-auto rounded-xl border border-slate-100">
                  <table className="w-full text-xs">
                    <thead className="bg-slate-100">
                      <tr>
                        {["Filename", "Defect Class", "Confidence", "Uncertainty", "Area %", "Uncertain?", "Inference ms", "Source"].map(h => (
                          <th key={h} className="px-3 py-2 text-left font-semibold text-slate-600">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(vis.records as any[]).map((r: any, i: number) => (
                        <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}>
                          <td className="px-3 py-2 font-mono text-slate-700">{r.filename}</td>
                          <td className="px-3 py-2 font-semibold text-slate-800 uppercase">{r.defect_class}</td>
                          <td className="px-3 py-2">{(r.confidence * 100).toFixed(1)}%</td>
                          <td className="px-3 py-2">{r.uncertainty_score?.toFixed(4)}</td>
                          <td className="px-3 py-2">{r.defect_area_pct?.toFixed(2)}%</td>
                          <td className="px-3 py-2">{r.is_uncertain ? "⚠ Yes" : "No"}</td>
                          <td className="px-3 py-2">{r.inference_time_ms}</td>
                          <td className="px-3 py-2 font-mono text-xs text-slate-400">{r.source}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </details>
            )}
          </>
        ) : (
          <NotAvailable reason={vis.reason} />
        )}
      </Section>

      {/* ── SEC 4+5: Process Performance & Bottleneck ── */}
      <Section icon={<Activity className="h-4 w-4" />} title="4+5 · Process Performance & Bottleneck Analysis" accent="amber" defaultOpen={proc.available}>
        {proc.available ? (
          <>
            <div className="grid md:grid-cols-2 gap-x-8 mb-4">
              <div>
                <KVRow label="Primary Bottleneck"    value={proc.primary_bottleneck} accent="text-orange-700 font-bold" />
                <KVRow label="Max Station Utilization" value={`${proc.max_utilization_pct}%`} />
                <KVRow label="Line Efficiency"         value={`${proc.line_efficiency_pct}%`} />
              </div>
              <div>
                <KVRow label="Estimated Lead Time"  value={`${proc.estimated_lead_time_hrs} hrs`} />
                <KVRow label="Total WIP Units"       value={`${proc.total_wip_units} units`} />
                <KVRow label="Data Source"           value={proc.data_source} mono />
              </div>
            </div>
            {(proc.stations ?? []).length > 0 && (
              <div className="mt-2 overflow-x-auto rounded-xl border border-slate-100">
                <table className="w-full text-xs">
                  <thead className="bg-amber-50">
                    <tr>
                      {["Station", "Utilization %", "Queue Units", "Bottleneck", "Source"].map(h => (
                        <th key={h} className="px-3 py-2 text-left font-semibold text-amber-700">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(proc.stations as any[]).map((s: any, i: number) => (
                      <tr key={i} className={s.is_bottleneck ? "bg-orange-50 font-semibold" : (i % 2 === 0 ? "bg-white" : "bg-slate-50")}>
                        <td className="px-3 py-2 text-slate-800">{s.name} {s.is_bottleneck ? "★" : ""}</td>
                        <td className="px-3 py-2">{s.utilization_pct ?? "—"}%</td>
                        <td className="px-3 py-2">{s.queue_units ?? "—"}</td>
                        <td className="px-3 py-2">{s.is_bottleneck ? "YES — Primary Constraint" : "—"}</td>
                        <td className="px-3 py-2 font-mono text-xs text-slate-400">{s.source}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        ) : (
          <NotAvailable reason={proc.reason} />
        )}
      </Section>

      {/* ── SEC 8: Root Cause Analysis ── */}
      <Section icon={<Target className="h-4 w-4" />} title="8 · Root Cause Analysis (XGBoost + SHAP)" accent="purple" defaultOpen={rca.available}>
        {rca.available ? (
          <>
            <div className="grid md:grid-cols-2 gap-x-8 mb-4">
              <div>
                <KVRow label="Root Cause"         value={rca.root_cause?.replace(/_/g, " ")} accent="text-red-700 font-bold" />
                <KVRow label="Associated Defect"  value={rca.associated_defect} />
                <KVRow label="Model Confidence"   value={`${rca.confidence_pct}%`} />
                <KVRow label="Data Source"        value={rca.data_source} mono />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Recommendation</p>
                <p className="text-sm text-slate-700 leading-relaxed">{rca.recommendation ?? NA}</p>
              </div>
            </div>
            <div className="p-3 bg-purple-50 border border-purple-100 rounded-xl text-xs text-purple-700 mb-4">
              ⚠ {rca.note}
            </div>

            {/* SHAP Features */}
            {(rca.shap_features ?? []).length > 0 && (
              <>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">SHAP Feature Attributions</p>
                <div className="overflow-x-auto rounded-xl border border-slate-100 mb-4">
                  <table className="w-full text-xs">
                    <thead className="bg-purple-50">
                      <tr>
                        {["Rank", "Feature", "Value", "SHAP Attribution", "Direction", "Source"].map(h => (
                          <th key={h} className="px-3 py-2 text-left font-semibold text-purple-700">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(rca.shap_features as any[]).map((f: any, i: number) => (
                        <tr key={i} className={i === 0 ? "bg-purple-50 font-semibold" : (i % 2 === 0 ? "bg-white" : "bg-slate-50")}>
                          <td className="px-3 py-2 text-slate-500">#{i + 1}</td>
                          <td className="px-3 py-2 text-slate-800">{f.feature}</td>
                          <td className="px-3 py-2 font-mono">{f.feature_value}</td>
                          <td className="px-3 py-2 font-mono font-bold text-purple-700">{Number(f.shap_value ?? 0) >= 0 ? "+" : ""}{Number(f.shap_value ?? 0).toFixed(4)}</td>
                          <td className="px-3 py-2">{f.contribution}</td>
                          <td className="px-3 py-2 font-mono text-xs text-slate-400">{rca.data_source}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {/* Failure Mode Probabilities */}
            {rca.probabilities && Object.keys(rca.probabilities).length > 0 && (
              <>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Failure Mode Probabilities</p>
                <div className="space-y-2">
                  {Object.entries(rca.probabilities as Record<string, number>)
                    .sort(([, a], [, b]) => b - a)
                    .map(([mode, prob]) => (
                      <div key={mode} className="flex items-center gap-3">
                        <span className="text-xs text-slate-600 min-w-[260px] capitalize">{mode.replace(/_/g, " ")}</span>
                        <div className="flex-1 bg-slate-100 rounded-full h-2">
                          <div
                            className="h-2 rounded-full bg-gradient-to-r from-purple-500 to-blue-500"
                            style={{ width: `${Math.min(100, prob * 100).toFixed(1)}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono text-slate-700 min-w-[48px] text-right">{(prob * 100).toFixed(1)}%</span>
                      </div>
                    ))
                  }
                </div>
              </>
            )}
          </>
        ) : (
          <NotAvailable reason={rca.reason} />
        )}
      </Section>

      {/* ── SEC 10: Economic Impact ── */}
      <Section icon={<DollarSign className="h-4 w-4" />} title="10 · Economic Impact" accent="emerald" defaultOpen={econ.available}>
        {econ.available ? (
          <>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                <p className="text-xs font-semibold text-red-600 uppercase tracking-wide">Hourly Throughput Loss</p>
                <p className="text-2xl font-bold text-red-700 mt-1">
                  USD {Number(econ.hourly_throughput_loss_usd ?? 0).toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="p-4 bg-orange-50 border border-orange-200 rounded-xl">
                <p className="text-xs font-semibold text-orange-600 uppercase tracking-wide">Monthly Throughput Loss</p>
                <p className="text-2xl font-bold text-orange-700 mt-1">
                  USD {Number(econ.monthly_throughput_loss_usd ?? 0).toLocaleString()}
                </p>
              </div>
            </div>
            <KVRow label="Currency"    value={econ.currency ?? "USD"} />
            <KVRow label="Note"        value={econ.note} />
            <KVRow label="Data Source" value={econ.data_source} mono />
          </>
        ) : (
          <NotAvailable reason={econ.reason} />
        )}
      </Section>

      {/* ── SEC 11: What-If ── */}
      <Section icon={<TrendingDown className="h-4 w-4" />} title="11 · What-If / Scenario Analysis" accent="teal" defaultOpen={false}>
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-700 text-xs mb-4">
          ⚠ All results in this section are <b>SIMULATED / PREDICTED</b>. They do not represent actual production data.
        </div>
        {sim.available ? (
          <div className="space-y-4">
            {(sim.scenarios as any[]).map((sc: any, i: number) => (
              <div key={i} className="p-4 bg-teal-50 border border-teal-200 rounded-xl">
                <p className="text-sm font-bold text-teal-800 mb-3">Scenario #{sc.scenario_id} — {sc.material_code}</p>
                <div className="grid md:grid-cols-3 gap-x-8">
                  <KVRow label="Baseline Defect %"     value={`${sc.baseline_defect_pct}%`} />
                  <KVRow label="Simulated Defect %"    value={`${sc.simulated_defect_pct}%`} />
                  <KVRow label="Defect Reduction"      value={`${sc.defect_reduction_pct}%`} />
                  <KVRow label="Throughput Change"     value={`${sc.throughput_change_pct > 0 ? "+" : ""}${sc.throughput_change_pct}%`} />
                  <KVRow label="Monthly Savings (USD)" value={`USD ${Number(sc.monthly_savings_usd).toLocaleString()}`} />
                  <KVRow label="Risk Level"            value={sc.risk_level} />
                </div>
                <p className="text-xs text-teal-600 italic mt-2">{sc.label}</p>
              </div>
            ))}
          </div>
        ) : (
          <NotAvailable reason={sim.reason} />
        )}
      </Section>

      {/* ── SEC 12: Safety & Operating Limits ── */}
      <Section icon={<ShieldCheck className="h-4 w-4" />} title="12 · Safety & Operating Limits" accent="red" defaultOpen={mat.available}>
        {mat.available ? (
          <>
            <KVRow label="Material"                   value={mat.name} accent="text-slate-900 font-semibold" />
            <KVRow label="Critical Hydraulic Pressure" value={`${mat.critical_hydraulic_pressure_bar} bar (DO NOT EXCEED)`} accent="text-red-700 font-semibold" />
            <KVRow label="Optimal Coolant pH"          value={`${mat.optimal_coolant_ph_min} – ${mat.optimal_coolant_ph_max}`} />
            <KVRow label="Max Conveyor Speed"          value={`${mat.max_conveyor_speed_mps} m/s`} />
            <KVRow label="Yield Strength"              value={`${mat.yield_strength_mpa} MPa`} />
            <KVRow label="Tensile Strength"            value={`${mat.tensile_strength_mpa} MPa`} />
            <KVRow label="Governing Physics"           value={mat.governing_physics} />
            <KVRow label="Data Source"                 value={mat.data_source} mono />
          </>
        ) : (
          <NotAvailable reason={mat.reason} />
        )}
      </Section>

      {/* ── SEC 13: Recommendations ── */}
      <Section icon={<Lightbulb className="h-4 w-4" />} title="13 · Industrial Recommendations" accent="orange">
        {recs.length > 0 ? (
          <div className="space-y-4">
            {recs.map((rec: any, i: number) => (
              <div key={i} className="p-4 rounded-xl border border-slate-200 bg-slate-50">
                <div className="flex items-center gap-2 mb-3 flex-wrap">
                  <PriorityBadge p={rec.priority ?? "INFO"} />
                  <span className="text-sm font-semibold text-slate-800">{rec.category}</span>
                </div>
                <KVRow label="Problem"    value={rec.problem} />
                <KVRow label="Evidence"   value={rec.evidence} />
                <KVRow label="Action"     value={rec.action} accent="text-emerald-700 font-medium" />
                <KVRow label="Confidence" value={rec.confidence_level} />
                <KVRow label="Human Approval Required" value={rec.human_approval_required ? "YES — Do not implement autonomously" : "No"} />
                <KVRow label="Traceable Source" value={rec.source} mono />
              </div>
            ))}
          </div>
        ) : (
          <NotAvailable reason="No recommendations could be derived — insufficient analysis data." />
        )}
      </Section>

      {/* ── SEC 14: Automation Plan ── */}
      <Section icon={<Zap className="h-4 w-4" />} title="14 · Automation Plan" accent="slate" defaultOpen={false}>
        <div className="space-y-2 text-sm">
          {[
            { status: "✅", label: "File upload (PNG / CSV / ZIP)", impl: true },
            { status: "✅", label: "Data validation and ingestion", impl: true },
            { status: "✅", label: "Vision AI inspection (EfficientNet-B4 + Grad-CAM)", impl: true },
            { status: "✅", label: "Defect classification + confidence + uncertainty", impl: true },
            { status: "✅", label: "Process bottleneck detection (DES surrogate)", impl: true },
            { status: "✅", label: "CUSUM statistical process control", impl: true },
            { status: "✅", label: "Spearman rank correlation analysis", impl: true },
            { status: "✅", label: "Root cause analysis (XGBoost + SHAP)", impl: true },
            { status: "✅", label: "What-If simulation + economic impact", impl: true },
            { status: "✅", label: "AI Copilot advisory (LLM-powered)", impl: true },
            { status: "✅", label: "Automated report generation + PDF download", impl: true },
            { status: "🔲", label: "Real-time sensor ingestion (OPC-UA / MQTT) — PROPOSED", impl: false },
            { status: "🔲", label: "Closed-loop parameter adjustment — PROPOSED (requires safety review)", impl: false },
            { status: "🔲", label: "Multi-facility cross-benchmarking — PROPOSED", impl: false },
          ].map((step, i) => (
            <div key={i} className={`flex items-center gap-3 p-2.5 rounded-lg ${step.impl ? "bg-emerald-50" : "bg-slate-100"}`}>
              <span className="text-base">{step.status}</span>
              <span className={`text-sm ${step.impl ? "text-emerald-800" : "text-slate-500 italic"}`}>{step.label}</span>
            </div>
          ))}
        </div>
      </Section>

      {/* ── SEC 15: Traceability ── */}
      <Section icon={<Layers className="h-4 w-4" />} title="15 · Traceability" accent="slate" defaultOpen={false}>
        {[
          ["Inspection Records",   "InspectionRecord table (batch_id indexed)"],
          ["Process State",        "ProcessState table (batch_id indexed)"],
          ["Root Cause",           "RootCauseAttribution table (batch_id indexed)"],
          ["Economic Metrics",     "ProcessState.hourly_throughput_loss_usd / monthly_throughput_loss_usd"],
          ["Simulation Scenarios", "SimulationScenario table (batch_id indexed)"],
          ["Material Specs",       "Material table (code indexed)"],
          ["Uploaded Files",       "UploadedFile table (batch_id indexed)"],
          ["Report Payload",       `AnalysisReport.report_id = ${meta.report_id}`],
          ["PDF Source",           "Same AnalysisReport canonical payload — no re-calculation"],
        ].map(([k, v], i) => <KVRow key={i} label={k} value={v} mono />)}
      </Section>

      {/* ── SEC 16: Analytics Appendix ── */}
      <Section icon={<Cpu className="h-4 w-4" />} title="16 · Analytics Appendix (Full Payload)" accent="slate" defaultOpen={false}>
        <p className="text-xs text-slate-500 mb-3">
          The complete canonical JSON payload is reproduced below for full traceability. This is the exact same data used to generate the PDF.
        </p>
        <details>
          <summary className="text-xs font-semibold text-blue-600 cursor-pointer hover:underline">Show full canonical payload JSON</summary>
          <pre className="mt-3 p-4 bg-slate-900 text-green-400 text-xs rounded-xl overflow-x-auto max-h-[600px] overflow-y-auto">
            {JSON.stringify(payload, null, 2)}
          </pre>
        </details>
      </Section>

      {/* ── Footer ── */}
      <div className="text-center text-xs text-slate-400 pt-4 border-t border-slate-100">
        ForgeX Industrial Decision Intelligence · Report {meta.report_id} · Batch {meta.batch_id} ·{" "}
        All values sourced from the application database · Generated {fmtDate(meta.created_at)}
      </div>
    </div>
  );
}
