import React, { useState, useEffect } from 'react';
import { MessageSquare, LayoutDashboard, Zap } from 'lucide-react';
import UserSelector from './components/UserSelector';
import ChatInterface from './components/ChatInterface';
import ProactiveDashboard from './components/ProactiveDashboard';

export default function App() {
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');
  const API_HOST = '';

  useEffect(() => {
    fetch(`${API_HOST}/api/chat/users`)
      .then((res) => res.json())
      .then((data) => {
        if (data.users && data.users.length > 0) {
          setUsers(data.users);
          setCurrentUser(data.users[0]);
        }
      })
      .catch((err) => {
        console.error('Failed to fetch mock users:', err);
        const fallbackUsers = [
          {
            user_id: 'CUST-ACCT-001',
            role: 'customer',
            user_name: 'Northstar Logistics (Enterprise)',
            account_id: 'ACCT-001',
            account_name: 'Northstar Logistics',
            plan: 'Enterprise',
            is_internal: false
          },
          {
            user_id: 'AGENT-ROHIT',
            role: 'internal',
            user_name: 'Rohit (Support Operations Lead)',
            account_id: null,
            account_name: 'ParcelPilot Internal',
            plan: 'Internal',
            is_internal: true
          }
        ];
        setUsers(fallbackUsers);
        setCurrentUser(fallbackUsers[0]);
      });
  }, []);

  const handleSelectUser = (user) => {
    setCurrentUser(user);
    if (!user.is_internal && activeTab === 'dashboard') {
      setActiveTab('chat');
    }
  };

  if (!currentUser) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-sm">
        Initializing ParcelPilot AI Platform...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-40 px-4 lg:px-8 py-3 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 shadow-lg shadow-indigo-500/20 text-white">
            <Zap className="w-6 h-6 fill-current" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent flex items-center gap-2">
              ParcelPilot AI
              <span className="text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/30">
                v1.0
              </span>
            </h1>
            <p className="text-[11px] text-slate-400 font-medium">B2B Logistics Support & Proactive Operations Platform</p>
          </div>
        </div>

        {/* User Selector Dropdown */}
        <UserSelector users={users} currentUser={currentUser} onSelectUser={handleSelectUser} />

        {/* View Switcher Tabs */}
        <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('chat')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${activeTab === 'chat'
                ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
              }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>AI Chatbot</span>
          </button>

          {currentUser.is_internal && (
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${activeTab === 'dashboard'
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
                }`}
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              <span>Proactive Dashboard</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Workspace Area */}
      <main className="flex-1 p-4 lg:p-8 max-w-7xl w-full mx-auto">
        {activeTab === 'chat' ? (
          <ChatInterface currentUser={currentUser} users={users} apiHost={API_HOST} />
        ) : (
          <ProactiveDashboard currentUser={currentUser} apiHost={API_HOST} />
        )}
      </main>
    </div>
  );
}
