#!/usr/bin/env python3
"""
AET Auto-Profiler
Real benchmark system for AET expressions
"""

import time
import numpy as np
import sys
from typing import List

sys.path.insert(0, '/home/zixen15/aet-aeon-lang/src')

from aet_state import AET, ReLU, Tanh, LayerNorm

__version__ = "0.3.0"  # Working version

def profile_aet_expression(expression: str, iterations: int = 100) -> dict:
    """
    Profile AET expression execution
    
    Args:
        expression: AET expression string
        iterations: Number of iterations for timing
    
    Returns:
        Profile results dict
    """
    aet = AET()
    
    # Warm-up
    for _ in range(5):
        try:
            aet.compute(expression)
        except:
            pass
    
    # Benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = aet.compute(expression)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # ms
    
    # Compute statistics
    times_arr = np.array(times)
    
    return {
        'expression': expression,
        'iterations': iterations,
        'time_ms': {
            'mean': float(np.mean(times_arr)),
            'median': float(np.median(times_arr)),
            'min': float(np.min(times_arr)),
            'max': float(np.max(times_arr)),
            'std': float(np.std(times_arr)),
            'p95': float(np.percentile(times_arr, 95)),
            'p99': float(np.percentile(times_arr, 99)),
        },
        'metrics': result.get('metrics', {}),
        'status': result.get('status', 'unknown')
    }


def compare_expressions(expressions: List[str], iterations: int = 100) -> List[dict]:
    """
    Compare multiple AET expressions
    
    Args:
        expressions: List of AET expression strings
        iterations: Iterations per expression
    
    Returns:
        List of profile results
    """
    results = []
    for expr in expressions:
        profile = profile_aet_expression(expr, iterations)
        results.append(profile)
    
    return results


def benchmark_operation_sizes(sizes: List[int], operation: str = "State") -> dict:
    """
    Benchmark operation across different state sizes
    
    Args:
        sizes: List of state dimensions to test
        operation: Operation to benchmark (default: "State")
    
    Returns:
        Benchmark results
    """
    results = []
    
    for size in sizes:
        if operation == "State":
            expr = f"State({size})"
        elif operation == "Transform":
            expr = f"State({size}) @ W{size}"
        elif operation == "Chain":
            expr = f"State({size}) >> ReLU >> LayerNorm"
        else:
            expr = f"State({size})"
        
        profile = profile_aet_expression(expr, iterations=50)
        results.append({
            'size': size,
            'mean_ms': profile['time_ms']['mean'],
            'std_ms': profile['time_ms']['std'],
        })
    
    return results


def auto_select_best(expressions: List[str], 
                     criteria: str = 'time') -> dict:
    """
    Auto-select best expression based on criteria
    
    Args:
        expressions: List of expressions to compare
        criteria: Selection criteria ('time', 'memory', 'operations')
    
    Returns:
        Best expression and comparison results
    """
    profiles = compare_expressions(expressions, iterations=50)
    
    if criteria == 'time':
        sorted_profiles = sorted(profiles, key=lambda p: p['time_ms']['mean'])
    elif criteria == 'memory':
        sorted_profiles = sorted(profiles, key=lambda p: p['metrics'].get('dimension', 0))
    else:
        sorted_profiles = profiles
    
    return {
        'best': sorted_profiles[0] if sorted_profiles else None,
        'all': profiles,
        'ranking': [p['expression'] for p in sorted_profiles]
    }


# ========== Demo ==========
if __name__ == "__main__":
    print("=" * 70)
    print("AET Auto-Profiler - Working Implementation")
    print("=" * 70)
    
    # Test basic expressions
    expressions = [
        "State(512)",
        "State(1024)",
        "State(2048) >> ReLU",
        "State(1024) >> ReLU >> LayerNorm",
    ]
    
    print("\n1. Benchmarking expressions:")
    results = compare_expressions(expressions, iterations=20)
    
    for r in results:
        print(f"\n   Expression: {r['expression']}")
        print(f"   Time: {r['time_ms']['mean']:.3f}ms ± {r['time_ms']['std']:.3f}ms")
        print(f"   P95: {r['time_ms']['p95']:.3f}ms")
        print(f"   Status: {r['status']}")
    
    # Auto-select best
    print("\n2. Auto-select best:")
    best_result = auto_select_best(expressions, criteria='time')
    
    print(f"   Best: {best_result['best']['expression']}")
    print(f"   Time: {best_result['best']['time_ms']['mean']:.3f}ms")
    print(f"   Ranking: {best_result['ranking']}")
    
    # Benchmark different sizes
    print("\n3. Scaling benchmark:")
    sizes = [256, 512, 1024, 2048]
    scale_results = benchmark_operation_sizes(sizes, operation="Chain")
    
    for r in scale_results:
        print(f"   Size {r['size']:4d}: {r['mean_ms']:6.3f}ms ± {r['std_ms']:5.3f}ms")
    
    print("\n" + "=" * 70)
    print("AET Auto-Profiler: WORKING ✓")
    print("=" * 70)