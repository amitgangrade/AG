import os
import subprocess
import time
import sys
import statistics
import re

# Configuration
WIDTH = 1000
HEIGHT = 1000
MAX_ITER = 256

def run_command(cmd, shell=False):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Return both stdout and stderr in case it crashed after printing some results
        return (e.stdout or "") + (e.stderr or "")
    except FileNotFoundError:
        return "Command not found"

def extract_times(output):
    if not isinstance(output, str):
        return []
    # Regex to find "Run X: Y.YYYY seconds" or similar patterns
    # Handles "Run 1: 0.1234 seconds" and "Run  1: 0.1234 seconds"
    pattern = r"Run\s+\d+:\s+(\d+\.\d+)"
    times = [float(t) for t in re.findall(pattern, output)]
    return times

def calculate_stats(times):
    if not times:
        return None
    return {
        "fastest": min(times),
        "slowest": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times)
    }

def main():
    print(f"Mandelbrot Multi-Language Benchmark ({WIDTH}x{HEIGHT}, {MAX_ITER} iterations)")
    print("Each language runs 20 iterations in a single session.")
    print("=" * 80)
    
    stats_data = {}

    # 1. Python (Numba)
    print("Running Python (Numba)...")
    py_path = os.path.join("Python", "benchmarks", "benchmark_numba.py")
    output = run_command([sys.executable, py_path])
    stats_data["Python (Numba)"] = calculate_stats(extract_times(output))

    # 2. Go
    print("Running Go...")
    go_path = os.path.join("Go", "mandelbrot.go")
    output = run_command(["go", "run", go_path])
    stats_data["Go"] = calculate_stats(extract_times(output))

    # 3. Java
    print("Running Java...")
    java_class_path = "Java"
    run_command(["javac", os.path.join(java_class_path, "Mandelbrot.java")])
    output = run_command(["java", "-cp", java_class_path, "Mandelbrot"])
    stats_data["Java"] = calculate_stats(extract_times(output))

    # 4. Rust (Direct rustc)
    print("Running Rust...")
    rust_src = os.path.join("Rust", "mandelbrot", "src", "main.rs")
    rust_bin = os.path.join("Rust", "mandelbrot", "mandelbrot.exe")
    run_command(["rustc", "-O", rust_src, "-o", rust_bin])
    if os.path.exists(rust_bin):
        output = run_command([rust_bin])
        stats_data["Rust"] = calculate_stats(extract_times(output))

    # 5. Julia
    print("Running Julia...")
    julia_path = os.path.join("Julia", "mandelbrot.jl")
    output = run_command(["julia", julia_path])
    if output and "Command not found" not in str(output):
        stats_data["Julia"] = calculate_stats(extract_times(output))

    # Final Detailed Table
    print("\n" + "=" * 80)
    header = f"{'Language':<18} | {'Fastest':<10} | {'Slowest':<10} | {'Mean':<10} | {'Median':<10}"
    print(header)
    print("-" * 80)
    
    # Sort by fastest time
    successful_results = {k: v for k, v in stats_data.items() if v}
    sorted_langs = sorted(successful_results.keys(), key=lambda x: successful_results[x]["fastest"])
    
    for lang in sorted_langs:
        s = successful_results[lang]
        print(f"{lang:<18} | {s['fastest']:>10.4f} | {s['slowest']:>10.4f} | {s['mean']:>10.4f} | {s['median']:>10.4f}")
    
    # Show missing
    all_langs = ["Python (Numba)", "Go", "Java", "Rust", "Julia"]
    for lang in all_langs:
        if lang not in successful_results:
            print(f"{lang:<18} | {'N/A':>10} | {'N/A':>10} | {'N/A':>10} | {'N/A':>10}")
    print("=" * 80)

if __name__ == "__main__":
    main()
