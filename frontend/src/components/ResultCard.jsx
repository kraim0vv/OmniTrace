import React, { useState } from 'react';
import { 
  ExternalLink, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  Clock, 
  Copy, 
  Check, 
  ChevronDown, 
  ChevronUp,
  ShieldAlert,
  Globe,
  Tag
} from 'lucide-react';

export default function ResultCard({ finding }) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const isFound = finding.status === 'found';
  const isError = finding.status === 'error' || finding.status === 'rate_limited';
  const isInfo = finding.status === 'info';

  const copyUrl = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const elapsedMs = finding.metadata?.elapsed_ms;

  return (
    <div
      className={`glass-panel rounded-xl p-4 transition-all duration-200 border ${
        isFound
          ? 'border-emerald-500/30 bg-emerald-950/10 hover:border-emerald-500/50 hover:shadow-lg hover:shadow-emerald-950/30'
          : isError
          ? 'border-rose-900/40 bg-rose-950/5 hover:border-rose-800/60'
          : 'border-slate-800/80 bg-slate-900/40 hover:border-slate-700/80'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Source & Title */}
        <div className="flex items-start gap-3 min-w-0">
          {/* Status Icon */}
          <div className="mt-0.5">
            {isFound ? (
              <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <CheckCircle2 className="w-4 h-4" />
              </span>
            ) : isError ? (
              <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30">
                <AlertCircle className="w-4 h-4" />
              </span>
            ) : isInfo ? (
              <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                <Globe className="w-4 h-4" />
              </span>
            ) : (
              <span className="flex items-center justify-center w-7 h-7 rounded-lg bg-slate-800 text-slate-500">
                <XCircle className="w-4 h-4" />
              </span>
            )}
          </div>

          {/* Details Header */}
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="font-bold text-sm text-slate-100">{finding.source}</span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 font-medium">
                {finding.category}
              </span>
              {elapsedMs && (
                <span className="text-[10px] text-slate-500 flex items-center gap-0.5 font-mono">
                  <Clock className="w-2.5 h-2.5" />
                  {elapsedMs}ms
                </span>
              )}
            </div>

            {finding.title && (
              <h4 className="text-sm font-medium text-slate-200 truncate">
                {finding.title}
              </h4>
            )}

            {finding.description && (
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                {finding.description}
              </p>
            )}

            {/* Subdomains / Special list preview */}
            {finding.metadata?.subdomains && (
              <div className="mt-2 text-xs">
                <span className="text-slate-400 font-semibold">Subdomains Sample:</span>
                <div className="flex flex-wrap gap-1.5 mt-1 max-h-24 overflow-y-auto">
                  {finding.metadata.subdomains.slice(0, 15).map((sub, idx) => (
                    <span key={idx} className="font-mono text-[11px] bg-slate-800 px-2 py-0.5 rounded text-cyan-300 border border-slate-700">
                      {sub}
                    </span>
                  ))}
                  {finding.metadata.subdomains.length > 15 && (
                    <span className="text-[11px] text-slate-500 self-center">
                      +{finding.metadata.subdomains.length - 15} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5 shrink-0">
          {finding.url && (
            <>
              <button
                onClick={() => copyUrl(finding.url)}
                className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
                title="Copy URL"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>

              <a
                href={finding.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-medium transition-colors"
              >
                <span>Open</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </>
          )}

          {finding.metadata && Object.keys(finding.metadata).length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
              title="Toggle Raw Metadata"
            >
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      </div>

      {/* Expanded Metadata JSON Viewer */}
      {expanded && (
        <div className="mt-3 pt-3 border-t border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 bg-slate-950/80 p-2.5 rounded-lg border border-slate-800/80 overflow-x-auto">
            <pre>{JSON.stringify(finding.metadata, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
