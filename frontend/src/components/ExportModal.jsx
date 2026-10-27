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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-md bg-zinc-950 border border-white/10 rounded-xl shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/10 bg-zinc-900/40">
          <div className="flex items-center gap-2.5">
            <Download className="w-4 h-4 text-white" />
            <h3 className="font-semibold text-sm text-white">Export Forensic Dossier</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5">
          <div className="mb-4 text-xs text-zinc-400 font-mono">
            Target: <strong className="text-white">{target}</strong>
          </div>

          <div className="flex flex-col gap-2.5">
            {/* HTML Report */}
            <button
              onClick={() => handleDownload('html')}
              className="flex items-center justify-between p-3 rounded-lg bg-zinc-900 border border-white/10 hover:border-white/30 text-left transition-all group"
            >
              <div className="flex items-center gap-3">
                <Globe className="w-4 h-4 text-zinc-300 group-hover:text-white" />
                <div>
                  <div className="text-xs font-semibold text-white">
                    HTML Report
                  </div>
                  <div className="text-[11px] text-zinc-400 font-mono">
                    Printable standalone dossier
                  </div>
                </div>
              </div>
              <Download className="w-3.5 h-3.5 text-zinc-500 group-hover:text-white" />
            </button>

            {/* JSON Dump */}
            <button
              onClick={() => handleDownload('json')}
              className="flex items-center justify-between p-3 rounded-lg bg-zinc-900 border border-white/10 hover:border-white/30 text-left transition-all group"
            >
              <div className="flex items-center gap-3">
                <FileCode className="w-4 h-4 text-zinc-300 group-hover:text-white" />
                <div>
                  <div className="text-xs font-semibold text-white">
                    JSON Structured Data
                  </div>
                  <div className="text-[11px] text-zinc-400 font-mono">
                    Full payload + SHA-256 fingerprint
                  </div>
                </div>
              </div>
              <Download className="w-3.5 h-3.5 text-zinc-500 group-hover:text-white" />
            </button>

            {/* CSV */}
            <button
              onClick={() => handleDownload('csv')}
              className="flex items-center justify-between p-3 rounded-lg bg-zinc-900 border border-white/10 hover:border-white/30 text-left transition-all group"
            >
              <div className="flex items-center gap-3">
                <FileSpreadsheet className="w-4 h-4 text-zinc-300 group-hover:text-white" />
                <div>
                  <div className="text-xs font-semibold text-white">
                    CSV Table
                  </div>
                  <div className="text-[11px] text-zinc-400 font-mono">
                    Import to Excel / Maltego
                  </div>
                </div>
              </div>
              <Download className="w-3.5 h-3.5 text-zinc-500 group-hover:text-white" />
            </button>
          </div>

          <div className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2 text-[10px] text-zinc-500 font-mono">
            <ShieldCheck className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
            <span>Chain of custody cryptographic integrity maintained locally.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
