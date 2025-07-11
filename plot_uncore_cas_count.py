import matplotlib.pyplot as plt
import pandas as pd

# Load and clean data
df = pd.read_csv("pointer_chase_cache_profile.csv")
df.columns = df.columns.str.strip()

# Average over trials
df_avg = df.groupby("N").mean().reset_index()

# Cache level boundaries in bytes
cache_sizes = {
    'L1': 80 * 1024,
    'L2': 2 * 1024**2,
    'L3': 105 * 1024**2,
    'DRAM': 416 * 1024**2
}

# Set up the plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot uncore CAS read and write counters
ax.plot(df_avg["N"], df_avg["unc_m_cas_count.rd"] / 1e6, marker='o', linestyle='-', color='#1f77b4', label="Read CAS (unc_m_cas_count.rd)")
ax.plot(df_avg["N"], df_avg["unc_m_cas_count.wr"] / 1e6, marker='x', linestyle='--', color='#ff7f0e', label="Write CAS (unc_m_cas_count.wr)")

# Vertical lines for cache boundaries
for label, xpos in cache_sizes.items():
    ax.axvline(x=xpos, color='red', linestyle='--')
    ax.text(xpos, ax.get_ylim()[1]*0.05, label, color='red', fontsize=10, ha='right', rotation=0)

# Labels and scales
ax.set_xlabel("Array Size N")
ax.set_ylabel("CAS Events (Millions)")
ax.set_xscale('log', base=2)
ax.set_title("DRAM Read vs Write Activity from Uncore CAS Counters")
ax.grid(True)
ax.legend()
ax.set_yscale('log', base=2)

plt.tight_layout()
plt.savefig("uncore_cas_read_vs_write_plot.png")
plt.show()
