"use client";

import { useState, useEffect } from "react";
import {
  Cpu,
  Search,
  AlertTriangle,
  ArrowRight,
  GitBranch,
  ShieldAlert,
  Info,
  CheckCircle2,
  RefreshCw,
  Database,
  Layers,
  MapPin,
  Tag,
  Activity,
} from "lucide-react";
import { api, ComponentSummary, ComponentDetailResponse } from "@/lib/api";

export default function ComponentsPage() {
  const [components, setComponents] = useState<ComponentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("ALL");

  const [selectedCompId, setSelectedCompId] = useState<string | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [componentDetail, setComponentDetail] = useState<ComponentDetailResponse | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  const loadComponents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getComponents();
      setComponents(data);
    } catch (err: any) {
      setError(err?.message || "Failed to load components");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComponents();
  }, []);

  const openComponentDetail = async (id: string) => {
    setSelectedCompId(id);
    setDetailLoading(true);
    setDetailError(null);
    try {
      const detail = await api.getComponentDetail(id);
      setComponentDetail(detail);
    } catch (err: any) {
      setDetailError(err?.message || `Failed to fetch details for ${id}`);
    } finally {
      setDetailLoading(false);
    }
  };

  const filteredComponents = components.filter((c) => {
    const matchesSearch =
      c.component_id.toLowerCase().includes(search.toLowerCase()) ||
      c.canonical_name.toLowerCase().includes(search.toLowerCase()) ||
      c.aliases.some((a) => a.toLowerCase().includes(search.toLowerCase()));
    const matchesType = typeFilter === "ALL" || c.component_type.toLowerCase() === typeFilter.toLowerCase();
    return matchesSearch && matchesType;
  });

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <Cpu className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold font-mono text-white">
              Component Catalog & Entity Disambiguation
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Canonical register of Series-7 hardware, sensors, actuators, and negative disambiguation rules.
          </p>
        </div>

        <button
          onClick={loadComponents}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-400" : ""}`} />
          Reload Components
        </button>
      </div>

      {/* Negative Disambiguation Rule Banner */}
      <div className="p-4 rounded-xl bg-purple-950/40 border border-purple-800/80 text-purple-200 text-xs space-y-2">
        <div className="flex items-center gap-2 font-mono font-bold text-purple-300">
          <ShieldAlert className="w-4 h-4 text-purple-400" />
          MANDATORY DISAMBIGUATION RULES & FALSE-FRIEND PROTECTION
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-[11px] pt-1">
          <div className="p-2.5 rounded bg-slate-950/80 border border-purple-900/60">
            <span className="text-rose-400 font-bold">PS-04 &ne; PS-04A:</span>
            <p className="text-slate-300 font-sans mt-0.5">
              PS-04 was replaced by PS-04A in SW 3.2 per ECN-1042 to fix sensor drift.
            </p>
          </div>
          <div className="p-2.5 rounded bg-slate-950/80 border border-purple-900/60">
            <span className="text-rose-400 font-bold">PS-04 &ne; PS-40:</span>
            <p className="text-slate-300 font-sans mt-0.5">
              PS-40 does not exist in Aegis Series-7. It is a legacy Series-6 transducer.
            </p>
          </div>
          <div className="p-2.5 rounded bg-slate-950/80 border border-purple-900/60">
            <span className="text-emerald-400 font-bold">P.S.04-A &rarr; PS-04A:</span>
            <p className="text-slate-300 font-sans mt-0.5">
              Standardizes non-standard punctuation and whitespace aliases deterministically.
            </p>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative flex-1 w-full sm:max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search canonical ID, alias, name..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs font-mono">
          <span className="text-slate-400">Component Type:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value="ALL">All Types</option>
            <option value="sensor">Sensors</option>
            <option value="valve">Valves</option>
            <option value="controller">Controllers</option>
            <option value="reservoir">Reservoirs</option>
            <option value="power_unit">Power Units</option>
            <option value="electrical">Electrical</option>
            <option value="alarm">Alarms</option>
          </select>
        </div>
      </div>

      {/* Components Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full text-center py-12 text-slate-400">
            <RefreshCw className="w-5 h-5 animate-spin mx-auto text-blue-400 mb-2" />
            Loading component registry...
          </div>
        ) : filteredComponents.length === 0 ? (
          <div className="col-span-full text-center py-12 text-slate-400">
            No components matched your search.
          </div>
        ) : (
          filteredComponents.map((c) => (
            <div
              key={c.component_id}
              onClick={() => openComponentDetail(c.component_id)}
              className="p-5 rounded-xl bg-slate-900/40 border border-slate-800 hover:border-blue-600/60 hover:bg-slate-900/70 transition-all cursor-pointer flex flex-col justify-between group space-y-4"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-base font-bold font-mono text-white group-hover:text-blue-400 transition-colors">
                      {c.component_id}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                        c.status === "Active"
                          ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                          : "bg-amber-950 text-amber-300 border-amber-800"
                      }`}
                    >
                      {c.status}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {c.component_type}
                  </span>
                </div>

                <p className="text-xs text-slate-300 font-medium mt-1">{c.canonical_name}</p>

                {c.location && (
                  <p className="text-[11px] text-slate-400 mt-2 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{c.location}</span>
                  </p>
                )}

                {/* Known Aliases */}
                {c.aliases && c.aliases.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {c.aliases.slice(0, 3).map((alias, i) => (
                      <span
                        key={i}
                        className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800"
                      >
                        {alias}
                      </span>
                    ))}
                    {c.aliases.length > 3 && (
                      <span className="text-[10px] font-mono text-slate-400 px-1">
                        +{c.aliases.length - 3} more
                      </span>
                    )}
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                <div className="flex items-center gap-3 font-mono text-[11px]">
                  <span>{c.fact_count} facts</span>
                  <span>•</span>
                  <span>{c.relationship_count} relations</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
              </div>
            </div>
          ))
        )}
      </div>

      {/* Component Detail Modal */}
      {selectedCompId && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedCompId(null)}
        >
          <div
            className="w-full max-w-3xl max-h-[85vh] overflow-y-auto bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-6 space-y-6 font-sans text-xs"
            onClick={(e) => e.stopPropagation()}
          >
            {detailLoading ? (
              <div className="py-12 text-center text-slate-400 font-mono">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-400 mb-2" />
                Loading component details...
              </div>
            ) : componentDetail ? (
              <>
                {/* Modal Header */}
                <div className="flex items-start justify-between border-b border-slate-800 pb-4">
                  <div>
                    <div className="flex items-center gap-3">
                      <h2 className="text-xl font-bold font-mono text-white">
                        {componentDetail.component_id}
                      </h2>
                      <span
                        className={`text-xs font-mono px-2 py-0.5 rounded border ${
                          componentDetail.status === "Active"
                            ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                            : "bg-amber-950 text-amber-300 border-amber-800"
                        }`}
                      >
                        {componentDetail.status}
                      </span>
                    </div>
                    <p className="text-sm text-slate-300 mt-1">{componentDetail.canonical_name}</p>
                    {componentDetail.description && (
                      <p className="text-xs text-slate-400 mt-1">{componentDetail.description}</p>
                    )}
                  </div>
                  <button
                    onClick={() => setSelectedCompId(null)}
                    className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
                  >
                    Close
                  </button>
                </div>

                {/* Aliases & Location */}
                <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2 font-mono text-[11px]">
                  <div>
                    <span className="text-slate-400">Physical Location:</span>
                    <span className="text-slate-200 ml-2 font-semibold">
                      {componentDetail.location || "System Chassis / Diagram Block"}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400">Known Aliases:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {componentDetail.aliases.map((a, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-blue-300"
                        >
                          {a}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Relationships */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-slate-300 font-mono text-xs uppercase tracking-wider flex items-center gap-2">
                    <GitBranch className="w-3.5 h-3.5 text-blue-400" />
                    Topological Relationships ({componentDetail.relationships.length})
                  </h3>
                  {componentDetail.relationships.length === 0 ? (
                    <p className="text-slate-400 italic">No direct connections recorded.</p>
                  ) : (
                    <div className="space-y-2">
                      {componentDetail.relationships.map((rel) => (
                        <div
                          key={rel.rel_id}
                          className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs font-mono space-y-1"
                        >
                          <div className="flex items-center justify-between text-slate-200">
                            <span>
                              <strong className="text-blue-400">{rel.source_component}</strong>{" "}
                              &rarr;{" "}
                              <span className="text-purple-300">{rel.relationship_type}</span>{" "}
                              &rarr;{" "}
                              <strong className="text-emerald-400">{rel.target_component}</strong>
                            </span>
                            <span className="text-slate-400 text-[10px]">{rel.line_type}</span>
                          </div>
                          {rel.notes && (
                            <p className="text-[11px] font-sans text-slate-400">{rel.notes}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Facts */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-slate-300 font-mono text-xs uppercase tracking-wider flex items-center gap-2">
                    <Database className="w-3.5 h-3.5 text-cyan-400" />
                    Ingested Facts & Specifications ({componentDetail.facts.length})
                  </h3>
                  {componentDetail.facts.length === 0 ? (
                    <p className="text-slate-400 italic">No facts registered for this subject.</p>
                  ) : (
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {componentDetail.facts.map((f) => (
                        <div
                          key={f.fact_id}
                          className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs font-mono flex items-center justify-between"
                        >
                          <div>
                            <span className="text-slate-400">{f.predicate}:</span>{" "}
                            <strong className="text-white">
                              {f.object_value} {f.unit || ""}
                            </strong>
                            <div className="text-[10px] text-slate-400 font-sans mt-0.5">
                              Source: {f.source_document} (p. {f.page_number})
                            </div>
                          </div>
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded border ${
                              f.fact_type === "specified_setpoint"
                                ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                                : f.fact_type === "observed_measurement"
                                ? "bg-blue-950 text-blue-300 border-blue-800"
                                : "bg-amber-950 text-amber-300 border-amber-800"
                            }`}
                          >
                            {f.fact_type}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="text-rose-400">{detailError || "No details found."}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

