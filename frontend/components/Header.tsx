"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Bell,
  Search,
  Settings,
  ChevronDown,
  LogOut,
  UserCheck,
  Shield,
  Activity,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { useAppStore } from "@/lib/store";
import { getDemoUsers, DemoUser } from "@/lib/api";

export function Header() {
  const router = useRouter();
  const { currentUser, setCurrentUser, logout } = useAppStore();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [demoUsers, setDemoUsers] = useState<DemoUser[]>([]);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getDemoUsers().then((res) => {
      if (res.success && res.data?.users) {
        setDemoUsers(res.data.users);
      }
    }).catch(() => {});

    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSwitchUser = (user: DemoUser) => {
    setCurrentUser(
      {
        id: user.id,
        email: user.email,
        full_name: user.full_name,
        role: user.role,
        avatar_initials: user.avatar_initials,
      },
      "demo_token"
    );
    setDropdownOpen(false);
  };

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
    router.push("/login");
  };

  return (
    <header className="h-16 bg-[#F8F6F3]/90 backdrop-blur-md flex items-center justify-between px-2 mb-2 sticky top-0 z-40 border-b border-stone-200/40">
      {/* Search Bar */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-stone-400" />
          <Input
            type="text"
            placeholder="Search ForgeX batches, defect modes, telemetry..."
            className="pl-10 h-10 rounded-full bg-white border-stone-200/70 text-xs text-[#181818] placeholder:text-stone-400 focus-visible:ring-stone-400 shadow-xs"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3">
        <button
          title="Live Notifications"
          className="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-xs border border-stone-200/60 hover:bg-stone-50 transition relative text-[#181818]"
        >
          <Bell size={18} />
          <span className="absolute top-2 right-2 w-2 h-2 bg-[#F6BFC4] rounded-full ring-2 ring-white" />
        </button>

        <Link
          href="/dashboard/settings"
          title="System Settings & Diagnostics"
          className="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-xs border border-stone-200/60 hover:bg-stone-50 transition text-[#181818]"
        >
          <Settings size={18} />
        </Link>

        {/* User Pill & Interactive Dropdown */}
        <div className="relative pl-2" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2.5 p-1 rounded-full hover:bg-stone-100/70 transition cursor-pointer"
          >
            <div className="text-right hidden sm:block">
              <div className="text-xs font-semibold text-[#181818] leading-tight">
                {currentUser?.full_name || "Authorized Lead"}
              </div>
              <div className="text-[10px] text-stone-500 font-medium">
                {currentUser?.role || "Quality Engineer"}
              </div>
            </div>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center font-bold text-xs shadow-xs border border-white">
              {currentUser?.avatar_initials || "A"}
            </div>
            <ChevronDown size={14} className="text-stone-500 hidden sm:block" />
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-white rounded-2xl shadow-xl border border-stone-200/80 p-3 z-50 animate-fade-in text-xs">
              <div className="px-3 py-2 border-b border-stone-100 mb-2">
                <div className="font-semibold text-slate-900">{currentUser?.full_name || "Guest Operator"}</div>
                <div className="text-[11px] text-slate-500">{currentUser?.email || "Not signed in"}</div>
                <div className="inline-block mt-1 px-2 py-0.5 bg-blue-50 text-blue-700 font-medium rounded-md text-[10px]">
                  {currentUser?.role || "Authorized Access"}
                </div>
              </div>

              {/* Demo Persona Quick Switcher */}
              <div className="mb-2">
                <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Switch Demo Persona
                </div>
                <div className="space-y-1 mt-1 max-h-48 overflow-y-auto">
                  {demoUsers.map((u) => (
                    <button
                      key={u.id}
                      onClick={() => handleSwitchUser(u)}
                      className={`w-full text-left px-3 py-1.5 rounded-lg flex items-center justify-between transition ${
                        currentUser?.email === u.email
                          ? "bg-blue-50 text-blue-800 font-semibold"
                          : "hover:bg-slate-50 text-slate-700"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[10px] font-bold">
                          {u.avatar_initials}
                        </span>
                        <span>{u.full_name}</span>
                      </div>
                      <span className="text-[9px] text-slate-400">{u.role.split(" ")[0]}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="pt-2 border-t border-stone-100 space-y-1">
                <Link
                  href="/dashboard/settings"
                  onClick={() => setDropdownOpen(false)}
                  className="w-full px-3 py-2 rounded-lg flex items-center gap-2 text-slate-700 hover:bg-slate-50 transition"
                >
                  <Activity size={14} className="text-slate-500" />
                  <span>ML & System Diagnostics</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="w-full px-3 py-2 rounded-lg flex items-center gap-2 text-red-600 hover:bg-red-50 transition text-left"
                >
                  <LogOut size={14} />
                  <span>Sign Out to Login Page</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
