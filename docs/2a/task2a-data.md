# Task 2a LRU vs RRIP vs I-RRIP data

Speedup is IPC divided by the LRU IPC for the same trace. Values use the existing 25M warmup / 25M ROI logs. The LRU rows are from the stored `default-baseline` logs; RRIP and I-RRIP rows are from the 2026-10-14 reruns. The RRIP and I-RRIP reruns match their original stored logs exactly; LRU was not rerun in that check.

| Trace | Policy | IPC | Speedup vs LRU | L2C Load MPKI | L2 Instruction Load MPKI | L2 Data Load MPKI | L2 Total MPKI |
|---|---|---:|---:|---:|---:|---:|---:|
| trace1 | LRU | 0.232204 | 1.0000 | 17.73020 | 10.38430 | 7.34592 | 23.92560 |
| trace1 | RRIP | 0.232075 | 0.9994 | 17.61550 | 10.53600 | 7.07956 | 23.82430 |
| trace1 | I-RRIP | 0.232122 | 0.9996 | 17.56660 | 10.05370 | 7.51292 | 24.56720 |
| trace2 | LRU | 0.251130 | 1.0000 | 27.92340 | 19.39080 | 8.53252 | 33.94840 |
| trace2 | RRIP | 0.251900 | 1.0031 | 26.29570 | 18.33290 | 7.96284 | 32.18180 |
| trace2 | I-RRIP | 0.255396 | 1.0170 | 23.94020 | 15.09400 | 8.84616 | 31.17760 |
| trace3 | LRU | 0.382061 | 1.0000 | 3.95904 | 1.12584 | 2.83320 | 6.11848 |
| trace3 | RRIP | 0.381743 | 0.9992 | 4.04324 | 1.19624 | 2.84700 | 6.34944 |
| trace3 | I-RRIP | 0.381920 | 0.9996 | 3.95396 | 1.07696 | 2.87700 | 6.36412 |


