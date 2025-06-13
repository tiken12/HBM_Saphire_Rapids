import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Load and clean data
df = pd.read_csv("pointer_chase_cache_profile.csv")
df.columns = df.columns.str.strip()
df["Perf_Bandwidth_GBps"] = df["Perf_Bandwidth_GBps"].fillna(0)

# Average over trials
df_avg = df.groupby("N").mean().reset_index()

cache_sizes = {
    'L1': 80 * 1024,       # 80 KB
    'L2': 2 * 1024**2,     # 2 MB
    'L3': 105 * 1024**2    # 105 MB
}


def violinplot_color(bandwidth_col, color, ax):

    x_vals = sorted(df['N'].unique())

    for x in x_vals:
        data = df[df['N'] == x][bandwidth_col]
        vp = ax.violinplot(dataset=data, positions=[x], widths=x*0.4, showmeans=False, showmedians=True)   
        # Set violin body color
        for pc in vp['bodies']:
            pc.set_facecolor(color)
            pc.set_edgecolor(color)
            # pc.set_alpha(1)
        
        # Set median line color
        if 'cmedians' in vp:
            vp['cmedians'].set_color(color)
        
        # Set bar lines (min/max) color
        if 'cbars' in vp:
            vp['cbars'].set_color(color)
        
        # Set cap lines (the horizontal lines at min/max)
        if 'cmins' in vp:
            vp['cmins'].set_color(color)
        if 'cmaxes' in vp:
            vp['cmaxes'].set_color(color)


# Set up dual Y-axis
fig, ax1 = plt.subplots(figsize=(12, 6))

#sns.violinplot(data=df, x="N", y="App_Bandwidth_GBps", scale="width", inner="quartile")

# App-Derived on left y-axis
color1 = '#1f77b4'
ax1.set_xlabel("Array Size N")
ax1.set_ylabel("App-Derived Bandwidth (GB/s)", color=color1)
ax1.plot(df_avg["N"], df_avg["App_Bandwidth_GBps"], marker='o', linestyle='-', color=color1, label="App-Derived Bandwidth")
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True)
violinplot_color("App_Bandwidth_GBps", color1, ax1)

# Perf-Derived on right y-axis
ax2 = ax1.twinx()
color2 = '#ff7f0e'
ax2.set_ylabel("Perf-Derived Bandwidth (GB/s)", color=color2)
ax2.plot(df_avg["N"], df_avg["Perf_Bandwidth_GBps"], marker='x', linestyle='--', color=color2, label="Perf-Derived Bandwidth")
ax2.tick_params(axis='y', labelcolor=color2)
violinplot_color("Perf_Bandwidth_GBps", color2, ax2)

for label, xpos in cache_sizes.items():
    plt.axvline(x=xpos, color='red', linestyle='--')
    plt.text(xpos, plt.ylim()[1]*0.05, label, color='red', fontsize=10, ha='right')

# Title and layout
plt.title("Pointer Chase Cache Profile: App vs Perf Bandwidth")
plt.xscale('log', base=2)
fig.tight_layout()
plt.savefig("pointer_chase_bandwidth_dual_yaxis.png")
plt.show()
