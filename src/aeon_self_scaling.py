#!/usr/bin/env python3
"""
AEON Self-Scaling Node
Dynamic scaling based on task complexity
Dependencies: asyncio, aiohttp, uvicorn (for async support)
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field

import sys
sys.path.insert(0, '/home/zixen15/aet-aeon-lang/src')
from aeon.aeon_node import AEONNode, NodeState

__version__ = "0.3.0"

@dataclass
class ScalingMetrics:
    """
    Scaling metrics for AEON node
    """
    task_complexity: float
    current_nodes: int
    active_connections: int
    memory_usage_kb: int
    cpu_usage_percent: float
    scaling_latency_ms: float
    recommended_scale: int
    
    def to_scale_factor(self) -> float:
        """
        Compute scale factor
        1.0 = current scale, 2.0 = double scale, etc.
        """
        return self.recommended_scale / self.current_nodes


class ScalingPolicy:
    """
    Determine when to scale up/down based on metrics
    """
    
    def __init__(self):
        self.metrics: List[ScalingMetrics] = []
    
    def compute_scale_factor(self, task_complexity: float, 
                            current_nodes: int,
                            memory_percent: float = 50.0) -> ScalingMetrics:
        """
        Compute optimal scale factor for node
        
        Args:
            task_complexity: 0.0 - 1.0 (0=simple, 1=complex)
            current_nodes: Current number of cluster nodes
            memory_percent: Current memory usage (%)
        """
        memory_percent = float(memory_percent)
        node = float(current_nodes)
        
        # Compute complexity score
        complexity_score = float(task_complexity)
        
        # Determine recommended scale
        # Complex tasks (0.7+) need more nodes
        if complexity_score >= 0.7:
            # Complex task: scale up by 2x
            recommended = max(2, int(node * ((complexity_score + memory_percent) / 50)))
        elif complexity_score >= 0.4:
            # Medium task: scale by 1.5x
            recommended = max(int(node * 1.5), node)
        elif complexity_score < 0.3:
            # Simple task: scale down by 0.5x (but maintain minimum 1)
            recommended = max(node - 1, int(node * 0.5))
        else:
            recommended = node
        
        latency_ms = max(0.5, 10.0 * (1.0 / (complexity_score + 0.1)))
        
        return ScalingMetrics(
            task_complexity=complexity_score,
            current_nodes=current_nodes,
            active_connections=self.metrics.append(
                active_connections=0,
                memory_usage_kb=memory_percent / 100 * 1024,
                cpu_usage_percent=complexity_score * 50,
                scaling_latency_ms=latency_ms,
                recommended_scale=recommended,
                recommended_scale=recommended
            )
            recommended_scale=recommended
        )


class SelfScalingAEONNode(AEONNode):
    """
    AEONNode with self-scaling capabilities
    """
    
    def __init__(self, cluster_size: int = 4, verbose: bool = False):
        """
        Args:
            cluster_size: Maximum cluster size (default=4 nodes)
            verbose: Enable scaling debug output
        """
        super().__init__(verbose=verbose)
        self._cluster_size = cluster_size
        self._scaling_policy = ScalingPolicy()
        self._scaling_active = False
        self._scale_factor = 1.0
        self._active_nodes: List[AEONNode] = []
    
    async def _scale_up(self) -> None:
        """
        Scale up cluster (add more nodes)
        """
        # Check if within cluster size limits
        if len(self._active_nodes) >= self._cluster_size:
            if self._verbose:
                print("[AEON] Cluster at capacity. Cannot scale up further.")
            return
        
        # Create new node for cluster
        new_node = AEONNode(
            name=f"node-{len(self._active_nodes) + 1}",
            model="qwen3.5:9b",  # Use same model as current
            temperature=0.3,
            verbose=False,
            warmup_iterations=1,
            verbose=False
        )
        
        # Add to cluster
        self._active_nodes.append(new_node)
        
        if self._verbose:
            print(f"[AEON] Cluster: {len(self._active_nodes)} nodes now active")
    
    async def _scale_down(self) -> None:
        """
        Scale down cluster (remove nodes if idle)
        """
        # Check if we can reduce cluster size
        if len(self._active_nodes) <= 1:
            if self._verbose:
                print("[AEON] Minimum cluster size (1) maintained.")
            return
        
        # Remove idle nodes
        idle_nodes = [n for n in self._active_nodes if n.is_idle()]
        
        if idle_nodes:
            for idle_node in idle_nodes[:1]:  # Remove one at a time
                self._active_nodes.remove(idle_node)
                if self._verbose:
                    print(f"[AEON] Cluster reduced to {len(self._active_nodes)} nodes")
    
    async def _balance_load(self, tasks: List[asyncio.Task]) -> None:
        """
        Balance load across cluster nodes
        """
        active_count = len(self._active_nodes)
        
        if active_count == 0:
            # Start with single node
            await self._active_nodes.append(AEONNode(
                name="node-1",
                model="qwen3.5:9b",
                temperature=0.3,
                warmup_iterations=1
            ))
            if self._verbose:
                print(f"[AEON] Cluster initialized with 1 node")
        
        # Distribute tasks across cluster
        task_queue = []
        current_node_index = 0
        
        for task_index, task in enumerate(tasks):
            # Round-robin across nodes
            current_node = self._active_nodes[current_node_index % active_count]
            task_queue.append((task, current_node))
            
            # Update node index
            current_node_index += 1
        
        # Execute tasks with load balancing
        for task, node in task_queue:
            await node.process_task(task)
    
    async def scale_based_on_complexity(self, task_complexity: float) -> None:
        """
        Scale cluster based on task complexity
        """
        metrics = self._scaling_policy.compute_scale_factor(
            task_complexity,
            len(self._active_nodes)
        )
        
        if self._verbose:
            print(f"[AEON] Scaling: {metrics.task_complexity:.2f} → {metrics.recommended_scale} nodes")
        
        if metrics.recommended_scale > len(self._active_nodes):
            await self._scale_up()
        
        elif metrics.recommended_scale < len(self._active_nodes) and metrics.recommended_scale > 0:
            await self._scale_down()
        
        if self._verbose:
            print(f"[AEON] Scaling complete. Active nodes: {len(self._active_nodes)}")
    
    async def process_task(self, task: asyncio.Task) -> None:
        """
        Process task with scaling logic
        """
        # Compute task complexity (would use AET analysis)
        task_complexity = float(task_complexity)
        
        # Scale cluster
        await self.scale_based_on_complexity(task_complexity)
        
        # Process task
        await super().process_task(task)
    
    def __len__(self) -> int:
        """
        Return current cluster size
        """
        return len(self._active_nodes)
    

if __name__ == "__main__":
    asyncio.run()
    print("[AEON] Self-scaling node demo (for testing)")
    node = SelfScalingAEONNode(cluster_size=4, verbose=True)
    print(f"[AEON] Cluster initialized with {len(node) if hasattr(node, '_active_nodes') else 0} node(s)")
print("=" * 60)
print("[self-scaling AEONNode complete")
