"""Mechanical boundary models for acoustic simulations."""


class Membrane:
    """Lumped mass-spring-damper model of a membrane sealing a tube end.

    Positive displacement and velocity point outward from the tube. The
    pressure passed to :meth:`step` must therefore be the tube-side pressure
    minus ``back_pressure``.
    """

    def __init__(
        self,
        mass: float,
        damping: float,
        stiffness: float,
        area: float,
        dt: float,
        back_pressure: float = 0.0,
    ) -> None:
        if mass <= 0:
            raise ValueError("mass must be positive")
        if damping < 0:
            raise ValueError("damping must be non-negative")
        if stiffness < 0:
            raise ValueError("stiffness must be non-negative")
        if area <= 0:
            raise ValueError("area must be positive")
        if dt <= 0:
            raise ValueError("dt must be positive")

        self.mass = mass
        self.damping = damping
        self.stiffness = stiffness
        self.area = area
        self.dt = dt
        self.back_pressure = back_pressure

        self.displacement = 0.0
        self.velocity = 0.0
        self.time = 0.0

    def step(self, pressure: float) -> None:
        """Advance the mechanical state from a membrane pressure difference."""
        force = pressure * self.area

        acceleration = (
            force
            - self.damping * self.velocity
            - self.stiffness * self.displacement
        ) / self.mass

        self.velocity += acceleration * self.dt
        self.displacement += self.velocity * self.dt

        self.time += self.dt

    def step_from_pipe_cell(
        self,
        cell_pressure: float,
        *,
        density: float,
        half_cell_width: float,
        pipe_area: float,
    ) -> float:
        """Couple the membrane to a pipe end and return outward volume velocity.

        The wall pressure is solved from the membrane equation of motion and
        the acoustic momentum equation across the final half-cell. This avoids
        treating the cell-centre pressure as if it were located at the wall.
        """
        if density <= 0:
            raise ValueError("density must be positive")
        if half_cell_width <= 0:
            raise ValueError("half_cell_width must be positive")
        if pipe_area <= 0:
            raise ValueError("pipe_area must be positive")

        area_ratio = self.area / pipe_area
        acoustic_conductance = 1 / (density * half_cell_width)
        mechanical_conductance = area_ratio * self.area / self.mass
        restoring_force = (
            self.damping * self.velocity
            + self.stiffness * self.displacement
        )

        wall_pressure = (
            acoustic_conductance * cell_pressure
            + area_ratio
            / self.mass
            * (self.area * self.back_pressure + restoring_force)
        ) / (acoustic_conductance + mechanical_conductance)

        self.step(wall_pressure - self.back_pressure)
        return self.area * self.velocity
