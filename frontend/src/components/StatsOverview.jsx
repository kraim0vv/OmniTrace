import React from 'react';
import { Layers, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

export default function StatsOverview({ summary, isScanning }) {
  if (!summary && !isScanning) return null;

  const total = summary?.total_checks || 0;
  const found = summary?.found_count || 0;
  const notFound = summary?.not_found_count || 0;
  const errors = summary?.error_count || 0;

  return (
    <div className="w-full max-w-4xl mx-auto mb-6">
      {/* Top Progress bar if scan is running */}
      {isScanning && (
        <div className="w-full bg-zinc-900 rounded-full h-1 mb-4 overflow-hidden border border-white/10">
          <div className="bg-white h-1 rounded-full animate-pulse w-full"></div>
        </div>
      )}

      {/* Grid of Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        {/* Total Checks */}
        <div className="mono-panel p-3.5 rounded-lg border border-white/10 flex items-center justify-between">
          <div>
            <div className="text-xl font-bold font-mono text-white">{total}</div>
            <div className="text-[10px] text-zinc-400 uppercase tracking-wider font-mono">
              Total Checks
            </div>
          </div>
          <Layers className="w-4 h-4 text-zinc-500" />
        </div>

        {/* Confirmed Finds */}
        <div className="mono-panel p-3.5 rounded-lg border border-white/20 bg-white/[0.03] flex items-center justify-between">
          <div>
            <div className="text-xl font-bold font-mono text-white">{found}</div>
            <div className="text-[10px] text-zinc-300 uppercase tracking-wider font-mono">
              Confirmed Finds
            </div>
          </div>
          <CheckCircle2 className="w-4 h-4 text-white" />
        </div>

        {/* Not Found */}
        <div className="mono-panel p-3.5 rounded-lg border border-white/5 flex items-center justify-between">
          <div>
            <div className="text-xl font-bold font-mono text-zinc-400">{notFound}</div>
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-mono">
              Not Found
            </div>
          </div>
          <XCircle className="w-4 h-4 text-zinc-600" />
        </div>

        {/* Errors / Limits */}
        <div className="mono-panel p-3.5 rounded-lg border border-white/5 flex items-center justify-between">
          <div>
            <div className="text-xl font-bold font-mono text-zinc-300">{errors}</div>
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider font-mono">
              Errors / Skipped
            </div>
          </div>
          <AlertTriangle className="w-4 h-4 text-zinc-500" />
        </div>
      </div>
    </div>
  );
}
