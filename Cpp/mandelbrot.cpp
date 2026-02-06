#include <iostream>
#include <vector>
#include <complex>
#include <chrono>

const int WIDTH = 1000;
const int HEIGHT = 1000;
const int MAX_ITER = 256;

int mandelbrot(double cr, double ci) {
    double zr = 0.0;
    double zi = 0.0;
    int n = 0;
    while (zr * zr + zi * zi <= 4.0 && n < MAX_ITER) {
        double temp_zr = zr * zr - zi * zi + cr;
        zi = 2.0 * zr * zi + ci;
        zr = temp_zr;
        n++;
    }
    return n;
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();
    
    std::vector<int> image(WIDTH * HEIGHT);
    long long checksum = 0;

    for (int y = 0; y < HEIGHT; ++y) {
        for (int x = 0; x < WIDTH; ++x) {
             double cr = (x - 500.0) / 200.0;
             double ci = (y - 500.0) / 200.0;
             int val = mandelbrot(cr, ci);
             image[y * WIDTH + x] = val;
             checksum += val;
        }
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    
    std::cout << "C++ Execution Time: " << elapsed.count() << "s" << std::endl;
    std::cout << "Checksum: " << checksum << std::endl;
    
    return 0;
}
