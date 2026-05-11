#!/usr/bin/env python3
"""
AET_AEON_WORKER_PI.py - Pi-based AI Worker
==========================================
Executes tasks using pi with ollama cloud models as the brain.
Uses qwen3.5:9b:cloud for inference.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Import our hardware guarding
sys.path.insert(0, str(Path(__file__).parent))
from aetc import check_hardware_safety

WORKER_NAME = "AETHEL_PI"
LOG_DIR = "/home/zixen15/aet_aeon/logs"
RESULTS_DIR = "/home/zixen15/aet_aeon/results"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Corrected cloud model name
DEFAULT_MODEL = "qwen3.5:cloud"

def log(msg):
    ts = datetime.now().isoformat()
    print(f"🤖 [{WORKER_NAME}] {msg}")
    with open(os.path.join(LOG_DIR, f"{WORKER_NAME}.log"), "a") as f:
        f.write(f"[{ts}] {msg}\n")

def execute_ollama_task(prompt, task_id, model=None):
    """Execute task via ollama with Hardware Guarding"""
    model = model or DEFAULT_MODEL
    log(f"Executing task {task_id} with {model}...")
    
    # HG: Check hardware safety before launch
    is_safe = check_hardware_safety()
    env = os.environ.copy()
    if not is_safe:
        log("HG: GPU instability detected. Forcing CPU-only execution.")
        env["OLLAMA_NUM_GPU"] = "0"
    
    # Use ollama run
    cmd = ["ollama", "run", model, prompt]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # Increased to 10 min for CPU mode
            env=env
        )
        
        output = result.stdout + result.stderr
        
        # Clean ANSI codes
        import re
        output = re.sub(r'\x1b\[[^m]*m', '', output)
        
        # Save result
        result_file = os.path.join(RESULTS_DIR, f"{task_id}_result.json")
        with open(result_file, "w") as f:
            json.dump({
                "task_id": task_id,
                "worker": WORKER_NAME,
                "model": model,
                "prompt": prompt,
                "output": output[:5000],
                "success": result.returncode == 0,
                "completed_at": datetime.now().isoformat()
            }, f, indent=2)
        
        log(f"Task {task_id} completed. Output: {len(output)} chars")
        return output
        
    except subprocess.TimeoutExpired:
        log(f"Task {task_id} TIMED OUT")
        return "TIMEOUT"
    except Exception as e:
        log(f"Task {task_id} FAILED: {e}")
        return f"ERROR: {e}"

def run_worker_loop():
    """Main worker loop - polls for tasks"""
    log("🤖 AETHEL_PI Worker started (using ollama cloud). Polling for tasks...")
    
    sys.path.insert(0, "/home/zixen15/aet_aeon")
    from task_queue import TaskQueue
    queue = TaskQueue()
    
    while True:
        pending = queue.get_pending("pi")
        
        if pending:
            task = pending[0]
            task_id = task["id"]
            queue.mark_running(task_id)
            
            # Get model from task metadata or use default
            model = task.get("model", DEFAULT_MODEL)
            result = execute_ollama_task(task["prompt"], task_id, model)
            queue.complete(task_id, result)
        else:
            time.sleep(5)  # Poll every 5 seconds

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        # Single task mode
        prompt = sys.argv[2] if len(sys.argv) > 2 else "Hello from AETHEL"
        model = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_MODEL
        execute_ollama_task(prompt, "manual", model)
    else:
        run_worker_loop()
