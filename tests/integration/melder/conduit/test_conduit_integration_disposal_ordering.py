"""Integration: scoped teardown runs dependents before their dependencies.

Symptom:
    `Creations._dispose_disposable_registry` walked `_disposable_creations`
    forward. Dict iteration is insertion-ordered and insertion happens at
    creation time, so entries were disposed oldest-first. Resolution builds a
    dependency BEFORE the dependent that holds it, so the dependency was torn
    down first - while the dependent's own disposal method could still reach for
    it. Same defect class as python-dependency-injector issue #432.

Why these are integration tests rather than unit tests:
    The unit regression for this fix hand-inserts entries into a bare
    `Creations` store in an order the test chooses, which quietly ASSUMES the
    thing that actually needs proving - that melder's real resolution registers
    a dependency ahead of its dependent. These tests build a real Spellbook,
    conjure a real Conduit, and let genuine constructor DI decide the insertion
    order, so they fail if that assumption ever stops holding.

Contract under test:
    Across a real resolution graph, teardown visits dependents before the
    dependencies they hold, for conduit scope and for spellspace scope, at
    depth greater than two.
"""

from typing import ClassVar, List, Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    set_frame_system_state_for_spellbook_configuration,
)


class _TeardownLog:
    """Test-local sink recording the order in which teardown happened.

    Contract:
        - Melder constructs the spells under test through DI, so a shared
          class-level sink is the seam available for observing order; the
          probes cannot be handed a log through their constructors without
          changing the dependency shape the test exists to exercise.
        - `reset()` runs per test through an autouse fixture.
    """

    entries: ClassVar[List[str]] = []

    @classmethod
    def reset(cls) -> None:
        """Clear the recorded teardown sequence."""
        cls.entries = []

    @classmethod
    def record(cls, label: str) -> None:
        """Append one teardown label in call order.

        Args:
            label: Identifier for the object being torn down.
        """
        cls.entries.append(label)


class _Engine:
    """Leaf dependency: built first, therefore must be disposed last.

    Contract:
        - `closed` flips on teardown so dependents can observe usability.
    """

    def __init__(self) -> None:
        """Create the engine in an open state."""
        self.closed = False

    def cleanup(self) -> None:
        """Close the engine and record the teardown."""
        self.closed = True
        _TeardownLog.record("engine")


class _Pool:
    """Middle node: depends on `_Engine`, is depended on by `_Session`.

    Contract:
        - Records whether its own dependency was still open during teardown.
    """

    def __init__(self, engine: _Engine) -> None:
        """Hold the injected engine without owning its lifecycle.

        Args:
            engine: Dependency resolved and registered before this object.
        """
        self._engine = engine
        self.closed = False
        self.saw_engine_open: Optional[bool] = None

    def cleanup(self) -> None:
        """Record dependency usability, close, and log the teardown."""
        self.saw_engine_open = not self._engine.closed
        self.closed = True
        _TeardownLog.record("pool")


class _Worker:
    """Sibling probe for `Existence.many`, identified by construction sequence.

    Contract:
        - Each instance takes the next ordinal, so a bucket of three records
          three DISTINCT labels and the teardown assertion actually proves
          sequence rather than merely proving three disposals happened.
        - `next_ordinal` is reset per test by the autouse fixture.
    """

    next_ordinal: ClassVar[int] = 0

    @classmethod
    def reset_ordinals(cls) -> None:
        """Restart the construction sequence at zero."""
        cls.next_ordinal = 0

    def __init__(self) -> None:
        """Claim the next construction ordinal."""
        type(self).next_ordinal += 1
        self.ordinal = type(self).next_ordinal
        self.closed = False

    def cleanup(self) -> None:
        """Close the worker and record its ordinal in teardown order."""
        self.closed = True
        _TeardownLog.record(f"worker-{self.ordinal}")


class _Session:
    """Outermost dependent: built last, therefore must be disposed first.

    Contract:
        - Records whether its injected pool was still open during teardown.
    """

    def __init__(self, pool: _Pool) -> None:
        """Hold the injected pool without owning its lifecycle.

        Args:
            pool: Dependency resolved and registered before this object.
        """
        self._pool = pool
        self.saw_pool_open: Optional[bool] = None

    def cleanup(self) -> None:
        """Record dependency usability and log the teardown."""
        self.saw_pool_open = not self._pool.closed
        _TeardownLog.record("session")


@pytest.fixture(autouse=True)
def reset_runtime_singletons_and_log() -> None:
    """Give each test a clean Aether singleton and an empty teardown log.

    Contract:
        - Resets the Aether singleton and rebinds Spellbook/Conduit references
          before and after each test, matching the convention used by the other
          conduit integration suites.
        - Clears `_TeardownLog` so order assertions cannot inherit entries from
          a previous test.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    _TeardownLog.reset()
    _Worker.reset_ordinals()
    yield
    _TeardownLog.reset()
    _Worker.reset_ordinals()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _build_spellbook() -> SpellbookConfiguration:
    """Build a dynamic configuration with disposal enabled.

    Contract:
        - `disposal` and `disposal_method_names` are idempotent, set-once keys,
          so they are written BEFORE `load_default_dictionary()` seeds them.
          Setting them afterwards is permanently refused.

    Returns:
        SpellbookConfiguration: Configuration ready to construct a Spellbook.
    """
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "dynamic")
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["cleanup"])
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_conduit_integration_teardown_visits_dependents_before_dependencies() -> None:
    """A three-deep resolution chain tears down in exact reverse build order.

    Purpose:
        Prove the ordering claim against real DI rather than hand-inserted
        entries: melding `_Session` builds engine, then pool, then session, so
        teardown must run session, pool, engine.
    """
    configuration = _build_spellbook()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=_Engine,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    spellbook.bind(
        spell=_Pool,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    session_id = spellbook.bind(
        spell=_Session,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )

    conduit = spellbook.conjure(dynamic=True, name="root")
    session = conduit.meld(spell_id=session_id)
    assert isinstance(session, _Session)

    conduit.cleanup()

    assert _TeardownLog.entries == ["session", "pool", "engine"]


def test_conduit_integration_dependent_sees_its_dependency_still_usable() -> None:
    """Each dependent observes its dependency as open during its own teardown.

    Purpose:
        Assert the behavioural consequence rather than only the sequence. Under
        forward disposal the engine and pool close first and both observations
        flip to False, which is the #432 failure.
    """
    configuration = _build_spellbook()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=_Engine,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    spellbook.bind(
        spell=_Pool,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    session_id = spellbook.bind(
        spell=_Session,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )

    conduit = spellbook.conjure(dynamic=True, name="root")
    session = conduit.meld(spell_id=session_id)
    pool = session._pool

    conduit.cleanup()

    assert session.saw_pool_open is True
    assert pool.saw_engine_open is True


def test_conduit_integration_spellspace_scope_disposes_newest_first() -> None:
    """Spellspace scope shares the ordering because it uses a plain `Creations`.

    Purpose:
        Cover the second real store type. `SpellSpace` instantiates the generic
        `Creations` directly rather than a spellspace-specific subclass, so the
        same disposal walk governs it; this test fails if that ever diverges.
    """
    configuration = _build_spellbook()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=_Engine,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    spellbook.bind(
        spell=_Pool,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    session_id = spellbook.bind(
        spell=_Session,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )

    conduit = spellbook.conjure(dynamic=True, name="root")
    try:
        with conduit.enter_spellspace() as space:
            session = space.meld(spell_id=session_id)
            assert isinstance(session, _Session)

        assert _TeardownLog.entries == ["session", "pool", "engine"]
    finally:
        conduit.cleanup()


def test_conduit_integration_many_bucket_disposes_newest_instance_first() -> None:
    """Instances inside one `Existence.many` bucket tear down newest-first.

    Purpose:
        Cover the inner walk. Bucket members are siblings of one spell and hold
        no references to each other, so this asserts the sequence directly
        rather than a usability consequence.
    """
    configuration = _build_spellbook()
    spellbook = Spellbook(configuration=configuration)
    worker_id = spellbook.bind(
        spell=_Worker,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(dynamic=True, name="root")
    first = conduit.meld(spell_id=worker_id)
    second = conduit.meld(spell_id=worker_id)
    third = conduit.meld(spell_id=worker_id)
    assert (first.ordinal, second.ordinal, third.ordinal) == (1, 2, 3)

    conduit.cleanup()

    assert _TeardownLog.entries == ["worker-3", "worker-2", "worker-1"]
    assert first.closed is True
    assert second.closed is True
    assert third.closed is True
