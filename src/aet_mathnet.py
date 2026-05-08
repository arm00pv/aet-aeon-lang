#!/usr/bin/env python3
"""
AET-MathNet Training System
===========================
Train AET models on MathNet competition problems.

MathNet contains:
- 7,492 mathematical competition problems
- Solutions with LaTeX
- Topics: Geometry, Combinatorics, Algebra, Number Theory, etc.
- Multiple image attachments per problem

This creates an AET training corpus for AI mathematical reasoning.
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

MATHNET_JSONL = Path("/home/zixen15/hdd_data/AETHELOS_LAB/mathnet_all.jsonl")
MATHNET_IMAGES = Path("/home/zixen15/hdd_data/AETHELOS_LAB/mathnet_images")

@dataclass
class MathProblem:
    id: str
    competition: str
    country: str
    topic: str
    problem_type: str
    problem_text: str
    solutions: List[str]
    final_answer: Optional[str]
    image_files: List[str]

def load_mathnet() -> List[MathProblem]:
    """Load MathNet dataset"""
    problems = []
    with open(MATHNET_JSONL, 'r') as f:
        for line in f:
            data = json.loads(line)
            topics = data.get('topics_flat', [])
            topic = topics[0] if topics else "Unknown"
            problems.append(MathProblem(
                id=data['id'],
                competition=data['competition'],
                country=data.get('country', 'Unknown'),
                topic=topic,
                problem_type=data['problem_type'],
                problem_text=data['problem_markdown'],
                solutions=data['solutions_markdown'] or [],
                final_answer=data.get('final_answer'),
                image_files=data.get('image_files', [])
            ))
    return problems

def problem_to_aet(problem: MathProblem) -> str:
    """Convert MathNet problem to AET format"""
    # AET state for mathematical reasoning
    aet = f"""// MathNet Problem: {problem.id}
@Competition: {problem.competition}
@Topic: {problem.topic}

// State space for mathematical reasoning
State(4096) → reasoning_space
WaveState(2048) → solution_wave

// Problem: {problem.problem_text[:200]}...

// Apply reasoning transform
reasoning_space @ W_initial >> LayerNorm

// Attention over solution candidates
Attention(query=reasoning_space, memory=solution_wave)

// Entropy gate to collapse to correct solution
⊕EntropyGate(threshold=0.3)

// Answer: {problem.final_answer or "TBD"}
"""
    return aet

def generate_training_corpus():
    """Generate AET training data from MathNet"""
    print("Loading MathNet...")
    problems = load_mathnet()
    print(f"Loaded {len(problems)} problems")
    
    # Group by topic
    topics = {}
    for p in problems:
        topic = p.topic.split(" > ")[0]
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(p)
    
    print("\nProblems by topic:")
    for topic, probs in sorted(topics.items(), key=lambda x: -len(x[1])):
        print(f"  {topic}: {len(probs)}")
    
    # Generate AET versions
    corpus_dir = Path("/home/zixen15/aet-aeon-lang/training/mathnet")
    corpus_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nGenerating AET training corpus at {corpus_dir}...")
    for i, problem in enumerate(problems[:100]):  # First 100 as sample
        aet_code = problem_to_aet(problem)
        out_file = corpus_dir / f"{problem.id}.aet"
        out_file.write_text(aet_code)
        if (i + 1) % 20 == 0:
            print(f"  Processed {i+1}/{min(100, len(problems))}")
    
    print(f"\nAET corpus generated: {corpus_dir}")
    return corpus_dir

# AET-QSS Integration
# The QSS (Quantum State Space) model maps mathematical concepts to AET operations
QSS_TOPIC_MAP = {
    "Geometry": {
        "state_dim": 2048,
        "wave_freq": 1.0,
        "attention_heads": 8,
        "operations": ["rotate", "reflect", "project", "distance"]
    },
    "Discrete Mathematics": {
        "state_dim": 4096,
        "wave_freq": 0.5,
        "attention_heads": 16,
        "operations": ["count", "color", "partition", "match"]
    },
    "Algebra": {
        "state_dim": 1024,
        "wave_freq": 0.8,
        "attention_heads": 4,
        "operations": ["solve", "factor", "simplify", "substitute"]
    },
    "Number Theory": {
        "state_dim": 512,
        "wave_freq": 2.0,
        "attention_heads": 2,
        "operations": ["modular", "divisibility", "prime", "congruence"]
    }
}

def aet_for_topic(topic: str) -> str:
    """Generate AET code for a specific topic"""
    for key, params in QSS_TOPIC_MAP.items():
        if key in topic:
            return f"""
State({params['state_dim']}) → math_state
WaveState({params['state_dim']//2}) → wave
@ W_{key.lower().replace(' ', '_')}
Attention(query=math_state, memory=wave)
⊕EntropyGate(threshold=0.4)
"""
    return "State(2048) → default_state"

def demo():
    print("AET-MathNet Training System")
    print("=" * 50)
    print()
    
    # Load and analyze
    problems = load_mathnet()
    print(f"MathNet contains {len(problems)} problems")
    print()
    
    # Show sample
    if problems:
        p = problems[0]
        print(f"Sample: {p.id}")
        print(f"  Competition: {p.competition}")
        print(f"  Topic: {p.topic}")
        print(f"  Type: {p.problem_type}")
        print(f"  Images: {len(p.image_files)}")
        print(f"  Solution length: {len(p.solutions[0]) if p.solutions else 0} chars")
    
    print()
    print("Generating training corpus...")
    corpus_dir = generate_training_corpus()
    
    print()
    print("=" * 50)
    print("AET-QSS Topic Parameters:")
    for topic, params in QSS_TOPIC_MAP.items():
        print(f"  {topic}: dim={params['state_dim']}, heads={params['attention_heads']}")

if __name__ == "__main__":
    demo()