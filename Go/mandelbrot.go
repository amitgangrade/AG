package main

import (
	"fmt"
	"time"
)

const (
	WIDTH    = 1000
	HEIGHT   = 1000
	MAX_ITER = 256
	X_MIN    = -2.0
	X_MAX    = 1.0
	Y_MIN    = -1.5
	Y_MAX    = 1.5
)

func mandelbrot(width, height int) [][]int {
	result := make([][]int, height)
	xStep := (X_MAX - X_MIN) / float64(width)
	yStep := (Y_MAX - Y_MIN) / float64(height)

	for y := 0; y < height; y++ {
		result[y] = make([]int, width)
		cy := Y_MIN + float64(y)*yStep
		for x := 0; x < width; x++ {
			cx := X_MIN + float64(x)*xStep
			var zx, zy float64
			var count int

			for zx*zx+zy*zy <= 4.0 && count < MAX_ITER {
				temp := zx*zx - zy*zy + cx
				zy = 2.0*zx*zy + cy
				zx = temp
				count++
			}
			result[y][x] = count
		}
	}
	return result
}

func main() {
	fmt.Println("Benchmarking Mandelbrot Set (Go with 20 iterations)...")

	iterations := 20
	var bestTime float64 = 1e9

	for i := 1; i <= iterations; i++ {
		start := time.Now()
		_ = mandelbrot(WIDTH, HEIGHT)
		duration := time.Since(start).Seconds()
		if duration < bestTime {
			bestTime = duration
		}
		fmt.Printf("  Run %2d: %.4f seconds\n", i, duration)
	}

	fmt.Printf("Go Time:    %.4f seconds (best of %d)\n", bestTime, iterations)
}
