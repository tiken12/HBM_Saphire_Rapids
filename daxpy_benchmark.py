import numpy as np
from scipy.linalg.blas import daxpy
import time


def daxpy_benchmark(N, alpha=2.0, repeat=1000):
    x = np.ones(N, dtype=np.float64)
    y = np.ones(N, dtype=np.float64)

    # Warm-up: assign result manually
    # Kenneth: A warm up makes sense here. Is this important/done for the other tests? (Probably should be)
    _ = daxpy(x, y, a=alpha)

    start = time.perf_counter()
    # Kenneth: Does it make sense to repeat the test from within itself? I'm not sure I understand the goal. Shouldn't we have one sample in the CSV per repeat?
    for _ in range(repeat):
        _ = daxpy(x, y, a=alpha)
    end = time.perf_counter()

    elapsed = end - start
    avg_elapsed = elapsed / repeat
    bytes_moved = x.nbytes + y.nbytes
    bandwidth = bytes_moved / avg_elapsed / 1e9

    print(f"N = {N:,}, repeat= {repeat}")
    print(f"Total elapsed time: {elapsed: .6f} sec")
    print(f"Avg time per DAXPY: {avg_elapsed:.8f} sec")
    print(f"Bandwidth: {bandwidth:.2f} GB/s")

    return avg_elapsed, bandwidth


if __name__ == "__main__":
    daxpy_benchmark(100_000_000)
