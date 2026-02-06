import taichi as ti
import numpy as np
import time
import argparse

# Initialize Taichi
# arch=ti.gpu will auto-select Vulkan or DirectX on Windows/AMD
ti.init(arch=ti.gpu)

# Benchmark Configuration
WIDTH = 4096
HEIGHT = 4096
MAX_ITER = 1000  # High iteration count makes it "Compute Bound"

# --- CPU Implementation (Using NumPy/Vectorized) ---
def benchmark_cpu():
    print(f"Running CPU Mandelbrot ({WIDTH}x{HEIGHT}, {MAX_ITER} iter)...")
    
    # Precompute grids
    x = np.linspace(-2.0, 1.0, WIDTH, dtype=np.float32)
    y = np.linspace(-1.5, 1.5, HEIGHT, dtype=np.float32)
    c = x + y[:, None] * 1j
    
    start = time.perf_counter()
    
    z = np.zeros_like(c)
    output = np.zeros(c.shape, dtype=np.int32)
    mask = np.full(c.shape, True, dtype=bool)

    # Note: This is an optimized vectorized NumPy approach
    # It's much faster than naive loops but still CPU bound.
    for i in range(MAX_ITER):
        z[mask] = z[mask] * z[mask] + c[mask]
        mask[np.abs(z) > 2.0] = False
        output[mask] = i
        if not np.any(mask):
            break
            
    end = time.perf_counter()
    elapsed = end - start
    print(f"  CPU Time: {elapsed:.4f}s")
    return elapsed

# --- GPU Implementation (Taichi) ---
@ti.kernel
def mandelbrot_kernel(pixels: ti.types.ndarray(dtype=ti.i32, ndim=2)):
    for i, j in pixels:
        c_re = -2.0 + (i / WIDTH) * 3.0
        c_im = -1.5 + (j / HEIGHT) * 3.0
        
        z_re = 0.0
        z_im = 0.0
        
        count = 0
        while z_re * z_re + z_im * z_im <= 4.0 and count < MAX_ITER:
            new_re = z_re * z_re - z_im * z_im + c_re
            new_im = 2.0 * z_re * z_im + c_im
            z_re = new_re
            z_im = new_im
            count += 1
        pixels[i, j] = count

def benchmark_gpu():
    print(f"Running GPU Mandelbrot (Taichi/Vulkan)...")
    pixels = np.zeros((WIDTH, HEIGHT), dtype=np.int32)
    
    # Warmup / Compilation
    mandelbrot_kernel(pixels)
    ti.sync()
    
    start = time.perf_counter()
    mandelbrot_kernel(pixels)
    ti.sync() # Wait for GPU to finish
    end = time.perf_counter()
    
    elapsed = end - start
    print(f"  GPU Time: {elapsed:.4f}s")
    return elapsed

def main():
    print(f"--- GPU vs CPU Benchmark: Mandelbrot Set ---")
    print(f"Resolution: {WIDTH}x{HEIGHT} | Max Iterations: {MAX_ITER}")
    print("-" * 50)
    
    # Run GPU first (usually faster to get it over with)
    t_gpu = benchmark_gpu()
    
    print("-" * 30)
    
    # Run CPU (Brace yourself, this will be slower)
    t_cpu = benchmark_cpu()
    
    print("=" * 50)
    if t_cpu > t_gpu:
        print(f"RESULT: GPU was {t_cpu / t_gpu:.2f}x FASTER than CPU")
    else:
        print(f"RESULT: CPU was {t_gpu / t_cpu:.2f}x FASTER than GPU")
        print("\nNote: On some systems, NumPy's vectorized CPU code is very efficient.")
        print("Try increasing MAX_ITER to 2000 or resolution to see GPU pull ahead.")
    print("=" * 50)

if __name__ == "__main__":
    main()

