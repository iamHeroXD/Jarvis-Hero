import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Lock, User, Key, ArrowRight, Zap, AlertCircle } from 'lucide-react';
import { authApi, setToken } from '../services/api';
import { useAuthStore } from '../store';

export default function LoginPage() {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  const [username, setUsername] = useState('rohan');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleQuickUnlock = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await authApi.quickUnlock();
      setAuth(res.access_token, res.user_id, res.display_name, res.is_owner);
      setToken(res.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Quick unlock failed. Please enter credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleStandardLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Please enter username and password.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const res = await authApi.login(username.trim(), password.trim());
      setAuth(res.access_token, res.user_id, res.display_name, res.is_owner);
      setToken(res.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-surface-0 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background radial glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-accent/15 via-transparent to-transparent pointer-events-none" />

      {/* Main Container */}
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="card w-full max-w-md p-8 border border-accent/40 shadow-glow relative z-10 flex flex-col items-center"
      >
        {/* Arc Reactor Holographic Pulse */}
        <div className="relative w-24 h-24 mb-6 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border-2 border-cyan-400/40 animate-ping opacity-30" />
          <div className="absolute inset-1 rounded-full border border-accent/50 animate-pulse" />
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent to-accent-cyan flex items-center justify-center shadow-glow">
            <span className="text-white font-extrabold text-2xl font-mono tracking-widest">J</span>
          </div>
        </div>

        <h1 className="text-xl font-bold text-text-primary tracking-wider mb-1">PROJECT J.A.R.V.I.S.</h1>
        <p className="text-xs text-text-secondary text-center mb-6">
          Personal AI Command Centre &bull; Systems Online
        </p>

        {/* Quick Owner Access Button */}
        <button
          onClick={handleQuickUnlock}
          disabled={loading}
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-accent to-accent-cyan hover:from-accent/90 hover:to-accent-cyan/90 text-white font-semibold text-xs shadow-glow flex items-center justify-center gap-2 mb-4 transition-all disabled:opacity-50"
        >
          <Zap size={16} className="text-yellow-300" />
          <span>Quick Unlock as Owner (Rohan)</span>
          <ArrowRight size={14} />
        </button>

        <div className="w-full flex items-center gap-3 my-2">
          <div className="flex-1 h-px bg-surface-border" />
          <span className="text-[10px] text-text-muted uppercase tracking-widest font-mono">or password</span>
          <div className="flex-1 h-px bg-surface-border" />
        </div>

        {/* Standard Form */}
        <form onSubmit={handleStandardLogin} className="w-full space-y-3 mt-2">
          <div>
            <label className="block text-[11px] font-semibold text-text-secondary mb-1">Username</label>
            <div className="relative">
              <User size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="rohan"
                className="w-full input text-xs pl-9 pr-3 py-2 bg-surface-2 border border-surface-border rounded-lg"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-text-secondary mb-1">Password</label>
            <div className="relative">
              <Key size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password..."
                className="w-full input text-xs pl-9 pr-3 py-2 bg-surface-2 border border-surface-border rounded-lg"
              />
            </div>
          </div>

          {error && (
            <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle size={14} className="flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl bg-surface-3 hover:bg-surface-4 text-text-primary font-semibold text-xs border border-surface-border transition-all flex items-center justify-center gap-2 disabled:opacity-50 mt-4"
          >
            <Lock size={13} />
            <span>{loading ? 'Authenticating...' : 'Sign In with Password'}</span>
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-surface-border/50 text-center text-[11px] text-text-muted font-mono">
          Security: Local Windows Credential Enclave &bull; DPAPI
        </div>
      </motion.div>
    </div>
  );
}
