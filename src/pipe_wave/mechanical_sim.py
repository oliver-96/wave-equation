class Membrane:
    def __init__(
        self,
        mass: float,
        damping: float,
        stiffness: float,
        area: float,
        dt: float,
    ):
        self.mass = mass
        self.damping = damping
        self.stiffness = stiffness
        self.area = area
        self.dt = dt

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