import React, { useCallback, useMemo, useEffect } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ConnectionMode,
  NodeTypes,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// Entity type color scheme
const entityTypeColors: Record<string, string> = {
  // Organizations
  organization: '#10b981', // green-500

  // Applications & Services
  application: '#8b5cf6', // violet-500
  service: '#a855f7', // purple-500
  repository: '#7c3aed', // violet-600

  // Infrastructure
  datacenter: '#3b82f6', // blue-500
  vpc: '#6366f1', // indigo-500
  subnet: '#6366f1', // indigo-500
  compute: '#ec4899', // pink-500
  network: '#14b8a6', // teal-500

  // Data
  storage: '#0ea5e9', // sky-500
  database: '#06b6d4', // cyan-500

  // Security & Identity
  user: '#f59e0b', // amber-500
  security_issue: '#ef4444', // red-500

  // Default fallback
  default: '#64748b', // slate-500
};

interface GraphNode {
  id: string;
  label: string;
  type: string;
  metadata?: Record<string, any>;
}

interface GraphEdge {
  from: string;
  to: string;
  label?: string;
}

interface NetworkGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  height?: string;
  onNodeClick?: (node: GraphNode) => void;
}

// Custom node component for better styling
const CustomNode: React.FC<{ data: any }> = ({ data }) => {
  const color = entityTypeColors[data.nodeType] || entityTypeColors.default;

  return (
    <div
      className="px-4 py-2 shadow-lg rounded-lg border-2 min-w-[150px] text-center cursor-pointer hover:shadow-xl transition-shadow"
      style={{
        backgroundColor: `${color}20`,
        borderColor: color,
      }}
    >
      <div className="font-semibold text-sm" style={{ color }}>
        {data.nodeType === 'organization' ? '🏢' : '📦'} {data.nodeType}
      </div>
      <div className="text-xs text-slate-700 mt-1 font-medium">{data.label}</div>
    </div>
  );
};

const nodeTypes: NodeTypes = {
  custom: CustomNode,
};

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  nodes: graphNodes,
  edges: graphEdges,
  height = '600px',
  onNodeClick,
}) => {
  // Convert our graph data to React Flow format
  const initialNodes: Node[] = useMemo(() => {
    return graphNodes.map((node, index) => {
      const angle = (index / graphNodes.length) * 2 * Math.PI;
      const radius = Math.min(300, graphNodes.length * 50);

      return {
        id: node.id,
        type: 'custom',
        position: {
          x: 400 + radius * Math.cos(angle),
          y: 300 + radius * Math.sin(angle),
        },
        data: {
          label: node.label,
          nodeType: node.type,
          metadata: node.metadata,
        },
      };
    });
  }, [graphNodes]);

  const initialEdges: Edge[] = useMemo(() => {
    console.log('NetworkGraph: Converting edges:', graphEdges);
    console.log('NetworkGraph: graphEdges type:', typeof graphEdges, 'isArray:', Array.isArray(graphEdges));

    if (!graphEdges || !Array.isArray(graphEdges)) {
      console.error('NetworkGraph: graphEdges is not an array!', graphEdges);
      return [];
    }

    const converted = graphEdges.map((edge, index) => {
      console.log(`NetworkGraph: Processing edge ${index}:`, edge);

      // Different colors for different edge types
      const edgeColor = edge.label === 'parent' ? '#10b981' :
                       edge.label === 'contains' ? '#3b82f6' :
                       '#f59e0b'; // dependencies

      const reactFlowEdge: Edge = {
        id: `edge-${index}`,
        source: edge.from,
        target: edge.to,
        label: edge.label || '',
        type: 'smoothstep',
        animated: true,
        style: {
          stroke: edgeColor,
          strokeWidth: 3,
        },
        labelStyle: {
          fill: edgeColor,
          fontWeight: 700,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: edgeColor,
        },
      };
      console.log('NetworkGraph: Created edge:', reactFlowEdge);
      return reactFlowEdge;
    });
    console.log('NetworkGraph: Total edges converted:', converted.length);
    console.log('NetworkGraph: Final edges array:', converted);
    return converted;
  }, [graphEdges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  console.log('NetworkGraph: Current nodes state:', nodes);
  console.log('NetworkGraph: Node IDs:', nodes.map(n => n.id));
  console.log('NetworkGraph: Current edges state:', edges);
  console.log('NetworkGraph: Edge connections:', edges.map(e => ({ id: e.id, source: e.source, target: e.target })));

  // Update nodes when graph data changes
  useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes, setNodes]);

  // Update edges when graph data changes
  useEffect(() => {
    console.log('NetworkGraph: Updating edges state with:', initialEdges);
    setEdges(initialEdges);
  }, [initialEdges, setEdges]);

  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        const graphNode: GraphNode = {
          id: node.id,
          label: node.data.label,
          type: node.data.nodeType,
          metadata: node.data.metadata,
        };
        onNodeClick(graphNode);
      }
    },
    [onNodeClick]
  );

  if (graphNodes.length === 0) {
    return (
      <div
        className="flex items-center justify-center bg-slate-50 rounded-lg border-2 border-dashed border-slate-300"
        style={{ height }}
      >
        <div className="text-center text-slate-500">
          <p className="text-lg font-medium">No relationships to display</p>
          <p className="text-sm mt-2">Create entities and dependencies to see the graph</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height, width: '100%' }} className="bg-slate-50 rounded-lg border border-slate-200">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        connectionMode={ConnectionMode.Loose}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={4}
        elementsSelectable={true}
        nodesConnectable={false}
        nodesDraggable={true}
        zoomOnScroll={true}
        panOnScroll={false}
        zoomOnDoubleClick={true}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#94a3b8" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const nodeType = node.data?.nodeType || 'default';
            return entityTypeColors[nodeType] || entityTypeColors.default;
          }}
          nodeStrokeWidth={3}
          zoomable
          pannable
        />
      </ReactFlow>
    </div>
  );
};
