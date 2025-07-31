import pandas as pd
import matplotlib.pyplot as plt

# Load dot results CSV
df = pd.read_csv("dot_results.csv")

# Convert necessary columns
df["N"] = df["N"].astype(int)
df["Bandwidth_GBps"] = df["Bandwidth_GBps"].astype(float)
df["Elapsed"] = df["Elapsed"].astype(float)
df["Dot_Result"] = df["Dot_Result"].astype(float)

# Average across trials
df_avg = df.groupby("N").mean().reset_index()

# Plot Bandwidth
plt.figure(figsize=(10, 5))
plt.plot(df_avg["N"], df_avg["Bandwidth_GBps"], marker='o', label="Bandwidth (GB/s)", color='blue')
plt.xlabel("Array Size (N)")
plt.ylabel("Bandwidth (GB/s)")
plt.title("Dot Product: Bandwidth vs Array Size")
plt.xscale("log", base=2)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("dot_bandwidth_vs_size.png")
plt.show()

# Plot Elapsed Time
plt.figure(figsize=(10, 5))
plt.plot(df_avg["N"], df_avg["Elapsed"], marker='s', label="Elapsed Time (s)", color='orange')
plt.xlabel("Array Size (N)")
plt.ylabel("Elapsed Time (s)")
plt.title("Dot Product: Elapsed Time vs Array Size")
plt.xscale("log", base=2)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("dot_elapsed_vs_size.png")
plt.show()

# Plot Dot Result (mainly to check variation)
plt.figure(figsize=(10, 5))
plt.plot(df_avg["N"], df_avg["Dot_Result"], marker='x', label="Dot Result", color='green')
plt.xlabel("Array Size (N)")
plt.ylabel("Dot Product Result")
plt.title("Dot Product: Result vs Array Size")
plt.xscale("log", base=2)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("dot_result_vs_size.png")
plt.show()
