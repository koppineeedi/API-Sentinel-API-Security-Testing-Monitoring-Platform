import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Activity, ShieldAlert, Code, Search } from 'lucide-react';
import { Modal } from '../components/common/Modal';

export const TrafficPage = () => {
  const [traffic, setTraffic] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [searchFilter, setSearchFilter] = useState('');

  useEffect(() => {
    fetchTraffic();
  }, []);

  const fetchTraffic = async () => {
    try {
      const res = await api.get('/traffic?limit=100');
      setTraffic(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const getStatusColor = (code) => {
    if (code >= 500) return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
    if (code >= 400) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    if (code >= 300) return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30';
    return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
  };

  const filteredTraffic = traffic.filter(e => 
    e.request_url.toLowerCase().includes(searchFilter.toLowerCase()) ||
    e.request_method.toLowerCase().includes(searchFilter.toLowerCase()) ||
    (e.client_ip && e.client_ip.includes(searchFilter))
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            API Traffic Monitor
          </h1>
          <p className="text-xs text-slate-400 mt-1">Real-time API transaction stream, latency breakdown, and anomaly detection logs</p>
        </div>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search path, method, IP..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>
      </div>

      <div className="glass-panel rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/60 text-slate-400 font-mono border-b border-slate-800 uppercase text-[10px]">
            <tr>
              <th className="py-3 px-4">Method</th>
              <th className="py-3 px-4">Request URL</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Latency</th>
              <th className="py-3 px-4">Client IP</th>
              <th className="py-3 px-4">Anomaly Flags</th>
              <th className="py-3 px-4">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
            {filteredTraffic.map((t) => (
              <tr
                key={t.id}
                onClick={() => setSelectedEvent(t)}
                className="hover:bg-slate-800/40 cursor-pointer transition-colors"
              >
                <td className="py-3 px-4 font-bold text-slate-200">{t.request_method}</td>
                <td className="py-3 px-4 text-cyan-400 truncate max-w-xs">{t.request_url}</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] border ${getStatusColor(t.response_status)}`}>
                    {t.response_status}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-400 text-[11px]">{t.response_time_ms} ms</td>
                <td className="py-3 px-4 text-slate-400 text-[11px]">{t.client_ip || '127.0.0.1'}</td>
                <td className="py-3 px-4">
                  {t.flag_reasons && t.flag_reasons.length > 0 ? (
                    <span className="px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded text-[10px]">
                      {t.flag_reasons[0]}
                    </span>
                  ) : (
                    <span className="text-slate-600 text-[10px]">Normal</span>
                  )}
                </td>
                <td className="py-3 px-4 text-slate-500 text-[11px]">
                  {new Date(t.timestamp).toLocaleTimeString()}
                </td>
              </tr>
            ))}
            {filteredTraffic.length === 0 && (
              <tr>
                <td colSpan={7} className="py-10 text-center text-slate-500">
                  No API traffic events currently recorded.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedEvent && (
        <Modal isOpen={!!selectedEvent} onClose={() => setSelectedEvent(null)} title="HTTP Transaction Trace">
          <div className="space-y-4 max-h-[70vh] overflow-y-auto">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="font-bold text-cyan-400">{selectedEvent.request_method} {selectedEvent.request_url}</span>
              <span className={`px-2 py-0.5 rounded border ${getStatusColor(selectedEvent.response_status)}`}>
                HTTP {selectedEvent.response_status}
              </span>
            </div>

            <div>
              <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Headers</h5>
              <pre className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-[11px] font-mono text-slate-300 overflow-x-auto">
                {JSON.stringify(selectedEvent.headers || { "User-Agent": "Sentinel-Monitor/1.0" }, null, 2)}
              </pre>
            </div>

            <div>
              <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Payload</h5>
              <pre className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-[11px] font-mono text-cyan-300 overflow-x-auto">
                {selectedEvent.payload || 'No body payload included'}
              </pre>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
