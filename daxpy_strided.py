import numpy as np
from scipy.linalg.blas import daxpy
import time
import csv

def daxpy_strided(N, stride):
    x = np.ones(N * stride, dtype=np.float64)[::stride]
    y = np.ones(N * stride, dtype=np.float64)[::stride]

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
    print(f"Elapsed time: {elapsed:.4f} sec")
    print(f"Estimated Bandwidth: {bandwidth:.2f} GB/s")

    return (stride, elapsed, bandwidth)

if __name__ == "__main__":
    results = []
    N = 10_000_000
    for stride in [1, 2, 4, 8]:
        print(f"\n--- Testing Stride {stride} ---")
        results.append(daxpy_strided(N, stride))

    with open("daxpy_strided_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Stride", "Elapsed Time (s)", "Bandwidth (GB/s)"])
        writer.writerows(results)

    print("\n Results written to daxpy_strided_results.csv")

