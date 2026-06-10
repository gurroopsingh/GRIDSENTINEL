'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';

const CITIES = [
  { name: 'Mumbai', color: '#00d4ff', icon: '🏙️' },
  { name: 'Delhi', color: '#8b5cf6', icon: '🕌' },
  { name: 'Bengaluru', color: '#00ff88', icon: '💻' },
  { name: 'Chennai', color: '#ffaa00', icon: '⛵' },
];

export default function CommandCenter() {
  const [gridState, setGridState] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [agentLog, setAgentLog] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [state, met] = await Promise.all([api.getGridState(), api.getMetrics()]);
        setGridState(state);
        setMetrics(met);
        try { const log = await api.getAgentLog(); setAgentLog(log); } catch {}
      } catch (err) { console.error('Failed to load:', err); }
      setLoading(false);
    }
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingScreen />;

  return (
    <div className="space-y-4">
      {/* Hero Metrics Row */}
      <div className="grid grid-cols-5 gap-3">
        <MetricCard label="TOTAL GENERATION" value={metrics?.total_generation_mw || 0} unit="MW" color="#00d4ff" />
        <MetricCard label="TOTAL LOAD" value={metrics?.total_load_mw || 0} unit="MW" color="#8b5cf6" />
        <MetricCard label="RESERVE MARGIN" value={metrics?.reserve_margin_pct || 0} unit="%" color="#00ff88" />
        <MetricCard label="RENEWABLE MIX" value={metrics?.renewable_penetration_pct || 0} unit="%" color="#ffaa00" />
        <MetricCard label="HEALTH SCORE" value={(metrics?.national_health_score || 0) * 100} unit="%" color={
          (metrics?.national_health_score || 0) > 0.7 ? '#00ff88' : (metrics?.national_health_score || 0) > 0.4 ? '#ffaa00' : '#ff3366'
        } />
      </div>

      <div className="grid grid-cols-12 gap-3">
        {/* City Status Cards */}
        <div className="col-span-8">
          <div className="grid grid-cols-4 gap-3 mb-3">
            {CITIES.map((city, i) => {
              const cityData = gridState?.cities?.find((c: any) => c.city === city.name);
              return (
                <motion.div key={city.name} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }} className="glass-card">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg">{city.icon}</span>
                    <span className={`pulse-dot pulse-dot-${cityData?.status === 'healthy' ? 'healthy' : cityData?.status === 'degraded' ? 'warning' : 'critical'}`} />
                  </div>
                  <h3 className="text-sm font-semibold mb-1">{city.name}</h3>
                  <div className="space-y-1 text-xs" style={{ color: '#94a3b8' }}>
                    <div className="flex justify-between">
                      <span>Generation</span>
                      <span style={{ color: city.color }}>{cityData?.total_generation_mw?.toFixed(0) || '—'} MW</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Load</span>
                      <span>{cityData?.total_load_mw?.toFixed(0) || '—'} MW</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Health</span>
                      <span style={{ color: (cityData?.health_score || 0) > 0.7 ? '#00ff88' : '#ffaa00' }}>
                        {((cityData?.health_score || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  {/* Mini bar */}
                  <div className="mt-2 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
                    <motion.div className="h-full rounded-full" initial={{ width: 0 }}
                                animate={{ width: `${(cityData?.health_score || 0) * 100}%` }}
                                transition={{ duration: 1, delay: i * 0.2 }}
                                style={{ background: `linear-gradient(90deg, ${city.color}, ${city.color}88)` }} />
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* System Vitals */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
                      className="glass-card">
            <h3 className="text-sm font-semibold mb-3" style={{ color: '#00d4ff' }}>⚡ SYSTEM VITALS</h3>
            <div className="grid grid-cols-4 gap-4">
              <VitalGauge label="Voltage Stability" value={metrics?.voltage_stability_index || 0} />
              <VitalGauge label="N-1 Contingency" value={metrics?.n1_contingency_score || 0} />
              <VitalGauge label="Transformer Health" value={metrics?.avg_transformer_health || 0} />
              <VitalGauge label="Line Utilization" value={1 - (metrics?.avg_line_loading_pct || 0) / 100} inverted />
            </div>
          </motion.div>
        </div>

        {/* Agent Activity Feed */}
        <div className="col-span-4">
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
                      className="glass-card h-full flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold" style={{ color: '#8b5cf6' }}>🤖 AGENT ACTIVITY</h3>
              <TriggerAnalysisButton />
            </div>
            <div className="flex-1 overflow-y-auto space-y-2 max-h-[400px]">
              {agentLog.length === 0 ? (
                <div className="text-xs text-center py-8" style={{ color: '#64748b' }}>
                  No agent activity yet.<br />Click &quot;Analyze&quot; to activate agents.
                </div>
              ) : (
                agentLog.slice(-15).reverse().map((msg: any, i: number) => (
                  <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: i * 0.05 }}
                              className="p-2 rounded-lg text-xs" style={{ background: 'rgba(255,255,255,0.03)' }}>
                    <div className="flex items-center gap-2 mb-1">
                      <span>{msg.emoji || '🤖'}</span>
                      <span className="font-semibold" style={{ color: '#00d4ff' }}>{msg.agent}</span>
                      <span className="ml-auto text-[10px]" style={{ color: '#475569' }}>{msg.role}</span>
                    </div>
                    <p style={{ color: '#94a3b8' }} className="whitespace-pre-line leading-relaxed">{msg.content?.slice(0, 200)}</p>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, unit, color }: { label: string; value: number; unit: string; color: string }) {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                className="glass-card text-center py-3">
      <div className="text-[10px] font-medium tracking-widest mb-1" style={{ color: '#64748b' }}>{label}</div>
      <div className="text-2xl font-bold" style={{ color }}>
        {typeof value === 'number' ? value.toFixed(1) : value}
        <span className="text-xs font-normal ml-1" style={{ color: '#64748b' }}>{unit}</span>
      </div>
    </motion.div>
  );
}

function VitalGauge({ label, value, inverted }: { label: string; value: number; inverted?: boolean }) {
  const pct = Math.max(0, Math.min(100, value * 100));
  const displayPct = inverted ? 100 - pct : pct;
  const color = displayPct > 70 ? '#00ff88' : displayPct > 40 ? '#ffaa00' : '#ff3366';
  return (
    <div className="text-center">
      <div className="relative w-16 h-16 mx-auto mb-2">
        <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
          <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
          <motion.path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none" stroke={color} strokeWidth="3" strokeLinecap="round"
                initial={{ strokeDasharray: "0 100" }}
                animate={{ strokeDasharray: `${pct} 100` }}
                transition={{ duration: 1.5, ease: "easeOut" }} />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center text-xs font-bold" style={{ color }}>
          {pct.toFixed(0)}%
        </div>
      </div>
      <div className="text-[10px]" style={{ color: '#64748b' }}>{label}</div>
    </div>
  );
}

function TriggerAnalysisButton() {
  const [analyzing, setAnalyzing] = useState(false);
  async function handleAnalyze() {
    setAnalyzing(true);
    try { await api.triggerAnalysis(); } catch {}
    setTimeout(() => setAnalyzing(false), 2000);
  }
  return (
    <button onClick={handleAnalyze} disabled={analyzing}
            className="text-[10px] px-3 py-1 rounded-full font-semibold transition-all"
            style={{ background: analyzing ? 'rgba(139,92,246,0.3)' : 'rgba(0,212,255,0.15)',
                     color: analyzing ? '#8b5cf6' : '#00d4ff', border: '1px solid rgba(0,212,255,0.2)' }}>
      {analyzing ? '⏳ ANALYZING...' : '▶ ANALYZE'}
    </button>
  );
}

function LoadingScreen() {
  return (
    <div className="flex items-center justify-center h-full">
      <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  className="w-12 h-12 rounded-full border-2 border-transparent"
                  style={{ borderTopColor: '#00d4ff', borderRightColor: '#8b5cf6' }} />
    </div>
  );
}
