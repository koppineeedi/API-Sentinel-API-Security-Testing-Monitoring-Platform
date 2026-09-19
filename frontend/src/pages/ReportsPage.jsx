import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { FileSpreadsheet, Plus, Download, FileText, CheckCircle2 } from 'lucide-react';
import { Modal } from '../components/common/Modal';

export const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [projects, setProjects] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [reportTitle, setReportTitle] = useState('');
  const [reportType, setReportType] = useState('EXECUTIVE_SUMMARY');
  const [reportFormat, setReportFormat] = useState('HTML');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchReports();
    fetchProjects();
  }, []);

  const fetchReports = async () => {
    try {
      const res = await api.get('/reports');
      setReports(res.data);
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

  const handleGenerateReport = async (e) => {
    e.preventDefault();
    if (!selectedProjectId) return;
    setGenerating(true);
    try {
      const proj = projects.find(p => p.id === parseInt(selectedProjectId));
      await api.post('/reports', {
        project_id: parseInt(selectedProjectId),
        title: reportTitle || `Executive Security Summary - ${proj?.name}`,
        report_type: reportType,
        format: reportFormat
      });
      setIsModalOpen(false);
      setReportTitle('');
      fetchReports();
    } catch (err) {
      alert(err.response?.data?.detail || 'Report generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = (reportId, format) => {
    const fmt = format?.toLowerCase() === 'pdf' ? 'pdf' : 'html';
    const token = localStorage.getItem('sentinel_token');
    // Open download link in browser
    window.open(`/api/v1/reports/${reportId}/download/${fmt}?token=${token}`, '_blank');
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            Security Assessment & Compliance Reports
          </h1>
          <p className="text-xs text-slate-400 mt-1">Export executive vulnerability summaries, compliance audits, and HTML/PDF remediation docs</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-3.5 py-2 rounded-lg text-xs flex items-center gap-2 transition-all shadow-lg shadow-cyan-500/10"
        >
          <FileSpreadsheet className="w-4 h-4" />
          Generate New Report
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reports.map((rep) => (
          <div key={rep.id} className="glass-panel p-5 rounded-xl border border-slate-800 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded font-mono text-[10px] font-bold">
                  {rep.format}
                </span>
                <span className="text-[11px] font-mono text-slate-500">
                  {new Date(rep.created_at).toLocaleDateString()}
                </span>
              </div>
              <h4 className="font-semibold text-sm text-slate-100">{rep.title}</h4>
              <p className="text-xs text-slate-400 mt-1 font-mono">Type: {rep.report_type}</p>
            </div>

            <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-500 font-mono">Status: Ready</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDownload(rep.id, 'html')}
                  className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1 bg-cyan-500/10 border border-cyan-500/20 px-2 py-1 rounded"
                >
                  <Download className="w-3.5 h-3.5" /> HTML
                </button>
                <button
                  onClick={() => handleDownload(rep.id, 'pdf')}
                  className="text-xs text-purple-400 hover:text-purple-300 font-medium flex items-center gap-1 bg-purple-500/10 border border-purple-500/20 px-2 py-1 rounded"
                >
                  <Download className="w-3.5 h-3.5" /> PDF
                </button>
              </div>
            </div>
          </div>
        ))}

        {reports.length === 0 && (
          <div className="col-span-full glass-panel p-10 rounded-xl text-center text-xs font-mono text-slate-500">
            No compliance reports generated yet. Click "Generate New Report" to create an executive summary.
          </div>
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Generate Security Report">
        <form onSubmit={handleGenerateReport} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Target API Project</label>
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Report Title</label>
            <input
              type="text"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              placeholder="Q3 API Security Posture Audit"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Report Type</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              <option value="EXECUTIVE_SUMMARY">Executive Summary (CISO / Management)</option>
              <option value="TECHNICAL_DETAILED">Technical Detailed (Developers / SecOps)</option>
              <option value="COMPLIANCE">Compliance & OWASP API Top 10 Mapping</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Export Format</label>
            <select
              value={reportFormat}
              onChange={(e) => setReportFormat(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              <option value="HTML">HTML Interactive Report</option>
              <option value="PDF">PDF Document</option>
            </select>
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
              disabled={generating}
              className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5"
            >
              <FileSpreadsheet className="w-4 h-4" /> Generate Report
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
