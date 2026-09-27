"""User module for the class-annotation probe: one class per annotation shape (Python 3.14 lazy annotations)."""
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from decimal import Decimal


class ResolvedFields:
    """Every class-level annotation resolves at runtime, one of them quoted."""
    count: int
    name: "str"


class TypeCheckingField:
    """One field names a TYPE_CHECKING-only type; set PROBE_EXTRA_FIELD to add a second one."""
    amount: Decimal
    label: str
    if os.environ.get("PROBE_EXTRA_FIELD"):
        extra: Decimal


class QuotedUnavailable:
    """A quoted annotation naming a TYPE_CHECKING-only type."""
    amount: "Decimal"
    label: str


class NestedUnavailable:
    """The unavailable name is nested inside a generic."""
    amounts: list[Decimal]
    total: Optional[Decimal]
    count: int


@dataclass
class DataclassField:
    """Dataclass whose field names a TYPE_CHECKING-only type."""
    amount: Decimal
    label: str = "x"


class NoAnnotations:
    """No class-level annotations at all."""


def candidates() -> dict:
    """Return the probe classes by name."""
    return {
        "ResolvedFields": ResolvedFields,
        "TypeCheckingField": TypeCheckingField,
        "QuotedUnavailable": QuotedUnavailable,
        "NestedUnavailable": NestedUnavailable,
        "DataclassField": DataclassField,
        "NoAnnotations": NoAnnotations,
    }
