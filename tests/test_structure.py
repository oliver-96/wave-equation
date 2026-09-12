"""Structural and configuration tests for the public simulation API."""

import math
import unittest

import numpy as np

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

    def test_rigid_membrane_matches_closed_pipe(self) -> None:
        source_amplitude = 1e-5
        pipe_settings = {
            "length": 1.0,
            "cells": 200,
            "dt": 1e-6,
            "left_boundary": "velocity_source",
            "source_amplitude": source_amplitude,
            "source_frequency": 171.5,
            "cross_sectional_area": 0.01,
        }
        closed_pipe = WaveSimulation(right_boundary="closed", **pipe_settings)
        rigid_membrane = Membrane(
            mass=1e6,
            damping=0.02,
            stiffness=1e12,
            area=0.01,
            dt=1e-6,
        )
        membrane_pipe = WaveSimulation(
            right_boundary="membrane",
            membrane=rigid_membrane,
            **pipe_settings,
        )

        for _ in range(10_000):
            closed_pipe.step()
            membrane_pipe.step()

        self.assertLess(abs(membrane_pipe.velocity[-1]), source_amplitude * 1e-5)
        np.testing.assert_allclose(
            membrane_pipe.pressure,
            closed_pipe.pressure,
            rtol=1e-5,
            atol=1e-10,
        )

    def test_higher_membrane_damping_lowers_and_broadens_response(self) -> None:
        frequencies = np.arange(300.0, 701.0, 50.0)

        def displacement_amplitudes(damping: float) -> np.ndarray:
            amplitudes = []
            for frequency in frequencies:
                dt = 5e-6
                membrane = Membrane(
                    mass=0.01,
                    damping=damping,
                    stiffness=100_000.0,
                    area=0.01,
                    dt=dt,
                )
                simulation = WaveSimulation(
                    length=0.1,
                    cells=20,
                    dt=dt,
                    left_boundary="velocity_source",
                    right_boundary="membrane",
                    source_amplitude=1e-3,
                    source_frequency=frequency,
                    cross_sectional_area=0.01,
                    membrane=membrane,
                )

                steady_displacements = []
                for step in range(12_000):
                    simulation.step()
                    if step >= 6_000:
                        steady_displacements.append(membrane.displacement)

                amplitudes.append(
                    (max(steady_displacements) - min(steady_displacements)) / 2
                )
            return np.asarray(amplitudes)

        low_damping = displacement_amplitudes(damping=2.0)
        high_damping = displacement_amplitudes(damping=20.0)

        self.assertLess(high_damping.max(), low_damping.max())

        def half_power_width(amplitudes: np.ndarray) -> float:
            half_power = amplitudes.max() / math.sqrt(2)
            frequencies_above_half_power = frequencies[amplitudes >= half_power]
            return frequencies_above_half_power[-1] - frequencies_above_half_power[0]

        self.assertGreater(
            half_power_width(high_damping),
            half_power_width(low_damping),
        )
