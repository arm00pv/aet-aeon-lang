#!/usr/bin/env python3
"""
AET Model Router with Fallback Protocol (Optimized)
===================================================
Resilient AI system with automatic failover to local models.
"""

import time
import subprocess
import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
from collections import deque

from aetc import check_hardware_safety

class ModelTier(Enum):
    CLOUD_PRIMARY = 1
    CLOUD_SECONDARY = 2
    LOCAL_FALLBACK = 3

@dataclass
class ModelConfig:
    name: str
    tier: ModelTier
    endpoint: Optional[str] = None
    local_path: Optional[str] = None
    mount_point: Optional[str] = None
    warmup_prompt: str = "Ready for computation."
    instructions: List[str] = field(default_factory=list)
    timeout: int = 120
    max_retries: int = 3
    rate_limit_wait: int = 60

@dataclass
class ModelStats:
    total_calls: int = 0
    successful: int = 0
    failed: int = 0
    rate_limited: int = 0
    last_error: Optional[str] = None
    avg_latency: float = 0.0
    latency_history: deque = field(default_factory=lambda: deque(maxlen=100))

@dataclass
class FallbackEvent:
    timestamp: float
    from_model: str
    to_model: str
    reason: str
    recovered: bool = False

class AETModelRouter:
    """
    Intelligent model routing with automatic fallback.
    """
    
    MODELS = {
        "kimi-k2.6:cloud": ModelConfig(
            name="kimi-k2.6:cloud",
            tier=ModelTier.CLOUD_PRIMARY,
            timeout=120,
            instructions=["You are kimi-k2.6, the primary AET generator.", "Generate ONLY AET code."]
        ),
        "qwen3.5:cloud": ModelConfig(
            name="qwen3.5:cloud",
            tier=ModelTier.CLOUD_PRIMARY,
            timeout=120,
            instructions=["You are qwen3.5 cloud edition.", "Generate concise AET code."]
        ),
        "nemotron-3-super:cloud": ModelConfig(
            name="nemotron-3-super:cloud",
            tier=ModelTier.CLOUD_SECONDARY,
            timeout=180,
            instructions=["You are nemotron-3-super, specialized in verification."]
        ),
        "qwen3.5:9b": ModelConfig(
            name="qwen3.5:9b",
            tier=ModelTier.LOCAL_FALLBACK,
            timeout=300,
            warmup_prompt="System ready. Qwen3.5 9B active."
        ),
        "qwen3.5:4b": ModelConfig(
            name="qwen3.5:4b",
            tier=ModelTier.LOCAL_FALLBACK,
            timeout=300,
            warmup_prompt="System ready. Qwen3.5 4B active."
        ),
    }
    
    FALLBACK_CHAIN = [
        ("kimi-k2.6:cloud", "qwen3.5:cloud"),
        ("qwen3.5:cloud", "nemotron-3-super:cloud"),
        ("nemotron-3-super:cloud", "qwen3.5:9b"),
        ("qwen3.5:9b", "qwen3.5:4b"),
        ("qwen3.5:4b", None),
    ]
    
    def __init__(self):
        self.stats: Dict[str, ModelStats] = {
            name: ModelStats() for name in self.MODELS
        }
        self.current_model = "kimi-k2.6:cloud"
        self.fallback_history: List[FallbackEvent] = []
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.local_mounted = False
        
    def check_429_error(self, output: str) -> bool:
        patterns = ["429", "rate limit", "too many requests", "quota exceeded"]
        return any(p.lower() in output.lower() for p in patterns)
    
    def is_local_model(self, model_name: str) -> bool:
        config = self.MODELS.get(model_name)
        return config and config.tier == ModelTier.LOCAL_FALLBACK
    
    def mount_local_model(self, model_name: str) -> bool:
        if self.is_local_model(model_name):
            print(f"Mounting local model {model_name}...")
            self.local_mounted = True
            return True
        return False
        
    def warmup_model(self, model_name: str):
        config = self.MODELS.get(model_name)
        if config:
            print(f"Warming up {model_name}...")
            
    def execute_with_fallback(self, prompt: str, preferred_model: str = None) -> Dict:
        start_time = time.time()
        fallback_count = 0
        model = preferred_model or self.current_model
        
        while True:
            self.stats[model].total_calls += 1
            config = self.MODELS.get(model)
            
            # HG: Check hardware safety before launch
            is_safe = check_hardware_safety()
            env = os.environ.copy()
            if not is_safe:
                env["OLLAMA_NUM_GPU"] = "0" # Force CPU only
            
            try:
                # Actual execution via Ollama
                result = subprocess.run(
                    ["ollama", "run", model, prompt],
                    capture_output=True,
                    text=True,
                    timeout=config.timeout if config else 120,
                    env=env
                )
                
                output = result.stdout
                
                if result.returncode != 0:
                    raise Exception(f"Ollama Error: {result.stderr}")
                
                # Check for 429 (Simulated or via output text)
                if self.check_429_error(output):
                    raise Exception("429 Rate Limit")
                
                latency = time.time() - start_time
                self.stats[model].successful += 1
                return {
                    "output": output,
                    "model_used": model,
                    "fallback_count": fallback_count,
                    "latency": latency,
                    "success": True
                }
            except Exception as e:
                self.stats[model].failed += 1
                fallback = self._get_fallback(model)
                if fallback:
                    print(f"FALLBACK: {model} → {fallback} ({e})")
                    model = fallback
                    fallback_count += 1
                    continue
                else:
                    return {"success": False, "error": str(e), "model_used": model}

    def _get_fallback(self, from_model: str) -> Optional[str]:
        for chain_from, chain_to in self.FALLBACK_CHAIN:
            if chain_from == from_model:
                return chain_to
        return None
    
    def get_status(self) -> Dict:
        return {
            "current_model": self.current_model,
            "local_mounted": self.local_mounted,
            "stats": {name: {"calls": s.total_calls, "success": s.successful} for name, s in self.stats.items()}
        }
