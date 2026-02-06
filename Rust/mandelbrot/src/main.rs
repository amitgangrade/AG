use std::time::Instant;

const WIDTH: usize = 1000;
const HEIGHT: usize = 1000;
const MAX_ITER: usize = 256;

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
    let start = Instant::now();
    
    let mut image = vec![0; WIDTH * HEIGHT];
    let mut checksum: u64 = 0;

    for y in 0..HEIGHT {
        for x in 0..WIDTH {
            let cr = (x as f64 - 500.0) / 200.0;
            let ci = (y as f64 - 500.0) / 200.0;
            let val = mandelbrot(cr, ci);
            image[y * WIDTH + x] = val;
            checksum += val as u64;
        }
    }
    
    let duration = start.elapsed();
    println!("Rust Execution Time: {:.4}s", duration.as_secs_f64());
    println!("Checksum: {}", checksum);
}
