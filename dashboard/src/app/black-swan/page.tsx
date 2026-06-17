'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';

const SCENARIO_ICONS: Record<string, string> = {
  climate: '🌪️', cyber: '🛡️', equipment: '⚙️', renewable: '☀️', demand: '📈', custom: '🦢',
};

export default function BlackSwanPage() {
  const [scenarios, setScenarios] = useState<Record<string, any>>({});
  const [result, setResult] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [activeScenario, setActiveScenario] = useState('');
  const [customDesc, setCustomDesc] = useState('');

  useEffect(() => {
    api.getScenarios().then(setScenarios).catch(console.error);
  }, []);

  async function runScenario(key: string) {
    setRunning(true);
    setActiveScenario(key);
    setResult(null);
    try {
      const res = await api.runSimulation(key);
      setResult(res);
    } catch (err) { console.error(err); }
    setRunning(false);
  }

  async function runCustom() {
    if (!customDesc.trim()) return;
    setRunning(true);
    setActiveScenario('custom');
    setResult(null);
    try {
      const res = await api.runSimulation('custom', customDesc);
      setResult(res);
    } catch (err) { console.error(err); }
    setRunning(false);
  }

  return (
    <div className="h-full flex flex-col gap-4">
      <div>
        <h2 className="text-xl font-bold" style={{ color: '#ff3366' }}>🦢 Black Swan Scenario Engine</h2>
        <p className="text-xs mt-1" style={{ color: '#64748b' }}>Simulate extreme events. Test grid resilience. Watch autonomous response.</p>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        {/* Scenario Cards */}
        <div className="col-span-5 space-y-3 overflow-y-auto pr-2">
          {/* Custom Scenario */}
          <div className="glass-card" style={{ borderColor: 'rgba(255,51,102,0.3)' }}>
            <div className="text-xs font-semibold mb-2" style={{ color: '#ff3366' }}>🦢 CUSTOM DISASTER</div>
            <textarea value={customDesc} onChange={e => setCustomDesc(e.target.value)}
                      placeholder="Describe any disaster scenario... e.g. 'Category 5 cyclone hits Mumbai during peak summer demand while solar panels are damaged'"
                      className="w-full h-20 bg-transparent border rounded-lg p-2 text-xs resize-none"
                      style={{ borderColor: 'rgba(255,51,102,0.2)', color: '#e2e8f0' }} />
            <button onClick={runCustom} disabled={running || !customDesc.trim()}
                    className="mt-2 w-full py-2 rounded-lg text-xs font-semibold transition-all"
                    style={{ background: 'rgba(255,51,102,0.2)', color: '#ff3366', border: '1px solid rgba(255,51,102,0.3)' }}>
              ⚡ LAUNCH CUSTOM SCENARIO
            </button>
          </div>

          {/* Preset Scenarios */}
          {Object.entries(scenarios).map(([key, scenario]: [string, any]) => (
            <motion.div key={key} whileHover={{ scale: 1.01 }}
                        className={`glass-card cursor-pointer transition-all ${activeScenario === key ? 'ring-1 ring-cyan-500/30' : ''}`}
                        onClick={() => !running && runScenario(key)}>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">{SCENARIO_ICONS[scenario.type] || '⚡'}</span>
                <span className="text-sm font-semibold" style={{ color: '#e2e8f0' }}>{scenario.name}</span>
              </div>
              <p className="text-xs mb-2" style={{ color: '#64748b' }}>{scenario.description}</p>
              <div className="flex gap-2">
                <span className={`agent-badge severity-${scenario.severity}`}>{scenario.severity?.toUpperCase()}</span>
                <span className="agent-badge" style={{ background: 'rgba(255,255,255,0.05)', color: '#94a3b8' }}>
                  {scenario.city}
                </span>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Results Panel */}
        <div className="col-span-7 glass-card flex flex-col overflow-hidden">
          {running && (
            <motion.div animate={{ opacity: [0.5, 1, 0.5] }} transition={{ duration: 1.5, repeat: Infinity }}
                        className="flex-1 flex items-center justify-center flex-col gap-4">
              <div className="text-4xl">🌊</div>
              <div className="text-sm font-semibold" style={{ color: '#ff3366' }}>Simulating Disaster...</div>
              <div className="text-xs" style={{ color: '#64748b' }}>Running cascade analysis • Activating agents • Computing impact</div>
            </motion.div>
          )}

          {!running && !result && (
            <div className="flex-1 flex items-center justify-center flex-col gap-2">
              <div className="text-4xl">🦢</div>
              <div className="text-sm" style={{ color: '#475569' }}>Select a scenario or create a custom disaster</div>
            </div>
          )}

          {!running && result && (
            <div className="flex-1 overflow-y-auto space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold" style={{ color: '#ff3366' }}>{result.scenario}</h3>
                <span className={`agent-badge severity-${result.severity}`}>{result.severity?.toUpperCase()}</span>
              </div>

              {/* Economic Impact */}
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: 'Population Affected', value: `${(result.economic_impact?.population_affected || 0).toLocaleString()}`, color: '#ff3366' },
                  { label: 'Business Impact', value: `₹${result.economic_impact?.business_impact_crores || 0} Cr`, color: '#ffaa00' },
                  { label: 'AI Prevention Savings', value: `₹${result.economic_impact?.net_savings_crores || 0} Cr`, color: '#00ff88' },
                ].map(item => (
                  <div key={item.label} className="p-3 rounded-xl text-center" style={{ background: 'rgba(255,255,255,0.03)' }}>
                    <div className="text-[10px] tracking-wider mb-1" style={{ color: '#64748b' }}>{item.label}</div>
                    <div className="text-lg font-bold" style={{ color: item.color }}>{item.value}</div>
                  </div>
                ))}
              </div>

              {/* Cascade Timeline */}
              {result.cascade_timeline?.length > 0 && (
                <div>
                  <div className="text-xs font-semibold mb-2" style={{ color: '#ffaa00' }}>⚡ CASCADE TIMELINE</div>
                  <div className="space-y-1">
                    {result.cascade_timeline.map((event: any, i: number) => (
                      <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                                  transition={{ delay: i * 0.1 }}
                                  className="flex items-center gap-2 text-xs p-2 rounded-lg"
                                  style={{ background: 'rgba(255,255,255,0.02)' }}>
                        <span className={`w-2 h-2 rounded-full ${event.severity === 'emergency' ? 'bg-red-500' : event.severity === 'critical' ? 'bg-amber-500' : 'bg-green-500'}`} />
                        <span className="font-mono text-[10px]" style={{ color: '#475569' }}>T+{event.step * 30}s</span>
                        <span style={{ color: '#94a3b8' }}>{event.description}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}

              {/* Healing Actions */}
              {result.healing_result?.actions_taken?.length > 0 && (
                <div>
                  <div className="text-xs font-semibold mb-2" style={{ color: '#00ff88' }}>🔧 AUTONOMOUS HEALING</div>
                  <div className="space-y-1">
                    {result.healing_result.actions_taken.map((action: any, i: number) => (
                      <div key={i} className="flex items-start gap-2 text-xs p-2 rounded-lg"
                           style={{ background: 'rgba(0,255,136,0.03)' }}>
                        <span style={{ color: '#00ff88' }}>✓</span>
                        <div>
                          <div style={{ color: '#e2e8f0' }}>{action.action}</div>
                          <div style={{ color: '#64748b' }}>{action.reasoning}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Before/After Metrics */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl" style={{ background: 'rgba(255,51,102,0.05)', border: '1px solid rgba(255,51,102,0.1)' }}>
                  <div className="text-[10px] font-semibold mb-2" style={{ color: '#ff3366' }}>BEFORE (HEALTHY)</div>
                  <div className="space-y-1 text-xs" style={{ color: '#94a3b8' }}>
                    <div>Health: {((result.before_metrics?.national_health_score || 0) * 100).toFixed(0)}%</div>
                    <div>Voltage: {result.before_metrics?.voltage_stability_index?.toFixed(3)}</div>
                    <div>Max Load: {result.before_metrics?.max_line_loading_pct?.toFixed(1)}%</div>
                  </div>
                </div>
                <div className="p-3 rounded-xl" style={{ background: 'rgba(0,255,136,0.05)', border: '1px solid rgba(0,255,136,0.1)' }}>
                  <div className="text-[10px] font-semibold mb-2" style={{ color: '#00ff88' }}>AFTER (HEALED)</div>
                  <div className="space-y-1 text-xs" style={{ color: '#94a3b8' }}>
                    <div>Health: {((result.after_metrics?.national_health_score || 0) * 100).toFixed(0)}%</div>
                    <div>Voltage: {result.after_metrics?.voltage_stability_index?.toFixed(3)}</div>
                    <div>Max Load: {result.after_metrics?.max_line_loading_pct?.toFixed(1)}%</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
