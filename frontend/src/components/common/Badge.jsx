import React from 'react';

export const SeverityBadge = ({ severity }) => {
  const styles = {
    CRITICAL: 'bg-rose-500/10 text-rose-400 border-rose-500/30 shadow-rose-500/10',
    HIGH: 'bg-amber-500/10 text-amber-400 border-amber-500/30 shadow-amber-500/10',
    MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
    LOW: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    INFO: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  };

  return (
    <span className={`px-2.5 py-0.5 text-xs font-mono font-semibold rounded border ${styles[severity] || styles.INFO}`}>
      {severity}
    </span>
  );
};

export const StatusBadge = ({ status }) => {
  const styles = {
    OPEN: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    CONFIRMED: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    FALSE_POSITIVE: 'bg-slate-700/40 text-slate-400 border-slate-600/30',
    RESOLVED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  };

  return (
    <span className={`px-2 py-0.5 text-[11px] font-mono rounded border ${styles[status] || styles.OPEN}`}>
      {status}
    </span>
  );
};
