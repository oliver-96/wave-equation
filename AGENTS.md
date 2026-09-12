# AGENTS.md

Guidance for AI coding agents (and humans) working in this repo.

## What this is

A 1D acoustic wave-equation simulator: `WaveSimulation`, driven by a leapfrog
finite-difference scheme on a staggered grid, can be coupled to a lumped
mass–spring–damper `Membrane` at either pipe boundary. A live matplotlib
animation visualizes the pipe pressure. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the module layout and physics
model in detail.

## Environment

- Python `>=3.13` (see `.python-version`), managed with **uv**.
- Dependencies: `numpy`, `matplotlib`. Tests use the Python standard library's
  `unittest`; no linting or type-checking dependency is configured.

## Common commands

```sh
uv sync                 # install/update the environment from uv.lock
uv run wave-equation    # run the console-script entry point (opens the plot)
uv run python -m pipe_wave.run   # equivalent, direct module invocation
uv run python -m unittest discover -s tests  # run the structural/API tests
uv add <package>        # add a runtime dependency
```

There is no configured linter, formatter, or type checker (`ruff` and `mypy`
are not in `pyproject.toml`). Don't assume `uv run pytest` or `uv run ruff
check` will work; use the standard-library test command above and/or a quick
`uv run python -c "..."` smoke check against `WaveSimulation`.

## Conventions

- **Keep physics and UI separate.** Numerical/model code belongs in
  `src/pipe_wave/acoustic_simulation.py`, `src/pipe_wave/membrane.py`, or
  `src/pipe_wave/system.py` and must not import matplotlib. Shared boundary
  contracts live in `src/pipe_wave/boundaries.py`; reusable constructor values
  live in `src/pipe_wave/config.py`. Visualization/animation/widget code
  belongs in `src/pipe_wave/app.py`. `src/pipe_wave/run.py` is intentionally a
  thin wrapper only (console-script entry point) — don't grow it.
- **Boundary conditions are side-specific and validated.** Valid values live
  in `LeftBoundaryKind` / `RightBoundaryKind` in `boundaries.py`. Adding a new
  kind means updating its supported-side alias, validation set, and branch in
  `WaveSimulation.apply_boundary_conditions`, plus the physical description.
- **Membrane coupling is at either boundary.** The `membrane` boundary passes
  the local acoustic pressure difference to `Membrane.step()` and uses its
  updated velocity at the corresponding velocity face. A `WaveSimulation`
  accepts one membrane, so it cannot use a membrane at both ends. Keep the
  acoustic and mechanical time steps consistent when constructing coupled
  models.
- **Don't change existing numerical formulas incidentally.** If a
  task is about structure/naming/typing/docs, preserve the math in
  `step()` / `apply_boundary_conditions()` exactly — treat changes to
  the actual finite-difference update as a distinct, explicitly-
  requested kind of task.
- **Type hints matter here**: methods that return a value should be
  annotated with the real return type (not `-> None` out of habit —
  that mistake has happened before in this repo).
- Standard physics/numerics shorthand (`N`, `dx`, `dt`, `c`, `rho`) is
  intentional and should not be renamed to verbose alternatives.

## Verifying a change

There's no test suite, so verify manually:

```sh
uv run python -c "
from pipe_wave import CoupledPipeSystem, MembraneConfig, PipeConfig
dt = 1e-6
system = CoupledPipeSystem.from_configs(
    PipeConfig(
        dt=dt,
        left_boundary='velocity_source',
        right_boundary='membrane',
        cross_sectional_area=0.01,
    ),
    MembraneConfig(
        mass=0.01, damping=0.02, stiffness=100.0, area=0.01, dt=dt,
    ),
)
for _ in range(100):
    system.step()
print('finite:', __import__('numpy').isfinite(system.pipe.pressure).all())
"
```

and/or run `uv run wave-equation` to confirm the animation window still
opens and updates.
