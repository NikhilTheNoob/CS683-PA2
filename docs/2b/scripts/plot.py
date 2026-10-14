#!/usr/bin/env python3
"""Parse docs/2b/results/*.txt, write docs/2b/task2b-data.md and the plots in docs/2b/.

Usage: python3 docs/2b/scripts/plot.py   (needs matplotlib)
"""
import math
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "results")

TRACES = ["Trace1", "Trace2", "Trace3"]
THRESHOLDS = [100, 200, 250, 350, 500]
CONFIGS = ["rrip", "irrip"] + ["dyn_irrip_t%d" % t for t in THRESHOLDS]
LABELS = {"rrip": "RRIP", "irrip": "I-RRIP"}
LABELS.update({"dyn_irrip_t%d" % t: "Dyn I-RRIP (%.2f)" % (t / 1000) for t in THRESHOLDS})


def parse(path):
    """Pull ROI stats out of one ChampSim output file."""
    text = open(path).read()
    roi = text.split("Region of Interest Statistics")[1]
    num = r"([-+0-9.eE]+|-?nan|inf)"
    d = {
        "ipc": float(re.search(r"CPU 0 cumulative IPC: " + num, roi).group(1)),
        "l2c_load_mpki": float(re.search(r"L2C LOAD .*?MPKI: " + num, roi).group(1)),
        "l2c_instr_mpki": float(re.search(r"L2C INSTRUCTION LOAD MPKI: " + num, roi).group(1)),
        "l2c_data_mpki": float(re.search(r"L2C DATA LOAD MPKI: " + num, roi).group(1)),
    }
    m_i = re.search(r"DYN_IRRIP epochs in I-RRIP mode: (\d+)", text)
    m_r = re.search(r"DYN_IRRIP epochs in RRIP mode: (\d+)", text)
    if m_i and m_r:
        tot = int(m_i.group(1)) + int(m_r.group(1))
        d["irrip_epoch_pct"] = 100.0 * int(m_i.group(1)) / tot if tot else 0.0
    return d


data = {(t, c): parse(os.path.join(RES, "%s_%s.txt" % (t, c))) for t in TRACES for c in CONFIGS}
for (t, c), d in data.items():
    d["speedup"] = d["ipc"] / data[(t, "rrip")]["ipc"]
    d["speedup_pct"] = (d["speedup"] - 1) * 100


def geomean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


# ---------------- table ----------------
lines = [
    "# Task 2b: Dynamic I-RRIP data",
    "",
    "Baseline: standard RRIP (no L1D prefetcher). 25M warmup / 25M simulated instructions. Built with GCC 7.5 (docker/Dockerfile).",
    "Dyn I-RRIP (x) = dynamic I-RRIP with threshold x. Epochs in I-RRIP = % of 4096-access epochs that ended in I-RRIP mode.",
    "",
    "| Trace | Policy | IPC | Speedup vs RRIP | L2C Load MPKI | L2 Instruction Load MPKI | L2 Data Load MPKI | Epochs in I-RRIP |",
    "|---|---|---:|---:|---:|---:|---:|---:|",
]
for t in TRACES:
    for c in CONFIGS:
        d = data[(t, c)]
        ep = "%.1f%%" % d["irrip_epoch_pct"] if "irrip_epoch_pct" in d else "-"
        lines.append("| %s | %s | %.6f | %.4f | %.5f | %.5f | %.5f | %s |" % (
            t, LABELS[c], d["ipc"], d["speedup"], d["l2c_load_mpki"],
            d["l2c_instr_mpki"], d["l2c_data_mpki"], ep))
lines += ["", "## Geometric mean speedup over RRIP", "", "| Policy | Geomean speedup |", "|---|---:|"]
for c in CONFIGS:
    lines.append("| %s | %.4f |" % (LABELS[c], geomean([data[(t, c)]["speedup"] for t in TRACES])))
open(os.path.join(ROOT, "task2b-data.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))


# ---------------- plots ----------------
def bar_plot(key, ylabel, title, fname, configs, baseline_line=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    w = 0.8 / len(configs)
    for i, c in enumerate(configs):
        xs = [j + (i - (len(configs) - 1) / 2) * w for j in range(len(TRACES))]
        ax.bar(xs, [data[(t, c)][key] for t in TRACES], w, label=LABELS[c], edgecolor="black", linewidth=0.5)
    if baseline_line is not None:
        ax.axhline(baseline_line, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(range(len(TRACES)))
    ax.set_xticklabels(TRACES)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.set_axisbelow(True)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, fname), dpi=120)
    plt.close(fig)


dyn = ["dyn_irrip_t%d" % t for t in THRESHOLDS]
bar_plot("ipc", "IPC", "Task 2b: IPC", "ipc.png", CONFIGS)
bar_plot("speedup_pct", "Speedup over RRIP (%)", "Task 2b: Speedup over RRIP", "speedup.png", ["irrip"] + dyn, baseline_line=0.0)
bar_plot("l2c_load_mpki", "L2C Load MPKI", "Task 2b: L2C Load MPKI", "l2c-load-mpki.png", CONFIGS)
bar_plot("l2c_instr_mpki", "L2 Instruction Load MPKI", "Task 2b: L2 Instruction Load MPKI", "l2-instruction-load-mpki.png", CONFIGS)
bar_plot("l2c_data_mpki", "L2 Data Load MPKI", "Task 2b: L2 Data Load MPKI", "l2-data-load-mpki.png", CONFIGS)

# sensitivity: speedup vs threshold, one line per trace + geomean
fig, ax = plt.subplots(figsize=(8, 5))
xs = [t / 1000 for t in THRESHOLDS]
for t in TRACES:
    ax.plot(xs, [data[(t, c)]["speedup"] for c in dyn], marker="o", label=t)
ax.plot(xs, [geomean([data[(t, c)]["speedup"] for t in TRACES]) for c in dyn],
        marker="s", color="black", linestyle="--", label="Geomean")
ax.axhline(1.0, color="grey", linewidth=0.8)
ax.set_xticks(xs)
ax.set_xlabel("Threshold")
ax.set_ylabel("Speedup over RRIP")
ax.set_title("Task 2b: Threshold sensitivity")
ax.grid(linestyle=":", alpha=0.6)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "sensitivity.png"), dpi=120)
plt.close(fig)
