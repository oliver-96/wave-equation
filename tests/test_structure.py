"""Structural and configuration tests for the public simulation API."""

import unittest

from pipe_wave import CoupledPipeSystem, MembraneConfig, PipeConfig, WaveSimulation


class WaveSimulationConfigurationTests(unittest.TestCase):
    def test_left_source_boundaries_are_supported(self) -> None:
        for boundary in ("pressure_source", "velocity_source"):
            with self.subTest(boundary=boundary):
                simulation = WaveSimulation(left_boundary=boundary)  # type: ignore[arg-type]
                self.assertEqual(simulation.left_boundary, boundary)

    def test_right_source_boundary_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid right boundary"):
            WaveSimulation(right_boundary="velocity_source")  # type: ignore[arg-type]

    def test_coupled_system_advances_pipe_and_membrane(self) -> None:
        dt = 1e-6
        system = CoupledPipeSystem.from_configs(
            PipeConfig(
                dt=dt,
                left_boundary="velocity_source",
                right_boundary="membrane",
                cross_sectional_area=0.01,
            ),
            MembraneConfig(
                mass=0.01,
                damping=0.02,
                stiffness=100.0,
                area=0.01,
                dt=dt,
            ),
        )

        system.step()

        self.assertEqual(system.pipe.time, dt)
        self.assertIsNotNone(system.membrane)
        assert system.membrane is not None
        self.assertEqual(system.membrane.time, dt)
