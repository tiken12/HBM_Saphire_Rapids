import numpy as np
import time
import random
import csv

def pointer_chase(N, trials=3):
    repeat_factor= max(1, 10_000 // N)
    idx = list(range(N))
    random.shuffle(idx)

    arr = np.zeros(N, dtype=np.int64)
    for i in range(N):
        arr[i] = idx[i]

    latencies = []

    for _ in range(trials):
        i = 0
        start = time.perf_counter()
        for _ in range(max(1, N * repeat_factor)):
            i = arr[i]
        end = time.perf_counter()
        
        elapsed = end - start
        latency_ns = (elapsed / N) * 1e9
        latencies.append(latency_ns)

    return latencies



if __name__ == "__main__":
    results = []
    trials = 3
    sizes = [1 , 5 , 10 ,50, 75, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1_000, 1_500, 2_000, 3_000, 4_000, 5_000, 6_000, 8_000, 10_000, 15_000, 20_000, 25_000, 30_000,
    35_000, 40_000, 50_000, 60_000, 75_000, 90_000, 100_000, 110_000, 120_000, 130_000, 140_000,
    150_000, 160_000, 170_000, 180_000, 190_000, 200_000, 230_000, 270_000, 290_000, 300_000,
    325_000, 350_000, 375_000, 400_000, 410_000, 425_000, 430_000, 450_000, 475_000, 500_000,
    525_000, 540_000, 575_000, 590_000, 600_000, 610_000, 625_000, 650_000, 675_000, 750_000,
    800_000, 850_000, 900_000, 925_000, 950_000, 975_000, 1_000_000, 5_000_000, 10_000_000,
    15_000_000, 20_000_000, 30_000_000, 40_000_000, 50_000_000, 60_000_000, 70_000_000,
    75_000_000, 100_000_000, 110_000_000, 120_000_000, 130_000_000, 140_000_000, 150_000_000]


    # Save results to CSV
    with open("pointer_chase_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "Trial", "Latency_ns"])

        for N in sizes:
            latencies = pointer_chase (N, trials)
            for trial_idx, latency in enumerate(latencies):
                writer.writerow([N, trial_idx + 1, latency])

    print("\nResults written to pointer_chase_violin_results.csv")
