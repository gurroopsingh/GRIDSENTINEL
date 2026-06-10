'use client';

import { useState, useEffect, useRef, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html } from '@react-three/drei';
import { api } from '@/lib/api';
import * as THREE from 'three';

function GridNode({ position, name, type, status, color }: any) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.3;
      if (status === 'critical') {
        meshRef.current.scale.setScalar(1 + Math.sin(Date.now() * 0.005) * 0.15);
      }
    }
  });

  const size = type === 'slack' ? 0.5 : type === 'substation' ? 0.4 : type === 'generator' ? 0.35 : 0.25;
  const emissive = status === 'critical' ? '#ff3366' : status === 'warning' ? '#ffaa00' : color;

  return (
    <group position={position}>
      <mesh ref={meshRef} onPointerOver={() => setHovered(true)} onPointerOut={() => setHovered(false)}>
        {type === 'substation' ? <boxGeometry args={[size, size, size]} /> :
         type === 'generator' ? <octahedronGeometry args={[size]} /> :
         <sphereGeometry args={[size, 16, 16]} />}
        <meshStandardMaterial color={color} emissive={emissive} emissiveIntensity={hovered ? 1.5 : 0.5}
                              transparent opacity={0.85} />
      </mesh>
      {/* Glow */}
      <pointLight color={emissive} intensity={hovered ? 3 : 1} distance={3} />
      {hovered && (
        <Html distanceFactor={10}>
          <div className="glass-card p-2 text-[10px] whitespace-nowrap" style={{ color: '#e2e8f0', minWidth: 120 }}>
            <div className="font-bold" style={{ color }}>{name}</div>
            <div style={{ color: '#64748b' }}>{type} • {status}</div>
          </div>
        </Html>
      )}
    </group>
  );
}

function PowerLine({ start, end, status }: { start: [number, number, number]; end: [number, number, number]; status: string }) {
  const ref = useRef<THREE.Line>(null);
  const color = status === 'critical' ? '#ff3366' : status === 'warning' ? '#ffaa00' : '#00d4ff';

  const points = [new THREE.Vector3(...start), new THREE.Vector3(...end)];
  const geometry = new THREE.BufferGeometry().setFromPoints(points);

  return (
    // @ts-ignore
    <line ref={ref as any} geometry={geometry}>
      <lineBasicMaterial color={color} transparent opacity={status === 'critical' ? 0.9 : 0.3} linewidth={1} />
    </line>
  );
}

function GridScene({ topology, gridState }: { topology: any; gridState: any }) {
  if (!topology?.nodes) return null;

  const CITY_POSITIONS: Record<string, [number, number, number]> = {
    Mumbai: [-6, 0, -2],
    Delhi: [-2, 0, 6],
    Bengaluru: [4, 0, -4],
    Chennai: [6, 0, 2],
  };

  const nodePositions: Record<number, [number, number, number]> = {};

  topology.nodes.forEach((node: any, i: number) => {
    const cityBase = CITY_POSITIONS[node.city] || [0, 0, 0];
    const angle = (i % 12) * (Math.PI * 2 / 12);
    const radius = node.type === 'slack' ? 0 : 2 + (i % 3);
    nodePositions[node.id] = [
      cityBase[0] + Math.cos(angle) * radius,
      (node.vn_kv > 100 ? 1 : 0),
      cityBase[2] + Math.sin(angle) * radius,
    ];
  });

  const CITY_COLORS: Record<string, string> = {
    Mumbai: '#00d4ff', Delhi: '#8b5cf6', Bengaluru: '#00ff88', Chennai: '#ffaa00',
  };

  // Get line statuses from grid state
  const getLineStatus = (edgeName: string) => {
    for (const city of (gridState?.cities || [])) {
      const line = city.lines?.find((l: any) => l.name === edgeName);
      if (line) return line.status;
    }
    return 'normal';
  };

  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 10, 0]} intensity={0.5} color="#00d4ff" />

      {/* Grid floor */}
      <gridHelper args={[30, 30, '#1e2a4a', '#0d1330']} position={[0, -0.5, 0]} />

      {/* Nodes */}
      {topology.nodes.map((node: any) => (
        <GridNode key={node.id} position={nodePositions[node.id]}
                  name={node.name} type={node.type} color={CITY_COLORS[node.city] || '#00d4ff'}
                  status={'normal'} />
      ))}

      {/* Edges */}
      {topology.edges.map((edge: any) => {
        const start = nodePositions[edge.from];
        const end = nodePositions[edge.to];
        if (!start || !end) return null;
        return <PowerLine key={edge.id} start={start} end={end}
                          status={edge.in_service ? getLineStatus(edge.name) : 'critical'} />;
      })}

      {/* City Labels */}
      {Object.entries(CITY_POSITIONS).map(([city, pos]) => (
        <Text key={city} position={[pos[0], 3, pos[2]]} fontSize={0.5}
              color={CITY_COLORS[city]} anchorX="center" anchorY="middle">
          {city}
        </Text>
      ))}

      <OrbitControls enableDamping dampingFactor={0.05} maxPolarAngle={Math.PI / 2.2}
                     minDistance={5} maxDistance={25} />
    </>
  );
}

export default function DigitalTwinPage() {
  const [topology, setTopology] = useState<any>(null);
  const [gridState, setGridState] = useState<any>(null);

  useEffect(() => {
    Promise.all([api.getTopology(), api.getGridState()])
      .then(([topo, state]) => { setTopology(topo); setGridState(state); })
      .catch(console.error);
  }, []);

  return (
    <div className="h-full flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold" style={{ color: '#00d4ff' }}>🌐 National Digital Twin</h2>
          <p className="text-xs mt-1" style={{ color: '#64748b' }}>3D visualization of India&apos;s power grid — Mumbai • Delhi • Bengaluru • Chennai</p>
        </div>
      </div>
      <div className="flex-1 glass-card p-0 overflow-hidden rounded-2xl" style={{ minHeight: 500 }}>
        <Canvas camera={{ position: [12, 8, 12], fov: 50 }} style={{ background: '#030712' }}>
          <Suspense fallback={null}>
            <GridScene topology={topology} gridState={gridState} />
          </Suspense>
        </Canvas>
      </div>
    </div>
  );
}
