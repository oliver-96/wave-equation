# wave-equation

A 1D acoustic wave equation simulator on a staggered grid (pressure at
cell centers, velocity at cell faces), with a live matplotlib
visualization of the driving source propagating through the pipe.

## Run

```sh
uv sync
uv run wave-equation
```

Boundary conditions and source parameters (amplitude, frequency,
left/right boundary kind) are currently set in code — see
`WaveSimulation` in `src/pipe_wave/acoustic_simulation.py` and its construction in
`src/pipe_wave/app.py`.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for how the code is laid out
and how the numerical model works, and [`AGENTS.md`](AGENTS.md) for
conventions and commands if you're working on this with an AI coding
agent.
