#!/usr/bin/env python3
"""aetc - AET Compiler (AET → Zig → native binary)"""

import sys, re, subprocess
from pathlib import Path

ZIG = "/home/zixen15/zig-linux-x86_64-0.14.0/zig"
OUT = Path("/tmp/aet_compile")

def parse(src):
    ops = []
    for line in src.strip().split('\n'):
        l = line.split('//')[0].strip()
        if not l: continue
        m = re.match(r'State\((\d+)\)\s*→\s*(\w+)', l)
        if m: ops.append(('s', int(m.group(1)), m.group(2)))
    return ops

def gen(ops):
    states = [(d,n) for o in ops if o[0]=='s' for d,n in [(o[1],o[2])]]
    md = max((d for d,_ in states), default=512)
    
    z = """// AET → Zig (Generated)
const std = @import("std");
const math = std.math;

pub fn main() void {
    var prng = std.Random.DefaultPrng.init(42);
    const rng = prng.random();
"""
    for d,n in states:
        z += f"    // {n} = VectorState({d})\n"
        z += f"    var {n}: [{d}]f64 = undefined;\n"
        z += f"    var i: usize = 0;\n"
        z += f"    while (i < {d}) : (i += 1) {n}[i] = rng.floatNorm(f64);\n\n"
    
    z += f"""    // @ Linear Transform
    var m: [{md}][{md}]f64 = undefined;
    var row: usize = 0;
    while (row < {md}) : (row += 1) {{
        var col: usize = 0;
        while (col < {md}) : (col += 1) m[row][col] = rng.floatNorm(f64);
    }}

    // WaveState
    var wr: [1024]f64 = undefined;
    var wi: [1024]f64 = undefined;
    var wi_idx: usize = 0;
    while (wi_idx < 1024) : (wi_idx += 1) {{
        const px = @as(f64, @floatFromInt(wi_idx)) - 512.0;
        wr[wi_idx] = @exp(-px * px / 200.0);
        wi[wi_idx] = px;
    }}

    // Attention
    var att: f64 = 0.0;
    var att_idx: usize = 0;
    while (att_idx < {md}) : (att_idx += 1) att += m[0][att_idx] * wr[att_idx % 1024];
    att /= @sqrt(@as(f64, {md}));

    // ⊗ Superposition + ⊕ EntropyGate
    var paths: [4][1024]f64 = undefined;
    var pi: usize = 0;
    while (pi < 4) : (pi += 1) {{
        const v: f64 = switch (pi) {{
            0 => 0.5, 1 => 1.0, 2 => 1.5, else => 2.0,
        }};
        var pj: usize = 0;
        while (pj < 1024) : (pj += 1) paths[pi][pj] = v;
    }}
    var best: usize = 0;
    var bv: f64 = math.floatMax(f64);
    pi = 0;
    while (pi < 4) : (pi += 1) {{
        var mn: f64 = 0.0;
        var pj: usize = 0;
        while (pj < 1024) : (pj += 1) mn += paths[pi][pj];
        mn /= 1024.0;
        var vr: f64 = 0.0;
        pj = 0;
        while (pj < 1024) : (pj += 1) {{
            const d = paths[pi][pj] - mn;
            vr += d * d;
        }}
        vr /= 1024.0;
        if (vr < bv) {{ bv = vr; best = pi; }}
    }}
}}
"""
    return z

def compile(src, emit=False):
    ops = parse(src)
    zig = gen(ops)
    if emit:
        print(zig); return None
        
    OUT.mkdir(exist_ok=True)
    f = OUT/"main.zig"
    f.write_text(zig)
    
    # Compile from the OUT directory so binary is created there
    r = subprocess.run(
        [ZIG, "build-exe", "main.zig", "-O", "ReleaseFast"],
        cwd=str(OUT),
        capture_output=True,
        text=True
    )
    if r.returncode:
        print(f"Error:\n{r.stderr}"); return None
    return OUT/"main"

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Usage: aetc.py <file.aet> [--emit|--build]")
        sys.exit(1)
    src = Path(sys.argv[1]).read_text()
    b = compile(src, '--emit' in sys.argv)
    if b and b.exists():
        print(f"Binary: {b}")
        if '--build' not in sys.argv and '--emit' not in sys.argv:
            r = subprocess.run([str(b)])
            print(f"Exit: {r.returncode}")