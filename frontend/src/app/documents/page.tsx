"use client";

import { useState, useEffect } from "react";
import {
  Files,
  Search,
  Filter,
  Shield,
  Hash,
  FileText,
  Archive,
  CheckCircle2,
  AlertTriangle,
  Copy,
  Check,
  ExternalLink,
  Layers,
  RefreshCw,
} from "lucide-react";
import { api, DocumentListItem } from "@/lib/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [tierFilter, setTierFilter] = useState<number | "ALL">("ALL");
  const [typeFilter, setTypeFilter] = useState<string | "ALL">("ALL");
  const [copiedHash, setCopiedHash] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<DocumentListItem | null>(null);

  const loadDocs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err: any) {
      setError(err?.message || "Failed to load ingested document catalog.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleCopyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const getTierColor = (tier: number) => {
    switch (tier) {
      case 1:
        return "bg-purple-950/80 text-purple-300 border-purple-700/60";
      case 2:
        return "bg-blue-950/80 text-blue-300 border-blue-700/60";
      case 3:
        return "bg-amber-950/80 text-amber-300 border-amber-700/60";
      case 4:
        return "bg-orange-950/80 text-orange-300 border-orange-700/60";
      default:
        return "bg-slate-800 text-slate-400 border-slate-700";
    }
  };

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch =
      doc.filename.toLowerCase().includes(search.toLowerCase()) ||
      doc.title.toLowerCase().includes(search.toLowerCase()) ||
      doc.document_id.toLowerCase().includes(search.toLowerCase());
    const matchesTier = tierFilter === "ALL" || doc.trust_tier === tierFilter;
    const matchesType = typeFilter === "ALL" || doc.document_type.toUpperCase() === typeFilter;
    return matchesSearch && matchesTier && matchesType;
  });

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <Files className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold font-mono text-white">
              Document Registry & Cryptographic Manifest
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Complete registry of all 20 ingested files with SHA-256 hashes, trust tiers, and archival statuses.
          </p>
        </div>

        <button
          onClick={loadDocs}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-400" : ""}`} />
          Reload Registry
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
            placeholder="Search by filename, document ID, title..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Tier Filter */}
          <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs font-mono">
            <span className="text-slate-400">Trust Tier:</span>
            <select
              value={tierFilter}
              onChange={(e) => setTierFilter(e.target.value === "ALL" ? "ALL" : Number(e.target.value))}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Tiers (1–4)</option>
              <option value={1}>Tier 1 (Master / ECN)</option>
              <option value={2}>Tier 2 (Official Spec)</option>
              <option value={3}>Tier 3 (Internal Draft)</option>
              <option value={4}>Tier 4 (Training / Maint)</option>
            </select>
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs font-mono">
            <span className="text-slate-400">Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Formats</option>
              <option value="PDF">PDF</option>
              <option value="DOCX">DOCX</option>
              <option value="PPTX">PPTX</option>
              <option value="XLSX">XLSX</option>
              <option value="HTML">HTML</option>
              <option value="PNG">PNG (OCR)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Documents Table */}
      <div className="rounded-xl bg-slate-900/40 border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 font-mono uppercase text-[11px]">
              <tr>
                <th className="py-3 px-4">Doc ID & Title</th>
                <th className="py-3 px-3">Type</th>
                <th className="py-3 px-3">Revision</th>
                <th className="py-3 px-3">Trust Tier</th>
                <th className="py-3 px-4">SHA-256 Hash</th>
                <th className="py-3 px-3 text-center">Chunks</th>
                <th className="py-3 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500 font-sans">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto text-blue-400 mb-2" />
                    Loading document catalog...
                  </td>
                </tr>
              ) : filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500 font-sans">
                    No documents matched search criteria.
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => (
                  <tr
                    key={doc.document_id}
                    onClick={() => setSelectedDoc(doc)}
                    className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                  >
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-200">{doc.document_id}</div>
                      <div className="text-[11px] font-sans text-slate-400">{doc.title}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{doc.filename}</div>
                    </td>
                    <td className="py-3 px-3 text-slate-300 font-semibold">{doc.document_type}</td>
                    <td className="py-3 px-3 text-slate-300 font-semibold">{doc.revision}</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getTierColor(doc.trust_tier)}`}>
                        Tier {doc.trust_tier}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-slate-400 truncate max-w-[180px]">
                          {doc.sha256_hash}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCopyHash(doc.sha256_hash);
                          }}
                          className="p-1 rounded hover:bg-slate-700/60 text-slate-400 hover:text-slate-200 transition-colors"
                          title="Copy full 64-char SHA-256 hash"
                        >
                          {copiedHash === doc.sha256_hash ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-center text-blue-400 font-bold">{doc.chunk_count}</td>
                    <td className="py-3 px-3 text-right">
                      {doc.is_archived ? (
                        <span className="px-2 py-0.5 rounded text-[10px] bg-amber-950 text-amber-300 border border-amber-800">
                          Archived
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-800">
                          Active
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Document Detail Modal */}
      {selectedDoc && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedDoc(null)}
        >
          <div
            className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-6 space-y-4 font-mono text-xs"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">{selectedDoc.document_id}</h3>
                <p className="text-xs font-sans text-slate-300 mt-0.5">{selectedDoc.title}</p>
              </div>
              <span className={`px-2.5 py-0.5 rounded border text-[11px] font-semibold ${getTierColor(selectedDoc.trust_tier)}`}>
                Tier {selectedDoc.trust_tier}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-[11px] bg-slate-950 p-4 rounded-lg border border-slate-800/80">
              <div>
                <span className="text-slate-400">Filename:</span>
                <p className="text-slate-200 font-semibold">{selectedDoc.filename}</p>
              </div>
              <div>
                <span className="text-slate-400">System:</span>
                <p className="text-slate-200 font-semibold">{selectedDoc.system}</p>
              </div>
              <div>
                <span className="text-slate-400">Revision:</span>
                <p className="text-slate-200 font-semibold">{selectedDoc.revision}</p>
              </div>
              <div>
                <span className="text-slate-400">Type:</span>
                <p className="text-slate-200 font-semibold">{selectedDoc.document_type}</p>
              </div>
              <div className="col-span-2">
                <span className="text-slate-400">Cryptographic SHA-256:</span>
                <p className="text-blue-300 break-all select-all font-mono mt-0.5">{selectedDoc.sha256_hash}</p>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-3">
                <span className="text-slate-400">
                  Indexed Chunks: <strong className="text-white">{selectedDoc.chunk_count}</strong>
                </span>
                <a
                  href={api.getRawDocumentUrl(selectedDoc.filename)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-sans font-medium text-xs transition-colors shadow-sm"
                >
                  <span>Open Source File</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-sans font-medium text-xs transition-colors"
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

