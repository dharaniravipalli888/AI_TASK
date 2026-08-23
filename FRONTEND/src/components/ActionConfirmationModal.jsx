import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, XCircle, ShieldAlert } from 'lucide-react';

export default function ActionConfirmationModal({ pendingAction, currentUser, onConfirm, onCancel }) {
  const [loading, setLoading] = useState(false);

  if (!pendingAction) return null;

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm(pendingAction.confirmation_token);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-amber-500/40 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4 animate-in fade-in zoom-in duration-200">
        <div className="flex items-center gap-3 text-amber-400 border-b border-slate-800 pb-3">
          <ShieldAlert className="w-6 h-6 animate-bounce" />
          <div>
            <h3 className="font-bold text-lg text-slate-100">State-Changing Action Confirmation Required</h3>
            <p className="text-xs text-amber-300/80">Requirement 4: Explicit Confirmation Token Safeguard</p>
          </div>
        </div>

        <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 space-y-2 text-sm">
          <div className="flex justify-between items-center text-xs text-slate-400">
            <span>Action Type:</span>
            <span className="font-mono text-indigo-400 font-semibold">{pendingAction.action_type}</span>
          </div>

          <div className="text-slate-100 font-semibold text-base border-t border-slate-800/80 pt-2">
            {pendingAction.summary}
          </div>

          <p className="text-slate-300 text-xs bg-slate-900 p-2.5 rounded-lg border border-slate-800">
            {pendingAction.details}
          </p>

          <div className="flex justify-between items-center text-xs text-slate-400 pt-1 font-mono">
            <span>Confirmation Token:</span>
            <span className="text-amber-400 font-bold bg-amber-950/50 px-2 py-0.5 rounded border border-amber-800">
              {pendingAction.confirmation_token}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-xl transition-all flex items-center gap-1.5"
          >
            <XCircle className="w-4 h-4" /> Cancel Action
          </button>

          <button
            onClick={handleConfirm}
            disabled={loading}
            className="px-5 py-2 text-xs font-bold text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 rounded-xl shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-1.5 cursor-pointer"
          >
            {loading ? (
              <span>Executing Action...</span>
            ) : (
              <>
                <CheckCircle className="w-4 h-4" /> Confirm & Execute
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
