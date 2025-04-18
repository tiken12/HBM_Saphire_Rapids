import csv
import os
from datetime import datetime
import subprocess
import time

# Estimated cache line size in bytes
CACHE_LINE_SIZE = 64
SLEEP_SECONDS = 1
CSV_FILE = "cha_bandwidth_metrics.csv"

# Define events to test
uncore_events = {
        "CHA58_READS": "unc_c_cha_58/UNC_CHA_IMC_READS_COUNT/",
    "CHA58_WRITES": "unc_c_cha_58/UNC_CHA_IMC_WRITES_COUNT/",
    "CHA59_READS": "unc_c_cha_59/UNC_CHA_IMC_READS_COUNT/",
    "CHA59_WRITES": "unc_c_cha_59/UNC_CHA_IMC_WRITES_COUNT/",
    "CHA59_CLOCK": "unc_c_cha_59/UNC_CHA_CLOCKTICKS/",
    "CHA59_SNP": "unc_c_cha_59/UNC_CHA_CORE_SNP/",
    "IMC_READS": "unc_m_cas_count.rd",
    "IMC_WRITES": "unc_m_cas_count.wr",
    "HBM_CAS": "uncore_hbm_0/UNC_HBM_CAS_COUNT/"
}

print("\n Testing CHA-based uncore events using `perf stat`...\n")

results = {}


with open(CSV_FILE, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["timestamp", "source", "reads", "writes", "bandwidth_MBps"])

    def run_perf(event_name, event_cmd):
        try:
            result = subprocess.run(
                ["perf", "stat","-a","-C","0","-e", event_cmd, "sleep", str(SLEEP_SECONDS)],
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                universal_newlines = True,
                timeout=SLEEP_SECONDS + 2
            )

            stderr = result.stderr
            if "not supported" in stderr.lower() or "unknown event" in stderr.lower():
                print(f"❌ {event_name} not supported")
                results[event_name] = None
                return

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

    # Run all events
    for name, perf_event in uncore_events.items():
        run_perf(name, perf_event)

    timestamp = datetime.now().isoformat()

    # CHA 58
    rd = results.get("CHA58_READS", 0)
    wr = results.get("CHA58_WRITES", 0)
    if rd is not None and wr is not None:
        total_bytes = (rd + wr) * CACHE_LINE_SIZE
        bw_MBps = total_bytes / SLEEP_SECONDS / (1024 * 1024)
        writer.writerow([timestamp, "CHA58", rd, wr, f"{bw_MBps:.2f}"])

    # CHA 59
    rd = results.get("CHA59_READS", 0)
    wr = results.get("CHA59_WRITES", 0)
    if rd is not None and wr is not None:
        total_bytes = (rd + wr) * CACHE_LINE_SIZE
        bw_MBps = total_bytes / SLEEP_SECONDS / (1024 * 1024)
        writer.writerow([timestamp, "CHA59", rd, wr, f"{bw_MBps:.2f}"])

    # IMC Bandwidth
    rd = results.get("IMC_READS", 0)
    wr = results.get("IMC_WRITES", 0)
    if rd is not None and wr is not None:
        total_bytes = (rd + wr) * CACHE_LINE_SIZE
        bw_MBps = total_bytes / SLEEP_SECONDS / (1024 * 1024)
        writer.writerow([timestamp, "IMC", rd, wr, f"{bw_MBps:.2f}"])

    # HBM CAS Total
    hbm = results.get("HBM_CAS", 0)
    if hbm is not None:
        total_bytes = hbm * CACHE_LINE_SIZE
        bw_MBps = total_bytes / SLEEP_SECONDS / (1024 * 1024)
        writer.writerow([timestamp, "HBM", hbm, 0, f"{bw_MBps:.2f}"])

print("\n✅ Script complete. Results saved to:", CSV_FILE)
