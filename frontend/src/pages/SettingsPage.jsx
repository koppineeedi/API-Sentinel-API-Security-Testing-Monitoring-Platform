import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Settings, Lock, ShieldCheck, Users, CheckCircle2, AlertCircle } from 'lucide-react';

export const SettingsPage = () => {
  const { user, changePassword } = useAuth();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pwdMsg, setPwdMsg] = useState({ type: '', text: '' });

  const [rules, setRules] = useState([]);
  const [userList, setUserList] = useState([]);

  useEffect(() => {
    fetchRules();
    if (user?.role === 'ADMIN') {
      fetchUsers();
    }
  }, [user]);

  const fetchRules = async () => {
    try {
      const res = await api.get('/rules');
      setRules(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await api.get('/users');
      setUserList(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleRule = async (ruleId, currentEnabled) => {
    if (user?.role !== 'ADMIN') {
      alert('Rule modification requires ADMIN role.');
      return;
    }
    try {
      const res = await api.patch(`/rules/${ruleId}`, { enabled: !currentEnabled });
      setRules(rules.map(r => r.id === ruleId ? res.data : r));
    } catch (err) {
      alert(err.response?.data?.detail || 'Rule toggle failed');
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setPwdMsg({ type: '', text: '' });
    if (newPassword !== confirmPassword) {
      setPwdMsg({ type: 'error', text: 'New passwords do not match.' });
      return;
    }
    try {
      await changePassword(oldPassword, newPassword);
      setPwdMsg({ type: 'success', text: 'Password successfully updated.' });
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setPwdMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to update password.' });
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          System & Security Settings
        </h1>
        <p className="text-xs text-slate-400 mt-1">Manage user account credentials, security rules, and RBAC directory</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile & Password Change */}
        <div className="space-y-6">
          <div className="glass-panel p-5 rounded-xl border border-slate-800">
            <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-cyan-400" /> User Profile Summary
            </h3>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-slate-800/80">
                <span className="text-slate-400">Full Name:</span>
                <span className="text-slate-200">{user?.full_name || 'N/A'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/80">
                <span className="text-slate-400">Email:</span>
                <span className="text-slate-200">{user?.email}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Assigned Role:</span>
                <span className="text-cyan-400 font-bold">{user?.role}</span>
              </div>
            </div>
          </div>

          <div className="glass-panel p-5 rounded-xl border border-slate-800">
            <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
              <Lock className="w-4 h-4 text-cyan-400" /> Change Password
            </h3>

            {pwdMsg.text && (
              <div className={`mb-3 p-2.5 rounded-lg text-xs flex items-center gap-2 ${
                pwdMsg.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
              }`}>
                {pwdMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                <span>{pwdMsg.text}</span>
              </div>
            )}

            <form onSubmit={handlePasswordSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Current Password</label>
                <input
                  type="password"
                  required
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">New Password</label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Confirm New Password</label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold py-2 rounded-lg text-xs transition-all shadow-lg shadow-cyan-500/10"
              >
                Update Password
              </button>
            </form>
          </div>
        </div>

        {/* Security Rule Catalog */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-5 rounded-xl border border-slate-800">
            <h3 className="text-sm font-semibold text-slate-200 mb-3">Security Rules Catalog</h3>
            <div className="space-y-3">
              {rules.map((r) => (
                <div key={r.id} className="p-3 bg-slate-900/80 border border-slate-800 rounded-lg flex items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-cyan-400">{r.id}</span>
                      <span className="text-xs font-semibold text-slate-100">{r.name}</span>
                      <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">{r.category}</span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{r.description}</p>
                  </div>
                  <button
                    onClick={() => handleToggleRule(r.id, r.enabled)}
                    className={`px-3 py-1 rounded text-[11px] font-mono font-semibold transition-all ${
                      r.enabled
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : 'bg-slate-800 text-slate-500 border border-slate-700'
                    }`}
                  >
                    {r.enabled ? 'ENABLED' : 'DISABLED'}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* User Directory (Admin Only) */}
          {user?.role === 'ADMIN' && (
            <div className="glass-panel p-5 rounded-xl border border-slate-800">
              <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" /> Platform Users Directory (Admin View)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/60 text-slate-400 font-mono border-b border-slate-800 uppercase text-[10px]">
                    <tr>
                      <th className="py-2.5 px-3">ID</th>
                      <th className="py-2.5 px-3">Email</th>
                      <th className="py-2.5 px-3">Full Name</th>
                      <th className="py-2.5 px-3">Role</th>
                      <th className="py-2.5 px-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
                    {userList.map((u) => (
                      <tr key={u.id}>
                        <td className="py-2.5 px-3">{u.id}</td>
                        <td className="py-2.5 px-3 text-cyan-400">{u.email}</td>
                        <td className="py-2.5 px-3 font-sans text-slate-200">{u.full_name || 'N/A'}</td>
                        <td className="py-2.5 px-3 font-bold">{u.role}</td>
                        <td className="py-2.5 px-3 text-emerald-400">{u.is_active ? 'Active' : 'Inactive'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
