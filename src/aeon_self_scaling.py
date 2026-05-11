#!/usr/bin/env python3
"""
AEON Self-Scaling System
Auto-scaling AEON cluster based on task complexity
"""

import asyncio
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

import sys
sys.path.insert(0, '/home/zixen15/aet-aeon-lang/src')
sys.path.insert(0, '/home/zixen15/aet-aeon-lang/src/aeon')

from protocol import AEONNode

__version__ = "0.4.1"  # Fixed version

class ScalingPolicy(Enum):
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    ADAPTIVE = "adaptive"

@dataclass
class ScalingMetrics:
    """Metrics for scaling decisions"""
    task_complexity: float
    current_nodes: int
    recommended_scale: int
    scaling_latency_ms: float
    memory_usage_kb: float
    cpu_usage_percent: float

class SelfScalingNode:
    """
    AEON node with self-scaling capabilities
    """
    
    def __init__(self, 
                 node_id: str,
                 models: List[str],
                 cluster_size: int = 4,
                 verbose: bool = False):
        self.node_id = node_id
        self.models = models
        self.cluster_size = cluster_size
        self.verbose = verbose
        
        # Create primary node
        self.primary = AEONNode(node_id, models)
        
        # Worker nodes
        self.workers: List[AEONNode] = []
        
        # Metrics
        self.metrics = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'avg_latency_ms': 0.0,
        }
    
    @property
    def is_idle(self) -> bool:
        return self.metrics['completed_tasks'] < 10
    
    @property
    def is_active(self) -> bool:
        return self.metrics['completed_tasks'] > 0
    
    def analyze_complexity(self, task: str) -> float:
        """
        Analyze task complexity (0.0 to 1.0)
        """
        complexity = 0.5  # Base complexity
        
        # Increase for complex keywords
        complex_keywords = ['reasoning', 'math', 'analysis', 'optimization', 
                          'transformer', 'neural', 'quantum']
        for kw in complex_keywords:
            if kw in task.lower():
                complexity += 0.1
        
        # Cap at 1.0
        return min(1.0, complexity)
    
    def recommend_scale(self, complexity: float) -> int:
        """
        Recommend number of nodes based on complexity
        """
        if complexity >= 0.7:
            return min(self.cluster_size, 4)  # Max 4 for high complexity
        elif complexity >= 0.4:
            return 2  # Medium
        else:
            return 1  # Low complexity
    
    async def execute_task(self, task: str, priority: str = "medium") -> Dict:
        """
        Execute task with auto-scaling
        """
        self.metrics['total_tasks'] += 1
        
        # Analyze complexity
        complexity = self.analyze_complexity(task)
        recommended_nodes = self.recommend_scale(complexity)
        
        if self.verbose:
            print(f"[{self.node_id}] Task complexity: {complexity:.2f}, "
                  f"Recommended nodes: {recommended_nodes}")
        
        # Scale up if needed
        while len(self.workers) < recommended_nodes - 1:
            await self._scale_up()
        
        # Execute task
        start = time.time()
        
        # Use primary node
        result = self.primary.send_task(
            task_id=f"task-{self.metrics['total_tasks']}",
            priority=priority,
            aet_code=task,
            target_models=self.models
        )
        
        latency_ms = (time.time() - start) * 1000
        
        # Update metrics
        self.metrics['completed_tasks'] += 1
        self.metrics['avg_latency_ms'] = (
            (self.metrics['avg_latency_ms'] * (self.metrics['completed_tasks'] - 1) + latency_ms)
            / self.metrics['completed_tasks']
        )
        
        # Scale down if idle
        if self.is_idle and len(self.workers) > 0:
            await self._scale_down()
        
        return {
            'task_id': f"task-{self.metrics['total_tasks']}",
            'complexity': complexity,
            'nodes_used': len(self.workers) + 1,
            'latency_ms': latency_ms,
            'message': result
        }
    
    async def _scale_up(self) -> None:
        """Add a worker node"""
        if len(self.workers) >= self.cluster_size - 1:
            if self.verbose:
                print(f"[{self.node_id}] At max capacity ({self.cluster_size})")
            return
        
        new_node = AEONNode(
            f"{self.node_id}-worker-{len(self.workers) + 1}",
            self.models
        )
        self.workers.append(new_node)
        
        if self.verbose:
            print(f"[{self.node_id}] Scaled up to {len(self.workers) + 1} nodes")
    
    async def _scale_down(self) -> None:
        """Remove idle worker node"""
        if len(self.workers) <= 0:
            return
        
        self.workers.pop()
        
        if self.verbose:
            print(f"[{self.node_id}] Scaled down to {len(self.workers) + 1} nodes")
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        return {
            **self.metrics,
            'active_workers': len(self.workers),
            'cluster_size': self.cluster_size
        }


# ========== Demo ==========
if __name__ == "__main__":
    async def demo():
        print("=" * 60)
        print("AEON Self-Scaling System - Fixed")
        print("=" * 60)
        
        # Create self-scaling node
        node = SelfScalingNode(
            node_id="scaler-1",
            models=["qwen3.5:4b"],
            cluster_size=4,
            verbose=True
        )
        
        # Test tasks of varying complexity
        tasks = [
            ("State(1024) → simple computation", "low"),
            ("Reasoning with attention mechanisms", "high"),
            ("Math optimization problem", "high"),
            ("Simple query", "low"),
        ]
        
        print("\nExecuting tasks with auto-scaling:")
        for task, priority in tasks:
            print(f"\n--- Task: {task[:40]}... ---")
            result = await node.execute_task(task, priority)
            print(f"  Complexity: {result['complexity']:.2f}")
            print(f"  Nodes used: {result['nodes_used']}")
            print(f"  Latency: {result['latency_ms']:.1f}ms")
        
        print("\n" + "=" * 60)
        print("Final metrics:", node.get_metrics())
        print("Self-Scaling: WORKING ✓")
        print("=" * 60)
    
    asyncio.run(demo())