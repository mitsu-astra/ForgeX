"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Factory,
  Home,
  Upload,
  Camera,
  Activity,
  BarChart3,
  Sliders,
  Bot,
  Settings,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Overview", href: "/dashboard", icon: Home },
  { name: "Upload Data Streams", href: "/dashboard/upload", icon: Upload },
  { name: "Visual Quality Inspection", href: "/dashboard/quality", icon: Camera },
  { name: "Process Telemetry & Flow", href: "/dashboard/process", icon: Activity },
  { name: "Root Cause & SHAP Analysis", href: "/dashboard/analysis", icon: BarChart3 },
  { name: "What-If Metallurgy Simulator", href: "/dashboard/simulator", icon: Sliders },
  { name: "AI Factory Copilot", href: "/dashboard/copilot", icon: Bot },
  { name: "Analysis Reports", href: "/dashboard/reports", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[82px] shrink-0 rounded-[28px] bg-[#EFE9E3] flex flex-col items-center py-6 shadow-sm border border-stone-200/50 select-none">
      {/* Factory Logo */}
      <Link
        href="/dashboard"
        title="ForgeX • Industrial Decision Intelligence"
        className="w-11 h-11 rounded-2xl bg-black text-white flex items-center justify-center mb-6 shadow-sm hover:scale-105 transition-transform"
      >
        <Factory size={21} />
      </Link>

      {/* Navigation Icons */}
      <nav className="flex flex-col gap-3">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              title={item.name}
              className={cn(
                "w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-200 relative group",
                isActive
                  ? "bg-black text-white shadow-sm"
                  : "text-black/60 hover:text-black hover:bg-white"
              )}
            >
              <Icon size={20} />
              {/* Tooltip Label on Hover */}
              <div className="absolute left-[64px] px-3 py-1.5 bg-[#181818] text-white text-xs font-medium rounded-xl whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-md">
                {item.name}
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Bottom Profile / Settings */}
      <div className="mt-auto flex flex-col items-center gap-4">
        <Link
          href="/dashboard/settings"
          title="Settings"
          className={cn(
            "w-12 h-12 rounded-2xl flex items-center justify-center transition-all relative group",
            pathname === "/dashboard/settings"
              ? "bg-black text-white shadow-sm"
              : "text-black/60 hover:text-black hover:bg-white"
          )}
        >
          <Settings size={20} />
          <div className="absolute left-[64px] px-3 py-1.5 bg-[#181818] text-white text-xs font-medium rounded-xl whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 shadow-md">
            Settings
          </div>
        </Link>

        <div
          title="Authorized Operator"
          className="w-11 h-11 rounded-full bg-[#D6B6C8] text-[#181818] flex items-center justify-center font-semibold text-sm shadow-sm"
        >
          A
        </div>
      </div>
    </aside>
  );
}
