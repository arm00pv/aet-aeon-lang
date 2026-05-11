#!/usr/bin/env python3
"""
AET Logic-Arbitrage Engine (Stabilized)
======================================
Provides model comparison logic for AET generation.
"""

import time
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add path for AET modules
sys.path.insert(0, str(Path(__file__).parent))

from aet_orchestrator import AETOrchestrator, ExecutionResult
from aet_verification import VerificationHook

class LogicArbitrageur:
    def __init__(self):
        self.orch = AETOrchestrator()
        self.verifier = VerificationHook()

    def mmla_reason(self, task: str, models: List[str] = None) -> ExecutionResult:
        """
        Sequentially queries models to find the most accurate AET logic.
        Sequential execution prevents VRAM overflow and system crashes.
        """
        if models is None:
            models = ["kimi-k2.6:cloud", "qwen3.5:cloud", "qwen3.5:9b"]
        
        print(f"[MMLA] Dispatching task to {len(models)} models sequentially...")
        
        best_result = None
        
        for model in models:
            print(f"  → Querying {model}...")
            res = self.orch.router.execute_with_fallback(task, preferred_model=model)
            if res["success"]:
                v_res = self.verifier.auto_verify(res["output"], f"Arbitrage grading")
                if v_res.is_valid:
                    print(f"  [OK] Model {model} produced valid logic.")
                    return ExecutionResult(
                        success=True,
                        model_used=res["model_used"],
                        fallback_count=res["fallback_count"],
                        latency=res["latency"],
                        output=res["output"],
                        context_used=["mmla_arbitrage", "verified_logic"]
                    )
        
        # If no preferred model works, use standard orchestrator fallback
        return self.orch.generate_aet(task)
