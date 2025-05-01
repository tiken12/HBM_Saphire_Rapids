import numpy as np
import time
import os
import csv

def daxpy(a, X, Y):
    Y += a * X
    return Y

a = 2.5
sizes = [
    1_000, 1_500, 2_000, 3_000, 4_000, 5_000, 6_000, 8_000, 10_000, 15_000, 20_000, 25_000, 30_000,
    35_000, 40_000, 50_000, 60_000, 75_000, 90_000, 100_000, 110_000, 120_000, 130_000, 140_000,
    150_000, 160_000, 170_000, 180_000, 190_000, 200_000, 230_000, 270_000, 290_000, 300_000,
    325_000, 350_000, 375_000, 400_000, 410_000, 425_000, 430_000, 450_000, 475_000, 500_000,
    525_000, 540_000, 575_000, 590_000, 600_000, 610_000, 625_000, 650_000, 675_000, 750_000,
    800_000, 850_000, 900_000, 925_000, 950_000, 975_000, 1_000_000, 5_000_000, 10_000_000,
    15_000_000, 20_000_000, 30_000_000, 40_000_000, 50_000_000, 60_000_000, 70_000_000,
    75_000_000, 100_000_000, 110_000_000, 120_000_000, 130_000_000, 140_000_000, 150_000_000
]
num_threads_list = [1, 2, 4, 8, 16, 32, 64, 128] 

csv_filename = "daxpy_parallel_results.csv"
if not os.path.exists(csv_filename):
    with open(csv_filename, mode = 'w', newline= '') as file:
        writer = csv.writer(file)
        writer.writerow(["threads", "size", "time_sec", "bandwidth_GBps"])

print("threads,size,time_sec,bandwidth_GBps")

for threads in num_threads_list:
    os.environ["OMP_NUM_THREADS"] = str(threads)

    for N in sizes:
        X = np.ones(N, dtype=np.float64)
        Y = np.ones(N, dtype=np.float64)

        start = time.time()
        Y = daxpy(a, X, Y)
        end = time.time()

        elapsed = end - start
        bandwidth = (3 * X.nbytes) / (elapsed * 1e9)  # 2 reads + 1 write

        print(f"{threads},{N},{elapsed:.6f},{bandwidth:.2f}")
        
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([threads, N, elapsed, bandwidth])
