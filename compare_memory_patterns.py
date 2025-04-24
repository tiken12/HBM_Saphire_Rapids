import matplotlib.pyplot as plt
import csv

def read_csv(filename):
    x, y = [], []
    with open(filename, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header if exists
        for row in reader:
            x.append(int(row[0]))
            y.append(float(row[2]) if 'bandwidth' in filename else float(row[1]))
    return x, y

# Load data
stride_x, stride_y = read_csv("daxpy_strided_results.csv")
scale_x, scale_y = read_csv("daxpy_scale_results.csv")
pointer_x, pointer_y = read_csv("pointer_chase_results.csv")

# Plot bandwidth patterns
plt.figure(figsize=(10, 6))

plt.plot(scale_x, scale_y, label='DAXPY (Streaming)', marker='o')
plt.plot(stride_x, stride_y, label='Strided Access', marker='s')
plt.plot(pointer_x, [1.0 / t for t in pointer_y], label='Pointer Chase (Est. Accesses/sec)', marker='^')

plt.xscale("log")
plt.xlabel("Data Size / Stride")
plt.ylabel("Performance (GB/s or 1/sec)")
plt.title("Memory Access Pattern Comparison")
plt.legend()
plt.grid(True, which='both', linestyle='--')
plt.tight_layout()
plt.savefig("memory_access_comparison.png")
plt.show()
