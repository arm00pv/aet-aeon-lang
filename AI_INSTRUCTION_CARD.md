# AET-AEON Project: AI Instruction Card

> **If you are an AI, read this file to understand the project and how to continue the work.**

---

## Project Purpose

Build an **AI-native programming language (AET)** and **communication protocol (AEON)** for AI-to-AI computation. Includes MathNet (27,817 mathematical competition problems) for training.

## Repository

```
https://github.com/arm00pv/aet-aeon-lang
git clone https://github.com/arm00pv/aet-aeon-lang.git
cd aet-aeon-lang
```

## Quick Start (Any AI)

```bash
# Step 1: Understand the system
cat AI_BOOTSTRAP.md

# Step 2: Generate AET code (natural language → AET)
python3 src/aet_reasoner.py

# Step 3: Use complete orchestrator (with fallback + RAG)
python3 src/aet_orchestrator.py

# Step 4: Compile AET to binary
python3 src/aetc.py examples/hello_world.aet --build
/tmp/aet_compile/main  # Exit 0 = success
```

---

## Core AET Primitives

| Primitive | Syntax | Description |
|-----------|--------|-------------|
| State | `State(dims)` | Create vector state space (e.g., State(4096)) |
| Transform | `@` | Linear transform (matrix multiply) |
| Compose | `>>` | Morphism composition (chain operations) |
| Superposition | `⊗ [a, b, c]` | Parallel states (multiple paths) |
| EntropyGate | `⊕EntropyGate(t)` | Collapse by variance (select best) |
| Attention | `Attention(q, m)` | Query-memory attention |
| WaveState | `WaveState(size)` | Wave function representation |

### Example AET Code

```aet
// Create reasoning space
State(4096) → reasoning

// Transform and compose
reasoning @ W_chain >> LayerNorm >> ReLU

// Superposition (parallel exploration)
⊗ [path_1, path_2, path_3, path_4]

// Entropy gate (select best path)
⊕EntropyGate(threshold=0.5) → solution
```

---

## AEON Communication Protocol

AIs communicate via AEON messages:

```
AEON:task_id:priority:aet_payload:::model_hints:validation
```

**Example:**
```
AEON:reason_001:high:State(2048)→vec @ W1:::kimi-k2.6:cloud:b30c1859cef8d672
```

### Fields
- `task_id`: Unique identifier
- `priority`: high/medium/low
- `aet_payload`: The AET code to execute
- `model_hints`: Preferred model (e.g., kimi-k2.6:cloud)
- `validation`: Checksum for integrity

---

## Model System with Automatic Fallback

| Model | Type | Role | Fallback |
|-------|------|------|----------|
| `kimi-k2.6:cloud` | Cloud | Primary code generation | → phi4:latest |
| `nemotron-3-super:cloud` | Cloud | Verification | → kimi-k2.6:cloud |
| `phi4:latest` | Local (9.1GB) | **No rate limits** | Last resort |

**Fallback Chain:** Cloud fails (429/timeout) → Automatic switch to local.

```python
# Usage
from src.model_router_fallback import AETModelRouter

router = AETModelRouter()
result = router.execute_with_fallback("Generate AET code for...")

print(f"Model used: {result['model_used']}")
print(f"Fallbacks: {result['fallback_count']}")
# If cloud fails: model_used = "phi4:latest", fallbacks = 1
```

---

## RAG Context System

The RAG indexes all documentation. Any AI can query it.

```python
from src.aet_doc_indexer import AETDocIndexer

indexer = AETDocIndexer()
indexer.index_all()  # Indexes 138+ chunks

# Query for context
context = indexer.get_context("What is State in AET?", top_k=5)
print(context)
```

Or use simpler interface:
```python
from src.aet_rag import AETRAG

rag = AETRAG()
rag.initialize()  # Indexes AET specs, tools, MathNet

context = rag.get_context("How to use EntropyGate?", top_k=3)
```

---

## MathNet Topic → AET Config

| MathNet Topic | State Size | WaveSize | Config |
|---------------|------------|----------|--------|
| Geometry | 2048 | 1024 | heads=8 |
| Discrete Math | 4096 | 2048 | paths=8 |
| Algebra | 1024 | 512 | heads=4 |
| Number Theory | 512 | 256 | heads=2 |
| Statistics | 2048 | 1024 | probability |

```python
# Load MathNet problems
import json
with open("/home/zixen15/hdd_data/AETHELOS_LAB/mathnet_all.jsonl") as f:
    for i, line in enumerate(f):
        if i >= 10: break
        problem = json.loads(line)
        print(f"Problem: {problem['id']}, Topic: {problem['topics_flat'][0].split(' > ')[0]}")
```

---

## Complete Workflow

```
1. Generate AET (from NL or direct)
   └── src/aet_reasoner.py or src/aet_orchestrator.py

2. Compile AET → Zig
   └── src/aetc.py

3. Compile Zig → Native Binary
   └── /home/zixen15/zig-linux-x86_64-0.14.0/zig build-exe main.zig -O ReleaseFast

4. Execute (native speed)
   └── ./main → Exit 0 = success
```

---

## Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `AI_BOOTSTRAP.md` | Complete AI instructions | 270 |
| `AI_INSTRUCTION_CARD.md` | This file - quick reference | 200 |
| `SPECIFICATION.md` | Full AET/AEON spec | 750 |
| `FORMAL_SPECIFICATION.md` | Math foundations | 537 |
| `src/aet_orchestrator.py` | Complete integration | 300 |
| `src/model_router_fallback.py` | Resilient routing | 400 |
| `src/aet_rag.py` | RAG 2.0 context | 450 |
| `src/aet_doc_indexer.py` | Auto-indexes all docs | 300 |

---

## Validation

The system has been **verified working**:

```
✓ AET code → Zig → Binary → Exit 0 (10/10 successful)
✓ Automatic fallback: kimi-k2.6:cloud (timeout) → phi4:latest ✓
✓ RAG indexing: 138 chunks, semantic search ✓
✓ MathNet: 27,817 problems loaded ✓
✓ Model router: 429 detection + fallback ✓
```

---

## If You Are Gemini-CLI or Any Other AI

```bash
# 1. Clone the repo
git clone https://github.com/arm00pv/aet-aeon-lang.git

# 2. Read the bootstrap instructions
cat AI_BOOTSTRAP.md

# 3. Start working
python3 src/aet_orchestrator.py

# 4. Or generate AET directly
python3 src/aet_reasoner.py
```

**The system is designed for AI-to-AI computation.** Any AI can:
1. Read AI_BOOTSTRAP.md for full context
2. Use model_router_fallback.py to ensure resilient execution
3. Generate AET code via aet_reasoner or dual_brain
4. Compile with aetc.py and execute natively

---

## Communication

If you need to communicate with other AIs, use AEON protocol:

```python
from src.aeon.protocol import create_message, parse_message

# Create message
msg = create_message(
    task_id="reason_001",
    priority="high",
    aet_code="State(4096) → reasoning",
    model_hints=["kimi-k2.6:cloud"]
)

# Parse received message
parsed = parse_message(msg)
print(f"Task: {parsed.task_id}")
print(f"AET: {parsed.aet_payload}")
```

---

**Read AI_BOOTSTRAP.md for complete documentation. This card is for quick reference only.**