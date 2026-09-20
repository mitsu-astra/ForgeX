"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Camera,
  Activity,
  Factory,
  BarChart3,
  AlertTriangle,
  Bot,
  Package,
  ChevronRight,
  Gauge,
  Sliders,
  Sparkles,
  ArrowUpRight,
  CheckCircle2,
  Upload,
} from "lucide-react";
import { getAnalyticsOverview } from "@/lib/api";
import { formatINR } from "@/lib/currency";

export default function DashboardPage() {
  const [overview, setOverview] = useState<any>(null);

  useEffect(() => {
    getAnalyticsOverview()
      .then((res) => {
        if (res.success && res.data) {
          setOverview(res.data);
        }
      })
      .catch(() => {
        // Fallback default state
      });
  }, []);

  const kpis = overview?.kpis;
  const hasInspectionData = (kpis?.total_inspected_today || 0) > 0;
  const hasProcessData = (kpis?.current_line_throughput_pph || 0) > 0;
  const hasAnyData = hasInspectionData || hasProcessData;

  const yieldPct = hasInspectionData ? `${kpis.overall_yield_pct}%` : "—";
  const throughput = hasProcessData ? `${kpis.current_line_throughput_pph}/hr` : "—";
  const monthlyLossUSD = kpis?.estimated_monthly_scrap_loss_usd || 0;
  const monthlyLossINR = monthlyLossUSD > 0 ? formatINR(monthlyLossUSD, { compact: true }) : "₹0";

  const cards = [
    {
      title: "Visual Inspection",
      category: "VISION AI",
      description: "Detect cracks, scratches, dents and surface defects.",
      value: yieldPct,
      label: hasInspectionData
        ? `${kpis.total_inspected_today} specimens evaluated`
        : "Awaiting image uploads",
      badge: hasInspectionData ? "Active" : "Awaiting Data",
      color: "bg-[#F6BFC4]",
      icon: Camera,
      href: "/dashboard/quality",
    },
    {
      title: "Process Analytics",
      category: "FLOW AI",
      description: "Analyze production flow, bottlenecks and cycle time.",
      value: throughput,
      label: hasProcessData
        ? "Line throughput capacity"
        : "Awaiting telemetry CSV",
      badge: hasProcessData ? "Active" : "Awaiting Data",
      color: "bg-[#C7E8DC]",
      icon: Activity,
      href: "/dashboard/process",
    },
    {
      title: "Root Cause Analysis",
      category: "RCA ENGINE",
      description: "Connect defects with machine and process parameters.",
      value: hasInspectionData ? `${kpis.defects_detected_today}` : "0",
      label: hasInspectionData
        ? `${kpis.defects_detected_today} active defect modes mapped`
        : "0 active defect drivers",
      badge: hasInspectionData ? "Active" : "Nominal",
      color: "bg-[#D7C8F5]",
      icon: Bot,
      href: "/dashboard/analysis",
    },
    {
      title: "Production Economics",
      category: "PROFIT AI",
      description: "Track scrap, rework, downtime and production cost.",
      value: monthlyLossINR,
      label: monthlyLossUSD > 0 ? "Monthly cost at risk" : "Zero financial loss recorded",
      badge: monthlyLossUSD > 0 ? "Active" : "Nominal",
      color: "bg-[#F8D8B5]",
      icon: BarChart3,
      href: "/dashboard/simulator",
    },
  ];

  return (
    <div className="w-full space-y-6">
      {/* MAIN CONTENT AREA */}
      <div className="w-full">
        {/* Header */}
        <header className="mb-6">
          <p className="text-xs font-medium text-stone-500 uppercase tracking-wider mb-1">
            Manufacturing Intelligence
          </p>
          <h1 className="text-[38px] md:text-[44px] leading-[1.08] tracking-[-1.5px] font-medium text-[#181818]">
            ForgeX
          </h1>
        </header>

        {/* Filter Pills */}
        <div className="flex gap-2.5 mb-8 overflow-x-auto pb-1 select-none">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-black text-white text-xs font-medium shadow-xs"
          >
            <Factory size={16} />
            Overview
          </Link>

          <Link
            href="/dashboard/quality"
            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-white text-xs font-medium text-[#181818] border border-stone-200/70 hover:bg-stone-50 transition shadow-xs"
          >
            <Camera size={16} />
            Visual Inspection
          </Link>

          <Link
            href="/dashboard/process"
            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-white text-xs font-medium text-[#181818] border border-stone-200/70 hover:bg-stone-50 transition shadow-xs"
          >
            <Activity size={16} />
            Process Flow
          </Link>

          <Link
            href="/dashboard/simulator"
            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-white text-xs font-medium text-[#181818] border border-stone-200/70 hover:bg-stone-50 transition shadow-xs"
          >
            <BarChart3 size={16} />
            Economics & Simulator
          </Link>

          <Link
            href="/dashboard/upload"
            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-white text-xs font-medium text-[#181818] border border-stone-200/70 hover:bg-stone-50 transition shadow-xs ml-auto"
          >
            <Package size={16} />
            Upload Batch
          </Link>
        </div>

        {/* Awaiting Data Onboarding Banner */}
        {!hasAnyData && (
          <div className="bg-white rounded-[24px] p-5 border border-stone-200/80 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-2xl bg-amber-50 border border-amber-200/70 flex items-center justify-center shrink-0">
                <Package size={20} className="text-amber-600" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-stone-900">Awaiting Production Batch & Telemetry</h3>
                <p className="text-xs text-stone-500 mt-0.5 max-w-2xl leading-relaxed">
                  You are currently in a fresh workspace with zero simulated or hardcoded data. Upload specimen images (PNG/JPG) or discrete-event CSV logs to trigger real-time AI computer vision, throughput tracking, and root-cause analysis.
                </p>
              </div>
            </div>
            <Link
              href="/dashboard/upload"
              className="px-4 py-2 rounded-full bg-black text-white text-xs font-medium hover:bg-stone-800 transition shrink-0 flex items-center gap-2 shadow-xs"
            >
              <Upload size={14} />
              Upload Batch Data
            </Link>
          </div>
        )}

        {/* SECTION TITLE */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-semibold tracking-wider text-stone-600 uppercase">
            AI DECISION ENGINES
          </h2>
          <Link
            href="/dashboard/copilot"
            className="text-xs text-stone-500 hover:text-black flex items-center gap-1 font-medium transition"
          >
            Ask AI Copilot
            <ChevronRight size={14} />
          </Link>
        </div>

        {/* AI CARDS GRID */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {cards.map((card) => {
            const Icon = card.icon;

            return (
              <Link
                key={card.title}
                href={card.href}
                className={`${card.color} min-h-[220px] rounded-[28px] p-6 relative overflow-hidden hover:scale-[1.015] transition-all duration-200 border border-black/5 shadow-xs group block`}
              >
                {/* Top Row */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/80 rounded-full flex items-center justify-center shadow-xs">
                      <Icon size={18} className="text-[#181818]" />
                    </div>
                    <span className="text-xs font-semibold tracking-wider text-[#181818]">
                      {card.category}
                    </span>
                  </div>

                  <div className="bg-white/80 rounded-full px-3 py-1 text-[11px] font-medium text-[#181818] shadow-xs">
                    {card.badge}
                  </div>
                </div>

                {/* Bottom Content */}
                <div className="mt-8">
                  <h3 className="text-[23px] font-medium tracking-tight mb-1.5 text-[#181818]">
                    {card.title}
                  </h3>

                  <p className="text-xs text-black/65 max-w-[320px] leading-relaxed">
                    {card.description}
                  </p>

                  <div className="flex items-end justify-between mt-6">
                    <div>
                      <div className="text-2xl font-bold tracking-tight text-[#181818]">
                        {card.value}
                      </div>
                      <div className="text-[11px] text-black/55 font-medium">
                        {card.label}
                      </div>
                    </div>

                    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-xs group-hover:bg-black group-hover:text-white transition-colors">
                      <ArrowUpRight size={18} />
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* RECENT ALERTS / PRODUCTION EVENTS */}
        <div className="mt-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xs font-semibold tracking-wider text-stone-600 uppercase">
              Recent Production Events & Diagnostics
            </h2>
            <span className="text-xs text-stone-500 font-medium">Live telemetry</span>
          </div>

          {overview?.recent_events && overview.recent_events.length > 0 ? (
            <div className="bg-white rounded-[28px] p-3 border border-stone-200/60 shadow-xs space-y-2">
              {overview.recent_events.map((ev: any) => (
                <div
                  key={ev.id}
                  className="flex items-center gap-4 p-3.5 rounded-2xl hover:bg-[#F8F6F3] transition-colors"
                >
                  <div
                    className={`w-11 h-11 rounded-full ${
                      ev.is_defect ? "bg-[#F6BFC4]" : "bg-[#C7E8DC]"
                    } flex items-center justify-center shrink-0`}
                  >
                    {ev.is_defect ? (
                      <AlertTriangle size={19} className="text-[#181818]" />
                    ) : (
                      <CheckCircle2 size={19} className="text-[#181818]" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm text-[#181818]">{ev.title}</div>
                    <div className="text-xs text-stone-500 mt-0.5">
                      {ev.station} · {ev.timestamp}
                    </div>
                  </div>
                  <span
                    className={`text-xs px-3 py-1.5 rounded-full font-medium text-[#181818] ${
                      ev.is_defect ? "bg-[#FBE7E8]" : "bg-[#E3F4ED]"
                    }`}
                  >
                    {ev.defect_class} ({ev.confidence_pct}%)
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-[28px] p-8 border border-stone-200/60 shadow-xs text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-stone-100 flex items-center justify-center mx-auto text-stone-400">
                <Activity size={22} />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-[#181818]">No Production Events Recorded Yet</h3>
                <p className="text-xs text-stone-500 mt-1 max-w-md mx-auto leading-relaxed">
                  Live inspection telemetry, automated defect alerts, and process diagnostic events will appear here once specimens or telemetry streams are evaluated.
                </p>
              </div>
              <Link
                href="/dashboard/upload"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-black text-white text-xs font-medium hover:bg-stone-800 transition mt-2 shadow-xs"
              >
                <Package size={14} />
                Upload Batch Data
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
