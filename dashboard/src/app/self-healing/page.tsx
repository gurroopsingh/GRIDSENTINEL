'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';

export default function SelfHealingPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    api.getHistory().then(setHistory).catch(console.error);
  }, []);

  return (
    <div className="h-full flex flex-col gap-4">
      <div>
        <h2 className="text-xl font-bold" style={{ color: '#00ff88' }}>🔧 Self-Healing Operations</h2>
        <p className="text-xs mt-1" style={{ color: '#64748b' }}>Autonomous grid repair actions and decision audit trail</p>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        <div className="col-span-5 glass-card flex flex-col overflow-hidden">
          <div className="text-xs font-semibold mb-3" style={{ color: '#00ff88' }}>HEALING HISTORY</div>
          <div className="flex-1 overflow-y-auto space-y-2">
            {history.length === 0 ? (
              <div className="text-center py-12 text-xs" style={{ color: '#475569' }}>
                No healing events yet. Run a Black Swan scenario first.
              </div>
            ) : (
              history.map((sim, i) => (
                <motion.div key={sim.id || i} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                            onClick={() => setSelected(sim)}
                            className={`p-3 rounded-xl cursor-pointer transition-all ${selected?.id === sim.id ? 'ring-1' : ''}`}
                            style={{ background: 'rgba(255,255,255,0.03)', '--tw-ring-color': 'rgba(0,255,136,0.3)' } as any}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold" style={{ color: '#e2e8f0' }}>{sim.scenario}</span>
                    <span className={`agent-badge severity-${sim.severity}`}>{sim.severity}</span>
                  </div>
                  <div className="text-[10px] flex gap-3" style={{ color: '#64748b' }}>
                    <span>{sim.healing_result?.total_actions || 0} actions</span>
                    <span>{sim.healing_result?.success ? '✅ Healed' : '⚠️ Partial'}</span>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>

        <div className="col-span-7 glass-card flex flex-col overflow-hidden">
          {selected ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 overflow-y-auto space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold" style={{ color: '#00ff88' }}>{selected.scenario}</h3>
                <span style={{ color: selected.healing_result?.success ? '#00ff88' : '#ffaa00' }}>
                  {selected.healing_result?.success ? '✅ FULLY HEALED' : '⚠️ PARTIAL RECOVERY'}
                </span>
              </div>

              <div className="text-xs font-semibold" style={{ color: '#00d4ff' }}>STRATEGIES DEPLOYED</div>
              <div className="flex flex-wrap gap-2">
                {selected.healing_result?.strategies_used?.map((s: string) => (
                  <span key={s} className="agent-badge severity-healthy">{s.replace(/_/g, ' ')}</span>
                ))}
              </div>

              <div className="text-xs font-semibold" style={{ color: '#00d4ff' }}>AUTONOMOUS ACTIONS</div>
              <div className="space-y-2">
                {selected.healing_result?.actions_taken?.map((action: any, i: number) => (
                  <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: i * 0.15 }}
                              className="p-3 rounded-xl" style={{ background: 'rgba(0,255,136,0.03)', borderLeft: '3px solid #00ff88' }}>
                    <div className="text-xs font-semibold" style={{ color: '#e2e8f0' }}>{action.action}</div>
                    <div className="text-[10px] mt-1" style={{ color: '#64748b' }}>{action.reasoning}</div>
                    <div className="text-[10px] mt-1" style={{ color: '#00ff88' }}>Strategy: {action.strategy}</div>
                  </motion.div>
                ))}
              </div>

              {selected.economic_impact && (
                <>
                  <div className="text-xs font-semibold" style={{ color: '#8b5cf6' }}>ECONOMIC OUTCOME</div>
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="p-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                      <div className="text-[10px]" style={{ color: '#64748b' }}>Impact Prevented</div>
                      <div className="text-sm font-bold" style={{ color: '#00ff88' }}>₹{selected.economic_impact.net_savings_crores} Cr</div>
                    </div>
                    <div className="p-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                      <div className="text-[10px]" style={{ color: '#64748b' }}>People Protected</div>
                      <div className="text-sm font-bold" style={{ color: '#00d4ff' }}>{selected.economic_impact.population_affected?.toLocaleString()}</div>
                    </div>
                    <div className="p-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                      <div className="text-[10px]" style={{ color: '#64748b' }}>Response Time</div>
                      <div className="text-sm font-bold" style={{ color: '#ffaa00' }}>{selected.duration_seconds?.toFixed(1)}s</div>
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          ) : (
            <div className="flex-1 flex items-center justify-center" style={{ color: '#475569' }}>
              Select a healing event to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
