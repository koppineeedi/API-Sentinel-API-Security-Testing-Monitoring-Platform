import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Modal } from '../components/common/Modal';
import { FolderGit2, Plus, Globe, Server, Code, Trash2, Search, Eye, Filter, ShieldCheck, Key } from 'lucide-react';

export const InventoryPage = () => {
  const [projects, setProjects] = useState([]);
  const [endpoints, setEndpoints] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [methodFilter, setMethodFilter] = useState('');

  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [isEndpointModalOpen, setIsEndpointModalOpen] = useState(false);

  // New Project Form
  const [projectName, setProjectName] = useState('');
  const [projectTargetUrl, setProjectTargetUrl] = useState('');
  const [projectDescription, setProjectDescription] = useState('');

  // New Endpoint Form
  const [endpointPath, setEndpointPath] = useState('');
  const [endpointMethod, setEndpointMethod] = useState('GET');
  const [endpointDesc, setEndpointDesc] = useState('');

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      fetchEndpoints(selectedProjectId);
    }
  }, [selectedProjectId]);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const res = await api.get('/projects');
      setProjects(res.data);
      if (res.data.length > 0 && !selectedProjectId) {
        setSelectedProjectId(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchEndpoints = async (projId) => {
    try {
      const res = await api.get(`/endpoints?project_id=${projId}`);
      setEndpoints(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      await api.post('/projects', {
        name: projectName,
        target_url: projectTargetUrl,
        description: projectDescription
      });
      setIsProjectModalOpen(false);
      setProjectName('');
      setProjectTargetUrl('');
      setProjectDescription('');
      fetchProjects();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create project');
    }
  };

  const handleCreateEndpoint = async (e) => {
    e.preventDefault();
    if (!selectedProjectId) return;
    try {
      await api.post('/endpoints', {
        project_id: selectedProjectId,
        path: endpointPath,
        method: endpointMethod,
        description: endpointDesc
      });
      setIsEndpointModalOpen(false);
      setEndpointPath('');
      setEndpointDesc('');
      fetchEndpoints(selectedProjectId);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create endpoint');
    }
  };

  const handleDeleteProject = async (projId) => {
    if (!confirm('Are you sure you want to delete this API Project?')) return;
    try {
      await api.delete(`/projects/${projId}`);
      if (selectedProjectId === projId) {
        setSelectedProjectId(null);
      }
      fetchProjects();
    } catch (err) {
      alert(err.response?.data?.detail || 'Delete failed');
    }
  };

  const getMethodBadgeClass = (method) => {
    switch (method.toUpperCase()) {
      case 'GET': return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'POST': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'PUT': return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'DELETE': return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default: return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
    }
  };

  const filteredEndpoints = endpoints.filter(ep => {
    const matchesSearch = ep.path.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (ep.description && ep.description.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesMethod = !methodFilter || ep.method.toUpperCase() === methodFilter.toUpperCase();
    return matchesSearch && matchesMethod;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            API Target Inventory
          </h1>
          <p className="text-xs text-slate-400 mt-1">Manage target applications, OpenAPI schemas, parameters & monitored route catalog</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsProjectModalOpen(true)}
            className="bg-cyan-500 text-slate-950 font-semibold px-3.5 py-2 rounded-lg text-xs flex items-center gap-2 hover:bg-cyan-400 transition-all shadow-lg shadow-cyan-500/10"
          >
            <Plus className="w-4 h-4" />
            Add API Project
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Projects List */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Monitored Projects</h3>
          <div className="space-y-2">
            {projects.map((proj) => (
              <div
                key={proj.id}
                onClick={() => setSelectedProjectId(proj.id)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  selectedProjectId === proj.id
                    ? 'bg-slate-800/80 border-cyan-500/50 shadow-lg shadow-cyan-500/5'
                    : 'glass-panel hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-sm text-slate-100">{proj.name}</h4>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteProject(proj.id);
                    }}
                    className="text-slate-500 hover:text-rose-400 p-1 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400 font-mono mt-1">
                  <Globe className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  <span className="truncate">{proj.target_url}</span>
                </div>
                <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-800 text-[11px] font-mono text-slate-500">
                  <span>Endpoints: {proj.endpoints_count || 0}</span>
                  <span>Findings: {proj.findings_count || 0}</span>
                </div>
              </div>
            ))}

            {projects.length === 0 && (
              <div className="glass-panel p-6 rounded-xl text-center text-xs text-slate-500 font-mono">
                No API projects configured. Click "Add API Project" to begin authorized security scanning.
              </div>
            )}
          </div>
        </div>

        {/* Right: Endpoints Details */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Endpoints Catalog {selectedProjectId && `(Project #${selectedProjectId})`}
            </h3>

            {/* Filter controls */}
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-slate-500" />
                <input
                  type="text"
                  placeholder="Filter path..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>

              <select
                value={methodFilter}
                onChange={(e) => setMethodFilter(e.target.value)}
                className="bg-slate-900 border border-slate-800 text-xs text-slate-200 rounded-lg px-2 py-1 font-mono focus:outline-none"
              >
                <option value="">All Methods</option>
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
                <option value="PATCH">PATCH</option>
              </select>

              {selectedProjectId && (
                <button
                  onClick={() => setIsEndpointModalOpen(true)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs px-2.5 py-1 rounded-lg flex items-center gap-1 font-medium shrink-0"
                >
                  <Plus className="w-3.5 h-3.5" /> Add Endpoint
                </button>
              )}
            </div>
          </div>

          <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/60 text-slate-400 font-mono border-b border-slate-800 uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Method</th>
                  <th className="py-3 px-4">Path</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4">Auth</th>
                  <th className="py-3 px-4 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
                {filteredEndpoints.map((ep) => (
                  <tr key={ep.id} className="hover:bg-slate-800/40">
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getMethodBadgeClass(ep.method)}`}>
                        {ep.method}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-cyan-400 font-medium">{ep.path}</td>
                    <td className="py-3 px-4 text-slate-400 font-sans">{ep.description || 'N/A'}</td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">{ep.auth_type || 'Bearer JWT'}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedEndpoint(ep)}
                        className="bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 px-2 py-0.5 rounded text-[11px] flex items-center gap-1 ml-auto"
                      >
                        <Eye className="w-3 h-3" /> View
                      </button>
                    </td>
                  </tr>
                ))}
                {filteredEndpoints.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-500 font-mono">
                      No endpoints found for this project.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Endpoint Inspection Modal */}
      {selectedEndpoint && (
        <Modal isOpen={!!selectedEndpoint} onClose={() => setSelectedEndpoint(null)} title="Endpoint Specification & Schema Inspector">
          <div className="space-y-4 max-h-[70vh] overflow-y-auto font-mono text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${getMethodBadgeClass(selectedEndpoint.method)}`}>
                  {selectedEndpoint.method}
                </span>
                <span className="text-cyan-400 font-bold">{selectedEndpoint.path}</span>
              </div>
              <span className="text-slate-400 text-[11px]">Auth: {selectedEndpoint.auth_type || 'Required'}</span>
            </div>

            <div>
              <h5 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">Description</h5>
              <p className="text-slate-300 font-sans">{selectedEndpoint.description || 'No description provided.'}</p>
            </div>

            <div>
              <h5 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">Parameters & Headers</h5>
              <pre className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-300 overflow-x-auto text-[11px]">
                {JSON.stringify(selectedEndpoint.parameters || { "Header": "Authorization: Bearer <JWT>" }, null, 2)}
              </pre>
            </div>
          </div>
        </Modal>
      )}

      {/* Add Project Modal */}
      <Modal isOpen={isProjectModalOpen} onClose={() => setIsProjectModalOpen(false)} title="Create New API Target Project">
        <form onSubmit={handleCreateProject} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Project Name</label>
            <input
              type="text"
              required
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="e.g. Staging Auth Microservice"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Target Base URL (Authorized Systems Only)</label>
            <input
              type="text"
              required
              value={projectTargetUrl}
              onChange={(e) => setProjectTargetUrl(e.target.value)}
              placeholder="http://localhost:8000 or http://10.0.0.15:8080"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Description</label>
            <textarea
              value={projectDescription}
              onChange={(e) => setProjectDescription(e.target.value)}
              placeholder="Authorized internal lab or staging deployment environment"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
              rows={3}
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsProjectModalOpen(false)}
              className="px-4 py-2 text-xs text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-4 py-2 rounded-xl text-xs"
            >
              Create Project
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Endpoint Modal */}
      <Modal isOpen={isEndpointModalOpen} onClose={() => setIsEndpointModalOpen(false)} title="Add Endpoint to Catalog">
        <form onSubmit={handleCreateEndpoint} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">HTTP Method</label>
            <select
              value={endpointMethod}
              onChange={(e) => setEndpointMethod(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
              <option value="PATCH">PATCH</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Endpoint Path</label>
            <input
              type="text"
              required
              value={endpointPath}
              onChange={(e) => setEndpointPath(e.target.value)}
              placeholder="/api/v1/users/{id}"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Description</label>
            <input
              type="text"
              value={endpointDesc}
              onChange={(e) => setEndpointDesc(e.target.value)}
              placeholder="Retrieves user profile details"
              className="w-full bg-slate-900 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsEndpointModalOpen(false)}
              className="px-4 py-2 text-xs text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-4 py-2 rounded-xl text-xs"
            >
              Save Endpoint
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
