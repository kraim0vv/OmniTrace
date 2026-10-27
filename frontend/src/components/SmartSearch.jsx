import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  SlidersHorizontal, 
  StopCircle, 
  User, 
  Mail, 
  Globe, 
  Radio, 
  Phone, 
  Key,
  X,
  ArrowRight
} from 'lucide-react';
import { detectEntity } from '../services/api';

const TYPE_ICONS = {
  username: <User className="w-3.5 h-3.5 text-zinc-300" />,
  email: <Mail className="w-3.5 h-3.5 text-zinc-300" />,
  domain: <Globe className="w-3.5 h-3.5 text-zinc-300" />,
  ip: <Radio className="w-3.5 h-3.5 text-zinc-300" />,
  phone: <Phone className="w-3.5 h-3.5 text-zinc-300" />,
  hash: <Key className="w-3.5 h-3.5 text-zinc-300" />,
  unknown: <Search className="w-3.5 h-3.5 text-zinc-500" />,
};

const PRESETS = [
  { label: 'Username', value: 'torvalds' },
  { label: 'Email', value: 'contact@cloudflare.com' },
  { label: 'Domain', value: 'python.org' },
  { label: 'IP', value: '1.1.1.1' },
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
    }, 200);

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
      <div className="relative mono-panel rounded-xl p-2.5 shadow-2xl border border-white/10">
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-center gap-2">
          
          {/* Main Input Box */}
          <div className="relative flex-1 w-full flex items-center">
            <div className="absolute left-3.5 text-zinc-400 flex items-center pointer-events-none">
              <Search className="w-4 h-4 text-zinc-400" />
            </div>

            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Query identifier: username, email, phone, domain, IP, or hash..."
              disabled={isScanning}
              className="w-full pl-10 pr-28 py-3 bg-zinc-950/90 rounded-lg text-white placeholder-zinc-500 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-white/40 border border-white/10 disabled:opacity-60 transition-all"
            />

            {/* Clear button if has text */}
            {query && !isScanning && (
              <button
                type="button"
                onClick={() => { setQuery(''); setDetection(null); }}
                className="absolute right-20 text-zinc-400 hover:text-white p-1"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}

            {/* Entity Detection Badge */}
            {detection && (
              <div className="absolute right-3 flex items-center gap-1.5 px-2 py-0.5 rounded bg-zinc-800 border border-white/10 text-[11px] font-mono text-zinc-200">
                {TYPE_ICONS[detection.detected_type] || TYPE_ICONS.unknown}
                <span className="uppercase font-semibold">
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
              className={`p-3 rounded-lg border transition-colors flex items-center gap-1.5 text-xs font-medium ${
                showModuleSelector || selectedModules.length > 0
                  ? 'bg-zinc-800 border-white/30 text-white'
                  : 'bg-zinc-950 border-white/10 text-zinc-400 hover:text-white hover:border-white/20'
              }`}
              title="Modules"
            >
              <SlidersHorizontal className="w-4 h-4" />
              {selectedModules.length > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-white text-zinc-950 text-[10px] font-bold">
                  {selectedModules.length}
                </span>
              )}
            </button>

            {/* Launch / Stop Button */}
            {isScanning ? (
              <button
                type="button"
                onClick={onStopScan}
                className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-5 py-3 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white text-xs font-semibold border border-white/20 transition-all"
              >
                <StopCircle className="w-4 h-4 text-rose-400" />
                <span>Abort Scan</span>
              </button>
            ) : (
              <button
                type="submit"
                disabled={!query.trim()}
                className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-white hover:bg-zinc-200 text-zinc-950 font-bold text-xs shadow-sm transition-all disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <span>Investigate</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </form>

        {/* Modules Multi-Select Drawer */}
        {showModuleSelector && (
          <div className="mt-3 p-4 bg-zinc-950 border border-white/10 rounded-lg animate-fadeIn">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/5">
              <span className="text-xs font-semibold text-zinc-300 uppercase tracking-wider font-mono">
                Active Modules ({availableModules.length})
              </span>
              <button
                type="button"
                onClick={() => setSelectedModules([])}
                className="text-xs text-zinc-400 hover:text-white underline font-mono"
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
                        ? 'bg-zinc-800 border-white/40 text-white'
                        : 'bg-zinc-900/60 border-white/5 text-zinc-400 hover:border-white/20 hover:text-zinc-200'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => {}}
                      className="mt-0.5 rounded border-zinc-700 text-white focus:ring-0"
                    />
                    <div>
                      <div className="font-semibold text-zinc-200">{mod.name}</div>
                      <div className="text-[11px] text-zinc-500 line-clamp-1">{mod.description}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Presets & Info */}
        <div className="mt-2.5 pt-2 border-t border-white/5 flex items-center justify-between flex-wrap gap-2 text-xs">
          <div className="flex items-center gap-1.5 text-zinc-400">
            <span className="text-zinc-500 font-mono text-[11px]">Presets:</span>
            {PRESETS.map((p) => (
              <button
                key={p.value}
                type="button"
                onClick={() => handlePresetClick(p.value)}
                className="px-2 py-0.5 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white font-mono text-[11px] transition-colors border border-white/5"
              >
                {p.value}
              </button>
            ))}
          </div>

          <div className="text-[11px] text-zinc-500 font-mono flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-white inline-block"></span>
            <span>130+ Sources • Local & Self-Hosted • Zero External Logs</span>
          </div>
        </div>
      </div>
    </div>
  );
}
