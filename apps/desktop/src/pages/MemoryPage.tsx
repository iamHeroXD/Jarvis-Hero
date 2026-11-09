import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Search,
  Plus,
  Pin,
  Trash2,
  Tag,
  Lock,
  Sparkles,
  BookOpen,
  FolderKanban,
  Sliders,
  User,
  Briefcase,
  Layers,
} from 'lucide-react';
import { memoryApi, Memory } from '../services/api';

const CATEGORIES = [
  { id: 'all', label: 'All Memories', icon: Layers },
  { id: 'personal', label: 'Personal', icon: User },
  { id: 'project', label: 'Projects', icon: FolderKanban },
  { id: 'work', label: 'Work', icon: Briefcase },
  { id: 'technical', label: 'Technical', icon: BookOpen },
  { id: 'preference', label: 'Preferences', icon: Sliders },
  { id: 'learning', label: 'Learning', icon: Sparkles },
];

export default function MemoryPage() {
  const queryClient = useQueryClient();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  // Form state
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('technical');
  const [content, setContent] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [isSensitive, setIsSensitive] = useState(false);

  // Queries
  const { data: memories = [], isLoading } = useQuery({
    queryKey: ['memories', selectedCategory, searchQuery],
    queryFn: () => {
      if (searchQuery.trim().length > 1) {
        return memoryApi.search(searchQuery.trim());
      }
      return memoryApi.list(selectedCategory === 'all' ? undefined : selectedCategory);
    },
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: memoryApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memories'] });
      setShowAddModal(false);
      setTitle('');
      setContent('');
      setTags([]);
    },
  });

  const togglePinMutation = useMutation({
    mutationFn: ({ id, is_pinned }: { id: number; is_pinned: boolean }) =>
      memoryApi.update(id, { is_pinned: !is_pinned }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memories'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: memoryApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memories'] });
    },
  });

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  return (
    <div className="flex-1 overflow-hidden flex flex-col md:flex-row">
      {/* ── Left Category Sidebar ──────────────────────────────── */}
      <div className="w-full md:w-64 border-r border-surface-border bg-surface-1 flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-surface-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain size={18} className="text-accent" />
            <span className="font-semibold text-sm text-text-primary">Memory Engine</span>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="p-1.5 rounded-lg bg-accent/20 hover:bg-accent/30 text-accent border border-accent/40 text-xs transition-colors"
            title="Store New Memory"
          >
            <Plus size={14} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isSelected = selectedCategory === cat.id && !searchQuery;
            return (
              <button
                key={cat.id}
                onClick={() => {
                  setSelectedCategory(cat.id);
                  setSearchQuery('');
                }}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isSelected
                    ? 'bg-surface-3 text-accent border border-accent/40'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface-2'
                }`}
              >
                <Icon size={14} />
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>

        {/* Privacy Note */}
        <div className="p-3 border-t border-surface-border bg-surface-2/40 text-[11px] text-text-muted flex items-start gap-2">
          <Lock size={12} className="text-accent mt-0.5 flex-shrink-0" />
          <span>FTS5 encrypted store. Restricted strictly to Authenticated Owner profile.</span>
        </div>
      </div>

      {/* ── Main Memory Stream ─────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Top Search & Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-md">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search memories via SQLite FTS5 index..."
              className="w-full input text-xs pl-9 pr-3 py-2 bg-surface-2 border border-surface-border rounded-lg"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary text-xs"
              >
                ✕
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-text-muted font-mono">{memories.length} entries found</span>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-3.5 py-1.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow flex items-center gap-1.5 transition-all"
            >
              <Plus size={13} /> Remember Item
            </button>
          </div>
        </div>

        {/* Memories Grid */}
        {isLoading ? (
          <div className="p-12 text-center text-xs text-text-muted">Querying neural knowledge base...</div>
        ) : memories.length === 0 ? (
          <div className="card p-12 text-center border-dashed border-surface-border">
            <Brain size={36} className="mx-auto text-text-muted mb-3 opacity-60" />
            <h3 className="text-sm font-semibold text-text-primary">No Memory Records Found</h3>
            <p className="text-xs text-text-secondary mt-1">
              Store important facts, credentials, coding preferences, or project decisions.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {memories.map((mem) => (
              <div
                key={mem.id}
                className={`card p-4 border transition-all ${
                  mem.is_pinned ? 'border-accent/60 bg-surface-2' : 'border-surface-border hover:border-surface-border/80'
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-surface-3 text-accent border border-accent/20">
                      {mem.category}
                    </span>
                    <h3 className="text-sm font-bold text-text-primary">{mem.title}</h3>
                  </div>

                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => togglePinMutation.mutate({ id: mem.id, is_pinned: mem.is_pinned })}
                      className={`p-1 rounded hover:bg-surface-3 transition-colors ${
                        mem.is_pinned ? 'text-accent' : 'text-text-muted'
                      }`}
                      title={mem.is_pinned ? 'Unpin' : 'Pin to top'}
                    >
                      <Pin size={13} />
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(mem.id)}
                      className="p-1 rounded hover:bg-surface-3 text-text-muted hover:text-rose-400 transition-colors"
                      title="Delete memory"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>

                <p className="text-xs text-text-secondary leading-relaxed mb-3 font-sans whitespace-pre-wrap">
                  {mem.content}
                </p>

                <div className="flex items-center justify-between text-[11px] text-text-muted pt-2 border-t border-surface-border/50">
                  <span className="font-mono">{new Date(mem.created_at).toLocaleDateString()}</span>
                  {mem.is_sensitive && (
                    <span className="flex items-center gap-1 text-amber-400 text-[10px]">
                      <Lock size={10} /> Sensitive
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Add Memory Modal ───────────────────────────────────── */}
      <AnimatePresence>
        {showAddModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="card w-full max-w-lg p-6 border border-accent/40 shadow-glow"
            >
              <div className="flex items-center justify-between mb-4 border-b border-surface-border pb-3">
                <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
                  <Brain size={18} className="text-accent" /> Store Long-Term Memory
                </h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="text-text-muted hover:text-text-primary text-xs"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Memory Title</label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g. Owner preference for concise British persona"
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full input text-xs py-2 px-2 bg-surface-2 border border-surface-border rounded-lg"
                  >
                    <option value="personal">Personal</option>
                    <option value="project">Project</option>
                    <option value="work">Work</option>
                    <option value="technical">Technical</option>
                    <option value="preference">Preference</option>
                    <option value="learning">Learning</option>
                    <option value="conversation">Conversation</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-text-secondary mb-1">Content</label>
                  <textarea
                    rows={4}
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Write details, context, code snippet or instruction to remember..."
                    className="w-full input text-xs py-2 px-3 bg-surface-2 border border-surface-border rounded-lg"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="isSens"
                    checked={isSensitive}
                    onChange={(e) => setIsSensitive(e.target.checked)}
                    className="rounded bg-surface-2 border-surface-border text-accent focus:ring-0"
                  />
                  <label htmlFor="isSens" className="text-xs text-text-secondary cursor-pointer">
                    Mark as Sensitive (Owner profile only)
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-surface-border">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 rounded-lg text-xs text-text-muted hover:text-text-primary"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (!title.trim() || !content.trim()) return;
                    createMutation.mutate({
                      title: title.trim(),
                      category,
                      content: content.trim(),
                      tags,
                      is_sensitive: isSensitive,
                    });
                  }}
                  disabled={!title.trim() || !content.trim() || createMutation.isPending}
                  className="px-4 py-1.5 rounded-lg bg-accent hover:bg-accent/90 text-white text-xs font-semibold shadow-glow disabled:opacity-50"
                >
                  {createMutation.isPending ? 'Committing...' : 'Store Memory'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
