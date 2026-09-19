import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { StatCard } from '../components/common/StatCard';
import { SeverityBadge, StatusBadge } from '../components/common/Badge';
import { FolderGit2, AlertTriangle, ShieldAlert, Activity, PlaySquare, ArrowUpRight, RefreshCw, ShieldCheck, Zap } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Link } from 'react-router-dom';

export const DashboardPage = () => {
  const [projects, setProjects] = useState([]);
  const [endpoints, setEndpoints] = useState([]);
  const [findings, setFindings] = useState([]);
  const [scans, setScans] = useState([]);
  const [traffic, setTraffic] = useState([]);
  const [statusStats, setStatusStats] = useState({});
  const [riskScore, setRiskScore] = useState(100.0);
  const [riskStatusLabel, setRiskStatusLabel] = useState('PRISTINE');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [projRes, epRes, findRes, scanRes, trafRes, statusRes] = await Promise.all([
        api.get('/projects'),
        api.get('/endpoints'),
        api.get('/findings'),
        api.get('/scans'),
        api.get('/traffic?limit=50'),
        api.get('/traffic/stats/status-codes')
      ]);

      setProjects(projRes.data);
      setEndpoints(epRes.data);
      setFindings(findRes.data);
      setScans(scanRes.data);
      setTraffic(trafRes.data);
      setStatusStats(statusRes.data || {});

      if (projRes.data.length > 0) {
        try {
          const scoreRes = await api.get(`/risk/score/${projRes.data[0].id}`);
          setRiskScore(scoreRes.data.security_score || 100.0);
          setRiskStatusLabel(scoreRes.data.status_label || 'PRISTINE');
        } catch (e) {
          console.error("Error fetching score:", e);
        }
      }
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const criticalCount = findings.filter(f => f.severity === 'CRITICAL' && f.status !== 'RESOLVED').length;
  const highCount = findings.filter(f => f.severity === 'HIGH' && f.status !== 'RESOLVED').length;
  const mediumCount = findings.filter(f => f.severity === 'MEDIUM' && f.status !== 'RESOLVED').length;
  const lowCount = findings.filter(f => f.severity === 'LOW' && f.status !== 'RESOLVED').length;
  const openCount = findings.filter(f => f.status === 'OPEN').length;

  const severityData = [
    { name: 'CRITICAL', value: findings.filter(f => f.severity === 'CRITICAL').length, color: '#ef4444' },
    { name: 'HIGH', value: findings.filter(f => f.severity === 'HIGH').length, color: '#f59e0b' },
    { name: 'MEDIUM', value: findings.filter(f => f.severity === 'MEDIUM').length, color: '#eab308' },
    { name: 'LOW', value: findings.filter(f => f.severity === 'LOW').length, color: '#10b981' },
    { name: 'INFO', value: findings.filter(f => f.severity === 'INFO').length, color: '#06b6d4' },
  ].filter(d => d.value > 0);

  const statusDistributionData = [
    { name: '2xx Success', value: statusStats['2xx'] || 0, color: '#10b981' },
    { name: '3xx Redirect', value: statusStats['3xx'] || 0, color: '#06b6d4' },
    { name: '4xx Client Err', value: statusStats['4xx'] || 0, color: '#f59e0b' },
    { name: '5xx Server Err', value: statusStats['5xx'] || 0, color: '#ef4444' },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            Security Operations Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-1">Real-time threat metrics, risk score gauge & active inventory telemetry</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboardData}
            className="p-2 bg-slate-900 border border-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-all"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <Link
            to="/scans"
            className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-3.5 py-2 rounded-lg text-xs flex items-center gap-2 transition-all shadow-lg shadow-cyan-500/10"
          >
            <PlaySquare className="w-4 h-4" />
            Launch Active Scan
          </Link>
        </div>
      </div>

      {/* Stat Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard title="Monitored APIs" value={projects.length} subtitle={`${endpoints.length} endpoints`} icon={FolderGit2} color="cyan" />
        <StatCard title="API Risk Score" value={`${riskScore.toFixed(1)}`} subtitle={riskStatusLabel} icon={ShieldCheck} color="emerald" />
        <StatCard title="Critical Threats" value={criticalCount} subtitle="Immediate action required" icon={ShieldAlert} color="rose" />
        <StatCard title="High Vulnerabilities" value={highCount} subtitle="Elevated exposure" icon={AlertTriangle} color="amber" />
        <StatCard title="Open Findings" value={openCount} subtitle="Pending resolution" icon={Activity} color="purple" />
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Severity Donut */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-slate-200">Finding Severity Breakdown</h3>
            <span className="text-[11px] font-mono text-slate-400">{findings.length} Total</span>
          </div>
          <div className="h-56">
            {severityData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0d1424', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500 font-mono">
                No findings logged yet
              </div>
            )}
          </div>
          <div className="grid grid-cols-3 gap-2 text-center pt-2 border-t border-slate-800/80">
            {severityData.map((item) => (
              <div key={item.name} className="text-xs">
                <span className="text-[10px] font-mono block text-slate-400">{item.name}</span>
                <span className="font-mono font-bold text-slate-200">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* HTTP Status Code Distribution */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-slate-200">HTTP Status Distribution</h3>
            <span className="text-[11px] font-mono text-cyan-400">Traffic Telemetry</span>
          </div>
          <div className="h-56">
            {statusDistributionData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {statusDistributionData.map((entry, index) => (
                      <Cell key={`status-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0d1424', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500 font-mono">
                No HTTP traffic recorded yet
              </div>
            )}
          </div>
          <div className="grid grid-cols-2 gap-2 text-center pt-2 border-t border-slate-800/80">
            {statusDistributionData.map((item) => (
              <div key={item.name} className="text-xs">
                <span className="text-[10px] font-mono block text-slate-400">{item.name}</span>
                <span className="font-mono font-bold text-slate-200">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Scans Overview */}
        <div className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-200">Recent Audit Jobs</h3>
            <Link to="/scans" className="text-xs text-cyan-400 hover:underline">View All</Link>
          </div>
          <div className="space-y-3 overflow-y-auto max-h-56 pr-1">
            {scans.slice(0, 4).map((s) => (
              <div key={s.id} className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-slate-200 block truncate max-w-[140px]">{s.name}</span>
                  <span className="text-[10px] text-slate-500 font-mono">{s.scan_type} • {s.progress}%</span>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${s.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'}`}>
                  {s.status}
                </span>
              </div>
            ))}
            {scans.length === 0 && (
              <div className="text-center text-xs text-slate-500 font-mono py-8">
                No recent security scans executed.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Security Findings Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-200">Active Vulnerability Catalog</h3>
          <Link to="/findings" className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
            View All Findings <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/60 text-slate-400 font-mono border-b border-slate-800 uppercase text-[10px]">
              <tr>
                <th className="py-3 px-6">Severity</th>
                <th className="py-3 px-6">Rule ID</th>
                <th className="py-3 px-6">Vulnerability Title</th>
                <th className="py-3 px-6">Status</th>
                <th className="py-3 px-6">Confidence</th>
                <th className="py-3 px-6">Discovered</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {findings.slice(0, 5).map((f) => (
                <tr key={f.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-6">
                    <SeverityBadge severity={f.severity} />
                  </td>
                  <td className="py-3 px-6 font-mono text-cyan-400 text-[11px]">{f.rule_id || 'SEC-CORE'}</td>
                  <td className="py-3 px-6 font-medium text-slate-200">{f.title}</td>
                  <td className="py-3 px-6">
                    <StatusBadge status={f.status} />
                  </td>
                  <td className="py-3 px-6 font-mono text-[11px] text-slate-400">{f.confidence}</td>
                  <td className="py-3 px-6 font-mono text-[11px] text-slate-500">
                    {new Date(f.discovered_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
              {findings.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 font-mono text-xs">
                    No active security findings. Trigger a scan from the Scans menu.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
