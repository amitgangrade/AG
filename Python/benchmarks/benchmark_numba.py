"""
Mandelbrot Set Benchmark
------------------------
This script compares the performance of a pure Python implementation of the 
Mandelbrot set generation against a Numba JIT-accelerated implementation.

The Mandelbrot set is a set of complex numbers that forms a fractal. 
The calculation is computationally intensive, making it an excellent candidate 
for performance optimization using Just-In-Time (JIT) compilation.
"""

import time
import numpy as np
from numba import jit

# --- Configuration ---
# Canvas dimensions
WIDTH = 1000
HEIGHT = 1000
# Maximum iterations per pixel to determine inclusion in the set
MAX_ITER = 256
# Coordinate bounds in the complex plane
X_MIN, X_MAX = -2.0, 1.0
Y_MIN, Y_MAX = -1.5, 1.5

# --- Pure Python Implementation ---
def mandelbrot_python(height, width, max_iter, x_min, x_max, y_min, y_max):
    """
    Generates the Mandelbrot set using pure Python and NumPy.
    
    Args:
        height (int): Height of the output image.
        width (int): Width of the output image.
        max_iter (int): Maximum number of iterations per pixel.
        x_min, x_max (float): Range of the real axis.
        y_min, y_max (float): Range of the imaginary axis.
        
    Returns:
        np.ndarray: A 2D array of iteration counts.
    """
    result = np.zeros((height, width), dtype=np.int32)
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height

    for y in range(height):
        cy = y_min + y * y_step
        for x in range(width):
            cx = x_min + x * x_step
            zx, zy = 0.0, 0.0
            count = 0
            # Standard Mandelbrot iteration: z = z^2 + c
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
    """
    Generates the Mandelbrot set using Numba's JIT compiler.
    The implementation is identical to the Python version, but compiled to machine code.
    """
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
    """
    Runs the benchmark, comparing pure Python and Numba JIT performance.
    """
    print(f"Benchmarking Mandelbrot Set generation ({WIDTH}x{HEIGHT}, {MAX_ITER} iterations)...")
    print("-" * 60)

    # --- 1. Measure Pure Python ---
    print("Running Pure Python implementation... (this might take a while)")
    start_py = time.time()
    _ = mandelbrot_python(HEIGHT, WIDTH, MAX_ITER, X_MIN, X_MAX, Y_MIN, Y_MAX)
    end_py = time.time()
    time_py = end_py - start_py
    print(f"Python Time: {time_py:.4f} seconds")

    # --- 2. Measure Numba ---
    print("\nRunning Numba implementation...")
    # Warmup / Compilation: Numba compiles the function on the first call.
    # We run it once on a small grid to ensure compilation overhead doesn't skew benchmark results.
    print("  Compiling...", end="\r")
    _ = mandelbrot_numba(10, 10, MAX_ITER, X_MIN, X_MAX, Y_MIN, Y_MAX) 
    print("  Compiling... Done.")
    
    # Actual timed run with the full grid
    start_nb = time.time()
    result_nb = mandelbrot_numba(HEIGHT, WIDTH, MAX_ITER, X_MIN, X_MAX, Y_MIN, Y_MAX)
    end_nb = time.time()
    time_nb = end_nb - start_nb
    print(f"Numba Time:  {time_nb:.4f} seconds")

    # --- 3. Results Summary ---
    speedup = time_py / time_nb
    print("-" * 60)
    print(f"SPEEDUP: {speedup:.2f}x FASTER")
    print("-" * 60)
    
    # Save a visualization to verify correct computation
    try:
        from PIL import Image
        # Convert the iteration counts to an 8-bit image
        img = Image.fromarray((result_nb % 255).astype(np.uint8))
        img.save("mandelbrot.png")
        print("\nVisualization saved to 'mandelbrot.png'")
    except ImportError:
        print("\nPIL not installed, skipping image save (Pillow is required for this step).")

if __name__ == "__main__":
    run_benchmark()
