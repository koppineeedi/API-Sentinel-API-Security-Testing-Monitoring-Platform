import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldAlert,
  LayoutDashboard,
  FolderGit2,
  AlertTriangle,
  PlaySquare,
  Activity,
  FileSpreadsheet,
  Settings,
  Lock,
  History
} from 'lucide-react';

export const Sidebar = () => {
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/inventory', label: 'API Inventory', icon: FolderGit2 },
    { path: '/findings', label: 'Findings', icon: AlertTriangle },
    { path: '/scans', label: 'Scans', icon: PlaySquare },
    { path: '/traffic', label: 'Traffic Monitor', icon: Activity },
    { path: '/reports', label: 'Reports', icon: FileSpreadsheet },
    { path: '/audit', label: 'Audit Logs', icon: History },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0d1424] border-r border-slate-800 flex flex-col justify-between shrink-0 min-h-screen">
      <div>
        {/* Brand Header */}
        <div className="p-5 flex items-center gap-3 border-b border-slate-800/80">
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
            <ShieldAlert className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 text-lg tracking-wide flex items-center gap-1.5">
              API Sentinel
            </h1>
            <p className="text-[10px] text-cyan-400/80 font-mono tracking-wider uppercase">SecOps Platform</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/5'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Authorized Scope Banner */}
      <div className="p-4 m-3 bg-slate-900/60 border border-amber-500/20 rounded-xl text-xs">
        <div className="flex items-center gap-2 text-amber-400 font-semibold mb-1">
          <Lock className="w-3.5 h-3.5" />
          <span>Authorized Scope</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Authorized security testing only. Staging, lab & permitted systems.
        </p>
      </div>
    </aside>
  );
};
