import React from 'react';
import { Search, Database, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function ToolIndicator({ toolLogs }) {
  if (!toolLogs || toolLogs.length === 0) return null;

  const getToolIcon = (name) => {
    if (name.includes('document') || name.includes('search')) return <Search className="w-3.5 h-3.5 text-cyan-400" />;
    if (name.includes('lookup') || name.includes('calculate')) return <Database className="w-3.5 h-3.5 text-indigo-400" />;
    return <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />;
  };

  const getToolLabel = (name) => {
    if (name === 'document_search') return 'Tool 1: Document Retrieval & Policy Search';
    if (name === 'lookup_order') return 'Tool 2: Structured Order Lookup';
    if (name === 'lookup_ticket') return 'Tool 2: Ticket History Lookup';
    if (name === 'calculate_cancellation_fee') return 'Tool 2: Fee & SLA Calculation';
    if (name === 'calculate_service_credit') return 'Tool 2: Service Credit Engine';
    if (name.includes('prepare')) return 'Tool 3: State-Changing Action Preparation';
    return name;
  };

  return (
    <div className="my-3 p-3 bg-slate-900/80 border border-slate-800 rounded-xl space-y-2">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 border-b border-slate-800/80 pb-1.5">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
        <span>AGENT TOOL EXECUTION TRACE ({toolLogs.length} STEPS EXECUTED)</span>
      </div>

      <div className="space-y-1.5">
        {toolLogs.map((log, index) => (
          <div key={index} className="flex flex-col gap-1 p-2 bg-slate-950/60 rounded-lg text-xs font-mono border border-slate-800/60">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-slate-500 font-bold">Step {index + 1}:</span>
                {getToolIcon(log.tool_name)}
                <span className="font-semibold text-slate-200">{getToolLabel(log.tool_name)}</span>
              </div>
              <span className="text-emerald-400 text-[10px] flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Executed
              </span>
            </div>

            {log.args && (
              <div className="text-[11px] text-slate-400 pl-6">
                Params: <span className="text-indigo-300">{JSON.stringify(log.args)}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
