"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Network,
  Info,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  ExternalLink,
  Layers,
  MapPin,
  Cpu,
} from "lucide-react";
import { api, DiagramResponse, DiagramElement, DiagramConnection } from "@/lib/api";

export default function HydraulicDiagramPage() {
  const [diagram, setDiagram] = useState<DiagramResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedElement, setSelectedElement] = useState<DiagramElement | null>(null);
  const [hoveredConn, setHoveredConn] = useState<DiagramConnection | null>(null);

  const loadDiagram = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDiagramData();
      setDiagram(data);
      if (data.elements.length > 0) {
        setSelectedElement(data.elements[0]);
      }
    } catch (err: any) {
      setError(err?.message || "Failed to load diagram topology");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDiagram();
  }, []);

  // Element bounds calculation helper
  const getBoxProps = (bbox: number[]) => {
    const [x0, y0, x1, y1] = bbox;
    return {
      x: x0,
      y: y0,
      width: x1 - x0,
      height: y1 - y0,
    };
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <Network className="w-5 h-5 text-blue-400" />
            <h1 className="text-xl font-bold font-mono text-white">
              Hydraulic Schematic Topology Viewer
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic vector rendering of AEG-DWG-H01 extracted from system_diagram_hydraulic.pdf.
          </p>
        </div>

        <button
          onClick={loadDiagram}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-blue-400" : ""}`} />
          Reload Topology
        </button>
      </div>

      {/* Schematic Topology Callout */}
      <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 text-xs space-y-2">
        <div className="flex items-center gap-2 font-mono font-bold text-purple-300">
          <ShieldAlert className="w-4 h-4 text-purple-400" />
          EXTRACTED SCHEMATIC GROUND TRUTH (NO INVENTED CONNECTIONS)
        </div>
        <p className="text-slate-300 leading-relaxed font-sans">
          The vector geometry parser extracts exact bounding boxes and stroke colors from the PDF.
          <strong> PLC-03</strong> maintains direct purple control/signal lines only to <strong>PS-04A</strong> (sensor transducer) and <strong>IV-21</strong> (valve solenoid). The <strong>Auxiliary Reservoir</strong> connects solely to the Main Reservoir via a tan interconnect feed line.
        </p>
      </div>

      {/* Main Layout: SVG Canvas + Element Inspector Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Interactive SVG Diagram */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-slate-950 border border-slate-800 shadow-2xl flex flex-col items-center justify-center relative overflow-hidden min-h-[580px]">
          {loading ? (
            <div className="py-24 text-center text-slate-400 font-mono">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-400 mb-2" />
              Rendering vector schematic...
            </div>
          ) : diagram ? (
            <div className="w-full h-full flex flex-col items-center justify-center">
              <svg
                viewBox="50 170 500 400"
                className="w-full max-h-[520px] select-none"
              >
                {/* SVG Definitions: Marker arrows for control & fluid */}
                <defs>
                  <marker
                    id="arrow-purple"
                    viewBox="0 0 10 10"
                    refX="6"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#c084fc" />
                  </marker>
                  <marker
                    id="arrow-grey"
                    viewBox="0 0 10 10"
                    refX="6"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#94a3b8" />
                  </marker>
                  <marker
                    id="arrow-tan"
                    viewBox="0 0 10 10"
                    refX="6"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#f59e0b" />
                  </marker>
                </defs>

                {/* 1. Draw Vector Connection Paths */}
                {/* PLC-03 to PS-04A: Purple Control Line */}
                <path
                  d="M 230.4 231.8 L 130 231.8 L 130 302.4"
                  fill="none"
                  stroke="#c084fc"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="transition-all hover:stroke-purple-300 cursor-pointer"
                />

                {/* PLC-03 to IV-21: Purple Control Line */}
                <path
                  d="M 374.4 231.8 L 446.4 231.8 L 446.4 302.4"
                  fill="none"
                  stroke="#c084fc"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="transition-all hover:stroke-purple-300 cursor-pointer"
                />

                {/* Central grey fluid lines: HPU <-> Main Reservoir */}
                <path
                  d="M 302.4 345.6 L 302.4 403.2"
                  fill="none"
                  stroke="#94a3b8"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  className="transition-all hover:stroke-white cursor-pointer"
                />

                {/* Main Reservoir <-> Press Circuit */}
                <path
                  d="M 302.4 446.4 L 302.4 504.0"
                  fill="none"
                  stroke="#94a3b8"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  className="transition-all hover:stroke-white cursor-pointer"
                />

                {/* PS-04A <-> HPU fluid tap line */}
                <line
                  x1="187.2"
                  y1="324.0"
                  x2="230.4"
                  y2="324.0"
                  stroke="#64748b"
                  strokeWidth="2.5"
                  strokeDasharray="4 2"
                />

                {/* HPU <-> IV-21 discharge tap line */}
                <line
                  x1="374.4"
                  y1="324.0"
                  x2="388.8"
                  y2="324.0"
                  stroke="#64748b"
                  strokeWidth="2.5"
                  strokeDasharray="4 2"
                />

                {/* Tan Reservoir Interconnect Line: Main Reservoir <-> Auxiliary Reservoir */}
                <path
                  d="M 374.4 424.8 L 410.4 424.8"
                  fill="none"
                  stroke="#f59e0b"
                  strokeWidth="4"
                  strokeLinecap="round"
                  className="transition-all hover:stroke-amber-300 cursor-pointer"
                />

                {/* 2. Draw Component Rectangles & Labels */}
                {diagram.elements.map((el) => {
                  const b = getBoxProps(el.bbox);
                  const isSelected = selectedElement?.id === el.id;
                  return (
                    <g
                      key={el.id}
                      onClick={() => setSelectedElement(el)}
                      className="cursor-pointer group"
                    >
                      {/* Bounding Box */}
                      <rect
                        x={b.x}
                        y={b.y}
                        width={b.width}
                        height={b.height}
                        rx="6"
                        fill={isSelected ? "#1e293b" : el.fill_color}
                        stroke={isSelected ? "#38bdf8" : el.border_color}
                        strokeWidth={isSelected ? "2.5" : "1.5"}
                        className="transition-all group-hover:stroke-blue-400 group-hover:brightness-125"
                      />

                      {/* Label Text */}
                      <text
                        x={b.x + b.width / 2}
                        y={b.y + b.height / 2 - (el.sublabel ? 4 : 0)}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        fill={isSelected ? "#38bdf8" : "#f8fafc"}
                        fontSize="12"
                        fontWeight="bold"
                        fontFamily="monospace"
                        className="transition-colors pointer-events-none"
                      >
                        {el.label}
                      </text>

                      {/* Sublabel Text */}
                      {el.sublabel && (
                        <text
                          x={b.x + b.width / 2}
                          y={b.y + b.height / 2 + 12}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill="#94a3b8"
                          fontSize="9"
                          fontFamily="sans-serif"
                          className="pointer-events-none"
                        >
                          {el.sublabel}
                        </text>
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>
          ) : (
            <div className="text-rose-400 font-mono text-xs">{error || "Failed to load"}</div>
          )}

          {/* Canvas Footnote */}
          <div className="absolute bottom-3 left-4 text-[10px] text-slate-400 font-mono">
            Source: system_diagram_hydraulic.pdf • AEG-DWG-H01 Vector Topology
          </div>
        </div>

        {/* Right 1 Col: Element Inspector & Legend */}
        <div className="space-y-6">
          {/* Selected Element Detail Card */}
          <div className="p-6 rounded-xl bg-slate-900/50 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
                Component Inspector
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-mono">
                {selectedElement?.type || "None"}
              </span>
            </div>

            {selectedElement ? (
              <div className="space-y-3 font-mono text-xs">
                <div>
                  <h3 className="text-lg font-bold text-white">{selectedElement.label}</h3>
                  <p className="text-xs text-slate-400 font-sans mt-0.5">{selectedElement.sublabel}</p>
                </div>

                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Canonical ID:</span>
                    <strong className="text-blue-400">{selectedElement.id}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Schematic BBox:</span>
                    <span className="text-slate-300">
                      [{selectedElement.bbox.map((v) => v.toFixed(1)).join(", ")}]
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Box Dimensions:</span>
                    <span className="text-slate-300">
                      {(selectedElement.bbox[2] - selectedElement.bbox[0]).toFixed(0)} &times;{" "}
                      {(selectedElement.bbox[3] - selectedElement.bbox[1]).toFixed(0)} pt
                    </span>
                  </div>
                </div>

                {/* Direct Connections from this Element */}
                <div className="space-y-2 pt-2">
                  <span className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider block">
                    Schematic Connectivity:
                  </span>
                  {selectedElement.id === "PLC-03" && (
                    <div className="space-y-1.5 text-[11px]">
                      <div className="p-2 rounded bg-purple-950/60 border border-purple-800/60 text-purple-200">
                        &bull; <strong>PS-04A:</strong> Direct solid purple control/signal line (senses pressure).
                      </div>
                      <div className="p-2 rounded bg-purple-950/60 border border-purple-800/60 text-purple-200">
                        &bull; <strong>IV-21:</strong> Direct solid purple control line (solenoid driver).
                      </div>
                    </div>
                  )}
                  {selectedElement.id === "PS-04A" && (
                    <div className="p-2 rounded bg-purple-950/60 border border-purple-800/60 text-purple-200 text-[11px]">
                      &bull; Receives signal/control from <strong>PLC-03</strong>; senses pressure at HPU discharge.
                    </div>
                  )}
                  {selectedElement.id === "IV-21" && (
                    <div className="p-2 rounded bg-purple-950/60 border border-purple-800/60 text-purple-200 text-[11px]">
                      &bull; Driven directly by <strong>PLC-03</strong>; isolates HPU supply to Press Circuit.
                    </div>
                  )}
                  {selectedElement.id === "AUX_RESERVOIR" && (
                    <div className="p-2 rounded bg-amber-950/60 border border-amber-800/60 text-amber-200 text-[11px]">
                      &bull; Interconnects only with <strong>Main Reservoir</strong> via tan top-up line.
                    </div>
                  )}
                  {selectedElement.id === "MAIN_RESERVOIR" && (
                    <div className="space-y-1.5 text-[11px]">
                      <div className="p-2 rounded bg-slate-950 border border-slate-800 text-slate-300">
                        &bull; Suction connection to <strong>HPU</strong> pump via grey line.
                      </div>
                      <div className="p-2 rounded bg-amber-950/60 border border-amber-800/60 text-amber-200">
                        &bull; Top-up interconnect to <strong>Auxiliary Reservoir</strong> via tan line.
                      </div>
                    </div>
                  )}
                </div>

                <div className="pt-2">
                  <Link
                    href={`/components`}
                    className="inline-flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 font-sans"
                  >
                    View in Canonical Component Catalog
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ) : (
              <p className="text-slate-400 text-xs">Select a component on the diagram.</p>
            )}
          </div>

          {/* Color-Coded Schematic Legend */}
          <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800 space-y-3 font-mono text-xs">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
              Vector Color Legend
            </span>
            <div className="space-y-2">
              <div className="flex items-center gap-2.5 p-2 rounded bg-slate-950 border border-slate-800">
                <span className="w-4 h-1.5 rounded bg-[#c084fc]" />
                <div className="text-[11px] font-sans">
                  <strong className="text-purple-300 font-mono">Solid Purple:</strong> Control/signal to PLC-03
                </div>
              </div>
              <div className="flex items-center gap-2.5 p-2 rounded bg-slate-950 border border-slate-800">
                <span className="w-4 h-1.5 rounded bg-[#94a3b8]" />
                <div className="text-[11px] font-sans">
                  <strong className="text-slate-300 font-mono">Solid Grey:</strong> Hydraulic fluid path
                </div>
              </div>
              <div className="flex items-center gap-2.5 p-2 rounded bg-slate-950 border border-slate-800">
                <span className="w-4 h-1.5 rounded bg-[#f59e0b]" />
                <div className="text-[11px] font-sans">
                  <strong className="text-amber-300 font-mono">Solid Tan:</strong> Reservoir top-up interconnect
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

