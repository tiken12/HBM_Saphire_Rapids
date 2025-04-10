import subprocess
import time

# Estimated cache line size in bytes (usually 64B)
CACHE_LINE_SIZE = 64
SLEEP_SECONDS = 1

# Define events to test
uncore_events = {
    "spr_unc_cha58": "UNC_CHA_IMC_READS_COUNT/",
    "spr_unc_cha58": "UNC_CHA_IMC_WRITES_COUNT/",
    "spr_unc_cha59": "UNC_CHA_IMC_READS_COUNT/",
    "spr_unc_cha59": "UNC_CHA_IMC_WRITES_COUNT/",
    "spr_unc_cha59": "UNC_CHA_CLOCKTICKS/",
    "spr_unc_cha59": "UNC_CHA_CORE_SNP/",
}

print("\n Testing CHA-based uncore events using `perf stat`...\n")

results = {}

def run_perf(event_name, event_cmd):
    try:
        result = subprocess.run(
            ["perf", "stat", "-e", event_cmd, "sleep", str(SLEEP_SECONDS)],
            capture_output=True,
            text=True,
            timeout=SLEEP_SECONDS + 2
        )

        stderr = result.stderr
        if "not supported" in stderr.lower() or "unknown event" in stderr.lower():
            print(f"❌ {event_name} not supported")
            results[event_name] = None
            return

        # Parse the perf stat output
        for line in stderr.splitlines():
            if event_cmd.split('/')[1] in line:
                value_str = line.strip().split()[0].replace(',', '')
                try:
                    value = int(value_str)
                    print(f"✅ {event_name}: {value}")
                    results[event_name] = value
                    return
                except ValueError:
                    continue

        print(f"⚠️  {event_name} ran but value not found.")
        results[event_name] = None

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout for {event_name}")
        results[event_name] = None
    except Exception as e:
        print(f"❌ Error for {event_name}: {e}")
        results[event_name] = None

# Run all tests
for name, perf_event in uncore_events.items():
    run_perf(name, perf_event)

# Compute estimated bandwidth
print("\n📊 Estimated Memory Bandwidth (per CHA):")
for cha in ["CHA58", "CHA59"]:
    rd = results.get(f"{cha}_IMC_READS")
    wr = results.get(f"{cha}_IMC_WRITES")
    if rd is not None and wr is not None:
        total_bytes = (rd + wr) * CACHE_LINE_SIZE
        bw_MBps = total_bytes / SLEEP_SECONDS / (1024 * 1024)
        print(f"💡 {cha}: {bw_MBps:.2f} MB/s")
    else:
        print(f"⚠️  {cha}: insufficient data to compute bandwidth")

print("\n✅ Script complete.")
