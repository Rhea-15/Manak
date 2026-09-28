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
        position: { x: 320, y: 30 },
        data: {
          label: (
            <div className="text-center px-2 py-1">
              <div className="font-bold text-sm text-[#211735]">{rootStandard}</div>
              <div className="text-xs text-[#74478A] mt-0.5">{rootTitle}</div>
            </div>
          ),
        },
        type: 'input',
        style: {
          background: '#EDE0EC',
          borderColor: '#74478A',
          borderWidth: 2,
          borderRadius: 12,
          minWidth: 220,
        },
      },
    ];

    const generatedEdges: Edge[] = [];
    const linked = graphData?.linked_standards || [];

    if (linked.length === 0) {
      generatedNodes.push({
        id: 'no-links',
        position: { x: 320, y: 180 },
        data: { label: 'No allied or normative references linked in Neo4j' },
        style: { background: '#F8F9FA', borderColor: '#CCC', color: '#666', borderRadius: 8 },
      });
      generatedEdges.push({
        id: 'e-root-none',
        source: 'root',
        target: 'no-links',
        animated: true,
      });
    } else {
      const itemsPerRow = 3;
      const xSpacing = 260;
      const ySpacing = 130;

      linked.forEach((item, index) => {
        const id = `node-${index}`;
        const row = Math.floor(index / itemsPerRow);
        const col = index % itemsPerRow;

        // Center rows nicely beneath root node
        const xOffset = 60 + col * xSpacing;
        const yOffset = 180 + row * ySpacing;

        // Use the actual standard title from PostgreSQL/Neo4j
        const standardTitle = item.title || 'Referenced Standard';

        generatedNodes.push({
          id,
          position: { x: xOffset, y: yOffset },
          data: {
            label: (
              <div className="text-center px-2 py-1">
                <div className="font-semibold text-xs text-[#211735]">{item.standard_number}</div>
                <div className="text-[11px] text-[#554a5c] mt-0.5 line-clamp-2">{standardTitle}</div>
              </div>
            ),
          },
          style: {
            background: '#FFFFFF',
            borderColor: '#DCCBCF',
            borderWidth: 1.5,
            borderRadius: 10,
            width: 220,
            boxShadow: '0 2px 6px rgba(0,0,0,0.04)',
          },
        });

        generatedEdges.push({
          id: `e-root-${id}`,
          source: 'root',
          target: id,
          animated: true,
          style: { stroke: '#A35A91', strokeWidth: 1.5 },
        });
      });
    }

    return { nodes: generatedNodes, edges: generatedEdges };
  }, [graphData]);

  return (
    <div className="w-full h-[480px] rounded-2xl border border-[#E4DAD5] bg-[#FAF7FA]">
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background gap={18} size={1} color="#DDD2DC" />
        <Controls />
      </ReactFlow>
    </div>
  );
}