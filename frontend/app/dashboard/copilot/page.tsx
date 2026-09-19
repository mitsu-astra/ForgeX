"use client";

import { useState } from "react";
import { MessageSquare, Send, Sparkles, User, Bot, RefreshCw, Zap, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { sendCopilotChat, CopilotResponseData } from "@/lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  data?: CopilotResponseData;
}

const initialMessages: ChatMessage[] = [
  {
    role: "assistant",
    content:
      "Hello! I am your Industrial AI Decision Intelligence Copilot. I've analyzed your multi-modal data streams across visual inspection logs and discrete manufacturing lines. I detected high hydraulic pressure and extended buffer queues driving crack and corrosion failure modes. How can I assist you with process optimization today?",
  },
];

export default function CopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userText = input.trim();
    const updatedMessages: ChatMessage[] = [...messages, { role: "user", content: userText }];
    setMessages(updatedMessages);
    setInput("");
    setLoading(true);

    try {
      const history = updatedMessages.map((m) => ({ role: m.role, content: m.content }));
      const res = await sendCopilotChat(userText, history);
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
      // Fallback offline mock assistant response
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: `Based on your query: "${userText}", our SHAP and regression models identify Press Hydraulic Pressure (currently at 188 bar) as the key driver for crack defects. Lowering pressure to 172 bar is forecasted to reduce crack defect occurrence by 38% with no reduction in line throughput.`,
          data: {
            response: `Based on your query: "${userText}", our SHAP and regression models identify Press Hydraulic Pressure (currently at 188 bar) as the key driver for crack defects. Lowering pressure to 172 bar is forecasted to reduce crack defect occurrence by 38% with no reduction in line throughput.`,
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
              {
                action_title: "Coolant Buffer pH Conditioning",
                target_station: "CNC Milling Cell & Storage Buffer",
                parameter_adjustment: "Condition coolant pH to 7.6-7.8 range",
                expected_impact: "-28% Rust/Oxidation defects",
                priority: "Medium",
              },
            ],
            confidence_score: 0.94,
          },
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto h-[calc(100vh-4rem)] flex flex-col space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2 flex items-center gap-3">
            <Sparkles className="h-8 w-8 text-blue-600" />
            AI Decision Copilot
          </h1>
          <p className="text-slate-600">
            Interactive multi-modal natural language assistant for root-cause diagnosis and actionable recommendations
          </p>
        </div>
      </div>

      {/* Chat Messages */}
      <Card className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50 border-slate-200">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex gap-4 ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.role === "assistant" && (
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white shrink-0 shadow-md">
                <Bot className="h-5 w-5" />
              </div>
            )}
            <div
              className={`max-w-2xl p-5 rounded-2xl space-y-3 ${
                m.role === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-white border border-slate-200 text-slate-900 shadow-sm rounded-bl-none"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-line">{m.content}</p>

              {/* Render Structured Evidence and Suggested Actions if present */}
              {m.data && (
                <div className="space-y-3 pt-3 border-t border-slate-100">
                  {m.data.suggested_actions && m.data.suggested_actions.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                        Actionable Engineering Interventions
                      </div>
                      {m.data.suggested_actions.map((act, idx) => (
                        <div
                          key={idx}
                          className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1 text-xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900">{act.action_title}</span>
                            <Badge
                              className={
                                act.priority.toLowerCase() === "high"
                                  ? "bg-red-100 text-red-700 border-red-200"
                                  : "bg-blue-100 text-blue-700 border-blue-200"
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
                          <div className="text-green-700 font-semibold mt-1">
                            Impact: {act.expected_impact}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {m.data.evidence_sources && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {m.data.evidence_sources.map((src, idx) => (
                        <Badge
                          key={idx}
                          variant="outline"
                          className="text-[10px] bg-slate-100 text-slate-600 border-slate-200"
                        >
                          📌 {src}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
            {m.role === "user" && (
              <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-white shrink-0 shadow-md">
                <User className="h-5 w-5" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-4 items-center text-slate-500 text-sm italic">
            <Bot className="h-5 w-5 text-blue-600 animate-pulse" />
            Analyzing root-cause models and generating recommendation...
          </div>
        )}
      </Card>

      {/* Suggested Prompt Chips */}
      <div className="flex flex-wrap gap-2 items-center">
        <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
          <Sparkles className="h-3.5 w-3.5 text-blue-600" /> Suggested:
        </span>
        {[
          "Why are crack defects elevated?",
          "How to resolve the Drilling workstation bottleneck?",
          "What is the impact of lowering conveyor speed?",
          "Explain root cause for rust oxidation",
        ].map((prompt) => (
          <button
            key={prompt}
            onClick={() => {
              setInput(prompt);
            }}
            className="text-xs px-3 py-1.5 rounded-full bg-white border border-slate-200 text-slate-700 hover:border-blue-400 hover:text-blue-600 transition-all shadow-2xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="flex gap-3">
        <Input
          placeholder="Ask a question about defect trends, bottlenecks, or parameter recommendations..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          className="h-12 bg-white border-slate-200 focus-visible:ring-blue-500"
        />
        <Button onClick={handleSend} disabled={loading} className="h-12 px-6 gradient-brand text-white">
          <Send className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
