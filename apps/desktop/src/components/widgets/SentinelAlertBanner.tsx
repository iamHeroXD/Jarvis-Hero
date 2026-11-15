import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, Trash2, ArrowRight, X } from 'lucide-react';

interface SentinelAlertBannerProps {
  freeGb: number;
  totalGb: number;
  percentUsed: number;
  onOpenStorageModal: () => void;
  onQuickClean: () => void;
  onDismiss: () => void;
}

export default function SentinelAlertBanner({
  freeGb,
  totalGb,
  percentUsed,
  onOpenStorageModal,
  onQuickClean,
  onDismiss,
}: SentinelAlertBannerProps) {
  const isCritical = freeGb < 6.0;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`relative z-30 mx-6 my-2 px-4 py-2.5 rounded-2xl border backdrop-blur-xl flex items-center justify-between font-mono shadow-lg ${
        isCritical
          ? 'bg-rose-950/80 border-rose-500/70 text-rose-200 shadow-[0_0_25px_rgba(244,63,94,0.35)]'
          : 'bg-amber-950/80 border-amber-500/70 text-amber-200 shadow-[0_0_25px_rgba(245,158,11,0.35)]'
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`p-1.5 rounded-xl border ${isCritical ? 'bg-rose-500/30 border-rose-400 animate-ping' : 'bg-amber-500/30 border-amber-400'}`}>
          <ShieldAlert size={16} />
        </div>
        <div className="text-xs">
          <span className="font-extrabold tracking-wider text-white">
            {isCritical ? 'CRITICAL STORAGE ALERT // ' : 'STORAGE ADVISORY // '}
          </span>
          <span>
            Primary C: Drive has only <strong>{freeGb} GB free</strong> remaining ({percentUsed}% used). Clean temporary storage to prevent OS degradation.
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onQuickClean}
          className="px-3 py-1 rounded-xl bg-rose-500/30 hover:bg-rose-500/50 border border-rose-400 text-white text-[11px] font-bold flex items-center gap-1.5 transition-all shadow-sm"
          title="Directly purge temporary files and Recycle Bin"
        >
          <Trash2 size={12} />
          <span>🧹 PURGE TEMP</span>
        </button>

        <button
          onClick={onOpenStorageModal}
          className="px-3 py-1 rounded-xl bg-black/50 hover:bg-black/80 border border-rose-400/50 text-rose-200 hover:text-white text-[11px] font-bold flex items-center gap-1 transition-all"
        >
          <span>DETAILS</span>
          <ArrowRight size={12} />
        </button>

        <button
          onClick={onDismiss}
          className="p-1 hover:text-white transition-colors"
          title="Dismiss Alert"
        >
          <X size={14} />
        </button>
      </div>
    </motion.div>
  );
}
