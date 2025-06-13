import numpy as np
import time
import random
import csv
import subprocess
import re
import os
import math
from pathlib import Path

def get_l3_cache_kb():
    """Get L3 cache size in KB from lscpu."""
    try:
        result = subprocess.run(["lscpu"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "L3 cache" in line:
                match = re.search(r'(\d+)([KMG])', line)
                if match:
                    size = int(match.group(1))
                    unit = match.group(2)
                    if unit == 'K':
                        return size
                    elif unit == 'M':
                        return size * 1024
                    elif unit == 'G':
                        return size * 1024 * 1024
        return 30 * 1024  # fallback default
    except Exception:
        return 30 * 1024


def generate_test_sizes(l3_kb, max_limit=100_000_000):
    """Generate test sizes based on L3 cache size."""
    base_sizes = [2 ** i for i in range(0, int(math.log2(max_limit)) + 1)]
    return sorted(set(base_sizes))


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
    latency_ns = (elapsed / (N * repeat_factor)) * 1e9
    app_bytes = N * repeat_factor * 8  # 8 bytes per int64
    app_bandwidth = app_bytes / elapsed / 1e9  # in GB/s

    return latency_ns, elapsed, app_bandwidth


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
        "-e",
        "cache-misses,L1-dcache-load-misses,LLC-load-misses,LLC-loads,UNC_M_CAS_COUNT.RD,UNC_M_CAS_COUNT.WR",
        "python3", "temp_pointer_chase_perf.py"
    ]

    result = subprocess.run(perf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stderr = result.stderr
    stdout = result.stdout

    # Extract elapsed time
    elapsed_match = re.search(r"Elapsed:\s*([\d.]+)", stdout)
    elapsed = float(elapsed_match.group(1)) if elapsed_match else 0.0

    events = {
        "cache-misses": 0,
        "L1-dcache-load-misses": 0,
        "LLC-load-misses": 0,
        "LLC-loads": 0,
        "UNC_M_CAS_COUNT.RD": 0,
        "UNC_M_CAS_COUNT.WR": 0
    }

    for line in stderr.splitlines():
        for event in events:
            if event in line and re.search(r"^\s*[\d,]+", line):
                match = re.search(r"([\d,]+)", line)
                if match:
                    num_str = match.group(1).replace(",", "")
                    if num_str.isdigit():
                        events[event] = int(num_str)
                break

    # Compute perf-derived bandwidth
    if events["cache-misses"] > 0 and elapsed > 0:
        perf_bandwidth = (events["cache-misses"] * 64) / elapsed / 1e9
    else:
        perf_bandwidth = 0.0

    if os.path.exists("temp_pointer_chase_perf.py"):
        os.remove("temp_pointer_chase_perf.py")

    return perf_bandwidth, elapsed, events


def main():
    trials = 10
    l3_kb = get_l3_cache_kb()
    print(f"L3 Cache Size: {l3_kb / 1024} MB")
    sizes = generate_test_sizes(l3_kb * 1024)
    print(f"Generated test sizes: {sizes}")

    Path("results").mkdir(exist_ok=True)
    output_csv = Path("results/pointer_chase_cache_profile.csv")

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "N", "Trial", "Latency_ns", "App_Bandwidth_GBps", "Perf_Bandwidth_GBps",
            "Perf_Elapsed", "Cache_Misses", "L1-dcache-load-misses", "LLC-load-misses",
            "LLC-loads", "UNC_M_CAS_COUNT.RD", "UNC_M_CAS_COUNT.WR"
        ])

        for N in sizes:
            repeat_factor = max(1, 10_000 // N)
            for trial in range(trials):
                latency_ns, elapsed, app_bandwidth = pointer_chase(N, repeat_factor)
                perf_bandwidth, perf_elapsed, events = run_perf(N, repeat_factor)

                writer.writerow([
                    N,
                    trial + 1,
                    latency_ns,
                    app_bandwidth,
                    perf_bandwidth,
                    perf_elapsed,
                    events["cache-misses"],
                    events["L1-dcache-load-misses"],
                    events["LLC-load-misses"],
                    events["LLC-loads"],
                    events["UNC_M_CAS_COUNT.RD"],
                    events["UNC_M_CAS_COUNT.WR"]
                ])

    print(f"\nResults written to {output_csv}")


if __name__ == "__main__":
    main()
