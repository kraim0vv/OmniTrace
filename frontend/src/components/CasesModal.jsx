import React, { useState } from 'react';
import { X, FolderLock, Plus, Trash2, Check, Calendar, FileText } from 'lucide-react';

export default function CasesModal({
  isOpen,
  onClose,
  cases = [],
  activeCase,
  onSelectCase,
  onCreateCase,
  onDeleteCase,
}) {
  const [isCreating, setIsCreating] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [notes, setNotes] = useState('');

  if (!isOpen) return null;

  const handleCreateSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onCreateCase({
      name: name.trim(),
      description: description.trim(),
      notes: notes.trim(),
    });
    setName('');
    setDescription('');
    setNotes('');
    setIsCreating(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <FolderLock className="w-5 h-5 text-cyan-400" />
            <h3 className="font-bold text-base text-slate-100">
              Investigation Cases & Workspaces
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
        <div className="p-6 overflow-y-auto flex-1">
          {/* Create New Case Accordion / Form */}
          {isCreating ? (
            <form onSubmit={handleCreateSubmit} className="mb-6 p-4 rounded-xl bg-slate-950 border border-cyan-500/30">
              <h4 className="text-sm font-semibold text-cyan-300 mb-3">Create New Investigation</h4>
              <div className="flex flex-col gap-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Case Title</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Operation Falcon / Subject Alpha"
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Description</label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Brief objective of this investigation..."
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Investigator Notes (Optional)</label>
                  <textarea
                    rows={2}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Initial hypotheses, known emails, or target metadata..."
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div className="flex items-center justify-end gap-2 mt-2">
                  <button
                    type="button"
                    onClick={() => setIsCreating(false)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-slate-950 shadow-md"
                  >
                    Save Case
                  </button>
                </div>
              </div>
            </form>
          ) : (
            <div className="flex justify-between items-center mb-4">
              <span className="text-xs font-mono uppercase text-slate-400">
                {cases.length} Recorded Cases
              </span>
              <button
                onClick={() => setIsCreating(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/30 text-xs font-medium transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Case</span>
              </button>
            </div>
          )}

          {/* List of Cases */}
          <div className="flex flex-col gap-2.5">
            {cases.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-sm">
                No cases created yet. Create one to organize investigations.
              </div>
            ) : (
              cases.map((c) => {
                const isSelected = activeCase?.id === c.id;
                return (
                  <div
                    key={c.id}
                    className={`p-4 rounded-xl border transition-all flex items-start justify-between gap-3 ${
                      isSelected
                        ? 'bg-cyan-950/30 border-cyan-500/40'
                        : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                    }`}
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-slate-100">{c.name}</span>
                        {isSelected && (
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-semibold">
                            ACTIVE
                          </span>
                        )}
                      </div>
                      {c.description && (
                        <p className="text-xs text-slate-400 mt-0.5">{c.description}</p>
                      )}
                      <div className="flex items-center gap-3 mt-2 text-[11px] text-slate-500 font-mono">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(c.created_at * 1000).toLocaleDateString()}
                        </span>
                        {c.notes && (
                          <span className="flex items-center gap-1 text-slate-400">
                            <FileText className="w-3 h-3" />
                            Has notes
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      {!isSelected && (
                        <button
                          onClick={() => onSelectCase(c)}
                          className="px-2.5 py-1 rounded-lg text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
                        >
                          Select
                        </button>
                      )}
                      <button
                        onClick={() => onDeleteCase(c.id)}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-950/30 transition-colors"
                        title="Delete Case"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
