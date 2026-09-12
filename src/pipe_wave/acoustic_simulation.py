"""Acoustic finite-difference model for a one-dimensional pipe."""

import numpy as np

from pipe_wave.boundaries import (
    LeftBoundaryKind,
    PressureDrivenBoundary,
    RightBoundaryKind,
    _VALID_LEFT_BOUNDARIES,
    _VALID_RIGHT_BOUNDARIES,
)
from pipe_wave.config import PipeConfig


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
        left_boundary: LeftBoundaryKind = "open",
        right_boundary: RightBoundaryKind = "open",
        source_amplitude: float = 1.0,
        source_frequency: float = 100.0,
        cross_sectional_area: float = 1.0,
        membrane: PressureDrivenBoundary | None = None,
    ) -> None:

        self.length = length
        self.N = cells
        self.c = sound_speed
        self.rho = density
        self.dt = dt
        self.source_amplitude = source_amplitude
        self.source_frequency = source_frequency
        self.cross_sectional_area = cross_sectional_area
        self.membrane = membrane

        if cross_sectional_area <= 0:
            raise ValueError("cross_sectional_area must be positive")

        if left_boundary not in _VALID_LEFT_BOUNDARIES:
            raise ValueError(f"Invalid left boundary: {left_boundary}")

        if right_boundary not in _VALID_RIGHT_BOUNDARIES:
            raise ValueError(f"Invalid right boundary: {right_boundary}")

        self.left_boundary = left_boundary
        self.right_boundary = right_boundary

        uses_membrane = (
            left_boundary == "membrane" or right_boundary == "membrane"
        )
        if uses_membrane and membrane is None:
            raise ValueError("A membrane boundary requires a Membrane instance")
        if left_boundary == "membrane" and right_boundary == "membrane":
            raise ValueError("One Membrane instance cannot terminate both pipe ends")
        if membrane is not None and membrane.dt != dt:
            raise ValueError("membrane.dt must equal the pipe time step")

        self.dx = length / cells

        self.x_pressure = (np.arange(cells) + 0.5) * self.dx
        self.x_velocity = (np.arange(cells + 1)) * self.dx

        self.pressure = np.zeros(cells)
        self.velocity = np.zeros(cells + 1)

        self.time = 0.0
        self.phase = 0.0

    @classmethod
    def from_config(
        cls,
        config: PipeConfig,
        membrane: PressureDrivenBoundary | None = None,
    ) -> "WaveSimulation":
        """Construct a simulation from a reusable configuration object."""
        return cls(
            length=config.length,
            cells=config.cells,
            sound_speed=config.sound_speed,
            density=config.density,
            dt=config.dt,
            left_boundary=config.left_boundary,
            right_boundary=config.right_boundary,
            source_amplitude=config.source_amplitude,
            source_frequency=config.source_frequency,
            cross_sectional_area=config.cross_sectional_area,
            membrane=membrane,
        )

    def apply_boundary_conditions(self) -> None:
        """Patch the two boundary velocities according to boundary kind.

        - ``closed``: rigid wall, velocity pinned to zero.
        - ``open``: free end, radiates outward (simple absorbing update).
        - ``pressure_source``: drives the boundary pressure towards the
          source waveform.
        - ``velocity_source``: drives the boundary velocity directly
          with the source waveform.
        - ``membrane``: moves the pipe end with a pressure-driven membrane.
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

        if self.left_boundary == "membrane":
            assert self.membrane is not None
            pressure_difference = self.pressure[0] - self.membrane.back_pressure
            self.membrane.step(pressure_difference)
            self.velocity[0] = -(
                self.membrane.area / self.cross_sectional_area
            ) * self.membrane.velocity

        # RIGHT BOUNDARY
        if self.right_boundary == "closed":
            self.velocity[self.N] = 0

        if self.right_boundary == "open":
            self.velocity[self.N] += (
                2 * self.dt / (self.rho * self.dx)
                * self.pressure[-1]
            )
        
        if self.right_boundary == "membrane":
            assert self.membrane is not None
            pressure_difference = self.pressure[-1] - self.membrane.back_pressure
            self.membrane.step(pressure_difference)
            self.velocity[self.N] = (
                self.membrane.area / self.cross_sectional_area
            ) * self.membrane.velocity

    def source_input(self) -> float:
        return self.source_amplitude * np.sin(self.phase)

    def step(self) -> None:
        """Advance the simulation by one time step (leapfrog update)."""
        # 1. Update velocity from pressure gradient
        self.velocity[1:self.N] -= (
            self.dt / (self.rho * self.dx)
            * (self.pressure[1:] - self.pressure[:-1])
        )

        # 2. Apply boundary conditions
        self.apply_boundary_conditions()

        # 3. Update pressure from velocity gradient
        self.pressure -= (
            self.rho * self.c**2 * self.dt / self.dx
            * (self.velocity[1:] - self.velocity[:-1])
        )

        self.time += self.dt
        self.phase += 2 * np.pi * self.source_frequency * self.dt

    def advance(self, duration: float) -> None:
        """Step the simulation forward by ``duration`` seconds."""
        steps = round(duration / self.dt)

        for _ in range(steps):
            self.step()
