# Exact Optimization of Continuous Galvanizing Line Coil Sequencing

This repository solves 30 real-world Continuous Galvanizing Line (CGL) coil-sequencing instances as **minimum-cost Hamiltonian path** problems with asymmetric transition costs and forbidden transitions.

The implementation uses an exact mixed-integer linear programming (MILP) approach with:

- a zero-cost **dummy node** to transform the open Hamiltonian path into a cycle,
- binary transition variables,
- one-in / one-out degree constraints,
- **iterative DFJ subtour-elimination constraints (SEC)**, and
- the open-source **HiGHS** MILP solver through `scipy.optimize.milp`.

No commercial solver license is required.

## Main result

All **30/30 benchmark instances were solved to proven optimality** with validated sequences and zero reported MIP gap.

- Instances solved: **30**
- Proven optimal: **30/30**
- Valid sequences: **30/30**
- Maximum MIP gap: **0.0**
- Median runtime: **4.40 s**
- Mean runtime: **797.81 s**
- Total runtime: **23,934.27 s = 6.65 h**
- Fastest: `cgl_17`, **0.069 s**
- Slowest: `cgl_114`, **19,427.29 s = 5.40 h**
- DFJ cut-generation iterations: **1,171** total
- SEC cuts added: **6,571** total

The mean runtime is dominated by the two largest/hardest cases. `cgl_114` alone accounts for about 81% of the total runtime.

## Literature comparison

The most recent Path Bridging (PB) benchmark for the same free-start/free-end CGL problem reports best costs that match the exact optimum obtained here on **29 of 30 instances**. On `cgl_81`, this exact solution obtains **6816**, compared with the reported PB best of **6919**, an improvement of **103 cost units (1.49%)**.

This comparison is about **solution cost**, not raw runtime. PB is a time-budgeted local-search/metaheuristic method evaluated over repeated runs, whereas this repository runs an exact MILP procedure until an optimality proof is obtained. Hardware and stopping criteria are also different, so runtime numbers should not be compared directly.

See `results/literature_comparison.csv` and `RESULTS.md` for the row-by-row comparison.

## Problem definition

For an instance with `n` coils, the input is an `n x n` matrix `C`:

- `C[i,j] = -1`: transition `i -> j` is forbidden.
- `C[i,j] >= 0`: transition `i -> j` is allowed and has cost `C[i,j]`.
- Costs are asymmetric in general.
- Every coil must appear exactly once.
- The first and final coils are decision variables.

For a sequence

```text
v1 -> v2 -> ... -> vn
```

the objective is

```text
min  C[v1,v2] + C[v2,v3] + ... + C[v(n-1),vn]
```

subject to every selected consecutive transition being allowed.

## Implemented exact formulation

Let `D` be a dummy node. The real path

```text
v1 -> v2 -> ... -> vn
```

is represented as the augmented cycle

```text
D -> v1 -> v2 -> ... -> vn -> D
```

with zero-cost dummy arcs. Binary variable `x[i,j]` equals 1 when arc `i -> j` is selected.

The model minimizes

```text
sum C[i,j] * x[i,j]
```

over allowed real arcs, with zero cost on dummy arcs.

Every augmented node has exactly one selected incoming and one selected outgoing arc. If the resulting integer solution contains multiple cycles, the program detects each proper subtour `S` and adds the DFJ cut

```text
sum_{i in S} sum_{j in S, j != i} x[i,j] <= |S| - 1
```

The MILP is re-solved until one cycle contains all real coils plus the dummy node. Removing the dummy gives the production sequence.

## MTZ versus this implementation

MTZ is another valid exact MILP formulation and is described in `docs/CGL_Optimization_Problem_MILP_HiGHS_Explanation.docx`. The executable code in this repository **does not use MTZ**; it uses iterative DFJ cuts.

## Repository structure

```text
.
├── README.md
├── RESULTS.md
├── LICENSE
├── DATASET_LICENSE.md
├── requirements.txt
├── solve_cgl.py
├── analyze_results.py
├── GITHUB_PUBLISHING.md
├── PORTFOLIO_AND_LINKEDIN.md
├── .github/workflows/ci.yml
├── tests/test_solver.py
├── data/
│   ├── DATASET_README.txt
│   └── cgl_*.txt
├── results/
│   ├── highs_results.csv
│   ├── sequences.json
│   ├── summary.json
│   └── literature_comparison.csv
├── figures/
│   ├── runtime_vs_problem_size.png
│   └── sec_cuts_vs_problem_size.png
└── docs/
    └── CGL_Optimization_Problem_MILP_HiGHS_Explanation.docx
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Automated verification

A lightweight GitHub Actions workflow runs the unit tests on every push and pull request. The smoke test solves `cgl_17` and verifies the proven optimal objective of 4422, along with matrix loading and sequence validation.

Run the same tests locally with:

```powershell
python -m unittest discover -s tests -v
```

## Solve one instance

```powershell
python solve_cgl.py data\cgl_17.txt
```

The program prints solver status, objective, best bound, MIP gap, runtime, cut statistics, validation status, and the final sequence.

## Solve all 30 instances

```powershell
python solve_cgl.py data
```

Progress is saved after each completed instance to:

```text
results/highs_results.csv
results/sequences.json
```

By default, there is no explicit time limit and the requested MIP gap is zero.

For a limited exploratory run:

```powershell
python solve_cgl.py data --time-limit 60
```

A time-limited incumbent must not be described as optimal unless `proven_optimal` is `True`.

## Benchmark results

| Instance | Coils | Optimal cost | Runtime | DFJ iterations | SEC cuts |
|---|---:|---:|---:|---:|---:|
| `cgl_17` | 17 | 4422 | 0.069 s | 4 | 12 |
| `cgl_26` | 26 | 5255 | 0.433 s | 14 | 50 |
| `cgl_28` | 28 | 2833 | 1.45 s | 24 | 85 |
| `cgl_32` | 32 | 4035 | 0.260 s | 9 | 37 |
| `cgl_33` | 33 | 9071 | 0.360 s | 10 | 43 |
| `cgl_37` | 37 | 4883 | 1.39 s | 19 | 75 |
| `cgl_38` | 38 | 3887 | 0.654 s | 9 | 29 |
| `cgl_43` | 43 | 4899 | 15.28 s | 43 | 173 |
| `cgl_44` | 44 | 8949 | 2.53 s | 29 | 126 |
| `cgl_45` | 45 | 7995 | 0.748 s | 12 | 80 |
| `cgl_47` | 47 | 5046 | 0.373 s | 6 | 39 |
| `cgl_48` | 48 | 9148 | 2.02 s | 15 | 101 |
| `cgl_48b` | 48 | 4271 | 0.560 s | 8 | 65 |
| `cgl_50` | 50 | 5335 | 0.329 s | 10 | 72 |
| `cgl_51` | 51 | 12498 | 0.790 s | 8 | 51 |
| `cgl_51b` | 51 | 4146 | 1.15 s | 13 | 72 |
| `cgl_57` | 57 | 7999 | 8.25 s | 30 | 163 |
| `cgl_58` | 58 | 3652 | 1.09 min | 87 | 438 |
| `cgl_60` | 60 | 10144 | 6.27 s | 29 | 150 |
| `cgl_66` | 66 | 8217 | 9.38 s | 30 | 186 |
| `cgl_70` | 70 | 9235 | 6.69 s | 11 | 98 |
| `cgl_70b` | 70 | 5454 | 14.46 s | 32 | 146 |
| `cgl_72` | 72 | 7664 | 47.42 s | 85 | 517 |
| `cgl_73` | 73 | 6148 | 2.88 min | 50 | 326 |
| `cgl_76` | 76 | 9399 | 52.33 s | 19 | 126 |
| `cgl_78` | 78 | 8985 | 12.28 min | 151 | 835 |
| `cgl_81` | 81 | **6816** | 1.25 min | 44 | 222 |
| `cgl_88` | 88 | 10431 | 4.18 min | 24 | 187 |
| `cgl_107` | 107 | 5515 | 50.56 min | 221 | 1262 |
| `cgl_114` | 114 | 8685 | 5.40 h | 125 | 805 |

Full sequences are stored in `results/sequences.json`.

## Reproduce the result summary

```powershell
python analyze_results.py results\highs_results.csv
```

## Dataset

The 30 instances were published by Nicolás Álvarez-Gil and collaborators and are hosted on Mendeley Data:

- Dataset DOI: https://doi.org/10.17632/v357z2ncbh.2
- Dataset record: https://data.mendeley.com/datasets/v357z2ncbh/2
- Dataset license: CC BY 4.0

See `DATASET_LICENSE.md` for attribution details.

## References

1. N. Álvarez-Gil, S. Álvarez García, R. Rosillo, D. de la Fuente, “Problem instances dataset of a real-world sequencing problem with transition constraints and asymmetric costs,” *Data in Brief*, 41, 107844, 2022. https://doi.org/10.1016/j.dib.2022.107844
2. N. Álvarez-Gil, S. Álvarez García, R. Rosillo, D. de la Fuente, “Sequencing jobs with asymmetric costs and transition constraints in a finishing line: A real case study,” *Computers & Industrial Engineering*, 165, 107908, 2022. https://doi.org/10.1016/j.cie.2021.107908
3. S. Álvarez-García, N. Álvarez-Gil, R. Rosillo, D. de la Fuente, “An effective graph-analysis method to schedule a continuous galvanizing line with campaigning boundary constraints,” *Computers & Industrial Engineering*, 192, 110206, 2024. https://doi.org/10.1016/j.cie.2024.110206
4. S. Álvarez-García, N. Álvarez-Gil, R. Rosillo, “Path bridging: A novel local search methodology for optimizing scheduling in highly constrained continuous galvanizing line operations,” *Expert Systems with Applications*, 276, 127209, 2025. https://doi.org/10.1016/j.eswa.2025.127209

## Notes on interpretation

- A zero MIP gap and matching incumbent/bound support the claim of proven optimality for the exact run.
- Different optimal sequences can have the same optimal objective value.
- Runtime depends strongly on instance structure, hardware, solver version, and stopping criteria.
- `node_count` in the raw CSV is the node count reported by the **final** MILP solve, not a cumulative branch-and-bound node count across all DFJ iterations.

## Author

Seshu Kumar Damarla
