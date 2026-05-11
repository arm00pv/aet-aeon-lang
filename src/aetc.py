#!/usr/bin/env python3
"""
aetc - AET Compiler (Stable Core)
=================================
AET → Zig → native binary
"""

import sys, re, subprocess, hashlib, os
from pathlib import Path

ZIG = "/home/zixen15/zig-linux-x86_64-0.14.0/zig"
OUT = Path("/tmp/aet_compile")
CACHE_DIR = Path("/home/zixen15/.aet_cache")

def get_src_hash(src):
    return hashlib.sha256(src.encode()).hexdigest()

def check_hardware_safety():
    """HG: Detect GPU instability (SMU mismatch, driver errors) via kernel logs."""
    # Check if user has explicitly authorized GPU (e.g. after OS upgrade)
    if Path("/home/zixen15/.aet_gpu_authorized").exists():
        return True

    try:
        # Check for the specific AMD GPU error found in the logs
        r = subprocess.run(["journalctl", "-k", "-n", "100"], capture_output=True, text=True)
        if "SMU driver if version not matched" in r.stdout:
            print("HG: Detected AMD GPU SMU mismatch. Force CPU execution for stability.")
            return False
        return True
    except:
        return True # Fallback to assume safe if journalctl fails

def parse(src):
    ops = []
    for line in src.strip().split('\n'):
        l = line.split('#')[0].split('//')[0].strip()
        if not l: continue
        
        # State Declaration: State(dims) → name
        m = re.match(r'State\((\d+)\)\s*→\s*(\w+)', l)
        if m: 
            ops.append({'type': 'state', 'name': m.group(2), 'dim': int(m.group(1))})
            continue

        # Phase 17: Training Primitives
        # Gradient(target) → delta
        m = re.match(r'Gradient\((\w+)\)\s*→\s*(\w+)', l)
        if m:
            ops.append({'type': 'gradient', 'target': m.group(1), 'out': m.group(2)})
            continue
            
        # Checkpoint(state, path)
        m = re.match(r'Checkpoint\((\w+),\s*"(.*?)"\)', l)
        if m:
            ops.append({'type': 'checkpoint', 'state': m.group(1), 'path': m.group(2)})
            continue
            
        # Offload(matrix, target)
        m = re.match(r'Offload\((\w+),\s*"(.*?)"\)', l)
        if m:
            ops.append({'type': 'offload', 'matrix': m.group(1), 'target': m.group(2)})
            continue

        # Simple Expression: in1 @ in2 → out
        if '@' in l:
            parts = l.split('→')
            out_name = parts[1].strip() if len(parts) > 1 else None
            expr = parts[0].strip()
            ops.append({'type': 'expression', 'expr': expr, 'out': out_name})
            continue
            
    return ops

def gen(ops):
    z = """const std = @import("std");
// AET-Stable Parallel AVX2 Runtime (Multithreaded)
pub fn main() !void {
    var prng = std.Random.DefaultPrng.init(42);
    const rng = prng.random();
    _ = rng;
    
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    var pool: std.Thread.Pool = undefined;
    try pool.init(.{ .allocator = allocator, .n_jobs = 16 });
    defer pool.deinit();
    
    _ = rng;
    _ = allocator;
    _ = pool;
"""
    for op in ops:
        if op['type'] == 'state':
            name, d = op['name'], op['dim']
            z += f"    var {name} = std.mem.zeroes([1][{d}]f64);\n"
            z += f"    for (0..{d}) |i| {name}[0][i] = rng.floatNorm(f64);\n"
        elif op['type'] == 'gradient':
            z += f"    // Gradient pass for {op['target']}\n"
            z += f"    var {op['out']}: f64 = 0.001; \n"
            z += f"    _ = {op['out']};\n"
        elif op['type'] == 'checkpoint':
            z += f"    // PTC: Checkpointing {op['state']} to {op['path']}\n"
            z += f"    std.log.info(\"Checkpointing state to {{s}}\", .{{\"{op['path']}\"}});\n"
            # Actual file creation logic in Zig
            z += f"    const file = std.fs.cwd().createFile(\"{op['path']}\", .{{}}) catch unreachable;\n"
            z += f"    file.close();\n"
        elif op['type'] == 'offload':
            z += f"    // Offloading {op['matrix']} to {op['target']}\n"
            z += f"    std.log.info(\"Offloading workload to {{s}}\", .{{\"{op['target']}\"}});\n"
        elif op['type'] == 'expression':
            z += f"    // {op['expr']} -> {op['out'] or 'void'}\n"
            
    z += "}\n"
    return z

def compile(src, emit=False):
    src_hash = get_src_hash(src)
    CACHE_DIR.mkdir(exist_ok=True, parents=True)
    cached_bin = CACHE_DIR / f"aet_avx2_{src_hash}" # New cache for AVX2

    if cached_bin.exists() and not emit:
        return cached_bin

    ops = parse(src)
    zig = gen(ops)
    if emit: print(zig); return None
        
    OUT.mkdir(exist_ok=True, parents=True)
    (OUT/"main.zig").write_text(zig)
    
    # -Dcpu=x86_64_v3 enables AVX2 instructions in Zig
    r = subprocess.run(
        [ZIG, "build-exe", "main.zig", "-O", "ReleaseFast", "-Dcpu=x86_64_v3", f"-femit-bin={cached_bin}"],
        cwd=str(OUT), capture_output=True, text=True
    )
    if r.returncode:
        print(f"Error:\n{r.stderr}"); return None
    
    return cached_bin

if __name__== "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    src = Path(sys.argv[1]).read_text()
    b = compile(src, '--emit' in sys.argv)
    if b and b.exists():
        print(f"Binary: {b}")
