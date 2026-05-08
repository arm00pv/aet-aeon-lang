#!/usr/bin/env python3
"""aetc - AET Compiler (AET → Zig → native binary)"""

import sys, re, subprocess
from pathlib import Path

ZIG = "/home/zixen15/zig-linux-x86_64-0.14.0/zig"
OUT = Path("/tmp/aet_compile")

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

        # State Assignment: name = State(dimensions=dims)
        m = re.match(r'(\w+)\s*=\s*State\(dimensions=(\d+).*?\)', l)
        if m: 
            ops.append({'type': 'state', 'name': m.group(1), 'dim': int(m.group(2))})
            continue
            
        # WaveState
        m = re.match(r'WaveState\((\d+)\)\s*→\s*(\w+)', l)
        if m:
            ops.append({'type': 'wavestate', 'name': m.group(2), 'dim': int(m.group(1))})
            continue

        m = re.match(r'(\w+)\s*=\s*WaveState\(.*?\)', l)
        if m:
            ops.append({'type': 'wavestate', 'name': m.group(1), 'dim': 1024})
            continue
            
        # Linear Transform @ and Composition >>
        # Pattern: in1 @ in2 >> Op1 >> Op2 ...
        if '@' in l or '>>' in l:
            parts = l.split('→')
            out_name = parts[1].strip() if len(parts) > 1 else None
            expr = parts[0].strip()
            
            # Simple handle for now
            ops.append({'type': 'expression', 'expr': expr, 'out': out_name})
            continue
            
        # Superposition ⊗
        if '⊗' in l:
            ops.append({'type': 'superposition', 'line': l})
            continue
            
        # Attention
        if 'Attention' in l:
            ops.append({'type': 'attention', 'line': l})
            continue
            
        # EntropyGate ⊕
        if '⊕' in l or 'EntropyGate' in l:
            ops.append({'type': 'entropy_gate', 'line': l})
            continue
            
    return ops

def gen(ops):
    z = """// AET → Zig (Generated)
const std = @import("std");
const math = std.math;

pub fn main() void {
    var prng = std.Random.DefaultPrng.init(42);
    const rng = prng.random();

"""
    dims = {}
    
    for op in ops:
        if op['type'] == 'state':
            name, d = op['name'], op['dim']
            dims[name] = d
            z += f"    // {name} = VectorState({d})\n"
            z += f"    var {name}: [{d}]f64 = undefined;\n"
            z += f"    for (0..{d}) |i| {name}[i] = rng.floatNorm(f64);\n\n"
        
        elif op['type'] == 'wavestate':
            name, d = op['name'], op.get('dim', 1024)
            dims[name] = d
            z += f"    // {name} = WaveState({d})\n"
            z += f"    var {name}_r: [{d}]f64 = undefined;\n"
            z += f"    var {name}_i: [{d}]f64 = undefined;\n"
            z += f"    for (0..{d}) |i| {{\n"
            z += f"        const p = @as(f64, @floatFromInt(i)) - @as(f64, @floatFromInt({d}))/2.0;\n"
            z += f"        {name}_r[i] = @exp(-p * p / 200.0);\n"
            z += f"        {name}_i[i] = p;\n"
            z += f"    }}\n\n"
            
        elif op['type'] == 'expression':
            expr, out = op['expr'], op['out']
            z += f"    // Expression: {expr} → {out or 'void'}\n"
            
            # Handle in @ mat >> Op1 >> Op2
            parts = expr.split('>>')
            first = parts[0].strip()
            
            if '@' in first:
                in_parts = first.split('@')
                in1 = in_parts[0].strip()
                in2 = in_parts[1].strip()
                d1 = dims.get(in1, 512)
                d2 = dims.get(in2, 512)
                out_d = d1 # Simplified assumption: square or compatible
                
                # If we have an output name, declare it
                if out:
                    dims[out] = out_d
                    z += f"    var {out}: [{out_d}]f64 = undefined;\n"
                    z += f"    for (0..{out_d}) |i| {{\n"
                    z += f"        var s: f64 = 0.0;\n"
                    z += f"        for (0..{d2}) |j| s += {in1}[j % {d1}] * {in2}[j];\n"
                    z += f"        {out}[i] = s;\n"
                    z += f"    }}\n"
                
                # Handle subsequent compositions (e.g. >> ReLU)
                current_var = out
                for i in range(1, len(parts)):
                    op_name = parts[i].strip()
                    if 'ReLU' in op_name and current_var:
                        z += f"    for (0..{dims[current_var]}) |idx| {{ if ({current_var}[idx] < 0) {current_var}[idx] = 0; }}\n"
                    elif 'LayerNorm' in op_name and current_var:
                        z += f"    {{\n"
                        z += f"        var sum: f64 = 0.0;\n"
                        z += f"        for (0..{dims[current_var]}) |idx| sum += {current_var}[idx];\n"
                        z += f"        const mean = sum / @as(f64, {dims[current_var]});\n"
                        z += f"        var var_sum: f64 = 0.0;\n"
                        z += f"        for (0..{dims[current_var]}) |idx| {{ const diff = {current_var}[idx] - mean; var_sum += diff * diff; }}\n"
                        z += f"        const std_dev = @sqrt(var_sum / @as(f64, {dims[current_var]}) + 1e-5);\n"
                        z += f"        for (0..{dims[current_var]}) |idx| {current_var}[idx] = ({current_var}[idx] - mean) / std_dev;\n"
                        z += f"    }}\n"
            z += "\n"

        elif op['type'] == 'superposition':
            z += f"    // Superposition: {op['line']}\n"
            z += f"    var paths: [4][1024]f64 = undefined;\n"
            z += f"    for (0..4) |pi| {{\n"
            z += f"        for (0..1024) |pj| {{\n"
            z += f"            paths[pi][pj] = @as(f64, @floatFromInt(pi)) + rng.floatNorm(f64);\n"
            z += f"        }}\n"
            z += f"    }}\n\n"

        elif op['type'] == 'attention':
            z += f"    // Attention: {op['line']}\n"
            z += f"    var att_out: f64 = 0.0;\n"
            z += f"    for (0..512) |_| att_out += rng.floatNorm(f64);\n\n"

        elif op['type'] == 'entropy_gate':
            z += f"    // EntropyGate: {op['line']}\n"
            z += f"    const best_path: usize = 0;\n"
            z += f"    _ = best_path;\n\n"

    z += "}\n"
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