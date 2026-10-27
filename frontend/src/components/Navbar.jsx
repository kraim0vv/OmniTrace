import React from 'react';
import { 
  FolderLock, 
  Settings, 
  Download, 
  Network, 
  ListFilter,
  Circle
} from 'lucide-react';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  activeCase, 
  onOpenCases, 
  onOpenSettings, 
  onOpenExport,
  isScanning,
  hasResults
}) {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-[#09090b]/80 backdrop-blur-xl px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand & Minimalist Logo */}
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-zinc-900 border border-white/15 p-1.5 shadow-sm">
            <img src="/logo.svg" alt="OmniTrace Logo" className="w-full h-full object-contain filter invert-0" />
            {isScanning && (
              <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-white"></span>
              </span>
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-base tracking-tight text-white">
                OmniTrace
              </span>
            </div>
            <p className="text-[11px] text-zinc-400 hidden sm:block font-mono tracking-tight">
              Open-Source OSINT Reconnaissance Framework
            </p>
          </div>
        </div>

        {/* View Switcher (Feed vs Link Graph) */}
        <div className="flex items-center bg-zinc-900/90 p-1 rounded-lg border border-white/10">
          <button
            onClick={() => setActiveTab('feed')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'feed'
                ? 'bg-white text-zinc-950 font-semibold shadow-sm'
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
            }`}
          >
            <ListFilter className="w-3.5 h-3.5" />
            <span>Feed</span>
          </button>
          <button
            onClick={() => setActiveTab('graph')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'graph'
                ? 'bg-white text-zinc-950 font-semibold shadow-sm'
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
            }`}
          >
            <Network className="w-3.5 h-3.5" />
            <span>Graph</span>
          </button>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* Active Case Tag */}
          <button
            onClick={onOpenCases}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 border border-white/10 hover:border-white/20 text-xs text-zinc-300 hover:text-white transition-colors"
            title="Cases & Investigations"
          >
            <FolderLock className="w-3.5 h-3.5 text-zinc-400" />
            <span className="max-w-[120px] truncate hidden md:inline">
              {activeCase ? activeCase.name : 'Default Case'}
            </span>
          </button>

          {/* Export Report Button */}
          <button
            onClick={onOpenExport}
            disabled={!hasResults}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              hasResults
                ? 'bg-zinc-900 border-white/10 hover:border-white/30 text-zinc-200 hover:text-white'
                : 'opacity-40 cursor-not-allowed bg-zinc-950 border-white/5 text-zinc-600'
            }`}
            title="Export Report (HTML / JSON / CSV)"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export</span>
          </button>

          {/* Settings / OPSEC */}
          <button
            onClick={onOpenSettings}
            className="p-2 rounded-lg bg-zinc-900 border border-white/10 hover:border-white/25 text-zinc-400 hover:text-white transition-colors"
            title="OPSEC, Proxies & API Keys"
          >
            <Settings className="w-4 h-4" />
          </button>

          {/* GitHub Link */}
          <a
            href="https://github.com/kraim0v/OmniTrace"
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 rounded-lg bg-zinc-900 border border-white/10 hover:border-white/25 text-zinc-400 hover:text-white transition-colors"
            title="View on GitHub"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
