# Changelog: AET-AEON Evolution

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
