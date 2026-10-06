# GitHub Publishing Guide

## Recommended repository name

`cgl-exact-sequencing-highs`

## Repository title

**Exact Optimization of Continuous Galvanizing Line Coil Sequencing with HiGHS**

## GitHub About description

Exact MILP optimization of 30 real Continuous Galvanizing Line coil-sequencing instances using HiGHS and iterative DFJ subtour cuts; 30/30 proven global optima.

## Suggested GitHub topics

`operations-research`, `mixed-integer-programming`, `milp`, `highs`, `scipy`, `optimization`, `scheduling`, `steel-industry`, `continuous-galvanizing-line`, `hamiltonian-path`, `dfj`, `industrial-optimization`

## Publish from PowerShell

After extracting this project and creating an empty GitHub repository named `cgl-exact-sequencing-highs`, run:

```powershell
cd C:\mlflow\Steel_continuous-galvanizing-line\cgl_highs_github_ready

git init
git branch -M main
git add .
git commit -m "Initial release: exact CGL sequencing with HiGHS"
git remote add origin https://github.com/<YOUR-USERNAME>/cgl-exact-sequencing-highs.git
git push -u origin main
```

Replace `<YOUR-USERNAME>` with your GitHub username.

If Git asks for authentication, use your normal GitHub authentication method. Do not put passwords, tokens, or credentials in this repository.

## Recommended repository settings

- Visibility: Public, if you want to use it as a portfolio project.
- Default branch: `main`.
- Issues: enabled.
- Actions: enabled so the solver smoke test runs automatically.
- Add the topics listed above.
- Add the GitHub About description shown above.

## What to highlight on the repository page

1. Real industrial scheduling problem: CGL coil sequencing with asymmetric costs and forbidden transitions.
2. Exact MILP model: dummy-node transformation plus iterative DFJ subtour-elimination cuts.
3. Open-source solver: HiGHS through SciPy; no commercial solver license required.
4. Reproducibility: all 30 instances, solver code, raw results, optimal sequences, analysis, and documentation are included.
5. Main result: 30/30 instances solved to proven global optimality with zero reported MIP gap.
6. Benchmark observation: the exact result for `cgl_81` is 6816, lower than the Path Bridging best value of 6919 recorded in the literature-comparison file. Present this as a solution-cost comparison, not a runtime comparison.

## Before making the repository public

- Review your name and contact information in `CITATION.cff`.
- Keep `DATASET_LICENSE.md` with the redistributed benchmark data.
- Keep the original dataset DOI in the README.
- Do not add local virtual environments, IDE folders, credentials, or large temporary solver files.
- Verify the README renders correctly after the first push.
