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
        return 30 * 1024
    except Exception:
        return 30 * 1024

def generate_test_sizes(l3_kb, max_limit=2**30):
    base_sizes = []
    for i in range(0, int(math.log2(max_limit)) + 1):
        size = 2 ** i
        base_sizes.append(size)
        base_sizes.append(int(size * 1.5))
    return sorted(set(base_sizes))

def make_single_cycle_permutation(N):
    idx = list(range(N))
    random.shuffle(idx[1:])
    arr = np.zeros(N, dtype=np.int64)
    for i in range(N - 1):
        arr[idx[i]] = idx[i + 1]
    arr[idx[-1]] = idx[0]
    return arr

def pointer_chase(N, repeat_factor):
    arr = make_single_cycle_permutation(N)
    visited = set()
    i = 0
    for _ in range(N):
        visited.add(i)
        i = arr[i]
    assert len(visited) == N, "Pointer chase did not visit all elements"

    i = 0
    start = time.perf_counter()
    for _ in range(N * repeat_factor):
        i = arr[i]
    end = time.perf_counter()

    elapsed = end - start
    latency_ns = (elapsed / (N * repeat_factor)) * 1e9
    app_bytes = N * repeat_factor * 8
    app_bandwidth = app_bytes / elapsed / 1e9
    return latency_ns, elapsed, app_bandwidth

def run_perf(N, repeat_factor):
    code = f"""
import numpy as np
import random
import time

N = {N}
repeat_factor = {repeat_factor}

idx = list(range(N))
random.shuffle(idx[1:])
arr = np.zeros(N, dtype=np.int64)
for i in range(N - 1):
    arr[idx[i]] = idx[i + 1]
arr[idx[-1]] = idx[0]

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
        "-C", "0",
        "-e", 
        "cache-misses,L1-dcache-load-misses,LLC-load-misses,LLC-loads,unc_m_cas_count.rd,unc_m_cas_count.wr",
        "python3", "temp_pointer_chase_perf.py"
    ]

    result = subprocess.run(perf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stderr = result.stderr
    stdout = result.stdout

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

    # ✅ Correct bandwidth calculation using CAS counts
   # rd = events.get("unc_m_cas_count.rd", 0)
   # wr = events.get("unc_m_cas_count.wr", 0)
   # if elapsed > 0 and (rd + wr) > 0:
   #     perf_bandwidth = ((rd + wr) * 64) / elapsed / 1e9  # in GB/s
    if events["cache-misses"] > 0 and elapsed > 0:
        perf_bandwidth = (events["cache-misses"] * 64) / elapsed / 1e9  # in GB/s
    elif events["unc_m_cas_count.rd"] > 0 or events["unc_m_cas_count.wr"] > 0:
        rd = events.get("unc_m_cas_count.rd", 0)
        wr = events.get("unc_m_cas_count.wr", 0)
        if elapsed > 0 and (rd + wr) > 0:
            perf_bandwidth = ((rd + wr) * 64) / elapsed / 1e9  # in GB/s
        else:
            perf_bandwidth = 0.0
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
            try:
                latency_ns, elapsed, app_bandwidth = pointer_chase(N, repeat_factor)
                perf_bandwidth, perf_elapsed, events = run_perf(N, repeat_factor)

                with open(output_csv, "a", newline="") as f:
                    writer = csv.writer(f)
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
                    f.flush()
            except Exception as e:
                print(f"Trial failed for N={N}, trial={trial+1}: {e}")

    print(f"\nResults written to {output_csv}")

if __name__ == "__main__":
    main()
