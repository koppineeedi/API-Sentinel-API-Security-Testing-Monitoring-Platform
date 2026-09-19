import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { User, LogOut, ShieldCheck, Bell, Clock } from 'lucide-react';
import { formatIST } from '../../utils/dateFormatter';

export const TopNav = () => {
  const { user, logout } = useAuth();
  const [istTime, setIstTime] = useState('');

  useEffect(() => {
    const updateClock = () => {
      setIstTime(formatIST(new Date()));
    };
    updateClock();
    const timer = setInterval(updateClock, 1000);
    return () => clearInterval(timer);
  }, []);

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'ADMIN':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'SECURITY_ANALYST':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
      default:
        return 'bg-slate-700/50 text-slate-300 border-slate-600/30';
    }
  };

  return (
    <header className="h-16 bg-[#0d1424]/80 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>SYSTEM ACTIVE</span>
        </div>
        <div className="hidden md:flex items-center gap-2 text-xs font-mono text-cyan-300 bg-cyan-950/40 border border-cyan-800/40 px-3 py-1 rounded-md">
          <Clock className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span>{istTime || 'Loading IST...'}</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Role Badge */}
        {user?.role && (
          <span className={`text-xs font-mono font-semibold px-2.5 py-1 rounded-md border ${getRoleBadgeColor(user.role)}`}>
            {user.role}
          </span>
        )}

        {/* User Info */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-cyan-400 font-bold text-xs">
            {user?.email?.[0]?.toUpperCase() || <User className="w-4 h-4" />}
          </div>
          <div className="text-left hidden sm:block">
            <div className="text-xs font-medium text-slate-200">{user?.full_name || 'Security User'}</div>
            <div className="text-[11px] text-slate-400 font-mono">{user?.email}</div>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={logout}
          title="Sign Out"
          className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors border border-transparent hover:border-rose-500/20"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
