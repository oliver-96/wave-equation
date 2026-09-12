from typing import Literal

import numpy as np



BoundaryKind = Literal["open", "closed", "pressure_source", "velocity_source", "membrane"]

_VALID_BOUNDARIES: set[BoundaryKind] = {
    "open",
    "closed",
    "pressure_source",
    "velocity_source",
    "membrane",
}


class WaveSimulation:
    """1D acoustic wave equation solver on a staggered grid.

    Pressure is stored at ``N`` cell centers (``self.pressure``,
    positions ``self.x_pressure``) and velocity is stored at ``N + 1``
    cell faces (``self.velocity``, positions ``self.x_velocity``),
    including the two domain boundaries at indices ``0`` and ``N``.
    Time integration is explicit leapfrog: each ``step()`` updates
    velocity from the pressure gradient, then pressure from the
    velocity divergence.
    """

    def __init__(
        self,
        length: float = 1.0,
        cells: int = 200,
        sound_speed: float = 343.0,
        density: float = 1.2,
        dt: float = 1e-6,
        left_boundary: BoundaryKind = "open",
        right_boundary: BoundaryKind = "open",
        source_amplitude: float = 1,
        source_frequency: float = 100,
    ):

        self.length = length
        self.N = cells
        self.c = sound_speed
        self.rho = density
        self.dt = dt
        self.source_amplitude = source_amplitude
        self.source_frequency = source_frequency

        if left_boundary not in _VALID_BOUNDARIES:
            raise ValueError(f"Invalid left boundary: {left_boundary}")

        if right_boundary not in _VALID_BOUNDARIES:
            raise ValueError(f"Invalid right boundary: {right_boundary}")

        self.left_boundary = left_boundary
        self.right_boundary = right_boundary

        self.dx = length / cells

        self.x_pressure = (np.arange(cells) + 0.5) * self.dx
        self.x_velocity = (np.arange(cells + 1)) * self.dx

        self.pressure = np.zeros(cells)
        self.velocity = np.zeros(cells + 1)

        self.time = 0.0
        self.phase = 0.0

    def apply_boundary_conditions(self, membrane) -> None:
        """Patch the two boundary velocities according to boundary kind.

        - ``closed``: rigid wall, velocity pinned to zero.
        - ``open``: free end, radiates outward (simple absorbing update).
        - ``pressure_source``: drives the boundary pressure towards the
          source waveform.
        - ``velocity_source``: drives the boundary velocity directly
          with the source waveform.
        """

        # LEFT BOUNDARY
        if self.left_boundary == "closed":
            self.velocity[0] = 0

        if self.left_boundary == "open":
            self.velocity[0] -= (
                2 * self.dt / (self.rho * self.dx)
                * self.pressure[0]
            )

        if self.left_boundary == "pressure_source":
            source_pressure = self.source_input()

            self.velocity[0] += (
                2 * self.dt / (self.rho * self.dx)
                * (source_pressure - self.pressure[0])
            )

        if self.left_boundary == "velocity_source":
            self.velocity[0] = self.source_input()

        # RIGHT BOUNDARY
        if self.right_boundary == "closed":
            self.velocity[self.N] = 0

        if self.right_boundary == "open":
            self.velocity[self.N] += (
                2 * self.dt / (self.rho * self.dx)
                * self.pressure[-1]
            )
        
        if self.right_boundary == 'membrane':
            membrane_pressure = self.pressure[-1]
            membrane.step(membrane_pressure)
            self.velocity[self.N] = membrane.velocity

    def source_input(self) -> float:
        return self.source_amplitude * np.sin(self.phase)

    def step(self, membrane) -> None:
        """Advance the simulation by one time step (leapfrog update)."""
        # 1. Update velocity from pressure gradient
        self.velocity[1:self.N] -= (
            self.dt / (self.rho * self.dx)
            * (self.pressure[1:] - self.pressure[:-1])
        )

        # 2. Apply boundary conditions
        self.apply_boundary_conditions(membrane)

        # 3. Update pressure from velocity gradient
        self.pressure -= (
            self.rho * self.c**2 * self.dt / self.dx
            * (self.velocity[1:] - self.velocity[:-1])
        )

        self.time += self.dt
        self.phase += 2 * np.pi * self.source_frequency * self.dt

    def advance(self, duration: float, membrane) -> None:
        """Step the simulation forward by ``duration`` seconds."""
        steps = round(duration / self.dt)

        for _ in range(steps):
            self.step(membrane)
