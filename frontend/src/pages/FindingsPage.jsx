import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { SeverityBadge, StatusBadge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { 
  AlertTriangle, Filter, Eye, CheckCircle2, XCircle, Sparkles, Code, 
  Search, ArrowUpDown, ChevronLeft, ChevronRight, ShieldAlert, FileText, RefreshCw, AlertOctagon, CornerUpLeft
} from 'lucide-react';

import { formatIST } from '../utils/dateFormatter';

export const FindingsPage = () => {
  const [findings, setFindings] = useState([]);
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [confidenceFilter, setConfidenceFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('discovered_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const [selectedFinding, setSelectedFinding] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loadingAi, setLoadingAi] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFindings();
  }, [severityFilter, statusFilter, confidenceFilter, categoryFilter, searchQuery, sortBy, sortOrder, currentPage]);

  const fetchFindings = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (severityFilter) params.append('severity', severityFilter);
      if (statusFilter) params.append('status', statusFilter);
      if (confidenceFilter) params.append('confidence', confidenceFilter);
      if (categoryFilter) params.append('category', categoryFilter);
      if (searchQuery) params.append('search', searchQuery);
      if (sortBy) params.append('sort_by', sortBy);
      if (sortOrder) params.append('sort_order', sortOrder);
      params.append('skip', (currentPage - 1) * pageSize);
      params.append('limit', pageSize);

      const res = await api.get(`/findings?${params.toString()}`);
      setFindings(res.data);
    } catch (err) {
      console.error("Error fetching findings:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleStateAction = async (findingId, actionEndpoint) => {
    try {
      const res = await api.post(`/findings/${findingId}/${actionEndpoint}`);
      setFindings(findings.map(f => f.id === findingId ? res.data : f));
      if (selectedFinding?.id === findingId) {
        setSelectedFinding(res.data);
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Status update failed');
    }
  };

  const handleGenerateAiAnalysis = async (findingId) => {
    setLoadingAi(true);
    try {
      const res = await api.post('/ai/analyze', { finding_id: findingId });
      setAiAnalysis(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || 'AI analysis failed');
    } finally {
      setLoadingAi(false);
    }
  };

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            Vulnerability Findings Catalog
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Normalized security findings, forensic request evidence, and remediation lifecycle
          </p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="glass-panel p-4 rounded-xl border border-slate-800 space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
          {/* Search */}
          <div className="relative md:col-span-2">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search title, description, rule ID..."
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          {/* Severity */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300">
            <Filter className="w-3 h-3 text-slate-500" />
            <select
              value={severityFilter}
              onChange={(e) => { setSeverityFilter(e.target.value); setCurrentPage(1); }}
              className="w-full bg-transparent text-slate-200 focus:outline-none font-mono text-xs"
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
              <option value="INFO">INFO</option>
            </select>
          </div>

          {/* Status */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300">
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}
              className="w-full bg-transparent text-slate-200 focus:outline-none font-mono text-xs"
            >
              <option value="">All Statuses</option>
              <option value="OPEN">OPEN</option>
              <option value="CONFIRMED">CONFIRMED</option>
              <option value="FALSE_POSITIVE">FALSE_POSITIVE</option>
              <option value="RESOLVED">RESOLVED</option>
            </select>
          </div>

          {/* Confidence */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300">
            <select
              value={confidenceFilter}
              onChange={(e) => { setConfidenceFilter(e.target.value); setCurrentPage(1); }}
              className="w-full bg-transparent text-slate-200 focus:outline-none font-mono text-xs"
            >
              <option value="">All Confidence</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>
        </div>
      </div>

      {/* Findings Table */}
      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/60 text-slate-400 font-mono border-b border-slate-800 uppercase text-[10px]">
            <tr>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-200" onClick={() => toggleSort('severity')}>
                <div className="flex items-center gap-1">Severity <ArrowUpDown className="w-3 h-3" /></div>
              </th>
              <th className="py-3 px-4">Rule ID</th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-200" onClick={() => toggleSort('title')}>
                <div className="flex items-center gap-1">Vulnerability Title <ArrowUpDown className="w-3 h-3" /></div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-200" onClick={() => toggleSort('status')}>
                <div className="flex items-center gap-1">Status <ArrowUpDown className="w-3 h-3" /></div>
              </th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-200" onClick={() => toggleSort('discovered_at')}>
                <div className="flex items-center gap-1">First Seen <ArrowUpDown className="w-3 h-3" /></div>
              </th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {loading ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-500 font-mono text-xs">
                  <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-cyan-400" />
                  Fetching security findings...
                </td>
              </tr>
            ) : findings.map((f) => (
              <tr key={f.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4">
                  <SeverityBadge severity={f.severity} />
                </td>
                <td className="py-3.5 px-4 font-mono text-[11px] text-cyan-400">{f.rule_id || 'SEC-RULE'}</td>
                <td className="py-3.5 px-4 font-medium text-slate-100">{f.title}</td>
                <td className="py-3.5 px-4">
                  <StatusBadge status={f.status} />
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-400 text-[11px]">{f.confidence}</td>
                <td className="py-3.5 px-4 font-mono text-slate-500 text-[11px]">
                  {formatIST(f.discovered_at)}
                </td>
                <td className="py-3.5 px-4 text-right">
                  <button
                    onClick={() => {
                      setSelectedFinding(f);
                      setAiAnalysis(null);
                    }}
                    className="bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 px-2.5 py-1 rounded text-[11px] font-mono flex items-center gap-1.5 ml-auto transition-all"
                  >
                    <Eye className="w-3.5 h-3.5" /> Details
                  </button>
                </td>
              </tr>
            ))}
            {!loading && findings.length === 0 && (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-500 font-mono text-xs">
                  No security findings matched the selected criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {/* Pagination Bar */}
        <div className="px-4 py-3 bg-slate-900/40 border-t border-slate-800 flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Page {currentPage}</span>
          <div className="flex items-center gap-2">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              className="p-1 rounded bg-slate-800 border border-slate-700 disabled:opacity-40 hover:bg-slate-700"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              disabled={findings.length < pageSize}
              onClick={() => setCurrentPage(p => p + 1)}
              className="p-1 rounded bg-slate-800 border border-slate-700 disabled:opacity-40 hover:bg-slate-700"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Finding Inspector Modal */}
      {selectedFinding && (
        <Modal isOpen={!!selectedFinding} onClose={() => setSelectedFinding(null)} title="Vulnerability Deep Inspection">
          <div className="space-y-4 max-h-[75vh] overflow-y-auto pr-1">
            {/* Top Badge & State Transitions */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <SeverityBadge severity={selectedFinding.severity} />
                <span className="font-mono text-xs text-cyan-400">{selectedFinding.rule_id}</span>
                <StatusBadge status={selectedFinding.status} />
              </div>
              
              {/* Quick Action State Transition Buttons */}
              <div className="flex flex-wrap items-center gap-1.5">
                {selectedFinding.status !== 'CONFIRMED' && (
                  <button
                    onClick={() => handleStateAction(selectedFinding.id, 'confirm')}
                    className="bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[11px] font-mono px-2 py-1 rounded flex items-center gap-1"
                  >
                    <CheckCircle2 className="w-3 h-3" /> Confirm
                  </button>
                )}
                {selectedFinding.status !== 'RESOLVED' && (
                  <button
                    onClick={() => handleStateAction(selectedFinding.id, 'resolve')}
                    className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[11px] font-mono px-2 py-1 rounded flex items-center gap-1"
                  >
                    <CheckCircle2 className="w-3 h-3" /> Resolve
                  </button>
                )}
                {selectedFinding.status !== 'FALSE_POSITIVE' && (
                  <button
                    onClick={() => handleStateAction(selectedFinding.id, 'false-positive')}
                    className="bg-slate-800 hover:bg-slate-700 text-slate-400 border border-slate-700 text-[11px] font-mono px-2 py-1 rounded flex items-center gap-1"
                  >
                    <AlertOctagon className="w-3 h-3" /> False Positive
                  </button>
                )}
                {selectedFinding.status !== 'OPEN' && (
                  <button
                    onClick={() => handleStateAction(selectedFinding.id, 'reopen')}
                    className="bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/30 text-[11px] font-mono px-2 py-1 rounded flex items-center gap-1"
                  >
                    <CornerUpLeft className="w-3 h-3" /> Reopen
                  </button>
                )}
              </div>
            </div>

            {/* Metadata Section */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800 text-[11px] font-mono">
              <div>
                <span className="text-slate-500 block">First Seen</span>
                <span className="text-slate-200">{formatIST(selectedFinding.discovered_at)}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Last Update</span>
                <span className="text-slate-200">{selectedFinding.resolved_at ? formatIST(selectedFinding.resolved_at) : 'Active'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Confidence</span>
                <span className="text-slate-200">{selectedFinding.confidence}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Rule ID</span>
                <span className="text-cyan-400">{selectedFinding.rule_id}</span>
              </div>
            </div>

            {/* Title & Overview */}
            <div>
              <h4 className="text-sm font-bold text-slate-100">{selectedFinding.title}</h4>
              <p className="text-xs text-slate-300 leading-relaxed mt-1">{selectedFinding.description}</p>
            </div>

            {/* Impact */}
            {selectedFinding.impact && (
              <div className="p-3.5 bg-rose-500/10 border border-rose-500/20 rounded-xl">
                <h5 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5" /> Threat Impact
                </h5>
                <p className="text-xs text-slate-300 leading-relaxed">{selectedFinding.impact}</p>
              </div>
            )}

            {/* Remediation */}
            {selectedFinding.remediation && (
              <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                <h5 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5" /> Recommended Remediation
                </h5>
                <p className="text-xs text-slate-300 leading-relaxed">{selectedFinding.remediation}</p>
              </div>
            )}

            {/* Technical Evidence */}
            {selectedFinding.evidence && (
              <div>
                <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <Code className="w-3.5 h-3.5 text-cyan-400" /> Forensics Evidence
                </h5>
                <pre className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-[11px] font-mono text-cyan-300 overflow-x-auto whitespace-pre-wrap">
                  {selectedFinding.evidence}
                </pre>
              </div>
            )}

            {/* AI Security Analyst Section */}
            <div className="pt-3 border-t border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <h5 className="text-xs font-semibold text-purple-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4" /> AI Security Analyst Risk Synthesis
                </h5>
                <button
                  onClick={() => handleGenerateAiAnalysis(selectedFinding.id)}
                  disabled={loadingAi}
                  className="bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 border border-purple-500/30 text-xs px-3 py-1 rounded-lg font-medium flex items-center gap-1.5 transition-all"
                >
                  {loadingAi ? 'Synthesizing...' : 'Run AI Analysis'}
                </button>
              </div>

              {aiAnalysis && (
                <div className="p-4 bg-purple-950/20 border border-purple-500/30 rounded-xl space-y-2.5 text-xs">
                  <div className="flex items-center justify-between font-mono text-xs border-b border-purple-500/20 pb-2">
                    <span className="text-purple-400">Model: {aiAnalysis.model_used}</span>
                    <span className="font-bold text-amber-400">Risk Rating: {aiAnalysis.risk_score}/10</span>
                  </div>
                  <div>
                    <span className="font-bold text-purple-300 uppercase text-[10px] block font-mono">OBSERVED EVIDENCE</span>
                    <p className="text-slate-200 mt-0.5">{selectedFinding.evidence || 'Standard request telemetry'}</p>
                  </div>
                  <div>
                    <span className="font-bold text-purple-300 uppercase text-[10px] block font-mono">DETECTION RESULT</span>
                    <p className="text-slate-200 mt-0.5">{aiAnalysis.summary}</p>
                  </div>
                  <div>
                    <span className="font-bold text-purple-300 uppercase text-[10px] block font-mono">AI INTERPRETATION</span>
                    <p className="text-slate-300 mt-0.5">{aiAnalysis.root_cause}</p>
                  </div>
                  <div>
                    <span className="font-bold text-purple-300 uppercase text-[10px] block font-mono">AI RECOMMENDATION</span>
                    <p className="text-slate-300 mt-0.5">{aiAnalysis.custom_remediation}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
