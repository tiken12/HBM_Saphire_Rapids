import subprocess
import csv
import re

# Events to track with perf
events = [
    "instructions",
    "cycles",
    "cache-misses",
    "cache-references",
    "LLC-loads",
    "LLC-load-misses"
]

# Sizes and trials
sizes = [1_000_000, 10_000_000, 50_000_000]
trials = 5
output_csv = "pointer_chase_perf_results.csv"

# Compile perf event string
event_str = ",".join(events)

# Header for CSV
csv_header = ["N"] + events

def run_perf(N):
    # Run perf with the current problem size
    command = [
        "perf", "stat",
        "-e", event_str,
        "python3", "pointer_chase.py"
    ]
    env = {"N": str(N)}
    
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    output = result.stderr  # perf writes to stderr

    stats = [N]
    for event in events:
        # Regex to match event line: <value> <event-name>
        match = re.search(rf"(\d+[,\d+]*)\s+{event}", output)
        if match:
            value = match.group(1).replace(",", "")
            stats.append(int(value))
        else:
            stats.append(None)

    return stats

# Run and collect data
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)

    for N in sizes:
        print(f"Running perf for N = {N}")
        stats = run_perf(N)
        writer.writerow(stats)

print(f"\nPerf results saved to: {output_csv}")
