import numpy as np
import time
import random
import csv

def pointer_chase(N, trials=5):
    idx = list(range(N))
    random.shuffle(idx)

    arr = np.zeros(N, dtype=np.int64)
    for i in range(N):
        arr[i] = idx[i]

    total_time = 0.0
    for _ in range(trials):
        i = 0
        start = time.perf_counter()
        for _ in range(N):
            i = arr[i]
        end = time.perf_counter()
        total_time += (end - start)

    avg_time = total_time / trials
    latency_ns = (avg_time / N) * 1e9

    print(f"N = {N:,}, Trials = {trials}")
    print(f"  Avg Time: {avg_time:.6f} sec")
    print(f"  Avg Latency: {latency_ns:.2f} ns")

    return (N, trials, avg_time, latency_ns)

if __name__ == "__main__":
    results = []
    trials = 5
    sizes = [1_000_000, 5_000_000, 10_000_000, 25_000_000, 50_000_000, 75_000_000, 100_000_000]

    for N in sizes:
        result = pointer_chase(N, trials)
        results.append(result)

    # Save results to CSV
    with open("pointer_chase_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "Trials", "Avg Time (s)", "Avg Latency (ns)"])
        writer.writerows(results)

    print("\nResults written to pointer_chase_results.csv")
