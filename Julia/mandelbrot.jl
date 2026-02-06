# Mandelbrot Set Benchmark - Julia Version
# ----------------------------------------

const WIDTH = 1000
const HEIGHT = 1000
const MAX_ITER = 256
const X_MIN, X_MAX = -2.0, 1.0
const Y_MIN, Y_MAX = -1.5, 1.5

function mandelbrot(height, width, max_iter, x_min, x_max, y_min, y_max)
    result = zeros(Int32, height, width)
    x_step = (x_max - x_min) / width
    y_step = (y_max - y_min) / height

    for y in 0:height-1
        cy = y_min + y * y_step
        for x in 0:width-1
            cx = x_min + x * x_step
            zx, zy = 0.0, 0.0
            count = 0
            while zx*zx + zy*zy <= 4.0 && count < max_iter
                zx_new = zx*zx - zy*zy + cx
                zy = 2.0 * zx * zy + cy
                zx = zx_new
                count += 1
            end
            result[y+1, x+1] = count
        end
    end
    return result
end

function run_benchmark()
    println("Benchmarking Mandelbrot Set (Julia with 20 iterations)...")
    
    # Warmup / Compilation
    print("  Compiling... ")
    mandelbrot(10, 10, MAX_ITER, X_MIN, X_MAX, Y_MIN, Y_MAX)
    println("Done.")

    iterations = 20
    best_time = 1e9

    for i in 1:iterations
        start_time = time()
        _ = mandelbrot(HEIGHT, WIDTH, MAX_ITER, X_MIN, X_MAX, Y_MIN, Y_MAX)
        end_time = time()
        
        duration = end_time - start_time
        if duration < best_time
            best_time = duration
        end
        @printf("  Run %2d: %.4f seconds\n", i, duration)
    end
    
    @printf("Julia Time: %.4f seconds (best of %d)\n", best_time, iterations)
end

using Printf
run_benchmark()
