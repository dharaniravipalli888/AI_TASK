import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, AlertCircle, FileText, CheckCircle2, ShieldCheck } from 'lucide-react';
import ToolIndicator from './ToolIndicator';
import ActionConfirmationModal from './ActionConfirmationModal';

export default function ChatInterface({ currentUser, users, apiHost = '' }) {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: `Hello! I am ParcelPilot AI. I am currently operating in **${currentUser.is_internal ? 'Internal Operations' : currentUser.account_name}** mode.\n\nHow can I assist you with order cancellations, service credits, policy terms, or support tickets today?`,
      tool_calls: [],
      source_resolution: null
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg = { sender: 'user', text: query };
    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${apiHost}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          user_id: currentUser.user_id
        })
      });

      if (!response.ok) {
        throw new Error('API server returned an error');
      }

      const data = await response.json();

      const botMsg = {
        sender: 'bot',
        text: data.response,
        tool_calls: data.tool_calls_executed || [],
        source_resolution: data.source_resolution || null
      };

      setMessages((prev) => [...prev, botMsg]);

      if (data.pending_action) {
        setPendingAction(data.pending_action);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: `⚠️ Communication Error: Unable to reach ParcelPilot AI backend API (${err.message}). Please make sure the backend server is running.`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmAction = async (token) => {
    try {
      const res = await fetch(`${apiHost}/api/chat/confirm-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          confirmation_token: token,
          user_id: currentUser.user_id
        })
      });

      const data = await res.json();
      setPendingAction(null);

      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: `✅ **Action Confirmed & Executed Successfully**\n\n${data.message}`,
          tool_calls: [{ tool_name: 'execute_confirmed_action', args: { token }, output: data }]
        }
      ]);
    } catch (e) {
      alert(`Action confirmation failed: ${e.message}`);
    }
  };

  const exampleQueries = currentUser.is_internal
    ? [
      "Which tickets are currently breaching SLA targets?",
      "Investigate TKT-501 for Northstar Logistics outage",
      "Escalate ticket TKT-501 to Tier 2 Operations as P1 Critical",
      "Detect recurring product issue complaints"
    ]
    : [
      "Can Northstar cancel ORD-1001 without a cancellation fee? Explain why.",
      "A pickup is 3 hours late because of carrier fault. Should I get a service credit?",
      "What are our support response SLA targets for P1 and P2?",
      "Can we cancel order ORD-2001 after 75 minutes of booking?"
    ];

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] glass-panel overflow-hidden border border-slate-800 shadow-2xl">
      {/* Top Banner */}
      <div className="px-6 py-3.5 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              ParcelPilot AI Assistant
              <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full font-semibold border border-emerald-500/30 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Active Agent
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              {currentUser.is_internal
                ? "Internal Operations Context — Full Cross-Account Visibility"
                : `Customer Support Context — Scoped strictly to ${currentUser.account_name}`}
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
          <ShieldCheck className="w-4 h-4 text-indigo-400" />
          <span>Precedence Rule: Contract &gt; Policy v3 &gt; SOP v4</span>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 max-w-3xl ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''
              }`}
          >
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${msg.sender === 'user'
                  ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md'
                  : 'bg-slate-800 text-indigo-400 border border-slate-700'
                }`}
            >
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`rounded-2xl p-4 text-sm leading-relaxed shadow-lg ${msg.sender === 'user'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-tr-none'
                  : 'bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none space-y-3'
                }`}
            >
              {/* Tool Execution Visualizer */}
              {msg.tool_calls && msg.tool_calls.length > 0 && (
                <ToolIndicator toolLogs={msg.tool_calls} />
              )}

              <div className="whitespace-pre-wrap">{msg.text}</div>

              {/* Source Resolution Citation Badge */}
              {msg.source_resolution && msg.source_resolution.primary_source && (
                <div className="mt-3 pt-3 border-t border-slate-800 text-xs space-y-1 bg-slate-950/60 p-2.5 rounded-xl">
                  <div className="flex items-center gap-1.5 text-indigo-400 font-semibold">
                    <FileText className="w-3.5 h-3.5" />
                    <span>Primary Cited Authority: {msg.source_resolution.primary_source.file_name}</span>
                  </div>
                  {msg.source_resolution.conflicts_detected && msg.source_resolution.conflicts_detected.length > 0 && (
                    <div className="text-[11px] text-amber-300/90">
                      ⚡ {msg.source_resolution.conflicts_detected.join(' | ')}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 max-w-2xl items-center text-slate-400 text-xs">
            <div className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center text-indigo-400 border border-slate-700 animate-spin">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="bg-slate-900/80 p-3 rounded-2xl border border-slate-800 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
              <span>ParcelPilot AI is reasoning over documents and structured data...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts */}
      <div className="px-6 py-2 bg-slate-950/60 border-t border-slate-800/60 flex items-center gap-2 overflow-x-auto">
        <span className="text-[11px] font-semibold text-slate-400 shrink-0">Suggested Queries:</span>
        {exampleQueries.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            className="text-xs bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-indigo-300 px-3 py-1.5 rounded-lg border border-slate-800/80 transition-all shrink-0 cursor-pointer"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <div className="p-4 bg-slate-900/90 border-t border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Ask ParcelPilot AI as ${currentUser.user_name}...`}
            className="flex-1 bg-slate-950 text-slate-100 placeholder-slate-500 text-sm rounded-xl px-4 py-3 border border-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-inner"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-semibold text-sm px-5 py-3 rounded-xl shadow-lg shadow-indigo-500/20 disabled:opacity-50 transition-all flex items-center gap-2 cursor-pointer shrink-0"
          >
            <span>Send</span>
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

      {/* Action Confirmation Modal */}
      {pendingAction && (
        <ActionConfirmationModal
          pendingAction={pendingAction}
          currentUser={currentUser}
          onConfirm={handleConfirmAction}
          onCancel={() => setPendingAction(null)}
        />
      )}
    </div>
  );
}
