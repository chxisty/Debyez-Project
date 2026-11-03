"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  MessageSquareText,
  Files,
  Cpu,
  GitCompare,
  FileSearch,
  Network,
  CheckCircle2,
  ShieldAlert,
  Activity,
  ChevronRight,
  Database,
} from "lucide-react";
import { api, HealthResponse } from "@/lib/api";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "AI Assistant", icon: MessageSquareText },
  { href: "/documents", label: "Document Registry", icon: Files },
  { href: "/components", label: "Component Catalog", icon: Cpu },
  { href: "/revisions", label: "Revision Compare", icon: GitCompare },
  { href: "/diagram", label: "Hydraulic Diagram", icon: Network },
  { href: "/evidence", label: "Evidence Inspector", icon: FileSearch },
  { href: "/evaluation", label: "23-Q Benchmark", icon: CheckCircle2 },
];

export function Sidebar() {
  const pathname = usePathname();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    const checkHealth = async () => {
      try {
        const res = await api.getHealth();
        if (mounted) {
          setHealth(res);
          setIsOnline(true);
        }
      } catch (err) {
        if (mounted) {
          setIsOnline(false);
        }
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <aside className="w-64 bg-[#070b14] border-r border-slate-800 flex flex-col justify-between shrink-0 h-screen sticky top-0 select-none">
      <div>
        {/* Brand / Title Header */}
        <div className="p-5 border-b border-slate-800/80 bg-slate-950/40">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-lg shadow-blue-500/20 border border-blue-400/30">
              <Activity className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-slate-100 tracking-wider text-base font-mono">AEGIS-7</span>
                <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-300 border border-blue-700/50">
                  HCS
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Debyez Technologies</p>
            </div>
          </div>
        </div>

        {/* Navigation Section */}
        <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-230px)]">
          <div className="px-3 py-2 text-[10px] font-semibold tracking-wider uppercase text-slate-400">
            Operations & Analytics
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all group ${
                  isActive
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm shadow-blue-500/10 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 transition-colors ${
                      isActive ? "text-blue-400" : "text-slate-400 group-hover:text-slate-200"
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {isActive && <ChevronRight className="w-3.5 h-3.5 text-blue-400" />}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer / System Status Pill */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/60 space-y-2">
        <div className="flex items-center justify-between text-[11px] font-mono">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-slate-400" />
            Backend API
          </span>
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                isOnline ? "bg-emerald-400 shadow-sm shadow-emerald-400/50" : "bg-rose-500 animate-ping"
              }`}
            />
            <span className={isOnline ? "text-emerald-400 font-semibold" : "text-rose-400 font-semibold"}>
              {isOnline ? "ONLINE :8000" : "OFFLINE"}
            </span>
          </div>
        </div>

        {health && (
          <div className="text-[10px] font-mono text-slate-400 bg-slate-900/80 p-2 rounded border border-slate-800 space-y-1">
            <div className="flex justify-between">
              <span>DB Documents:</span>
              <span className="text-slate-300 font-semibold">{health.database.documents} files</span>
            </div>
            <div className="flex justify-between">
              <span>Embeddings:</span>
              <span className="text-blue-300 font-semibold">{health.retrieval_engine.indexed_chunks} chunks</span>
            </div>
            <div className="flex justify-between">
              <span>Target Baseline:</span>
              <span className="text-emerald-300 font-semibold">SW &ge; 3.2</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
