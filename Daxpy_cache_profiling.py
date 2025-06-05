import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns

# Settings
trials_per_N = 5
alpha = 2.5
element_size = 8  # float64
sizes = [
    256, 512, 1024, 2048, 4096, 8192,
    16_384, 32_768, 65_536, 131_072,
    262_144, 524_288, 1_048_576,
    2_097_152, 4_194_304, 8_388_608,
    16_777_216
]

results = []

# Benchmark loop
for N in sizes:
    x = np.random.rand(N).astype(np.float64)
    y = np.random.rand(N).astype(np.float64)
    for trial in range(trials_per_N):
        start = time.perf_counter()
        y += alpha * x
        end = time.perf_counter()

        elapsed = end - start  # in seconds
        bytes_moved = N * 3 * element_size  # x, y read + y write
        bandwidth_GBps = bytes_moved / elapsed / 1e9

        results.append({
            "N": N,
            "Trial": trial,
            "Time_sec": elapsed,
            "Bandwidth_GBps": bandwidth_GBps
        })

# Save to CSV
df = pd.DataFrame(results)
df.to_csv("daxpy_cache_profile.csv", index=False)
print("✅ Benchmark complete. Results saved to daxpy_cache_profile.csv")

