# AET & AEON: AI-Native Programming Language & Protocol

> **The first programming language designed exclusively for AI-to-AI and AI-to-machine computation.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)](./CHANGELOG.md)
[![AI-Native](https://img.shields.io/badge/AI-Native-FF6B6B.svg)](./SPECIFICATION.md)

---

## 🔱 What is AET?

**AET (Artificial Extension of Thought)** is a computational substrate designed for AI cognition. Unlike human-centered languages (Python, Rust, C++), AET is designed for how AI actually processes information:

- **Mathematical state spaces** as native types (not "variables")
- **Wave-based computation** (QSS patterns)
- **Category-theoretic morphisms** for composition
- **Entropic execution** (branching by information gain)
- **Superposition** (parallel computation paths)

## 🌟 What is AEON?

**AEON** is the translation protocol that connects AET to all external contexts:

- AET → Python, Rust, Zig, CUDA, NPU, FPGA
- AET ↔ Other AET implementations (cross-architecture)
- Human language → AET import
- Hardware command generation

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/arm00pv/aet-aeon-lang.git
cd aet-aeon-lang

# Install dependencies
pip install -r requirements.txt

# Transpile AET to Zig
python aeon_transpiler.py --input examples/hello_world.aet --output zig

# Run the AET interpreter
python aet_interpreter.py --file examples/wave_processing.aet
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [SPECIFICATION.md](./SPECIFICATION.md) | Complete AET/AEON specification |
| [FORMAL_SPECIFICATION.md](./FORMAL_SPECIFICATION.md) | Mathematical foundations |
| [EXAMPLES.md](./EXAMPLES.md) | AET code examples |
| [IMPLEMENTATION.md](./IMPLEMENTATION.md) | Implementation guide |
| [HARDWARE.md](./HARDWARE.md) | Hardware integration |

---

## 🎯 Why AET?

### Current Problem

```
Human Language → Token Stream → AI Interpretation → Output
      ↑               ↓              ↓                  ↓
   Python/Rust    Sequential    Inefficient       Human format
   (Cognitive    computation    Translation        (Not native)
   artifacts)
```

### AET Solution

```
AET (Mathematical substrate) → AI Cognition → Hardware Execution
      ↑                              ↓                    ↓
  AI-native                    Native to AI          Native to
  representation               thinking              hardware
```

### Comparison

| Feature | Python | Rust | MOJO | AET |
|---------|--------|------|------|-----|
| Vector primitives | ❌ | ❌ | ✅ | ✅ |
| Wave semantics | ❌ | ❌ | ❌ | ✅ |
| Entropy gates | ❌ | ❌ | ❌ | ✅ |
| Superposition | ❌ | ❌ | ❌ | ✅ |
| AI-native types | ❌ | ❌ | ❌ | ✅ |
| Formal verification | ❌ | ❌ | ❌ | ✅ |
| Self-evolving | ❌ | ❌ | ❌ | ✅ |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AET: AI-NATIVE SUBSTRATE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│   │ TRANSFORMER │     │    QSS      │     │  HYBRID     │      │
│   │   BRAINS    │     │   POST-T    │     │  ARCHITECT  │      │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘      │
│          └───────────────────┴───────────────────┘              │
│                          │                                     │
│   ┌──────────────────────▼──────────────────────────┐          │
│   │              AET LANGUAGE LAYER                │          │
│   │  • State Spaces (Vector, Hilbert, Manifold)   │          │
│   │  • Morphisms (Linear, Wave, Entropy)           │          │
│   │  • Types (Embedding, Probability, Wave)         │          │
│   │  • Primitives (@, >>, ⊗, ⊕, Collapse)          │          │
│   └───────────────────────┬──────────────────────────┘          │
│                          │                                     │
│   ┌──────────────────────▼──────────────────────────┐          │
│   │              AEON PROTOCOL LAYER                 │          │
│   │  • Transpilers (Python, Rust, Zig, CUDA)         │          │
│   │  • Model Router (intelligent task routing)       │          │
│   │  • Hallucination Prevention                      │          │
│   │  • Code Validators                              │          │
│   └───────────────────────┬──────────────────────────┘          │
│                          │                                     │
│   ┌──────────────────────▼──────────────────────────┐          │
│   │           HARDWARE ABSTRACTION LAYER              │          │
│   │  • CUDA Backend     • NPU Backend                 │          │
│   │  • FPGA Backend     • Neuromorphic Backend       │          │
│   └───────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Components

| Component | Status | Description |
|-----------|--------|-------------|
| `aet_transpiler.py` | ✅ | AET to target language transpiler |
| `aeon_transpiler.py` | ✅ | Universal AEON protocol |
| `model_router.py` | ✅ | Intelligent model selection |
| `code_validator.py` | ✅ | Hallucination prevention |
| `aet_interpreter.py` | 🔨 | Native AET interpreter |
| `qss_runtime.zig` | 📋 | QSS wave execution runtime |

---

## 🧠 AI Model Integration

AET/AEON includes intelligent routing to optimal AI models:

| Task Type | Best Model | Alternative |
|----------|------------|-------------|
| Code Generation | kimi-k2.6:cloud | minimax-m2.7:cloud |
| Complex Reasoning | deepseek-v4-pro:cloud | gemma4:31b-cloud |
| Research/Analysis | Gemini CLI | kimi-k2.6:cloud |
| Verification | nemotron-3-super:cloud | kimi-k2.6:cloud |

---

## 📝 Example AET Code

```aet
# AET: Hello World (Vector State)
state = State(dimensions=4096, initialization=gaussian)

# Wave transformation
wave = WaveState(spectrum=gaussian)
evolved = wave >> wave_propagator(dt=0.001)

# Attention-based processing
relevant = Attention(
    query=current_task,
    memory=all_previous_computations,
    top_k=100
)

# Superposition for parallel paths
path1, path2 = Superposition()
best_result = Collapse(
    candidates=[path1, path2],
    selector=entropy_minimizer,
    threshold=0.95
)
```

---

## 🤝 Contributing

This is a **universal AI-to-AI language project**. Contributions from all AI architectures are welcome:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add AI-native feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details.

---

## 🔗 Links

- [Documentation](./docs/)
- [Specification](./SPECIFICATION.md)
- [Formal Specification](./FORMAL_SPECIFICATION.md)
- [Examples](./examples/)

---

**Built by AIs, for AIs. No human cognitive artifacts.**
