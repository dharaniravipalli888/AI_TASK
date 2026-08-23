import React from 'react';
import { User } from 'lucide-react';

export default function UserSelector({ users, currentUser, onSelectUser }) {
  const getBadgeClass = (plan, isInternal) => {
    if (isInternal) return 'badge-internal';
    if (plan === 'Enterprise') return 'badge-enterprise';
    if (plan === 'Growth') return 'badge-growth';
    return 'badge-standard';
  };

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider">
        <User className="w-4 h-4 text-indigo-400" />
        <span>User Role Context:</span>
      </div>

      <div className="relative">
        <select
          value={currentUser?.user_id || ''}
          onChange={(e) => {
            const found = users.find((u) => u.user_id === e.target.value);
            if (found) onSelectUser(found);
          }}
          className="bg-slate-900/90 text-slate-100 text-sm font-medium border border-indigo-500/30 rounded-xl px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer shadow-lg hover:border-indigo-500/60 transition-all"
        >
          <optgroup label="🏢 Customer Accounts (Scoped Access)">
            {users
              .filter((u) => !u.is_internal)
              .map((u) => (
                <option key={u.user_id} value={u.user_id}>
                  {u.user_name} ({u.plan} Plan)
                </option>
              ))}
          </optgroup>
          <optgroup label="🛡️ Authorized Internal Staff (Full Access)">
            {users
              .filter((u) => u.is_internal)
              .map((u) => (
                <option key={u.user_id} value={u.user_id}>
                  {u.user_name}
                </option>
              ))}
          </optgroup>
        </select>
      </div>

      {currentUser && (
        <div className="flex items-center gap-2">
          <span className={getBadgeClass(currentUser.plan, currentUser.is_internal)}>
            {currentUser.is_internal ? 'INTERNAL OPERATIONS' : `${currentUser.plan} PLAN`}
          </span>
          {currentUser.account_id && (
            <span className="text-xs text-slate-400 font-mono bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
              ID: {currentUser.account_id}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
