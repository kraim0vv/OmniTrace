import React from 'react';
import { X, Download, FileCode, FileSpreadsheet, Globe, ShieldCheck } from 'lucide-react';
import { getExportUrl } from '../services/api';

export default function ExportModal({ isOpen, onClose, scanId, target }) {
  if (!isOpen || !scanId) return null;

  const handleDownload = (format) => {
    const url = getExportUrl(scanId, format);
    window.open(url, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <Download className="w-5 h-5 text-cyan-400" />
            <h3 className="font-bold text-base text-slate-100">Export Intelligence Dossier</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6">
          <div className="mb-4 text-xs text-slate-400">
            Exporting verified findings for <strong className="text-slate-200 font-mono">{target}</strong>.
            All formats include verified timestamps and source attribution.
          </div>

          <div className="flex flex-col gap-3">
            {/* HTML / Print Dossier */}
            <button
              onClick={() => handleDownload('html')}
              className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-cyan-500/40 hover:bg-cyan-950/20 text-left transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  <Globe className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-100 group-hover:text-cyan-300">
                    Standalone HTML Report
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Printable, self-contained executive forensic report
                  </div>
                </div>
              </div>
              <Download className="w-4 h-4 text-slate-500 group-hover:text-cyan-400" />
            </button>

            {/* JSON Dump */}
            <button
              onClick={() => handleDownload('json')}
              className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-cyan-500/40 hover:bg-cyan-950/20 text-left transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  <FileCode className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-100 group-hover:text-cyan-300">
                    JSON Structured Data
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Complete machine-readable payload + SHA-256 hash
                  </div>
                </div>
              </div>
              <Download className="w-4 h-4 text-slate-500 group-hover:text-cyan-400" />
            </button>

            {/* CSV Spreadsheet */}
            <button
              onClick={() => handleDownload('csv')}
              className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-cyan-500/40 hover:bg-cyan-950/20 text-left transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-100 group-hover:text-cyan-300">
                    CSV Spreadsheet
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Import directly to Excel, Google Sheets, or Maltego
                  </div>
                </div>
              </div>
              <Download className="w-4 h-4 text-slate-500 group-hover:text-cyan-400" />
            </button>
          </div>

          <div className="mt-5 pt-3 border-t border-slate-800 flex items-center gap-2 text-[11px] text-slate-500 font-mono">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Forensic chain of custody maintained locally. No third-party data tracking.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
