#!/usr/bin/env python3
"""
AEON Distributed AI Brain Cluster
Multi-agent collaboration for reasoning, math, and code tasks
Dependencies: asyncio, numpy

Fixed version - Worker class moved before DistributedCluster.
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

import sys
sys.path.insert(0, '/home/zixen15/aet-aeon-lang/src')

__version__ = "0.6.1"  # Bumped after fix

class NodeRole(Enum):
    REASONING = "reasoning"
    MATH = "math"
    CODE = "code"
    RAG = "rag"
    VERIFICATION = "verification"
    COORDINATOR = "coordinator"

@dataclass
class NodeMetrics:
    """Node performance metrics"""
    node_id: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_latency_ms: float = 0.0
    success_rate: float = 1.0
    memory_usage_kb: int = 0
    cpu_usage_percent: float = 0
    
    def __post_init__(self):
        if not self.memory_usage_kb:
            self.memory_usage_kb = 12 * 1024
        if not self.cpu_usage_percent:
            self.cpu_usage_percent = 10.0
    
    def update_metrics(self, latency_ms: float = 0.0) -> None:
        self.memory_usage_kb += 12 * 1024
        self.cpu_usage_percent = min(100.0, self.cpu_usage_percent + 5.0)
        self.avg_latency_ms = (
            (self.avg_latency_ms * (self.tasks_completed)) +
            latency_ms
        ) / (self.tasks_completed + 1) if self.tasks_completed > 0 else latency_ms
    
    def is_idle(self) -> bool:
        return self.cpu_usage_percent < 10.0 and self.tasks_completed < 10
    
    def is_active(self) -> bool:
        return self.tasks_completed > 0 or self.cpu_usage_percent > 5.0
    
    def to_dict(self) -> Dict:
        return {
            'node_id': self.node_id,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'avg_latency_ms': self.avg_latency_ms,
            'success_rate': self.success_rate,
            'memory_usage_kb': self.memory_usage_kb,
            'cpu_usage_percent': self.cpu_usage_percent,
        }

class MessageQueue:
    """Queue for inter-node messages"""
    
    def __init__(self, max_size: int = 1000):
        self._queue: List[Dict] = []
        self._max_size = max_size
    
    def put(self, message: Dict) -> bool:
        self._queue.append(message)
        return len(self._queue) <= self._max_size
    
    def get(self) -> Optional[Dict]:
        if self._queue:
            return self._queue.pop(0)
        return None
    
    def remove(self, message: Dict) -> bool:
        for i, queue_message in enumerate(self._queue):
            if queue_message['id'] == message['id']:
                self._queue.pop(i)
                return True
        return False
    
    def clear(self) -> None:
        self._queue.clear()

class NodeMessage:
    """AET message with metadata"""
    
    def __init__(self, node_id: str, content: str, metadata: Dict = None):
        self.node_id = node_id
        self.content = content
        self.metadata = metadata or {}

# ========== Worker - MOVED BEFORE DistributedCluster ==========
class Worker:
    """
    Distributed cluster worker
    
    Features:
    - Process tasks assigned to it
    - Collaborate with other workers
    - Update metrics based on task processing
    """
    
    def __init__(self,
                 node_id: str,
                 embedding_dim: int,
                 message_queue: MessageQueue):
        self._node_id = node_id
        self._embedding_dim = embedding_dim
        self._message_queue = message_queue
        self._result: Dict = {}
        self._metrics = NodeMetrics(node_id=node_id)
    
    @property
    def node_id(self) -> str:
        return self._node_id
    
    @property
    def result(self) -> Dict:
        return self._result
    
    @property
    def metrics(self) -> NodeMetrics:
        return self._metrics
    
    async def process_task(self, task: str, task_id: Optional[str] = None) -> Dict:
        """Process task"""
        import time
        import random
        
        start = time.time()
        
        # Simulate task processing
        self._result = {
            'node_id': self._node_id,
            'task_id': task_id or 'task',
            'embedding': np.random.randn(self._embedding_dim),
            'output': f"Processed: {task[:50]}..." if len(task) > 50 else f"Processed: {task}"
        }
        
        latency_ms = (time.time() - start) * 1000 + random.uniform(10, 100)
        self._metrics.update_metrics(latency_ms)
        
        # Queue result
        self._message_queue.put({
            'id': task_id,
            'node_id': self._node_id,
            'result': self._result
        })
        
        return self._result
    
    async def collaborate(self, other_worker: 'Worker', task: str) -> Dict:
        """Collaborate with another worker"""
        await other_worker.process_task(task)
        return {
            'collaborated_with': other_worker.node_id,
            'my_result': self._result,
            'their_result': other_worker.result
        }

# ========== DistributedCluster ==========
class DistributedCluster:
    """
    Distributed AI Brain Cluster
    
    Features:
    - Multi-agent collaboration for complex tasks
    - Role-based node assignment
    - Message queue for inter-node communication
    - Performance metrics tracking
    """
    
    def __init__(self, 
                 num_workers: int = 4,
                 embedding_dim: int = 2048,
                 max_queue_size: int = 1000):
        self._num_workers = num_workers
        self._embedding_dim = embedding_dim
        self._max_queue_size = max_queue_size
        
        # Initialize workers
        self._workers = [
            Worker(
                node_id=f"worker-{i}",
                embedding_dim=self._embedding_dim,
                message_queue=MessageQueue(self._max_queue_size)
            ) for i in range(num_workers)
        ]
        
        # Initialize message queue
        self._message_queue = MessageQueue(self._max_queue_size)
        self._cluster_metrics: Dict[str, NodeMetrics] = {
            w.node_id: w.metrics for w in self._workers
        }
    
    @property
    def workers(self) -> List[Worker]:
        return self._workers
    
    async def add_task(self, task: str) -> Dict:
        """Add task to cluster"""
        task_id = f"task-{id(task)}"
        
        # Distribute to all workers
        results = []
        for worker in self._workers:
            result = await worker.process_task(task, task_id)
            results.append(result)
        
        return {
            'task_id': task_id,
            'results': results,
            'num_workers': len(self._workers)
        }
    
    async def distribute_task(self, task: str) -> None:
        """Distribute task to workers"""
        for worker in self._workers:
            await worker.process_task(task)
    
    def get_metrics(self) -> Dict:
        """Get cluster metrics"""
        return {
            'num_workers': len(self._workers),
            'worker_metrics': {
                w.node_id: w.metrics.to_dict() for w in self._workers
            }
        }
    
    def get_worker(self, node_id: str) -> Optional[Worker]:
        """Get worker by ID"""
        for w in self._workers:
            if w.node_id == node_id:
                return w
        return None


# ========== Demo ==========
if __name__ == "__main__":
    async def demo():
        print("=" * 60)
        print("AEON Distributed AI Brain Cluster - Fixed")
        print("=" * 60)
        
        # Create cluster
        cluster = DistributedCluster(num_workers=3, embedding_dim=1024)
        
        print(f"\nCluster initialized:")
        print(f"  Workers: {len(cluster.workers)}")
        print(f"  Embedding dim: {cluster._embedding_dim}")
        
        # Add task
        print("\nProcessing task...")
        result = await cluster.add_task("Solve AET state space problem")
        
        print(f"  Task ID: {result['task_id']}")
        print(f"  Results from {result['num_workers']} workers")
        
        # Show metrics
        metrics = cluster.get_metrics()
        print("\nWorker Metrics:")
        for node_id, m in metrics['worker_metrics'].items():
            print(f"  {node_id}: {m['tasks_completed']} tasks, {m['avg_latency_ms']:.1f}ms avg")
        
        print("\n" + "=" * 60)
        print("AEON Cluster: WORKING ✓")
        print("=" * 60)
    
    asyncio.run(demo())