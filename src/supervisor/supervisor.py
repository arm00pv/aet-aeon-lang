#!/usr/bin/env python3
"""
AET_AEON_SUPERVISOR.py - Enhanced Orchestration Supervisor
========================================================
Supervises parallel AI work with intelligent model routing.
HALLOW prevention through model selection and code validation.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

WORKER_NAME = "AETHELOS_SUPERVISOR"
LOG_DIR = "/home/zixen15/aet_aeon/logs"
RESULTS_DIR = "/home/zixen15/aet_aeon/results"
TASKS_DIR = "/home/zixen15/aet_aeon/tasks"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

sys.path.insert(0, "/home/zixen15/aet_aeon")
from task_queue import TaskQueue
from model_router import ModelRouter, CodeValidator
from aeon_transpiler import AEONTranspiler

def log(msg):
    ts = datetime.now().isoformat()
    print(f"👑 [{WORKER_NAME}] {msg}")
    with open(os.path.join(LOG_DIR, "supervisor.log"), "a") as f:
        f.write(f"[{ts}] {msg}\n")

class AEONSupervisor:
    def __init__(self):
        self.queue = TaskQueue()
        self.router = ModelRouter()
        self.validator = CodeValidator()
        self.transpiler = AEONTranspiler()
        self.active_tasks = {}
        self.results_history = []
        self.hallucination_count = 0
        self.total_tasks = 0
        
    def dispatch_task(self, task_type, prompt, priority="high", model=None):
        """Dispatch task with intelligent routing"""
        self.total_tasks += 1
        
        # If no model specified, use router to select best model
        if not model and task_type == "pi":
            worker_type, selected_model, validation = self.router.route(prompt)
            task_id = self.queue.enqueue(worker_type, prompt, priority, selected_model)
            self.active_tasks[task_id] = {
                "type": worker_type,
                "prompt": prompt,
                "model": selected_model,
                "validation_required": validation,
                "dispatched_at": datetime.now().isoformat()
            }
            log(f"Dispatched task {task_id} (model: {selected_model}, validation: {validation})")
        else:
            task_id = self.queue.enqueue(task_type, prompt, priority, model)
            self.active_tasks[task_id] = {
                "type": task_type,
                "prompt": prompt,
                "model": model,
                "validation_required": True,
                "dispatched_at": datetime.now().isoformat()
            }
            log(f"Dispatched task {task_id}")
            
        return task_id
    
    def bulk_dispatch(self, tasks):
        """Dispatch multiple tasks with automatic model routing"""
        task_ids = []
        for task_type, prompt in tasks:
            tid = self.dispatch_task(task_type, prompt)
            task_ids.append(tid)
        log(f"Bulk dispatch complete: {len(task_ids)} tasks queued")
        return task_ids
    
    def get_result(self, task_id):
        """Retrieve result for completed task"""
        result_file = os.path.join(RESULTS_DIR, f"{task_id}_result.json")
        if os.path.exists(result_file):
            with open(result_file) as f:
                return json.load(f)
        return None
    
    def validate_output(self, result):
        """Validate worker output for hallucination and quality"""
        if not result:
            return {"valid": False, "reason": "no_result"}
        
        output = result.get("output", "")
        task_id = result.get("task_id", "unknown")
        model = result.get("model", "unknown")
        
        # Check if task failed
        if not result.get("success", False):
            return {
                "valid": False, 
                "reason": "task_failed",
                "action": "retry",
                "score": 0
            }
        
        # Check for error patterns in output
        error_patterns = [
            "Error:", "ERROR:", "error:",
            "Exception:", "EXCEPTION:",
            "Traceback", "panic!",
            "FAILED", "Failed to",
            "undefined", "undeclared"
        ]
        
        for pattern in error_patterns:
            if pattern in output:
                return {
                    "valid": False,
                    "reason": f"error_pattern: {pattern}",
                    "action": "retry",
                    "score": 0
                }
        
        # Check for code validation if validation_required
        task_info = self.active_tasks.get(task_id, {})
        if task_info.get("validation_required", True):
            # Validate as code if it looks like code
            if any(x in output for x in ["fn ", "pub fn", "def ", "function ", "const ", "let ", "//", "/*"]):
                validation = self.validator.validate(output)
                
                if not validation["valid"]:
                    self.hallucination_count += 1
                    return {
                        "valid": False,
                        "reason": "hallucination_detected",
                        "action": "retry_with_different_model",
                        "score": validation["score"],
                        "issues": validation["issues"]
                    }
                
                # Return validation with warnings
                return {
                    "valid": True,
                    "score": validation["score"],
                    "warnings": validation["warnings"],
                    "reason": "validated"
                }
        
        # Basic success
        if len(output) < 50 and not result.get("success"):
            return {
                "valid": False,
                "reason": "output_too_short",
                "action": "retry",
                "score": 10
            }
        
        return {
            "valid": True,
            "score": 100,
            "reason": "basic_validation_passed"
        }
    
    def review_and_correct(self, result):
        """Review worker output and apply corrections if needed"""
        validation = self.validate_output(result)
        
        if not validation["valid"]:
            action = validation.get("action", "none")
            reason = validation.get("reason", "unknown")
            
            if action == "retry":
                log(f"⚠️ Validation failed: {reason}. Will retry.")
                return {"needs_review": True, "action": "retry", "reason": reason}
            
            elif action == "retry_with_different_model":
                log(f"🚨 Hallucination detected: {reason}. Retrying with different model.")
                return {
                    "needs_review": True, 
                    "action": "retry_different_model", 
                    "reason": reason,
                    "issues": validation.get("issues", [])
                }
        
        return {"needs_review": False, "action": "none"}
    
    def transpile_aet(self, aet_code, target="zig"):
        """Transpile AET code to target language"""
        try:
            return self.transpiler.transpile(aet_code, target)
        except Exception as e:
            log(f"Transpilation error: {e}")
            return f"// Error: {e}"
    
    def status_report(self):
        """Generate comprehensive status report"""
        queue_status = self.queue.status()
        
        # Calculate hallucination rate
        halluc_rate = (self.hallucination_count / max(1, self.total_tasks)) * 100
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "queue": queue_status,
            "active_tasks": len(self.active_tasks),
            "history_size": len(self.results_history),
            "hallucination_stats": {
                "detected": self.hallucination_count,
                "total_tasks": self.total_tasks,
                "rate": f"{halluc_rate:.1f}%"
            }
        }
        
        log(f"Status: {queue_status} | Hallucination rate: {halluc_rate:.1f}%")
        return report
    
    def run_project(self, project_prompt):
        """Execute a full project with both workers and validation"""
        log(f"🎯 Starting project: {project_prompt[:80]}...")
        
        # Break project into parallel sub-tasks
        planning_task = ("pi", f"Break this task into 3-5 parallel subtasks with specific code requirements: {project_prompt}")
        research_task = ("gemini", f"Research technical requirements for: {project_prompt}")
        
        task_ids = self.bulk_dispatch([planning_task, research_task])
        
        # Wait for completion with timeout
        timeout = 300
        start = time.time()
        results = []
        
        while time.time() - start < timeout:
            results = [self.get_result(tid) for tid in task_ids if self.get_result(tid)]
            if len(results) >= 2:  # Both completed
                break
            time.sleep(5)
        
        # Validate results
        validated_results = []
        for tid, res in zip(task_ids, results):
            if res:
                validation = self.review_and_correct(res)
                validated_results.append({
                    "task_id": tid,
                    "result": res,
                    "validation": validation
                })
        
        # Compile results
        compiled = {
            "project": project_prompt,
            "subtask_results": validated_results,
            "compiled_at": datetime.now().isoformat()
        }
        
        return compiled
    
    def execute_with_retry(self, task_type, prompt, max_retries=3):
        """Execute task with automatic retry on hallucination"""
        for attempt in range(max_retries):
            task_id = self.dispatch_task(task_type, prompt)
            
            # Wait for result
            timeout = 180
            start = time.time()
            result = None
            
            while time.time() - start < timeout:
                result = self.get_result(task_id)
                if result:
                    break
                time.sleep(2)
            
            if result:
                validation = self.review_and_correct(result)
                
                if not validation["needs_review"]:
                    log(f"✅ Task {task_id} succeeded on attempt {attempt + 1}")
                    return result
                
                if attempt < max_retries - 1:
                    log(f"🔄 Retrying task {task_id} (attempt {attempt + 2}/{max_retries})")
                    # Try different model on retry
                    if validation["action"] == "retry_different_model":
                        # Router will select different model
                        pass
            else:
                log(f"❌ Task {task_id} timed out")
        
        log(f"🚨 Task failed after {max_retries} attempts")
        return None

if __name__ == "__main__":
    supervisor = AEONSupervisor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            print(json.dumps(supervisor.status_report(), indent=2))
        elif sys.argv[1] == "--project":
            project = " ".join(sys.argv[2:])
            result = supervisor.run_project(project)
            print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
        elif sys.argv[1] == "--dispatch":
            worker_type = sys.argv[2] if len(sys.argv) > 2 else "pi"
            prompt = " ".join(sys.argv[3:])
            tid = supervisor.dispatch_task(worker_type, prompt)
            print(f"Task {tid} dispatched")
        elif sys.argv[1] == "--transpile":
            if len(sys.argv) > 3:
                code = " ".join(sys.argv[2:-1])
                target = sys.argv[-1]
                print(supervisor.transpile_aet(code, target))
            else:
                print("Usage: --transpile <aet_code> <target_language>")
    else:
        log("👑 AETHELOS_SUPERVISOR initialized with hallucination prevention.")
        print("Usage:")
        print("  --status           Show queue and hallucination stats")
        print("  --project <task>   Run full project")
        print("  --dispatch <type> <prompt>  Dispatch single task")
        print("  --transpile <code> <target> Transpile AET to language")
