"""Boundary types shared by acoustic models and boundary devices."""

from typing import Literal, Protocol


LeftBoundaryKind = Literal[
    "open", "closed", "pressure_source", "velocity_source", "membrane"
]
RightBoundaryKind = Literal["open", "closed", "membrane"]

_VALID_LEFT_BOUNDARIES: set[LeftBoundaryKind] = {
    "open",
    "closed",
    "pressure_source",
    "velocity_source",
    "membrane",
}
_VALID_RIGHT_BOUNDARIES: set[RightBoundaryKind] = {"open", "closed", "membrane"}


class PressureDrivenBoundary(Protocol):
    """A movable boundary advanced from its pressure difference."""

    area: float
    back_pressure: float
    dt: float
    velocity: float

    def step(self, pressure: float) -> None:
        """Advance the boundary state using the supplied pressure difference."""
