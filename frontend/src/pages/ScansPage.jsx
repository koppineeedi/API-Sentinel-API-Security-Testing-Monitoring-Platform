import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Modal } from '../components/common/Modal';
import { PlaySquare, Plus, CheckCircle2, Clock, AlertCircle, RefreshCw, XOctagon, StopCircle, ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const ScansPage = () => {
  const [scans, setScans] = useState([]);
  const [projects, setProjects] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [scanName, setScanName] = useState('');
  const [scanType, setScanType] = useState('FULL');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchScans();
    fetchProjects();
    const interval = setInterval(fetchScans, 3000); // Polling for scan progress
    return () => clearInterval(interval);
  }, []);

  const fetchScans = async () => {
    try {
      const res = await api.get('/scans');
      setScans(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchProjects = async () => {
    try {
      const res = await api.get('/projects');
      setProjects(res.data);
      if (res.data.length > 0 && !selectedProjectId) {
        setSelectedProjectId(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleLaunchScan = async (e) => {
    e.preventDefault();
    if (!selectedProjectId) return;
    setSubmitting(true);
    try {
      const proj = projects.find(p => p.id === parseInt(selectedProjectId));
      await api.post('/scans', {
        project_id: parseInt(selectedProjectId),
        name: scanName || `OWASP Audit - ${proj?.name || 'Target'}`,
        target_url: proj?.target_url || 'http://localhost:8000',
        scan_type: scanType
      });
      setIsModalOpen(false);
      setScanName('');
      fetchScans();
    } catch (err) {
      alert(err.response?.data?.detail || 'Scan launch failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelScan = async (scanId) => {
    if (!window.confirm("Are you sure you want to cancel this active scan job?")) return;
    try {
      await api.post(`/scans/${scanId}/cancel`);
      fetchScans();
    } catch (err) {
      alert(err.response?.data?.detail || 'Cancellation failed');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="flex items-center gap-1.5 text-emerald-400 font-mono text-xs"><CheckCircle2 className="w-4 h-4" /> COMPLETED</span>;
      case 'RUNNING':
        return <span className="flex items-center gap-1.5 text-cyan-400 font-mono text-xs"><RefreshCw className="w-4 h-4 animate-spin" /> RUNNING</span>;
      case 'QUEUED':
        return <span className="flex items-center gap-1.5 text-purple-400 font-mono text-xs"><Clock className="w-4 h-4" /> QUEUED</span>;
      case 'CANCELLED':
        return <span className="flex items-center gap-1.5 text-slate-400 font-mono text-xs"><XOctagon className="w-4 h-4" /> CANCELLED</span>;
      case 'FAILED':
        return <span className="flex items-center gap-1.5 text-rose-400 font-mono text-xs"><AlertCircle className="w-4 h-4" /> FAILED</span>;
      default:
        return <span className="flex items-center gap-1.5 text-slate-400 font-mono text-xs"><Clock className="w-4 h-4" /> PENDING</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            Active Security Scans
          </h1>
          <p className="text-xs text-slate-400 mt-1">Configure & execute vulnerability scanning jobs against authorized targets</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-3.5 py-2 rounded-lg text-xs flex items-center gap-2 transition-all shadow-lg shadow-cyan-500/10"
        >
          <PlaySquare className="w-4 h-4" />
          Launch New Scan Job
        </button>
      </div>

      {/* Scans Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/60 text-slate-400 font-mono border-b border-slate-800 uppercase text-[10px]">
            <tr>
              <th className="py-3.5 px-4">Scan Name</th>
              <th className="py-3.5 px-4">Profile</th>
              <th className="py-3.5 px-4">Target URL</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4">Progress</th>
              <th className="py-3.5 px-4">Findings</th>
              <th className="py-3.5 px-4">Started At</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {scans.map((s) => (
              <tr key={s.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4 font-semibold text-slate-100 font-sans">{s.name}</td>
                <td className="py-3.5 px-4 text-cyan-400 text-[11px]">{s.scan_type}</td>
                <td className="py-3.5 px-4 text-slate-400 text-[11px] truncate max-w-xs">{s.target_url}</td>
                <td className="py-3.5 px-4">{getStatusBadge(s.status)}</td>
                <td className="py-3.5 px-4">
                  <div className="w-24 bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
                    <div
                      className={`h-full transition-all duration-300 ${s.status === 'COMPLETED' ? 'bg-emerald-500' : s.status === 'CANCELLED' ? 'bg-slate-600' : s.status === 'FAILED' ? 'bg-rose-500' : 'bg-cyan-500'}`}
                      style={{ width: `${s.progress}%` }}
                    ></div>
                  </div>
                  <span className="text-[10px] text-slate-400 mt-0.5 block">{s.progress}%</span>
                </td>
                <td className="py-3.5 px-4 text-amber-400 font-bold">{s.findings_count}</td>
                <td className="py-3.5 px-4 text-slate-500 text-[11px]">
                  {s.started_at ? new Date(s.started_at).toLocaleString() : 'Queued'}
                </td>
                <td className="py-3.5 px-4 text-right">
                  {(s.status === 'RUNNING' || s.status === 'QUEUED' || s.status === 'PENDING') ? (
                    <button
                      onClick={() => handleCancelScan(s.id)}
                      className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 px-2.5 py-1 rounded text-[11px] font-mono flex items-center gap-1.5 ml-auto"
                    >
                      <StopCircle className="w-3.5 h-3.5" /> Cancel
                    </button>
                  ) : (
                    <Link
                      to="/findings"
                      className="text-cyan-400 hover:underline text-[11px] flex items-center gap-1 justify-end"
                    >
                      View Findings <ArrowUpRight className="w-3 h-3" />
                    </Link>
                  )}
                </td>
              </tr>
            ))}
            {scans.length === 0 && (
              <tr>
                <td colSpan={8} className="py-10 text-center text-slate-500">
                  No scan jobs currently logged. Click "Launch New Scan Job" above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal Dialog */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Configure & Start Security Scan">
        <form onSubmit={handleLaunchScan} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Target API Project</label>
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name} ({p.target_url})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Scan Job Title</label>
            <input
              type="text"
              value={scanName}
              onChange={(e) => setScanName(e.target.value)}
              placeholder="OWASP API Security Audit 2026"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Scan Strategy Profile</label>
            <select
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              <option value="FULL">FULL (OWASP API Top 10 Complete Audit)</option>
              <option value="BOLA_ONLY">BOLA_ONLY (Broken Object Level Authorization)</option>
              <option value="AUTH_ONLY">AUTH_ONLY (Authentication & JWT Security)</option>
              <option value="PASSIVE">PASSIVE (Security Headers & Information Disclosure)</option>
              <option value="INPUT_VALIDATION_ONLY">INPUT_VALIDATION (Injection & Parameter Tampering)</option>
            </select>
          </div>

          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs text-amber-300 leading-relaxed">
            Note: All scan modules execute non-destructively against explicitly configured authorized targets.
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 text-xs text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5"
            >
              <PlaySquare className="w-4 h-4" /> Start Background Scan
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
