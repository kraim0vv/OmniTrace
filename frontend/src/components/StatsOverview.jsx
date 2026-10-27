import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Layers, Clock } from 'lucide-react';

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
        <div className="w-full bg-slate-900 rounded-full h-1.5 mb-4 overflow-hidden border border-cyan-500/30">
          <div className="bg-gradient-to-r from-cyan-500 via-sky-400 to-indigo-500 h-1.5 rounded-full animate-pulse w-full"></div>
        </div>
      )}

      {/* Grid of Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Total Checks */}
        <div className="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xl font-bold font-mono text-slate-100">{total}</div>
            <div className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
              Total Checks
            </div>
          </div>
        </div>

        {/* Confirmed Finds */}
        <div className="glass-panel p-3.5 rounded-xl border border-emerald-500/30 bg-emerald-950/10 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/20 border border-emerald-500/30 text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xl font-bold font-mono text-emerald-400">{found}</div>
            <div className="text-[11px] text-emerald-300 uppercase tracking-wider font-semibold">
              Confirmed Finds
            </div>
          </div>
        </div>

        {/* Not Found */}
        <div className="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-slate-800 text-slate-400">
            <XCircle className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xl font-bold font-mono text-slate-300">{notFound}</div>
            <div className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">
              Not Found
            </div>
          </div>
        </div>

        {/* Errors / Limits */}
        <div className="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xl font-bold font-mono text-rose-400">{errors}</div>
            <div className="text-[11px] text-rose-300 uppercase tracking-wider font-semibold">
              Errors / Limits
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
