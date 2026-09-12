"""Live matplotlib visualization for the wave-equation simulation.

Keeps the animation/UI wiring (figure, FuncAnimation) separate from
the physics in :mod:`pipe_wave.acoustic_simulation`.
"""

from collections import deque

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

from pipe_wave.config import MembraneConfig, PipeConfig
from pipe_wave.system import CoupledPipeSystem


def run_app() -> None:
    membrane_config = MembraneConfig(
        mass=0.01,
        damping=0.02,
        stiffness=100.0,
        area=0.01,
        dt=1e-6,
    )

    pipe_config = PipeConfig(
        dt=membrane_config.dt,
        left_boundary="velocity_source",
        right_boundary="membrane",
        source_amplitude=0.00001,
        source_frequency=171.5,
        cross_sectional_area=membrane_config.area,
    )
    system = CoupledPipeSystem.from_configs(pipe_config, membrane_config)
    pipe_sim = system.pipe

    sim_time_per_frame = 0.00005
    history_duration = 0.05
    membrane_times: deque[float] = deque([0.0])
    membrane_displacements: deque[float] = deque([0.0])

    fig, (pressure_ax, membrane_ax) = plt.subplots(2, 1, layout="constrained")

    pressure_line, = pressure_ax.plot(pipe_sim.x_pressure, pipe_sim.pressure)

    pressure_ax.set_xlim(0, pipe_sim.length)
    pressure_ax.set_ylim(-1.1, 1.1)
    pressure_ax.set_xlabel("Position (m)")
    pressure_ax.set_ylabel("Pressure (Pa)")

    time_text = pressure_ax.text(0.02, 0.95, "", transform=pressure_ax.transAxes)

    membrane_line, = membrane_ax.plot([], [], color="tab:orange")
    membrane_ax.set_xlim(0, history_duration)
    membrane_ax.set_ylim(-1e-12, 1e-12)
    membrane_ax.set_xlabel("Time (s)")
    membrane_ax.set_ylabel("Membrane displacement (m)")

    def update(_frame: int):
        system.advance(sim_time_per_frame)
        pressure_line.set_ydata(pipe_sim.pressure)

        assert system.membrane is not None
        membrane_times.append(pipe_sim.time)
        membrane_displacements.append(system.membrane.displacement)
        while membrane_times[0] < pipe_sim.time - history_duration:
            membrane_times.popleft()
            membrane_displacements.popleft()

        history_times = np.fromiter(membrane_times, dtype=float)
        history_displacements = np.fromiter(membrane_displacements, dtype=float)
        membrane_line.set_data(history_times, history_displacements)
        membrane_ax.set_xlim(
            max(0.0, pipe_sim.time - history_duration),
            max(history_duration, pipe_sim.time),
        )
        displacement_scale = max(np.max(np.abs(history_displacements)), 1e-12)
        membrane_ax.set_ylim(-1.2 * displacement_scale, 1.2 * displacement_scale)

        # Update displayed time
        time_text.set_text(
            f"t = {pipe_sim.time:.4f} s"
        )

        return pressure_line, membrane_line, time_text

    _animation = FuncAnimation(
        fig,
        update,
        interval=10,
        blit=False,
    )

    plt.show()
