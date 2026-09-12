# AGENTS.md

Guidance for AI coding agents (and humans) working in this repo.

## What this is

A 1D acoustic wave-equation simulator: a small numerical model
(`WaveSimulation`) driven by a leapfrog finite-difference scheme on a
staggered grid, plus a live matplotlib animation to visualize it. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the module layout and physics
model in detail.

## Environment

- Python `>=3.13` (see `.python-version`), managed with **uv**.
- Dependencies: `numpy`, `matplotlib`. No dev/test/lint dependencies
  are configured yet.

## Common commands

```sh
uv sync                 # install/update the environment from uv.lock
uv run wave-equation    # run the console-script entry point (opens the plot)
uv run python -m pipe_wave.run   # equivalent, direct module invocation
uv add <package>        # add a runtime dependency
```

There is currently **no test suite and no linter/formatter/type-checker
configured** (no `pytest`, `ruff`, or `mypy` in `pyproject.toml`). Don't
assume `uv run pytest` or `uv run ruff check` will work until one is
added — verify changes by running the app and/or a quick `uv run
python -c "..."` smoke check against `pipe_wave.acoustic_simulation.WaveSimulation`.

## Conventions

- **Keep physics and UI separate.** Numerical/model code belongs in
  `src/pipe_wave/acoustic_simulation.py` and must not import matplotlib.
  Visualization/animation/widget code belongs in
  `src/pipe_wave/app.py`. `src/pipe_wave/run.py` is intentionally a
  thin wrapper only (console-script entry point) — don't grow it.
- **Boundary conditions are a closed, validated set.** Valid values
  live in `BoundaryKind` / `_VALID_BOUNDARIES` in `acoustic_simulation.py`.
  Adding a new boundary kind means updating both the `Literal` alias
  and the `if` branch in `WaveSimulation.apply_boundary_conditions`, plus
  the docstring listing what each kind means physically.
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
from pipe_wave.acoustic_simulation import WaveSimulation
sim = WaveSimulation(left_boundary='velocity_source', right_boundary='closed')
for _ in range(100):
    sim.step()
print('finite:', __import__('numpy').isfinite(sim.pressure).all())
"
```

and/or run `uv run wave-equation` to confirm the animation window still
opens and updates.
