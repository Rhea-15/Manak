'use client';

import React, { useMemo } from 'react';
import { ReactFlow, Controls, Background, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

type LinkedStandard = {
  standard_number: string;
  title?: string;
  relationship?: string;
};

type GraphData = {
  found?: boolean;
  standard_number?: string;
  title?: string;
  linked_standards?: LinkedStandard[];
};

export default function NormativeTreeGraph({ graphData }: { graphData?: GraphData | null }) {
  const { nodes, edges } = useMemo(() => {
    const rootStandard = graphData?.standard_number || 'Selected Standard';
    const rootTitle = graphData?.title || 'Primary Specification';

    const generatedNodes: Node[] = [
      {
        id: 'root',
        position: { x: 250, y: 20 },
        data: { label: `${rootStandard}: ${rootTitle}` },
        type: 'input',
        style: { background: '#EDE0EC', borderColor: '#74478A', fontWeight: 600, color: '#211735' },
      },
    ];

    const generatedEdges: Edge[] = [];
    const linked = graphData?.linked_standards || [];

    if (linked.length === 0) {
      generatedNodes.push({
        id: 'no-links',
        position: { x: 250, y: 150 },
        data: { label: 'No allied or normative references linked in Neo4j' },
        style: { background: '#F8F9FA', borderColor: '#CCC', color: '#666' },
      });
      generatedEdges.push({
        id: 'e-root-none',
        source: 'root',
        target: 'no-links',
        animated: true,
      });
    } else {
      linked.forEach((item, index) => {
        const id = `node-${index}`;
        const xOffset = 60 + (index % 3) * 220;
        const yOffset = 140 + Math.floor(index / 3) * 110;

        generatedNodes.push({
          id,
          position: { x: xOffset, y: yOffset },
          data: { label: `${item.standard_number}: ${item.relationship || 'REFERENCED'}` },
          style: { background: '#FFFFFF', borderColor: '#DCCBCF', color: '#211735' },
        });

        generatedEdges.push({
          id: `e-root-${id}`,
          source: 'root',
          target: id,
          label: item.relationship,
          animated: true,
        });
      });
    }

    return { nodes: generatedNodes, edges: generatedEdges };
  }, [graphData]);

  return (
    <div className="w-full h-[450px] rounded-xl border border-slate-200 bg-white">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}