#!/usr/bin/env python3
"""Parse docs/3/results/*.txt and write docs/3/task3-data.md and the Task 3 plots.

Usage: python3 docs/3/scripts/plot.py   (needs matplotlib)
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
CONFIGS = ["no", "spp_lru", "spp_rrip", "dyn", "spp_dyn_plain", "spp_dyn"]
LABELS = {
    "no": "No prefetcher + LRU",
    "spp_lru": "SPP + LRU",
    "spp_rrip": "SPP + RRIP",
    "dyn": "Dyn I-RRIP (no prefetcher)",
    "spp_dyn_plain": "SPP + Dyn I-RRIP (not prefetch-aware)",
    "spp_dyn": "SPP + prefetch-aware Dyn I-RRIP",
}


def num(pattern, text):
    m = re.search(pattern, text, re.M)
    return float(m.group(1)) if m else None


def parse(path):
    roi = open(path).read().split("Warmup complete")[-1]
    return {
        "ipc": num(r"CPU 0 cumulative IPC: ([\d.]+)", roi),
        "l1_miss": num(r"^L1D LOAD .*MISS:\s+(\d+)", roi),
        "l1_mpki": num(r"^L1D LOAD .*MPKI: ([\d.]+)", roi),
        "useful": num(r"L1D USEFUL LOAD PREFETCHES:\s+(\d+)", roi) or 0,
        "lower": num(r"L1D USEFUL LOAD PREFETCHES:.*LOWER LEVEL:\s+(\d+)", roi) or 0,
        "l2_mpki": num(r"^L2C LOAD .*MPKI: ([\d.]+)", roi),
        "l2i_mpki": num(r"L2C INSTRUCTION LOAD MPKI: ([\d.]+)", roi),
        "l2d_mpki": num(r"L2C DATA LOAD MPKI: ([\d.]+)", roi),
    }


data = {(t, c): parse(os.path.join(RES, "%s_%s.txt" % (t, c))) for t in TRACES for c in CONFIGS}
for t in TRACES:
    base = data[(t, "no")]
    for c in CONFIGS:
        d = data[(t, c)]
        d["speedup"] = d["ipc"] / base["ipc"]
        if d["lower"]:
            d["acc"] = 100.0 * d["useful"] / d["lower"]
            d["cov"] = 100.0 * (base["l1_miss"] - d["l1_miss"]) / base["l1_miss"]


def geomean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


def pct(d, k):
    return "%.1f%%" % d[k] if k in d else "-"


lines = [
    "# Task 3: SPP + prefetch-aware dynamic I-RRIP",
    "",
    "25M warmup + 25M simulated instructions, GCC 7.5 (Ubuntu 20.04 package). Speedup is IPC over no prefetcher + LRU.",
    "Accuracy and coverage are for the L1D prefetcher; coverage is the fraction of the no-prefetcher L1D load misses removed.",
    "Regenerate with `docs/3/scripts/run.sh` and then `python3 docs/3/scripts/plot.py`; raw output is in `results/`.",
    "",
    "| Trace | Configuration | IPC | Speedup | L1D acc. | L1D cov. | L1D load MPKI | L2C load MPKI | L2 instr. load MPKI | L2 data load MPKI |",
    "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
]
for t in TRACES:
    for c in CONFIGS:
        d = data[(t, c)]
        lines.append("| %s | %s | %.6f | %.4f | %s | %s | %.3f | %.3f | %.3f | %.3f |" % (
            t, LABELS[c], d["ipc"], d["speedup"], pct(d, "acc"), pct(d, "cov"),
            d["l1_mpki"], d["l2_mpki"], d["l2i_mpki"], d["l2d_mpki"]))
lines += ["", "## Speedup of SPP + prefetch-aware Dyn I-RRIP over each reference", "",
          "| Reference | Trace1 | Trace2 | Trace3 | Geomean |", "|---|---:|---:|---:|---:|"]
for ref in ["spp_lru", "spp_rrip", "dyn", "spp_dyn_plain"]:
    r = [data[(t, "spp_dyn")]["ipc"] / data[(t, ref)]["ipc"] for t in TRACES]
    lines.append("| %s | %s | %.4f |" % (LABELS[ref], " | ".join("%.4f" % x for x in r), geomean(r)))
lines += ["", "| Configuration | Geomean speedup over no prefetcher |", "|---|---:|"]
for c in CONFIGS:
    lines.append("| %s | %.4f |" % (LABELS[c], geomean([data[(t, c)]["speedup"] for t in TRACES])))
open(os.path.join(ROOT, "task3-data.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))


def bar(key, ylabel, title, fname, configs, ref=None):
    fig, ax = plt.subplots(figsize=(10, 5))
    w = 0.8 / len(configs)
    for i, c in enumerate(configs):
        xs = [j + (i - (len(configs) - 1) / 2) * w for j in range(len(TRACES))]
        ax.bar(xs, [data[(t, c)][key] for t in TRACES], w, label=LABELS[c], edgecolor="black", linewidth=0.5)
    if ref is not None:
        ax.axhline(ref, color="black", linewidth=0.8, linestyle="--")
    if key == "speedup":
        vals = [data[(t, c)][key] for t in TRACES for c in configs]
        ax.set_ylim(min(0.995, min(vals) - 0.002), max(vals) + 0.006)
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


ALL = CONFIGS[1:]
PF = ["spp_lru", "spp_rrip", "spp_dyn_plain", "spp_dyn"]
bar("speedup", "Speedup over no prefetcher + LRU", "Task 3: Speedup", "speedup.png", ALL, ref=1.0)
bar("acc", "L1D prefetch accuracy (%)", "Task 3: L1D prefetch accuracy", "accuracy.png", PF)
bar("cov", "L1D coverage (%)", "Task 3: L1D coverage", "coverage.png", PF)
bar("l1_mpki", "L1D load MPKI", "Task 3: L1D load MPKI", "l1d-load-mpki.png", CONFIGS)
bar("l2_mpki", "L2C load MPKI", "Task 3: L2C load MPKI", "l2c-load-mpki.png", CONFIGS)
bar("l2i_mpki", "L2 instruction load MPKI", "Task 3: L2 instruction load MPKI", "l2-instruction-load-mpki.png", CONFIGS)
bar("l2d_mpki", "L2 data load MPKI", "Task 3: L2 data load MPKI", "l2-data-load-mpki.png", CONFIGS)
