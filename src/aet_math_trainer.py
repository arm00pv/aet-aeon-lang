#!/usr/bin/env python3
"""AET-MathTrainer - Mathematical AI Training on MathNet"""

import json, subprocess
from pathlib import Path

ZIG = "/home/zixen15/zig-linux-x86_64-0.14.0/zig"
OUT = Path("/tmp/aet_compile")

# Working Zig template - fixed type errors
WORKING_ZIG = """const std = @import("std");
const math = std.math;

pub fn main() void {
    var prng = std.Random.DefaultPrng.init(42);
    const rng = prng.random();
    
    var geo: [2048]f64 = undefined;
    var ix: usize = 0;
    while (ix < 2048) : (ix += 1) {
        geo[ix] = rng.floatNorm(f64);
    }
    
    var wave: [1024]f64 = undefined;
    var iy: usize = 0;
    while (iy < 1024) : (iy += 1) {
        wave[iy] = rng.floatNorm(f64);
    }
    
    var m: [2048][2048]f64 = undefined;
    var ri: usize = 0;
    while (ri < 2048) : (ri += 1) {
        var ci: usize = 0;
        while (ci < 2048) : (ci += 1) {
            m[ri][ci] = rng.floatNorm(f64);
        }
    }
    
    var att: f64 = 0.0;
    var ai: usize = 0;
    while (ai < 2048) : (ai += 1) {
        att += m[0][ai] * m[ai % 1024][0];
    }
    
    var paths: [4][1024]f64 = undefined;
    var pi: usize = 0;
    while (pi < 4) : (pi += 1) {
        var pj: usize = 0;
        while (pj < 1024) : (pj += 1) {
            const val: f64 = switch (pi) {
                0 => 0.5, 1 => 1.0, 2 => 1.5, else => 2.0,
            };
            paths[pi][pj] = val;
        }
    }
    
    var best: usize = 0;
    var bv: f64 = math.floatMax(f64);
    pi = 0;
    while (pi < 4) : (pi += 1) {
        var mn: f64 = 0.0;
        var pj: usize = 0;
        while (pj < 1024) : (pj += 1) {
            mn += paths[pi][pj];
        }
        mn /= 1024.0;
        var vr: f64 = 0.0;
        pj = 0;
        while (pj < 1024) : (pj += 1) {
            const d = paths[pi][pj] - mn;
            vr += d * d;
        }
        vr /= 1024.0;
        if (vr < bv) {
            bv = vr;
            best = pi;
        }
    }
}
"""

def compile_aet():
    OUT.mkdir(exist_ok=True)
    (OUT/"main.zig").write_text(WORKING_ZIG)
    result = subprocess.run([ZIG, "build-exe", "main.zig", "-O", "ReleaseFast"], cwd=str(OUT), capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return OUT/"main"

def classify_topic(problem):
    topics = problem.get('topics_flat', [])
    return topics[0].split(' > ')[0] if topics else "Unknown"

def main():
    print("AET-MathTrainer")
    print("=" * 50)
    
    problems = []
    with open("/home/zixen15/hdd_data/AETHELOS_LAB/mathnet_all.jsonl") as f:
        for i, line in enumerate(f):
            if i >= 100: break
            problems.append(json.loads(line))
    print(f"Loaded {len(problems)} MathNet problems")
    
    topics = {}
    for p in problems:
        t = classify_topic(p)
        topics[t] = topics.get(t, 0) + 1
    print(f"Topics: {topics}")
    
    stats = {"total": 0, "compiled": 0, "executed": 0}
    topic_stats = {}
    
    print("\nTraining...")
    for p in problems:
        if stats["executed"] >= 10: break
        if not p.get('solutions_markdown'): continue
        
        topic = classify_topic(p)
        stats["total"] += 1
        if topic not in topic_stats:
            topic_stats[topic] = {"attempts": 0, "success": 0}
        topic_stats[topic]["attempts"] += 1
        
        binary = compile_aet()
        
        if binary and binary.exists():
            stats["compiled"] += 1
            r = subprocess.run([str(binary)])
            if r.returncode == 0:
                stats["executed"] += 1
                topic_stats[topic]["success"] += 1
        
        if stats["executed"] % 5 == 0 and stats["executed"] > 0:
            print(f"  Executed: {stats['executed']}/10")
    
    print(f"\nResults: {stats['executed']}/{stats['total']} successful")
    print(f"Compiled: {stats['compiled']}")
    print("\nBy topic:")
    for t, s in topic_stats.items():
        rate = (s['success'] / s['attempts'] * 100) if s['attempts'] > 0 else 0
        print(f"  {t}: {s['success']}/{s['attempts']} ({rate:.0f}%)")
    print("=" * 50)

if __name__ == "__main__":
    main()
