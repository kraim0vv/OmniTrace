import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  Sparkles, 
  SlidersHorizontal, 
  CheckCircle2, 
  AlertCircle, 
  StopCircle, 
  User, 
  Mail, 
  Globe, 
  Radio, 
  Phone, 
  Key,
  X
} from 'lucide-react';
import { detectEntity } from '../services/api';

const TYPE_ICONS = {
  username: <User className="w-3.5 h-3.5 text-sky-400" />,
  email: <Mail className="w-3.5 h-3.5 text-purple-400" />,
  domain: <Globe className="w-3.5 h-3.5 text-emerald-400" />,
  ip: <Radio className="w-3.5 h-3.5 text-amber-400" />,
  phone: <Phone className="w-3.5 h-3.5 text-rose-400" />,
  hash: <Key className="w-3.5 h-3.5 text-cyan-400" />,
  unknown: <Search className="w-3.5 h-3.5 text-slate-400" />,
};

const PRESETS = [
  { label: 'Username', value: 'torvalds' },
  { label: 'Email', value: 'support@github.com' },
  { label: 'Domain', value: 'cloudflare.com' },
  { label: 'IP', value: '8.8.8.8' },
  { label: 'Phone', value: '+14155552671' },
];

export default function SmartSearch({ 
  onStartScan, 
  onStopScan, 
  isScanning, 
  availableModules = [] 
}) {
  const [query, setQuery] = useState('');
  const [detection, setDetection] = useState(null);
  const [showModuleSelector, setShowModuleSelector] = useState(false);
  const [selectedModules, setSelectedModules] = useState([]);
  const debounceRef = useRef(null);

  // Debounced entity detection
  useEffect(() => {
    if (!query.trim()) {
      setDetection(null);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      try {
        const res = await detectEntity(query);
        setDetection(res);
      } catch (err) {
        console.error('Detection error:', err);
      }
    }, 250);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || isScanning) return;
    onStartScan({
      target: query.trim(),
      target_type: detection ? detection.detected_type : null,
      modules: selectedModules.length > 0 ? selectedModules : null,
    });
  };

  const toggleModule = (modId) => {
    setSelectedModules((prev) =>
      prev.includes(modId) ? prev.filter((m) => m !== modId) : [...prev, modId]
    );
  };

  const handlePresetClick = (presetVal) => {
    setQuery(presetVal);
  };

  return (
    <div className="w-full max-w-4xl mx-auto mb-8">
      {/* Search Bar Container */}
      <div className="relative glass-panel rounded-2xl p-2 sm:p-3 shadow-2xl border border-cyan-500/20">
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-center gap-2">
          
          {/* Main Input Box */}
          <div className="relative flex-1 w-full flex items-center">
            <div className="absolute left-3.5 text-slate-400 flex items-center pointer-events-none">
              <Search className="w-5 h-5 text-cyan-400" />
            </div>

            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter Target: username, email, phone, domain, IP, or hash..."
              disabled={isScanning}
              className="w-full pl-11 pr-24 py-3 bg-slate-900/80 rounded-xl text-slate-100 placeholder-slate-500 text-sm sm:text-base font-mono focus:outline-none focus:ring-2 focus:ring-cyan-500/50 border border-slate-800 disabled:opacity-60 transition-all"
            />

            {/* Clear button if has text */}
            {query && !isScanning && (
              <button
                type="button"
                onClick={() => { setQuery(''); setDetection(null); }}
                className="absolute right-14 text-slate-400 hover:text-slate-200 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            {/* Entity Detection Pill */}
            {detection && (
              <div className="absolute right-3.5 flex items-center gap-1.5 px-2 py-1 rounded-md bg-slate-800/90 border border-slate-700 text-xs font-mono">
                {TYPE_ICONS[detection.detected_type] || TYPE_ICONS.unknown}
                <span className="uppercase font-semibold text-[11px] text-slate-300">
                  {detection.detected_type}
                </span>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            {/* Module Filter Button */}
            <button
              type="button"
              onClick={() => setShowModuleSelector(!showModuleSelector)}
              className={`p-3 rounded-xl border transition-colors flex items-center gap-1.5 text-xs font-medium ${
                showModuleSelector || selectedModules.length > 0
                  ? 'bg-cyan-500/10 border-cyan-500/40 text-cyan-300'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
              title="Select Modules"
            >
              <SlidersHorizontal className="w-4 h-4" />
              {selectedModules.length > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-cyan-500/30 text-cyan-200 text-[10px]">
                  {selectedModules.length}
                </span>
              )}
            </button>

            {/* Launch / Stop Button */}
            {isScanning ? (
              <button
                type="button"
                onClick={onStopScan}
                className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-sm font-semibold shadow-lg shadow-rose-600/30 transition-all"
              >
                <StopCircle className="w-4 h-4" />
                <span>Abort Scan</span>
              </button>
            ) : (
              <button
                type="submit"
                disabled={!query.trim()}
                className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-600 hover:from-cyan-400 hover:to-sky-500 text-slate-950 font-bold text-sm shadow-lg shadow-cyan-500/25 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <Sparkles className="w-4 h-4 text-slate-950" />
                <span>Investigate</span>
              </button>
            )}
          </div>
        </form>

        {/* Modules Multi-Select Drawer */}
        {showModuleSelector && (
          <div className="mt-3 p-4 bg-slate-900/95 border border-slate-800 rounded-xl animate-fadeIn">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Active OSINT Modules ({availableModules.length})
              </span>
              <button
                type="button"
                onClick={() => setSelectedModules([])}
                className="text-xs text-cyan-400 hover:underline"
              >
                Reset to Auto-Recommend
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
              {availableModules.map((mod) => {
                const isSelected = selectedModules.includes(mod.id);
                return (
                  <div
                    key={mod.id}
                    onClick={() => toggleModule(mod.id)}
                    className={`flex items-start gap-2.5 p-2 rounded-lg border cursor-pointer text-xs transition-colors ${
                      isSelected
                        ? 'bg-cyan-950/40 border-cyan-500/40 text-cyan-200'
                        : 'bg-slate-950/60 border-slate-800/80 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => {}}
                      className="mt-0.5 rounded border-slate-700 text-cyan-500 focus:ring-0"
                    />
                    <div>
                      <div className="font-semibold text-slate-200">{mod.name}</div>
                      <div className="text-[11px] text-slate-500 line-clamp-1">{mod.description}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Presets / Demo Targets */}
        <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between flex-wrap gap-2 text-xs">
          <div className="flex items-center gap-1.5 text-slate-500">
            <span>Quick targets:</span>
            {PRESETS.map((p) => (
              <button
                key={p.value}
                type="button"
                onClick={() => handlePresetClick(p.value)}
                className="px-2 py-0.5 rounded bg-slate-800/60 hover:bg-slate-800 text-slate-400 hover:text-cyan-300 font-mono transition-colors"
              >
                {p.value}
              </button>
            ))}
          </div>

          <div className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span>
            Zero Setup • Full OPSEC • 100% Client/Self-Hosted
          </div>
        </div>
      </div>
    </div>
  );
}
