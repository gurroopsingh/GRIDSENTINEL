'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { getWSUrl } from '@/lib/api';

export function useWebSocket() {
  const [gridState, setGridState] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const ws = new WebSocket('wss://gurroopsingh-gridsentinel.hf.space/ws');

    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      setTimeout(connect, 3000);
    };
    ws.onerror = () => ws.close();

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'initial_state' || msg.type === 'grid_update') {
          setGridState(msg.data);
          if (msg.data?.metrics) setMetrics(msg.data.metrics);
        }
        if (msg.type !== 'pong') {
          setEvents(prev => [...prev.slice(-100), msg]);
        }
      } catch { }
    };
  }, []);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return { gridState, metrics, events, connected };
}
