import numpy as np
from scipy.linalg.blas import daxpy
import time

def daxpy_benchmark(N, alpha=2.0):
    x = np.ones(N, dtype=np.float64)
    y = np.ones(N, dtype=np.float64)

    # Warm-up: assign result manually
    _ = daxpy(x, y, a=alpha)

    start = time.perf_counter()
    result = daxpy(x, y, a=alpha)
    end = time.perf_counter()

    elapsed = end - start
    bytes_moved = x.nbytes + y.nbytes
    bandwidth = bytes_moved / elapsed / 1e9

    print(f"N = {N:,}")
    print(f"Elapsed time: {elapsed:.4f} sec")
    print(f"Bandwidth: {bandwidth:.2f} GB/s")

if __name__ == "__main__":
    daxpy_benchmark(100_000_000)
