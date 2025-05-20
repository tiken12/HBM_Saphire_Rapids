import numpy as np
import time
import random
import csv
import subprocess
import re

def pointer_chase(N, repeat_factor):
    idx = list(range(N))
    random.shuffle(idx)
    arr = np.zeros(N, dtype=np.int64)
    for i in range(N):
        arr[i] = idx[i]

    i = 0
    start = time.perf_counter()
    for _ in range(N * repeat_factor):
        i = arr[i]
    end = time.perf_counter()

    elapsed = end - start
    latency_ns = (elapsed / N) * 1e9

    return latency_ns, elapsed

def run_perf(N, repeat_factor):
    code = f"""
import numpy as np
import random
import time

N = {N}
repeat_factor = {repeat_factor}

idx = list(range(N))
random.shuffle(idx)
arr = np.zeros(N, dtype=np.int64)
for i in range(N):
    arr[i] = idx[i]

i = 0
start = time.perf_counter()
for _ in range(N * repeat_factor):
    i = arr[i]
end = time.perf_counter()
print(f"Elapsed: {{end - start}}")
"""

    with open("temp_pointer_chase_perf.py", "w") as temp:
        temp.write(code)

    perf_command = [
        "perf", "stat",
        "-e", "cache-misses",
        "python3", "temp_pointer_chase_perf.py"
    ]

    result = subprocess.run(perf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stderr = result.stderr
    stdout = result.stdout

    # Extract elapsed time
    elapsed_match = re.search(r"Elapsed:\s*([\d.]+)", stdout)
    elapsed = float(elapsed_match.group(1)) if elapsed_match else None

    # Extract cache misses
    cache_misses = None
    for line in stderr.splitlines():
        if "cache-misses" in line:
            match = re.search(r'([\d,]+)', line)
            if match:
                cache_misses = int(match.group(1).replace(",", ""))
                break

    return elapsed, cache_misses



if __name__ == "__main__":
    results = []
    trials = 3
    sizes = [1 , 5 , 10 ,50, 75, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1_000, 1_500, 2_000, 3_000, 4_000, 5_000, 6_000,
            8_000, 10_000, 15_000, 20_000, 25_000, 30_000, 35_000, 40_000, 50_000, 60_000, 75_000, 90_000, 100_000, 110_000, 
            120_000, 130_000, 140_000, 150_000, 160_000, 170_000, 180_000, 190_000, 200_000, 230_000, 270_000, 290_000, 300_000
            , 325_000, 350_000, 375_000, 400_000, 410_000, 425_000, 430_000, 450_000, 475_000, 500_000, 525_000, 540_000, 
            575_000, 590_000, 600_000, 610_000, 625_000, 650_000, 675_000, 750_000, 800_000, 850_000, 900_000, 925_000, 
            950_000, 975_000, 1_000_000, 5_000_000, 10_000_000, 15_000_000, 20_000_000, 30_000_000, 40_000_000, 50_000_000, 
            60_000_000, 70_000_000]


    # Save results to CSV
    with open("pointer_chase_perf_validated.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["N", "Trial", "Latency_ns", "App_Bandwidth_GBps", "Perf_Elapsed", "Cach_Misses", "Perf_Bandwidth_GBps"])

        for N in sizes:
            repeat_factor = max(1, 10_000 // N)
            for trial in range(trials):
                #Run app-native measurement
                latency_ns, elapsed = pointer_chase(N, repeat_factor)
                app_bytes = N * repeat_factor * 8
                app_bandwidth = app_bytes / elapsed / 1e9 #in GB/s

                # Run perf-based measurement
                perf_elapsed, cache_misses = run_perf(N, repeat_factor)
                if perf_elapsed and cache_misses:
                    perf_bandwidth = (cache_misses * 64) / perf_elapsed / 1e9
                else:
                    perf_bandwidth = None

                writer.writerow([
                    N,
                    trial +1,
                    latency_ns,
                    app_bandwidth,
                    perf_elapsed,
                    cache_misses,
                    perf_bandwidth
                    ])


    print("\nResults written to pointer_chase_perf_validated.csv")
