"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAppStore } from "@/lib/store";
import { ShieldAlert, Loader2 } from "lucide-react";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { currentUser, isAuthReady, initializeAuth } = useAppStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    initializeAuth();
  }, [initializeAuth]);

  useEffect(() => {
    if (!mounted || !isAuthReady) return;

    if (!currentUser) {
      const redirectParam = pathname ? `?redirect=${encodeURIComponent(pathname)}` : "";
      router.replace(`/login${redirectParam}`);
    }
  }, [mounted, isAuthReady, currentUser, router, pathname]);

  // While initializing or if unauthenticated, show protected gateway screen
  if (!mounted || !isAuthReady || !currentUser) {
    return (
      <div className="min-h-screen bg-[#F8F6F3] flex flex-col items-center justify-center p-6">
        <div className="bg-white p-8 rounded-2xl shadow-xl border border-stone-200/80 max-w-sm w-full text-center space-y-4 animate-fade-in">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 text-white flex items-center justify-center mx-auto shadow-md">
            <Loader2 className="h-7 w-7 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Verifying Plant Authorization</h3>
            <p className="text-xs text-slate-500 mt-1">
              Validating operator credentials and PostgreSQL security session...
            </p>
          </div>
          <div className="pt-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-50 border border-amber-200 text-amber-800 text-[11px] font-medium rounded-full">
              <ShieldAlert className="h-3.5 w-3.5 shrink-0" />
              Restricted Industrial Network
            </span>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
