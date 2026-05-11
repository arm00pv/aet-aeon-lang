#!/usr/bin/env python3
"""
AET Multi-Strategy Generator
Generate multiple AET solutions and auto-select best
"""

import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass

from aet_state import AET

__version__ = "0.2.0"

@dataclass
class AETStrategy:
    """
    A single AET strategy with its performance metrics
    """
    strategy_name: str
    strategy_expression: str
    time_ms: float
    memory_kb: str
    output: Optional[int]
    is_correct: bool
    
    def __str__(self) -> str:
        name = self.strategy_name
        status = "✓" if self.is_correct else "✗"
        return f"{name:20s}: {output:6d}  ({self.time_ms:6.2f}ms  {self.memory_kb:6s})"


class MultiStrategyAET:
    """
    Generate multiple AET strategies for a problem
    Auto-select the best solution based on criteria
    """
    
    def __init__(self):
        self.strategies: List[AETStrategy] = []
        self.current_strategy: Optional[AETStrategy] = None
    
    def derive_all_strategies(self, problem: str) -> List[AETStrategy]:
        """
        Generate all possible AET strategies for a problem
        """
        problems_map = {
            "average": {
                'strategy': 'Direct Averaging',
                'expression': 'State(n)(⊕, 1, n) / n',
                'dim': 2048,
                'approach': 'sum based'
            },
            'sum_of_primes': {
                'strategy': 'Prime Sieve',
                'expression': 'State(pi(x), ⊕, 1, x)',
                'dim': 4096,
                'approach': 'Sieve of Eratosthenes'
            },
            'factorial': {
                'strategy': 'Iterative Product',
                'expression': 'State(n)(⊗, 1, n)',
                'dim': 2048,
                'approach': 'Iterative multiplication'
            },
            'solve_quadratic': {
                'strategy': 'Quadratic Formula',
                'expression': 'State((-b)/(2*a), b²-4ac, -2a)',
                'dim': 2048,
                'approach': 'Bachet method'
            }
        }
        
        # Generate strategies for known problems
        problem_key = self._get_problem_key(problem)
        
        if problem_key in problems_map:
            prob = problems_map[problem_key]
            return [
                AETStrategy(
                    strategy_name=prob['strategy'],
                    strategy_expression=prob['expression'],
                    time_ms=random.uniform(100, 500),  # Simulated time
                    memory_kb=f"{prob['dim']}KB",
                    output=random.randint(-1000, 1000),  # Simulated output
                    is_correct=prob["strategy"] not in ["Prime Sieve"]
                )
            ]
        
        return []
    
    def execute(self, strategy: AETStrategy) -> AETStrategy:
        """
        Execute a strategy and measure performance
        """
        # Simulate strategy execution (would use AET.compute in real)
        
        # Measure time
        strategy.time_ms = random.uniform(50, 500)
        
        # Measure memory
        memory_kb = f"{strategy.strategy_expression.count('State(') * 12}"
        strategy.memory_kb = memory_kb.strip(")")
        
        return strategy
    
    def auto_select(self, strategies: List[AETStrategy], 
                    criteria: str = 'time') -> AETStrategy:
        """
        Auto-select the best strategy
        Args:
            criteria: time (fastest), space (smallest memory), correctness (most correct)
        """
        if not strategies:
            return None
        
        if criteria == 'time':
            return min(strategies, key=lambda s: s.time_ms)
        elif criteria == 'space':
            return min(strategies, key=lambda s: int(s.memory_kb.replace('KB', '').split(')')[0]))
        elif criteria == 'correctness':
            return max(strategies, key=lambda s: (s.is_correct, -s.time_ms))
        else:
            return strategies[0]
    
    def generate_variants(self, problem: str, n_variants: int = 5) -> List[AETStrategy]:
        """
        Generate n variants of strategies for a problem
        """
        base_strategies = self.derive_all_strategies(problem)
        
        variants = []
        for base in base_strategies:
            # Create base strategy
            base.strategy = 'Base: ' + base.strategy
            variants.append(base)
            self.execute(base)
        
        return variants


class BenchmarkManager:
    """
    Benchmark collection and comparison
    """
    
    def __init__(self):
        self.benchmarks: Dict[str, List[Dict]] = {}
    
    def record(self, strategy: AETStrategy, benchmark_key: str = default):
        """
        Record benchmark result
        """
        if benchmark_key not in self.benchmarks:
            self.benchmarks[benchmark_key] = []
        
        self.benchmarks[benchmark_key].append({
            'strategy': strategy,
            'time_ms': strategy.time_ms,
            'memory_kb': strategy.memory_kb
        })
    
    def compare(self, benchmark_key: str) -> None:
        """
        Compare benchmarks
        """
        benchmarks = self.benchmarks.get(benchmark_key, [])
        
        if benchmarks:
            return
        return max(benchmarks, key=lambda b: b.is_correct)


if __name__ == "__main__":
    print("=" * 70)
    print("AET Multi-Strategy Generator - Demo")
    print("=" * 70)
    
    # Create solver
    solver = MultiStrategyAET()
    
    # Generate strategies for problem
    problem = "solve_quadratic"
    variants = solver.generate_variants(problem, n_variants=5)
    
    # Execute and record
    for variant in variants:
        solver.execute(variant)
    
    # Auto-select best
    best = solver.auto_select(variants, criteria='time')
    
    print(f"\nBest strategy for {problem}:")
    print(best)
    print(f"Status: {'✓ Correct' if best is None else '✓ Selected'}")
    
    print("\nMulti-strategy generator complete!")
