"""Clean annotations: none of these may be reported."""
from typing import TYPE_CHECKING, Any, ClassVar, List, Literal, Optional, TypeVar

if TYPE_CHECKING:
    from decimal import Decimal

T = TypeVar("T")


class Car:
    """Self references, class-scope names, TYPE_CHECKING-only names, forward references."""

    Alias: ClassVar[type] = int
    price: Decimal
    maybe: Optional["Car"] = None
    later: Truck

    def peer(self, other: Optional[Car], price: Optional[Decimal] = None) -> Car | None:
        """Unquoted self reference and a PEP 604 union without strings."""
        return other

    def uses_class_name(self, value: Alias) -> List["Car"]:
        """Class-scope name and a quoted generic argument."""
        return []

    def generic(self, item: T, mode: Literal["a", "b"]) -> T:
        """TypeVar and Literal values."""
        local: "NotEvaluated" | None = None
        return item


class Truck:
    """Defined after its first reference."""


def factory[U](value: U) -> U:
    """PEP 695 type parameter."""
    return value


def closure() -> None:
    """Nested function using an enclosing local."""
    from decimal import Context

    def inner(ctx: Context) -> Any:
        """Uses the enclosing function's import."""
        return ctx
