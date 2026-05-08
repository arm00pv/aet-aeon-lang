#!/usr/bin/env python3
"""AET-MathTrainer - Mathematical AI Training on MathNet"""

import json, subprocess, sys
from pathlib import Path

# Add src to path if needed
sys.path.insert(0, str(Path(__file__).parent))
import aetc
from aet_reasoner import AETReasoner

def compile_aet(aet_code: str):
    binary = aetc.compile(aet_code)
    return binary

def classify_topic(problem):
    topics = problem.get('topics_flat', [])
    return topics[0].split(' > ')[0] if topics else "Unknown"

def main():
    print("AET-MathTrainer (Real Compiler Integration)")
    print("=" * 50)
    
    problems = []
    # Using relative path or checking if file exists
    math_path = Path("/home/zixen15/hdd_data/AETHELOS_LAB/mathnet_all.jsonl")
    if not math_path.exists():
        print(f"Error: MathNet data not found at {math_path}")
        return

    with open(math_path) as f:
        for i, line in enumerate(f):
            if i >= 100: break
            problems.append(json.loads(line))
    print(f"Loaded {len(problems)} MathNet problems")
    
    reasoner = AETReasoner()
    stats = {"total": 0, "compiled": 0, "executed": 0}
    topic_stats = {}
    
    print("\nTraining...")
    for p in problems:
        if stats["executed"] >= 5: break # Reduced for demo
        if not p.get('solutions_markdown'): continue
        
        problem_text = p.get('problem_markdown', "")
        topic = classify_topic(p)
        stats["total"] += 1
        if topic not in topic_stats:
            topic_stats[topic] = {"attempts": 0, "success": 0}
        topic_stats[topic]["attempts"] += 1
        
        # 1. Generate AET code for the problem
        aet_code = reasoner.generate_aet(problem_text, expected_answer_type=topic)
        
        # 2. Compile AET to native binary
        binary = compile_aet(aet_code)
        
        if binary and binary.exists():
            stats["compiled"] += 1
            # 3. Execute binary
            r = subprocess.run([str(binary)])
            if r.returncode == 0:
                stats["executed"] += 1
                topic_stats[topic]["success"] += 1
        
        print(f"  [{topic}] {problem_text[:50]}... -> {'SUCCESS' if binary else 'FAIL'}")
    
    print(f"\nResults: {stats['executed']}/{stats['total']} successful")
    print(f"Compiled: {stats['compiled']}")
    print("\nBy topic:")
    for t, s in topic_stats.items():
        rate = (s['success'] / s['attempts'] * 100) if s['attempts'] > 0 else 0
        print(f"  {t}: {s['success']}/{s['attempts']} ({rate:.0f}%)")
    print("=" * 50)

if __name__ == "__main__":
    main()
