# Task 1: IP-stride vs SPP

25M warmup + 25M simulated instructions, L1D prefetcher only, LRU everywhere, GCC 7.5 (Ubuntu 20.04 package).
Regenerate with `docs/1/scripts/run.sh` and then `python3 docs/1/scripts/plot.py`; raw output is in `results/`.

* **Speedup**: IPC / IPC with no prefetcher.
* **Accuracy**: ChampSim's L1D accuracy, useful prefetches / prefetches that missed L1D and went to L2.
* **Accuracy excl. L2 fills**: the same, but without prefetches issued with `FILL_L2` under MSHR pressure. Those never fill L1D, so they can never count as useful there. **To L2** is their share.
* **Uniform / pattern accuracy**: useful / filled into L1D, for prefetches issued by each SPP mode.
* **Coverage**: fraction of the no-prefetcher L1D load misses removed.

| Trace | Prefetcher | IPC | Speedup | L1D load MPKI | Accuracy | Accuracy excl. L2 fills | To L2 | Uniform acc. | Pattern acc. | Coverage |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Trace1 | No prefetcher | 0.232345 | 1.0000 | 10.6780 | - | - | - | - | - | - |
| Trace1 | IP-stride | 0.233452 | 1.0048 | 10.1190 | 52.7% | 58.1% | 9.3% | - | - | 5.2% |
| Trace1 | SPP | 0.234546 | 1.0095 | 9.5279 | 51.3% | 55.1% | 7.0% | 60.0% | 57.6% | 10.8% |
| Trace2 | No prefetcher | 0.251158 | 1.0000 | 13.5379 | - | - | - | - | - | - |
| Trace2 | IP-stride | 0.251260 | 1.0004 | 13.4378 | 38.2% | 39.9% | 4.2% | - | - | 0.7% |
| Trace2 | SPP | 0.254259 | 1.0123 | 13.0176 | 51.1% | 53.1% | 3.9% | 60.0% | 54.8% | 3.8% |
| Trace3 | No prefetcher | 0.382065 | 1.0000 | 3.4034 | - | - | - | - | - | - |
| Trace3 | IP-stride | 0.382862 | 1.0021 | 3.3182 | 16.0% | 16.6% | 3.9% | - | - | 2.5% |
| Trace3 | SPP | 0.391621 | 1.0250 | 2.6721 | 48.0% | 51.0% | 5.8% | 49.8% | 57.6% | 21.5% |

| Prefetcher | Geomean speedup |
|---|---:|
| No prefetcher | 1.0000 |
| IP-stride | 1.0024 |
| SPP | 1.0156 |

## SPP storage

Hardware bit widths (not C++ type widths). The L1D has 64 sets x 12 ways = 768 lines.

| Structure | Field | Bits | Why |
|---|---|---:|---|
| IP table entry (x64) | `ip` tag | 8 | low 8 IP bits; a wider tag was measured to hurt, see below |
| | `last_cl_addr` | 16 | low 16 bits of the line address; stride = sign-extended difference |
| | `last_stride` | 16 | range of a 16-bit difference |
| | `lru` | 6 | log2(64), fully associative |
| | `conf` | 2 | saturating at 3 |
| | `sig` | 12 | last 3 strides x 4 bits |
| **IP table** | 64 x 60 | **3,840** | |
| Pattern table entry (x4096) | `next_stride` | 4 | -8..+7 |
| | `conf` | 2 | saturating at 3 |
| **Pattern table** | 4096 x 6 | **24,576** | |
| Throttle (per mode, x2) | degree level | 2 | 4 levels: 1/2/4/8 |
| | epoch fill counter | 7 | 0..64 |
| | epoch useful counter | 7 | 0..64 |
| **Throttle** | 2 x 16 | **32** | |
| L1D line (x768) | prefetch mode bit | 1 | uniform or pattern, so useful hits can be credited per mode |
| **L1D extra state** | 768 x 1 | **768** | |
| **Total** | | **29,216** | about 3.6 KB |

The IP table uses an 8-bit tag on purpose. The traces have about 13,000-17,000 distinct load IPs per
100k L1D accesses (Trace1, Trace3), far more than any affordable table holds; grouping IPs that share
their low 8 bits lets an entry learn a stride before it is evicted. A 12-bit hashed tag lowered the
geomean speedup from 1.0149 to 1.0119, and set-associative 8x8 / 16x4 organisations cost 0.06-0.10%.
