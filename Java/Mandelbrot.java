public class Mandelbrot {
    // Configuration congruent with Python version
    static final int WIDTH = 1000;
    static final int HEIGHT = 1000;
    static final int MAX_ITER = 256;
    static final double X_MIN = -2.0;
    static final double X_MAX = 1.0;
    static final double Y_MIN = -1.5;
    static final double Y_MAX = 1.5;

    public static void main(String[] args) {
        System.out.println("Benchmarking Mandelbrot Set (Java with JIT Warmup)...");

        int iterations = 20;
        double bestTime = Double.MAX_VALUE;

        for (int i = 1; i <= iterations; i++) {
            long startTime = System.nanoTime();
            int[][] result = mandelbrot(WIDTH, HEIGHT);
            long endTime = System.nanoTime();

            double durationSeconds = (endTime - startTime) / 1_000_000_000.0;
            if (durationSeconds < bestTime) {
                bestTime = durationSeconds;
            }
            System.out.printf("  Run %2d: %.4f seconds%n", i, durationSeconds);
        }

        System.out.printf("Java Time:  %.4f seconds (best of %d)%n", bestTime, iterations);
    }

    public static int[][] mandelbrot(int width, int height) {
        int[][] result = new int[height][width];
        double xStep = (X_MAX - X_MIN) / width;
        double yStep = (Y_MAX - Y_MIN) / height;

        for (int y = 0; y < height; y++) {
            double cy = Y_MIN + y * yStep;
            for (int x = 0; x < width; x++) {
                double cx = X_MIN + x * xStep;
                double zx = 0.0;
                double zy = 0.0;
                int count = 0;

                while (zx * zx + zy * zy <= 4.0 && count < MAX_ITER) {
                    double temp = zx * zx - zy * zy + cx;
                    zy = 2.0 * zx * zy + cy;
                    zx = temp;
                    count++;
                }
                result[y][x] = count;
            }
        }
        return result;
    }
}
