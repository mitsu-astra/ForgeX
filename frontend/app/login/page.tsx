"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  KeyRound,
  Mail,
  ArrowRight,
  Factory,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Lock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { loginUser } from "@/lib/api";
import { useAppStore } from "@/lib/store";

export default function LoginPage() {
  const router = useRouter();
  const { currentUser, authToken, isAuthReady, initializeAuth, setCurrentUser } = useAppStore();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  useEffect(() => {
    if (isAuthReady && currentUser && authToken) {
      router.replace("/dashboard");
    }
  }, [isAuthReady, currentUser, authToken, router]);

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!email.trim() || !password.trim()) {
      setErrorMsg("Please enter both email and password.");
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const res = await loginUser(email.trim(), password.trim());
      if (res.success && res.data) {
        setCurrentUser(res.data.user, res.data.token);
        setSuccessMsg(`Welcome, ${res.data.user.full_name} (${res.data.user.role})`);

        const redirectParam = typeof window !== "undefined"
          ? new URLSearchParams(window.location.search).get("redirect") || "/dashboard"
          : "/dashboard";

        setTimeout(() => {
          router.push(redirectParam);
        }, 400);
      } else {
        setErrorMsg(res.message || "Invalid credentials. Please verify your email and password.");
      }
    } catch {
      setErrorMsg("Unable to connect to PostgreSQL backend service. Please check API status.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F6F3] flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8 selection:bg-stone-200">
      {/* Top Brand Header matching Dashboard typography */}
      <div className="text-center max-w-md mx-auto mb-8">
        <div className="w-12 h-12 rounded-full bg-white border border-stone-200/80 shadow-xs flex items-center justify-center text-[#181818] mx-auto mb-4 hover:scale-105 transition-transform">
          <Factory size={22} />
        </div>
        <p className="text-xs font-medium text-stone-500 uppercase tracking-wider mb-1">
          ForgeX &bull; Industrial Decision Intelligence
        </p>
        <h1 className="text-[38px] md:text-[44px] leading-[1.08] tracking-[-1.5px] font-medium text-[#181818]">
          Operator
          <br />
          Authentication
        </h1>
        <p className="text-xs md:text-sm text-stone-500 mt-2 max-w-xs mx-auto leading-relaxed">
          Enter registered credentials to access ForgeX line telemetry and decision engines.
        </p>
      </div>

      {/* Main Login Card matching Dashboard rounded-[28px] style */}
      <div className="w-full max-w-md">
        <div className="bg-white border border-stone-200/80 rounded-[28px] p-6 sm:p-8 shadow-xs relative overflow-hidden">
          {/* Card Top Row Header */}
          <div className="flex items-center justify-between pb-5 mb-6 border-b border-stone-100">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 bg-stone-100 rounded-full flex items-center justify-center text-[#181818] shadow-xs">
                <Lock size={16} />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-[#181818] tracking-tight">
                  Secure Sign In
                </h2>
                <p className="text-[11px] text-stone-400">PostgreSQL Session Gateway</p>
              </div>
            </div>
            <span className="bg-stone-100 border border-stone-200/70 rounded-full px-3 py-1 text-[11px] font-medium text-[#181818] shadow-xs">
              System Active
            </span>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {errorMsg && (
              <div className="p-3 bg-red-50/90 border border-red-200 text-red-700 text-xs rounded-2xl flex items-center gap-2.5 animate-fade-in">
                <AlertCircle className="h-4 w-4 shrink-0 text-red-600" />
                <span>{errorMsg}</span>
              </div>
            )}

            {successMsg && (
              <div className="p-3 bg-emerald-50/90 border border-emerald-200 text-emerald-800 text-xs rounded-2xl flex items-center gap-2.5 animate-fade-in">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
                <span>{successMsg}</span>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-stone-600 uppercase tracking-wider mb-1.5">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-stone-400" />
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="operator@industrial.ai"
                    className="pl-10 h-11 rounded-xl bg-white border border-stone-200/80 text-xs text-[#181818] placeholder:text-stone-400 shadow-xs focus-visible:ring-1 focus-visible:ring-stone-400"
                    autoComplete="email"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-stone-600 uppercase tracking-wider mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <KeyRound className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-stone-400" />
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="pl-10 h-11 rounded-xl bg-white border border-stone-200/80 text-xs text-[#181818] placeholder:text-stone-400 shadow-xs focus-visible:ring-1 focus-visible:ring-stone-400"
                    autoComplete="current-password"
                    required
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading || !email.trim() || !password.trim()}
                className="w-full h-11 rounded-full bg-black hover:bg-stone-900 text-white text-xs font-medium shadow-xs hover:scale-[1.005] transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 mt-2"
              >
                <span>{loading ? "Verifying Credentials..." : "Authenticate Session"}</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>

            <div className="pt-4 text-center border-t border-stone-100 flex items-center justify-between text-xs">
              <span className="text-[11px] text-stone-400 inline-flex items-center gap-1">
                <ShieldCheck size={13} className="text-stone-500" />
                PBKDF2 Encrypted
              </span>
              <Link
                href="/dashboard"
                className="text-stone-500 hover:text-black font-medium transition inline-flex items-center gap-1"
              >
                Return to Dashboard &rarr;
              </Link>
            </div>
          </form>
        </div>

        {/* Bottom System Note */}
        <p className="text-[11px] text-center text-stone-400 mt-6 tracking-wide">
          ForgeX &bull; Industrial Decision Intelligence Operating System
        </p>
      </div>
    </div>
  );
}
