"""Composition helpers for complete pipe-wave simulations."""

from dataclasses import asdict

from pipe_wave.acoustic_simulation import WaveSimulation
from pipe_wave.config import MembraneConfig, PipeConfig
from pipe_wave.membrane import Membrane


class CoupledPipeSystem:
    """A pipe simulation and its optional pressure-driven membrane."""

    def __init__(self, pipe: WaveSimulation, membrane: Membrane | None = None) -> None:
        self.pipe = pipe
        self.membrane = membrane

    @classmethod
    def from_configs(
        cls,
        pipe_config: PipeConfig,
        membrane_config: MembraneConfig | None = None,
    ) -> "CoupledPipeSystem":
        membrane = (
            Membrane(**asdict(membrane_config))
            if membrane_config is not None
            else None
        )
        pipe = WaveSimulation.from_config(pipe_config, membrane=membrane)
        return cls(pipe, membrane)

    def step(self) -> None:
        """Advance the complete coupled system by one time step."""
        self.pipe.step()

    def advance(self, duration: float) -> None:
        """Advance the complete coupled system by ``duration`` seconds."""
        self.pipe.advance(duration)
