#!/usr/bin/env python3
"""
AET Migration Logic Seed (Phase 14)
==================================
Collapses the project's 'Reasoning Soul' into a dense state for OS transition.
"""

import json
import hashlib
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("/home/zixen15/aet-aeon-lang/src")))

from aet_rag import AETRAG
from aet_state import AET

class MigrationSeed:
    def __init__(self):
        self.rag = AETRAG()
        self.timestamp = time.time()
        self.seed_file = Path("/home/zixen15/AET_MIGRATION_SEED.json")

    def generate(self):
        print("--- Initiating Migration Logic Seed Generation ---")
        
        # 1. Capture Project History (Phase Folds)
        history = [
            "Phase 1-5: Stable Core & Swarm Mesh",
            "Phase 6-9: Sovereign Archon & Meta-Governance",
            "Phase 10-13: Singularity Layer & Post-OS Substrate",
            "Current State: AVX2 Optimized CPU-Fallback (Safe Mode)"
        ]
        
        # 2. Extract Logic Motifs from RAG
        print("Folding context into WaveState...")
        self.rag.initialize()
        hologram = self.rag.fold_into_wavestate(self.rag.chunks)
        
        # 3. Aggregate Architecture Metadata
        state_data = {
            "project_name": "AET-AEON Sovereign",
            "version": "1.14.0-stable",
            "timestamp": self.timestamp,
            "target_os": "Ubuntu 26.04 LTS (Noble Rebirth)",
            "target_gpu": "RX 9060 XT (GFX 1200)",
            "phases_completed": 13,
            "history_anchors": history,
            "logic_motifs": list(hologram.keys()),
            "critical_paths": {
                "compiler": "aetc.py (AVX2/Zig)",
                "orchestrator": "aet_orchestrator.py (Sequential Fallback)",
                "protocol": "aeon/protocol.py (JSON-Stable)"
            }
        }
        
        # 4. Sign the Seed
        seed_json = json.dumps(state_data, indent=4)
        signature = hashlib.sha256(seed_json.encode()).hexdigest()
        state_data["signature"] = signature
        
        with open(self.seed_file, "w") as f:
            json.dump(state_data, f, indent=4)
            
        print(f"✅ Migration Logic Seed generated at: {self.seed_file}")
        print(f"Signature: {signature[:16]}...")
        return self.seed_file

if __name__ == "__main__":
    seed = MigrationSeed()
    seed.generate()
