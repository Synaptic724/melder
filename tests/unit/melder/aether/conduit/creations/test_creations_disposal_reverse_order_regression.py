"""Regression: scoped disposal runs in reverse creation order.

Symptom:
    `Creations._dispose_disposable_registry` walked `_disposable_creations`
    forward. Dict iteration is insertion-ordered and insertion happens at
    creation time, so entries were disposed oldest-first. Resolution builds a
    dependency BEFORE the dependent that holds it, so the dependency was
    registered first and therefore torn down first - while a dependent's own
    disposal method could still reach for it. Same defect class as
    python-dependency-injector issue #432, where a database session was closed
    ahead of the token whose teardown still needed that session.

Contract under test:
    Disposal walks the scope newest-first, both across keys and inside a single
    `Existence.many` bucket, so a dependent is always disposed before the
    dependency it holds.

Scope note:
    These tests cover ordering WITHIN one `Creations` store. Ordering BETWEEN
    stores (lesser conduit before root, narrower existence before broader) is
    owned by the conduit cleanup cascade and is not exercised here.
"""

from typing import List, Optional

from melder.aether.conduit.creations.creations import Creations


class OrderRecorder:
    """Creation double that records the sequence in which disposal happens.

    Contract:
        - `dispose()` appends this probe's label to the shared log exactly once
          per invocation, so a test can assert the full teardown sequence
          rather than only that teardown occurred.
    """

    def __init__(self, label: str, log: List[str]) -> None:
        """Bind the probe to a label and the shared disposal log.

        Args:
            label: Identifier appended to the log on disposal.
            log: Shared list accumulating disposal order across probes.
        """
        self.label = label
        self._log = log

    def dispose(self) -> None:
        """Record one disposal invocation against the shared log."""
        self._log.append(self.label)


class Pool:
    """Dependency double standing in for a resource a dependent still needs.

    Contract:
        - `closed` starts `False` and flips on `close()`.
        - Models the object that resolution registers FIRST, because a
          dependent asked for it during construction.
    """

    def __init__(self) -> None:
        """Create the pool in an open state."""
        self.closed = False

    def close(self) -> None:
        """Mark the pool closed."""
        self.closed = True


class Session:
    """Dependent double whose teardown reaches into its injected dependency.

    Contract:
        - `close()` records whether the held `Pool` was still open at the moment
          this object was disposed.
        - This is the shape that makes teardown order observable: under forward
          order the pool is already closed by the time the session tears down.
    """

    def __init__(self, pool: Pool) -> None:
        """Hold the injected pool without owning its lifecycle.

        Args:
            pool: Dependency registered before this object during resolution.
        """
        self._pool = pool
        self.saw_pool_open: Optional[bool] = None

    def close(self) -> None:
        """Record whether the held pool was still usable during teardown."""
        self.saw_pool_open = not self._pool.closed


def _make_store() -> Creations:
    """Build one scoped store with stable owner and scope identifiers.

    Returns:
        Creations: Empty store ready to accept scoped registrations.
    """
    return Creations(owner_conduit_id="conduit-1", id="conduit-1")


def test_unique_creations_dispose_newest_first() -> None:
    """Unique entries tear down in reverse creation order."""
    log: List[str] = []
    store = _make_store()

    for label in ("first", "second", "third"):
        store.add_creation(
            f"spell-{label}",
            OrderRecorder(label, log),
            has_disposal_methods=True,
            disposal_methods=["dispose"],
        )

    store.cleanup()

    assert log == ["third", "second", "first"]


def test_many_bucket_entries_dispose_newest_first() -> None:
    """Instances inside one `many` bucket tear down in reverse creation order."""
    log: List[str] = []
    store = _make_store()

    for label in ("first", "second", "third"):
        store.add_many_creations(
            "spell-many",
            OrderRecorder(label, log),
            has_disposal_methods=True,
            disposal_methods=["dispose"],
        )

    store.cleanup()

    assert log == ["third", "second", "first"]


def test_dependent_is_disposed_before_the_dependency_it_holds() -> None:
    """The #432 shape: a session's teardown still sees its pool open.

    Resolution registers `pool` first because `session` required it during
    construction. Forward disposal closed the pool first and the session's own
    teardown observed an already-closed dependency.
    """
    store = _make_store()

    pool = Pool()
    session = Session(pool)

    store.add_creation(
        "spell-pool",
        pool,
        has_disposal_methods=True,
        disposal_methods=["close"],
    )
    store.add_creation(
        "spell-session",
        session,
        has_disposal_methods=True,
        disposal_methods=["close"],
    )

    store.cleanup()

    assert session.saw_pool_open is True
    assert pool.closed is True


def test_clear_all_uses_the_same_reverse_order() -> None:
    """The reusable clear path shares the disposal walk, so it shares the order."""
    log: List[str] = []
    store = _make_store()

    for label in ("first", "second"):
        store.add_creation(
            f"spell-{label}",
            OrderRecorder(label, log),
            has_disposal_methods=True,
            disposal_methods=["dispose"],
        )

    store.clear_all()

    assert log == ["second", "first"]
