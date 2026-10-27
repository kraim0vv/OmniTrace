import React, { useState, useMemo } from 'react';
import { Search, CheckCircle2, XCircle, AlertCircle, Inbox, Loader2 } from 'lucide-react';
import ResultCard from './ResultCard';

export default function ResultsStream({ findings = [], isScanning }) {
  const [statusFilter, setStatusFilter] = useState('found');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  const categories = useMemo(() => {
    const set = new Set();
    findings.forEach((f) => {
      if (f.category) set.add(f.category);
    });
    return Array.from(set);
  }, [findings]);

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

  const filteredFindings = useMemo(() => {
    return findings.filter((f) => {
      if (statusFilter !== 'all') {
        if (statusFilter === 'found' && f.status !== 'found') return false;
        if (statusFilter === 'not_found' && f.status !== 'not_found') return false;
        if (statusFilter === 'errors' && !['error', 'rate_limited'].includes(f.status)) return false;
      }
      if (categoryFilter !== 'all' && f.category !== categoryFilter) return false;
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
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-4 pb-3 border-b border-white/10">
        
        {/* Status Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          <button
            onClick={() => setStatusFilter('found')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              statusFilter === 'found'
                ? 'bg-white text-zinc-950 shadow-sm'
                : 'text-zinc-400 hover:text-white bg-zinc-900 border border-white/5'
            }`}
          >
            <span>Found</span>
            <span className={`ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
              statusFilter === 'found' ? 'bg-zinc-200 text-zinc-950 font-bold' : 'bg-zinc-800 text-zinc-300'
            }`}>
              {counts.found}
            </span>
          </button>

          <button
            onClick={() => setStatusFilter('all')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              statusFilter === 'all'
                ? 'bg-white text-zinc-950 font-semibold shadow-sm'
                : 'text-zinc-400 hover:text-white bg-zinc-900 border border-white/5'
            }`}
          >
            <span>All Checks</span>
            <span className={`ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
              statusFilter === 'all' ? 'bg-zinc-200 text-zinc-950 font-bold' : 'bg-zinc-800 text-zinc-300'
            }`}>
              {counts.all}
            </span>
          </button>

          <button
            onClick={() => setStatusFilter('not_found')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              statusFilter === 'not_found'
                ? 'bg-white text-zinc-950 font-semibold shadow-sm'
                : 'text-zinc-400 hover:text-white bg-zinc-900 border border-white/5'
            }`}
          >
            <span>Not Found</span>
            <span className={`ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
              statusFilter === 'not_found' ? 'bg-zinc-200 text-zinc-950 font-bold' : 'bg-zinc-800 text-zinc-300'
            }`}>
              {counts.notFound}
            </span>
          </button>

          <button
            onClick={() => setStatusFilter('errors')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              statusFilter === 'errors'
                ? 'bg-white text-zinc-950 font-semibold shadow-sm'
                : 'text-zinc-400 hover:text-white bg-zinc-900 border border-white/5'
            }`}
          >
            <span>Errors</span>
            <span className={`ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
              statusFilter === 'errors' ? 'bg-zinc-200 text-zinc-950 font-bold' : 'bg-zinc-800 text-zinc-300'
            }`}>
              {counts.errors}
            </span>
          </button>
        </div>

        {/* Right Search Input & Category Filter */}
        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          {categories.length > 1 && (
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="bg-zinc-900 border border-white/10 text-zinc-300 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-white/30 font-mono"
            >
              <option value="all">All Categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          )}

          <div className="relative flex items-center">
            <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter results..."
              className="bg-zinc-900 border border-white/10 pl-8 pr-3 py-1.5 text-xs rounded-lg text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-white/30 w-36 sm:w-44 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Results List */}
      {filteredFindings.length > 0 ? (
        <div className="flex flex-col gap-2">
          {filteredFindings.map((finding) => (
            <ResultCard key={finding.id} finding={finding} />
          ))}
        </div>
      ) : (
        <div className="mono-panel rounded-xl p-12 text-center border border-white/10 my-6">
          <div className="w-10 h-10 rounded-lg bg-zinc-900 border border-white/10 mx-auto flex items-center justify-center text-zinc-400 mb-3">
            {isScanning ? (
              <Loader2 className="w-5 h-5 text-white animate-spin" />
            ) : (
              <Inbox className="w-5 h-5 text-zinc-500" />
            )}
          </div>
          <h3 className="text-sm font-semibold text-white">
            {isScanning ? 'Querying Target Across 130+ Sources...' : 'No Findings in this View'}
          </h3>
          <p className="text-xs text-zinc-400 max-w-sm mx-auto mt-1 font-mono">
            {isScanning
              ? 'Asynchronous probes are streaming findings directly from public sources.'
              : statusFilter === 'found' && counts.found === 0 && counts.all > 0
              ? 'No confirmed matches yet. Select "All Checks" to view full audit logs.'
              : 'Enter a target query above to initiate automated reconnaissance.'}
          </p>
        </div>
      )}
    </div>
  );
}
