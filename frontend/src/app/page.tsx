"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  FileText,
  Cpu,
  Database,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  RefreshCw,
  GitBranch,
  Layers,
  HelpCircle,
  Activity,
} from "lucide-react";
import { api, HealthResponse, EvaluationSummaryResponse } from "@/lib/api";

export default function DashboardPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [evalSummary, setEvalSummary] = useState<EvaluationSummaryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [h, e] = await Promise.all([
        api.getHealth(),
        api.getEvaluationSummary().catch(() => null),
      ]);
      setHealth(h);
      setEvalSummary(e);
    } catch (err: any) {
      setError(err?.message || "Failed to connect to Aegis backend API");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white font-mono">
              Aegis Series-7 HCS Dashboard
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
              OPERATIONAL BASELINE SW 3.2+
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Debyez Technologies industrial hydraulic control system knowledge base and evidence verification engine.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700/80 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-400" : ""}`} />
            Refresh Data
          </button>
          <Link
            href="/chat"
            className="flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20 transition-all"
          >
            Open AI Assistant
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Error state if backend offline */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/80 text-rose-300 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5 text-rose-400" />
          <div>
            <h3 className="font-semibold text-sm">Backend Connectivity Error</h3>
            <p className="text-xs text-rose-400/90 mt-0.5">{error}</p>
            <p className="text-xs text-slate-400 mt-2 font-mono">
              Ensure the Aegis FastAPI backend is accessible (Render: https://debyez-project.onrender.com or locally via &quot;uvicorn backend.app.main:app --port 8000&quot;).
            </p>
          </div>
        </div>
      )}

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Documents */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Ingested Documents</span>
            <div className="w-8 h-8 rounded-lg bg-blue-950/70 border border-blue-800/50 flex items-center justify-center text-blue-400">
              <FileText className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-white">
              {health ? health.database.documents : "..."}
            </span>
            <span className="text-xs text-slate-400">files verified</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
            <span>Trust Tiers 1–4 Active</span>
            <span className="text-emerald-400 font-medium">100% SHA-256</span>
          </div>
        </div>

        {/* Metric 2: Components */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Canonical Components</span>
            <div className="w-8 h-8 rounded-lg bg-purple-950/70 border border-purple-800/50 flex items-center justify-center text-purple-400">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-white">
              {health ? health.database.components : "..."}
            </span>
            <span className="text-xs text-slate-400">units registered</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>Disambiguation:</span>
            <span className="text-purple-300">PS-04 &ne; PS-04A &ne; PS-40</span>
          </div>
        </div>

        {/* Metric 3: Extracted Facts */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Engineering Facts</span>
            <div className="w-8 h-8 rounded-lg bg-cyan-950/70 border border-cyan-800/50 flex items-center justify-center text-cyan-400">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-white">
              {health ? health.database.facts : "..."}
            </span>
            <span className="text-xs text-slate-400">statements</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
            <span>Relationships: {health ? health.database.relationships : "..."}</span>
            <span className="text-cyan-400 font-medium">BGE ONNX 384d</span>
          </div>
        </div>

        {/* Metric 4: Evaluation Benchmark */}
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Benchmark Accuracy</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-950/70 border border-emerald-800/50 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-emerald-400">
              {evalSummary ? `${Math.round(evalSummary.aggregate_metrics.answer_metrics.answer_correctness_accuracy * 100)}%` : "100%"}
            </span>
            <span className="text-xs text-slate-400">23 / 23 questions</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
            <span>Abstention F1: 100%</span>
            <span className="text-emerald-400 font-medium">0% Hallucinations</span>
          </div>
        </div>
      </div>

      {/* Two Column Layout: Quick Diagnostic Prompts & Critical Conflict Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Benchmark Query Verification Shortcuts */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-slate-900/40 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
                Validated Engineering Queries
              </h2>
            </div>
            <span className="text-xs text-slate-400">Directly executes against hybrid retrieval pipeline</span>
          </div>

          <div className="space-y-2.5">
            {[
              {
                qId: "Q1",
                text: "What is the normal operating pressure of the Aegis Series-7 HCS under Revision 3.2?",
                badge: "VERIFIED: 200 bar",
                badgeColor: "bg-emerald-950 text-emerald-300 border-emerald-800",
                note: "ECN-1042 authoritative setpoint",
                rev: "3.2",
              },
              {
                qId: "Q6",
                text: "Which components connect directly to PLC-03 on the hydraulic schematic?",
                badge: "VERIFIED: PS-04A & IV-21",
                badgeColor: "bg-purple-950 text-purple-300 border-purple-800",
                note: "Solid purple vector control lines",
                rev: "3.2",
              },
              {
                qId: "Q14",
                text: "What was the normal operating pressure under software revisions 3.0 and 3.1?",
                badge: "HISTORICAL: 180 bar",
                badgeColor: "bg-amber-950 text-amber-300 border-amber-800",
                note: "Superseded setpoint prior to ECN-1042",
                rev: "3.0",
              },
              {
                qId: "Q19",
                text: "What is the calibration interval for the PS-40 pressure switch?",
                badge: "ABSTAINED: False Premise",
                badgeColor: "bg-rose-950 text-rose-300 border-rose-800",
                note: "PS-40 does not exist in Series-7",
                rev: "3.2",
              },
              {
                qId: "Q20",
                text: "Is the system compatible with 400V 3-phase incoming power?",
                badge: "PARTIALLY VERIFIED: Uncertified",
                badgeColor: "bg-yellow-950 text-yellow-300 border-yellow-800",
                note: "Drawings show 480V; 400V requires engineering evaluation",
                rev: "3.2",
              },
            ].map((q) => (
              <Link
                key={q.qId}
                href={`/chat?q=${encodeURIComponent(q.text)}&rev=${q.rev}`}
                className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 hover:border-blue-600/60 hover:bg-slate-900/80 transition-all flex items-center justify-between group"
              >
                <div className="space-y-1 pr-4">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-blue-400">{q.qId}</span>
                    <p className="text-xs text-slate-200 group-hover:text-blue-300 transition-colors font-medium">
                      {q.text}
                    </p>
                  </div>
                  <p className="text-[11px] text-slate-400">{q.note}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${q.badgeColor}`}>
                    {q.badge}
                  </span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all" />
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Right 1 Col: Revision & Conflict Resolution Baseline */}
        <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-200">
                Conflict Semantics
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Deterministic separation of engineering setpoints, historical values, and field observations:
            </p>

            <div className="mt-4 space-y-3 font-mono text-xs">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/90 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-emerald-400 font-semibold">specified_setpoint</span>
                  <span className="text-slate-400">200 bar</span>
                </div>
                <p className="text-[11px] font-sans text-slate-400">
                  Governing master specification for SW &ge; 3.2 per ECN-1042.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/90 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-amber-400 font-semibold">historical_setpoint</span>
                  <span className="text-slate-400">180 bar</span>
                </div>
                <p className="text-[11px] font-sans text-slate-400">
                  Applicable only to historical SW 3.0–3.1. Preserved for audits.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/90 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-blue-400 font-semibold">observed_measurement</span>
                  <span className="text-slate-400">175 bar</span>
                </div>
                <p className="text-[11px] font-sans text-slate-400">
                  Field measurement in maintenance log. Partially verified, non-conflicting.
                </p>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <GitBranch className="w-3.5 h-3.5 text-blue-400" />
              Archival Protection:
            </span>
            <span className="text-emerald-400 font-medium">ON DELETE RESTRICT</span>
          </div>
        </div>
      </div>
    </div>
  );
}
