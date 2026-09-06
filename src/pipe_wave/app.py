"""Live matplotlib visualization for the wave-equation simulation.

Keeps the animation/UI wiring (figure, slider, FuncAnimation) separate
from the physics in :mod:`pipe_wave.simulation`.
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

from pipe_wave.simulation import Simulation


def run_app() -> None:
    sim = Simulation(
        left_boundary="velocity_source",
        right_boundary="closed",
        source_amplitude=0.000001,
        source_frequency=857.5,
    )

    sim_time_per_frame = 0.00005

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    line, = ax.plot(sim.x_pressure, sim.pressure)

    ax.set_xlim(0, sim.length)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlabel("Position (m)")
    ax.set_ylabel("Pressure")

    time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

    freq_ax = fig.add_axes([0.25, 0.1, 0.5, 0.03])
    freq_slider = Slider(
        ax=freq_ax,
        label="Frequency (Hz)",
        valmin=10,
        valmax=1000,
        valinit=sim.source_frequency,
    )

    def on_freq_change(val):
        sim.source_frequency = val

    freq_slider.on_changed(on_freq_change)

    def update(frame):
        sim.advance(sim_time_per_frame)
        line.set_ydata(sim.pressure)

        # Update displayed time
        time_text.set_text(
            f"t = {sim.time:.4f} s"
        )

        return line, time_text

    animation = FuncAnimation(
        fig,
        update,
        interval=10,
        blit=True,
    )

    plt.show()
