import numpy as np
from scipy.linalg.blas import daxpy
import time
import csv


def daxpy_strided(N, stride):
    x_base = np.ones(N * stride, dtype=np.float64, order='C')
    y_base = np.ones(N * stride, dtype=np.float64, order='C')

    x = x_base[::stride]
    y = y_base[::stride]

    assert len(x) == N, f"Expected {N} elements, got {len(x)}"

    # Warm-up
    _ = daxpy(x, y, a=2.0)

    # Timed run
    start = time.perf_counter()
    result = daxpy(x, y, a=2.0)
    end = time.perf_counter()

    elapsed = end - start
    bytes_moved = x.nbytes + y.nbytes
    bandwidth = bytes_moved / elapsed / 1e9  # GB/s

    print(f"Stride = {stride}, N = {N:,}")
    print(f"Elapsed time: {elapsed:.6f} sec")
    print(f"Estimated Bandwidth: {bandwidth:.2f} GB/s")

    return (stride, elapsed, bandwidth)


if __name__ == "__main__":
    results = []
    N = 10_000_000
    for stride in [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 75, 80, 96, 112, 128, 140, 156, 160, 192, 256]:
        print(f"\n--- Testing Stride {stride} ---")
        results.append(daxpy_strided(N, stride))

    with open("daxpy_strided_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Stride", "Elapsed Time (s)", "Bandwidth (GB/s)"])
        writer.writerows(results)

    print("\n Results written to daxpy_strided_results.csv")
