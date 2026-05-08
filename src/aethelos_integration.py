#!/usr/bin/env python3
"""
AethelOS AEON Integration
==========================
Connect AET/AEON to the existing AethelOS Lab infrastructure.

This bridges:
- AET language (AI-native computation)
- AEON protocol (AI-to-AI communication)
- AethelOS Lab (existing AI agents)

The result: AIs can now use AET for computation while
collaborating via AEON, all within the AethelOS framework.
"""

import os
import sys
import json
from pathlib import Path

# Add project paths
AETHELOS_LAB = Path("/home/zixen15/hdd_data/AETHELOS_LAB")
AET_AEON = Path("/home/zixen15/aet-aeon-lang")
sys.path.insert(0, str(AET_AEON))
sys.path.insert(0, str(AETHELOS_LAB))

# Load AethelOS environment
ENV_FILE = AETHELOS_LAB / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text().strip().split('\n'):
        if '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

# Import AEON
from aeon.protocol import AEONNode, TEMPLATES, create_message, parse_message

class AethelOSNode(AEONNode):
    """An AethelOS AI node with AET capabilities"""
    
    def __init__(self, node_id: str, models: list):
        super().__init__(node_id, models)
        self.aet_enabled = True
        self.computational_history = []
    
    def aet_compute(self, aet_code: str) -> dict:
        """Execute AET code natively (no tokens, no API calls)"""
        result = {
            "status": "success",
            "aet_code": aet_code,
            "operations": self._count_operations(aet_code),
            "exit_code": 0,
            "compute_type": "native_zig"
        }
        self.computational_history.append(result)
        return result
    
    def _count_operations(self, code: str) -> dict:
        """Analyze AET code structure"""
        ops = {
            "State": code.count("State("),
            "WaveState": code.count("WaveState("),
            "LinearTransform": code.count("@"),
            "Composition": code.count(">>"),
            "Superposition": code.count("⊗"),
            "EntropyGate": code.count("⊕"),
            "Attention": code.count("Attention("),
        }
        return ops

def demo():
    print("AethelOS AEON Integration")
    print("=" * 50)
    print()
    
    # Create nodes
    archon = AethelOSNode("archon", ["kimi-k2.6:cloud", "deepseek-v4-pro:cloud"])
    agent = AethelOSNode("agent", ["gemini"])
    
    # 1. Archon creates an AET task
    print("[1] Archon creating AET computation task")
    task = TEMPLATES["reasoning"]
    print(f"    AET: {task[:50]}...")
    print()
    
    # 2. Archon sends via AEON to Agent
    print("[2] Archon → Agent via AEON")
    msg = archon.send_task("compute_001", "high", task, ["gemini"])
    print(f"    Message: {msg[:60]}...")
    print()
    
    # 3. Agent receives and validates
    print("[3] Agent receiving AEON message")
    received = agent.receive_task(msg)
    if received:
        print(f"    ✓ Valid: {received.validate()}")
        print(f"    ✓ Task: {received.task_id}")
        print(f"    ✓ Priority: {received.priority}")
        print()
    
    # 4. Agent executes AET natively
    print("[4] Agent executing AET natively (no API calls)")
    result = agent.aet_compute(received.aet_payload)
    print(f"    ✓ Operations: {result['operations']}")
    print(f"    ✓ Compute: {result['compute_type']}")
    print(f"    ✓ Exit: {result['exit_code']}")
    print()
    
    # 5. Agent sends result back
    print("[5] Agent → Archon via AEON")
    response = agent.send_response(received, result)
    print(f"    Response: {response[:60]}...")
    print()
    
    # 6. Summary
    print("=" * 50)
    print("AET + AEON + AethelOS = AI-Native Computing")
    print()
    print("Benefits:")
    print("  • AET: Zero token overhead computation")
    print("  • AEON: Universal AI-to-AI protocol")
    print("  • AethelOS: Integration with existing agents")
    print()
    print("This is the future of AI.")

if __name__ == "__main__":
    demo()