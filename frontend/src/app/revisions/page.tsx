"use client";

import { useState, useEffect } from "react";
import {
  GitCompare,
  CheckCircle2,
  AlertTriangle,
  Clock,
  FileText,
  ShieldAlert,
  ArrowRight,
  Layers,
  RefreshCw,
  GitCommit,
} from "lucide-react";
import { api, RevisionItem } from "@/lib/api";

export default function RevisionComparisonPage() {
  const [revisions, setRevisions] = useState<RevisionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [revA, setRevA] = useState<string>("3.0");
  const [revB, setRevB] = useState<string>("3.2");

  const loadRevisions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRevisions();
      setRevisions(data);
    } catch (err: any) {
      setError(err?.message || "Failed to load revisions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRevisions();
  }, []);

  const revAData = revisions.find((r) => r.software_revision === revA);
  const revBData = revisions.find((r) => r.software_revision === revB);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <GitCompare className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold font-mono text-white">
              Software Revision & Engineering Delta Comparison
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Compare setpoints, sensor hardware, and ECN authority across Aegis Series-7 software releases.
          </p>
        </div>

        <button
          onClick={loadRevisions}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-400" : ""}`} />
          Reload Revisions
        </button>
      </div>

      {/* Critical Revision Segregation Warning */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-2">
        <div className="flex items-center gap-2 font-mono font-bold text-blue-300">
          <ShieldAlert className="w-4 h-4 text-blue-400" />
          SYSTEM REVISION CONTEXT VS. DOCUMENT PUBLICATION EDITIONS
        </div>
        <p className="text-slate-300 leading-relaxed">
          The Aegis Knowledge Base strictly segregates <strong>Software Operating Revisions</strong> (e.g., <code>SW 3.0</code>, <code>SW 3.1</code>, <code>SW 3.2</code>) from <strong>Document Publication Editions</strong> (e.g., <code>Rev 4</code>, <code>Rev 5</code> of the Operator Manual). Publication editions do not advance system operating pressure setpoints unless accompanied by an authorized Engineering Change Notice (ECN).
        </p>
      </div>

      {/* Revision Selectors Bar */}
      <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
        {/* Baseline A */}
        <div className="w-full md:w-1/2 p-4 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2 font-mono">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Baseline Release (Rev A)
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
              HISTORICAL
            </span>
          </div>
          <select
            value={revA}
            onChange={(e) => setRevA(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm font-bold text-amber-300 focus:outline-none focus:border-amber-500 cursor-pointer"
          >
            {revisions.map((r) => (
              <option key={r.software_revision} value={r.software_revision}>
                Software Rev {r.software_revision} ({r.effective_date})
              </option>
            ))}
          </select>
        </div>

        <div className="hidden md:flex items-center justify-center">
          <div className="w-10 h-10 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-slate-400 font-bold font-mono text-xs">
            VS
          </div>
        </div>

        {/* Baseline B */}
        <div className="w-full md:w-1/2 p-4 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2 font-mono">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Target Release (Rev B)
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              PRODUCTION
            </span>
          </div>
          <select
            value={revB}
            onChange={(e) => setRevB(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm font-bold text-emerald-300 focus:outline-none focus:border-emerald-500 cursor-pointer"
          >
            {revisions.map((r) => (
              <option key={r.software_revision} value={r.software_revision}>
                Software Rev {r.software_revision} ({r.effective_date})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Side-by-Side Comparison Matrix */}
      {revAData && revBData && (
        <div className="rounded-xl bg-slate-900/40 border border-slate-800 overflow-hidden shadow-2xl font-mono text-xs">
          <table className="w-full text-left">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 text-[11px] uppercase">
              <tr>
                <th className="py-3 px-6 w-1/3">Engineering Parameter</th>
                <th className="py-3 px-6 w-1/3 text-amber-300">
                  Rev {revAData.software_revision} ({revAData.effective_date})
                </th>
                <th className="py-3 px-6 w-1/3 text-emerald-300">
                  Rev {revBData.software_revision} ({revBData.effective_date})
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {/* Parameter 1: Operating Pressure */}
              <tr className="hover:bg-slate-800/30 transition-colors">
                <td className="py-4 px-6 text-slate-300 font-sans font-medium">
                  Normal Operating Pressure
                  <p className="text-[10px] text-slate-400 font-mono">Official specified setpoint</p>
                </td>
                <td className="py-4 px-6 text-amber-300 font-bold text-sm">
                  {revAData.operating_pressure_bar} bar
                </td>
                <td className="py-4 px-6 text-emerald-300 font-bold text-sm">
                  <div className="flex items-center gap-2">
                    <span>{revBData.operating_pressure_bar} bar</span>
                    {revAData.operating_pressure_bar !== revBData.operating_pressure_bar && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-semibold">
                        +{revBData.operating_pressure_bar - revAData.operating_pressure_bar} bar increase
                      </span>
                    )}
                  </div>
                </td>
              </tr>

              {/* Parameter 2: Active Pressure Sensor */}
              <tr className="hover:bg-slate-800/30 transition-colors">
                <td className="py-4 px-6 text-slate-300 font-sans font-medium">
                  Primary Pressure Transducer
                  <p className="text-[10px] text-slate-400 font-mono">Installed sensor hardware</p>
                </td>
                <td className="py-4 px-6 text-slate-300 font-semibold">
                  {revAData.active_pressure_sensor}
                  {revAData.active_pressure_sensor === "PS-04" && (
                    <span className="block text-[10px] text-rose-400 mt-0.5 font-sans">
                      Subject to 18-month calibration drift
                    </span>
                  )}
                </td>
                <td className="py-4 px-6 text-slate-300 font-semibold">
                  <div className="flex items-center gap-2">
                    <span>{revBData.active_pressure_sensor}</span>
                    {revAData.active_pressure_sensor !== revBData.active_pressure_sensor && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-semibold">
                        Replaced by ECN-1042
                      </span>
                    )}
                  </div>
                </td>
              </tr>

              {/* Parameter 3: Governing ECN */}
              <tr className="hover:bg-slate-800/30 transition-colors">
                <td className="py-4 px-6 text-slate-300 font-sans font-medium">
                  Governing Engineering Change
                  <p className="text-[10px] text-slate-400 font-mono">Master authority record</p>
                </td>
                <td className="py-4 px-6 text-slate-400">
                  {revAData.governing_ecn || "Initial Production Baseline"}
                </td>
                <td className="py-4 px-6 text-blue-300 font-bold">
                  {revBData.governing_ecn || "Initial Production Baseline"}
                </td>
              </tr>

              {/* Parameter 4: Release Status */}
              <tr className="hover:bg-slate-800/30 transition-colors">
                <td className="py-4 px-6 text-slate-300 font-sans font-medium">
                  Release Lifecycle Status
                  <p className="text-[10px] text-slate-400 font-mono">Operational deployment</p>
                </td>
                <td className="py-4 px-6">
                  <span className="px-2 py-0.5 rounded text-[10px] bg-amber-950 text-amber-300 border border-amber-800">
                    {revAData.status}
                  </span>
                </td>
                <td className="py-4 px-6">
                  <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800">
                    {revBData.status}
                  </span>
                </td>
              </tr>

              {/* Parameter 5: Summary of Changes */}
              <tr className="hover:bg-slate-800/30 transition-colors">
                <td className="py-4 px-6 text-slate-300 font-sans font-medium">
                  Summary of Engineering Changes
                </td>
                <td className="py-4 px-6 text-slate-400 font-sans text-xs leading-relaxed">
                  {revAData.summary_of_changes}
                </td>
                <td className="py-4 px-6 text-slate-300 font-sans text-xs leading-relaxed">
                  {revBData.summary_of_changes}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {/* Complete Historical Timeline */}
      <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 space-y-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono flex items-center gap-2">
          <GitCommit className="w-4 h-4 text-blue-400" />
          Complete Software Revision History
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono text-xs">
          {revisions.map((rev) => (
            <div
              key={rev.software_revision}
              className={`p-4 rounded-lg border transition-all ${
                rev.software_revision === revB
                  ? "bg-slate-950 border-emerald-500/50 shadow-md shadow-emerald-500/10"
                  : "bg-slate-950/60 border-slate-800"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-white">Rev {rev.software_revision}</span>
                <span className="text-[10px] text-slate-400">{rev.effective_date}</span>
              </div>
              <div className="mt-2 text-slate-300 font-sans text-[11px] space-y-1">
                <div>Operating Setpoint: <strong>{rev.operating_pressure_bar} bar</strong></div>
                <div>Sensor: <strong>{rev.active_pressure_sensor}</strong></div>
                <div>ECN: <strong>{rev.governing_ecn || "None"}</strong></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

