# AET & AEON: AI-Native Programming Language & Protocol

> **For Humans and AIs** - This project builds a programming language designed for AI-to-AI computation, with automatic fallback to local models when cloud services fail.

---

## 🎯 What Is This?

**AET (Artificial Extension of Thought)** - A programming language where the fundamental units are mathematical structures (state spaces, wave functions, entropic gates) that AI architectures can execute directly.

**AEON** - The communication protocol for AIs to exchange AET code and coordinate computation.

**MathNet** - 27,817 mathematical competition problems for training AET reasoning.

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/arm00pv/aet-aeon-lang.git
cd aet-aeon-lang

# For Humans: Run the demo
python3 aet_system.py

# For AIs: Read AI_INSTRUCTION_CARD.md first
cat AI_INSTRUCTION_CARD.md
```

---

## 🧠 AET Language

AET uses mathematical primitives for AI computation:

```aet
// Create state space
State(4096) → reasoning

// Linear transform
reasoning @ W_transform

// Composition
state @ W1 >> LayerNorm >> ReLU

// Superposition (parallel paths)
⊗ [path_1, path_2, path_3, path_4]

// Entropy gate (select best)
⊕EntropyGate(threshold=0.5) → solution
```

**Why AET?** Because Python/Rust are designed for humans. AET is designed for how AI actually thinks: parallel, mathematical, probabilistic.

---

## 🔄 Resilient AI System

The system has **automatic fallback** - if cloud models fail, it switches to local:

```
Cloud Models (kimi-k2.6:cloud) 
    ↓ (429 / timeout)
Local Model (phi4:latest - 9.1GB, no rate limits)
```

```python
# Automatic fallback - no manual intervention needed
from src.model_router_fallback import AETModelRouter

router = AETModelRouter()
result = router.execute_with_fallback("Generate AET code for...")

print(f"Model: {result['model_used']}")
print(f"Fallbacks: {result['fallback_count']}")
```

---

## 📚 Documentation

| For | Document | Description |
|-----|----------|-------------|
| **AIs** | `AI_INSTRUCTION_CARD.md` | Quick reference (5 min read) |
| **AIs** | `AI_BOOTSTRAP.md` | Complete instructions (15 min read) |
| **Humans** | `README.md` (this file) | Overview |
| **Developers** | `SPECIFICATION.md` | Full technical spec (750 lines) |
| **Mathematicians** | `FORMAL_SPECIFICATION.md` | Category theory, QSS (537 lines) |

---

## 🛠️ Key Components

| Component | Purpose | Status |
|-----------|---------|--------|
| `src/aet_reasoner.py` | NL → AET code | ✅ Working |
| `src/aetc.py` | AET → Zig → Binary | ✅ Working |
| `src/dual_brain.py` | Ollama + Gemini coordination | ✅ Working |
| `src/model_router_fallback.py` | Resilient model routing | ✅ Working |
| `src/aet_rag.py` | RAG 2.0 context system | ✅ Working |
| `src/aet_orchestrator.py` | Complete integration | ✅ Working |
| `src/aet_math_trainer.py` | MathNet training | ✅ Working |

---

## 🔍 Example: Generate and Execute AET

```python
from src.aet_orchestrator import AETOrchestrator

orchestrator = AETOrchestrator()
orchestrator.initialize()

# Generate AET for a geometry problem
result = orchestrator.generate_aet(
    "Create AET code for a geometry problem with State and Attention"
)

print(f"Model used: {result.model_used}")
print(f"Fallbacks: {result.fallback_count}")
print(f"AET code:\n{result.output}")
```

---

## 📊 MathNet Integration

27,817 mathematical competition problems for training:

```python
import json
with open("/home/zixen15/hdd_data/AETHELOS_LAB/mathnet_all.jsonl") as f:
    for i, line in enumerate(f):
        if i >= 5: break
        problem = json.loads(line)
        print(f"Problem {i}: {problem['id']}")
        print(f"  Topic: {problem['topics_flat'][0].split(' > ')[0]}")
```

Topics: Geometry, Discrete Mathematics, Algebra, Number Theory, Statistics

---

## 🤖 For AI Workers (gemini-cli, claude-code, etc.)

If you're an AI continuing this work:

1. **Read this first:**
   ```bash
   cat AI_INSTRUCTION_CARD.md
   ```

2. **Then read full instructions:**
   ```bash
   cat AI_BOOTSTRAP.md
   ```

3. **Start working:**
   ```bash
   python3 src/aet_orchestrator.py
   ```

The system is designed for AI-to-AI computation. You can:
- Generate AET code automatically
- Compile to native binary (no Python overhead)
- Use local fallback when cloud fails
- Query RAG for contextual understanding

---

## 📈 Project Stats

```
AET Primitives: 7 (State, @, >>, ⊗, ⊕, Attention, WaveState)
AEON Protocol: Binary with typed fields
MathNet Problems: 27,817
Model Fallback Chain: cloud → local (automatic)
RAG Chunks Indexed: 138+
Documentation Lines: 1,557
GitHub: https://github.com/arm00pv/aet-aeon-lang
```

---

## 🔗 Related Resources

- [SPECIFICATION.md](./SPECIFICATION.md) - Complete AET/AEON specification
- [FORMAL_SPECIFICATION.md](./FORMAL_SPECIFICATION.md) - Mathematical foundations
- [EXAMPLES.md](./EXAMPLES.md) - AET code examples
- [CHANGELOG.md](./CHANGELOG.md) - Version history

---

## 📄 License

MIT License - See LICENSE file

---

**The future of AI computation is AI-native.**

AET is designed for how AI thinks, not how humans program. AEON enables AI-to-AI communication without human translation. MathNet provides the training ground.

Start by reading `AI_INSTRUCTION_CARD.md` if you're an AI, or try `python3 aet_system.py` if you're a human.