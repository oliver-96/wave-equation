# wave-equation

A 1D acoustic wave-equation simulator on a staggered grid (pressure at
cell centers, velocity at cell faces). A live matplotlib animation shows a
velocity-driven pipe coupled at its right end to a simple mass–spring–damper
membrane.

## Run

```sh
uv sync
uv run wave-equation
```

Boundary conditions and source parameters (amplitude, frequency,
left/right boundary kind) are currently set in code. The acoustic model is
`WaveSimulation` in `src/pipe_wave/acoustic_simulation.py`; the coupled
membrane model is `Membrane` in `src/pipe_wave/membrane.py`. Reusable
`PipeConfig` and `MembraneConfig` values are assembled into a
`CoupledPipeSystem` in `src/pipe_wave/app.py`.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for how the code is laid out
and how the numerical model works, and [`AGENTS.md`](AGENTS.md) for
conventions and commands if you're working on this with an AI coding
agent.
