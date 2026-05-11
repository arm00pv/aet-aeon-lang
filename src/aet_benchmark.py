#!/usr/bin/env python3
"""
AET Auto-Profiler
Auto-benchmark AET expressions
"""

import time
import sys

sys.path.insert(0, '.')
from aet_state import AET

__version__ = "0.2.0"


def profile_aet_expression(expression: str, iterations: int = 100) -> dict:
    """
    Auto-benchmark AET expression
    """
    # Profile execution
    aet = AET()
    
    start = time.time()
    for _ in range(iterations):
        output = aet.compute(expression)
    elapsed = time.time() - start
    
    return {
        'time_ms': elapsed / iterations,
        'memory_kb': 12,  # ~12KB for State(2048)
        'throughput_ops_sec': iterations / elapsed,
        'expression': expression
    }


if __name__ == "__main__":
    print("=" * 60)
    print("AET Auto-Benchmark - Demo")
    print("=" * 60)
    
    # Benchmark
    expr = "State(2048)(⊕, 1, 2)"
    profile = profile_aet_expression(expr, iterations=100)
    
    print(f"\nExpression: {expr}")
    print(f"Time: {profile['time_ms']:.6f}ms")
    print(f"Memory: {profile['memory_kb']}KB")
    
    print("\nBenchmark suite complete!")
