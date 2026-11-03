"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Send,
  Sparkles,
  ShieldCheck,
  AlertOctagon,
  HelpCircle,
  FileText,
  Clock,
  Layers,
  Info,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Cpu,
  BookOpen,
  ArrowRight,
  RefreshCw,
  ExternalLink,
} from "lucide-react";
import { api, GroundedAnswer, EvidenceCitation } from "@/lib/api";

function ChatContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  const initialRev = searchParams.get("rev") || "3.2";

  const [query, setQuery] = useState(initialQuery);
  const [targetRevision, setTargetRevision] = useState(initialRev);
  const [forceOffline, setForceOffline] = useState(false);
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<GroundedAnswer | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (overrideQuery?: string, overrideRev?: string) => {
    const q = overrideQuery !== undefined ? overrideQuery : query;
    const rev = overrideRev !== undefined ? overrideRev : targetRevision;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await api.askChat(q, rev, forceOffline);
      setAnswer(res);
    } catch (err: any) {
      setError(err?.message || "Inference error occurred while querying knowledge base.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuery) {
      handleSearch(initialQuery, initialRev);
    }
  }, [initialQuery, initialRev]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "VERIFIED":
        return {
          bg: "bg-emerald-950/80 text-emerald-300 border-emerald-700/60",
          icon: CheckCircle2,
          label: "VERIFIED GROUNDING",
        };
      case "PARTIALLY VERIFIED":
        return {
          bg: "bg-yellow-950/80 text-yellow-300 border-yellow-700/60",
          icon: AlertTriangle,
          label: "PARTIALLY SUPPORTED / UNCONFIRMED",
        };
      case "CONFLICTING":
        return {
          bg: "bg-purple-950/80 text-purple-300 border-purple-700/60",
          icon: AlertOctagon,
          label: "CONFLICTING EVIDENCE DETECTED",
        };
      default:
        return {
          bg: "bg-rose-950/80 text-rose-300 border-rose-700/60",
          icon: HelpCircle,
          label: "NOT FOUND / UNVERIFIABLE",
        };
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold font-mono text-white">
              AI Knowledge Assistant
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Evidence-grounded question answering with revision context, atomic claim grounding, and epistemic abstention.
          </p>
        </div>

        {/* Controls: Revision Context & Offline Toggle */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs font-mono">
            <span className="text-slate-400">Context Revision:</span>
            <select
              value={targetRevision}
              onChange={(e) => setTargetRevision(e.target.value)}
              className="bg-transparent text-blue-300 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="3.2" className="bg-slate-900 text-slate-200">
                SW 3.2+ (Current Production)
              </option>
              <option value="3.0" className="bg-slate-900 text-slate-200">
                SW 3.0 – 3.1 (Historical)
              </option>
              <option value="3.2.1" className="bg-slate-900 text-slate-200">
                SW 3.2.1 (ECN-1058 Patch)
              </option>
            </select>
          </div>

          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg select-none">
            <input
              type="checkbox"
              checked={forceOffline}
              onChange={(e) => setForceOffline(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-blue-600 focus:ring-0"
            />
            <span className="font-mono text-[11px]">Deterministic Engine</span>
          </label>
        </div>
      </div>

      {/* Query Input Box */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 shadow-xl space-y-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a technical engineering question (e.g., normal operating pressure, PLC-03 connections, PS-04A drift interval)..."
            className="flex-1 px-4 py-2.5 rounded-lg bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium text-xs flex items-center gap-2 transition-all shadow-md shadow-blue-600/20"
          >
            {loading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            Query Engine
          </button>
        </form>

        {/* Quick Question Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-400">
          <span className="text-slate-400 font-medium">Quick Prompts:</span>
          {[
            { label: "Normal Pressure (Rev 3.2)", q: "What is the normal operating pressure under Revision 3.2?", rev: "3.2" },
            { label: "PLC-03 Schematic Pins", q: "Which components connect directly to PLC-03 on the hydraulic schematic?", rev: "3.2" },
            { label: "Historical 3.0 Pressure", q: "What was the normal operating pressure under software revisions 3.0 and 3.1?", rev: "3.0" },
            { label: "PS-40 Pressure Switch", q: "What is the calibration interval for the PS-40 pressure switch?", rev: "3.2" },
            { label: "400V Supply Rating", q: "Is the system compatible with 400V 3-phase incoming power?", rev: "3.2" },
            { label: "Auxiliary Reservoir", q: "What is the function of the Auxiliary Reservoir and which documents mention it?", rev: "3.2" },
          ].map((item, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(item.q);
                setTargetRevision(item.rev);
                handleSearch(item.q, item.rev);
              }}
              className="px-2.5 py-1 rounded bg-slate-950 border border-slate-800 hover:border-slate-700 hover:text-blue-300 text-slate-300 transition-colors font-mono"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">Query Execution Failed</h4>
            <p className="text-xs text-rose-300/90 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Answer Output View */}
      {answer && (
        <div className="space-y-6">
          {/* Main Direct Answer Card */}
          <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800 shadow-xl space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
              <div className="flex items-center gap-2.5">
                {(() => {
                  const b = getStatusBadge(answer.verification_status);
                  const Icon = b.icon;
                  return (
                    <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono font-semibold border ${b.bg}`}>
                      <Icon className="w-3.5 h-3.5" />
                      {b.label}
                    </span>
                  );
                })()}
                <span className="text-xs text-slate-400 font-mono">
                  Context: SW {answer.applicable_revision}
                </span>
              </div>

              <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
                <span>Method: {answer.generation_method}</span>
                <span>•</span>
                <span title="Heuristic engineering score based on source trust tier and extraction fidelity">
                  Confidence: {(answer.confidence_score * 100).toFixed(0)}%*
                </span>
              </div>
            </div>

            {/* Epistemic Abstention Warning Banner */}
            {answer.abstention_category && answer.abstention_category !== "NONE" && (
              <div className="p-4 rounded-lg bg-rose-950/50 border border-rose-800 text-rose-200 space-y-2">
                <div className="flex items-center gap-2">
                  <AlertOctagon className="w-4 h-4 text-rose-400" />
                  <span className="font-bold text-xs uppercase tracking-wider text-rose-300">
                    Epistemic Abstention: {answer.abstention_category}
                  </span>
                </div>
                <p className="text-xs text-rose-200/95 leading-relaxed">
                  {answer.abstention_explanation || "The system explicitly abstains from providing an ungrounded or speculative response."}
                </p>
              </div>
            )}

            {/* Limitations, Disambiguations & Conflicts */}
            {answer.limitations_and_conflicts && answer.limitations_and_conflicts.length > 0 && (
              <div className="p-3.5 rounded-lg bg-purple-950/40 border border-purple-800/60 text-purple-200 text-xs space-y-1">
                <div className="flex items-center gap-1.5 font-semibold text-purple-300 uppercase tracking-wider text-[11px]">
                  <Cpu className="w-3.5 h-3.5" />
                  Engineering Notes & Disambiguation Constraints
                </div>
                {answer.limitations_and_conflicts.map((note, i) => (
                  <p key={i} className="text-purple-300/90 font-mono text-[11px]">&bull; {note}</p>
                ))}
              </div>
            )}

            {/* Direct Answer Prose */}
            <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed space-y-2">
              <p className="whitespace-pre-line font-sans">{answer.direct_answer}</p>
            </div>

            {/* Confidence Justification Footnote */}
            <div className="pt-2 text-[11px] font-mono text-slate-400 flex items-center gap-2">
              <Info className="w-3.5 h-3.5 text-blue-400 shrink-0" />
              <span>Justification: {answer.confidence_justification}</span>
            </div>
          </div>

          {/* Atomic Supporting Claims */}
          {answer.supporting_claims && answer.supporting_claims.length > 0 && (
            <div className="p-5 rounded-xl bg-slate-900/30 border border-slate-800 space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Layers className="w-3.5 h-3.5 text-blue-400" />
                Atomic Claim Grounding & Verification ({answer.supporting_claims.length})
              </h3>
              <div className="space-y-2">
                {answer.supporting_claims.map((claimText, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-slate-950/80 border border-slate-800/80 flex items-start gap-3"
                  >
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <p className="text-xs text-slate-200 font-medium leading-relaxed">{claimText}</p>
                  </div>
                ))}
              </div>
              <p className="text-[10px] text-slate-400 italic font-mono pt-1">
                * Note: Confidence scores represent heuristic engineering scores derived from document trust tiers and extraction fidelity, not calibrated Bayesian probabilities.
              </p>
            </div>
          )}

          {/* Verified Citations & Evidence Audit Trail */}
          {answer.citations && answer.citations.length > 0 && (
            <div className="p-5 rounded-xl bg-slate-900/30 border border-slate-800 space-y-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <FileText className="w-3.5 h-3.5 text-blue-400" />
                Verified Citations & Technical Evidence Audit ({answer.citations.length})
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {answer.citations.map((cit, idx) => {
                  const rawUrl = api.getRawDocumentUrl(cit.source_document);
                  return (
                    <div
                      key={cit.chunk_id || idx}
                      className="p-4 rounded-lg bg-slate-950/90 border border-slate-800 hover:border-slate-700 transition-all space-y-2.5 flex flex-col justify-between"
                    >
                      <div className="space-y-2">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-mono font-bold text-blue-400">
                                {cit.chunk_id || `CIT-${idx + 1}`}
                              </span>
                              <span className="text-xs font-semibold text-slate-200 font-mono">
                                {cit.source_document}
                              </span>
                            </div>
                            <p className="text-[11px] font-mono text-slate-400 mt-0.5">
                              Page {cit.page_number}
                              {cit.section_or_cell ? ` • § ${cit.section_or_cell}` : ""}
                            </p>
                          </div>

                          <span
                            className={`text-[10px] font-mono px-2 py-0.5 rounded border shrink-0 ${
                              cit.trust_tier === 1
                                ? "bg-purple-950 text-purple-300 border-purple-800"
                                : "bg-blue-950 text-blue-300 border-blue-800"
                            }`}
                          >
                            Tier {cit.trust_tier}
                          </span>
                        </div>

                        {/* Excerpt quote */}
                        <div className="p-2.5 rounded bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-300 space-y-1">
                          <div className="text-[10px] text-slate-400 uppercase tracking-wider">
                            Quoted Evidence:
                          </div>
                          <p className="text-slate-200 leading-relaxed italic">
                            &quot;{cit.quoted_evidence}&quot;
                          </p>
                        </div>
                      </div>

                      {/* Footer: Open raw document link */}
                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono">
                        <span className="text-emerald-400 font-semibold">{cit.verification_status}</span>
                        <a
                          href={rawUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-blue-400 hover:text-blue-300 font-sans font-medium"
                        >
                          <span>Open Source File</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="p-8 text-slate-400 font-mono text-sm">Loading Knowledge Assistant...</div>}>
      <ChatContent />
    </Suspense>
  );
}
