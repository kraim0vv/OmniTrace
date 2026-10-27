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
  Globe
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
      className={`mono-panel rounded-lg p-3.5 transition-all border ${
        isFound
          ? 'border-white/25 bg-white/[0.03] hover:border-white/40'
          : isError
          ? 'border-white/10 bg-zinc-950/60'
          : 'border-white/5 bg-zinc-950/40 opacity-75 hover:opacity-100'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Source & Title */}
        <div className="flex items-start gap-3 min-w-0">
          {/* Status Indicator */}
          <div className="mt-0.5 shrink-0">
            {isFound ? (
              <span className="flex items-center justify-center w-6 h-6 rounded-md bg-white text-zinc-950">
                <Check className="w-3.5 h-3.5 stroke-[2.5]" />
              </span>
            ) : isError ? (
              <span className="flex items-center justify-center w-6 h-6 rounded-md bg-zinc-800 text-zinc-400">
                <AlertCircle className="w-3.5 h-3.5" />
              </span>
            ) : isInfo ? (
              <span className="flex items-center justify-center w-6 h-6 rounded-md bg-zinc-800 text-zinc-300">
                <Globe className="w-3.5 h-3.5" />
              </span>
            ) : (
              <span className="flex items-center justify-center w-6 h-6 rounded-md bg-zinc-900 text-zinc-600 border border-white/5">
                <XCircle className="w-3.5 h-3.5" />
              </span>
            )}
          </div>

          {/* Details Header */}
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="font-semibold text-xs tracking-tight text-white font-mono">
                {finding.source}
              </span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-zinc-800 border border-white/5 text-zinc-400 font-mono">
                {finding.category}
              </span>
              {elapsedMs && (
                <span className="text-[10px] text-zinc-500 flex items-center gap-0.5 font-mono">
                  <Clock className="w-2.5 h-2.5" />
                  {elapsedMs}ms
                </span>
              )}
            </div>

            {finding.title && (
              <h4 className="text-xs font-medium text-zinc-200 truncate">
                {finding.title}
              </h4>
            )}

            {finding.description && (
              <p className="text-[11px] text-zinc-400 mt-0.5 line-clamp-2">
                {finding.description}
              </p>
            )}

            {/* Subdomains preview */}
            {finding.metadata?.subdomains && (
              <div className="mt-2 text-xs">
                <span className="text-zinc-400 text-[11px] font-mono">Discovered Subdomains ({finding.metadata.count}):</span>
                <div className="flex flex-wrap gap-1.5 mt-1 max-h-24 overflow-y-auto">
                  {finding.metadata.subdomains.slice(0, 16).map((sub, idx) => (
                    <span key={idx} className="font-mono text-[10px] bg-zinc-900 px-1.5 py-0.5 rounded text-zinc-300 border border-white/10">
                      {sub}
                    </span>
                  ))}
                  {finding.metadata.subdomains.length > 16 && (
                    <span className="text-[10px] text-zinc-500 self-center font-mono">
                      +{finding.metadata.subdomains.length - 16} more
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
                className="p-1.5 rounded-md bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-white/5 transition-colors"
                title="Copy URL"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-white" /> : <Copy className="w-3.5 h-3.5" />}
              </button>

              <a
                href={finding.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-md bg-white hover:bg-zinc-200 text-zinc-950 text-xs font-semibold transition-colors"
              >
                <span>Open</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </>
          )}

          {finding.metadata && Object.keys(finding.metadata).length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1.5 rounded-md bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-white/5 transition-colors"
              title="Raw Metadata"
            >
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      </div>

      {/* Expanded Metadata JSON Viewer */}
      {expanded && (
        <div className="mt-3 pt-3 border-t border-white/5">
          <div className="text-[11px] font-mono text-zinc-400 bg-black p-2.5 rounded border border-white/5 overflow-x-auto">
            <pre>{JSON.stringify(finding.metadata, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
