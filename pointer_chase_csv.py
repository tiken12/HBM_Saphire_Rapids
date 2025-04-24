import numpy as np
import time
import random
import csv

def pointer_chase(N):
    idx = list(range(N))
    random.shuffle(idx)

    arr = np.zeros(N, dtype=np.int64)
    for i in range(N):
        arr[i] = idx[i]

    start = time.perf_counter()
    i = 0
    for _ in range(N):
        i = arr[i]
    end = time.perf_counter()

    elapsed = end - start

    print(f"Pointer Chase Test (N={N:,})")
    print(f"Elapsed time: {elapsed:.6f} sec")

    # Log to CSV
    with open("pointer_chase_results.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow([N, elapsed])

    return elapsed

if __name__ == "__main__":
    for N in [1_000_000, 10_000_000, 50_000_000]:
        pointer_chase(N)
