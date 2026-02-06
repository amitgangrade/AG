import time
import numpy as np
from numba import jit

# --- Configuration ---
WIDTH = 1000
HEIGHT = 1000
MAX_ITER = 256
X_MIN, X_MAX = -2.0, 1.0
Y_MIN, Y_MAX = -1.5, 1.5

# --- Pure Python Implementation ---
def mandelbrot_python(height, width, max_iter, x_min, x_max, y_min, y_max):
    result = np.zeros((height, width), dtype=np.int32)
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height

    for y in range(height):
        cy = y_min + y * y_step
        for x in range(width):
            cx = x_min + x * x_step
            zx, zy = 0.0, 0.0
            count = 0
            while zx*zx + zy*zy <= 4.0 and count < max_iter:
                temp = zx*zx - zy*zy + cx
                zy = 2.0 * zx * zy + cy
                zx = temp
                count += 1
            result[y, x] = count
    return result

# --- Numba JIT Implementation ---
@jit(nopython=True)
def mandelbrot_numba(height, width, max_iter, x_min, x_max, y_min, y_max):
    result = np.zeros((height, width), dtype=np.int32)
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height

    for y in range(height):
        cy = y_min + y * y_step
        for x in range(width):
            cx = x_min + x * x_step
            zx, zy = 0.0, 0.0
            count = 0
            while zx*zx + zy*zy <= 4.0 and count < max_iter:
                temp = zx*zx - zy*zy + cx
                zy = 2.0 * zx * zy + cy
                zx = temp
                count += 1
            result[y, x] = count
    return result

def run_benchmark():
    print(f"Benchmarking Mandelbrot Set generation ({WIDTH}x{HEIGHT}, {MAX_ITER} iterations)...")
    print("-" * 60)

    # 1. Measure Pure Python
    print("Running Pure Python implementation... (this might take a while)")
    start_py = time.time()
    _ = mandelbrot_python(HEIGHT, WIDTH, MAX_ITER, X_MIN, X_MAX, Y_MIN, Y_MAX)
    end_py = time.time()
    time_py = end_py - start_py
    print(f"Python Time: {time_py:.4f} seconds")

    # 2. Measure Numba (Run once to compile, then measure)
    print("\nRunning Numba implementation...")
    # Warmup / Compilation
    print("  Compiling...", end="\r")
    _ = mandelbrot_numba(10, 10, MAX_ITER, X_MIN, X_MAX, Y_MIN, Y_MAX) 
    print("  Compiling... Done.")
    
    start_nb = time.time()
    result_nb = mandelbrot_numba(HEIGHT, WIDTH, MAX_ITER, X_MIN, X_MAX, Y_MIN, Y_MAX)
    end_nb = time.time()
    time_nb = end_nb - start_nb
    print(f"Numba Time:  {time_nb:.4f} seconds")

    # 3. Results
    speedup = time_py / time_nb
    print("-" * 60)
    print(f"SPEEDUP: {speedup:.2f}x FASTER")
    print("-" * 60)
    
    # Save Image to prove it worked
    try:
        from PIL import Image
        img = Image.fromarray((result_nb % 255).astype(np.uint8))
        img.save("mandelbrot.png")
        print("\nVisualization saved to 'mandelbrot.png'")
    except ImportError:
        print("\nPIL not installed, skipping image save.")

if __name__ == "__main__":
    run_benchmark()
