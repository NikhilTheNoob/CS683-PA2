# Task 2b: Dynamic I-RRIP data

Baseline: standard RRIP (no L1D prefetcher). 25M warmup / 25M simulated instructions. Built with GCC 7.5 (docker/Dockerfile).
Dyn I-RRIP (x) = dynamic I-RRIP with threshold x. Epochs in I-RRIP = % of 4096-access epochs that ended in I-RRIP mode.

| Trace | Policy | IPC | Speedup vs RRIP | L2C Load MPKI | L2 Instruction Load MPKI | L2 Data Load MPKI | Epochs in I-RRIP |
|---|---|---:|---:|---:|---:|---:|---:|
| Trace1 | RRIP | 0.232075 | 1.0000 | 17.61550 | 10.53600 | 7.07956 | - |
| Trace1 | I-RRIP | 0.232122 | 1.0002 | 17.56660 | 10.05370 | 7.51292 | - |
| Trace1 | Dyn I-RRIP (0.10) | 0.232124 | 1.0002 | 17.57070 | 10.07200 | 7.49868 | 100.0% |
| Trace1 | Dyn I-RRIP (0.20) | 0.232148 | 1.0003 | 17.56900 | 10.07110 | 7.49788 | 100.0% |
| Trace1 | Dyn I-RRIP (0.25) | 0.232088 | 1.0001 | 17.58150 | 10.08080 | 7.50072 | 100.0% |
| Trace1 | Dyn I-RRIP (0.35) | 0.232165 | 1.0004 | 17.54370 | 10.04270 | 7.50100 | 84.6% |
| Trace1 | Dyn I-RRIP (0.50) | 0.232075 | 1.0000 | 17.61570 | 10.53620 | 7.07952 | 0.0% |
| Trace2 | RRIP | 0.251900 | 1.0000 | 26.29570 | 18.33290 | 7.96284 | - |
| Trace2 | I-RRIP | 0.255396 | 1.0139 | 23.94020 | 15.09400 | 8.84616 | - |
| Trace2 | Dyn I-RRIP (0.10) | 0.255252 | 1.0133 | 24.00140 | 15.18570 | 8.81576 | 100.0% |
| Trace2 | Dyn I-RRIP (0.20) | 0.255298 | 1.0135 | 24.00760 | 15.18160 | 8.82608 | 95.2% |
| Trace2 | Dyn I-RRIP (0.25) | 0.255267 | 1.0134 | 24.02600 | 15.20670 | 8.81928 | 95.2% |
| Trace2 | Dyn I-RRIP (0.35) | 0.255066 | 1.0126 | 24.20030 | 15.41880 | 8.78148 | 85.7% |
| Trace2 | Dyn I-RRIP (0.50) | 0.254651 | 1.0109 | 24.47940 | 15.78340 | 8.69604 | 66.7% |
| Trace3 | RRIP | 0.381743 | 1.0000 | 4.04324 | 1.19624 | 2.84700 | - |
| Trace3 | I-RRIP | 0.381920 | 1.0005 | 3.95396 | 1.07696 | 2.87700 | - |
| Trace3 | Dyn I-RRIP (0.10) | 0.381882 | 1.0004 | 3.95884 | 1.08332 | 2.87552 | 100.0% |
| Trace3 | Dyn I-RRIP (0.20) | 0.381859 | 1.0003 | 3.95752 | 1.08292 | 2.87460 | 100.0% |
| Trace3 | Dyn I-RRIP (0.25) | 0.381879 | 1.0004 | 3.95832 | 1.08296 | 2.87536 | 100.0% |
| Trace3 | Dyn I-RRIP (0.35) | 0.381751 | 1.0000 | 4.01004 | 1.13956 | 2.87048 | 71.4% |
| Trace3 | Dyn I-RRIP (0.50) | 0.381743 | 1.0000 | 4.04324 | 1.19624 | 2.84700 | 0.0% |

## Geometric mean speedup over RRIP

| Policy | Geomean speedup |
|---|---:|
| RRIP | 1.0000 |
| I-RRIP | 1.0048 |
| Dyn I-RRIP (0.10) | 1.0046 |
| Dyn I-RRIP (0.20) | 1.0047 |
| Dyn I-RRIP (0.25) | 1.0046 |
| Dyn I-RRIP (0.35) | 1.0043 |
| Dyn I-RRIP (0.50) | 1.0036 |
