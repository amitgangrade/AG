use std::time::Instant;

const WIDTH: usize = 1000;
const HEIGHT: usize = 1000;
const MAX_ITER: usize = 256;

const X_MIN: f64 = -2.0;
const X_MAX: f64 = 1.0;
const Y_MIN: f64 = -1.5;
const Y_MAX: f64 = 1.5;

fn mandelbrot(cr: f64, ci: f64) -> usize {
    let mut zr = 0.0;
    let mut zi = 0.0;
    let mut n = 0;
    while zr * zr + zi * zi <= 4.0 && n < MAX_ITER {
        let temp_zr = zr * zr - zi * zi + cr;
        zi = 2.0 * zr * zi + ci;
        zr = temp_zr;
        n += 1;
    }
    n
}

fn main() {
    println!("Benchmarking Mandelbrot Set (Rust with 20 iterations)...");
    
    let mut image = vec![0; WIDTH * HEIGHT];
    let mut _checksum: u64 = 0;

    let x_step = (X_MAX - X_MIN) / WIDTH as f64;
    let y_step = (Y_MAX - Y_MIN) / HEIGHT as f64;

    let iterations = 20;
    let mut best_time = 1e9;

    for i in 1..=iterations {
        let start = Instant::now();
        for y in 0..HEIGHT {
            let ci = Y_MIN + y as f64 * y_step;
            for x in 0..WIDTH {
                let cr = X_MIN + x as f64 * x_step;
                let val = mandelbrot(cr, ci);
                image[y * WIDTH + x] = val;
                _checksum += val as u64;
            }
        }
        let duration = start.elapsed().as_secs_f64();
        if duration < best_time {
            best_time = duration;
        }
        println!("  Run {:2}: {:.4}s", i, duration);
    }
    
    println!("Rust Execution Time: {:.4}s (best of {})", best_time, iterations);
    println!("Final Checksum: {}", _checksum);
}
