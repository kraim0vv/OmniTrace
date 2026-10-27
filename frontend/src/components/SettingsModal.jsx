import React, { useState, useEffect } from 'react';
import { X, Settings, Shield, Key, Save, CheckCircle2 } from 'lucide-react';
import { getSettings, updateSettings } from '../services/api';

export default function SettingsModal({ isOpen, onClose }) {
  const [proxyUrl, setProxyUrl] = useState('');
  const [timeout, setTimeoutVal] = useState('8.0');
  const [hibpKey, setHibpKey] = useState('');
  const [shodanKey, setShodanKey] = useState('');
  const [vtKey, setVtKey] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      getSettings().then((s) => {
        if (s.proxy_url) setProxyUrl(s.proxy_url);
        if (s.default_timeout) setTimeoutVal(String(s.default_timeout));
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await updateSettings({
        proxy_url: proxyUrl,
        default_timeout: timeout,
        hibp_api_key: hibpKey,
        shodan_api_key: shodanKey,
        virustotal_api_key: vtKey,
      });
      setSavedSuccess(true);
      setTimeout(() => {
        setSavedSuccess(false);
        onClose();
      }, 1200);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-lg bg-zinc-950 border border-white/10 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/10 bg-zinc-900/40">
          <div className="flex items-center gap-2.5">
            <Settings className="w-4 h-4 text-white" />
            <h3 className="font-semibold text-sm text-white">
              OPSEC & Module Configuration
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-5 overflow-y-auto flex-1 flex flex-col gap-5">
          {/* OPSEC & Anonymity */}
          <div>
            <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold uppercase tracking-wider text-white font-mono">
              <Shield className="w-3.5 h-3.5" />
              <span>Proxy & Tor Anonymity</span>
            </div>
            <p className="text-[11px] text-zinc-400 mb-3 font-mono">
              Route queries through an upstream HTTP, SOCKS5, or Tor proxy to shield your investigator IP address.
            </p>

            <div className="flex flex-col gap-3">
              <div>
                <label className="text-[11px] text-zinc-300 block mb-1 font-mono">
                  Upstream Proxy URL (Optional)
                </label>
                <input
                  type="text"
                  value={proxyUrl}
                  onChange={(e) => setProxyUrl(e.target.value)}
                  placeholder="e.g. socks5://127.0.0.1:9050 or http://1.2.3.4:8080"
                  className="w-full bg-zinc-900 border border-white/10 rounded px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-white/40"
                />
              </div>

              <div>
                <label className="text-[11px] text-zinc-300 block mb-1 font-mono">
                  Timeout (Seconds)
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="2"
                  max="30"
                  value={timeout}
                  onChange={(e) => setTimeoutVal(e.target.value)}
                  className="w-full bg-zinc-900 border border-white/10 rounded px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-white/40"
                />
              </div>
            </div>
          </div>

          {/* Optional API Keys */}
          <div className="pt-4 border-t border-white/10">
            <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold uppercase tracking-wider text-zinc-200 font-mono">
              <Key className="w-3.5 h-3.5" />
              <span>Optional API Keys</span>
            </div>
            <p className="text-[11px] text-zinc-400 mb-3 font-mono">
              OmniTrace functions 100% without keys. Adding personal keys enables optional deep dataset enrichment.
            </p>

            <div className="flex flex-col gap-3">
              <div>
                <label className="text-[11px] text-zinc-300 block mb-1 font-mono">
                  HaveIBeenPwned API Key
                </label>
                <input
                  type="password"
                  value={hibpKey}
                  onChange={(e) => setHibpKey(e.target.value)}
                  placeholder="Paste HIBP key..."
                  className="w-full bg-zinc-900 border border-white/10 rounded px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-white/40"
                />
              </div>

              <div>
                <label className="text-[11px] text-zinc-300 block mb-1 font-mono">
                  Shodan API Key
                </label>
                <input
                  type="password"
                  value={shodanKey}
                  onChange={(e) => setShodanKey(e.target.value)}
                  placeholder="Paste Shodan key..."
                  className="w-full bg-zinc-900 border border-white/10 rounded px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-white/40"
                />
              </div>

              <div>
                <label className="text-[11px] text-zinc-300 block mb-1 font-mono">
                  VirusTotal API Key
                </label>
                <input
                  type="password"
                  value={vtKey}
                  onChange={(e) => setVtKey(e.target.value)}
                  placeholder="Paste VirusTotal key..."
                  className="w-full bg-zinc-900 border border-white/10 rounded px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-white/40"
                />
              </div>
            </div>
          </div>

          {/* Footer Save */}
          <div className="pt-4 border-t border-white/10 flex items-center justify-between">
            <span className="text-[11px] text-zinc-500 font-mono">
              Stored locally on host
            </span>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2 rounded bg-white hover:bg-zinc-200 text-zinc-950 font-bold text-xs transition-colors disabled:opacity-50"
            >
              {savedSuccess ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Saved</span>
                </>
              ) : (
                <>
                  <Save className="w-3.5 h-3.5" />
                  <span>Save Configuration</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
