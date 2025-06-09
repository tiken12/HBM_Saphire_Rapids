import matplotlib.pyplot as plt
import csv

strides = []
bandwidths = []

with open("daxpy_strided_results.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        strides.append(int(row["Stride"]))
        bandwidths.append(float(row["Bandwidth (GB/s)"]))

# Kenneth: Update all relevant plots to use the enhancements we developed:
#           Verified that units are in fact GBps.
#           Perf bandwidth was reporting cache misses, not bandwidth.
#           Switched to log_2 scale on x-axis to see things more clearly.
#           Added cache thresholds to chart.
#           Use violin instead of averaging results.
plt.figure(figsize=(8, 5))
plt.plot(strides, bandwidths, marker='o', linewidth=2)
plt.xlabel("Stride")
plt.ylabel("Bandwidth (GB/s)")
plt.title("Memory Bandwidth vs. Stride")
plt.grid(True)
plt.xticks(strides)
plt.tight_layout()
plt.savefig("stride_bandwidth_plot.png")
plt.show()
