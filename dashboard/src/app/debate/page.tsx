'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';

const AGENT_COLORS: Record<string, string> = {
  'Mission Commander': '#00d4ff',
  'Grid Health Agent': '#00ff88',
  'Failure Prediction Agent': '#ff3366',
  'Weather Risk Agent': '#ffaa00',
  'Renewable Optimizer': '#3b82f6',
  'Economic Intelligence': '#8b5cf6',
  'Cybersecurity Agent': '#ef4444',
  'Grid Optimizer': '#06b6d4',
  'Self-Healing Agent': '#10b981',
  'Emergency Response': '#f59e0b',
  'Energy Scientist': '#ec4899',
};

export default function DebatePage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

  async function triggerDebate() {
    setLoading(true);
    setMessages([]);
    try {
      const result = await api.triggerAnalysis();
      setAnalysis(result);
      // Animate messages one by one
      const allMsgs = result.messages || [];
      for (let i = 0; i < allMsgs.length; i++) {
        await new Promise(r => setTimeout(r, 600));
        setMessages(prev => [...prev, allMsgs[i]]);
      }
    } catch (err) { console.error(err); }
    setLoading(false);
  }

  return (
    <div className="h-full flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold" style={{ color: '#00d4ff' }}>🗣️ Agent Debate Chamber</h2>
          <p className="text-xs mt-1" style={{ color: '#64748b' }}>
            Watch autonomous agents analyze, challenge, and decide on grid operations
          </p>
        </div>
        <button onClick={triggerDebate} disabled={loading}
                className="px-5 py-2 rounded-xl font-semibold text-sm transition-all"
                style={{
                  background: loading ? 'rgba(139,92,246,0.2)' : 'linear-gradient(135deg, #00d4ff, #8b5cf6)',
                  color: '#fff', border: 'none', cursor: loading ? 'wait' : 'pointer',
                }}>
          {loading ? '⏳ Agents Deliberating...' : '⚡ Initiate Agent Analysis'}
        </button>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        {/* Debate Feed */}
        <div className="col-span-8 glass-card flex flex-col overflow-hidden">
          <div className="text-xs font-semibold mb-3 tracking-wider" style={{ color: '#64748b' }}>
            LIVE DEBATE FEED
          </div>
          <div className="flex-1 overflow-y-auto space-y-3 pr-2">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: -20, scale: 0.95 }}
                            animate={{ opacity: 1, x: 0, scale: 1 }}
                            transition={{ duration: 0.4 }}
                            className="flex gap-3 p-3 rounded-xl"
                            style={{ background: 'rgba(255,255,255,0.02)', borderLeft: `3px solid ${AGENT_COLORS[msg.agent] || '#00d4ff'}` }}>
                  <div className="text-2xl flex-shrink-0 mt-1">{msg.emoji || '🤖'}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-sm" style={{ color: AGENT_COLORS[msg.agent] || '#00d4ff' }}>
                        {msg.agent}
                      </span>
                      <span className={`agent-badge severity-${msg.type === 'verdict' ? 'info' : msg.type === 'challenge' ? 'warning' : 'healthy'}`}>
                        {msg.type?.toUpperCase() || 'ANALYSIS'}
                      </span>
                      <span className="ml-auto text-[10px]" style={{ color: '#475569' }}>
                        Confidence: {((msg.confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-xs leading-relaxed whitespace-pre-line" style={{ color: '#94a3b8' }}>
                      {msg.content}
                    </p>
                    {msg.reasoning && (
                      <div className="mt-2 text-[10px] p-2 rounded-lg" style={{ background: 'rgba(139,92,246,0.08)', color: '#8b5cf6' }}>
                        💡 Reasoning: {msg.reasoning}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            {loading && (
              <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1.5, repeat: Infinity }}
                          className="text-center py-4 text-sm" style={{ color: '#8b5cf6' }}>
                🤖 Agents are analyzing and debating...
              </motion.div>
            )}
            {!loading && messages.length === 0 && (
              <div className="text-center py-16 text-sm" style={{ color: '#475569' }}>
                Click &quot;Initiate Agent Analysis&quot; to start a debate session
              </div>
            )}
          </div>
        </div>

        {/* Agent Status Panel */}
        <div className="col-span-4 space-y-3">
          <div className="glass-card">
            <div className="text-xs font-semibold mb-3 tracking-wider" style={{ color: '#64748b' }}>
              ACTIVE AGENTS
            </div>
            <div className="space-y-2">
              {Object.entries(AGENT_COLORS).map(([name, color]) => (
                <div key={name} className="flex items-center gap-2 text-xs p-1.5 rounded-lg"
                     style={{ background: 'rgba(255,255,255,0.02)' }}>
                  <span className="pulse-dot pulse-dot-healthy" style={{ background: color, color }} />
                  <span style={{ color }}>{name}</span>
                </div>
              ))}
            </div>
          </div>

          {analysis && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card">
              <div className="text-xs font-semibold mb-2 tracking-wider" style={{ color: '#64748b' }}>
                ANALYSIS SUMMARY
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span style={{ color: '#94a3b8' }}>Risk Level</span>
                  <span className={`font-semibold ${analysis.risk_level === 'critical' ? 'text-red-400' : analysis.risk_level === 'warning' ? 'text-amber-400' : 'text-green-400'}`}>
                    {analysis.risk_level?.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#94a3b8' }}>Predictions</span>
                  <span style={{ color: '#ff3366' }}>{analysis.predictions?.length || 0} threats</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#94a3b8' }}>Economic Exposure</span>
                  <span style={{ color: '#8b5cf6' }}>₹{analysis.economic_impact?.business_impact_crores || 0} Cr</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#94a3b8' }}>Prevention Savings</span>
                  <span style={{ color: '#00ff88' }}>₹{analysis.economic_impact?.net_savings_crores || 0} Cr</span>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
