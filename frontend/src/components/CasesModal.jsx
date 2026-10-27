import React, { useState } from 'react';
import { X, FolderLock, Plus, Trash2, Calendar, FileText } from 'lucide-react';

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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-xl bg-zinc-950 border border-white/10 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/10 bg-zinc-900/40">
          <div className="flex items-center gap-2.5">
            <FolderLock className="w-4 h-4 text-white" />
            <h3 className="font-semibold text-sm text-white">
              Investigation Workspaces
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
        <div className="p-5 overflow-y-auto flex-1">
          {isCreating ? (
            <form onSubmit={handleCreateSubmit} className="mb-5 p-4 rounded-lg bg-zinc-900/80 border border-white/10">
              <h4 className="text-xs font-semibold text-white uppercase tracking-wider font-mono mb-3">
                New Investigation
              </h4>
              <div className="flex flex-col gap-3">
                <div>
                  <label className="text-[11px] text-zinc-400 block mb-1 font-mono">Title</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Case #104 — Subject X"
                    className="w-full bg-zinc-950 border border-white/10 rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-white/40"
                    required
                  />
                </div>
                <div>
                  <label className="text-[11px] text-zinc-400 block mb-1 font-mono">Description</label>
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Brief objective..."
                    className="w-full bg-zinc-950 border border-white/10 rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-white/40"
                  />
                </div>
                <div>
                  <label className="text-[11px] text-zinc-400 block mb-1 font-mono">Notes</label>
                  <textarea
                    rows={2}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Target identifiers, background hypotheses..."
                    className="w-full bg-zinc-950 border border-white/10 rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-white/40"
                  />
                </div>
                <div className="flex items-center justify-end gap-2 mt-1">
                  <button
                    type="button"
                    onClick={() => setIsCreating(false)}
                    className="px-3 py-1.5 rounded text-xs text-zinc-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 rounded text-xs font-semibold bg-white text-zinc-950 hover:bg-zinc-200"
                  >
                    Save Case
                  </button>
                </div>
              </div>
            </form>
          ) : (
            <div className="flex justify-between items-center mb-4">
              <span className="text-[11px] font-mono text-zinc-500 uppercase">
                {cases.length} Recorded Investigations
              </span>
              <button
                onClick={() => setIsCreating(true)}
                className="flex items-center gap-1.5 px-3 py-1 rounded bg-white text-zinc-950 hover:bg-zinc-200 text-xs font-semibold transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Case</span>
              </button>
            </div>
          )}

          {/* List of Cases */}
          <div className="flex flex-col gap-2">
            {cases.length === 0 ? (
              <div className="text-center py-8 text-zinc-500 text-xs font-mono">
                No active cases. Create one to organize your searches.
              </div>
            ) : (
              cases.map((c) => {
                const isSelected = activeCase?.id === c.id;
                return (
                  <div
                    key={c.id}
                    className={`p-3.5 rounded-lg border transition-all flex items-start justify-between gap-3 ${
                      isSelected
                        ? 'bg-zinc-900 border-white/30'
                        : 'bg-zinc-950 border-white/5 hover:border-white/15'
                    }`}
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-xs text-white">{c.name}</span>
                        {isSelected && (
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-white text-zinc-950 font-bold">
                            ACTIVE
                          </span>
                        )}
                      </div>
                      {c.description && (
                        <p className="text-[11px] text-zinc-400 mt-0.5">{c.description}</p>
                      )}
                      <div className="flex items-center gap-3 mt-2 text-[10px] text-zinc-500 font-mono">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(c.created_at * 1000).toLocaleDateString()}
                        </span>
                        {c.notes && (
                          <span className="flex items-center gap-1 text-zinc-400">
                            <FileText className="w-3 h-3" />
                            Notes attached
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      {!isSelected && (
                        <button
                          onClick={() => onSelectCase(c)}
                          className="px-2.5 py-1 rounded text-xs bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-colors"
                        >
                          Select
                        </button>
                      )}
                      <button
                        onClick={() => onDeleteCase(c.id)}
                        className="p-1.5 rounded text-zinc-500 hover:text-white hover:bg-zinc-800 transition-colors"
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
