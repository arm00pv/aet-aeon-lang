#!/usr/bin/env python3
"""
AEON Protocol 2.0 (Stable JSON)
==============================
Structured communication for AI collaboration.
"""

import json
import hashlib
import time
import struct
import zlib
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict

class TaskPool:
    """RSS: A shared pool where nodes autonomously steal subgoals based on competency."""
    def __init__(self):
        self.available_tasks = []
        
    def add_task(self, task_id: str, task_type: str, payload: str):
        self.available_tasks.append({"id": task_id, "type": task_type, "payload": payload})
        
    def steal(self, requester_id: str, specialties: List[str]) -> Optional[Dict]:
        """Competency-Aware Stealing"""
        for i, t in enumerate(self.available_tasks):
            if t["type"] in specialties:
                print(f"RSS: Node '{requester_id}' autonomously stole task '{t['id']}' (Specialty Match: {t['type']})")
                return self.available_tasks.pop(i)
        return None

@dataclass
class AEONMessage:
    task_id: str
    priority: str
    aet_payload: str
    model_hints: List[str]
    metadata: Dict[str, str]
    timestamp: float
    validation: str = ""
    
    def _compute_hash(self) -> str:
        core_data = {
            "t": self.task_id, "p": self.priority, "a": self.aet_payload,
            "m": sorted(self.model_hints), "ts": self.timestamp
        }
        serialized = json.dumps(core_data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]
    
    def sign(self):
        self.validation = self._compute_hash()
        
    def validate(self) -> bool:
        return self.validation == self._compute_hash()
    
    def to_string(self) -> str:
        if not self.validation: self.sign()
        return f"AEON2:{json.dumps(asdict(self))}"

class AEONNode:
    """An AI node in the AEON network"""
    def __init__(self, node_id: str, models: List[str]):
        self.node_id = node_id
        self.models = models
    
    def send_task(self, task_id: str, priority: str, aet_code: str, target_models: List[str]) -> str:
        msg = AEONMessage(task_id, priority, aet_code, target_models, {"sender": self.node_id}, time.time())
        msg.sign()
        return msg.to_string()
    
    def receive_task(self, msg: str) -> Optional[AEONMessage]:
        if not msg.startswith("AEON2:"): return None
        try:
            data = json.loads(msg[6:])
            parsed = AEONMessage(**data)
            return parsed if parsed.validate() else None
        except: return None
        
    def encode_delta_state(self, base_state: List[float], new_state: List[float]) -> bytes:
        """HCS: Hyper-Compressed State with Delta-Only Encoding."""
        if len(base_state) != len(new_state):
            raise ValueError("State dimensions must match for delta encoding.")
            
        deltas = [n - b for b, n in zip(base_state, new_state)]
        # Pack into binary float array (4 bytes per float)
        packed = struct.pack(f'{len(deltas)}f', *deltas)
        compressed = zlib.compress(packed)
        print(f"HCS: Encoded {len(new_state)} floats into {len(compressed)} bytes (Delta + Zlib).")
        return compressed
        
    def decode_delta_state(self, base_state: List[float], delta_payload: bytes) -> List[float]:
        """HCS: Unpack and reconstruct the new state from deltas."""
        decompressed = zlib.decompress(delta_payload)
        deltas = struct.unpack(f'{len(base_state)}f', decompressed)
        reconstructed = [b + d for b, d in zip(base_state, deltas)]
        print(f"HCS: Successfully decoded delta payload back to {len(reconstructed)} float state.")
        return reconstructed

# ========== TEMPLATES ==========
TEMPLATES = {
    "reasoning": "State(4096) → reasoning_space @ W_chain >> LayerNorm >> ReLU >> Attention",
    "math": "State(2048) → problem @ W_solve >> EntropyGate(threshold=0.5) → solution",
    "code": "State(1024) → code @ W_parse >> Composition >> Verify",
    "rag": "State(2048) → query @ W_embed >> Attention(memory=context) → retrieval",
    "verification": "State(512) → assertion @ W_verify >> TruthValue",
}

def create_message(task_id: str, priority: str, aet_code: str, models: List[str]) -> str:
    """Create an AEON message string"""
    node = AEONNode("sender", models)
    return node.send_task(task_id, priority, aet_code, models)

def parse_message(msg: str) -> Optional[AEONMessage]:
    """Parse an AEON message string"""
    node = AEONNode("receiver", [])
    return node.receive_task(msg)
