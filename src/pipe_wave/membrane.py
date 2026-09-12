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
        force = pressure * self.area

        acceleration = (
            force
            - self.damping * self.velocity
            - self.stiffness * self.displacement
        ) / self.mass

        self.velocity += acceleration * self.dt
        self.displacement += self.velocity * self.dt

        self.time += self.dt
