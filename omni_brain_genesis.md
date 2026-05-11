# AET-AEON Omni-Brain Genesis Documentation

> **AI INSTRUCTION**: Read this file to understand how to continue the construction and training of the Heterogeneous Omni-Brain.

## Current Progress (Phase 17)
We have established the foundational substrate for building a multi-layered post-transformer brain. 

### Core Components
- **Language**: AET has been expanded with `Gradient`, `Checkpoint`, and `Offload` primitives.
- **Compiler**: `aetc.py` supports multithreaded AVX2 execution for training passes.
- **Harvester**: `aet_dataset_harvester.py` aggregates math, physics, and coding data.
- **Persistence**: Persistent Tensor Checkpointing (PTC) is enabled to survive crashes.

## How to Resume Training
1. **Initialize Environment**:
   ```python
   from aet_orchestrator import AETOrchestrator
   orch = AETOrchestrator()
   orch.initialize()
   ```
2. **Layer Assembly Sequence**:
   - Follow the sequence: **Mamba-3** → **LNN** → **TTT** → **H-MoE Router**.
   - Use `orch.generate_aet(task)` where task is "Build Layer X".
3. **Resilient Training**:
   - Every epoch must call `Checkpoint(state, "/home/zixen15/ptc/epoch_n.ptc")`.
   - If a kernel panic occurs, check the last `.ptc` file in `/home/zixen15/ptc/`.

## Governance & Safety
- **IVA**: Ensure all training code includes `USER_ALIGNMENT`.
- **Hardware Guarding**: If GPU is unstable, the system automatically falls back to CPU-AVX2.

---
*Created by AET-Orchestrator during Phase 17 Genesis.*
