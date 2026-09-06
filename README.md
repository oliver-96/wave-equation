# wave-equation

A 1D acoustic wave equation simulator on a staggered grid (pressure at
cell centers, velocity at cell faces), with a live matplotlib
visualization and a frequency slider for the driving source.

## Run

```sh
uv sync
uv run wave-equation
```

Boundary conditions and source parameters (amplitude, initial
frequency, left/right boundary kind) are currently set in code — see
`Simulation` in `src/pipe_wave/simulation.py` and its construction in
`src/pipe_wave/app.py`.
