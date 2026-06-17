import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GRIDSENTINEL-X Ω — Autonomous Energy Defense Platform",
  description: "The World's First Autonomous Multi-Agent Energy Defense and Infrastructure Planning System",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased">
        <div className="scanline" />
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <main className="flex-1 flex flex-col overflow-hidden">
            <TopBar />
            <div className="flex-1 overflow-y-auto grid-bg p-4">
              {children}
            </div>
            <StatusRibbon />
          </main>
        </div>
      </body>
    </html>
  );
}

function Sidebar() {
  const navItems = [
    { href: '/', icon: '⚡', label: 'Command Center' },
    { href: '/debate', icon: '🗣️', label: 'Agent Debate' },
    { href: '/digital-twin', icon: '🌐', label: 'Digital Twin' },
    { href: '/black-swan', icon: '🦢', label: 'Black Swan' },
    { href: '/future-grid', icon: '🔮', label: 'Future Grid' },
    { href: '/self-healing', icon: '🔧', label: 'Self-Healing' },
    { href: '/economics', icon: '💰', label: 'Economics' },
  ];

  return (
    <aside className="w-[72px] h-screen flex flex-col items-center py-4 gap-2"
           style={{ background: 'linear-gradient(180deg, #0a0e27 0%, #060919 100%)', borderRight: '1px solid rgba(0,212,255,0.1)' }}>
      <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
           style={{ background: 'linear-gradient(135deg, #00d4ff, #8b5cf6)', fontSize: '1.25rem' }}>
        ⚡
      </div>
      {navItems.map(item => (
        <a key={item.href} href={item.href}
           className="w-12 h-12 rounded-xl flex items-center justify-center text-lg transition-all duration-200 hover:scale-110"
           style={{ background: 'rgba(255,255,255,0.03)' }}
           title={item.label}>
          {item.icon}
        </a>
      ))}
    </aside>
  );
}

function TopBar() {
  return (
    <header className="h-14 flex items-center justify-between px-6"
            style={{ background: 'rgba(10,14,39,0.9)', borderBottom: '1px solid rgba(0,212,255,0.08)' }}>
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold tracking-wide" style={{ color: '#00d4ff' }}>
          GRIDSENTINEL-X <span className="text-xs font-normal" style={{ color: '#8b5cf6' }}>Ω</span>
        </h1>
        <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(0,255,136,0.1)', color: '#00ff88', border: '1px solid rgba(0,255,136,0.2)' }}>
          AUTONOMOUS
        </span>
      </div>
      <div className="flex items-center gap-4 text-xs" style={{ fontFamily: 'JetBrains Mono, monospace', color: '#64748b' }}>
        <span>NATIONAL GRID</span>
        <span>•</span>
        <span>4 CITIES</span>
        <span>•</span>
        <span>12 AGENTS ONLINE</span>
        <span>•</span>
        <span style={{ color: '#00ff88' }}>● OPERATIONAL</span>
      </div>
    </header>
  );
}

function StatusRibbon() {
  return (
    <footer className="status-ribbon h-7 flex items-center justify-between px-6" style={{ color: '#64748b' }}>
      <div className="flex items-center gap-4">
        <span>SYS: NOMINAL</span>
        <span>|</span>
        <span>AGENTS: 12/12</span>
        <span>|</span>
        <span>GRID: CONVERGED</span>
      </div>
      <div className="flex items-center gap-4">
        <span>LATENCY: 3ms</span>
        <span>|</span>
        <span>v1.0.0-Ω</span>
      </div>
    </footer>
  );
}
