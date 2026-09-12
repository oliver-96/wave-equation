# Architecture

## Layout

```
wave-equation/
├── pyproject.toml              console-script: wave-equation = "pipe_wave:simulate"
├── README.md
├── AGENTS.md
├── ARCHITECTURE.md             (this file)
└── src/pipe_wave/
    ├── __init__.py             re-exports `simulate` as the package's public API
    ├── run.py                  thin entry point: simulate() -> app.run_app()
    ├── acoustic_simulation.py  the numerical model (WaveSimulation class) — no matplotlib
    └── app.py                  matplotlib figure/animation setup — the UI layer
```

**Import direction**: `run.py` → `app.py` → `acoustic_simulation.py`.
Nothing flows the other way; `acoustic_simulation.py` has no knowledge
of matplotlib or how it's visualized, so it can be imported and driven
headlessly (scripts, tests, notebooks) without pulling in a plotting
backend.

## The physics model (`acoustic_simulation.py`)

`WaveSimulation` solves the 1D acoustic wave equation with an explicit
**leapfrog** scheme on a **staggered grid**:

- `pressure` lives at `N` cell centers (`x_pressure`).
- `velocity` lives at `N + 1` cell faces (`x_velocity`), including
  both domain boundaries (indices `0` and `N`).

Each call to `step()` does, in order:

1. Update interior velocity faces from the local pressure gradient.
2. Apply boundary conditions — this is the only place `velocity[0]`
   and `velocity[N]` get their final values for the step.
3. Update pressure from the velocity divergence.
4. Advance `time` and the source oscillator's `phase`.

`advance(duration)` just calls `step()` enough times to cover
`duration` seconds at the configured `dt`.

### Boundary conditions

Set independently on each end via `left_boundary` / `right_boundary`
(`BoundaryKind` in `acoustic_simulation.py`):

| Kind               | Physical meaning                                   |
|--------------------|-----------------------------------------------------|
| `closed`           | Rigid wall — velocity pinned to zero                |
| `open`             | Free end — simple outward-radiating (absorbing) end |
| `pressure_source`  | Drives the boundary pressure toward the source wave |
| `velocity_source`  | Drives the boundary velocity directly with the source wave |

The driving waveform is a sine oscillator (`source_input()`) built
from an accumulated `phase` (incremented each step by `2π ·
source_frequency · dt`) rather than `sin(2π · f · t)` directly — this
means `source_frequency` can be changed mid-run without a phase
discontinuity (no sudden jump/impulse injected into the pipe).

## The visualization layer (`app.py`)

`run_app()` owns everything matplotlib-related:

- Builds one `WaveSimulation` with a fixed set of parameters.
- Sets up a `matplotlib` figure with the pressure line plot and an
  elapsed-time text label.
- Drives the simulation forward with `FuncAnimation`, calling
  `sim.advance(...)` once per animation frame and updating the line
  data — `blit=True` is used for performance, which means only
  artists explicitly returned from the frame-update callback get
  redrawn each frame.

Anything interactive (sliders, buttons) added here needs to account
for that `blit=True` behavior — widgets living on the same canvas can
appear unresponsive because the animation's saved background
overwrites their redraws each frame. (This is why a frequency slider
that was previously here was removed rather than debugged in place.)

## Entry point (`run.py` / `__init__.py`)

`pyproject.toml` points the `wave-equation` console script at
`pipe_wave:simulate`, which resolves through `__init__.py` →
`run.py`'s `simulate()` → `app.run_app()`. `run.py` is deliberately
kept to just that wrapper — new functionality should go in
`acoustic_simulation.py` or `app.py`, not here.
