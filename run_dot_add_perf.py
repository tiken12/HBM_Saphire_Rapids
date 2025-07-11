import subprocess
import csv
from pathlib import Path
import math

def generate_sizes(max_limit=2**28):
    sizes = []
    for i in range(10, int(math.log2(max_limit)) + 1):
        sizes.append(2 ** i)
        sizes.append(int(2 ** i * 1.5))
    return sorted(set(sizes))

def run_benchmark(exe_path, mode, output_csv, trials=5):
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Mode", "N", "Repeat", "Elapsed(s)", "Bandwidth(GB/s)", "Result(if dot)"])

    for N in generate_sizes():
        repeat = max(1, 10_000_000 // N)
        for _ in range(trials):
            command = [exe_path, str(N), str(repeat), mode, output_csv]
            subprocess.run(command)

if __name__ == "__main__":
    run_benchmark("./dot_add_benchmark", mode="dot", output_csv="results/dot_product_results.csv")
    run_benchmark("./dot_add_benchmark", mode="add", output_csv="results/vector_add_results.csv")
