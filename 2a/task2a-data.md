# Task 2a RRIP vs I-RRIP data

Baseline: standard RRIP. Candidate: current I-RRIP. Values are from the 25M warmup / 25M ROI simulations.

| Trace | Policy | IPC | Speedup vs RRIP | L2C Load MPKI | L2 Instruction Load MPKI | L2 Data Load MPKI | L2 Total MPKI |
|---|---|---:|---:|---:|---:|---:|---:|
| Trace1 | RRIP | 0.232075 | 0.0000% | 17.61550 | 10.53600 | 7.07956 | 23.82430 |
| Trace1 | I-RRIP | 0.232122 | 0.0203% | 17.56660 | 10.05370 | 7.51292 | 24.56720 |
| Trace2 | RRIP | 0.251900 | 0.0000% | 26.29570 | 18.33290 | 7.96284 | 32.18180 |
| Trace2 | I-RRIP | 0.255396 | 1.3879% | 23.94020 | 15.09400 | 8.84616 | 31.17760 |
| Trace3 | RRIP | 0.381743 | 0.0000% | 4.04324 | 1.19624 | 2.84700 | 6.34944 |
| Trace3 | I-RRIP | 0.381920 | 0.0464% | 3.95396 | 1.07696 | 2.87700 | 6.36412 |
