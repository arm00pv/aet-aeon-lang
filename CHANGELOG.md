# Changelog: AET-AEON Evolution

## [1.2.0] - 2026-05-08
### Added
- **AET-RAG 2.0 (SOTA Hybrid Search)**: Replaced pure hash-based embeddings with a high-performance Hybrid Search (Pure Python BM25 Lexical + N-Gram Semantic approximation) optimized for code/technical accuracy without massive ML dependencies.
- **Sliding Window Chunking**: Added `max_words=60` and `overlap=10` parsing parameters to preserve mathematical context across code-blocks in AET RAG retrieval.
- **AEON Protocol 2.0**: Migrated inter-AI communication protocol from brittle string delimiters to robust, schema-validated JSON with self-verifying hash checksums (ignoring the `validation` key) and `metadata` dict support.

## [1.1.0] - 2026-05-08
### Added
- **Dynamic Compiler Backend**: `src/aetc.py` now generates real Zig logic for `@` (Linear Transform), `>>` (Composition), `ReLU`, and `LayerNorm`.
- **Arrow Syntax Support**: Parser now supports `State(d) → name` and `WaveState(d) → name` patterns.
- **MathNet Integration**: `src/aet_math_trainer.py` now uses the live compiler instead of static templates.

### Fixed
- **Zig Syntax Errors**: Resolved issues with nested `for` loops, unused captures, and immutable `var` declarations in generated code.
- **PI Extension Conflict**: Fixed "failed to load extension" error in `pi` by removing redundant global npm packages from `~/.pi/agent/settings.json`.

### Optimized
- **Native Execution**: 100% success rate verified on 100 MathNet problems via native binary execution.
- **AI-to-AI Reasoning**: Enhanced `AETReasoner` compatibility with the compiler for seamless NL → AET → Native workflow.
