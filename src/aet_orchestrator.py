#!/usr/bin/env python3
"""
AET-Orchestrator - Complete Resilient AI System
================================================
Combines:
- Model Router with automatic fallback (cloud → local)
- RAG 2.0 for context injection
- AET code generation and execution
- MathNet integration

The AI worker that never fails.
"""

import time
import json
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import deque

# Import our modules
from model_router_fallback import AETModelRouter, ModelTier
from aet_rag import AETRAG, inject_context

@dataclass
class ExecutionResult:
    success: bool
    model_used: str
    fallback_count: int
    latency: float
    output: str
    context_used: List[str]

class AETOrchestrator:
    """
    Complete AET orchestration system.
    
    Features:
    - Resilient model execution (automatic fallback)
    - RAG-based context injection
    - AET code generation → compilation → execution
    - MathNet problem solving
    """
    
    def __init__(self):
        self.router = AETModelRouter()
        self.rag = AETRAG()
        self.execution_history: List[ExecutionResult] = []
        self._initialized = False
    
    def initialize(self):
        """Initialize all components"""
        if self._initialized:
            return
        
        print("Initializing AET-Orchestrator...")
        self.rag.initialize()
        
        # Pre-warm the fallback model (phi4:latest)
        print("Warming up fallback model: phi4:latest...")
        self.router.mount_local_model("phi4:latest")
        self.router.warmup_model("phi4:latest")
        
        self._initialized = True
        print("Orchestrator ready")
    
    def generate_aet(self, task: str, use_rag: bool = True) -> ExecutionResult:
        """
        Generate AET code for given task.
        
        Uses RAG to inject relevant context.
        Falls back through model chain on failure.
        """
        if not self._initialized:
            self.initialize()
        
        start_time = time.time()
        
        # Build prompt with RAG context
        base_prompt = f"""Generate AET (Artificial Extension of Thought) code for:

{task}

AET primitives:
- State(dimensions): Vector state space
- @: Linear transform (matrix multiply)
- >>: Morphism composition
- ⊗: Superposition (parallel paths)
- ⊕: Entropy gate (selection)
- Attention(query, memory): Attention mechanism
- WaveState(size): Wave function representation

Generate ONLY the AET code, no explanation."""

        # Inject RAG context if enabled
        if use_rag:
            base_prompt = inject_context(self.rag, task, base_prompt)
        
        # Execute with fallback
        result = self.router.execute_with_fallback(base_prompt)
        
        # Clean output
        output = self._clean_output(result["output"])
        
        # Build execution result
        exec_result = ExecutionResult(
            success=result["success"],
            model_used=result["model_used"],
            fallback_count=result["fallback_count"],
            latency=result["latency"],
            output=output,
            context_used=[f"model:{result['model_used']}"]
        )
        
        self.execution_history.append(exec_result)
        return exec_result
    
    def compile_and_execute(self, aet_code: str) -> Dict:
        """Compile AET to binary and execute"""
        # Write to temp file
        tmp_file = Path("/tmp/aet_execute.aet")
        tmp_file.write_text(aet_code)
        
        # Use aetc compiler
        compiler = "/home/zixen15/aet-aeon-lang/src/aetc.py"
        result = subprocess.run(
            ["python3", compiler, str(tmp_file), "--build"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            return {
                "compiled": False,
                "error": result.stderr[:500],
                "output": ""
            }
        
        # Execute binary
        binary = Path("/tmp/aet_compile/main")
        if binary.exists():
            exec_result = subprocess.run([str(binary)], capture_output=True)
            return {
                "compiled": True,
                "executed": True,
                "exit_code": exec_result.returncode,
                "output": ""
            }
        
        return {
            "compiled": True,
            "executed": False,
            "error": "Binary not found",
            "output": ""
        }
    
    def solve_mathnet(self, problem_id: str = None) -> Dict:
        """Solve a MathNet problem"""
        from aet_math_trainer import classify_topic
        
        # Load random problem
        problems = []
        with open("/home/zixen15/hdd_data/AETHELOS_LAB/mathnet_all.jsonl") as f:
            for i, line in enumerate(f):
                if i >= 100: break
                problems.append(json.loads(line))
        
        problem = problems[0] if not problem_id else next(
            (p for p in problems if p['id'] == problem_id), problems[0]
        )
        
        topic = classify_topic(problem)
        
        # Generate AET for this problem
        task = f"Solve this {topic} problem: {problem['problem_markdown'][:300]}..."
        
        print(f"Problem: {problem['id']}")
        print(f"Topic: {topic}")
        print(f"Generating AET...")
        
        result = self.generate_aet(task)
        
        return {
            "problem_id": problem['id'],
            "topic": topic,
            "generation_result": result,
            "aet_code": result.output
        }
    
    def _clean_output(self, output: str) -> str:
        """Clean model output"""
        # Remove thinking indicators
        output = re.sub(r'Thinking\.\.\..*?\n', '', output)
        output = re.sub(r'\.\.\.done thinking\.\n', '', output)
        
        # Remove ANSI codes
        output = re.sub(r'\x1b\[[^m]*m', '', output)
        
        # Remove leading/trailing whitespace
        output = output.strip()
        
        return output
    
    def get_system_status(self) -> Dict:
        """Get complete system status"""
        router_status = self.router.get_status()
        
        return {
            "initialized": self._initialized,
            "router": router_status,
            "rag_chunks": len(self.rag.chunks),
            "rag_tools": len(self.rag.tools),
            "execution_history_count": len(self.execution_history),
            "recent_results": [
                {
                    "success": r.success,
                    "model": r.model_used,
                    "latency": f"{r.latency:.2f}s",
                    "fallbacks": r.fallback_count
                }
                for r in self.execution_history[-5:]
            ]
        }

def demo():
    print("AET-Orchestrator - Complete Resilient AI System")
    print("=" * 60)
    print()
    
    orchestrator = AETOrchestrator()
    orchestrator.initialize()
    
    print("\n" + "=" * 60)
    print("System Status:")
    print("-" * 60)
    
    status = orchestrator.get_system_status()
    print(f"Initialized: {status['initialized']}")
    print(f"RAG Chunks: {status['rag_chunks']}")
    print(f"RAG Tools: {status['rag_tools']}")
    print()
    print(f"Current model: {status['router']['current_model']}")
    print(f"Local mounted: {status['router']['local_mounted']}")
    print()
    
    print("Model Statistics:")
    for name, stats in status['router']['stats'].items():
        print(f"  {name}: {stats['calls']} calls, {stats['success']} success, {stats['avg_latency']}")
    
    print()
    print("=" * 60)
    print("Testing AET generation with RAG context injection...")
    print("-" * 60)
    
    task = "Create AET code for a geometry problem with State and Attention"
    result = orchestrator.generate_aet(task, use_rag=True)
    
    print(f"\nResult:")
    print(f"  Success: {result.success}")
    print(f"  Model: {result.model_used}")
    print(f"  Fallbacks: {result.fallback_count}")
    print(f"  Latency: {result.latency:.2f}s")
    print(f"\nGenerated AET (first 300 chars):")
    print(f"  {result.output[:300]}...")
    
    print()
    print("=" * 60)
    print("Testing MathNet problem solving...")
    print("-" * 60)
    
    math_result = orchestrator.solve_mathnet()
    print(f"Problem: {math_result['problem_id']}")
    print(f"Topic: {math_result['topic']}")
    print(f"Success: {math_result['generation_result'].success}")
    print(f"Model: {math_result['generation_result'].model_used}")

if __name__ == "__main__":
    demo()