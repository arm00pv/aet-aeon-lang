#!/usr/bin/env python3
"""
AET Model Router with Fallback Protocol
========================================
Resilient AI system with automatic failover to local models.

Priority:
1. kimi-k2.6:cloud (Ollama Cloud) - fast, capable
2. nemotron-3-super:cloud (Verification model)
3. phi4:latest (LOCAL FALLBACK - no external dependencies)

If primary gives 429 (rate limit), automatically switch to local.
"""

import time
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
from collections import deque

class ModelTier(Enum):
    CLOUD_PRIMARY = 1
    CLOUD_SECONDARY = 2
    LOCAL_FALLBACK = 3

@dataclass
class ModelConfig:
    name: str
    tier: ModelTier
    endpoint: Optional[str] = None  # For cloud models
    local_path: Optional[str] = None  # For local models
    mount_point: Optional[str] = None
    warmup_prompt: str = "Ready for computation."
    instructions: List[str] = field(default_factory=list)
    timeout: int = 120
    max_retries: int = 3
    rate_limit_wait: int = 60  # Seconds to wait on 429

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
    
    Features:
    - Automatic 429 detection and fallback
    - Local model warm-up and mount management
    - Latency and success rate tracking
    - Configurable fallback chains
    """
    
    # Model configurations
    MODELS = {
        "kimi-k2.6:cloud": ModelConfig(
            name="kimi-k2.6:cloud",
            tier=ModelTier.CLOUD_PRIMARY,
            timeout=120,
            rate_limit_wait=60,
            instructions=[
                "You are kimi-k2.6, optimized for AET code generation.",
                "Generate concise AET code with State(), @, Attention, ⊗, ⊕ operators.",
                "Focus on mathematical precision in state space definitions.",
            ]
        ),
        "nemotron-3-super:cloud": ModelConfig(
            name="nemotron-3-super:cloud",
            tier=ModelTier.CLOUD_SECONDARY,
            timeout=180,
            instructions=[
                "You are nemotron-3-super, specialized in verification.",
                "Check AET code for: valid syntax, correct state dimensions, operator usage.",
            ]
        ),
        "phi4:latest": ModelConfig(
            name="phi4:latest",
            tier=ModelTier.LOCAL_FALLBACK,
            timeout=300,
            warmup_prompt="System ready. Phi-4 local mode active.",
            instructions=[
                "LOCAL MODE: No external API dependencies.",
                "Generate AET code for mathematical reasoning.",
                "Use State(2048) for general problems, State(4096) for combinatorics.",
                "Remember: You are running locally. No rate limits.",
            ]
        ),
    }
    
    # Fallback chain: if X fails, try Y
    FALLBACK_CHAIN = [
        ("kimi-k2.6:cloud", "phi4:latest"),
        ("nemotron-3-super:cloud", "kimi-k2.6:cloud"),
        ("phi4:latest", None),  # No fallback for local - it's the last resort
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
        """Detect rate limiting errors"""
        patterns = [
            "429", "rate limit", "too many requests",
            " quota exceeded", "limit exceeded",
            "service unavailable", "overloaded"
        ]
        return any(p.lower() in output.lower() for p in patterns)
    
    def is_local_model(self, model_name: str) -> bool:
        """Check if model is local (no external dependencies)"""
        config = self.MODELS.get(model_name)
        return config and config.tier == ModelTier.LOCAL_FALLBACK
    
    def mount_local_model(self, model_name: str) -> bool:
        """
        Mount and prepare local model for use.
        Phi-4 is 9.1GB - needs proper setup.
        """
        if self.is_local_model(model_name):
            # Check if already running
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True
            )
            if model_name in result.stdout:
                self.local_mounted = True
                return True
            
            # Pull if needed (happens once)
            print(f"Mounting local model: {model_name}")
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=600  # 10 min for 9GB
            )
            
            if result.returncode == 0:
                self.local_mounted = True
                return True
        
        return False
    
    def warmup_model(self, model_name: str) -> bool:
        """Send warm-up prompt to ensure model is responsive"""
        config = self.MODELS.get(model_name)
        if not config:
            return False
        
        print(f"Warming up {model_name}...")
        
        # For local models, use ollama run
        if self.is_local_model(model_name):
            result = subprocess.run(
                ["ollama", "run", model_name, config.warmup_prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        
        return True  # Cloud models warm up automatically
    
    def execute_with_fallback(self, prompt: str, preferred_model: str = None) -> Dict:
        """
        Execute prompt with automatic fallback.
        
        Returns:
            {
                "output": str,
                "model_used": str,
                "fallback_count": int,
                "latency": float,
                "success": bool
            }
        """
        start_time = time.time()
        fallback_count = 0
        model = preferred_model or self.current_model
        
        while True:
            # Update stats
            self.stats[model].total_calls += 1
            
            # Check if local model needs mounting
            if self.is_local_model(model) and not self.local_mounted:
                self.mount_local_model(model)
                self.warmup_model(model)
            
            config = self.MODELS.get(model)
            if not config:
                return {
                    "output": "No valid model available",
                    "model_used": model,
                    "fallback_count": fallback_count,
                    "latency": time.time() - start_time,
                    "success": False
                }
            
            # Execute
            try:
                output = self._execute_model(model, prompt, config.timeout)
                
                # Check for errors
                if self.check_429_error(output):
                    self.stats[model].rate_limited += 1
                    print(f"Rate limited on {model}, waiting {config.rate_limit_wait}s...")
                    time.sleep(config.rate_limit_wait)
                    
                    # Find fallback
                    fallback = self._get_fallback(model)
                    if fallback:
                        self._record_fallback(model, fallback, "429 rate limit")
                        model = fallback
                        fallback_count += 1
                        continue
                    else:
                        return {
                            "output": f"Rate limited on all models: {output[:200]}",
                            "model_used": model,
                            "fallback_count": fallback_count,
                            "latency": time.time() - start_time,
                            "success": False
                        }
                
                # Success
                latency = time.time() - start_time
                self.stats[model].successful += 1
                self.stats[model].latency_history.append(latency)
                self.stats[model].avg_latency = sum(self.stats[model].latency_history) / len(self.stats[model].latency_history)
                self.consecutive_failures = 0
                self.current_model = model
                
                return {
                    "output": output,
                    "model_used": model,
                    "fallback_count": fallback_count,
                    "latency": latency,
                    "success": True
                }
                
            except subprocess.TimeoutExpired:
                self.stats[model].failed += 1
                self.stats[model].last_error = "Timeout"
                self.consecutive_failures += 1
                
                fallback = self._get_fallback(model)
                if fallback and self.consecutive_failures < self.max_consecutive_failures:
                    self._record_fallback(model, fallback, "Timeout")
                    model = fallback
                    fallback_count += 1
                    continue
                else:
                    return {
                        "output": f"Timeout on {model}",
                        "model_used": model,
                        "fallback_count": fallback_count,
                        "latency": time.time() - start_time,
                        "success": False
                    }
                    
            except Exception as e:
                self.stats[model].failed += 1
                self.stats[model].last_error = str(e)
                self.consecutive_failures += 1
                
                fallback = self._get_fallback(model)
                if fallback and self.consecutive_failures < self.max_consecutive_failures:
                    self._record_fallback(model, fallback, str(e))
                    model = fallback
                    fallback_count += 1
                    continue
                else:
                    return {
                        "output": f"Error on {model}: {str(e)}",
                        "model_used": model,
                        "fallback_count": fallback_count,
                        "latency": time.time() - start_time,
                        "success": False
                    }
    
    def _execute_model(self, model: str, prompt: str, timeout: int) -> str:
        """Execute model via appropriate method"""
        
        if self.is_local_model(model):
            # Local - use ollama run
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout + result.stderr
            output = re.sub(r'\x1b\[[^m]*m', '', output)  # Clean ANSI
            return output.strip()
        else:
            # Cloud - use ollama run with :cloud model
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout + result.stderr
            output = re.sub(r'\x1b\[[^m]*m', '', output)
            return output.strip()
    
    def _get_fallback(self, from_model: str) -> Optional[str]:
        """Get next fallback model"""
        for chain_from, chain_to in self.FALLBACK_CHAIN:
            if chain_from == from_model:
                return chain_to
        return None
    
    def _record_fallback(self, from_model: str, to_model: str, reason: str):
        """Record fallback event"""
        event = FallbackEvent(
            timestamp=time.time(),
            from_model=from_model,
            to_model=to_model,
            reason=reason
        )
        self.fallback_history.append(event)
        print(f"FALLBACK: {from_model} → {to_model} ({reason})")
    
    def get_status(self) -> Dict:
        """Get router status"""
        return {
            "current_model": self.current_model,
            "local_mounted": self.local_mounted,
            "consecutive_failures": self.consecutive_failures,
            "stats": {
                name: {
                    "calls": s.total_calls,
                    "success": s.successful,
                    "failed": s.failed,
                    "rate_limited": s.rate_limited,
                    "avg_latency": f"{s.avg_latency:.2f}s"
                }
                for name, s in self.stats.items()
            },
            "recent_fallbacks": [
                {
                    "from": e.from_model,
                    "to": e.to_model,
                    "reason": e.reason,
                    "timestamp": e.timestamp
                }
                for e in self.fallback_history[-5:]
            ]
        }

def demo():
    print("AET Model Router with Fallback Protocol")
    print("=" * 60)
    print()
    
    router = AETModelRouter()
    
    # Show configuration
    print("Model Configuration:")
    print("-" * 40)
    for name, config in router.MODELS.items():
        tier_name = config.tier.name.replace("_", " ")
        print(f"  {name}")
        print(f"    Tier: {tier_name}")
        print(f"    Timeout: {config.timeout}s")
        if config.tier == ModelTier.LOCAL_FALLBACK:
            print(f"    Warmup: {config.warmup_prompt}")
        print()
    
    # Show fallback chain
    print("Fallback Chain:")
    print("-" * 40)
    for from_m, to_m in router.FALLBACK_CHAIN:
        print(f"  {from_m} → {to_m or 'NONE'}")
    print()
    
    # Test execution with fallback
    print("Testing execution...")
    test_prompt = "Generate AET code for: State(4096) → reasoning. Use @ and ⊕ operators."
    
    result = router.execute_with_fallback(test_prompt)
    
    print(f"\nResult:")
    print(f"  Success: {result['success']}")
    print(f"  Model: {result['model_used']}")
    print(f"  Fallbacks: {result['fallback_count']}")
    print(f"  Latency: {result['latency']:.2f}s")
    print()
    
    # Show status
    print("Router Status:")
    status = router.get_status()
    print(f"  Current: {status['current_model']}")
    print(f"  Local mounted: {status['local_mounted']}")
    for name, s in status['stats'].items():
        print(f"  {name}: {s['calls']} calls, {s['success']} success, {s['avg_latency']} avg")

if __name__ == "__main__":
    demo()