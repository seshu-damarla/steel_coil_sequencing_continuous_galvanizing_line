# Results and Literature Comparison

## Exact-solve outcome

The HiGHS + iterative DFJ implementation solved all 30 supplied CGL instances to proven optimality. Every reconstructed sequence passed the independent sequence validator and every reported MIP gap is zero.

Key aggregate statistics:

- 30/30 proven optimal.
- 30/30 valid sequences.
- Total runtime: 23,934.27 s (6.65 h).
- Median runtime: 4.40 s.
- Mean runtime: 797.81 s.
- Fastest: cgl_17, 0.069 s.
- Slowest: cgl_114, 19,427.29 s (5.40 h).
- Total cut-generation iterations: 1,171.
- Total DFJ SEC cuts: 6,571.

The runtime distribution is strongly right-skewed. The cgl_114 instance contributes about 81% of total runtime, and cgl_107 plus cgl_114 together contribute about 94%.

## Comparison with Path Bridging

The 2025 Path Bridging paper studies the same free-start/free-end minimum-cost Hamiltonian-path benchmark. Its benchmark values are also reproduced in Table 6 of patent publication WO2026047371A1.

The exact optimum obtained here equals the reported Path Bridging best on 29 of 30 instances. The exception is:

| Instance | Path Bridging reported best | Exact optimum here | Improvement | Improvement (%) |
|---|---:|---:|---:|---:|
| cgl_81 | 6919 | **6816** | **103** | **1.49%** |

This means the exact run provides two useful benchmark contributions:

1. It certifies the Path Bridging best costs as globally optimal on the 29 instances where the values match.
2. It establishes a lower proven optimum of 6816 for cgl_81 than the reported Path Bridging best of 6919.

The comparison should not be interpreted as a runtime competition. Path Bridging is a repeated, time-budgeted metaheuristic designed for fast industrial-quality scheduling. The present method is an exact MILP procedure run until proof. The hardware, number of runs, stopping criteria, and algorithmic goals differ.

## Computational behavior

Problem size alone does not explain runtime. For example, cgl_70 solves in 6.69 s, while cgl_73 requires 172.77 s and cgl_78 requires 736.86 s. The structure of the allowed-transition graph and the strength/difficulty of the MILP relaxations after subtour cuts are important.

The number of generated cuts also does not by itself predict runtime. cgl_107 adds 1,262 SEC cuts over 221 cut-generation iterations and takes about 50.6 minutes, whereas cgl_114 adds 805 SEC cuts over 125 iterations but takes about 5.40 hours. This indicates that later MILP solves can be substantially harder even with fewer generated subtour cuts.

## Files

- `results/highs_results.csv`: complete solver statistics and sequences.
- `results/sequences.json`: compact sequence-oriented output.
- `results/summary.json`: aggregate statistics.
- `results/literature_comparison.csv`: row-by-row comparison with the Path Bridging benchmark.
- `figures/runtime_vs_problem_size.png`: runtime on a logarithmic scale.
- `figures/sec_cuts_vs_problem_size.png`: SEC-cut count versus number of coils.

## Literature sources

- Path Bridging article: https://doi.org/10.1016/j.eswa.2025.127209
- Patent publication reproducing the benchmark table: https://patentscope.wipo.int/search/en/detail.jsf?docId=WO2026047371
- Dataset: https://doi.org/10.17632/v357z2ncbh.2
