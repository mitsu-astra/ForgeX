import Link from "next/link";
import { ArrowRight, Sparkles, Shield, Zap, TrendingUp, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* Animated gradient mesh background */}
      <div className="absolute inset-0 gradient-mesh opacity-40" />
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />

      {/* Floating orbs */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/30 rounded-full filter blur-3xl animate-pulse" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/30 rounded-full filter blur-3xl animate-pulse delay-700" />

      {/* Navigation */}
      <nav className="relative z-10 border-b border-white/10 glass-dark">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 bg-blue-500 rounded-xl blur-xl opacity-50" />
                <div className="relative w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
              </div>
              <div>
                <div className="text-lg font-bold text-white tracking-tight">ForgeX</div>
                <div className="text-xs text-slate-400">Industrial Decision Intelligence</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/login" className="text-sm text-slate-300 hover:text-white transition-colors">
                Sign In
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center justify-center rounded-lg text-sm font-medium px-4 py-2 text-white gradient-brand shadow-md hover:opacity-90 transition-all"
              >
                Launch Platform <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative z-10 container mx-auto px-6 pt-24 pb-16">
        <div className="max-w-5xl mx-auto text-center space-y-8 animate-fade-in">
          <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 px-4 py-1.5">
            <Sparkles className="h-3 w-3 mr-2 inline" />
            ForgeX • Autonomous Manufacturing Intelligence
          </Badge>

          <h1 className="text-6xl md:text-7xl font-bold text-white leading-tight tracking-tight">
            Transform Defects Into
            <span className="block mt-2 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 text-transparent bg-clip-text">
              Actionable Insights
            </span>
          </h1>

          <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
            Real-time visual inspection, root-cause analysis, and AI-driven recommendations
            for modern manufacturing. Boost quality, reduce costs, maximize throughput.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-6">
            <Link
              href="/dashboard/upload"
              className="inline-flex items-center justify-center rounded-lg text-lg font-medium gradient-brand text-white px-8 py-4 glow group shadow-lg hover:opacity-95 transition-all"
            >
              Start Analysis
              <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-lg text-lg font-medium border border-white/20 text-white hover:bg-white/10 px-8 py-4 transition-all"
            >
              View Demo
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 pt-12 max-w-3xl mx-auto">
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-1">94%</div>
              <div className="text-sm text-slate-400">Detection Accuracy</div>
            </div>
            <div className="text-center border-x border-white/10">
              <div className="text-4xl font-bold text-white mb-1">&lt;3s</div>
              <div className="text-sm text-slate-400">Processing Time</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-1">10K+</div>
              <div className="text-sm text-slate-400">Images Analyzed</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="relative z-10 container mx-auto px-6 py-20">
        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          <FeatureCard
            icon={<Shield className="h-6 w-6" />}
            title="AI-Powered Detection"
            description="Deep learning models classify and localize defects with industry-leading accuracy"
            metrics={["5 defect types", "Real-time processing"]}
          />
          <FeatureCard
            icon={<Zap className="h-6 w-6" />}
            title="Root Cause Analysis"
            description="Correlate defects with process conditions using statistical and ML methods"
            metrics={["SHAP explanations", "Evidence-based"]}
          />
          <FeatureCard
            icon={<TrendingUp className="h-6 w-6" />}
            title="Smart Recommendations"
            description="Actionable insights ranked by impact, feasibility, and expected ROI"
            metrics={["What-if simulator", "Cost analysis"]}
          />
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative z-10 container mx-auto px-6 py-20">
        <Card className="glass border-white/20 p-12 max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to optimize your production?</h2>
          <p className="text-lg text-slate-300 mb-8">
            Upload your inspection data and get instant AI-powered insights
          </p>
          <Link
            href="/dashboard/upload"
            className="inline-flex items-center justify-center rounded-lg text-lg font-medium gradient-brand text-white px-8 py-4 shadow-lg hover:opacity-95 transition-all"
          >
            Get Started for Free
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </Card>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description, metrics }: {
  icon: React.ReactNode;
  title: string;
  description: string;
  metrics: string[];
}) {
  return (
    <Card className="glass border-white/20 p-8 hover-lift group">
      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
        <div className="text-white">{icon}</div>
      </div>
      <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-slate-400 mb-6 leading-relaxed">{description}</p>
      <div className="flex flex-wrap gap-2">
        {metrics.map((metric, i) => (
          <Badge key={i} variant="outline" className="border-blue-500/30 text-blue-400 bg-blue-500/5">
            <Check className="h-3 w-3 mr-1" />
            {metric}
          </Badge>
        ))}
      </div>
    </Card>
  );
}
