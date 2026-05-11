# AET Model Update Summary - phi4 → qwen3.5:9b

## Changes Made

The system has been updated to use **Qwen3.5 models** instead of phi4/old models.
This is because phi4:latest is no longer available on this system.

### Updated Files

1. **`model_router_fallback.py`**
   - **Workflow**: kimi-k2.6:cloud → nemotron-3-super:cloud → qwen3.5:9b → qwen3.5:4b
   - **Models configured**:
     - `kimi-k2.6:cloud` - Primary cloud model for fast inference
     - `nemotron-3-super:cloud` - Secondary cloud model for verification
     - `qwen3.5:9b` - Local fallback (9B model ~8GB VRAM)
     - `qwen3.5:4b` - Final fallback (4B model ~4GB VRAM)
   - **Fallback logic**: When cloud gives 429 rate limit error, fall back to local models

2. **`aet_orchestrator.py`**
   - Updated to use `qwen3.5:4b` as fallback model
   - Now warms up both `qwen3.5:9b:cloud` and `qwen3.5:4b`

3. **`worker_pi.py`**
   - Changed from `kimi-k2.6:cloud` to `qwen3.5:9b:cloud`
   - Updated comments to reflect the new model

4. **`aethelos_integration.py`**
   - Changed Archon node from `["kimi-k2.6:cloud", "deepseek-v4-pro:cloud"]` to `["qwen3.5:9b:cloud"]`

5. **`aet_math_solver.py`**
   - Changed from `kimi-k2.6:cloud` to `qwen3.5:9b:cloud`

6. **`aet_reasoner.py`**
   - Changed from `["kimi-k2.6:cloud", "gemini"]` to `["qwen3.5:9b:cloud", "gemini"]`

7. **`aeon/protocol.py`**
   - Changed `alpha_node` from `["kimi-k2.6:cloud"]` to `["qwen3.5:9b"]`

8. **`aet_doc_indexer.py`**
   - Updated fallback from `phi4:latest` to `qwen3.5:4b`

9. **`dual_brain.py`**
   - Changed code_gen from `kimi-k2.6:cloud` to `qwen3.5:9b:cloud`
   - Updated model defaults for `__init__`

## Model Hierarchy

```
kimi-k2.6:cloud (CLOUD_PRIMARY)
    ↓ if 429 rate limit
nemotron-3-super:cloud (CLOUD_SECONDARY)
    ↓ if still failing
qwen3.5:9b (LOCAL_FALLBACK - ~8GB VRAM)
    ↓ if VRAM limited
qwen3.5:4b (LOCAL_FALLBACK - ~4GB VRAM, safe fallback)
```

## Benefits

1. **Better VRAM management**: qwen3.5:9b ~8GB, qwen3.5:4b ~4GB
2. **More precise math**: qwen3.5 is better for AET's mathematical reasoning
3. **Hybrid approach**: Uses cloud speed when available, local reliability when needed
4. **Automatic fallback**: System gracefully degrades from cloud to local models

## Usage

The system now automatically selects models based on availability and constraints:

1. Try fastest cloud model (kimi-k2.6)
2. If rate limited, use another cloud model (nemotron-3-super)
3. If cloud unavailable, use local 9B model as primary fallback
4. If VRAM is tight, fall back to 4B model

All models are fully configured and ready to use.
