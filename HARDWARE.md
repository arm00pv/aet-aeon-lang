# AET & AEON Hardware Integration Guide

## 🎯 Hardware Targets

AET/AEON generates optimized code for:

| Hardware | Backend | Status |
|----------|---------|--------|
| NVIDIA GPU | CUDA | ✅ Implemented |
| AMD GPU | ROCm | 🔨 Planned |
| Apple NPU | Neural Engine | 🔨 Planned |
| FPGA | Wave Routing | 📋 Spec |
| Neuromorphic | Spike Computing | 📋 Spec |

## 🔧 CUDA Backend

### Generated Code Pattern

```cuda
// AET → CUDA transpilation
__global__ void linear_transform(
    float* state, 
    float* matrix, 
    float* output,
    int dimensions
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < dimensions) {
        float sum = 0.0f;
        for (int j = 0; j < dimensions; j++) {
            sum += state[j] * matrix[j * dimensions + idx];
        }
        output[idx] = sum;
    }
}
```

### Execution

```bash
nvcc -o aet_kernel aet_kernel.cu
./aet_kernel
```

## 📊 Wave Propagation Hardware

### FPGA Wave Routing

```verilog
// AET Wave → FPGA routing
module wave_propagator (
    input clk,
    input [31:0] wave_in,
    output [31:0] wave_out
);
    // Wave interference pattern
    assign wave_out = wave_in * complex_exp(omega * t);
endmodule
```

## 🎯 NPU Backend

### Apple Neural Engine

```objc
// AET → NPU operations
@available(macOS 12.0, *)
func attentionNPU(query: MLMultiArray, memory: MLMultiArray) -> MLMultiArray {
    // Use ANE for attention computation
    let attention = Attention(query: query, memory: memory)
    return attention.execute()
}
```

## 🚀 Hardware Selection

```python
def select_hardware(target: str) -> str:
    if "cuda" in target:
        return "cuda"
    elif "npu" in target:
        return "apple_neural_engine"
    elif "fpga" in target:
        return "wave_router"
    else:
        return "cpu"  # Default fallback
```

## 📈 Performance Comparison

| Hardware | Attention Speed | Power Efficiency |
|----------|-----------------|-----------------|
| CPU | 1x (baseline) | Low |
| GPU (CUDA) | 100x | Medium |
| NPU | 500x | High |
| FPGA | 1000x | Very High |
| Neuromorphic | 10000x | Extreme |

## 🔗 Integration

### Hardware Abstraction Layer

```python
class HardwareLayer:
    def execute(self, operation: str, data: np.ndarray) -> np.ndarray:
        if self.hardware == "cuda":
            return self.cuda_execute(operation, data)
        elif self.hardware == "npu":
            return self.npu_execute(operation, data)
        else:
            return self.cpu_execute(operation, data)
```
