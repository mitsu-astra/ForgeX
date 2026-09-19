"use client";

import { useState } from "react";
import { Settings as SettingsIcon, Shield, Sliders, Bell, Database, CheckCircle2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";

export default function SettingsPage() {
  const [confidenceThreshold, setConfidenceThreshold] = useState("85");
  const [gradCamAuto, setGradCamAuto] = useState(true);
  const [bottleneckAlert, setBottleneckAlert] = useState(true);
  const [mcDropoutSamples, setMcDropoutSamples] = useState("5");
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSave = () => {
    setSaveSuccess(true);
    setTimeout(() => {
      setSaveSuccess(false);
    }, 3000);
  };

  return (
    <div className="p-8 space-y-8 max-w-4xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Platform Settings</h1>
          <p className="text-slate-600">Configure AI model thresholds, alerts, and system parameters</p>
        </div>
        <Button onClick={handleSave} className="gradient-brand text-white shadow-md">
          <Save className="h-4 w-4 mr-2" /> Save Configuration
        </Button>
      </div>

      {saveSuccess && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-xl text-green-800 text-sm font-semibold flex items-center gap-2 animate-fade-in">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          Settings saved successfully! Model inference and monitoring thresholds updated.
        </div>
      )}

      <div className="space-y-6">
        <Card className="border-slate-200 bg-white">
          <CardHeader>
            <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
              <Sliders className="h-5 w-5 text-blue-600" />
              AI Model Inference Settings
            </CardTitle>
            <CardDescription className="text-slate-600">
              Thresholds for defect classification and Grad-CAM generation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-900 text-sm">Confidence Flag Threshold (%)</div>
                <div className="text-xs text-slate-500">Minimum confidence to flag a defect region</div>
              </div>
              <Input
                type="number"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(e.target.value)}
                className="w-24 bg-white"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-900 text-sm">Monte Carlo Dropout Iterations</div>
                <div className="text-xs text-slate-500">Number of forward passes to quantify epistemic uncertainty</div>
              </div>
              <Input
                type="number"
                value={mcDropoutSamples}
                onChange={(e) => setMcDropoutSamples(e.target.value)}
                className="w-24 bg-white"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-900 text-sm">Grad-CAM Auto-Generation</div>
                <div className="text-xs text-slate-500">Automatically generate heatmaps for defects with confidence &gt;90%</div>
              </div>
              <Switch checked={gradCamAuto} onCheckedChange={setGradCamAuto} />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 bg-white">
          <CardHeader>
            <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
              <Bell className="h-5 w-5 text-amber-500" />
              Operational Alert Notifications
            </CardTitle>
            <CardDescription className="text-slate-600">
              Configure real-time monitoring thresholds and operator warnings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-slate-900 text-sm">Severe Bottleneck Alert</div>
                <div className="text-xs text-slate-500">Notify when workstation utilization exceeds 95%</div>
              </div>
              <Switch checked={bottleneckAlert} onCheckedChange={setBottleneckAlert} />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
