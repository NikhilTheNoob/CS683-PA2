# Task 2b: Dynamic I-RRIP

Implementation: `replacement/dyn_irrip.l2c_repl`
Data table: `task2b-data.md` | Plots: `*.png` | Raw ChampSim output: `results/`

## How to reproduce

Everything is built with GCC 7 inside Docker (`docker/Dockerfile`, Ubuntu 18.04, g++ 7.5):

```bash
./docker/run.sh ./docs/2b/scripts/all.sh
```

`all.sh` runs these three steps, which can also be run on their own:

```bash
./docs/2b/scripts/build.sh          # builds RRIP, I-RRIP, Dyn I-RRIP @ 0.10/0.20/0.25/0.35/0.50
./docs/2b/scripts/run.sh            # 3 traces x 7 configs, 25M warmup + 25M sim, in parallel
python3 docs/2b/scripts/plot.py     # writes task2b-data.md and the plots (needs matplotlib)
```

Traces go in `traces/` as `TraceN.champsimtrace.gz`.

## Design

### Two modes
* **I-RRIP mode** is the Task 2a policy. Instruction lines are inserted at RRPV 1 and data lines at RRPV 2. On eviction, a data line at maxRRPV is chosen before an instruction line at maxRRPV. Hits are promoted to RRPV 0.
* **RRIP mode** is plain SRRIP. Every line is inserted at RRPV 2, the first line at maxRRPV is evicted, and hits are promoted to RRPV 0.

### Leader sets
32 of the 1024 L2 sets (`set % 32 == 0`) are leaders and **always** run RRIP. The other 992 sets are followers and use whichever mode the monitor selects.

On every non-writeback access to a leader set, the monitor counts:

| Counter | Incremented when |
|---|---|
| `instr_access` | access to an instruction line |
| `instr_miss` | miss on an instruction line |
| `total_access` | any access |
| `total_miss` | any miss |

Writebacks are excluded because they are not demand accesses and carry no information about instruction pressure.

**Why the leaders run RRIP.** The leaders estimate how instruction-heavy the L2 traffic is under a policy that does not favour instructions. If they ran I-RRIP, protected instruction lines would hit more often, which would understate instruction misses and bias the measurement toward whatever mode is already active.

**Why 32 leader sets (about 3% of the cache).**
* *Cost.* Leader sets never get instruction protection, so when I-RRIP is the better policy those 3% of sets lose out. With 32 leaders the loss is small. On Trace2, Dyn I-RRIP (0.25) reaches a 1.47% speedup against 1.52% for static I-RRIP; part of that 0.05% gap is the leader sets.
* *Accuracy.* The monitor needs enough samples to react within a phase. With 32 leaders, about 1 in 32 L2 accesses trains the monitor, so a 4096-access epoch corresponds to about 130K L2 accesses. That is short compared with the program phases we care about, and long enough to average out noise.
* *Coverage.* Using `set % 32` spreads the leaders evenly over the index space, so they are not clustered in one region of the address space. 16 leaders would halve the sample rate. 64 would double the number of sets that never get instruction protection.

### Decision logic
```
score = (instr_access + instr_miss) / (total_access + total_miss)
followers use I-RRIP  if score > THRESHOLD, else RRIP
```
This is the formula from the handout. Adding misses to accesses means an instruction stream that keeps **missing** counts twice as much as one that hits. That is the case where protecting instruction lines helps: if instructions already hit under RRIP, there is little to gain from protecting them. The comparison is done in integers as `(ia+im)*1000 > (ta+tm)*THRESHOLD_PERMILLE`, as hardware would do it, with no division.

**Phase adaptation.** Every 4096 leader accesses, all four counters are halved. This makes the score an exponentially weighted moving average, so old phases fade out and the policy can switch back. It also bounds every counter below 2·4096, so each one fits in 14 bits.

**Hardware cost:** 4 counters × 14 bits + a 12-bit epoch counter = **68 bits**, on top of the RRPV bits that RRIP already has. Leader sets are identified by the set-index bits, so they need no storage.

## Results (speedup over RRIP)

Built with GCC 7.5 in the Docker image. The RRIP and I-RRIP rows match the Task 2a numbers exactly.

| Trace | I-RRIP | Dyn 0.10 | Dyn 0.20 | Dyn 0.25 | Dyn 0.35 | Dyn 0.50 |
|---|---:|---:|---:|---:|---:|---:|
| Trace1 | +0.02% | +0.02% | +0.03% | +0.01% | +0.04% | 0.00% |
| Trace2 | +1.39% | +1.33% | +1.35% | +1.34% | +1.26% | +1.09% |
| Trace3 | +0.05% | +0.04% | +0.03% | +0.04% | 0.00% | 0.00% |
| **Geomean** | **+0.48%** | +0.46% | **+0.47%** | +0.46% | +0.43% | +0.36% |

Fraction of epochs in which the followers were in I-RRIP mode:

| Trace | 0.10 | 0.20 | 0.25 | 0.35 | 0.50 |
|---|---:|---:|---:|---:|---:|
| Trace1 | 100% | 100% | 100% | 85% | 0% |
| Trace2 | 100% | 95% | 95% | 86% | 67% |
| Trace3 | 100% | 100% | 100% | 71% | 0% |

The full table, including L2C, L2 instruction and L2 data load MPKI, is in `task2b-data.md`.

## Sensitivity analysis (`sensitivity.png`)

* **0.10 to 0.25 form a plateau.** The scores of all three traces sit above 0.25 almost all the time, so the followers stay in I-RRIP mode. Performance matches static I-RRIP minus the leader-set cost: on Trace2, +1.34% against +1.39%.
* **0.35** starts dropping some epochs to RRIP on all traces (71–86% I-RRIP). Trace2 loses part of its gain (+1.26%), because its L2 instruction MPKI rises from 15.21 to 15.42. Trace3's whole gain disappears (instruction MPKI 1.140 compared with 1.083 at 0.25).
* **0.50** is too conservative. Trace1 and Trace3 never enter I-RRIP mode and behave exactly like RRIP, with identical MPKI. Trace2 spends a third of its epochs in RRIP and drops to +1.09%, giving up much of its L2 instruction-MPKI reduction (15.78 compared with 15.21).
* **Trace1** is where blind instruction priority stops paying off. I-RRIP removes 0.48 instruction MPKI but adds 0.43 data MPKI, so IPC does not change: all of Trace1's differences are within ±0.04%, which is noise. Thresholds of 0.50 or higher make the policy fall back to RRIP there at no cost. That trace-level fallback is the behaviour dynamic I-RRIP is designed for.

**Chosen threshold: 0.25.** It sits in the middle of the flat 0.10–0.25 region, so small changes in the workload mix do not flip the decision. It recovers 96% of static I-RRIP's gain on the instruction-heavy trace (Trace2) and loses nothing measurable on the other two. The differences between 0.10, 0.20 and 0.25 (+0.46% to +0.47% geomean) are within noise. Beyond 0.25 the policy gives up real instruction-MPKI reductions.

**Observation.** None of the three traces has a long phase in which favouring instructions really hurts: I-RRIP never loses more than noise against RRIP. Static I-RRIP is therefore an upper bound on these traces, and Dyn I-RRIP's job is to come close to it, which it does at 0.10–0.25, while staying safe on data-heavy phases. On a workload with data-dominated phases, the 0.25 threshold would switch those phases to RRIP and avoid the data-MPKI increase that I-RRIP shows on Trace1 and Trace2.
