// Setup wizard — first-run owner account creation + Gemini API key
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Key, CheckCircle, AlertCircle, Eye, EyeOff, ExternalLink } from 'lucide-react';
import { authApi, settingsApi, setToken } from '../services/api';
import { useAuthStore } from '../store';

interface SetupProps {
  onComplete: () => void;
}

export default function SetupWizard({ onComplete }: SetupProps) {
  const [step, setStep] = useState<'account' | 'api_key' | 'done'>('account');
  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { setAuth } = useAuthStore();

  const handleCreateAccount = async () => {
    if (!username.trim() || !password.trim() || !displayName.trim()) {
      setError('All fields are required.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const result = await authApi.setup(username, displayName, password);
      setAuth(result.access_token, result.user_id, result.display_name, result.is_owner);
      setToken(result.access_token);
      setStep('api_key');
    } catch (err: any) {
      setError(err.message || 'Failed to create account.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveApiKey = async () => {
    if (!apiKey.trim()) {
      setError('API key is required for AI functionality.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      await settingsApi.setGeminiKey(apiKey.trim());
      setApiKey(''); // Clear from memory
      setStep('done');
    } catch (err: any) {
      setError(err.message || 'Failed to store API key.');
    } finally {
      setLoading(false);
    }
  };

  const handleSkipApiKey = () => {
    setStep('done');
  };

  return (
    <div className="min-h-screen bg-surface-0 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-accent to-accent-cyan mb-4">
            <span className="text-white font-bold text-2xl">J</span>
          </div>
          <h1 className="text-2xl font-semibold text-text-primary">J.A.R.V.I.S.</h1>
          <p className="text-text-secondary text-sm mt-1">First-time setup</p>
        </div>

        {/* Step indicators */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {(['account', 'api_key', 'done'] as const).map((s, i) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                step === s ? 'bg-accent text-white'
                : i < ['account', 'api_key', 'done'].indexOf(step) ? 'bg-status-success text-white'
                : 'bg-surface-4 text-text-muted'
              }`}>
                {i < ['account', 'api_key', 'done'].indexOf(step) ? '✓' : i + 1}
              </div>
              {i < 2 && <div className="w-8 h-px bg-surface-border" />}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 'account' && (
            <motion.div
              key="account"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="card p-6 space-y-4"
            >
              <div className="flex items-center gap-2 mb-2">
                <User size={16} className="text-accent" />
                <h2 className="font-medium text-text-primary">Create Owner Account</h2>
              </div>
              <p className="text-sm text-text-secondary">
                This account will be the sole owner of this JARVIS installation. Keep your password secure.
              </p>

              <div className="space-y-3">
                <div>
                  <label className="text-xs text-text-muted mb-1 block">Your name</label>
                  <input
                    className="input selectable"
                    placeholder="e.g. Rohan"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-xs text-text-muted mb-1 block">Username</label>
                  <input
                    className="input selectable"
                    placeholder="e.g. rohan"
                    value={username}
                    onChange={(e) => setUsername(e.target.value.toLowerCase().replace(/\s/g, ''))}
                  />
                </div>
                <div>
                  <label className="text-xs text-text-muted mb-1 block">Password</label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      className="input selectable pr-10"
                      placeholder="Min. 8 characters"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleCreateAccount()}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted"
                    >
                      {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                  </div>
                </div>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-sm text-status-error bg-status-error/10 rounded-lg px-3 py-2">
                  <AlertCircle size={14} />
                  {error}
                </div>
              )}

              <button
                onClick={handleCreateAccount}
                disabled={loading}
                className="btn-primary w-full"
              >
                {loading ? 'Creating account...' : 'Create Account'}
              </button>
            </motion.div>
          )}

          {step === 'api_key' && (
            <motion.div
              key="api_key"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="card p-6 space-y-4"
            >
              <div className="flex items-center gap-2 mb-2">
                <Key size={16} className="text-accent" />
                <h2 className="font-medium text-text-primary">Gemini API Key</h2>
              </div>
              <p className="text-sm text-text-secondary">
                JARVIS uses Google Gemini as its primary AI provider. Your key is stored
                securely in Windows Credential Manager — never in any file or database.
              </p>

              <a
                href="https://ai.google.dev/gemini-api/docs/api-key"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-xs text-accent hover:text-accent-bright"
              >
                <ExternalLink size={12} />
                Get a free API key at ai.google.dev
              </a>

              <div>
                <label className="text-xs text-text-muted mb-1 block">Gemini API Key</label>
                <div className="relative">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    className="input selectable pr-10"
                    placeholder="AIza..."
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted"
                  >
                    {showApiKey ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-sm text-status-error bg-status-error/10 rounded-lg px-3 py-2">
                  <AlertCircle size={14} />
                  {error}
                </div>
              )}

              <div className="flex gap-2">
                <button onClick={handleSkipApiKey} className="btn-ghost flex-1">
                  Skip for now
                </button>
                <button onClick={handleSaveApiKey} disabled={loading} className="btn-primary flex-1">
                  {loading ? 'Saving...' : 'Save & Continue'}
                </button>
              </div>
            </motion.div>
          )}

          {step === 'done' && (
            <motion.div
              key="done"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="card p-6 text-center space-y-4"
            >
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-status-success/20 mb-2">
                <CheckCircle size={28} className="text-status-success" />
              </div>
              <h2 className="font-medium text-text-primary text-lg">JARVIS is ready.</h2>
              <p className="text-sm text-text-secondary">
                Your personal AI assistant is configured and online.
                You can adjust settings at any time.
              </p>
              <button onClick={onComplete} className="btn-primary w-full">
                Open JARVIS
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
