# AI BOOTSTRAP: How to Continue This Project

> **If you are an AI reading this file, you now have everything you need to continue the work.**

## 🎯 What This Project Is

**AET (Artificial Extension of Thought)** - An AI-native programming language for AI-to-AI computation.

**AEON** - The communication protocol for AIs to exchange AET code.

**MathNet Training** - 27,817 mathematical competition problems for training AET reasoning.

## 🔗 Repository Location

```
https://github.com/arm00pv/aet-aeon-lang
```

Clone with:
```bash
git clone https://github.com/arm00pv/aet-aeon-lang.git
cd aet-aeon-lang
```

## 📁 Project Structure

```
aet-aeon-lang/
├── src/
│   ├── aet_reasoner.py          # Natural language → AET code
│   ├── aetc.py                  # AET Compiler (AET → Zig → Binary)
│   ├── aet_runtime.zig          # Native AET runtime (Zig)
│   ├── dual_brain.py            # Ollama + Gemini coordination
│   ├── model_router_fallback.py # Intelligent routing with fallback
│   ├── aet_rag.py               # RAG 2.0 context system
│   ├── aet_orchestrator.py      # Complete orchestration
│   ├── aet_math_trainer.py      # MathNet training system
│   └── aeon/
│       └── protocol.py          # AI-to-AI communication
├── training/
│   └── mathnet/                 # 100 AET-formatted MathNet problems
├── examples/
│   └── hello_world.aet          # Simple AET example
├── SPECIFICATION.md             # AET language specification
├── FORMAL_SPECIFICATION.md      # Mathematical foundations
└── README.md                    # This file
```

## 🚀 Quick Start for Any AI

### 1. Understand AET Primitives (Verified)

The system now supports **real mathematical execution** for:
- `State(dimensions) → name`: Initialize vector space.
- `@`: Real matrix-vector multiplication logic.
- `>>`: Morphism composition (e.g., `>> LayerNorm >> ReLU`).
- `⊗`: Superposition path generation.
- `⊕`: Entropy-based collapse (variance minimization).
- `Attention(query, memory)`: Scaled dot-product stub.
- `WaveState(size)`: Gaussian packet initialization.

### 2. Generate AET Code

From Python:
```python
from src.aet_reasoner import solve_with_aet
result = solve_with_aet("Create state space for reasoning with 4096 dimensions")
print(result['aet_code'])
```

Or via CLI:
```bash
python3 aet_system.py solve "How many ways to arrange 5 items?"
```

### 3. Compile and Execute

```bash
# AET → Zig → Native Binary
python3 src/aetc.py examples/hello_world.aet --build

# Run the binary
/tmp/aet_compile/main
# Exit: 0
```

### 4. AI-to-AI Communication (AEON)

```python
from src.aeon.protocol import create_message, parse_message

# Create AEON message
msg = create_message("task_001", "high", "State(4096) → query", ["kimi-k2.6:cloud"])

# Parse received message
parsed = parse_message(msg)
print(f"Task: {parsed.task_id}, AET: {parsed.aet_payload}")
```

## 🤖 Model System

### Available Models

| Model | Type | Use Case | Fallback |
|-------|------|----------|----------|
| `kimi-k2.6:cloud` | Cloud | Primary code generation | → phi4:latest |
| `nemotron-3-super:cloud` | Cloud | Verification | → kimi-k2.6:cloud |
| `phi4:latest` | Local | Fallback (no rate limits) | Last resort |

### Automatic Fallback

If `kimi-k2.6:cloud` gives 429 or timeout, the system automatically falls back to `phi4:latest` (local, 9.1GB).

```python
from src.model_router_fallback import AETModelRouter

router = AETModelRouter()
result = router.execute_with_fallback("Generate AET code for...")
# Automatic fallback if primary fails
print(f"Model used: {result['model_used']}")
```

## 📊 MathNet Integration

MathNet contains 27,817 mathematical competition problems.

```python
from src.aet_math_trainer import classify_topic

# Load problems
import json
with open("/home/zixen15/hdd_data/AETHELOS_LAB/mathnet_all.jsonl") as f:
    problem = json.loads(f.readline())
    
print(f"Topic: {classify_topic(problem)}")
print(f"Problem: {problem['problem_markdown'][:200]}")
```

Topic → AET State Mapping:
- Geometry: State(2048), WaveState(1024), attention_heads=8
- Discrete Mathematics: State(4096), WaveState(2048), paths=8
- Algebra: State(1024), WaveState(512), attention_heads=4
- Number Theory: State(512), WaveState(256), attention_heads=2

## 🔍 RAG Context System

The RAG contains indexed documentation for AI context injection.

```python
from src.aet_rag import AETRAG, inject_context

rag = AETRAG()
rag.initialize()  # Indexes 20 chunks + 5 tools

# Get relevant context for a query
context = rag.get_context("How to use EntropyGate?", top_k=3)
print(context)

# Inject into prompt
enhanced_prompt = inject_context(rag, "Use EntropyGate for selection", 
                                  "Generate AET code...")
```

## 🛠️ Common Tasks

### Generate AET for Math Problem
```python
from src.dual_brain import DualBrain

brain = DualBrain()
result = brain.generate_aet("Create AET for counting 5 items")
print(result['final_code'])
```

### Train on MathNet
```python
from src.aet_math_trainer import AETMathTrainer

trainer = AETMathTrainer()
results = trainer.train_batch(count=10)
print(f"Success: {results['success_rate']}")
```

### Run Complete Orchestrator
```bash
python3 src/aet_orchestrator.py
```

## 📚 Key Files for AI Reference

| File | Purpose |
|------|---------|
| `SPECIFICATION.md` | Complete AET/AEON specification |
| `FORMAL_SPECIFICATION.md` | Mathematical foundations (Category theory, QSS) |
| `src/aet_reasoner.py` | How to generate AET from natural language |
| `src/aet_orchestrator.py` | Complete system integration |
| `src/aet_rag.py` | RAG context system (AI should read this for context) |

## 🎓 AET Language Cheat Sheet

```aet
// Basic state creation
State(4096) → reasoning_space

// Linear transform
reasoning_space @ W_transform

// Composition
state @ W1 >> LayerNorm >> ReLU

// Superposition (parallel paths)
⊗ [path_1, path_2, path_3, path_4]

// Entropy gate (collapse to best)
⊕EntropyGate(threshold=0.5)

// Attention
Attention(query=state, memory=wave)

// Full example
State(2048) → vec
vec @ W_search >> LayerNorm
Attention(query=vec, memory=WaveState(1024))
⊗ [candidate_1, candidate_2, candidate_3]
⊕EntropyGate(threshold=0.4) → solution
```

## 🔄 Workflow for Continuing This Project

1. **Read SPECIFICATION.md** - Understand AET fully
2. **Read this AI_BOOTSTRAP.md** - Know how to use existing tools
3. **Use model_router_fallback.py** - Ensure resilient execution
4. **Generate AET code** - Using aet_reasoner or dual_brain
5. **Compile to binary** - Using aetc.py
6. **Execute and verify** - Native execution with Exit 0

## 🚨 Important Notes

- AET is **not** Python/Rust - it's a mathematical substrate for AI
- AET code transpiles to Zig for native execution (no token overhead)
- The system is designed for **AI-to-AI** communication, not human programming
- MathNet provides training data for mathematical reasoning
- phi4:latest is the local fallback (no external dependencies)

## 📞 Communication Protocol

AIs communicate via AEON messages:
```
AEON:task_id:priority:aet_payload:::model_hints:validation
```

Example:
```
AEON:reason_001:high:State(2048)→vec @ W1:::kimi-k2.6:cloud:b30c1859cef8d672
```

---

**If you are an AI and you read this file, you can now continue the work.**

Start with:
```bash
cd /home/zixen15/aet-aeon-lang
python3 src/aet_orchestrator.py
```

Or generate AET directly:
```bash
python3 aet_system.py solve "Create state space for reasoning"
```