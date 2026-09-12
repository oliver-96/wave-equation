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
    """A movable boundary that couples itself to the final pipe half-cell."""

    dt: float

    def step_from_pipe_cell(
        self,
        cell_pressure: float,
        *,
        density: float,
        half_cell_width: float,
        pipe_area: float,
    ) -> float:
        """Advance the boundary and return its outward volume velocity."""
