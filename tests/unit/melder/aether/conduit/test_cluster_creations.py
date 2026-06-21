"""tests/unit/melder/aether/conduit/test_cluster_creations.py

Validation: Not run.

Unit tests for `melder.aether.conduit.creations.cluster_creations.ClusterCreations`.
Focus: the active-state contract and leader-store ISOLATION, exercised against a
fake store with no Aether / Conduit runtime. (The conduit-unit conftest resets
the singletons automatically; these tests do not need them.)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pytest

from melder.aether.conduit.creations.cluster_creations import ClusterCreations


class _FakeStore:
    """Minimal stand-in for an elected leader's `Creations` store."""

    def __init__(self, tag: str) -> None:
        self.tag = tag
        self._items: Dict[str, Any] = {}

    def get_creation(self, spell_id: str) -> Optional[Any]:
        return self._items.get(spell_id)

    def add_creation(
        self,
        spell_id: str,
        item: object,
        *,
        has_disposal_methods: bool = False,
        disposal_methods: Optional[List[str]] = None,
    ) -> None:
        self._items[spell_id] = item


def test_new_facade_is_disabled() -> None:
    assert ClusterCreations().is_active() is False


def test_disabled_facade_hard_errors_on_use() -> None:
    facade = ClusterCreations()
    with pytest.raises(RuntimeError):
        facade.resolved_store()
    with pytest.raises(RuntimeError):
        facade.get_creation("spell")
    with pytest.raises(RuntimeError):
        facade.add_creation("spell", object())


def test_bind_activates_and_delegates_through_to_store() -> None:
    store = _FakeStore("leader")
    facade = ClusterCreations()
    facade.bind(store)
    assert facade.is_active() is True
    assert facade.resolved_store() is store
    sentinel = object()
    facade.add_creation("s1", sentinel)
    assert facade.get_creation("s1") is sentinel
    assert store.get_creation("s1") is sentinel  # written through to the real store


def test_unbind_deactivates_and_drops_store() -> None:
    facade = ClusterCreations()
    facade.bind(_FakeStore("leader"))
    facade.unbind()
    assert facade.is_active() is False
    with pytest.raises(RuntimeError):
        facade.resolved_store()


def test_rebind_retargets_to_new_leader_store() -> None:
    facade = ClusterCreations()
    first = _FakeStore("first")
    second = _FakeStore("second")
    facade.bind(first)
    assert facade.resolved_store() is first
    facade.unbind()
    facade.bind(second)
    assert facade.resolved_store() is second


def test_two_facades_resolve_their_own_leader_store() -> None:
    """Facade-level isolation: each cluster's facade fronts its OWN leader store."""
    store_a = _FakeStore("a")
    store_b = _FakeStore("b")
    facade_a = ClusterCreations()
    facade_b = ClusterCreations()
    facade_a.bind(store_a)
    facade_b.bind(store_b)
    assert facade_a.resolved_store() is store_a
    assert facade_b.resolved_store() is store_b
    item_a = object()
    facade_a.add_creation("s", item_a)
    assert facade_a.get_creation("s") is item_a
    assert facade_b.get_creation("s") is None  # no cross-leak between clusters


def test_cleanup_is_idempotent_and_disables() -> None:
    facade = ClusterCreations()
    facade.bind(_FakeStore("leader"))
    facade.cleanup()
    facade.cleanup()  # idempotent: must not raise
    with pytest.raises(Exception):
        facade.is_active()  # check_cleaned trips after cleanup
