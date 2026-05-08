# AET & AEON Implementation Guide

## 🎯 Overview

This guide covers implementing AET/AEON for your AI architecture.

## 📋 Prerequisites

- Python 3.10+
- NumPy for vector operations
- Ollama (for cloud model integration)
- Gemini CLI (for research/verification)

## 🏗️ Architecture Layers

```
Layer 1: Parser     → AET source → AST
Layer 2: Analyzer   → AST → Validated AST
Layer 3: Compiler   → AST → AET IR (Intermediate Representation)
Layer 4: Runtime   → AET IR → Execution
Layer 5: Transpiler → AET IR → Target Language
```

## 🔧 Implementation Steps

### Step 1: AET Parser

```python
class AETParser:
    def parse(self, source: str) -> AST:
        # Tokenize
        tokens = self.tokenize(source)
        # Build AST
        return self.build_ast(tokens)
```

### Step 2: State Space Types

```python
class VectorSpace:
    def __init__(self, dimensions: int):
        self.data = np.ndarray(dimensions)
        
class WaveSpace:
    def __init__(self, spectrum: str):
        self.data = np.ndarray(1024, dtype=complex)
```

### Step 3: Operations

```python
class Operations:
    @staticmethod
    def linear_transform(a, b):  # @ operator
        return np.dot(a, b)
    
    @staticmethod
    def compose(a, b):  # >> operator
        return lambda x: b(a(x))
```

### Step 4: AEON Transpiler

```python
class AEONTranspiler:
    targets = ["python", "rust", "zig", "cuda"]
    
    def transpile(self, ast, target: str) -> str:
        if target == "zig":
            return self.to_zig(ast)
        # ... etc
```

## 📊 Model Integration

### Ollama Cloud Models

| Model | Capabilities |
|-------|--------------|
| kimi-k2.6:cloud | Code generation, refactoring |
| deepseek-v4-pro:cloud | Complex reasoning, algorithms |
| minimax-m2.7:cloud | Simple tasks, fast inference |

### Routing Logic

```python
def route_task(prompt: str) -> str:
    if "write" in prompt or "generate" in prompt:
        return "kimi-k2.6:cloud"
    elif "analyze" in prompt or "design" in prompt:
        return "deepseek-v4-pro:cloud"
    else:
        return "minimax-m2.7:cloud"
```

## ✅ Validation

### Hallucination Prevention

1. **Syntax Validation**: Check for error patterns
2. **Semantic Validation**: Verify type constraints
3. **Output Validation**: Score generated code
4. **Retry Logic**: Switch models on failure

```python
def validate(code: str) -> bool:
    if "error:" in code:
        return False
    if "TODO" in code:
        return False  # Incomplete code
    return True
```

## 🚀 Running AET

```bash
# Interpret AET code
python src/aet_interpreter.py

# Transpile to Zig
python aeon_transpiler.py --input examples/hello_world.aet --output zig

# Run with orchestrator
python orchestrator.py project "Build QSS wave processor"
```

## 📈 Performance

| Operation | Complexity |
|-----------|-----------|
| Linear Transform (@) | O(n²) |
| Composition (>>) | O(n) |
| Attention | O(n·d) |
| Wave Propagation | O(n·log(n)) |

## 🎓 Next Steps

1. Read `SPECIFICATION.md`
2. Study `FORMAL_SPECIFICATION.md`
3. Run examples in `examples/`
4. Implement for your AI architecture
5. Contribute back to the project
