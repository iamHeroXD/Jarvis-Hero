import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, Square, RotateCcw, Copy, ChevronDown, Loader2, Zap } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { clsx } from 'clsx';
import { useAuthStore, useChatStore } from '../store';
import { createChatWebSocket } from '../services/api';
import type { StreamEvent } from '../services/api';
import { format } from 'date-fns';

export default function ChatPage() {
  const { token } = useAuthStore();
  const {
    messages,
    isGenerating,
    toolActivity,
    activeConversationId,
    addMessage,
    appendToLastMessage,
    setLastMessageComplete,
    setGenerating,
    setToolActivity,
    setActiveConversationId,
  } = useChatStore();

  const [input, setInput] = useState('');
  const [wsReady, setWsReady] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, toolActivity]);

  // WebSocket connection
  useEffect(() => {
    if (!token) return;

    const ws = createChatWebSocket(handleStreamEvent, () => {
      setWsReady(false);
      // Reconnect after 2s
      setTimeout(() => {
        if (token) connectWs();
      }, 2000);
    });

    wsRef.current = ws;
    ws.onopen = () => setWsReady(true);

    return () => {
      ws.close();
    };
  }, [token]);

  const connectWs = useCallback(() => {
    if (!token) return;
    const ws = createChatWebSocket(handleStreamEvent, () => {
      setWsReady(false);
    });
    wsRef.current = ws;
    ws.onopen = () => setWsReady(true);
  }, [token]);

  const handleStreamEvent = useCallback((event: StreamEvent) => {
    switch (event.type) {
      case 'conversation_id':
        setActiveConversationId(event.value);
        break;
      case 'tool_activity':
        setToolActivity(event.action);
        break;
      case 'delta':
        appendToLastMessage(event.text);
        break;
      case 'completed':
        setLastMessageComplete();
        setGenerating(false);
        setToolActivity(null);
        if (event.conversation_id) setActiveConversationId(event.conversation_id);
        break;
      case 'error':
        setGenerating(false);
        setToolActivity(null);
        addMessage({
          id: Date.now().toString(),
          role: 'assistant',
          content: `Something went wrong: ${event.message}`,
          isError: true,
          timestamp: new Date(),
        });
        break;
    }
  }, []);

  const sendMessage = useCallback(() => {
    const text = input.trim();
    if (!text || !wsRef.current || !wsReady || isGenerating) return;

    // Add user message immediately
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    });

    // Add assistant placeholder
    addMessage({
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      isStreaming: true,
      timestamp: new Date(),
    });

    setGenerating(true);
    setInput('');

    wsRef.current.send(JSON.stringify({
      token,
      message: text,
      conversation_id: activeConversationId,
    }));
  }, [input, wsReady, isGenerating, token, activeConversationId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const stopGeneration = () => {
    // Phase 2: implement stop token
    setGenerating(false);
    setToolActivity(null);
    setLastMessageComplete();
  };

  return (
    <div className="flex flex-col h-full">
      {/* ── Header ───────────────────────────────────────────── */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-surface-border">
        <div>
          <h1 className="text-base font-semibold text-text-primary">Chat</h1>
          <p className="text-xs text-text-muted">
            {wsReady ? (
              <span className="text-status-success">● Connected</span>
            ) : (
              <span className="text-status-error">● Disconnected</span>
            )}
            {activeConversationId && ` · Conversation #${activeConversationId}`}
          </p>
        </div>
        <button
          onClick={() => {
            useChatStore.getState().clearMessages();
            setActiveConversationId(null);
          }}
          className="btn-ghost text-xs gap-1"
        >
          <RotateCcw size={12} /> New conversation
        </button>
      </div>

      {/* ── Messages ─────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto scroll-smooth-custom px-6 py-4 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-4 py-16">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent/20 to-accent-cyan/20 flex items-center justify-center border border-surface-border">
              <span className="text-2xl font-bold text-gradient">J</span>
            </div>
            <div>
              <p className="text-text-primary font-medium">JARVIS is ready.</p>
              <p className="text-text-muted text-sm mt-1">
                Type a message or press{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-surface-4 border border-surface-border text-xs">
                  Ctrl+Space
                </kbd>{' '}
                for voice.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm max-w-sm w-full">
              {[
                '"What\'s the status of my projects?"',
                '"Help me plan my week."',
                '"Research AI frameworks."',
                '"Explain this concept..."',
              ].map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => setInput(prompt.replace(/"/g, ''))}
                  className="panel px-3 py-2 text-left text-text-muted hover:text-text-primary hover:bg-surface-4 transition-colors text-xs"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatBubble key={msg.id} message={msg} index={i} />
        ))}

        {/* Tool activity indicator */}
        <AnimatePresence>
          {toolActivity && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex items-center gap-2 text-sm text-text-muted"
            >
              <Zap size={12} className="text-accent animate-pulse" />
              <span>{toolActivity}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* ── Input ─────────────────────────────────────────────── */}
      <div className="px-6 py-4 border-t border-surface-border">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message JARVIS... (Shift+Enter for new line)"
              rows={1}
              className={clsx(
                'input resize-none py-3 pr-12 selectable',
                'max-h-32 overflow-y-auto',
              )}
              style={{
                height: 'auto',
                minHeight: '44px',
              }}
              onInput={(e) => {
                const t = e.currentTarget;
                t.style.height = 'auto';
                t.style.height = `${Math.min(t.scrollHeight, 128)}px`;
              }}
              disabled={!wsReady || isGenerating}
            />
          </div>

          {isGenerating ? (
            <button
              onClick={stopGeneration}
              className="btn bg-status-error/20 hover:bg-status-error/30 text-status-error h-11 px-4"
            >
              <Square size={14} />
            </button>
          ) : (
            <button
              onClick={sendMessage}
              disabled={!input.trim() || !wsReady}
              className="btn-primary h-11 px-4 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Send size={14} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Chat Bubble ───────────────────────────────────────────────────────────────

function ChatBubble({
  message,
}: {
  message: ReturnType<typeof useChatStore.getState>['messages'][0];
  index: number;
}) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="message-user selectable">
          <p className="text-sm text-text-primary whitespace-pre-wrap">{message.content}</p>
          <p className="text-xs text-text-muted mt-1 text-right">
            {format(message.timestamp, 'HH:mm')}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3 group">
      <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent/30 to-accent-cyan/30 flex items-center justify-center flex-shrink-0 mt-0.5 border border-surface-border">
        <span className="text-xs font-bold text-accent-bright">J</span>
      </div>
      <div className="flex-1 min-w-0">
        {message.isStreaming && !message.content ? (
          <div className="flex items-center gap-2 text-text-muted">
            <Loader2 size={14} className="animate-spin" />
            <span className="text-sm">Thinking...</span>
          </div>
        ) : (
          <div className={clsx(
            'prose prose-sm max-w-none selectable',
            'prose-invert prose-p:text-text-primary prose-headings:text-text-primary',
            'prose-code:text-accent-bright prose-pre:bg-surface-2',
            message.isError && 'opacity-70',
          )}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  const isInline = !className;
                  return !isInline && match ? (
                    <SyntaxHighlighter
                      style={oneDark as any}
                      language={match[1]}
                      PreTag="div"
                      customStyle={{
                        margin: 0,
                        borderRadius: '8px',
                        fontSize: '0.8rem',
                        background: '#0f1117',
                      }}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className="bg-surface-3 px-1 py-0.5 rounded text-accent-bright text-xs font-mono" {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
            {message.isStreaming && (
              <span className="inline-block w-2 h-4 bg-accent-bright animate-pulse ml-0.5 rounded-sm" />
            )}
          </div>
        )}
        <div className="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <span className="text-xs text-text-muted">{format(message.timestamp, 'HH:mm')}</span>
          {message.content && (
            <button onClick={copy} className="text-xs text-text-muted hover:text-text-secondary flex items-center gap-1">
              <Copy size={10} />
              {copied ? 'Copied' : 'Copy'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
