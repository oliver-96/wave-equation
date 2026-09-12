"""Live matplotlib visualization for the wave-equation simulation.

Keeps the animation/UI wiring (figure, FuncAnimation) separate from
the physics in :mod:`pipe_wave.acoustic_simulation`.
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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

    fig, ax = plt.subplots()

    line, = ax.plot(pipe_sim.x_pressure, pipe_sim.pressure)

    ax.set_xlim(0, pipe_sim.length)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlabel("Position (m)")
    ax.set_ylabel("Pressure")

    time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

    def update(_frame: int):
        system.advance(sim_time_per_frame)
        line.set_ydata(pipe_sim.pressure)

        # Update displayed time
        time_text.set_text(
            f"t = {pipe_sim.time:.4f} s"
        )

        return line, time_text

    _animation = FuncAnimation(
        fig,
        update,
        interval=10,
        blit=True,
    )

    plt.show()
