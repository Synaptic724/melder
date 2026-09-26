"""User-style module for the inspect NameError probe: typing-only imports under TYPE_CHECKING.

Written in the repository's own recommended style (synaptic rule 5.14): the concrete type is
imported only for type checkers and named unquoted in annotations.
"""
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from decimal import Decimal


class Engine:
    """Plain dependency."""

    def __init__(self) -> None:
        self.hp = 100


class Car:
    """Consumer whose defaulted parameter and method annotations name a TYPE_CHECKING-only type."""

    ratio: Decimal

    def __init__(self, engine: Engine, price: Optional[Decimal] = None) -> None:
        self.engine = engine
        self.price = price

    def quote(self, markup: Decimal) -> Decimal:
        return markup

    @property
    def list_price(self) -> Decimal:
        return self.price


def make_car(engine: Engine, price: Optional[Decimal] = None) -> Car:
    """Factory with the same annotation pattern."""
    return Car(engine, price)


class Garage:
    """Late-bound consumer of Car (bound after conjure in the runtime-path probe)."""

    def __init__(self, car: Car) -> None:
        self.car = car
