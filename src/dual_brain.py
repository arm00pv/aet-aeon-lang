#!/usr/bin/env python3
"""
AET Dual-Brain System
=====================
Working AI system with:
- Ollama Cloud: Code generation, AET compilation
- Gemini: Research, verification, documentation

Both AIs working together to generate and verify AET code.
"""

import subprocess
import json
import time
import re
from datetime import datetime
from pathlib import Path

# Model assignments
MODELS = {
    "code_gen": "qwen3.5:9b",
    "research": "gemini",
    "verify": "nemotron-3-super:cloud",
}

class OllamaCloud:
    """Ollama Cloud worker - uses local ollama with cloud models"""
    
    def __init__(self, model="qwen3.5:9b"):
        self.model = model
        self.name = "OllamaCloud"
    
    def generate(self, prompt: str, timeout: int = 180) -> str:
        """Generate using ollama with cloud model"""
        try:
            # Use ollama CLI - works locally with cloud models
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                # Clean ANSI codes
                output = re.sub(r'\x1b\[[^m]*m', '', result.stdout)
                output = re.sub(r'\[K\?25h', '', output)
                output = re.sub(r'\[2K\[1G', '', output)
                return output.strip()
            else:
                return f"Error: {result.stderr[:200]}"
        except subprocess.TimeoutExpired:
            return "TIMEOUT"
        except Exception as e:
            return f"Error: {str(e)}"

class GeminiWorker:
    """Gemini CLI worker"""
    
    def __init__(self):
        self.name = "Gemini"
    
    def generate(self, prompt: str, timeout: int = 60) -> str:
        """Generate using Gemini CLI"""
        try:
            env = {"NO_COLOR": "1", "PATH": "/usr/local/bin:/usr/bin:/bin"}
            result = subprocess.run(
                ["gemini", "-p", prompt, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    return data.get("text", result.stdout[:2000])
                except:
                    return result.stdout[:2000]
            else:
                return f"Error: {result.stderr[:200]}"
        except subprocess.TimeoutExpired:
            return "TIMEOUT"
        except Exception as e:
            return f"Error: {str(e)}"

class DualBrain:
    """
    Dual-brain AI system where two AIs work together.
    Ollama Cloud generates AET code.
    Gemini verifies and improves it.
    """
    
    def __init__(self):
        self.ollama = OllamaCloud("qwen3.5:9b")
        self.gemini = GeminiWorker()
        self.history = []
    
    def generate_aet(self, task: str) -> dict:
        """Generate AET code using both brains"""
        
        # Phase 1: Ollama Cloud generates initial AET
        prompt = f"""Generate AET (Artificial Extension of Thought) code for this task:

Task: {task}

AET primitives:
- State(dimensions): Vector state space
- @: Linear transform (matrix multiply)
- >>: Morphism composition  
- ⊗: Superposition (parallel states)
- ⊕: Entropy gate (selection)
- Attention(query, memory): Attention mechanism

Generate ONLY the AET code, no explanation. Use State() >> @ >> Attention pattern.
"""
        initial_code = self.ollama.generate(prompt)
        
        # Phase 2: Gemini verifies and improves
        verify_prompt = f"""Review this AET code for correctness:

{initial_code[:500]}

Check for:
1. Valid AET syntax
2. Proper state dimensions
3. Correct operator usage

Return JSON: {{"valid": true/false, "fixed_code": "...", "issues": []}}
"""
        verification = self.gemini.generate(verify_prompt)
        
        # Try to parse verification
        try:
            if "{" in verification:
                start = verification.index("{")
                end = verification.rindex("}") + 1
                v_data = json.loads(verification[start:end])
                final_code = v_data.get("fixed_code", initial_code)
            else:
                final_code = initial_code
        except:
            final_code = initial_code
        
        result = {
            "task": task,
            "initial_code": initial_code[:1000],
            "verification": verification[:500],
            "final_code": final_code[:1000],
            "ollama_model": self.ollama.model,
            "gemini_status": "completed"
        }
        
        self.history.append(result)
        return result
    
    def execute_aet(self, aet_code: str) -> dict:
        """Execute AET code using aetc compiler"""
        tmp_file = Path("/tmp/aet_task.aet")
        tmp_file.write_text(aet_code)
        
        compiler_path = "/home/zixen15/aet-aeon-lang/src/aetc.py"
        result = subprocess.run(
            ["python3", compiler_path, str(tmp_file), "--build"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            binary = Path("/tmp/aet_compile/main")
            if binary.exists():
                exec_result = subprocess.run([str(binary)], capture_output=True)
                return {
                    "compiled": True,
                    "executed": True,
                    "exit_code": exec_result.returncode,
                    "binary": str(binary)
                }
        
        return {
            "compiled": False,
            "error": result.stderr[:500]
        }

def demo():
    print("AET Dual-Brain System")
    print("=" * 50)
    print()
    
    brain = DualBrain()
    
    task = "Create a state space for reasoning with 4096 dimensions"
    print(f"Task: {task}")
    print()
    
    print("Phase 1: Ollama Cloud generating AET...")
    result = brain.generate_aet(task)
    print(f"  Generated: {result['initial_code'][:150]}...")
    print()
    
    print("Phase 2: Compiling and executing...")
    exec_result = brain.execute_aet(result['final_code'])
    print(f"  Compiled: {exec_result.get('compiled', False)}")
    print(f"  Executed: {exec_result.get('executed', False)}")
    print(f"  Exit: {exec_result.get('exit_code', 'N/A')}")
    print()
    
    print("=" * 50)
    print("Dual-brain complete")

if __name__ == "__main__":
    demo()