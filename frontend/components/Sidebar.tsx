"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Upload,
  Eye,
  Activity,
  GitBranch,
  Sliders,
  MessageSquare,
  Settings,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const navigation = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Upload", href: "/dashboard/upload", icon: Upload, badge: "New" },
  { name: "Quality", href: "/dashboard/quality", icon: Eye },
  { name: "Process", href: "/dashboard/process", icon: Activity },
  { name: "Analysis", href: "/dashboard/analysis", icon: GitBranch },
  { name: "Simulator", href: "/dashboard/simulator", icon: Sliders },
  { name: "AI Copilot", href: "/dashboard/copilot", icon: MessageSquare, badge: "Beta" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-72 bg-slate-950 border-r border-white/10 flex flex-col relative overflow-hidden">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-950/20 to-transparent pointer-events-none" />

      {/* Logo */}
      <div className="relative p-6 border-b border-white/10">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="absolute inset-0 bg-blue-500 rounded-xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity" />
            <div className="relative w-11 h-11 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
          </div>
          <div>
            <div className="font-bold text-white text-lg">IndustryAI</div>
            <div className="text-xs text-slate-400">Decision Intelligence</div>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="relative flex-1 p-4 space-y-1">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-4 mb-4">
          Navigation
        </div>
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center justify-between gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative",
                isActive
                  ? "bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white shadow-lg shadow-blue-500/10"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              )}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-500 rounded-r-full" />
              )}
              <div className="flex items-center gap-3">
                <item.icon className={cn(
                  "h-5 w-5 transition-transform group-hover:scale-110",
                  isActive && "text-blue-400"
                )} />
                <span className="font-medium">{item.name}</span>
              </div>
              {item.badge && (
                <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-xs px-2">
                  {item.badge}
                </Badge>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="relative p-4 border-t border-white/10">
        <Link
          href="/dashboard/settings"
          className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
        >
          <Settings className="h-5 w-5" />
          <span className="font-medium">Settings</span>
        </Link>

        {/* Status indicator */}
        <div className="mt-4 px-4 py-3 rounded-xl bg-green-500/10 border border-green-500/20">
          <div className="flex items-center gap-2 text-sm">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-green-400 font-medium">System Online</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
