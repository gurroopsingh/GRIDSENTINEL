'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';

const CITIES = ['Mumbai', 'Delhi', 'Bengaluru', 'Chennai'];

export default function FutureGridPage() {
  const [city, setCity] = useState('Mumbai');
  const [year, setYear] = useState(2035);
  const [prompt, setPrompt] = useState('');
  const [blueprint, setBlueprint] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function design() {
    setLoading(true);
    setBlueprint(null);
    try {
      const res = await api.designFutureGrid(city, year, prompt || undefined);
      setBlueprint(res);
    } catch (err) { console.error(err); }
    setLoading(false);
  }

  return (
    <div className="h-full flex flex-col gap-4">
      <div>
        <h2 className="text-xl font-bold" style={{ color: '#8b5cf6' }}>🔮 Future Grid Designer</h2>
        <p className="text-xs mt-1" style={{ color: '#64748b' }}>Design tomorrow&apos;s infrastructure. AI-powered strategic planning.</p>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-4 min-h-0">
        {/* Input Panel */}
        <div className="col-span-4 space-y-3">
          <div className="glass-card">
            <label className="text-xs font-semibold block mb-2" style={{ color: '#8b5cf6' }}>TARGET CITY</label>
            <div className="grid grid-cols-2 gap-2">
              {CITIES.map(c => (
                <button key={c} onClick={() => setCity(c)}
                        className="py-2 rounded-lg text-xs font-semibold transition-all"
                        style={{
                          background: city === c ? 'rgba(139,92,246,0.2)' : 'rgba(255,255,255,0.03)',
                          color: city === c ? '#8b5cf6' : '#94a3b8',
                          border: `1px solid ${city === c ? 'rgba(139,92,246,0.3)' : 'rgba(255,255,255,0.05)'}`,
                        }}>
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div className="glass-card">
            <label className="text-xs font-semibold block mb-2" style={{ color: '#8b5cf6' }}>TARGET YEAR</label>
            <input type="range" min={2028} max={2050} value={year} onChange={e => setYear(+e.target.value)}
                   className="w-full" />
            <div className="text-center text-2xl font-bold mt-1" style={{ color: '#8b5cf6' }}>{year}</div>
          </div>

          <div className="glass-card">
            <label className="text-xs font-semibold block mb-2" style={{ color: '#8b5cf6' }}>CUSTOM PROMPT (Optional)</label>
            <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
                      placeholder={`e.g. "Design ${city}'s grid for ${year} with 80% renewables"`}
                      className="w-full h-20 bg-transparent border rounded-lg p-2 text-xs resize-none"
                      style={{ borderColor: 'rgba(139,92,246,0.2)', color: '#e2e8f0' }} />
          </div>

          <button onClick={design} disabled={loading}
                  className="w-full py-3 rounded-xl font-semibold text-sm transition-all"
                  style={{ background: 'linear-gradient(135deg, #8b5cf6, #06b6d4)', color: '#fff' }}>
            {loading ? '🔮 Designing...' : '⚡ Generate Blueprint'}
          </button>
        </div>

        {/* Blueprint Output */}
        <div className="col-span-8 glass-card flex flex-col overflow-hidden">
          {loading && (
            <motion.div animate={{ opacity: [0.5, 1, 0.5] }} transition={{ duration: 1.5, repeat: Infinity }}
                        className="flex-1 flex items-center justify-center flex-col gap-3">
              <div className="text-4xl">🔮</div>
              <div style={{ color: '#8b5cf6' }}>AI is designing {city}&apos;s grid for {year}...</div>
            </motion.div>
          )}

          {!loading && !blueprint && (
            <div className="flex-1 flex items-center justify-center flex-col gap-2" style={{ color: '#475569' }}>
              <div className="text-4xl">🏗️</div>
              <div>Configure parameters and generate a blueprint</div>
            </div>
          )}

          {!loading && blueprint && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                        className="flex-1 overflow-y-auto space-y-4">
              <h3 className="text-lg font-bold" style={{ color: '#8b5cf6' }}>
                {blueprint.city} Grid — {blueprint.target_year} Blueprint
              </h3>

              {/* Key Metrics */}
              <div className="grid grid-cols-4 gap-2">
                {[
                  { l: 'Current Capacity', v: `${blueprint.current_capacity_mw?.toFixed(0)} MW`, c: '#94a3b8' },
                  { l: 'Projected Demand', v: `${blueprint.projected_demand_mw?.toFixed(0)} MW`, c: '#ffaa00' },
                  { l: 'Total Investment', v: `₹${blueprint.estimated_cost_crores?.toLocaleString()} Cr`, c: '#8b5cf6' },
                  { l: 'Carbon Reduction', v: `${blueprint.carbon_reduction_percent}%`, c: '#00ff88' },
                ].map(m => (
                  <div key={m.l} className="p-3 rounded-xl text-center" style={{ background: 'rgba(255,255,255,0.03)' }}>
                    <div className="text-[10px] mb-1" style={{ color: '#64748b' }}>{m.l}</div>
                    <div className="text-sm font-bold" style={{ color: m.c }}>{m.v}</div>
                  </div>
                ))}
              </div>

              {/* Renewable Mix */}
              <div>
                <div className="text-xs font-semibold mb-2" style={{ color: '#00ff88' }}>☀️ RENEWABLE ENERGY MIX</div>
                <div className="space-y-2">
                  {blueprint.renewable_mix && Object.entries(blueprint.renewable_mix).map(([key, val]: [string, any]) => {
                    const total = Object.values(blueprint.renewable_mix as Record<string, number>).reduce((a: number, b: number) => a + b, 0);
                    const pct = total > 0 ? (val / total) * 100 : 0;
                    const colors: Record<string, string> = { solar_mw: '#ffaa00', wind_mw: '#3b82f6', hydro_mw: '#06b6d4', battery_storage_mwh: '#8b5cf6', thermal_mw: '#ef4444' };
                    return (
                      <div key={key}>
                        <div className="flex justify-between text-xs mb-1">
                          <span style={{ color: '#94a3b8' }}>{key.replace(/_/g, ' ').replace(/mw[h]?/, '').trim()}</span>
                          <span style={{ color: colors[key] || '#94a3b8' }}>{val} {key.includes('mwh') ? 'MWh' : 'MW'} ({pct.toFixed(0)}%)</span>
                        </div>
                        <div className="h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
                          <motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }}
                                      transition={{ duration: 1 }} className="h-full rounded-full"
                                      style={{ background: colors[key] || '#94a3b8' }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Infrastructure Projects */}
              <div>
                <div className="text-xs font-semibold mb-2" style={{ color: '#00d4ff' }}>🏗️ NEW INFRASTRUCTURE</div>
                <div className="space-y-2">
                  {blueprint.new_infrastructure?.map((proj: any, i: number) => (
                    <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="p-3 rounded-xl text-xs" style={{ background: 'rgba(255,255,255,0.03)' }}>
                      <div className="font-semibold" style={{ color: '#e2e8f0' }}>{proj.project}</div>
                      <div className="flex gap-4 mt-1" style={{ color: '#64748b' }}>
                        <span>Cost: ₹{proj.cost_crores} Cr</span>
                        <span>Timeline: {proj.timeline_years}y</span>
                        {proj.capacity_mw && <span>Capacity: {proj.capacity_mw} MW</span>}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              <div>
                <div className="text-xs font-semibold mb-2" style={{ color: '#ffaa00' }}>📋 RECOMMENDATIONS</div>
                <div className="space-y-1">
                  {blueprint.recommendations?.map((rec: string, i: number) => (
                    <div key={i} className="flex items-start gap-2 text-xs p-2 rounded" style={{ color: '#94a3b8' }}>
                      <span style={{ color: '#ffaa00' }}>→</span>
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
