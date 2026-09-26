'use client';

import React from 'react';
import { ReactFlow, Controls, Background, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [
  { id: '1', position: { x: 250, y: 0 }, data: { label: 'IS 456: Plain & Reinforced Concrete' }, type: 'input' },
  { id: '2', position: { x: 100, y: 100 }, data: { label: 'IS 10262: Concrete Mix Proportioning' } },
  { id: '3', position: { x: 400, y: 100 }, data: { label: 'IS 383: Coarse & Fine Aggregates' } },
  { id: '4', position: { x: 100, y: 200 }, data: { label: 'IS 8112: 43 Grade OPC' } },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e1-3', source: '1', target: '3', animated: true },
  { id: 'e2-4', source: '2', target: '4' },
];

export default function NormativeTreeGraph() {
  return (
    <div style={{ width: '100%', height: '500px', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
      <ReactFlow defaultNodes={initialNodes} defaultEdges={initialEdges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}