'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';

export default function EconomicsPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([api.getMetrics(), api.getHistory()])
      .then(([met, hist]) => { setMetrics(met); setHistory(hist); })
      .catch(console.error);
  }, []);

  const totalSavings = history.reduce((sum, s) => sum + (s.economic_impact?.net_savings_crores || 0), 0);
  const totalPopProtected = history.reduce((sum, s) => sum + (s.economic_impact?.population_affected || 0), 0);
  const totalIncidents = history.length;

  return (
    <div className="h-full flex flex-col gap-4">
      <div>
        <h2 className="text-xl font-bold" style={{ color: '#8b5cf6' }}>💰 Economic Intelligence Center</h2>
        <p className="text-xs mt-1" style={{ color: '#64748b' }}>Financial impact analysis for every autonomous decision</p>
      </div>

      {/* Hero Stats */}
      <div className="grid grid-cols-4 gap-3">
        {[
          { l: 'TOTAL SAVINGS', v: `₹${totalSavings.toFixed(1)} Cr`, c: '#00ff88', bg: 'rgba(0,255,136,0.08)' },
          { l: 'POPULATION PROTECTED', v: totalPopProtected.toLocaleString(), c: '#00d4ff', bg: 'rgba(0,212,255,0.08)' },
          { l: 'INCIDENTS HANDLED', v: totalIncidents, c: '#8b5cf6', bg: 'rgba(139,92,246,0.08)' },
          { l: 'GRID HEALTH', v: `${((metrics?.national_health_score || 0) * 100).toFixed(0)}%`, c: (metrics?.national_health_score || 0) > 0.7 ? '#00ff88' : '#ffaa00', bg: 'rgba(255,170,0,0.08)' },
        ].map((s, i) => (
          <motion.div key={s.l} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="glass-card text-center py-4" style={{ background: s.bg }}>
            <div className="text-[10px] tracking-widest mb-2" style={{ color: '#64748b' }}>{s.l}</div>
            <div className="text-2xl font-bold" style={{ color: s.c }}>{s.v}</div>
          </motion.div>
        ))}
      </div>

      {/* Incident Impact Table */}
      <div className="flex-1 glass-card overflow-hidden flex flex-col">
        <div className="text-xs font-semibold mb-3" style={{ color: '#8b5cf6' }}>📊 INCIDENT ECONOMIC LEDGER</div>
        <div className="flex-1 overflow-y-auto">
          {history.length === 0 ? (
            <div className="text-center py-16 text-sm" style={{ color: '#475569' }}>
              No incidents recorded. Run scenarios in the Black Swan Simulator to see economic analysis.
            </div>
          ) : (
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left" style={{ color: '#64748b' }}>
                  <th className="pb-2 pr-4">Scenario</th>
                  <th className="pb-2 pr-4">Severity</th>
                  <th className="pb-2 pr-4">Population</th>
                  <th className="pb-2 pr-4">Business Impact</th>
                  <th className="pb-2 pr-4">Prevention Cost</th>
                  <th className="pb-2">Net Savings</th>
                </tr>
              </thead>
              <tbody>
                {history.map((sim, i) => (
                  <motion.tr key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                             transition={{ delay: i * 0.05 }}
                             className="border-t" style={{ borderColor: 'rgba(255,255,255,0.05)' }}>
                    <td className="py-2 pr-4" style={{ color: '#e2e8f0' }}>{sim.scenario}</td>
                    <td className="py-2 pr-4">
                      <span className={`agent-badge severity-${sim.severity}`}>{sim.severity}</span>
                    </td>
                    <td className="py-2 pr-4" style={{ color: '#ff3366' }}>
                      {sim.economic_impact?.population_affected?.toLocaleString()}
                    </td>
                    <td className="py-2 pr-4" style={{ color: '#ffaa00' }}>
                      ₹{sim.economic_impact?.business_impact_crores} Cr
                    </td>
                    <td className="py-2 pr-4" style={{ color: '#00d4ff' }}>
                      ₹{sim.economic_impact?.prevention_cost_crores} Cr
                    </td>
                    <td className="py-2 font-bold" style={{ color: '#00ff88' }}>
                      ₹{sim.economic_impact?.net_savings_crores} Cr
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
