"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listReports, generateReport, downloadReportPdf, ReportMeta } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  FileText, Download, Eye, RefreshCw, Clock, CheckCircle2,
  XCircle, Loader2, AlertCircle, Database, BarChart3,
} from "lucide-react";

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  COMPLETED: { label: "Completed", color: "bg-emerald-100 text-emerald-700 border-emerald-200", icon: <CheckCircle2 className="h-3 w-3" /> },
  PARTIAL:   { label: "Partial",   color: "bg-amber-100 text-amber-700 border-amber-200",    icon: <AlertCircle className="h-3 w-3" /> },
  GENERATING:{ label: "Generating",color: "bg-blue-100 text-blue-700 border-blue-200",      icon: <Loader2 className="h-3 w-3 animate-spin" /> },
  PENDING:   { label: "Pending",   color: "bg-slate-100 text-slate-600 border-slate-200",    icon: <Clock className="h-3 w-3" /> },
  FAILED:    { label: "Failed",    color: "bg-red-100 text-red-700 border-red-200",          icon: <XCircle className="h-3 w-3" /> },
};

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG["PENDING"];
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${cfg.color}`}>
      {cfg.icon}{cfg.label}
    </span>
  );
}

export default function ReportsPage() {
  const router = useRouter();
  const [reports, setReports] = useState<ReportMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await listReports();
      if (res.success) {
        setReports(res.data?.reports ?? []);
      } else {
        setError(res.message || "Failed to load reports.");
      }
    } catch {
      setError("Could not connect to the backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReports(); }, []);

  // Auto-refresh if any report is still generating
  useEffect(() => {
    const generating = reports.some(r => r.status === "GENERATING" || r.status === "PENDING");
    if (!generating) return;
    const t = setTimeout(fetchReports, 4000);
    return () => clearTimeout(t);
  }, [reports]);

  const handleDownload = async (r: ReportMeta) => {
    setDownloading(r.report_id);
    try {
      await downloadReportPdf(r.report_id, r.batch_id);
    } catch (e: any) {
      alert(`Download failed: ${e.message}`);
    } finally {
      setDownloading(null);
    }
  };

  const fmtDate = (s: string | null) => {
    if (!s) return "—";
    return new Date(s).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
  };

  return (
    <div className="flex flex-col gap-8 p-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-blue-600" />
            Analysis Report History
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Every analysis run generates a persistent industrial report — stored in the database, available for review and PDF download at any time.
          </p>
        </div>
        <Button variant="outline" onClick={fetchReports} disabled={loading} className="gap-2">
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          <XCircle className="h-5 w-5 shrink-0" />
          {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && reports.length === 0 && !error && (
        <Card className="border-dashed border-slate-300">
          <CardContent className="flex flex-col items-center gap-4 py-16 text-center">
            <Database className="h-12 w-12 text-slate-300" />
            <div>
              <p className="text-slate-600 font-medium">No reports yet</p>
              <p className="text-slate-400 text-sm mt-1">
                Upload data and run the analysis pipeline — a report will be generated automatically.
              </p>
            </div>
            <Button onClick={() => router.push("/dashboard/upload")} className="gradient-brand text-white">
              Go to Upload
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-20 rounded-xl bg-slate-100 animate-pulse" />
          ))}
        </div>
      )}

      {/* Reports table */}
      {!loading && reports.length > 0 && (
        <Card className="border-slate-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">
              {reports.length} Report{reports.length !== 1 ? "s" : ""}
            </CardTitle>
            <CardDescription>
              Reports are persisted in the database and survive application restarts.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Report ID</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Batch ID</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Generated</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Completed</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">PDF</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map((r, idx) => (
                    <tr
                      key={r.report_id}
                      className={`border-b border-slate-50 hover:bg-slate-50 transition-colors ${idx % 2 === 0 ? "" : "bg-slate-50/30"}`}
                    >
                      <td className="px-4 py-3">
                        <span className="font-mono text-xs text-slate-700">{r.report_id}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-mono text-xs text-slate-600">{r.batch_id}</span>
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={r.status} />
                      </td>
                      <td className="px-4 py-3 text-slate-600 text-xs">{fmtDate(r.created_at)}</td>
                      <td className="px-4 py-3 text-slate-600 text-xs">{fmtDate(r.completed_at)}</td>
                      <td className="px-4 py-3">
                        {r.has_pdf ? (
                          <span className="inline-flex items-center gap-1 text-xs text-emerald-600 font-medium">
                            <CheckCircle2 className="h-3 w-3" /> Available
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => router.push(`/dashboard/reports/${r.report_id}`)}
                            className="gap-1 text-xs"
                            disabled={r.status !== "COMPLETED" && r.status !== "PARTIAL"}
                          >
                            <Eye className="h-3 w-3" />
                            View
                          </Button>
                          {r.has_pdf && (
                            <Button
                              size="sm"
                              className="gap-1 text-xs gradient-brand text-white"
                              onClick={() => handleDownload(r)}
                              disabled={downloading === r.report_id}
                            >
                              {downloading === r.report_id ? (
                                <Loader2 className="h-3 w-3 animate-spin" />
                              ) : (
                                <Download className="h-3 w-3" />
                              )}
                              PDF
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Note */}
      <p className="text-xs text-slate-400 text-center">
        Reports are linked to analysis runs. Navigate to{" "}
        <span className="text-blue-500 cursor-pointer" onClick={() => router.push("/dashboard/upload")}>Upload</span>
        {" "}to run a new analysis and generate a new report.
      </p>
    </div>
  );
}
