"""Structural and configuration tests for the public simulation API."""

import unittest

import math

from pipe_wave import (
    CoupledPipeSystem,
    Membrane,
    MembraneConfig,
    PipeConfig,
    WaveSimulation,
)


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

    def test_membrane_uses_half_cell_wall_pressure(self) -> None:
        membrane = Membrane(
            mass=0.01,
            damping=0.0,
            stiffness=0.0,
            area=0.01,
            dt=1e-6,
        )

        volume_velocity = membrane.step_from_pipe_cell(
            2.0,
            density=1.2,
            half_cell_width=0.0025,
            pipe_area=0.01,
        )

        acoustic_conductance = 1 / (1.2 * 0.0025)
        mechanical_conductance = 0.01 / 0.01 * 0.01 / 0.01
        expected_wall_pressure = 2.0 * acoustic_conductance / (
            acoustic_conductance + mechanical_conductance
        )
        expected_velocity = expected_wall_pressure * 0.01 / 0.01 * 1e-6

        self.assertTrue(math.isclose(membrane.velocity, expected_velocity))
        self.assertTrue(
            math.isclose(volume_velocity, membrane.area * expected_velocity)
        )
