import React, { useState, useMemo } from 'react';
import { Filter, Search, CheckCircle2, XCircle, AlertCircle, Sparkles, Inbox } from 'lucide-react';
import ResultCard from './ResultCard';

export default function ResultsStream({ findings = [], isScanning }) {
  const [statusFilter, setStatusFilter] = useState('found'); // Default to found for best UX!
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  // Extract unique categories
  const categories = useMemo(() => {
    const set = new Set();
    findings.forEach((f) => {
      if (f.category) set.add(f.category);
    });
    return Array.from(set);
  }, [findings]);

  // Counts
  const counts = useMemo(() => {
    let found = 0;
    let notFound = 0;
    let errors = 0;
    findings.forEach((f) => {
      if (f.status === 'found') found++;
      else if (f.status === 'not_found') notFound++;
      else if (f.status === 'error' || f.status === 'rate_limited') errors++;
    });
    return { all: findings.length, found, notFound, errors };
  }, [findings]);

  // Filtered findings
  const filteredFindings = useMemo(() => {
    return findings.filter((f) => {
      // Status filter
      if (statusFilter !== 'all') {
        if (statusFilter === 'found' && f.status !== 'found') return false;
        if (statusFilter === 'not_found' && f.status !== 'not_found') return false;
        if (statusFilter === 'errors' && !['error', 'rate_limited'].includes(f.status)) return false;
      }
      // Category filter
      if (categoryFilter !== 'all' && f.category !== categoryFilter) return false;
      // Search term
      if (searchTerm.trim()) {
        const query = searchTerm.toLowerCase();
        const matchSource = f.source?.toLowerCase().includes(query);
        const matchTitle = f.title?.toLowerCase().includes(query);
        const matchDesc = f.description?.toLowerCase().includes(query);
        const matchUrl = f.url?.toLowerCase().includes(query);
        if (!matchSource && !matchTitle && !matchDesc && !matchUrl) return false;
      }
      return true;
    });
  }, [findings, statusFilter, categoryFilter, searchTerm]);

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-800/80">
        
        {/* Status Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          <button
            onClick={() => setStatusFilter('found')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              statusFilter === 'found'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-800'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Found</span>
            <span className="ml-1 px-1.5 py-0.2 rounded-full bg-emerald-950 text-emerald-400 text-[10px] font-mono">
              {counts.found}
            </span>
          </button>

          <button
            onClick={() => setStatusFilter('all')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              statusFilter === 'all'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-800'
            }`}
          >
            <span>All Checks</span>
            <span className="ml-1 px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300 text-[10px] font-mono">
              {counts.all}
            </span>
          </button>

          <button
            onClick={() => setStatusFilter('not_found')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              statusFilter === 'not_found'
                ? 'bg-slate-700/50 text-slate-200 border border-slate-600 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-800'
            }`}
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>Not Found</span>
            <span className="ml-1 px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-400 text-[10px] font-mono">
              {counts.notFound}
            </span>
          </button>

          <button
            onClick={() => setStatusFilter('errors')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              statusFilter === 'errors'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-800'
            }`}
          >
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Errors</span>
            <span className="ml-1 px-1.5 py-0.2 rounded-full bg-rose-950 text-rose-400 text-[10px] font-mono">
              {counts.errors}
            </span>
          </button>
        </div>

        {/* Right Search Input & Category Filter */}
        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          {/* Category Dropdown */}
          {categories.length > 1 && (
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-cyan-500"
            >
              <option value="all">All Categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          )}

          {/* Quick Filter Search */}
          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter results..."
              className="bg-slate-900 border border-slate-800 pl-8 pr-3 py-1.5 text-xs rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-36 sm:w-44 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Results List */}
      {filteredFindings.length > 0 ? (
        <div className="flex flex-col gap-2.5">
          {filteredFindings.map((finding) => (
            <ResultCard key={finding.id} finding={finding} />
          ))}
        </div>
      ) : (
        <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800/80 my-8">
          <div className="w-12 h-12 rounded-2xl bg-slate-800/80 border border-slate-700 mx-auto flex items-center justify-center text-slate-400 mb-3">
            {isScanning ? (
              <Sparkles className="w-6 h-6 text-cyan-400 animate-spin" />
            ) : (
              <Inbox className="w-6 h-6 text-slate-500" />
            )}
          </div>
          <h3 className="text-base font-semibold text-slate-200">
            {isScanning ? 'Investigating Target...' : 'No Findings in this View'}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
            {isScanning
              ? 'Real-time OSINT modules are querying sources. As verified profiles and records appear, they will stream here.'
              : statusFilter === 'found' && counts.found === 0 && counts.all > 0
              ? 'No confirmed accounts found yet. Try switching filter to "All Checks" to view full audit logs.'
              : 'Enter a target identifier above to initiate reconnaissance.'}
          </p>
        </div>
      )}
    </div>
  );
}
