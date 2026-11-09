"""
Importable spell classes for the structural-snapshot parity contracts.

They live in a module both the pytest process and a child process can import under the SAME dotted name
(`tests.mocks.spellbook.structural_snapshot_classes`), because the snapshot key renders annotation types as
(module, qualname) rows and the two-process contract compares those rows across processes.
"""


class Engine:
    """Provider without dependencies (unique)."""


class EngineAlternative:
    """
    Alternative Engine version the parity contracts staged into Engine's index by a notch, until 2026-11-07.

    Unused since then: Engine is bound bare so that `Car`'s class annotation reaches it (a class lookup reaches only
    a spell bound bare), and a bare Engine index admits only a class named Engine (every version of an index is bound
    the way its first version was, 0.2.8273), so the parity notch event stages an edited Engine instead
    (`_edited_engine` in test_spellbook_component_structural_snapshot_parity.py). Kept until the owner decides to
    remove it.
    """


class Wheel:
    """Provider collected by Car (many)."""


class Radio:
    """Standalone provider with no dependents (unique); bound after conjure or transferred."""


class Car:
    """Consumer with one single socket and one collection socket (many)."""

    def __init__(self, engine: Engine, wheels: list[Wheel]) -> None:
        self.engine = engine
        self.wheels = wheels
