#!/usr/bin/env python3
"""
AET_AEON_TASK_QUEUE.py - Task Distribution Hub
==============================================
Distributes tasks to AI workers (ollama cloud + gemini) and tracks results.
"""

import os
import json
import time
import uuid
from datetime import datetime

QUEUE_DIR = "/home/zixen15/aet_aeon/tasks"
RESULTS_DIR = "/home/zixen15/aet_aeon/results"

def ensure_dirs():
    os.makedirs(QUEUE_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

class TaskQueue:
    def __init__(self):
        ensure_dirs()
        self.pending_file = os.path.join(QUEUE_DIR, "pending.jsonl")
        self.running_file = os.path.join(QUEUE_DIR, "running.jsonl")
        self.completed_file = os.path.join(RESULTS_DIR, "completed.jsonl")
        
    def enqueue(self, task_type, prompt, priority="normal", model=None):
        """Add task to queue
        
        Args:
            task_type: "pi" for ollama cloud, "gemini" for gemini-cli
            prompt: The task prompt
            priority: "high", "normal", "low"
            model: Optional model override for pi tasks (e.g., "deepseek-v4-pro:cloud")
        """
        task = {
            "id": str(uuid.uuid4())[:8],
            "type": task_type,
            "prompt": prompt,
            "priority": priority,
            "model": model,  # For pi tasks - specify which cloud model
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        with open(self.pending_file, "a") as f:
            f.write(json.dumps(task) + "\n")
        model_info = f" (model: {model})" if model else ""
        print(f"📋 [QUEUE] Task {task['id']} queued: {task_type}{model_info} | {prompt[:80]}...")
        return task["id"]
    
    def get_pending(self, worker_type):
        """Get next pending task for worker"""
        pending = []
        if os.path.exists(self.pending_file):
            with open(self.pending_file, "r") as f:
                for line in f:
                    try:
                        task = json.loads(line)
                        if task["type"] == worker_type and task["status"] == "pending":
                            pending.append(task)
                    except:
                        continue
        return pending
    
    def mark_running(self, task_id):
        """Move task to running"""
        tasks = []
        if os.path.exists(self.pending_file):
            with open(self.pending_file, "r") as f:
                tasks = [json.loads(l) for l in f]
        
        updated = []
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = "running"
                t["started_at"] = datetime.now().isoformat()
                with open(self.running_file, "a") as f:
                    f.write(json.dumps(t) + "\n")
            else:
                updated.append(t)
        
        with open(self.pending_file, "w") as f:
            for t in updated:
                f.write(json.dumps(t) + "\n")
    
    def complete(self, task_id, result):
        """Mark task completed with result"""
        tasks = []
        if os.path.exists(self.running_file):
            with open(self.running_file, "r") as f:
                tasks = [json.loads(l) for l in f]
        
        with open(self.completed_file, "a") as f:
            for t in tasks:
                if t["id"] == task_id:
                    t["status"] = "completed"
                    t["completed_at"] = datetime.now().isoformat()
                    t["result"] = result
                    f.write(json.dumps(t) + "\n")
        
        # Remove from running
        remaining = [t for t in tasks if t["id"] != task_id]
        with open(self.running_file, "w") as f:
            for t in remaining:
                f.write(json.dumps(t) + "\n")
    
    def status(self):
        """Get queue status"""
        def count(f):
            if not os.path.exists(f): return 0
            with open(f) as file: return sum(1 for _ in file)
        return {
            "pending": count(self.pending_file),
            "running": count(self.running_file),
            "completed": count(self.completed_file)
        }

if __name__ == "__main__":
    q = TaskQueue()
    print("🔮 AET/AEON Task Queue Active")
    print(f"Status: {q.status()}")
