#!/usr/bin/env python3
"""
AEON Protocol 2.0 - AI-to-AI Communication (JSON-Structured)
============================================================
Universal, structured language for AI collaboration.

Upgrades from 1.0:
- JSON structure instead of brittle string concatenation
- Extended metadata (timestamps, strict schemas)
- Self-verifying checksums
- Easily extensible for new AI architectures
"""

import json
import hashlib
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict

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
        """Compute structural hash ignoring the validation field itself"""
        core_data = {
            "t": self.task_id,
            "p": self.priority,
            "a": self.aet_payload,
            "m": sorted(self.model_hints),
            "ts": self.timestamp
        }
        serialized = json.dumps(core_data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]
    
    def sign(self):
        """Signs the message with a verification hash"""
        self.validation = self._compute_hash()
        
    def validate(self) -> bool:
        """Validates message integrity"""
        return self.validation == self._compute_hash()
    
    def to_string(self) -> str:
        """Serializes to the AEON JSON Envelope format"""
        if not self.validation:
            self.sign()
        return f"AEON2:{json.dumps(asdict(self))}"

def create_message(task_id: str, priority: str, aet_code: str, models: List[str], metadata: Dict = None) -> str:
    msg = AEONMessage(
        task_id=task_id,
        priority=priority,
        aet_payload=aet_code,
        model_hints=models,
        metadata=metadata or {},
        timestamp=time.time()
    )
    msg.sign()
    return msg.to_string()

def parse_message(msg: str) -> Optional[AEONMessage]:
    if not msg.startswith("AEON2:"):
        # Fallback for old AEON format
        if msg.startswith("AEON:"):
            print("Warning: Received deprecated AEON 1.0 message.")
            parts = msg[5:].split(":::")
            if len(parts) == 2:
                h_parts = parts[0].split(":", 2)
                if len(h_parts) == 3:
                    return AEONMessage(h_parts[0], h_parts[1], h_parts[2], [], {}, time.time(), parts[1].split(":")[1])
        return None
        
    try:
        data = json.loads(msg[6:])
        parsed = AEONMessage(**data)
        if parsed.validate():
            return parsed
        else:
            print("Error: AEON Message validation failed (corrupted payload).")
            return None
    except json.JSONDecodeError:
        print("Error: AEON Message malformed JSON.")
        return None

class AEONNode:
    """An AI node in the AEON network"""
    
    def __init__(self, node_id: str, models: List[str]):
        self.node_id = node_id
        self.models = models
        self.pending_tasks = []
        self.completed_tasks = []
    
    def send_task(self, task_id: str, priority: str, aet_code: str, target_models: List[str]) -> str:
        """Send task to another AI"""
        return create_message(task_id, priority, aet_code, target_models, {"sender": self.node_id})
    
    def receive_task(self, msg: str) -> Optional[AEONMessage]:
        """Receive and validate task"""
        parsed = parse_message(msg)
        if parsed:
            self.pending_tasks.append(parsed)
            return parsed
        return None
    
    def execute_aet(self, aet_code: str) -> dict:
        """Mock execute AET code"""
        return {
            "status": "success",
            "exit_code": 0,
            "result": "AET execution complete"
        }
    
    def send_response(self, original_task: AEONMessage, result: dict) -> str:
        """Send result back"""
        return create_message(
            f"{original_task.task_id}_response",
            original_task.priority,
            f"result:{result['status']}",
            [self.node_id],
            {"in_response_to": original_task.task_id}
        )

# AET Task Templates
TEMPLATES = {
    "reasoning": "State(2048) → reasoning_state\nreasoning_state @ W_chain >> LayerNorm >> ReLU\nAttention(query=reasoning_state, memory=WaveState(1024))\n⊕EntropyGate(threshold=0.5)",
    "search": "State(4096) → search_space\nsearch_space ⊗ [path_1, path_2, path_3, path_4]\n⊕EntropyGate(threshold=0.7) → best_path",
}

def demo():
    print("AEON Protocol 2.0 (Structured JSON) Demo")
    print("=" * 60)
    
    ai_alpha = AEONNode("alpha_node", ["kimi-k2.6:cloud"])
    ai_beta = AEONNode("beta_node", ["gemini-pro:cloud"])
    
    task = TEMPLATES["reasoning"]
    msg = ai_alpha.send_task("task_001", "high", task, ["gemini-pro:cloud"])
    
    print(f"[Alpha] Generated Message Payload:\n{msg}\n")
    
    received = ai_beta.receive_task(msg)
    if received:
        print(f"[Beta] Successfully decoded and validated message!")
        print(f"       Task ID: {received.task_id}")
        print(f"       Payload Length: {len(received.aet_payload)} bytes")
        
        result = ai_beta.execute_aet(received.aet_payload)
        response = ai_beta.send_response(received, result)
        print(f"\n[Beta] Response Payload:\n{response}")

if __name__ == "__main__":
    demo()