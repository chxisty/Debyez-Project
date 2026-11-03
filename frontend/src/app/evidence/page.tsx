"use client";

import { useState, useEffect } from "react";
import {
  FileSearch,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Layers,
  MapPin,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
} from "lucide-react";
import { api, FactItem } from "@/lib/api";

export default function EvidenceInspectorPage() {
  const [facts, setFacts] = useState<FactItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [factTypeFilter, setFactTypeFilter] = useState<string>("ALL");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [selectedFact, setSelectedFact] = useState<FactItem | null>(null);

  const loadFacts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getFacts();
      setFacts(data);
    } catch (err: any) {
      setError(err?.message || "Failed to load facts catalog");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFacts();
  }, []);

  const filteredFacts = facts.filter((f) => {
    const matchesSearch =
      f.subject.toLowerCase().includes(search.toLowerCase()) ||
      f.predicate.toLowerCase().includes(search.toLowerCase()) ||
      f.object_value.toLowerCase().includes(search.toLowerCase()) ||
      f.source_document.toLowerCase().includes(search.toLowerCase());
    const matchesType = factTypeFilter === "ALL" || f.fact_type === factTypeFilter;
    const matchesStatus = statusFilter === "ALL" || f.verification_status === statusFilter;
    return matchesSearch && matchesType && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "VERIFIED":
        return "bg-emerald-950/80 text-emerald-300 border-emerald-800";
      case "PARTIALLY VERIFIED":
        return "bg-yellow-950/80 text-yellow-300 border-yellow-800";
      case "CONFLICTING":
        return "bg-purple-950/80 text-purple-300 border-purple-800";
      default:
        return "bg-rose-950/80 text-rose-300 border-rose-800";
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <FileSearch className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold font-mono text-white">
              Evidence & Citation Inspector
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Deep forensic audit of extracted statements, exact source coordinates, extraction methods, and provenance.
          </p>
        </div>

        <button
          onClick={loadFacts}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-400" : ""}`} />
          Reload Evidence
        </button>
      </div>

      {/* Filters Bar */}
      <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative flex-1 w-full sm:max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search subject, predicate, value, source document..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Fact Type Filter */}
          <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs font-mono">
            <span className="text-slate-400">Fact Type:</span>
            <select
              value={factTypeFilter}
              onChange={(e) => setFactTypeFilter(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Types</option>
              <option value="specified_setpoint">Specified Setpoint</option>
              <option value="historical_setpoint">Historical Setpoint</option>
              <option value="observed_measurement">Observed Measurement</option>
              <option value="rule">Rule / Logic</option>
            </select>
          </div>

          {/* Verification Status Filter */}
          <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs font-mono">
            <span className="text-slate-400">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Statuses</option>
              <option value="VERIFIED">VERIFIED</option>
              <option value="PARTIALLY VERIFIED">PARTIALLY VERIFIED</option>
              <option value="CONFLICTING">CONFLICTING</option>
              <option value="NOT FOUND">NOT FOUND</option>
            </select>
          </div>
        </div>
      </div>

      {/* Facts Table */}
      <div className="rounded-xl bg-slate-900/40 border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[11px]">
              <tr>
                <th className="py-3 px-4">Subject & Predicate</th>
                <th className="py-3 px-3">Object Value</th>
                <th className="py-3 px-3">Fact Type</th>
                <th className="py-3 px-4">Source Document</th>
                <th className="py-3 px-3">Page / Cell</th>
                <th className="py-3 px-3">Extraction</th>
                <th className="py-3 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500 font-sans">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto text-blue-400 mb-2" />
                    Loading evidence database...
                  </td>
                </tr>
              ) : filteredFacts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500 font-sans">
                    No evidence statements matched criteria.
                  </td>
                </tr>
              ) : (
                filteredFacts.map((fact) => (
                  <tr
                    key={fact.fact_id}
                    onClick={() => setSelectedFact(fact)}
                    className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                  >
                    <td className="py-3 px-4">
                      <div className="font-bold text-blue-400">{fact.subject}</div>
                      <div className="text-[11px] text-slate-300 font-sans">{fact.predicate}</div>
                    </td>
                    <td className="py-3 px-3">
                      <strong className="text-white text-xs">
                        {fact.object_value} {fact.unit || ""}
                      </strong>
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                        {fact.fact_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-sans truncate max-w-[200px]">
                      {fact.source_document}
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      p. {fact.page_number}
                      {fact.cell_or_bbox ? ` (${fact.cell_or_bbox.substring(0, 16)}...)` : ""}
                    </td>
                    <td className="py-3 px-3 text-slate-400 text-[11px]">
                      {fact.extraction_method}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getStatusBadge(fact.verification_status)}`}>
                        {fact.verification_status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Fact Detail Modal */}
      {selectedFact && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedFact(null)}
        >
          <div
            className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-6 space-y-4 font-mono text-xs"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="text-blue-400 font-bold text-sm">{selectedFact.fact_id}</span>
                <h3 className="text-base font-bold text-white mt-0.5">
                  {selectedFact.subject} &bull; {selectedFact.predicate}
                </h3>
              </div>
              <span className={`px-2.5 py-0.5 rounded border text-[11px] font-semibold ${getStatusBadge(selectedFact.verification_status)}`}>
                {selectedFact.verification_status}
              </span>
            </div>

            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 grid grid-cols-2 gap-3">
              <div>
                <span className="text-slate-400">Object Value:</span>
                <p className="text-white text-sm font-bold mt-0.5">
                  {selectedFact.object_value} {selectedFact.unit || ""}
                </p>
              </div>
              <div>
                <span className="text-slate-400">Fact Type:</span>
                <p className="text-blue-300 font-semibold mt-0.5">{selectedFact.fact_type}</p>
              </div>
              <div>
                <span className="text-slate-400">Source Document:</span>
                <p className="text-slate-200 mt-0.5 font-sans font-medium">{selectedFact.source_document}</p>
              </div>
              <div>
                <span className="text-slate-400">Page & Coordinate:</span>
                <p className="text-slate-200 mt-0.5">
                  Page {selectedFact.page_number} {selectedFact.cell_or_bbox ? `(${selectedFact.cell_or_bbox})` : ""}
                </p>
              </div>
              <div>
                <span className="text-slate-400">Extraction Method:</span>
                <p className="text-slate-200 mt-0.5">{selectedFact.extraction_method}</p>
              </div>
              <div>
                <span className="text-slate-400">Extraction Confidence:</span>
                <p className="text-emerald-400 mt-0.5 font-bold">{(selectedFact.confidence * 100).toFixed(0)}%</p>
              </div>
            </div>

            {selectedFact.notes && (
              <div className="p-3 rounded bg-slate-950 border border-slate-800/80">
                <span className="text-slate-400 text-[10px] uppercase tracking-wider block">Auditor Notes:</span>
                <p className="text-slate-300 font-sans text-xs mt-1 leading-relaxed">
                  {selectedFact.notes}
                </p>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedFact(null)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-sans font-medium"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

