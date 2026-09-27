"""
Importable spell classes for the structural-snapshot parity contracts.

They live in a module both the pytest process and a child process can import under the SAME dotted name
(`tests.mocks.spellbook.structural_snapshot_classes`), because the snapshot key renders annotation types as
(module, qualname) rows and the two-process contract compares those rows across processes.
"""


class Engine:
    """Provider without dependencies (unique)."""


class EngineAlternative:
    """Alternative Engine version staged into Engine's index by a notch."""


class Wheel:
    """Provider collected by Car (many)."""


class Radio:
    """Standalone provider with no dependents (unique); bound after conjure or transferred."""


class Car:
    """Consumer with one single socket and one collection socket (many)."""

    def __init__(self, engine: Engine, wheels: list[Wheel]) -> None:
        self.engine = engine
        self.wheels = wheels
