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


def generate_test_sizes(l3_kb, max_limit=2**30):
    """Generate test sizes based on L3 cache size."""
    base_sizes = []
    for i in range(5, int(math.log2(max_limit)) + 1):
        size = 2 ** i
        base_sizes.append(size)
        base_sizes.append(int(size * 1.5))
    return sorted(set(base_sizes))
    
def make_single_cycle_permutation(N):
    idx = list(range(N))
    random.shuffle(idx[1:])  # Fix the first index
    arr = np.zeros(N, dtype=np.int64)
    for i in range(N - 1):
        arr[idx[i]] = idx[i + 1]
    arr[idx[-1]] = idx[0]  # Close the cycle
    return arr

def pointer_chase(N, repeat_factor):
    arr = make_single_cycle_permutation(N)
    # Warm-up pass to ensure cache is populated

    
    # Validate pointer chain covers all elements
    visited = set()
    i = 0
    for _ in range(N):
        visited.add(i)
        i = arr[i]
    assert len(visited) == N, "Pointer chase does not visit all elements"


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

# Optional full-cycle validation
visited = set()
i = 0
for _ in range(N):
    visited.add(i)
    i = arr[i]
assert len(visited) == N

# Warm-up pass
i = 0
for _ in range(N):
    i = arr[i]

# Timed pointer chase
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
        "cache-misses,L1-dcache-load-misses,LLC-load-misses,LLC-loads,unc_m_cas_count.rd,unc_m_cas_count.wr",
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
        "unc_m_cas_count.rd": 0,
        "unc_m_cas_count.wr": 0
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
            "LLC-loads", "unc_m_cas_count.rd", "unc_m_cas_count.wr"
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
                    events["unc_m_cas_count.rd"],
                    events["unc_m_cas_count.wr"]
                ])

    print(f"\nResults written to {output_csv}")


if __name__ == "__main__":
    main()
