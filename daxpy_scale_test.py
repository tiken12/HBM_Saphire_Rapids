from daxpy_benchmark import daxpy_benchmark

if __name__ == "__main__":
    for N in [5_000, 1_000_000, 10_000_000, 100_000_000, 150_000_000]:
        print(f"\n--- Vector Size: {N:,} ---")
        daxpy_benchmark(N)
