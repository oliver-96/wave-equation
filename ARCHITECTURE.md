# Architecture

## Layout

```
wave-equation/
├── pyproject.toml              console-script: wave-equation = "pipe_wave:simulate"
├── README.md
├── AGENTS.md
├── ARCHITECTURE.md             (this file)
└── src/pipe_wave/
    ├── __init__.py             re-exports the supported package API
    ├── run.py                  thin entry point: simulate() -> app.run_app()
    ├── boundaries.py           side-specific boundary types and device protocol
    ├── config.py               immutable PipeConfig and MembraneConfig values
    ├── membrane.py             membrane mass–spring–damper model (Membrane)
    ├── acoustic_simulation.py  acoustic numerical model (WaveSimulation)
    ├── system.py               CoupledPipeSystem composition wrapper
    └── app.py                  matplotlib figure/animation setup — the UI layer
```

**Import direction**: `run.py` → `app.py` → `system.py` →
(`acoustic_simulation.py`, `membrane.py`, `config.py`).
`acoustic_simulation.py` depends only on the boundary-device protocol in
`boundaries.py`, not on a concrete membrane. The model modules have no
knowledge of matplotlib or how the simulation is visualized, so they can be
imported and driven headlessly (scripts, tests, notebooks) without pulling in
a plotting backend.

## The physics model (`acoustic_simulation.py`)

`WaveSimulation` solves the 1D acoustic wave equation with an explicit
**leapfrog** scheme on a **staggered grid**:

- `pressure` lives at `N` cell centers (`x_pressure`).
- `velocity` lives at `N + 1` cell faces (`x_velocity`), including
  both domain boundaries (indices `0` and `N`).

`step()` and `advance(duration)` retain the pipe-only API. A membrane is
provided once, when constructing a `WaveSimulation` with a `membrane`
boundary.

Each call to `step()` does, in order:

1. Update interior velocity faces from the local pressure gradient.
2. Apply boundary conditions — this is the only place `velocity[0]`
   and `velocity[N]` get their final values for the step.
3. Update pressure from the velocity divergence.
4. Advance `time` and the source oscillator's `phase`.

`advance(duration)` just calls `step()` enough times to cover
`duration` seconds at the configured `dt`.

### Boundary conditions

Set independently via `LeftBoundaryKind` / `RightBoundaryKind` in
`boundaries.py`. The left end accepts every kind below; the right end accepts
`open`, `closed`, and `membrane` only. Unsupported side/kind combinations are
rejected during construction.

| Kind               | Physical meaning                                   |
|--------------------|-----------------------------------------------------|
| `closed`           | Rigid wall — velocity pinned to zero                |
| `open`             | Free end — simple outward-radiating (absorbing) end |
| `pressure_source`  | Drives the boundary pressure toward the source wave |
| `velocity_source`  | Drives the boundary velocity directly with the source wave |
| `membrane`         | End follows the coupled membrane's volume velocity  |

For a `membrane` boundary, the pipe gives the device the nearest cell pressure
and final half-cell geometry. The membrane solves for its wall pressure using
the acoustic momentum equation over that half-cell, advances its mechanics,
then returns outward volume velocity. The pipe converts this to end-face
particle velocity by dividing by `cross_sectional_area`. The application uses
a `velocity_source` on the left and a `membrane` on the right with matching
areas.

The driving waveform is a sine oscillator (`source_input()`) built
from an accumulated `phase` (incremented each step by `2π ·
source_frequency · dt`) rather than `sin(2π · f · t)` directly — this
means `source_frequency` can be changed mid-run without a phase
discontinuity (no sudden jump/impulse injected into the pipe).

## The mechanical model (`membrane.py`)

`Membrane` represents a lumped mass–spring–damper system. It is initialized
with `mass`, `damping`, `stiffness`, `area`, and `dt`; its state is
`displacement`, `velocity`, and `time`. On `step(pressure)`, pressure is
converted to force with `pressure * area`, then the membrane advances using
the resulting force minus damping and spring restoring forces. Its updated
velocity supplies the pipe's right-boundary velocity when coupled as above.

## The visualization layer (`app.py`)

`run_app()` owns everything matplotlib-related:

- Builds `PipeConfig` and `MembraneConfig` values, then creates one
  `CoupledPipeSystem` with a pipe and right-boundary membrane.
- Sets up a `matplotlib` figure with the pressure line plot and an
  elapsed-time text label.
- Drives the simulation forward with `FuncAnimation`, calling
  `system.advance(...)` once per animation frame and updating the line
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
`acoustic_simulation.py`, `membrane.py`, `system.py`, or `app.py`, not here.

`pipe_wave` exports `WaveSimulation`, `Membrane`, `PipeConfig`,
`MembraneConfig`, `CoupledPipeSystem`, and `simulate` as its supported public
API.
