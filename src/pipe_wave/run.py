import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class Simulation:
    def __init__(
        self,
        length: float = 1.0,
        cells: int = 200,
        sound_speed: float = 343.0,
        density: float = 1.2,
        dt: float = 1e-6,
        left_boundary: str = 'open',
        right_boundary: str = 'open'
    ):

        self.length = length
        self.N = cells
        self.c = sound_speed
        self.rho = density
        self.dt = dt


        valid_boundaries = {"open", "closed"}

        if left_boundary not in valid_boundaries:
            raise ValueError(f"Invalid left boundary: {left_boundary}")

        if right_boundary not in valid_boundaries:
            raise ValueError(f"Invalid right boundary: {right_boundary}")
        
        self.left_boundary = left_boundary
        self.right_boundary = right_boundary

        self.dx = length / cells

        self.x_pressure = (np.arange(cells) + 0.5) * self.dx
        self.x_velocity = (np.arange(cells + 1)) * self.dx

        self.pressure = np.zeros(cells)
        self.velocity = np.zeros(cells + 1)

        self.time = 0.0
    

    def apply_boundary_conditions(self) -> None:
        if self.left_boundary == "closed":
            self.velocity[0] = 0

        if self.right_boundary == "closed":
            self.velocity[self.N] = 0
        
        if self.left_boundary == "open":
            self.velocity[0] -= (
                2 * self.dt / (self.rho * self.dx)
                * self.pressure[0]
            )

        if self.right_boundary == "open":
            self.velocity[self.N] += (
                2 * self.dt / (self.rho * self.dx)
                * self.pressure[-1]
            )


    def step(self) -> None:
        # Update velocity from pressure gradient
        self.velocity[1:self.N] -= (
            self.dt / (self.rho * self.dx)
            * (self.pressure[1:] - self.pressure[:-1])
        )

        # Apply boundary conditions
        self.apply_boundary_conditions()

        # Update pressure from velocity gradient
        self.pressure -= (
            self.rho * self.c**2 * self.dt / self.dx
            * (self.velocity[1:] - self.velocity[:-1])
        )

        self.time += self.dt
    
    def advance(self, duration: float):
        steps = round(duration / self.dt)

        for _ in range(steps):
            self.step()



def simulate() -> None:

    sim = Simulation(
        left_boundary="closed",
        right_boundary="closed",
        )

    sim.pressure = np.exp(
        -((sim.x_pressure - 0.5) ** 2) / (2 * 0.06**2)
    )


    sim_time_per_frame = 0.00001

    fig, ax = plt.subplots()

    line, = ax.plot(sim.x_pressure, sim.pressure)

    ax.set_xlim(0, sim.length)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlabel("Position (m)")
    ax.set_ylabel("Pressure")

    time_text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

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



if __name__ == "__main__":
    simulate()

