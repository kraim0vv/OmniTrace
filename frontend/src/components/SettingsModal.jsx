import React, { useState, useEffect } from 'react';
import { X, Settings, Shield, Key, Network, Save, CheckCircle2, Lock } from 'lucide-react';
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <Settings className="w-5 h-5 text-cyan-400" />
            <h3 className="font-bold text-base text-slate-100">
              OPSEC, Proxies & Module Keys
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto flex-1 flex flex-col gap-5">
          {/* OPSEC & Anonymity Section */}
          <div>
            <div className="flex items-center gap-2 mb-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
              <Shield className="w-4 h-4" />
              <span>Network OPSEC & Proxy Routing</span>
            </div>
            <p className="text-xs text-slate-400 mb-3">
              Route all investigative traffic through an upstream HTTP, SOCKS5, or Tor proxy to protect your investigator IP address.
            </p>

            <div className="flex flex-col gap-3">
              <div>
                <label className="text-xs text-slate-300 block mb-1">
                  Proxy URL (Optional)
                </label>
                <input
                  type="text"
                  value={proxyUrl}
                  onChange={(e) => setProxyUrl(e.target.value)}
                  placeholder="e.g. socks5://127.0.0.1:9050 or http://user:pass@proxy:8080"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 block mb-1">
                  Request Timeout (Seconds)
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="2"
                  max="30"
                  value={timeout}
                  onChange={(e) => setTimeoutVal(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>

          {/* Optional API Keys Section */}
          <div className="pt-4 border-t border-slate-800">
            <div className="flex items-center gap-2 mb-2 text-xs font-semibold uppercase tracking-wider text-purple-400">
              <Key className="w-4 h-4" />
              <span>Optional Deep-Scan API Keys</span>
            </div>
            <p className="text-xs text-slate-400 mb-3">
              OmniTrace works 100% out of the box with zero keys. Adding optional personal keys unlocks deeper breach and infrastructure datasets.
            </p>

            <div className="flex flex-col gap-3">
              <div>
                <label className="text-xs text-slate-300 block mb-1">
                  HaveIBeenPwned API Key
                </label>
                <input
                  type="password"
                  value={hibpKey}
                  onChange={(e) => setHibpKey(e.target.value)}
                  placeholder="Paste HIBP key..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 block mb-1">
                  Shodan API Key
                </label>
                <input
                  type="password"
                  value={shodanKey}
                  onChange={(e) => setShodanKey(e.target.value)}
                  placeholder="Paste Shodan key..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 block mb-1">
                  VirusTotal API Key
                </label>
                <input
                  type="password"
                  value={vtKey}
                  onChange={(e) => setVtKey(e.target.value)}
                  placeholder="Paste VirusTotal key..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>

          {/* Footer Save */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
            <span className="text-[11px] text-slate-500 font-mono">
              Stored locally on your machine
            </span>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs shadow-lg transition-colors disabled:opacity-50"
            >
              {savedSuccess ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-950" />
                  <span>Saved!</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
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
