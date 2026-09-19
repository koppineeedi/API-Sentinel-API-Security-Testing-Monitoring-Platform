import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Shield, Search, Filter, RefreshCw, Clock, UserCheck } from 'lucide-react';

export const AuditLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [actionFilter, setActionFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditLogs();
  }, [actionFilter, searchQuery]);

  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (actionFilter) params.append('action', actionFilter);
      if (searchQuery) params.append('search', searchQuery);
      params.append('limit', '100');

      const res = await api.get(`/audit?${params.toString()}`);
      setLogs(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getActionBadge = (action) => {
    if (action.includes('STATUS')) return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    if (action.includes('SCAN')) return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    if (action.includes('REPORT')) return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    if (action.includes('AUTH') || action.includes('LOGIN')) return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    return 'bg-slate-800 text-slate-300 border-slate-700';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            System Security Audit Logs
          </h1>
          <p className="text-xs text-slate-400 mt-1">Immutable record of administrative actions, scan executions, finding state changes, and report generations</p>
        </div>
        <button
          onClick={fetchAuditLogs}
          className="p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-all"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="glass-panel p-4 rounded-xl border border-slate-800 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search action, resource type, user..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>

        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="bg-slate-900 border border-slate-800 text-xs text-slate-200 rounded-lg px-3 py-1.5 font-mono focus:outline-none"
        >
          <option value="">All Actions</option>
          <option value="FINDING_STATUS_CHANGE">FINDING_STATUS_CHANGE</option>
          <option value="SCAN_TRIGGERED">SCAN_TRIGGERED</option>
          <option value="SCAN_CANCELLED">SCAN_CANCELLED</option>
          <option value="REPORT_GENERATE">REPORT_GENERATE</option>
          <option value="AI_ANALYSIS_PERFORMED">AI_ANALYSIS_PERFORMED</option>
          <option value="PROJECT_CREATE">PROJECT_CREATE</option>
        </select>
      </div>

      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/60 text-slate-400 font-mono border-b border-slate-800 uppercase text-[10px]">
            <tr>
              <th className="py-3.5 px-4">Timestamp</th>
              <th className="py-3.5 px-4">User ID</th>
              <th className="py-3.5 px-4">Action</th>
              <th className="py-3.5 px-4">Resource Type</th>
              <th className="py-3.5 px-4">Resource ID</th>
              <th className="py-3.5 px-4">Forensic Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-800/40">
                <td className="py-3.5 px-4 text-slate-500 text-[11px]">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className="py-3.5 px-4 font-bold text-slate-300">User #{log.user_id}</td>
                <td className="py-3.5 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] border ${getActionBadge(log.action)}`}>
                    {log.action}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-slate-400">{log.resource_type}</td>
                <td className="py-3.5 px-4 text-cyan-400 font-semibold">{log.resource_id}</td>
                <td className="py-3.5 px-4 text-slate-400 text-[11px] truncate max-w-xs">
                  {JSON.stringify(log.details || {})}
                </td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan={6} className="py-10 text-center text-slate-500">
                  No security audit events recorded.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
