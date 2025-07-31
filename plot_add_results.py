import pandas as pd
import matplotlib.pyplot as plt

# Load the add results CSV
df = pd.read_csv("add_results.csv")

# Convert columns to proper types
df["N"] = df["N"].astype(int)
df["Bandwidth_GBps"] = df["Bandwidth_GBps"].astype(float)
df["Elapsed"] = df["Elapsed"].astype(float)

# Average over trials
df_avg = df.groupby("N").mean().reset_index()

# Plot Bandwidth vs N
plt.figure(figsize=(10, 5))
plt.plot(df_avg["N"], df_avg["Bandwidth_GBps"], marker='o', label="Bandwidth (GB/s)", color='green')
plt.xlabel("Array Size (N)")
plt.ylabel("Bandwidth (GB/s)")
plt.title("Vector Add: Average Bandwidth vs Array Size")
plt.xscale("log", base=2)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("add_bandwidth_vs_size.png")
plt.show()

# Plot Elapsed Time vs N
plt.figure(figsize=(10, 5))
plt.plot(df_avg["N"], df_avg["Elapsed"], marker='x', color='purple', label="Elapsed Time (s)")
plt.xlabel("Array Size (N)")
plt.ylabel("Elapsed Time (s)")
plt.title("Vector Add: Average Elapsed Time vs Array Size")
plt.xscale("log", base=2)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("add_elapsed_vs_size.png")
plt.show()
