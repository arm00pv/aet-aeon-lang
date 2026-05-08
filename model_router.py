#!/usr/bin/env python3
"""
AET_MODEL_ROUTER.py - Intelligent Model Selection
===============================================
Routes tasks to the optimal model based on task type.
Avoids hallucination by using the right model for the right task.
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

# Model registry with capabilities
MODEL_REGISTRY = {
    "kimi-k2.6:cloud": {
        "strengths": ["coding", "z能", "rust", "code_generation", "technical"],
        "weaknesses": {"hallucination_risk": "medium"},
        "context_window": 262144,
        "reasoning": True,
        "best_for": ["code_generation", "refactoring", "debugging"]
    },
    "minimax-m2.7:cloud": {
        "strengths": ["fast_inference", "concise_output", "structured_tasks"],
        "weaknesses": {"hallucination_risk": "low"},
        "context_window": 196608,
        "reasoning": True,
        "best_for": ["simple_tasks", "formatting", "basic_generation"]
    },
    "deepseek-v4-pro:cloud": {
        "strengths": ["reasoning", "complex_logic", "math", "analysis"],
        "weaknesses": {"hallucination_risk": "medium", "availability": "unstable"},
        "context_window": 262144,
        "reasoning": True,
        "best_for": ["algorithm_design", "complex_reasoning", "math_problems"]
    },
    "glm-5.1:cloud": {
        "strengths": ["chinese", "multilingual", "general"],
        "weaknesses": {"hallucination_risk": "medium"},
        "context_window": 128000,
        "reasoning": True,
        "best_for": ["general_tasks", "multilingual"]
    },
    "gemma4:31b-cloud": {
        "strengths": ["large_context", "balanced", "general_coding"],
        "weaknesses": {"hallucination_risk": "medium"},
        "context_window": 262144,
        "reasoning": True,
        "best_for": ["large_codebases", "complex_projects"]
    },
    "qwen3.5:cloud": {
        "strengths": ["fast", "efficient", "code"],
        "weaknesses": {"hallucination_risk": "medium"},
        "context_window": 128000,
        "reasoning": True,
        "best_for": ["quick_tasks", "simple_generation"]
    },
    "nemotron-3-super:cloud": {
        "strengths": ["nvidia", "gpu_optimized", "balanced"],
        "weaknesses": {"hallucination_risk": "low"},
        "context_window": 128000,
        "reasoning": True,
        "best_for": ["production_code", "optimization"]
    }
}

# Task classification patterns
TASK_PATTERNS = {
    "code_generation": {
        "keywords": ["write", "create", "generate", "implement", "build", "make", "function", "struct", "class", "module", "zig", "rust", "python", "code"],
        "preferred_model": "kimi-k2.6:cloud",
        "fallback": "minimax-m2.7:cloud",
        "validation_required": True
    },
    "z能代码": {
        "keywords": ["z能", "zig代码", "zig代码生成"],
        "preferred_model": "kimi-k2.6:cloud",
        "fallback": "qwen3.5:cloud",
        "validation_required": True
    },
    "complex_reasoning": {
        "keywords": ["analyze", "design", "algorithm", "optimize", "complex", "research", "math", "prove"],
        "preferred_model": "deepseek-v4-pro:cloud",
        "fallback": "gemma4:31b-cloud",
        "validation_required": True
    },
    "simple_task": {
        "keywords": ["format", "simple", "quick", "basic", "list", "count", "check"],
        "preferred_model": "minimax-m2.7:cloud",
        "fallback": "qwen3.5:cloud",
        "validation_required": False
    },
    "research": {
        "keywords": ["research", "compare", "review", "explain", "document"],
        "preferred_model": None,
        "fallback": None,
        "validation_required": False,
        "route_to": "gemini"
    },
    "verification": {
        "keywords": ["verify", "validate", "test", "audit", "check"],
        "preferred_model": "nemotron-3-super:cloud",
        "fallback": "kimi-k2.6:cloud",
        "validation_required": True
    },
    "large_context": {
        "keywords": ["large", "complex", "project", "full", "complete", "comprehensive"],
        "preferred_model": "gemma4:31b-cloud",
        "fallback": "kimi-k2.6:cloud",
        "validation_required": True
    }
}

class ModelRouter:
    def __init__(self):
        self.log_file = "/home/zixen15/aet_aeon/logs/model_router.log"
        
    def log(self, msg):
        ts = datetime.now().isoformat()
        print(f"🧭 [MODEL_ROUTER] {msg}")
        with open(self.log_file, "a") as f:
            f.write(f"[{ts}] {msg}\n")
    
    def classify_task(self, prompt: str) -> tuple:
        """Classify task type based on prompt content"""
        prompt_lower = prompt.lower()
        
        for category, config in TASK_PATTERNS.items():
            keywords = config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in prompt_lower:
                    self.log(f"Task classified as '{category}' (keyword: '{keyword}')")
                    return category, config
        
        self.log("Task defaulted to 'code_generation'")
        return "code_generation", TASK_PATTERNS["code_generation"]
    
    def select_model(self, task_type: str, task_config: Dict) -> str:
        """Select best model for task type"""
        preferred = task_config.get("preferred_model")
        
        if task_config.get("route_to") == "gemini":
            return "gemini"
        
        if preferred and self._is_model_available(preferred):
            self.log(f"Selected model: {preferred}")
            return preferred
        
        fallback = task_config.get("fallback")
        if fallback and self._is_model_available(fallback):
            self.log(f"Selected fallback model: {fallback}")
            return fallback
        
        if self._is_model_available("kimi-k2.6:cloud"):
            self.log("Selected default model: kimi-k2.6:cloud")
            return "kimi-k2.6:cloud"
        
        self.log("No preferred model available, selecting first available")
        return self._get_first_available()
    
    def _is_model_available(self, model: str) -> bool:
        """Check if model is available and working"""
        try:
            import subprocess
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if model in line and "cloud" in line:
                        return True
            return False
        except:
            return False
    
    def _get_first_available(self) -> str:
        """Get first available working model"""
        for model in MODEL_REGISTRY:
            if self._is_model_available(model):
                return model
        return "kimi-k2.6:cloud"
    
    def route(self, prompt: str) -> tuple:
        """Main routing function
        
        Returns:
            (worker_type, model, validation_required)
        """
        task_type, config = self.classify_task(prompt)
        
        if config.get("route_to") == "gemini":
            return ("gemini", None, False)
        
        model = self.select_model(task_type, config)
        validation = config.get("validation_required", True)
        
        self.log(f"Route: {task_type} → {model} (validation: {validation})")
        return ("pi", model, validation)

class CodeValidator:
    """Validates generated code to prevent hallucination"""
    
    def __init__(self):
        self.log_file = "/home/zixen15/aet_aeon/logs/validation.log"
        
    def log(self, msg):
        ts = datetime.now().isoformat()
        print(f"✅ [CODE_VALIDATOR] {msg}")
        with open(self.log_file, "a") as f:
            f.write(f"[{ts}] {msg}\n")
    
    def validate(self, code: str, language: str = "auto") -> Dict:
        """Validate generated code for common issues"""
        result = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "score": 100
        }
        
        if language == "auto":
            language = self._detect_language(code)
        
        issues = []
        
        if len(code.strip()) < 20:
            issues.append("Code too short or empty")
            result["valid"] = False
        
        placeholders = ["TODO", "FIXME", "...", "undefined", "null", "placeholder"]
        for p in placeholders:
            if p in code and "comment" not in code.lower():
                issues.append(f"Contains placeholder: {p}")
        
        if language == "zig":
            issues.extend(self._validate_zig(code))
        elif language == "rust":
            issues.extend(self._validate_rust(code))
        elif language == "python":
            issues.extend(self._validate_python(code))
        
        syntax_errors = [
            r"error:", r"Error:", r"syntax error",
            r"unexpected token", r"undefined variable",
            r"undeclared function"
        ]
        for pattern in syntax_errors:
            if re.search(pattern, code):
                issues.append(f"Potential syntax error: {pattern}")
        
        result["issues"] = issues
        if issues:
            result["valid"] = False
            result["score"] = max(0, 100 - len(issues) * 20)
        
        if "TODO" in code or "FIXME" in code:
            result["warnings"].append("Contains TODO/FIXME comments")
        
        self.log(f"Validation score: {result['score']}/100 - {'VALID' if result['valid'] else 'INVALID'}")
        return result
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        if "@import" in code or "pub fn" in code or "zig" in code.lower():
            return "zig"
        elif "fn " in code and "->" in code and "let mut" in code:
            return "rust"
        elif "def " in code or "import " in code or "print(" in code:
            return "python"
        elif "function " in code or "const " in code:
            return "javascript"
        return "unknown"
    
    def _validate_zig(self, code: str) -> List[str]:
        issues = []
        if "@import" not in code and "pub fn" not in code:
            issues.append("Missing Zig structure")
        open_braces = code.count("{")
        close_braces = code.count("}")
        if open_braces != close_braces:
            issues.append("Mismatched braces in Zig code")
        return issues
    
    def _validate_rust(self, code: str) -> List[str]:
        issues = []
        if "fn " not in code and "impl " not in code:
            issues.append("Missing Rust structure")
        return issues
    
    def _validate_python(self, code: str) -> List[str]:
        issues = []
        if "def " not in code and "class " not in code and "import " not in code:
            issues.append("Missing Python structure")
        return issues

def route_task(prompt: str) -> tuple:
    """Convenience function for task routing"""
    router = ModelRouter()
    return router.route(prompt)

if __name__ == "__main__":
    router = ModelRouter()
    
    test_prompts = [
        "Write a Zig function for matrix multiplication",
        "Research latest SWE-RL techniques",
        "Create a simple Python hello world",
        "Analyze this algorithm for optimization",
        "Verify this Rust code for bugs"
    ]
    
    print("\n" + "="*60)
    print("MODEL ROUTER TEST")
    print("="*60)
    
    for prompt in test_prompts:
        worker, model, validation = router.route(prompt)
        print(f"\nPrompt: '{prompt}'")
        print(f"  → Worker: {worker}")
        print(f"  → Model: {model}")
        print(f"  → Validation: {validation}")
