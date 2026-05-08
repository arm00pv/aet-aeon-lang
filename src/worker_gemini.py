#!/usr/bin/env python3
"""
AET_AEON_WORKER_GEMINI.py - Gemini CLI Worker
=============================================
Executes tasks using gemini-cli (Google's AI CLI).
Uses NO_COLOR=1 for clean output.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

WORKER_NAME = "AEON_GEMINI"
LOG_DIR = "/home/zixen15/aet_aeon/logs"
RESULTS_DIR = "/home/zixen15/aet_aeon/results"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().isoformat()
    print(f"✨ [{WORKER_NAME}] {msg}")
    with open(os.path.join(LOG_DIR, f"{WORKER_NAME}.log"), "a") as f:
        f.write(f"[{ts}] {msg}\n")

def execute_gemini_task(prompt, task_id):
    """Execute task via gemini-cli"""
    log(f"Executing task {task_id} with gemini-cli...")
    
    cmd = [
        "bash", "-c",
        f"NO_COLOR=1 gemini -p '{prompt.replace("'", "'\"'\"'")}' -o json"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "NO_COLOR": "1"}
        )
        
        output = result.stdout + result.stderr
        
        # Try to parse JSON output
        try:
            parsed = json.loads(output)
            output_text = parsed.get("text", output)
        except:
            output_text = output
        
        # Save result
        result_file = os.path.join(RESULTS_DIR, f"{task_id}_result.json")
        with open(result_file, "w") as f:
            json.dump({
                "task_id": task_id,
                "worker": WORKER_NAME,
                "prompt": prompt,
                "output": output_text[:5000],  # Truncate if needed
                "success": result.returncode == 0,
                "completed_at": datetime.now().isoformat()
            }, f, indent=2)
        
        log(f"Task {task_id} completed. Output: {len(output_text)} chars")
        return output_text
        
    except subprocess.TimeoutExpired:
        log(f"Task {task_id} TIMED OUT")
        return "TIMEOUT"
    except Exception as e:
        log(f"Task {task_id} FAILED: {e}")
        return f"ERROR: {e}"

def run_worker_loop():
    """Main worker loop - polls for tasks"""
    log("✨ AEON_GEMINI Worker started. Polling for tasks...")
    
    sys.path.insert(0, "/home/zixen15/aet_aeon")
    from task_queue import TaskQueue
    queue = TaskQueue()
    
    while True:
        pending = queue.get_pending("gemini")
        
        if pending:
            task = pending[0]
            task_id = task["id"]
            queue.mark_running(task_id)
            result = execute_gemini_task(task["prompt"], task_id)
            queue.complete(task_id, result)
        else:
            time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        prompt = sys.argv[2] if len(sys.argv) > 2 else "Hello from AEON"
        execute_gemini_task(prompt, "manual")
    else:
        run_worker_loop()
