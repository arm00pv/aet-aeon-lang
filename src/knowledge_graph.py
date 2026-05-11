#!/usr/bin/env python3
"""
AEON Knowledge Graph System
Relation discovery for RAG
Dependencies: networkx, matplotlib (optional)
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, deque

import sys
sys.path.insert(0, '/home/zixen15/aet-aeon-lang/src')

__version__ = "0.7.0"


# Graph storage structures
nodes: Dict[str, Dict] = {}
edges: Dict[Tuple[str, str], Dict] = defaultdict(lambda: {'weight': 1, 'timestamp': 0})
node_count: int = 0


class RelationDiscovery:
    """
    Relations within knowledge graph
    
    Features:
    - Entity linking (connect concepts)
    - Fact verification (validate entities)
    - Path-based retrieval (find shortest path)
    - Relation extraction (identify relationships)
    - Graph traversal (explore graph structure)
    """
    
    @staticmethod
    def extract_relations(graph_data: Dict) -> List[Tuple]:
        """
        Extract relations from graph
        
        Args:
            graph_data: Graph data dictionary
        
        Returns:
            List of relations (node pairs)
        """
        # Extract entity relations (e.g., Person-WorksFor-Company)
        relations = []
        
        # For demo: return empty (would use actual graph traversal)
        return relations
    
    @staticmethod
    def discover_entities(text: str) -> List[str]:
        """
        Discover entities from text
        
        Args:
            text: Text to extract entities from
        
        Returns:
            List of entities
        """
        # Extract entities (would use NLP parsing)
        entities = text.split()[:3]  # Demo: use first 3 words as entities
        
        return entities
    
    @staticmethod
    def verify_fact(statement: str, knowledge_base: Dict = None) -> bool:
        """
        Verify fact against knowledge base
        
        Args:
            statement: Fact to verify
            knowledge_base: Knowledge base for verification
        
        Returns:
            bool: Whether fact is verified
        """
        # For demo: return True (would check against knowledge base)
        return True


class KnowledgeGraphAEON:
    """
    AET Knowledge Graph System
    
    Features:
    - Entity linking (connect related concepts)
    - Relation extraction (identify relationships)
    - Path finding (shortest path between nodes)
    - Dynamic graph updates (add/remove nodes/edges)
    - Subgraph extraction (find specific subgraphs)
    - Graph serialization (save/load graph)
    """
    
    def __init__(self):
        """
        Initialize knowledge graph
        """
        self._graph: Dict[str, Dict] = {}
        self._edges: Dict[Tuple[str, str], Dict] = {}
        self._node_count: int = 0
        self._relation_types: Set[str] = set()
    
    def add_node(self, node_id: str, attributes: Dict) -> bool:
        """
        Add node to graph
        
        Args:
            node_id: Node identifier
            attributes: Node attributes (label, type, metadata)
        
        Returns:
            bool: Whether node was added successfully
        """
        # Check if node already exists
        if node_id in self._graph:
            # Update existing node
            self._graph[node_id].update(attributes)
        
        else:
            self._graph[node_id] = attributes
            self._node_count += 1
        
        self._relation_types.add(attributes.get("type", "default"))
        
        return True
    
    def add_edge(self, source: str, target: str, relation: Dict) -> bool:
        """
        Add edge to graph
        
        Args:
            source: Source node
            target: Target node
            relation: Edge relation (type, weight, metadata)
        
        Returns:
            bool: Whether edge was added successfully
        """
        # Check if both nodes exist
        if source not in self._graph or target not in self._graph:
            return False
        
        # Add edge
        self._edges[(source, target)] = relation
    
        # Check if reverse edge exists
        if relation.get("reverse"):
            self._edges[(target, source)] = relation
    
        return True
    
    def node_neighbors(self, node_id: str) -> List[str]:
        """
        Get node neighbors
        
        Args:
            node_id: Node to get neighbors for
        
        Returns:
            List of neighbor node IDs
        """
        neighbors = []
        
        # Check all edges for this node
        for (source, target) in self._edges:
            if source == node_id:
                neighbors.append(target)
            elif target == node_id:
                neighbors.append(source)
        
        return neighbors
    
    def edge(self, source: str, target: str) -> Dict:
        """
        Get edge between nodes
        
        Args:
            source: Source node
            target: Target node
        
        Returns:
            Edge dictionary (or empty dict if no edge)
        """
        return self._edges.get((source, target), {})
    
    def delete_node(self, node_id: str) -> None:
        """
        Delete node from graph
        
        Args:
            node_id: Node to delete
        """
        # Remove node edges
        for (source, target) in list(self._edges):
            if source == node_id or target == node_id:
                del self._edges[(source, target)]
        
        # Remove node
        if node_id in self._graph:
            del self._graph[node_id]
            self._node_count -= 1
    
    def find_path(self, start: str, end: str, max_hops: int = 3) -> Optional[List]:
        """
        Find path between nodes (BFS)
        
        Args:
            start: Starting node
            end: Target node
            max_hops: Maximum path length
        
        Returns:
            Path as list of nodes, or None if no path
        """
        # BFS traversal
        queue = deque([(start, [start])])
        visited = set()
        
        while queue:
            node, path = queue.popleft()
            
            if node in visited:
                continue
            
            visited.add(node)
            
            # Check if we reached target
            if node == end:
                return path
            
            # Add neighbors
            for neighbor in self.node_neighbors(node):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
                    
                    # Prune if exceeds max hops
                    if len(path) < max_hops:
                        if neighbor == end:
                            return path + [neighbor]
        
        return None
    
    def get_subgraph(self, node_id: str, max_depth: int = 2) -> Dict:
        """
        Get subgraph centered at node
        
        Args:
            node_id: Center node
            max_depth: Maximum depth to explore
        
        Returns:
            Subgraph dictionary
        """
        subgraph = {"center": node_id}
        
        # BFS to find subgraph
        queue = deque([(node_id, 0)])
        visited = {node_id}
        
        while queue:
            node, depth = queue.popleft()
            
            if depth > max_depth:
                continue
            
            # Get neighbors
            for neighbor in self.node_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    neighbor_attributes = self._graph.get(neighbor, {})
                    subgraph[neighbor] = neighbor_attributes
                    
                    queue.append((neighbor, depth + 1))
                    subgraph["edges"].append({
                        "from": node,
                        "to": neighbor,
                        "type": "neighbor"
                    })
        
        return subgraph
    
    def serialize(self) -> Dict:
        """
        Serialize graph to dictionary
        
        Returns:
            Graph dictionary
        """
        return {
            "nodes": self._graph,
            "edges": self._edges,
            "node_count": self._node_count,
            "relation_types": list(self._relation_types)
        }
    
    def __len__(self) -> int:
        """
        Return number of nodes
        """
        return len(self._graph)


if __name__ == "__main__":
    print("=" * 60)
    print("[AEON Knowledge Graph - Demo]")
    print("=" * 60)
    
    # Create knowledge graph
    kg = KnowledgeGraphAEON()
    
    # Add nodes
    kg.add_node("Person_1", {"label": "Person", "name": "Alice"})
    kg.add_node("Person_2", {"label": "Person", "name": "Bob"})
    
    # Add edges
    kg.add_edge(
        "Person_1", "Person_2",
        {"type": "knows", "weight": 0.9}
    )
    
    # Find path
    path = kg.find_path("Person_1", "Person_2")
    print(f"\nPath: {path}")
    
    # Get subgraph
    subgraph = kg.get_subgraph("Person_1", max_depth=2)
    print(f"Subgraph centered at Person_1: {len(subgraph)} nodes")
    
    print("\n[Knowledge Graph complete!)")
