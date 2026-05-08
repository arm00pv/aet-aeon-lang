#!/usr/bin/env python3
"""
AET_AEON_ORCHESTRATOR.py - Main Orchestration Entry Point
========================================================
Dual-brain architecture with intelligent model routing and hallucination prevention.
Ollama Cloud models + Gemini CLI. One does the work, one supervises and corrects.
"""

import os
import sys
import json
import subprocess

sys.path.insert(0, "/home/zixen15/aet_aeon")

from supervisor.supervisor import AEONSupervisor
from task_queue import TaskQueue
from model_router import ModelRouter, route_task
from aeon_transpiler import transpile

def banner():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║    🔱 AETHELOS ENGINE (AET) + AEON DUAL-BRAIN SYSTEM 🔱    ║
    ║─────────────────────────────────────────────────────────────║
    ║  Ollama Cloud    ← Primary execution (smart model routing) ║
    ║  Gemini CLI     ← Parallel research/verification            ║
    ║  Supervisor     ← I'm the architect, I correct & validate   ║
    ║─────────────────────────────────────────────────────────────║
    ║  HALLUCINATION PREVENTION: Model selection + code validation║
    ╚═══════════════════════════════════════════════════════════╝
    """)

def start_workers():
    """Start both workers in background"""
    print("🚀 Starting worker processes...")
    
    subprocess.Popen([
        sys.executable, 
        "/home/zixen15/aet_aeon/workers/worker_pi.py"
    ], stdout=open("/home/zixen15/aet_aeon/logs/worker_pi_stdout.log", "a"),
       stderr=subprocess.STDOUT)
    
    subprocess.Popen([
        sys.executable,
        "/home/zixen15/aet_aeon/workers/worker_gemini.py"
    ], stdout=open("/home/zixen15/aet_aeon/logs/worker_gemini_stdout.log", "a"),
       stderr=subprocess.STDOUT)
    
    print("✅ Workers started. Use --supervisor to interact.")

def list_models():
    """List available models"""
    print("\n📋 AVAILABLE MODELS (via Ollama)")
    print("-" * 50)
    import subprocess
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    for line in result.stdout.split("\n"):
        if ":cloud" in line or "SIZE" in line:
            status = "✅" if "9." in line or "2." in line or "phi4" in line else "🌐"
            print(f"  {status} {line}")
    print()

if __name__ == "__main__":
    banner()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 orchestrator.py start        - Start workers")
        print("  python3 orchestrator.py dispatch     - Dispatch tasks")
        print("  python3 orchestrator.py status      - Show status")
        print("  python3 orchestrator.py models      - List available models")
        print("  python3 orchestrator.py project     - Run full project")
        print("  python3 orchestrator.py parallel    - Run parallel tasks")
        print("  python3 orchestrator.py transpile   - Transpile AET code")
        print("  python3 orchestrator.py route      - Test model routing")
        sys.exit(1)
    
    cmd = sys.argv[1]
    supervisor = AEONSupervisor()
    
    if cmd == "start":
        start_workers()
        
    elif cmd == "dispatch":
        if len(sys.argv) > 2:
            worker = sys.argv[2]
            prompt = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else input("Task: ")
            tid = supervisor.dispatch_task(worker, prompt)
            print(f"📋 Task {tid} dispatched")
        else:
            print("Usage: dispatch <pi|gemini> <prompt>")
            
    elif cmd == "status":
        print(json.dumps(supervisor.status_report(), indent=2))
        
    elif cmd == "models":
        list_models()
        
    elif cmd == "project":
        if len(sys.argv) < 3:
            print("Usage: project <task_description>")
            sys.exit(1)
        project = " ".join(sys.argv[2:])
        result = supervisor.run_project(project)
        print(json.dumps(result, indent=2, ensure_ascii=False)[:3000])
        
    elif cmd == "parallel":
        # Example: parallel execution of research tasks
        supervisor = AEONSupervisor()
        tasks = [
            ("gemini", "Research latest SWE-RL techniques 2026"),
            ("pi", "Write Zig implementation of QSS wave logic"),
            ("gemini", "Compare transformer vs recurrent architectures"),
            ("pi", "Audit existing AETHEL code for optimization opportunities")
        ]
        tids = supervisor.bulk_dispatch(tasks)
        print(f"📋 Dispatched {len(tids)} parallel tasks: {tids}")
        
    elif cmd == "transpile":
        if len(sys.argv) > 3:
            code = sys.argv[2]
            target = sys.argv[3]
            print(transpile(code, target))
        else:
            print("Usage: transpile <aet_code> <target_language>")
            print("Example: transpile 'state = State(dimensions=4096)' zig")
            
    elif cmd == "route":
        # Test model routing
        if len(sys.argv) > 2:
            prompt = " ".join(sys.argv[2:])
        else:
            prompt = "Write a Zig function for matrix multiplication"
        
        worker, model, validation = route_task(prompt)
        print(f"\n🧭 ROUTING TEST")
        print(f"Prompt: '{prompt}'")
        print(f"  → Worker: {worker}")
        print(f"  → Model: {model}")
        print(f"  → Validation: {validation}")
