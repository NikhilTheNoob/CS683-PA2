#!/usr/bin/env python3
"""Parse docs/1/results/*.txt and write docs/1/task1b-data.md and the Task 1 plots.

Usage: python3 docs/1/scripts/plot.py   (needs matplotlib)
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
CONFIGS = ["no", "ipstride", "spp"]
LABELS = {"no": "No prefetcher", "ipstride": "IP-stride", "spp": "SPP"}


def num(pattern, text):
    m = re.search(pattern, text, re.M)
    return float(m.group(1)) if m else None


def parse(path):
    text = open(path).read()
    roi = text.split("Warmup complete")[-1]
    d = {
        "ipc": num(r"CPU 0 cumulative IPC: ([\d.]+)", roi),
        "load_miss": num(r"^L1D LOAD .*MISS:\s+(\d+)", roi),
        "mpki": num(r"^L1D LOAD .*MPKI: ([\d.]+)", roi),
        "useful": num(r"L1D USEFUL LOAD PREFETCHES:\s+(\d+)", roi) or 0,
        "lower": num(r"L1D USEFUL LOAD PREFETCHES:.*LOWER LEVEL:\s+(\d+)", roi) or 0,
        "to_l2": num(r"L1D PREFETCHES SAME FILL-ORIGIN LEVEL:.*DIFFERENT FILL-ORIGIN LEVEL: (\d+)", roi) or 0,
    }
    for mode in ("uniform", "pattern"):
        m = re.search(r"SPP %s prefetches filled into L1D: (\d+) useful: (\d+)" % mode, text)
        if m and int(m.group(1)):
            d[mode + "_acc"] = 100.0 * int(m.group(2)) / int(m.group(1))
    return d


data = {(t, c): parse(os.path.join(RES, "%s_%s.txt" % (t, c))) for t in TRACES for c in CONFIGS}
for t in TRACES:
    base = data[(t, "no")]
    for c in CONFIGS:
        d = data[(t, c)]
        d["speedup"] = d["ipc"] / base["ipc"]
        d["coverage"] = 100.0 * (base["load_miss"] - d["load_miss"]) / base["load_miss"]
        if d["lower"]:
            d["acc"] = 100.0 * d["useful"] / d["lower"]
            d["acc_l1"] = 100.0 * d["useful"] / (d["lower"] - d["to_l2"])
            d["to_l2_pct"] = 100.0 * d["to_l2"] / d["lower"]


def geomean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


def fmt(d, k, f="%.1f%%"):
    return f % d[k] if k in d else "-"


lines = [
    "# Task 1: IP-stride vs SPP",
    "",
    "25M warmup + 25M simulated instructions, L1D prefetcher only, LRU everywhere, GCC 7.5 (Ubuntu 20.04 package).",
    "Regenerate with `docs/1/scripts/run.sh` and then `python3 docs/1/scripts/plot.py`; raw output is in `results/`.",
    "",
    "* **Speedup**: IPC / IPC with no prefetcher.",
    "* **Accuracy**: ChampSim's L1D accuracy, useful prefetches / prefetches that missed L1D and went to L2.",
    "* **Accuracy excl. L2 fills**: the same, but without prefetches issued with `FILL_L2` under MSHR pressure. Those never fill L1D, so they can never count as useful there. **To L2** is their share.",
    "* **Uniform / pattern accuracy**: useful / filled into L1D, for prefetches issued by each SPP mode.",
    "* **Coverage**: fraction of the no-prefetcher L1D load misses removed.",
    "",
    "| Trace | Prefetcher | IPC | Speedup | L1D load MPKI | Accuracy | Accuracy excl. L2 fills | To L2 | Uniform acc. | Pattern acc. | Coverage |",
    "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
]
for t in TRACES:
    for c in CONFIGS:
        d = data[(t, c)]
        lines.append("| %s | %s | %.6f | %.4f | %.4f | %s | %s | %s | %s | %s | %s |" % (
            t, LABELS[c], d["ipc"], d["speedup"], d["mpki"], fmt(d, "acc"), fmt(d, "acc_l1"),
            fmt(d, "to_l2_pct"), fmt(d, "uniform_acc"), fmt(d, "pattern_acc"),
            "-" if c == "no" else "%.1f%%" % d["coverage"]))
lines += ["", "| Prefetcher | Geomean speedup |", "|---|---:|"]
for c in CONFIGS:
    lines.append("| %s | %.4f |" % (LABELS[c], geomean([data[(t, c)]["speedup"] for t in TRACES])))
lines += [
    "",
    "## SPP storage",
    "",
    "Hardware bit widths (not C++ type widths). The L1D has 64 sets x 12 ways = 768 lines.",
    "",
    "| Structure | Field | Bits | Why |",
    "|---|---|---:|---|",
    "| IP table entry (x64) | `ip` tag | 8 | low 8 IP bits; a wider tag was measured to hurt, see below |",
    "| | `last_cl_addr` | 16 | low 16 bits of the line address; stride = sign-extended difference |",
    "| | `last_stride` | 16 | range of a 16-bit difference |",
    "| | `lru` | 6 | log2(64), fully associative |",
    "| | `conf` | 2 | saturating at 3 |",
    "| | `sig` | 12 | last 3 strides x 4 bits |",
    "| **IP table** | 64 x 60 | **3,840** | |",
    "| Pattern table entry (x4096) | `next_stride` | 4 | -8..+7 |",
    "| | `conf` | 2 | saturating at 3 |",
    "| **Pattern table** | 4096 x 6 | **24,576** | |",
    "| Throttle (per mode, x2) | degree level | 2 | 4 levels: 1/2/4/8 |",
    "| | epoch fill counter | 7 | 0..64 |",
    "| | epoch useful counter | 7 | 0..64 |",
    "| **Throttle** | 2 x 16 | **32** | |",
    "| L1D line (x768) | prefetch mode bit | 1 | uniform or pattern, so useful hits can be credited per mode |",
    "| **L1D extra state** | 768 x 1 | **768** | |",
    "| **Total** | | **29,216** | about 3.6 KB |",
    "",
    "The IP table uses an 8-bit tag on purpose. The traces have about 13,000-17,000 distinct load IPs per",
    "100k L1D accesses (Trace1, Trace3), far more than any affordable table holds; grouping IPs that share",
    "their low 8 bits lets an entry learn a stride before it is evicted. A 12-bit hashed tag lowered the",
    "geomean speedup from 1.0149 to 1.0119, and set-associative 8x8 / 16x4 organisations cost 0.06-0.10%.",
]
open(os.path.join(ROOT, "task1b-data.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))


def bar(key, ylabel, title, fname, configs, ref=None, pct=False):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    w = 0.8 / len(configs)
    for i, c in enumerate(configs):
        xs = [j + (i - (len(configs) - 1) / 2) * w for j in range(len(TRACES))]
        ax.bar(xs, [data[(t, c)][key] for t in TRACES], w, label=LABELS[c], edgecolor="black", linewidth=0.5)
    if ref is not None:
        ax.axhline(ref, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(range(len(TRACES)))
    ax.set_xticklabels(TRACES)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9)
    if key == "speedup":
        lo = min(data[(t, c)][key] for t in TRACES for c in configs)
        hi = max(data[(t, c)][key] for t in TRACES for c in configs)
        ax.set_ylim(min(0.995, lo - 0.002), hi + 0.004)
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, fname), dpi=120)
    plt.close(fig)


bar("speedup", "Speedup (IPC / no-prefetcher IPC)", "Task 1: Speedup over no prefetching", "speedup.png", ["ipstride", "spp"], ref=1.0)
bar("mpki", "L1D load MPKI", "Task 1: L1D load MPKI", "load_mpki.png", CONFIGS)
bar("acc", "L1D prefetch accuracy (%)", "Task 1: L1D prefetch accuracy", "accuracy.png", ["ipstride", "spp"])
bar("coverage", "L1D coverage (%)", "Task 1: L1D coverage", "coverage.png", ["ipstride", "spp"])
