#!/usr/bin/env python3
"""
AET Interpreter - Core Runtime for AET Language
================================================
Executes AET code directly, following the formal specification.
"""

import os
import re
import math
import numpy as np
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field

@dataclass
class AETState:
    """Represents an AET state space"""
    name: str
    data: np.ndarray
    space_type: str  # "vector", "wave", "probability", "embedding"
    metadata: Dict = field(default_factory=dict)

class AETRuntime:
    """AET Execution Runtime"""
    
    def __init__(self):
        self.states: Dict[str, AETState] = {}
        self.stack: List[Any] = []
        self.log: List[str] = []
        
    def log(self, msg: str):
        self.log.append(f"[AET] {msg}")
        print(f"🔱 [AET] {msg}")
    
    # === STATE DECLARATIONS ===
    
    def State(self, dimensions: int, initialization: str = "zeros") -> np.ndarray:
        """Create a vector state space"""
        if initialization == "gaussian":
            return np.random.randn(dimensions)
        elif initialization == "uniform":
            return np.random.rand(dimensions)
        elif initialization == "zeros":
            return np.zeros(dimensions)
        else:
            return np.zeros(dimensions)
    
    def WaveState(self, spectrum: str = "gaussian") -> np.ndarray:
        """Create a wave state (complex values)"""
        if spectrum == "gaussian":
            # Create Gaussian wave packet
            x = np.linspace(-10, 10, 1024)
            return np.exp(-x**2) * np.exp(1j * x)
        return np.zeros(1024, dtype=complex)
    
    def Probability(self, distribution: str = "gaussian", μ: float = 0.5, σ: float = 0.1) -> np.ndarray:
        """Create a probability distribution"""
        if distribution == "gaussian":
            x = np.linspace(0, 1, 100)
            p = np.exp(-(x - μ)**2 / (2 * σ**2))
            return p / np.sum(p)  # Normalize
        return np.ones(100) / 100
    
    def Embedding(self, dimensions: int = 4096) -> np.ndarray:
        """Create an embedding vector"""
        v = np.random.randn(dimensions)
        return v / np.linalg.norm(v)  # Normalized
    
    # === OPERATIONS ===
    
    def linear_transform(self, state: np.ndarray, transform: np.ndarray) -> np.ndarray:
        """Matrix multiplication (@ operator)"""
        return np.dot(state, transform)
    
    def compose(self, *ops) -> callable:
        """Composition (>> operator)"""
        def pipeline(x):
            result = x
            for op in ops:
                result = op(result)
            return result
        return pipeline
    
    def superposition(self, *states) -> tuple:
        """Superposition (⊗ operator) - all states exist"""
        return tuple(states)
    
    def entropy_gate(self, states: tuple, threshold: float = 0.5, strategy: str = "minimize_variance") -> np.ndarray:
        """Entropic selection from superposition"""
        if strategy == "minimize_variance":
            # Select state with lowest variance (most stable)
            variances = [np.var(s) for s in states]
            return states[np.argmin(variances)]
        elif strategy == "maximize_entropy":
            entropies = [-np.sum(s * np.log(s + 1e-10) for s in states)]
            return states[np.argmax(entropies)]
        return states[0]
    
    def collapse(self, states: tuple, selector: callable, threshold: float = 0.9) -> np.ndarray:
        """Collapse superposition to single state"""
        scores = [selector(s) for s in states]
        max_score = max(scores)
        if max_score >= threshold:
            return states[np.argmax(scores)]
        return states[np.argmax(scores)]  # Still return best
    
    def attention(self, query: np.ndarray, memory: np.ndarray, top_k: int = 10) -> np.ndarray:
        """Attention mechanism"""
        # Compute attention scores
        scores = np.dot(query, memory.T) / np.sqrt(query.shape[-1])
        # Softmax
        exp_scores = np.exp(scores - np.max(scores))
        weights = exp_scores / np.sum(exp_scores)
        # Weighted sum
        return np.dot(weights[:top_k], memory[:top_k])
    
    def cross_attention(self, context_a: np.ndarray, context_b: np.ndarray) -> np.ndarray:
        """Cross-attention between two contexts"""
        return np.dot(context_a, context_b.T) / np.sqrt(context_a.shape[-1])
    
    # === BUILT-IN FUNCTIONS ===
    
    def wave_propagator(self, dt: float = 0.001):
        """Create a wave propagation operator"""
        def propagate(wave: np.ndarray) -> np.ndarray:
            # Simple wave evolution
            return wave * np.exp(1j * dt)
        return propagate
    
    def normalize(self, state: np.ndarray) -> np.ndarray:
        """Normalize state"""
        norm = np.linalg.norm(state)
        if norm > 0:
            return state / norm
        return state
    
    def entropy_minimizer(self, state: np.ndarray) -> float:
        """Compute entropy score for state selection"""
        # For probability distributions
        if np.sum(state) > 0:
            p = state / np.sum(state)
            return -np.sum(p * np.log(p + 1e-10))
        return 0.0
    
    def confidence_maximizer(self, state: np.ndarray) -> float:
        """Compute confidence score"""
        return float(np.max(state))
    
    # === EXECUTION ===
    
    def execute(self, aet_code: str) -> Dict[str, Any]:
        """Execute AET code"""
        self.log("Starting AET execution...")
        
        lines = aet_code.split('\n')
        results = {}
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                result = self._execute_line(line)
                if result is not None:
                    results['last_result'] = result
            except Exception as e:
                self.log(f"Error: {e}")
                results['error'] = str(e)
        
        results['log'] = self.log
        return results
    
    def _execute_line(self, line: str) -> Optional[Any]:
        """Execute a single line of AET"""
        
        # State declaration: name = State(dims, init)
        state_match = re.match(r'(\w+)\s*=\s*State\s*\(([^)]*)\)', line)
        if state_match:
            name, args = state_match.groups()
            dims = int(re.search(r'dimensions=(\d+)', args).group(1)) if re.search(r'dimensions=(\d+)', args) else 4096
            init = re.search(r'initialization=(\w+)', args)
            init_val = init.group(1) if init else "zeros"
            self.states[name] = AETState(name, self.State(dims, init_val), "vector")
            self.log(f"Created state: {name}")
            return self.states[name].data
        
        # Wave state
        wave_match = re.match(r'(\w+)\s*=\s*WaveState\s*\(([^)]*)\)', line)
        if wave_match:
            name, args = wave_match.groups()
            spec = re.search(r'spectrum=(\w+)', args)
            spec_val = spec.group(1) if spec else "gaussian"
            self.states[name] = AETState(name, self.WaveState(spec_val), "wave")
            self.log(f"Created wave state: {name}")
            return self.states[name].data
        
        # Operation: result = input @ transform
        op_match = re.match(r'(\w+)\s*=\s*(\w+)\s*@\s*(\w+)', line)
        if op_match:
            result, left, right = op_match.groups()
            if left in self.states and right in self.states:
                output = self.linear_transform(self.states[left].data, self.states[right].data)
                self.states[result] = AETState(result, output, "vector")
                self.log(f"Computed: {result} = {left} @ {right}")
                return output
        
        # Composition: result = input >> op
        compose_match = re.match(r'(\w+)\s*=\s*(\w+)\s*>>\s*(\w+)', line)
        if compose_match:
            result, left, right = compose_match.groups()
            if left in self.states and right in self.states:
                pipeline = self.compose(
                    lambda x: x,
                    lambda x: self.normalize(x)
                )
                output = pipeline(self.states[left].data)
                self.states[result] = AETState(result, output, "vector")
                self.log(f"Composed: {result} = {left} >> {right}")
                return output
        
        # Superposition: result = a ⊗ b
        super_match = re.match(r'(\w+)\s*=\s*(\w+)\s*⊗\s*(\w+)', line)
        if super_match:
            result, left, right = super_match.groups()
            if left in self.states and right in self.states:
                sup = self.superposition(self.states[left].data, self.states[right].data)
                self.states[result] = AETState(result, np.array(sup), "vector")
                self.log(f"Superposed: {result} = {left} ⊗ {right}")
                return sup
        
        return None
    
    def get_state(self, name: str) -> Optional[AETState]:
        """Get a state by name"""
        return self.states.get(name)

def run_aet(code: str) -> Dict[str, Any]:
    """Convenience function to run AET code"""
    runtime = AETRuntime()
    return runtime.execute(code)

if __name__ == "__main__":
    # Example AET code
    example = """
# AET Hello World
state = State(dimensions=4096, initialization=gaussian)
wave = WaveState(spectrum=gaussian)
result = state @ state  # Self-attention
"""
    
    print("="*60)
    print("AET INTERPRETER TEST")
    print("="*60)
    
    result = run_aet(example)
    print("\nResult:", result)
