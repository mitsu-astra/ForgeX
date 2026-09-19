"use client";

import { useState, useEffect } from "react";
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Package,
  DollarSign,
  Activity,
  Eye,
  RefreshCw,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { getAnalyticsOverview } from "@/lib/api";

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
        // Fallback default
      });
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Page Header */}
      <div>
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Executive Overview</h1>
        <p className="text-slate-600">
          Real-time manufacturing decision intelligence across computer vision QA and discrete-event flow
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Overall Yield"
          value={overview?.kpis?.overall_yield_pct ? `${overview.kpis.overall_yield_pct}%` : "96.8%"}
          change="+1.2%"
          trend="up"
          icon={<CheckCircle2 className="h-5 w-5" />}
          iconColor="text-green-500"
          bgColor="bg-green-50"
        />
        <KPICard
          title="Line Throughput"
          value={overview?.kpis?.current_line_throughput_pph ? `${overview.kpis.current_line_throughput_pph}/hr` : "145.0/hr"}
          change="+5.2%"
          trend="up"
          icon={<Activity className="h-5 w-5" />}
          iconColor="text-blue-500"
          bgColor="bg-blue-50"
        />
        <KPICard
          title="Primary Bottleneck"
          value={overview?.kpis?.primary_bottleneck_station ? `${overview.kpis.primary_bottleneck_station} (${overview.kpis.bottleneck_utilization_pct}%)` : "Drilling (96%)"}
          change="Station Limit"
          trend="down"
          icon={<AlertTriangle className="h-5 w-5" />}
          iconColor="text-red-500"
          bgColor="bg-red-50"
        />
        <KPICard
          title="Est. Monthly Loss"
          value={overview?.kpis?.estimated_monthly_scrap_loss_usd ? `$${(overview.kpis.estimated_monthly_scrap_loss_usd / 1000).toFixed(1)}K` : "$13.5K"}
          change="-12.3%"
          trend="down"
          icon={<DollarSign className="h-5 w-5" />}
          iconColor="text-purple-500"
          bgColor="bg-purple-50"
        />
      </div>

      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Batches */}
        <Card className="lg:col-span-2 hover-lift border-slate-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-900">
              <Package className="h-5 w-5 text-blue-500" />
              Recent Production Batches
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <BatchItem
              batch="BATCH-2026-001"
              images={142}
              defects={18}
              status="completed"
              time="10 mins ago"
            />
            <BatchItem
              batch="BATCH-2026-002"
              images={95}
              defects={9}
              status="completed"
              time="1 hour ago"
            />
            <BatchItem
              batch="BATCH-2026-003"
              images={120}
              defects={14}
              status="processing"
              time="Just now"
            />
          </CardContent>
        </Card>

        {/* Active Bottlenecks */}
        <Card className="hover-lift border-slate-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-900">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Primary Bottlenecks
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <BottleneckItem
              station="Drilling Station"
              utilization={96}
              severity="high"
            />
            <BottleneckItem
              station="Quality Check"
              utilization={81}
              severity="medium"
            />
            <BottleneckItem
              station="Assembly Station"
              utilization={72}
              severity="low"
            />
          </CardContent>
        </Card>
      </div>

      {/* Defect Distribution */}
      <Card className="hover-lift border-slate-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-slate-900">
            <Eye className="h-5 w-5 text-purple-500" />
            Defect Distribution Across Classes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
            <DefectTypeCard type="Rust" count={45} total={410} color="from-orange-500 to-red-500" />
            <DefectTypeCard type="Crack" count={32} total={410} color="from-red-500 to-pink-500" />
            <DefectTypeCard type="Scratch" count={28} total={410} color="from-yellow-500 to-orange-500" />
            <DefectTypeCard type="Hole" count={18} total={410} color="from-purple-500 to-pink-500" />
            <DefectTypeCard type="Normal" count={287} total={410} color="from-green-500 to-emerald-500" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function KPICard({
  title,
  value,
  change,
  trend,
  icon,
  iconColor,
  bgColor,
}: {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down";
  icon: React.ReactNode;
  iconColor: string;
  bgColor: string;
}) {
  const isPositive =
    (trend === "down" && title.includes("Loss")) ||
    (trend === "down" && title.includes("Defect")) ||
    (trend === "up" && !title.includes("Defect") && !title.includes("Loss"));

  return (
    <Card className="hover-lift border-slate-200">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-slate-600 mb-1">{title}</p>
            <p className="text-3xl font-bold text-slate-900">{value}</p>
          </div>
          <div className={`p-3 rounded-xl ${bgColor}`}>
            <div className={iconColor}>{icon}</div>
          </div>
        </div>
        <div className="mt-4 flex items-center gap-2">
          {trend === "up" ? (
            <TrendingUp className={`h-4 w-4 ${isPositive ? "text-green-600" : "text-red-600"}`} />
          ) : (
            <TrendingDown className={`h-4 w-4 ${isPositive ? "text-green-600" : "text-red-600"}`} />
          )}
          <span className={`text-sm font-semibold ${isPositive ? "text-green-600" : "text-red-600"}`}>
            {change}
          </span>
          <span className="text-sm text-slate-500">vs nominal baseline</span>
        </div>
      </CardContent>
    </Card>
  );
}

function BatchItem({
  batch,
  images,
  defects,
  status,
  time,
}: {
  batch: string;
  images: number;
  defects: number;
  status: string;
  time: string;
}) {
  return (
    <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors border border-slate-100">
      <div className="flex-1">
        <div className="font-semibold text-slate-900 mb-1">{batch}</div>
        <div className="text-sm text-slate-500">
          {images} images • {defects} defects • {time}
        </div>
      </div>
      <Badge
        className={
          status === "completed"
            ? "bg-green-100 text-green-700 border-green-200"
            : "bg-blue-100 text-blue-700 border-blue-200"
        }
      >
        {status}
      </Badge>
    </div>
  );
}

function BottleneckItem({
  station,
  utilization,
  severity,
}: {
  station: string;
  utilization: number;
  severity: string;
}) {
  const severityConfig =
    {
      high: { color: "bg-red-500", badge: "bg-red-100 text-red-700 border-red-200" },
      medium: { color: "bg-yellow-500", badge: "bg-yellow-100 text-yellow-700 border-yellow-200" },
      low: { color: "bg-blue-500", badge: "bg-blue-100 text-blue-700 border-blue-200" },
    }[severity] || { color: "bg-slate-500", badge: "bg-slate-100 text-slate-700 border-slate-200" };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="font-medium text-slate-900">{station}</span>
        <Badge className={severityConfig.badge}>{severity.toUpperCase()}</Badge>
      </div>
      <div className="space-y-1">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600">Utilization</span>
          <span className="font-semibold text-slate-900">{utilization}%</span>
        </div>
        <Progress value={utilization} className="h-2" />
      </div>
    </div>
  );
}

function DefectTypeCard({
  type,
  count,
  total,
  color,
}: {
  type: string;
  count: number;
  total: number;
  color: string;
}) {
  const percentage = ((count / total) * 100).toFixed(1);

  return (
    <div className="text-center space-y-3">
      <div className={`w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br ${color} p-0.5 shadow-sm`}>
        <div className="w-full h-full rounded-2xl bg-white flex items-center justify-center">
          <span className={`text-2xl font-bold bg-gradient-to-br ${color} text-transparent bg-clip-text`}>
            {count}
          </span>
        </div>
      </div>
      <div>
        <div className="font-semibold text-slate-900">{type}</div>
        <div className="text-sm text-slate-500">{percentage}%</div>
      </div>
    </div>
  );
}
