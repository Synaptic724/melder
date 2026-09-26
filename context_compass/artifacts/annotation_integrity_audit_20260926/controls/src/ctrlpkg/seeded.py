"""Seeded defects for the annotation audit's negative control. Each DEFECT line must be reported."""
from typing import TYPE_CHECKING, Literal, Optional, List

if TYPE_CHECKING:
    from decimal import Decimal


class Engine:
    """Plain class."""

    limit: "Engine" | None = None                        # DEFECT 1 class variable string union

    def peer(self, other: "Engine" | None) -> None:      # DEFECT 2 parameter string union
        """Method."""

    def back(self) -> None | "Engine":                   # DEFECT 3 return string union
        """Method."""

    class Inner:
        """Nested class."""

        def f(self, x: int | "Engine") -> None:          # DEFECT 4 nested class method
            """Nested method."""


module_var: "Decimal" | None = None                       # DEFECT 5 module variable string union


def outer() -> None:
    """Function with a nested function."""

    def inner(x: Optional[Engine] | "Engine") -> None:   # DEFECT 6 nested function (static only)
        """Nested function."""


def literal_union(mode: Literal["a" | "b"]) -> None:      # DEFECT 7 string union inside Literal
    """Literal misuse."""


def in_string(x: "'Engine' | None") -> None:              # DEFECT 8 inside a string annotation (static)
    """String annotation hiding a string union."""


def undefined(x: Missing) -> None:                         # DEFECT 9 undefined name
    """Typo'd / never-imported name."""
