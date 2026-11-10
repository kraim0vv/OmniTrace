import React from 'react';
import { X, Download, FileCode, FileSpreadsheet, Globe, ShieldCheck } from 'lucide-react';
import { getExportUrl } from '../services/api';
import { useI18n } from '../i18n';

export default function ExportModal({ isOpen, onClose, scanId, target }) {
  const { t } = useI18n();
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
            <h3 className="font-semibold text-sm text-white">{t('export.title')}</h3>
          </div>
          <button
            onClick={onClose}
            title={t('export.close')}
            aria-label={t('export.close')}
            className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5">
          <div className="mb-4 text-xs text-zinc-400 font-mono">
            {t('export.target')} <strong className="text-white">{target}</strong>
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
                    {t('export.htmlTitle')}
                  </div>
                  <div className="text-[11px] text-zinc-400 font-mono">
                    {t('export.htmlDesc')}
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
                    {t('export.jsonTitle')}
                  </div>
                  <div className="text-[11px] text-zinc-400 font-mono">
                    {t('export.jsonDesc')}
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
                    {t('export.csvTitle')}
                  </div>
                  <div className="text-[11px] text-zinc-400 font-mono">
                    {t('export.csvDesc')}
                  </div>
                </div>
              </div>
              <Download className="w-3.5 h-3.5 text-zinc-500 group-hover:text-white" />
            </button>
          </div>

          <div className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2 text-[10px] text-zinc-500 font-mono">
            <ShieldCheck className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
            <span>{t('export.custody')}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
