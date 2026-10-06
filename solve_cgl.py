"""
CGL production sequencing optimization with MILP + HiGHS.

The model is a minimum-cost Hamiltonian PATH with forbidden directed arcs.
To make subtour elimination convenient, one zero-cost dummy node is added,
turning the path into a Hamiltonian CYCLE. The dummy node is removed after
optimization.

The code uses iterative DFJ subtour-elimination cuts:
    1. Solve the degree-constrained MILP.
    2. Detect disconnected subtours.
    3. Add SEC cuts for those subtours.
    4. Re-solve.
    5. Stop when one cycle contains every real coil + the dummy node.

Each MILP is solved by HiGHS through scipy.optimize.milp.
No commercial solver license is required.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


def load_cost_matrix(path: str | Path) -> np.ndarray:
    """Load one semicolon-delimited CGL cost matrix."""
    path = Path(path)
    rows = []

    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append([float(v.strip()) for v in line.split(";")])

    C = np.asarray(rows, dtype=float)

    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise ValueError(f"{path.name}: expected a square matrix, got {C.shape}")

    return C


def natural_instance_key(path: Path):
    """Sort cgl_48 before cgl_48b, etc."""
    m = re.fullmatch(r"cgl_(\d+)([A-Za-z]*)\.txt", path.name)
    if not m:
        return (10**9, path.name)
    return (int(m.group(1)), m.group(2).lower())


def build_arc_data(C: np.ndarray):
    """
    Build the augmented graph.

    Real nodes: 0,...,n-1
    Dummy node: n

    Real arc (i,j) exists only when C[i,j] >= 0.
    Dummy -> every real node and every real node -> dummy have zero cost.
    """
    n = C.shape[0]
    dummy = n
    N = n + 1

    real_arcs = [
        (i, j)
        for i in range(n)
        for j in range(n)
        if i != j and C[i, j] >= 0
    ]

    dummy_arcs = (
        [(dummy, j) for j in range(n)]
        + [(i, dummy) for i in range(n)]
    )

    arcs = real_arcs + dummy_arcs
    arc_index = {arc: k for k, arc in enumerate(arcs)}

    costs = np.zeros(len(arcs), dtype=float)
    for k, (i, j) in enumerate(arcs):
        if i != dummy and j != dummy:
            costs[k] = C[i, j]

    return {
        "n": n,
        "N": N,
        "dummy": dummy,
        "arcs": arcs,
        "arc_index": arc_index,
        "costs": costs,
        "real_arc_count": len(real_arcs),
    }


def build_constraints(graph: dict, cuts: list[list[int]]) -> LinearConstraint:
    """
    Build degree equations plus accumulated DFJ subtour-elimination cuts.

    For every node v (including dummy):
        sum_i x[i,v] = 1
        sum_j x[v,j] = 1

    For every detected proper subtour S:
        sum_{i in S} sum_{j in S} x[i,j] <= |S| - 1
    """
    N = graph["N"]
    arcs = graph["arcs"]
    arc_index = graph["arc_index"]
    m = len(arcs)

    rows = 2 * N + len(cuts)
    A = lil_matrix((rows, m), dtype=float)
    lower = np.full(rows, -np.inf, dtype=float)
    upper = np.full(rows, np.inf, dtype=float)

    r = 0

    # Exactly one incoming arc per node.
    for v in range(N):
        for i in range(N):
            k = arc_index.get((i, v))
            if k is not None:
                A[r, k] = 1.0
        lower[r] = upper[r] = 1.0
        r += 1

    # Exactly one outgoing arc per node.
    for v in range(N):
        for j in range(N):
            k = arc_index.get((v, j))
            if k is not None:
                A[r, k] = 1.0
        lower[r] = upper[r] = 1.0
        r += 1

    # DFJ subtour-elimination constraints.
    for S in cuts:
        Sset = set(S)
        for k, (i, j) in enumerate(arcs):
            if i in Sset and j in Sset:
                A[r, k] = 1.0
        upper[r] = len(S) - 1
        r += 1

    return LinearConstraint(A.tocsr(), lower, upper)


def selected_successors(x: np.ndarray, graph: dict) -> dict[int, int]:
    """Return successor map from an integer MILP incumbent."""
    succ = {}
    for k, (i, j) in enumerate(graph["arcs"]):
        if x[k] > 0.5:
            if i in succ:
                raise RuntimeError(f"Node {i} has multiple selected successors.")
            succ[i] = j
    return succ


def find_cycles(succ: dict[int, int], N: int) -> list[list[int]]:
    """Decompose the selected degree-1 solution into directed cycles."""
    remaining = set(range(N))
    cycles = []

    while remaining:
        start = next(iter(remaining))
        order = []
        position = {}
        current = start

        while current not in position:
            position[current] = len(order)
            order.append(current)
            remaining.discard(current)

            if current not in succ:
                raise RuntimeError(
                    f"Node {current} has no selected successor; "
                    "the incumbent is not a complete integer assignment."
                )
            current = succ[current]

        cycle = order[position[current]:]
        cycles.append(cycle)

    return cycles


def augmented_cycle_to_path(succ: dict[int, int], graph: dict) -> list[int]:
    """
    Remove the dummy node from the single augmented Hamiltonian cycle.

    If dummy -> a and b -> dummy, the real path is:
        a -> ... -> b
    """
    n = graph["n"]
    dummy = graph["dummy"]

    first = succ[dummy]
    sequence = []
    current = first

    while current != dummy:
        sequence.append(current)
        current = succ[current]

        if len(sequence) > n:
            raise RuntimeError("Unexpected cycle while reconstructing real path.")

    return sequence


def validate_sequence(C: np.ndarray, sequence: list[int]):
    """Check all coils occur once, no forbidden transition is used, and compute cost."""
    n = C.shape[0]

    if len(sequence) != n:
        return False, None, f"Expected {n} coils, got {len(sequence)}."

    if sorted(sequence) != list(range(n)):
        return False, None, "The sequence does not contain every coil exactly once."

    cost = 0.0
    for i, j in zip(sequence[:-1], sequence[1:]):
        if C[i, j] < 0:
            return False, None, f"Forbidden transition used: {i} -> {j}."
        cost += C[i, j]

    return True, cost, "OK"


def scipy_status_name(status: int) -> str:
    return {
        0: "OPTIMAL",
        1: "LIMIT_REACHED",
        2: "INFEASIBLE",
        3: "UNBOUNDED",
        4: "OTHER",
    }.get(status, f"STATUS_{status}")


def solve_instance(
    file_path: str | Path,
    time_limit: float | None = None,
    mip_gap: float = 0.0,
    disp: bool = False,
) -> dict:
    """
    Solve one CGL instance exactly when possible.

    time_limit is the TOTAL time budget for the instance across all
    cut-generation iterations. If None, no explicit time limit is imposed.
    """
    file_path = Path(file_path)
    C = load_cost_matrix(file_path)
    graph = build_arc_data(C)

    m = len(graph["arcs"])
    integrality = np.ones(m, dtype=np.int32)
    bounds = Bounds(np.zeros(m), np.ones(m))

    cuts: list[list[int]] = []
    cut_keys = set()

    start_time = time.perf_counter()
    iteration = 0
    final_res = None
    final_sequence = None
    validation_message = "No feasible CGL sequence returned."
    validated_cost = None
    valid_sequence = False

    while True:
        elapsed = time.perf_counter() - start_time

        if time_limit is not None:
            remaining = time_limit - elapsed
            if remaining <= 0:
                break
        else:
            remaining = None

        constraint = build_constraints(graph, cuts)

        options = {
            "disp": disp,
            "presolve": True,
            "mip_rel_gap": float(mip_gap),
        }
        if remaining is not None:
            options["time_limit"] = max(0.01, float(remaining))

        res = milp(
            c=graph["costs"],
            integrality=integrality,
            bounds=bounds,
            constraints=constraint,
            options=options,
        )
        iteration += 1
        final_res = res

        # No integer incumbent available.
        if res.x is None:
            break

        try:
            succ = selected_successors(res.x, graph)
            cycles = find_cycles(succ, graph["N"])
        except Exception as exc:
            validation_message = str(exc)
            break

        # One cycle over all real nodes + dummy => a valid Hamiltonian path.
        if len(cycles) == 1 and len(cycles[0]) == graph["N"]:
            sequence = augmented_cycle_to_path(succ, graph)
            valid_sequence, validated_cost, validation_message = validate_sequence(
                C, sequence
            )
            if valid_sequence:
                final_sequence = sequence
            break

        # Add a cut for every proper subtour in the incumbent.
        new_cuts = 0
        for cycle in cycles:
            if len(cycle) >= graph["N"]:
                continue

            key = frozenset(cycle)
            if key not in cut_keys:
                cut_keys.add(key)
                cuts.append(cycle)
                new_cuts += 1

        # Safety: if no new cut can be generated, stop.
        if new_cuts == 0:
            validation_message = "Subtours remain but no new SEC cut was generated."
            break

        # If the current MILP itself hit its time limit, do not start another solve.
        if res.status == 1:
            break

    total_runtime = time.perf_counter() - start_time

    if final_res is None:
        return {
            "instance": file_path.stem,
            "n_coils": int(C.shape[0]),
            "allowed_real_arcs": int(graph["real_arc_count"]),
            "status": "LIMIT_REACHED",
            "proven_optimal": False,
            "objective": None,
            "validated_cost": None,
            "best_bound": None,
            "mip_gap": None,
            "runtime_sec": total_runtime,
            "node_count": None,
            "cut_iterations": iteration,
            "sec_cuts": len(cuts),
            "valid_sequence": False,
            "validation_message": validation_message,
            "sequence": None,
            "solver_message": "Time limit reached before a MILP solve completed.",
        }

    solver_status = scipy_status_name(int(final_res.status))

    objective = float(final_res.fun) if final_res.fun is not None else None
    best_bound = getattr(final_res, "mip_dual_bound", None)
    gap = getattr(final_res, "mip_gap", None)
    nodes = getattr(final_res, "mip_node_count", None)

    if best_bound is not None:
        best_bound = float(best_bound)
    if gap is not None:
        gap = float(gap)
    if nodes is not None:
        nodes = int(nodes)

    # A valid full tour is globally proven optimal only if the final MILP
    # relaxation was itself solved to optimality with the requested zero gap.
    proven_optimal = (
        final_sequence is not None
        and valid_sequence
        and final_res.status == 0
        and abs(float(mip_gap)) <= 1e-15
    )

    status = "OPTIMAL" if proven_optimal else solver_status

    return {
        "instance": file_path.stem,
        "n_coils": int(C.shape[0]),
        "allowed_real_arcs": int(graph["real_arc_count"]),
        "status": status,
        "proven_optimal": proven_optimal,
        "objective": objective,
        "validated_cost": validated_cost,
        "best_bound": best_bound,
        "mip_gap": gap,
        "runtime_sec": total_runtime,
        "node_count": nodes,
        "cut_iterations": iteration,
        "sec_cuts": len(cuts),
        "valid_sequence": valid_sequence,
        "validation_message": validation_message,
        "sequence": final_sequence,
        "solver_message": str(final_res.message),
    }


def pretty_number(value):
    if value is None:
        return "N/A"
    if abs(value - round(value)) < 1e-8:
        return str(int(round(value)))
    return f"{value:.6f}"


def print_result(result: dict):
    print("\n" + "=" * 80)
    print(f"Instance       : {result['instance']}")
    print(f"Coils          : {result['n_coils']}")
    print(f"Allowed arcs   : {result['allowed_real_arcs']}")
    print(f"Status         : {result['status']}")
    print(f"Proven optimal : {result['proven_optimal']}")
    print(f"Objective      : {pretty_number(result['validated_cost'] or result['objective'])}")
    print(f"Best bound     : {pretty_number(result['best_bound'])}")
    print(f"MIP gap        : {result['mip_gap']}")
    print(f"Runtime (s)    : {result['runtime_sec']:.3f}")
    print(f"Cut iterations : {result['cut_iterations']}")
    print(f"SEC cuts added : {result['sec_cuts']}")
    print(f"Valid sequence : {result['valid_sequence']}")
    print(f"Validation     : {result['validation_message']}")

    if result["sequence"] is not None:
        heading = (
            "OPTIMAL SEQUENCE"
            if result["proven_optimal"]
            else "BEST FEASIBLE SEQUENCE"
        )
        print(f"\n{heading}:")
        print(" -> ".join(map(str, result["sequence"])))

    print("=" * 80)


def save_results(results: list[dict], output_dir: str | Path):
    """Save progress after every completed instance."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "highs_results.csv"
    json_path = output_dir / "sequences.json"

    fields = [
        "instance",
        "n_coils",
        "allowed_real_arcs",
        "status",
        "proven_optimal",
        "objective",
        "validated_cost",
        "best_bound",
        "mip_gap",
        "runtime_sec",
        "node_count",
        "cut_iterations",
        "sec_cuts",
        "valid_sequence",
        "validation_message",
        "sequence",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for result in results:
            row = {k: result.get(k) for k in fields}
            row["sequence"] = (
                " -> ".join(map(str, result["sequence"]))
                if result["sequence"] is not None
                else ""
            )
            writer.writerow(row)

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                r["instance"]: {
                    "status": r["status"],
                    "proven_optimal": r["proven_optimal"],
                    "objective": r["validated_cost"],
                    "best_bound": r["best_bound"],
                    "mip_gap": r["mip_gap"],
                    "runtime_sec": r["runtime_sec"],
                    "sequence": r["sequence"],
                }
                for r in results
            },
            f,
            indent=2,
        )

    return csv_path, json_path


def main():
    parser = argparse.ArgumentParser(
        description="Solve CGL sequencing with exact MILP + HiGHS + DFJ cuts."
    )
    parser.add_argument(
        "path",
        help="One cgl_*.txt file, or a directory containing all cgl_*.txt files.",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=None,
        help=(
            "Optional TOTAL time limit in seconds per instance. "
            "Default: no explicit time limit."
        ),
    )
    parser.add_argument(
        "--mip-gap",
        type=float,
        default=0.0,
        help="Relative MIP gap for each MILP. Default 0.0 for proof of optimality.",
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Output directory for all-instance CSV/JSON results.",
    )
    parser.add_argument(
        "--solver-log",
        action="store_true",
        help="Show the HiGHS solver log.",
    )
    args = parser.parse_args()

    path = Path(args.path)

    if path.is_file():
        result = solve_instance(
            path,
            time_limit=args.time_limit,
            mip_gap=args.mip_gap,
            disp=args.solver_log,
        )
        print_result(result)
        return

    if not path.is_dir():
        raise FileNotFoundError(f"Path not found: {path}")

    instance_files = sorted(path.glob("cgl_*.txt"), key=natural_instance_key)

    if not instance_files:
        raise FileNotFoundError(f"No cgl_*.txt files found in {path}")

    print(f"Found {len(instance_files)} CGL instances.")

    results = []

    for number, file_path in enumerate(instance_files, start=1):
        print(f"\n[{number}/{len(instance_files)}] Solving {file_path.name} ...")

        result = solve_instance(
            file_path,
            time_limit=args.time_limit,
            mip_gap=args.mip_gap,
            disp=args.solver_log,
        )

        print_result(result)
        results.append(result)

        csv_path, json_path = save_results(results, args.output_dir)

    print("\nAll requested instances finished.")
    print(f"CSV results : {csv_path}")
    print(f"Sequences   : {json_path}")


if __name__ == "__main__":
    main()
