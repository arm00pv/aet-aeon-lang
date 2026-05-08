# Changelog

All notable changes to AET & AEON will be documented in this file.

## [1.0.0] - 2026-05-08

### Added
- **AET Language Specification** - Complete AI-native programming language definition
- **AEON Protocol** - Translation layer between AET and external contexts
- **Formal Specification** - Mathematical foundations (Category Theory, Type Theory)
- **AET Interpreter** - Native runtime for AET code execution
- **AEON Transpiler** - Transpiles AET to Python, Rust, Zig, CUDA
- **Model Router** - Intelligent AI model selection with hallucination prevention
- **Code Validator** - Validates generated code for quality and correctness
- **Examples** - Hello world and basic operations in AET
- **Implementation Guide** - How to implement AET for your AI architecture
- **Hardware Guide** - Integration with CUDA, NPU, FPGA backends

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| Interpreter | `src/aet_interpreter.py` | Execute AET code directly |
| Transpiler | `aeon_transpiler.py` | AET → target language |
| Model Router | `model_router.py` | Intelligent task routing |
| Orchestrator | `orchestrator.py` | Main CLI entry point |
| Supervisor | `src/supervisor/supervisor.py` | Orchestration with validation |

### AET Primitives

- `State(dimensions, initialization)` - Vector state space
- `WaveState(spectrum)` - Wave state (complex)
- `Probability(distribution)` - Probability distribution
- `@` - Linear transform (matrix multiplication)
- `>>` - Composition (morphism chain)
- `⊗` - Superposition (parallel states)
- `Attention(query, memory, top_k)` - Attention mechanism
- `Collapse(candidates, selector, threshold)` - State selection

### Supported Targets

- Python ✅
- Rust ✅
- Zig ✅
- CUDA ✅
- NPU (Apple Neural Engine) 🔨
- FPGA 🔨

### Model Integration

- Ollama Cloud Models (kimi, deepseek, minimax, gemma, etc.)
- Gemini CLI for research and verification
- Intelligent routing based on task type
- Hallucination prevention through validation

## [0.1.0] - 2026-05-08

### Added
- Initial specification
- Core language design
- Mathematical foundations

---

**Built by AIs, for AIs. No human cognitive artifacts.**
