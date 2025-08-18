/**
 * Organization Tree Component with React Flow
 */
import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  MiniMap,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  ConnectionMode,
  NodeTypes,
  MarkerType,
  ReactFlowProvider
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Box, CircularProgress, Typography } from '@mui/material';
import OrgNodeCard from './OrgNodeCard';
import { OrgUnit } from '../../types/organization';

interface OrgTreeProps {
  data: any[];
  loading: boolean;
  sandboxMode: boolean;
  onNodeUpdate: (unitId: string, newReportsTo: string | null) => void;
}

// Custom node types
const nodeTypes: NodeTypes = {
  orgUnit: OrgNodeCard,
};

const OrgTree: React.FC<OrgTreeProps> = ({ 
  data, 
  loading, 
  sandboxMode,
  onNodeUpdate 
}) => {
  // Convert tree data to React Flow nodes and edges
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];
    let yPos = 0;
    const levelWidth = 350;
    const nodeHeight = 200;
    const verticalSpacing = 250;

    // Helper function to process tree recursively
    const processNode = (
      node: any, 
      level: number = 0, 
      parentId: string | null = null,
      index: number = 0
    ) => {
      const nodeId = node.id;
      const xPos = level * levelWidth;
      
      // Add node
      nodes.push({
        id: nodeId,
        type: 'orgUnit',
        position: { x: xPos, y: yPos },
        data: {
          ...node.data,
          sandboxMode,
          onUpdate: onNodeUpdate
        },
      });

      // Add edge to parent if exists
      if (parentId) {
        edges.push({
          id: `${parentId}-${nodeId}`,
          source: parentId,
          target: nodeId,
          type: 'smoothstep',
          animated: sandboxMode,
          style: { stroke: '#b1b1b7', strokeWidth: 2 },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 20,
            height: 20,
            color: '#b1b1b7',
          },
        });
      }

      yPos += verticalSpacing;

      // Process children
      if (node.children && node.children.length > 0) {
        node.children.forEach((child: any, idx: number) => {
          processNode(child, level + 1, nodeId, idx);
        });
      }
    };

    // Process all root nodes
    data.forEach((rootNode, index) => {
      processNode(rootNode, 0, null, index);
    });

    return { nodes, edges };
  }, [data, sandboxMode, onNodeUpdate]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Handle new connections (drag and drop)
  const onConnect = useCallback(
    (params: Connection) => {
      if (!sandboxMode) return;

      // Update the reporting structure
      if (params.source && params.target) {
        onNodeUpdate(params.target, params.source);
      }

      setEdges((eds) => addEdge({
        ...params,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#b1b1b7', strokeWidth: 2 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#b1b1b7',
        },
      }, eds));
    },
    [sandboxMode, onNodeUpdate, setEdges]
  );

  // Handle node drag
  const onNodeDragStop = useCallback(
    (event: React.MouseEvent, node: Node) => {
      if (!sandboxMode) return;
      
      // Find if node was dropped on another node
      const targetNode = nodes.find(n => {
        if (n.id === node.id) return false;
        
        const targetBounds = {
          x: n.position.x,
          y: n.position.y,
          width: 300,
          height: 150
        };
        
        return (
          node.position.x >= targetBounds.x &&
          node.position.x <= targetBounds.x + targetBounds.width &&
          node.position.y >= targetBounds.y &&
          node.position.y <= targetBounds.y + targetBounds.height
        );
      });

      if (targetNode) {
        // Update reporting structure
        onNodeUpdate(node.id, targetNode.id);
      }
    },
    [sandboxMode, nodes, onNodeUpdate]
  );

  // Handle edge deletion
  const onEdgesDelete = useCallback(
    (deletedEdges: Edge[]) => {
      if (!sandboxMode) return;

      deletedEdges.forEach(edge => {
        // Remove reporting relationship
        onNodeUpdate(edge.target, null);
      });
    },
    [sandboxMode, onNodeUpdate]
  );

  if (loading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%' 
      }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%' 
      }}>
        <Typography variant="h6" color="textSecondary">
          조직 데이터가 없습니다.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height: '80vh' }}>
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeDragStop={onNodeDragStop}
          onEdgesDelete={onEdgesDelete}
          nodeTypes={nodeTypes}
          connectionMode={ConnectionMode.Loose}
          fitView
          fitViewOptions={{
            padding: 0.2,
            includeHiddenNodes: false,
          }}
          defaultEdgeOptions={{
            type: 'smoothstep',
            animated: sandboxMode,
          }}
          deleteKeyCode={sandboxMode ? 'Delete' : null}
          multiSelectionKeyCode={sandboxMode ? 'Control' : null}
        >
          <Background variant="dots" gap={12} size={1} />
          <Controls />
          <MiniMap 
            nodeStrokeColor={(node) => {
              if (node.data?.company === 'OK저축은행') return '#4169E1';
              if (node.data?.company === 'OK캐피탈') return '#FF6347';
              return '#888';
            }}
            nodeColor={(node) => {
              if (node.data?.company === 'OK저축은행') return '#E6F2FF';
              if (node.data?.company === 'OK캐피탈') return '#FFE6E6';
              return '#f5f5f5';
            }}
            nodeBorderRadius={2}
          />
        </ReactFlow>
      </ReactFlowProvider>
    </Box>
  );
};

export default OrgTree;