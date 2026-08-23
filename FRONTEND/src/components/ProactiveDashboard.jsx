import React, { useState, useEffect, useCallback } from 'react';
import { AlertTriangle, ShieldAlert, Cpu, RefreshCw, ArrowUpRight, Flame } from 'lucide-react';

export default function ProactiveDashboard({ currentUser, apiHost = '' }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiHost}/api/dashboard/proactive-issues?user_id=${currentUser.user_id}`);
      if (!res.ok) {
        throw new Error('Access denied or dashboard error');
      }
      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [apiHost, currentUser]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (!currentUser.is_internal) {
    return (
      <div className="glass-panel p-8 text-center max-w-lg mx-auto my-12 space-y-4 border border-rose-500/30">
        <ShieldAlert className="w-12 h-12 text-rose-400 mx-auto animate-bounce" />
        <h2 className="text-xl font-bold text-slate-100">Access Restricted</h2>
        <p className="text-sm text-slate-400">
          Proactive Issue Detection (Client Problem 1) is restricted to authorized ParcelPilot Support Operations personnel.
        </p>
        <p className="text-xs text-indigo-400 font-mono bg-slate-900 p-2.5 rounded-lg border border-slate-800">
          Please switch to an Internal Role (e.g., "Rohit (Support Operations Lead)") in the top selector to access this dashboard.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Flame className="w-4 h-4 text-amber-400" />
            <span>Client Problem 1: Proactive Issue Detection Engine</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-100">Support Operations Command Center</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time pattern detection across tickets, order anomalies, SLA breach timers, and recurring product defects.
          </p>
        </div>

        <div className="flex items-center gap-4">
          {data && (
            <div className="flex items-center gap-3 bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 text-xs">
              <div>
                <span className="text-slate-500 block text-[10px]">Reference Snapshot:</span>
                <span className="font-mono text-slate-200 font-bold">{data.snapshot_reference_time}</span>
              </div>
              <div className="border-l border-slate-800 pl-3">
                <span className="text-slate-500 block text-[10px]">Total Alerts:</span>
                <span className="font-bold text-rose-400 text-sm">{data.total_alerts_detected}</span>
              </div>
            </div>
          )}

          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded-xl transition-all cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      {data && data.summary && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="glass-panel p-4 border-l-4 border-l-rose-500 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase">Critical SLA Breaches</span>
              <div className="text-3xl font-extrabold text-rose-400 mt-1">{data.summary.critical_count}</div>
            </div>
            <ShieldAlert className="w-8 h-8 text-rose-500/40" />
          </div>

          <div className="glass-panel p-4 border-l-4 border-l-amber-500 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase font-mono">High Severity Defects</span>
              <div className="text-3xl font-extrabold text-amber-400 mt-1">{data.summary.high_count}</div>
            </div>
            <AlertTriangle className="w-8 h-8 text-amber-500/40" />
          </div>

          <div className="glass-panel p-4 border-l-4 border-l-cyan-500 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase font-mono">Carrier Anomalies</span>
              <div className="text-3xl font-extrabold text-cyan-400 mt-1">{data.summary.medium_count}</div>
            </div>
            <Cpu className="w-8 h-8 text-cyan-500/40" />
          </div>
        </div>
      )}

      {/* Alerts Feed */}
      {loading ? (
        <div className="glass-panel p-12 text-center text-slate-400 space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-indigo-400" />
          <p className="text-sm">Scanning support tickets, carrier webhooks, and SLA timers...</p>
        </div>
      ) : error ? (
        <div className="glass-panel p-6 border-rose-500/30 text-rose-400 text-sm">
          Error loading proactive dashboard: {error}
        </div>
      ) : (
        <div className="space-y-4">
          <h3 className="font-bold text-sm text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Active Proactive Detection Incidents ({data?.alerts?.length || 0})
          </h3>

          <div className="space-y-3">
            {data?.alerts?.map((alert, idx) => (
              <div
                key={idx}
                className={`glass-panel p-5 border transition-all space-y-3 ${
                  alert.severity === 'CRITICAL'
                    ? 'border-rose-500/40 bg-rose-950/10'
                    : alert.severity === 'HIGH'
                    ? 'border-amber-500/40 bg-amber-950/10'
                    : 'border-slate-800'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold tracking-wider ${
                        alert.severity === 'CRITICAL'
                          ? 'bg-rose-500 text-white'
                          : 'bg-amber-500 text-slate-950'
                      }`}
                    >
                      {alert.severity}
                    </span>
                    <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      {alert.category}
                    </span>
                    <h4 className="font-bold text-base text-slate-100">{alert.title}</h4>
                  </div>

                  <span className="text-xs text-slate-400 font-mono">ID: {alert.alert_id}</span>
                </div>

                <p className="text-sm text-slate-300 leading-relaxed">{alert.description}</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800/80 space-y-1">
                    <span className="text-slate-500 font-semibold uppercase text-[10px] block">Customer Impact:</span>
                    <p className="text-slate-200">{alert.impact}</p>
                  </div>

                  <div className="bg-indigo-950/30 p-3 rounded-xl border border-indigo-500/20 space-y-1">
                    <span className="text-indigo-400 font-semibold uppercase text-[10px] block flex items-center gap-1">
                      <ArrowUpRight className="w-3 h-3" /> Recommended Ops Action:
                    </span>
                    <p className="text-indigo-200">{alert.recommended_action}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
