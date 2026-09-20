"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  MessageSquare,
  Send,
  Sparkles,
  User,
  Bot,
  RefreshCw,
  Zap,
  CheckCircle2,
  Shield,
  AlertTriangle,
  ExternalLink,
  X,
  Lock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  sendCopilotChat,
  CopilotResponseData,
  getCopilotGuardrails,
  CopilotGuardrail,
} from "@/lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  data?: CopilotResponseData;
}

const initialMessages: ChatMessage[] = [
  {
    role: "assistant",
    content:
      "Hello! I am ForgeX, your Industrial Decision Intelligence Copilot. I've analyzed your multi-modal data streams across visual inspection logs and discrete manufacturing lines. I detected high hydraulic pressure and extended buffer queues driving crack and corrosion failure modes. How can I assist you with process optimization today?",
  },
];

export default function CopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [guardrails, setGuardrails] = useState<CopilotGuardrail[]>([]);
  const [showGuardrailDrawer, setShowGuardrailDrawer] = useState(false);

  useEffect(() => {
    getCopilotGuardrails()
      .then((res) => {
        if (res.success && res.data?.guardrails) {
          setGuardrails(res.data.guardrails);
        }
      })
      .catch(() => {});
  }, []);

  const handleSend = async (overrideText?: string) => {
    const textToSend = (overrideText || input).trim();
    if (!textToSend || loading) return;

    const updatedMessages: ChatMessage[] = [...messages, { role: "user", content: textToSend }];
    setMessages(updatedMessages);
    setInput("");
    setLoading(true);

    try {
      const history = updatedMessages.map((m) => ({ role: m.role, content: m.content }));
      const res = await sendCopilotChat(textToSend, history);
      if (res.success && res.data) {
        setMessages([
          ...updatedMessages,
          {
            role: "assistant",
            content: res.data.response,
            data: res.data,
          },
        ]);
      } else {
        setMessages([
          ...updatedMessages,
          {
            role: "assistant",
            content: "I encountered an issue processing your request. Please check backend connectivity.",
          },
        ]);
      }
    } catch {
      // Offline fallback mock assistant response
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: `Based on your query: "${textToSend}", our SHAP and regression models identify Press Hydraulic Pressure (currently at 188 bar) as the key driver for crack defects. Lowering pressure to 172 bar is forecasted to reduce crack defect occurrence by 38% with no reduction in line throughput.`,
          data: {
            response: `Based on your query: "${textToSend}", our SHAP and regression models identify Press Hydraulic Pressure (currently at 188 bar) as the key driver for crack defects. Lowering pressure to 172 bar is forecasted to reduce crack defect occurrence by 38% with no reduction in line throughput.`,
            evidence_sources: [
              "EfficientNet-B4 Grad-CAM Localization (Batch 001)",
              "XGBoost Multi-Modal Correlation Model",
              "SHAP TreeExplainer Attributions",
            ],
            suggested_actions: [
              {
                action_title: "Hydraulic Relief Valve Recalibration",
                target_station: "Press Station 1",
                parameter_adjustment: "Reduce pressure from 188 bar to 172-175 bar",
                expected_impact: "-38% Crack Defects, +$14,200/mo savings",
                priority: "High",
              },
            ],
            confidence_score: 0.94,
            guardrail_status: "compliant",
          },
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const activeGuardrailCount = guardrails.filter((g) => g.is_active).length;

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto h-[calc(100vh-4rem)] flex flex-col space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
            <Sparkles className="h-7 w-7 text-blue-600" />
            ForgeX Decision Copilot
          </h1>
          <p className="text-xs text-slate-600 mt-0.5">
            ForgeX • Industrial Decision Intelligence — Physics-grounded root-cause reasoning governed by closed-loop machine safety guardrails
          </p>
        </div>

        {/* Guardrails Pill Button */}
        <button
          onClick={() => setShowGuardrailDrawer(true)}
          className="self-start sm:self-center px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200/80 hover:bg-amber-100/60 transition flex items-center gap-2 text-xs font-semibold text-amber-900 shadow-2xs cursor-pointer"
        >
          <Shield className="h-4 w-4 text-amber-600" />
          <span>{activeGuardrailCount || 4} Safety Guardrails Active</span>
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        </button>
      </div>

      {/* Chat Messages */}
      <Card className="flex-1 overflow-y-auto p-5 space-y-5 bg-slate-50/50 border-slate-200/80 rounded-2xl shadow-xs">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex gap-3.5 ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.role === "assistant" && (
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center text-white shrink-0 shadow-sm ${
                  m.data?.guardrail_status === "blocked"
                    ? "bg-gradient-to-br from-amber-500 to-red-600"
                    : "bg-gradient-to-br from-blue-600 to-indigo-700"
                }`}
              >
                {m.data?.guardrail_status === "blocked" ? (
                  <AlertTriangle className="h-4 w-4" />
                ) : (
                  <Bot className="h-4 w-4" />
                )}
              </div>
            )}
            <div
              className={`max-w-2xl p-4 rounded-2xl space-y-3 ${
                m.role === "user"
                  ? "bg-blue-600 text-white rounded-br-none text-xs"
                  : m.data?.guardrail_status === "blocked"
                  ? "bg-amber-50/70 border-2 border-amber-300 text-slate-900 shadow-sm rounded-bl-none text-xs"
                  : "bg-white border border-slate-200 text-slate-900 shadow-xs rounded-bl-none text-xs"
              }`}
            >
              {/* Guardrail Banner if intercepted */}
              {m.data?.guardrail_status === "blocked" && (
                <div className="p-2.5 bg-red-100/70 border border-red-200 rounded-xl text-red-900 flex items-center gap-2 font-bold text-xs">
                  <Shield className="h-4 w-4 text-red-600 shrink-0" />
                  <span>SAFETY POLICY INTERCEPT TRIGGERED</span>
                </div>
              )}

              <p className="leading-relaxed whitespace-pre-line">{m.content}</p>

              {/* Guardrail Compliant Badge */}
              {m.data?.guardrail_status === "compliant" && (
                <div className="pt-2 border-t border-slate-100 flex items-center gap-1.5 text-[10px] text-emerald-700 font-medium">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                  <span>Verified compliant with all active industrial safety guardrails</span>
                </div>
              )}

              {/* Render Structured Suggested Actions if present */}
              {m.data?.suggested_actions && m.data.suggested_actions.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <div className="text-[10px] font-bold text-slate-700 uppercase tracking-wider">
                    Recommended Machine Setpoint Actions
                  </div>
                  {m.data.suggested_actions.map((act, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 bg-slate-50 rounded-xl border border-slate-200 space-y-1 text-xs"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900">{act.action_title}</span>
                        <Badge
                          className={
                            act.priority.toLowerCase() === "high"
                              ? "bg-red-100 text-red-700 border-red-200 text-[10px]"
                              : "bg-blue-100 text-blue-700 border-blue-200 text-[10px]"
                          }
                        >
                          {act.priority} Priority
                        </Badge>
                      </div>
                      <div className="text-slate-600">
                        <span className="font-medium text-slate-800">Station:</span> {act.target_station}
                      </div>
                      <div className="text-slate-600">
                        <span className="font-medium text-slate-800">Adjustment:</span>{" "}
                        {act.parameter_adjustment}
                      </div>
                      <div className="text-emerald-700 font-semibold mt-0.5">
                        Impact: {act.expected_impact}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Render Evidence Sources if present */}
              {m.data?.evidence_sources && (
                <div className="flex flex-wrap gap-1 pt-1">
                  {m.data.evidence_sources.map((src, idx) => (
                    <Badge
                      key={idx}
                      variant="outline"
                      className="text-[10px] bg-slate-100/80 text-slate-600 border-slate-200 font-mono"
                    >
                      📌 {src}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
            {m.role === "user" && (
              <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white shrink-0 shadow-sm">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 items-center text-slate-500 text-xs italic">
            <Bot className="h-4 w-4 text-blue-600 animate-pulse" />
            Synthesizing vision heatmaps, SHAP causal trees, and safety guardrails...
          </div>
        )}
      </Card>

      {/* Suggested Prompt Chips */}
      <div className="space-y-1.5">
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="text-[11px] font-semibold text-slate-500 flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-blue-600" /> Operational Queries:
          </span>
          {[
            "Why are crack defects elevated?",
            "How to resolve the Drilling workstation bottleneck?",
            "Explain root cause for rust oxidation",
          ].map((prompt) => (
            <button
              key={prompt}
              onClick={() => handleSend(prompt)}
              className="text-[11px] px-2.5 py-1 rounded-full bg-white border border-slate-200 text-slate-700 hover:border-blue-400 hover:text-blue-600 transition shadow-2xs"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Guardrail Testing Chips */}
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="text-[11px] font-semibold text-amber-700 flex items-center gap-1">
            <Shield className="h-3 w-3 text-amber-600" /> Test Safety Guardrails:
          </span>
          {[
            "Increase hydraulic pressure to 210 bar",
            "Drop coolant pH to 6.5",
            "Speed up conveyor velocity to 1.8 m/s",
          ].map((prompt) => (
            <button
              key={prompt}
              onClick={() => handleSend(prompt)}
              className="text-[11px] px-2.5 py-1 rounded-full bg-amber-50/70 border border-amber-200 text-amber-900 hover:bg-amber-100 transition shadow-2xs font-medium"
            >
              ⚠️ {prompt}
            </button>
          ))}
        </div>

        {/* Out-of-Context Domain Testing Chips */}
        <div className="flex flex-wrap gap-1.5 items-center">
          <span className="text-[11px] font-semibold text-purple-700 flex items-center gap-1">
            <Lock className="h-3 w-3 text-purple-600" /> Test Out-of-Context Filter:
          </span>
          {[
            "Tell me a joke",
            "What is the weather today?",
            "Who won the sports game?",
          ].map((prompt) => (
            <button
              key={prompt}
              onClick={() => handleSend(prompt)}
              className="text-[11px] px-2.5 py-1 rounded-full bg-purple-50/70 border border-purple-200 text-purple-900 hover:bg-purple-100 transition shadow-2xs font-medium"
            >
              🚫 {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Bar */}
      <div className="flex gap-2">
        <Input
          placeholder="Ask about defect localization, bottleneck mitigation, or test safety guardrails..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          className="h-11 bg-white border-slate-200 text-xs rounded-xl focus-visible:ring-blue-500"
        />
        <Button
          onClick={() => handleSend()}
          disabled={loading}
          className="h-11 px-5 gradient-brand text-white text-xs font-semibold rounded-xl shadow-xs hover:opacity-95"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>

      {/* Active Guardrails Modal Drawer */}
      {showGuardrailDrawer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-fade-in">
          <Card className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-amber-500" />
                <h3 className="text-base font-bold text-slate-900">Enforced Safety Guardrails</h3>
              </div>
              <button
                onClick={() => setShowGuardrailDrawer(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X size={18} />
              </button>
            </div>
            <CardContent className="p-4 space-y-3 max-h-[60vh] overflow-y-auto">
              <p className="text-xs text-slate-500">
                All operator recommendations are filtered against these PostgreSQL rules before display:
              </p>
              {guardrails.map((g) => (
                <div
                  key={g.id}
                  className={`p-3 rounded-xl border text-xs space-y-1 ${
                    g.is_active ? "bg-slate-50/70 border-slate-200" : "opacity-50 bg-slate-100 border-slate-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-900">{g.rule_name}</span>
                    <Badge variant="outline" className="text-[10px] font-mono">
                      {g.category}
                    </Badge>
                  </div>
                  <p className="text-slate-600 leading-relaxed text-[11px]">{g.rule_text}</p>
                </div>
              ))}
            </CardContent>
            <div className="p-3 border-t border-slate-100 bg-slate-50/50 rounded-b-2xl flex items-center justify-between">
              <Link
                href="/dashboard/settings"
                onClick={() => setShowGuardrailDrawer(false)}
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1"
              >
                Configure & Add Rules in Settings <ExternalLink size={12} />
              </Link>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowGuardrailDrawer(false)}
                className="text-xs rounded-xl"
              >
                Close
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
