# Portfolio and LinkedIn Material

## Short project title

**Exact Optimization of Steel CGL Production Sequencing**

## LinkedIn project description

Developed an exact optimization solution for a real-world Continuous Galvanizing Line (CGL) production-sequencing problem from the steel industry. Formulated the scheduling task as a constrained asymmetric minimum-cost Hamiltonian path with forbidden transitions and solved it using mixed-integer linear programming (MILP), a zero-cost dummy-node transformation, and iterative DFJ subtour-elimination cuts with the open-source HiGHS solver through SciPy.

Solved all 30 benchmark instances, ranging from 17 to 114 coils, to proven global optimality with validated production sequences and zero reported MIP gap. The repository includes reproducible Python code, benchmark data, complete optimal sequences, solver statistics, computational analysis, and mathematical documentation.

A literature-cost comparison shows that the exact solutions match the reported Path Bridging best costs on 29 instances and establish a lower proven objective of 6816 for `cgl_81` versus the reported value of 6919. Runtime comparisons are not claimed because the exact and heuristic methods use different computational goals and stopping criteria.

## Resume version

- Developed an exact MILP-based production-sequencing optimizer for 30 real steel Continuous Galvanizing Line scheduling instances with asymmetric transition costs and forbidden transitions.
- Implemented a dummy-node Hamiltonian-path transformation and iterative DFJ subtour-elimination procedure using the open-source HiGHS solver through SciPy.
- Solved and validated all 30 benchmark instances (17–114 coils) to proven global optimality with zero reported MIP gap; produced reproducible optimal sequences, solver statistics, and benchmark analysis.

## One-line portfolio summary

Exact industrial scheduling optimization in Python: 30 real CGL benchmark instances, 30 proven global optima, open-source HiGHS MILP solver, and reproducible DFJ cut generation.

## Skills demonstrated

Operations Research; Mixed-Integer Linear Programming; Production Scheduling; Combinatorial Optimization; Hamiltonian Path; DFJ Subtour Elimination; HiGHS; SciPy; Python; Benchmarking; Reproducible Research; Industrial Optimization.
