"""Configuration objects for assembling pipe-wave simulations."""

from dataclasses import dataclass

from pipe_wave.boundaries import LeftBoundaryKind, RightBoundaryKind


@dataclass(frozen=True)
class PipeConfig:
    """Parameters used to construct a :class:`WaveSimulation`."""

    length: float = 1.0
    cells: int = 200
    sound_speed: float = 343.0
    density: float = 1.2
    dt: float = 1e-6
    left_boundary: LeftBoundaryKind = "open"
    right_boundary: RightBoundaryKind = "open"
    source_amplitude: float = 1.0
    source_frequency: float = 100.0
    cross_sectional_area: float = 1.0


@dataclass(frozen=True)
class MembraneConfig:
    """Parameters used to construct a :class:`Membrane`."""

    mass: float
    damping: float
    stiffness: float
    area: float
    dt: float
    back_pressure: float = 0.0
