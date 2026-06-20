"""tests/aether/conduit/test_conduit_cluster.py

Validation: Not run.

These tests target `melder.aether.conduit.conduit_cluster.ConduitCluster`.
They focus on membership tracking and sharing contracts without running
full integration flows.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Any, Optional, Iterable, Dict, Union, Tuple

import pytest
from unittest.mock import MagicMock

from melder.aether.conduit.conduit_cluster import ConduitCluster
from melder.aether.conduit.creations.cluster_creations import ClusterCreations
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence


class _SpellStub:
    """Minimal spell stub with existence and indexing metadata."""

    def __init__(self, spell_id: str, existence: Existence, permissions: str = "create") -> None:
        """Initialize a spell stub with the identifiers and existence scope."""
        self.spell_id = spell_id
        self.spell_index = SpellIndex(spell_id)
        self.existence: Existence = existence
        self.permissions = permissions


class _SpellNoExistenceStub:
    """Spell stub missing the `existence` attribute for filter coverage."""

    def __init__(self, spell_id: str) -> None:
        """Initialize the stub with only a spell id and index."""
        self.spell_id = spell_id
        self.spell_index = SpellIndex(spell_id)


class _SpellNoPermissionsStub:
    """Spell stub that omits permissions to exercise default permission fallback."""

    def __init__(self, spell_id: str, existence: Existence) -> None:
        """Initialize a spell stub without a permissions attribute."""
        self.spell_id = spell_id
        self.spell_index = SpellIndex(spell_id)
        self.existence = existence


class _SpellbookStub:
    """Spellbook stub exposing `_spells` and `_lock`."""

    def __init__(self, spells: list[Any]) -> None:
        """Initialize the spellbook with a lock and a SpellIndex-keyed map."""
        self._lock = threading.RLock()
        self._spells = {spell.spell_index: spell for spell in spells}


class _SpellbookNoSpellsStub:
    """Spellbook stub that reports no spell registry."""

    def __init__(self) -> None:
        """Initialize with a lock and a None spells map."""
        self._lock = threading.RLock()
        self._spells = None


class _ConduitStub:
    """Conduit stub that records share/contract calls for assertions."""

    def __init__(
            self,
            conduit_id: str,
            spellbook: Optional[_SpellbookStub],
            aetheric_frame: str = "default",
            conduit_state: ConduitState = ConduitState.normal,
            raise_on: Optional[dict[str, set[str]]] = None,
    ) -> None:
        """Initialize the conduit stub with spellbook and optional raise rules."""
        self._id = conduit_id
        self._spellbook = spellbook
        self._aetheric_frame_name = aetheric_frame
        self._conduit_state = conduit_state
        self._raise_on = raise_on or {}
        self.contract_with_deps_calls: list[dict[str, Any]] = []
        self.contract_calls: list[dict[str, Any]] = []
        self.remove_root_calls: list[dict[str, Any]] = []

    def _should_raise(self, method: str, spell_id: str) -> bool:
        """Return True if the given method should raise for spell_id."""
        return spell_id in self._raise_on.get(method, set())

    def add_spell_to_contract_with_dependencies(
            self,
            *,
            spell: Any,
            conduit: Any,
            permissions: str,
            aetheric_frame: str,
    ) -> None:
        """Record dependency-aware contract calls and optionally raise."""
        self.contract_with_deps_calls.append(
            {
                "spell": spell,
                "conduit": conduit,
                "permissions": permissions,
                "aetheric_frame": aetheric_frame,
            }
        )
        if self._should_raise("with_deps", spell.spell_id):
            raise RuntimeError("simulated contract failure")

    def add_spell_to_contract(
            self,
            *,
            spell: Any,
            conduit: Any,
            permissions: str,
            aetheric_frame: str,
            reason: DetailReason,
            root_spell_id: str,
            link_dependencies: bool,
    ) -> None:
        """Record non-dependency contract calls and optionally raise."""
        self.contract_calls.append(
            {
                "spell": spell,
                "conduit": conduit,
                "permissions": permissions,
                "aetheric_frame": aetheric_frame,
                "reason": reason,
                "root_spell_id": root_spell_id,
                "link_dependencies": link_dependencies,
            }
        )
        if self._should_raise("contract", spell.spell_id):
            raise RuntimeError("simulated contract failure")

    def remove_root_from_contracts(
            self,
            *,
            root_spell_id: str,
            conduit: Any,
            aetheric_frame: str,
    ) -> None:
        """Record contract removals and optionally raise."""
        self.remove_root_calls.append(
            {
                "root_spell_id": root_spell_id,
                "conduit": conduit,
                "aetheric_frame": aetheric_frame,
            }
        )
        if self._should_raise("remove", root_spell_id):
            raise RuntimeError("simulated removal failure")

    @contextmanager
    def transaction(
            self,
            transaction_type: Union[ChangeTransactionType, str],
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable[Any]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> "_ConduitStub":
        """
        Provide a no-op transaction context manager for cluster tests.

        Purpose:
            Allow ConduitCluster to call transaction(...) on stub conduits
            without affecting test behavior.
        Contract:
            - Accepts transaction parameters but does not enforce them.
            - Yields self and performs no cleanup.
        Args:
            transaction_type: Change-control transaction type identifier.
            conduit_ids: Optional conduit ids participating in the request.
            conduits: Optional conduit objects participating in the request.
            scope_keys: Optional scope keys for conflict checks.
            scope_hashes: Optional scope hashes for conflict checks.
            binding_keys: Optional binding keys for the request.
            contract_keys: Optional contract keys for the request.
            metadata: Optional diagnostic metadata.
        Returns:
            _ConduitStub: The stub conduit instance.
        """
        yield self


class _ConduitNoFrameStub:
    """Conduit stub that intentionally lacks the `_aetheric_frame` attribute."""

    def __init__(self, conduit_id: str, spellbook: Optional[_SpellbookStub]) -> None:
        """Initialize a conduit stub without aetheric frame metadata."""
        self._id = conduit_id
        self._spellbook = spellbook
        self._conduit_state = ConduitState.normal


class _FrameStub:
    """Frame-local registry stub exposing conduit storage plus frame name."""

    def __init__(
            self,
            conduits: list[_ConduitStub],
            frame_name: str = "default",
    ) -> None:
        """Initialize the conduit lookup surface for cluster tests."""
        self.frame_name = frame_name
        self._conduits = {conduit._id: conduit for conduit in conduits}

def _make_cluster(
        name: str = "cluster",
        registry: Optional[Dict[str, _ConduitStub]] = None,
        aetheric_frame_name: str = "default",
        auto_link_dependencies: bool = True,
) -> ConduitCluster:
    """Build a ConduitCluster with the narrow registry plus frame-name contract."""
    if registry is None:
        registry = {}
    return ConduitCluster(
        name,
        registry,
        aetheric_frame_name,
        DevopsInformationRegistry(aetheric_frame_name),
        auto_link_dependencies,
    )


@pytest.fixture
def cluster() -> ConduitCluster:
    """Provide a default ConduitCluster for tests."""
    return _make_cluster("cluster")


def test_get_members_returns_snapshot(cluster: ConduitCluster) -> None:
    """Verify get_members returns a defensive copy."""
    cluster.add_member("conduit-1")

    snapshot = cluster.get_members()
    snapshot.remove("conduit-1")

    assert cluster.get_members() == {"conduit-1"}


def test_get_shared_spells_returns_snapshot(cluster: ConduitCluster) -> None:
    """Verify get_shared_spells returns defensive copies of buckets."""
    index = SpellIndex("spell-1")
    cluster.add_shared_spell("owner-1", index)

    snapshot = cluster.get_shared_spells()
    snapshot["owner-1"].clear()

    assert cluster.get_shared_spells()["owner-1"] == {index}


def test_remove_member_clears_shared_spells_for_owner(cluster: ConduitCluster) -> None:
    """Verify remove_member drops the owner bucket from shared_spells."""
    index = SpellIndex("spell-1")
    cluster.add_member("owner-1")
    cluster.add_shared_spell("owner-1", index)

    cluster.remove_member("owner-1")

    assert "owner-1" not in cluster.get_members()
    assert "owner-1" not in cluster.get_shared_spells()


def test_add_and_remove_shared_spell_drops_empty_bucket(cluster: ConduitCluster) -> None:
    """Verify empty shared buckets are removed after the last spell is removed."""
    index = SpellIndex("spell-1")
    cluster.add_shared_spell("owner-1", index)

    cluster.remove_shared_spell("owner-1", index)

    assert "owner-1" not in cluster.get_shared_spells()


def test_remove_shared_spell_noop_for_missing_owner(cluster: ConduitCluster) -> None:
    """Verify remove_shared_spell is a no-op when the owner is unknown."""
    cluster.remove_shared_spell("missing-owner", SpellIndex("spell-1"))


def test_refresh_shareable_roots_adds_cluster_scoped_spells(cluster: ConduitCluster) -> None:
    """Verify refresh_shareable_roots captures only cluster-scoped spells."""
    shareable = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    not_shareable = _SpellStub("spell-2", Existence.unique)
    no_existence = _SpellNoExistenceStub("spell-3")
    owner = _ConduitStub("owner-1", _SpellbookStub([shareable, not_shareable, no_existence]))

    cluster.refresh_shareable_roots(owner)

    shared = cluster.get_shared_spells()
    assert shared[owner._id] == {shareable.spell_index}


def test_refresh_shareable_roots_no_spellbook_noop(cluster: ConduitCluster) -> None:
    """Verify refresh_shareable_roots is a no-op if the spellbook is missing."""
    owner = _ConduitStub("owner-1", None)

    cluster.refresh_shareable_roots(owner)

    assert cluster.get_shared_spells() == {}


def test_handle_join_shares_between_members() -> None:
    """Verify handle_join shares roots in both directions for new members."""
    spell_a = _SpellStub("spell-a", Existence.unique_per_conduit_cluster)
    spell_b = _SpellStub("spell-b", Existence.unique_per_conduit_cluster)
    conduit_a = _ConduitStub("conduit-a", _SpellbookStub([spell_a]), aetheric_frame="frame-a")
    conduit_b = _ConduitStub("conduit-b", _SpellbookStub([spell_b]), aetheric_frame="frame-b")
    frame = _FrameStub([conduit_a, conduit_b], frame_name="frame-x")
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)

    cluster.handle_join(conduit_a)
    cluster.handle_join(conduit_b)

    assert conduit_b.contract_calls == [
        {
            "spell": spell_a,
            "conduit": conduit_a,
            "permissions": spell_a.permissions,
            "aetheric_frame": "frame-x",
            "reason": DetailReason.root,
            "root_spell_id": cluster._cluster_root_id(conduit_a._id, spell_a.spell_id),
            "link_dependencies": True,
        }
    ]
    assert conduit_a.contract_calls == [
        {
            "spell": spell_b,
            "conduit": conduit_b,
            "permissions": spell_b.permissions,
            "aetheric_frame": "frame-x",
            "reason": DetailReason.root,
            "root_spell_id": cluster._cluster_root_id(conduit_b._id, spell_b.spell_id),
            "link_dependencies": True,
        }
    ]


def test_handle_join_rejects_non_normal_conduit() -> None:
    """Verify cluster join rejects lesser/non-normal conduits."""
    cluster = _make_cluster("cluster")
    conduit = _ConduitStub(
        "conduit-a",
        _SpellbookStub([]),
        conduit_state=ConduitState.lesser,
    )

    with pytest.raises(RuntimeError, match="normal conduit"):
        cluster.handle_join(conduit)


def test_handle_leave_removes_peer_owned_roots_from_leaver() -> None:
    """Verify handle_leave strips remaining peers' roots from the leaver."""
    spell_a = _SpellStub("spell-a", Existence.unique_per_conduit_cluster)
    spell_b = _SpellStub("spell-b", Existence.unique_per_conduit_cluster)
    conduit_a = _ConduitStub("conduit-a", _SpellbookStub([spell_a]))
    conduit_b = _ConduitStub("conduit-b", _SpellbookStub([spell_b]))
    frame = _FrameStub([conduit_a, conduit_b], frame_name="frame-x")
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)

    cluster.handle_join(conduit_a)
    cluster.handle_join(conduit_b)

    cluster.handle_leave(conduit_b)

    assert {
        "root_spell_id": cluster._cluster_root_id(conduit_a._id, spell_a.spell_id),
        "conduit": conduit_a,
        "aetheric_frame": "frame-x",
    } in (
        conduit_b.remove_root_calls
    )
    assert cluster.get_members() == {"conduit-a"}


def test_add_and_share_spell_uses_cluster_default_when_no_override() -> None:
    """Verify add_and_share_spell uses the cluster auto_link_dependencies setting."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    frame = _FrameStub([owner, borrower], frame_name="frame-1")
    cluster = _make_cluster(
        "cluster",
        frame._conduits,
        frame.frame_name,
        auto_link_dependencies=True,
    )
    cluster.add_member(owner._id)
    cluster.add_member(borrower._id)

    cluster.add_and_share_spell(owner, spell)

    assert borrower.contract_calls == [
        {
            "spell": spell,
            "conduit": owner,
            "permissions": spell.permissions,
            "aetheric_frame": "frame-1",
            "reason": DetailReason.root,
            "root_spell_id": cluster._cluster_root_id(owner._id, spell.spell_id),
            "link_dependencies": True,
        }
    ]


def test_add_and_share_spell_respects_override_false() -> None:
    """Verify add_and_share_spell does not contract when link_dependencies is False."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    frame = _FrameStub([owner, borrower], frame_name="frame-1")
    cluster = _make_cluster(
        "cluster",
        frame._conduits,
        frame.frame_name,
        auto_link_dependencies=True,
    )
    cluster.add_member(owner._id)
    cluster.add_member(borrower._id)

    cluster.add_and_share_spell(owner, spell, link_dependencies=False)

    assert borrower.contract_calls == []


def test_remove_and_strip_spell_removes_then_readds_root() -> None:
    """Verify remove_and_strip_spell removes roots and re-adds them with manual reason."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    frame = _FrameStub([owner, borrower], frame_name="frame-1")
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member(owner._id)
    cluster.add_member(borrower._id)
    cluster.add_shared_spell(owner._id, spell.spell_index)

    cluster.remove_and_strip_spell(owner, spell)

    assert borrower.remove_root_calls == [
        {
            "root_spell_id": cluster._cluster_root_id(owner._id, spell.spell_id),
            "conduit": owner,
            "aetheric_frame": "frame-1",
        }
    ]
    assert borrower.contract_calls == [
        {
            "spell": spell,
            "conduit": owner,
            "permissions": spell.permissions,
            "aetheric_frame": "frame-1",
            "reason": DetailReason.manual,
            "root_spell_id": spell.spell_id,
            "link_dependencies": False,
        }
    ]


def test_remove_and_strip_spell_skips_readd_when_remove_fails() -> None:
    """Verify remove_and_strip_spell skips re-adding when removal raises."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    cluster_root_id = _make_cluster("cluster")._cluster_root_id(owner._id, spell.spell_id)
    borrower = _ConduitStub(
        "borrower-1",
        _SpellbookStub([]),
        raise_on={"remove": {cluster_root_id}},
    )
    frame = _FrameStub([owner, borrower])
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member(owner._id)
    cluster.add_member(borrower._id)
    cluster.add_shared_spell(owner._id, spell.spell_index)

    cluster.remove_and_strip_spell(owner, spell)

    assert borrower.remove_root_calls == [
        {
            "root_spell_id": cluster_root_id,
            "conduit": owner,
            "aetheric_frame": "default",
        }
    ]
    assert borrower.contract_calls == []


def test_share_to_borrower_uses_non_deps_when_disabled() -> None:
    """Verify share_to_borrower calls non-dependency contracts when disabled."""
    cluster = _make_cluster(
        "cluster",
        aetheric_frame_name="frame-a",
        auto_link_dependencies=False,
    )
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]), aetheric_frame="frame-a")
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    cluster.add_shared_spell(owner._id, spell.spell_index)

    cluster.share_to_borrower(owner, borrower)

    assert borrower.contract_calls == [
        {
            "spell": spell,
            "conduit": owner,
            "permissions": spell.permissions,
            "aetheric_frame": "frame-a",
            "reason": DetailReason.root,
            "root_spell_id": cluster._cluster_root_id(owner._id, spell.spell_id),
            "link_dependencies": False,
        }
    ]


def test_share_to_borrower_rejects_non_normal_owner() -> None:
    """Verify borrower sharing rejects non-normal owners."""
    cluster = _make_cluster("cluster")
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub(
        "owner-1",
        _SpellbookStub([spell]),
        conduit_state=ConduitState.lesser,
    )
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    cluster.add_shared_spell(owner._id, spell.spell_index)

    with pytest.raises(RuntimeError, match="normal conduit"):
        cluster.share_to_borrower(owner, borrower)


def test_share_to_borrower_continues_after_exception() -> None:
    """Verify share_to_borrower continues when a contract call raises."""
    cluster = _make_cluster("cluster", auto_link_dependencies=True)
    spell_one = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    spell_two = _SpellStub("spell-2", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell_one, spell_two]))
    borrower = _ConduitStub(
        "borrower-1",
        _SpellbookStub([]),
        raise_on={"contract": {spell_one.spell_id}},
    )
    cluster.add_shared_spell(owner._id, spell_one.spell_index)
    cluster.add_shared_spell(owner._id, spell_two.spell_index)

    cluster.share_to_borrower(owner, borrower)

    assert {call["spell"].spell_id for call in borrower.contract_calls} == {
        spell_one.spell_id,
        spell_two.spell_id,
    }


def test_remove_shared_from_borrower_skips_missing_spell() -> None:
    """Verify remove_shared_from_borrower ignores unresolved SpellIndex entries."""
    cluster = _make_cluster("cluster")
    owner = _ConduitStub("owner-1", _SpellbookStub([]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    missing_index = SpellIndex("missing")
    cluster.add_shared_spell(owner._id, missing_index)

    cluster.remove_shared_from_borrower(owner, borrower, aetheric_frame="frame-x")

    assert borrower.remove_root_calls == []


def test_set_auto_link_dependencies_coerces_bool(cluster: ConduitCluster) -> None:
    """Verify set_auto_link_dependencies coerces inputs to booleans."""
    cluster.set_auto_link_dependencies(0)
    assert cluster.describe()["auto_link_dependencies"] is False

    cluster.set_auto_link_dependencies("yes")
    assert cluster.describe()["auto_link_dependencies"] is True


def test_describe_reports_members_and_shared_spells(cluster: ConduitCluster) -> None:
    """Verify describe returns a diagnostic snapshot of the cluster."""
    index = SpellIndex("spell-1")
    cluster.add_member("member-1")
    cluster.add_shared_spell("member-1", index)
    cluster.set_auto_link_dependencies(False)

    snapshot = cluster.describe()

    assert snapshot["name"] == "cluster"
    assert snapshot["auto_link_dependencies"] is False
    assert "member-1" in snapshot["members"]
    assert snapshot["shared_spells"]["member-1"] == [index.id]


def test_cleanup_clears_state_and_is_idempotent() -> None:
    """Verify cleanup clears state and is safe to call multiple times."""
    cluster = _make_cluster("cluster")
    cluster.add_member("member-1")
    cluster.add_shared_spell("member-1", SpellIndex("spell-1"))

    cluster.cleanup()
    cluster.cleanup()

    assert cluster.cleaned is True
    assert cluster.members == set()
    assert cluster.shared_spells == {}
    assert not hasattr(cluster, "auto_link_dependencies")


def test_cleanup_returns_early_when_cleaned_flips_inside_lock() -> None:
    """cleanup should return safely if another path marks the cluster cleaned inside the lock."""
    cluster = _make_cluster("cluster")
    cluster.members.add("member-1")
    cluster.shared_spells["owner-1"] = {SpellIndex("spell-1")}
    original_lock = cluster._lock

    class _LockThatMarksCleaned:
        def __enter__(self_inner):
            cluster._cleaned = True
            return self_inner

        def __exit__(self_inner, exc_type, exc_value, traceback):
            return False

    try:
        cluster._lock = _LockThatMarksCleaned()
        cluster.cleanup()
    finally:
        cluster._lock = original_lock

    assert cluster.members == {"member-1"}


def test_cleanup_tolerates_bucket_clear_errors() -> None:
    """cleanup should tolerate errors while clearing individual shared-spell buckets."""
    cluster = _make_cluster("cluster")
    broken_bucket = MagicMock()
    broken_bucket.clear.side_effect = RuntimeError("bucket boom")
    cluster.shared_spells["owner-1"] = broken_bucket

    cluster.cleanup()

    assert cluster.cleaned is True
    assert cluster.shared_spells == {}


def test_init_defaults_auto_link_dependencies_true() -> None:
    """Verify auto_link_dependencies defaults to True on construction."""
    cluster = _make_cluster("cluster")

    assert cluster.auto_link_dependencies is True


def test_add_member_idempotent(cluster: ConduitCluster) -> None:
    """Verify adding the same member twice does not create duplicates."""
    cluster.add_member("member-1")
    cluster.add_member("member-1")

    assert cluster.get_members() == {"member-1"}


def test_remove_member_noop_when_missing(cluster: ConduitCluster) -> None:
    """Verify remove_member is safe when the member is absent."""
    cluster.remove_member("missing")

    assert cluster.get_members() == set()


def test_add_shared_spell_idempotent(cluster: ConduitCluster) -> None:
    """Verify adding the same SpellIndex twice does not duplicate it."""
    index = SpellIndex("spell-1")

    cluster.add_shared_spell("owner-1", index)
    cluster.add_shared_spell("owner-1", index)

    assert cluster.get_shared_spells()["owner-1"] == {index}


def test_remove_shared_spell_keeps_bucket_when_not_empty(cluster: ConduitCluster) -> None:
    """Verify removing one spell keeps the owner bucket when others remain."""
    index_one = SpellIndex("spell-1")
    index_two = SpellIndex("spell-2")
    cluster.add_shared_spell("owner-1", index_one)
    cluster.add_shared_spell("owner-1", index_two)

    cluster.remove_shared_spell("owner-1", index_one)

    assert cluster.get_shared_spells()["owner-1"] == {index_two}


def test_get_shared_spells_snapshot_dict_independence(cluster: ConduitCluster) -> None:
    """Verify mutating the snapshot dict does not affect the live registry."""
    index = SpellIndex("spell-1")
    cluster.add_shared_spell("owner-1", index)

    snapshot = cluster.get_shared_spells()
    del snapshot["owner-1"]

    assert "owner-1" in cluster.get_shared_spells()


def test_get_shareable_spells_returns_only_cluster_spells() -> None:
    """Verify _get_shareable_spells filters to cluster-scoped spells."""
    cluster = _make_cluster("cluster")
    shareable_one = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    shareable_two = _SpellStub("spell-2", Existence.unique_per_conduit_cluster)
    not_shareable = _SpellStub("spell-3", Existence.unique)
    owner = _ConduitStub("owner-1", _SpellbookStub([shareable_one, shareable_two, not_shareable]))

    shareables = cluster._get_shareable_spells(owner)

    assert {spell.spell_id for spell in shareables} == {"spell-1", "spell-2"}


def test_get_shareable_spells_empty_when_spellbook_missing() -> None:
    """Verify _get_shareable_spells returns empty when spellbook is None."""
    cluster = _make_cluster("cluster")
    owner = _ConduitStub("owner-1", None)

    assert cluster._get_shareable_spells(owner) == []


def test_get_shareable_spells_empty_when_spells_none() -> None:
    """Verify _get_shareable_spells returns empty when _spells is None."""
    cluster = _make_cluster("cluster")
    owner = _ConduitStub("owner-1", _SpellbookNoSpellsStub())

    assert cluster._get_shareable_spells(owner) == []


def test_resolve_spell_from_index_none_when_spellbook_missing() -> None:
    """Verify _resolve_spell_from_index returns None when spellbook is None."""
    cluster = _make_cluster("cluster")
    owner = _ConduitStub("owner-1", None)

    assert cluster._resolve_spell_from_index(owner, SpellIndex("spell-1")) is None


def test_resolve_spell_from_index_none_when_spells_none() -> None:
    """Verify _resolve_spell_from_index returns None when _spells is None."""
    cluster = _make_cluster("cluster")
    owner = _ConduitStub("owner-1", _SpellbookNoSpellsStub())

    assert cluster._resolve_spell_from_index(owner, SpellIndex("spell-1")) is None


def test_resolve_spell_from_index_none_when_not_found() -> None:
    """Verify _resolve_spell_from_index returns None when the index is unknown."""
    cluster = _make_cluster("cluster")
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))

    assert cluster._resolve_spell_from_index(owner, SpellIndex("missing")) is None


def test_resolve_spell_from_index_returns_spell() -> None:
    """Verify _resolve_spell_from_index returns the spell when present."""
    cluster = _make_cluster("cluster")
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))

    assert cluster._resolve_spell_from_index(owner, spell.spell_index) is spell


def test_refresh_shareable_roots_adds_multiple_cluster_spells() -> None:
    """Verify refresh_shareable_roots captures multiple shareable roots."""
    cluster = _make_cluster("cluster")
    spell_one = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    spell_two = _SpellStub("spell-2", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell_one, spell_two]))

    cluster.refresh_shareable_roots(owner)

    assert cluster.get_shared_spells()[owner._id] == {spell_one.spell_index, spell_two.spell_index}


def test_refresh_shareable_roots_preserves_existing_entries() -> None:
    """Verify refresh_shareable_roots merges with existing shared roots."""
    cluster = _make_cluster("cluster")
    existing_index = SpellIndex("spell-1")
    cluster.add_shared_spell("owner-1", existing_index)
    new_spell = _SpellStub("spell-2", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([new_spell]))

    cluster.refresh_shareable_roots(owner)

    assert cluster.get_shared_spells()["owner-1"] == {existing_index, new_spell.spell_index}


def test_refresh_member_shares_shares_both_directions() -> None:
    """Verify refresh_member_shares shares roots both ways between peers."""
    spell_a = _SpellStub("spell-a", Existence.unique_per_conduit_cluster)
    spell_b = _SpellStub("spell-b", Existence.unique_per_conduit_cluster)
    conduit_a = _ConduitStub("conduit-a", _SpellbookStub([spell_a]), aetheric_frame="frame-a")
    conduit_b = _ConduitStub("conduit-b", _SpellbookStub([spell_b]), aetheric_frame="frame-b")
    frame = _FrameStub([conduit_a, conduit_b], frame_name="frame-x")
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member(conduit_a._id)
    cluster.add_member(conduit_b._id)
    cluster.refresh_shareable_roots(conduit_b)

    cluster.refresh_member_shares(conduit_a)

    assert {call["spell"].spell_id for call in conduit_b.contract_calls} == {"spell-a"}
    assert {call["spell"].spell_id for call in conduit_a.contract_calls} == {"spell-b"}


def test_refresh_member_shares_skips_missing_peer() -> None:
    """Verify refresh_member_shares ignores peers missing from the frame."""
    spell_a = _SpellStub("spell-a", Existence.unique_per_conduit_cluster)
    conduit_a = _ConduitStub("conduit-a", _SpellbookStub([spell_a]))
    frame = _FrameStub([conduit_a])
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member(conduit_a._id)
    cluster.add_member("missing-peer")

    cluster.refresh_member_shares(conduit_a)

    assert conduit_a.contract_calls == []
    assert cluster.get_shared_spells()[conduit_a._id] == {spell_a.spell_index}


def test_handle_join_skips_missing_peer_in_frame() -> None:
    """Verify handle_join ignores member ids that are absent from the frame."""
    spell_a = _SpellStub("spell-a", Existence.unique_per_conduit_cluster)
    conduit_a = _ConduitStub("conduit-a", _SpellbookStub([spell_a]))
    frame = _FrameStub([conduit_a])
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member("missing-peer")

    cluster.handle_join(conduit_a)

    assert conduit_a.contract_calls == []
    assert cluster.get_members() == {"missing-peer", "conduit-a"}


def test_handle_join_refreshes_shareable_roots_for_existing_members() -> None:
    """Verify handle_join refreshes shareable roots for all members."""
    spell_a = _SpellStub("spell-a", Existence.unique_per_conduit_cluster)
    spell_b = _SpellStub("spell-b", Existence.unique_per_conduit_cluster)
    conduit_a = _ConduitStub("conduit-a", _SpellbookStub([spell_a]))
    conduit_b = _ConduitStub("conduit-b", _SpellbookStub([spell_b]))
    frame = _FrameStub([conduit_a, conduit_b], frame_name="frame-x")
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)

    cluster.handle_join(conduit_a)
    cluster.handle_join(conduit_b)

    shared = cluster.get_shared_spells()
    assert shared[conduit_a._id] == {spell_a.spell_index}
    assert shared[conduit_b._id] == {spell_b.spell_index}


def test_handle_leave_removes_leaver_from_shared_spells() -> None:
    """Verify handle_leave drops the leaver's shared roots from registry."""
    spell_a = _SpellStub("spell-a", Existence.unique_per_conduit_cluster)
    spell_b = _SpellStub("spell-b", Existence.unique_per_conduit_cluster)
    conduit_a = _ConduitStub("conduit-a", _SpellbookStub([spell_a]))
    conduit_b = _ConduitStub("conduit-b", _SpellbookStub([spell_b]))
    frame = _FrameStub([conduit_a, conduit_b], frame_name="frame-x")
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)

    cluster.handle_join(conduit_a)
    cluster.handle_join(conduit_b)
    cluster.handle_leave(conduit_b)

    assert conduit_b._id not in cluster.get_shared_spells()


def test_handle_leave_removes_leaver_owned_roots_from_peers() -> None:
    """Verify handle_leave strips the leaver's roots from remaining peers."""
    spell_a = _SpellStub("spell-a", Existence.unique_per_conduit_cluster)
    spell_b = _SpellStub("spell-b", Existence.unique_per_conduit_cluster)
    conduit_a = _ConduitStub("conduit-a", _SpellbookStub([spell_a]))
    conduit_b = _ConduitStub("conduit-b", _SpellbookStub([spell_b]))
    frame = _FrameStub([conduit_a, conduit_b], frame_name="frame-x")
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)

    cluster.handle_join(conduit_a)
    cluster.handle_join(conduit_b)
    cluster.handle_leave(conduit_a)

    assert {
        "root_spell_id": cluster._cluster_root_id(conduit_a._id, spell_a.spell_id),
        "conduit": conduit_a,
        "aetheric_frame": "frame-x",
    } in conduit_b.remove_root_calls


def test_handle_leave_skips_missing_peer() -> None:
    """Verify handle_leave ignores peers that are missing from the frame."""
    spell_a = _SpellStub("spell-a", Existence.unique_per_conduit_cluster)
    conduit_a = _ConduitStub("conduit-a", _SpellbookStub([spell_a]))
    frame = _FrameStub([conduit_a])
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member(conduit_a._id)
    cluster.add_member("missing-peer")

    cluster.handle_leave(conduit_a)

    assert cluster.get_members() == {"missing-peer"}


def test_add_and_share_spell_override_true_when_cluster_auto_false() -> None:
    """Verify add_and_share_spell obeys an explicit True override."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    frame = _FrameStub([owner, borrower], frame_name="frame-1")
    cluster = _make_cluster(
        "cluster",
        frame._conduits,
        frame.frame_name,
        auto_link_dependencies=False,
    )
    cluster.add_member(owner._id)
    cluster.add_member(borrower._id)

    cluster.add_and_share_spell(owner, spell, link_dependencies=True)

    assert borrower.contract_calls == [
        {
            "spell": spell,
            "conduit": owner,
            "permissions": spell.permissions,
            "aetheric_frame": "frame-1",
            "reason": DetailReason.root,
            "root_spell_id": cluster._cluster_root_id(owner._id, spell.spell_id),
            "link_dependencies": True,
        }
    ]


def test_add_and_share_spell_adds_shared_spell_without_peers() -> None:
    """Verify add_and_share_spell stores the root even when no peers exist."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    frame = _FrameStub([owner])
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member(owner._id)

    cluster.add_and_share_spell(owner, spell)

    assert cluster.get_shared_spells()[owner._id] == {spell.spell_index}


def test_add_and_share_spell_skips_missing_peer_entries() -> None:
    """Verify add_and_share_spell ignores member ids that are absent from the frame."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    frame = _FrameStub([owner])
    cluster = _make_cluster(
        "cluster",
        frame._conduits,
        frame.frame_name,
        auto_link_dependencies=True,
    )
    cluster.add_member(owner._id)
    cluster.add_member("missing-peer")

    cluster.add_and_share_spell(owner, spell)

    assert cluster.get_shared_spells()[owner._id] == {spell.spell_index}


def test_add_and_share_spell_uses_distinct_cluster_root_ids_per_owner() -> None:
    """Verify cluster root ids differ when two owners share the same spell id."""
    spell_id = "spell-shared"
    spell_a = _SpellStub(spell_id, Existence.unique_per_conduit_cluster)
    spell_b = _SpellStub(spell_id, Existence.unique_per_conduit_cluster)
    owner_a = _ConduitStub("owner-a", _SpellbookStub([spell_a]))
    owner_b = _ConduitStub("owner-b", _SpellbookStub([spell_b]))
    borrower = _ConduitStub("borrower", _SpellbookStub([]))
    frame = _FrameStub([owner_a, owner_b, borrower])
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member(owner_a._id)
    cluster.add_member(owner_b._id)
    cluster.add_member(borrower._id)

    cluster.add_and_share_spell(owner_a, spell_a)
    cluster.add_and_share_spell(owner_b, spell_b)

    root_ids = {call["root_spell_id"] for call in borrower.contract_calls}
    assert root_ids == {
        cluster._cluster_root_id(owner_a._id, spell_id),
        cluster._cluster_root_id(owner_b._id, spell_id),
    }


def test_add_and_share_spell_continues_after_exception_for_peer() -> None:
    """Verify add_and_share_spell continues when one peer contract fails."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    borrower_bad = _ConduitStub(
        "borrower-bad",
        _SpellbookStub([]),
        raise_on={"contract": {spell.spell_id}},
    )
    borrower_ok = _ConduitStub("borrower-ok", _SpellbookStub([]))
    frame = _FrameStub([owner, borrower_bad, borrower_ok])
    cluster = _make_cluster(
        "cluster",
        frame._conduits,
        frame.frame_name,
        auto_link_dependencies=True,
    )
    cluster.add_member(owner._id)
    cluster.add_member(borrower_bad._id)
    cluster.add_member(borrower_ok._id)

    cluster.add_and_share_spell(owner, spell)

    assert borrower_bad.contract_calls
    assert borrower_ok.contract_calls


def test_add_and_share_spell_uses_default_permissions_when_missing() -> None:
    """Verify add_and_share_spell defaults permissions when missing on the spell."""
    spell = _SpellNoPermissionsStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    frame = _FrameStub([owner, borrower], frame_name="frame-1")
    cluster = _make_cluster(
        "cluster",
        frame._conduits,
        frame.frame_name,
        auto_link_dependencies=True,
    )
    cluster.add_member(owner._id)
    cluster.add_member(borrower._id)

    cluster.add_and_share_spell(owner, spell)

    assert borrower.contract_calls[0]["permissions"] == "create"


def test_remove_and_strip_spell_skips_readd_when_add_contract_fails() -> None:
    """Verify remove_and_strip_spell swallows add failures after removal."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    borrower = _ConduitStub(
        "borrower-1",
        _SpellbookStub([]),
        raise_on={"contract": {spell.spell_id}},
    )
    frame = _FrameStub([owner, borrower], frame_name="frame-1")
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member(owner._id)
    cluster.add_member(borrower._id)

    cluster.remove_and_strip_spell(owner, spell)

    assert borrower.remove_root_calls == [
        {
            "root_spell_id": cluster._cluster_root_id(owner._id, spell.spell_id),
            "conduit": owner,
            "aetheric_frame": "frame-1",
        }
    ]
    assert len(borrower.contract_calls) == 1


def test_remove_and_strip_spell_skips_missing_peer_entries() -> None:
    """Verify remove_and_strip_spell ignores member ids that are absent from the frame."""
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    frame = _FrameStub([owner])
    cluster = _make_cluster("cluster", frame._conduits, frame.frame_name)
    cluster.add_member(owner._id)
    cluster.add_member("missing-peer")
    cluster.add_shared_spell(owner._id, spell.spell_index)

    cluster.remove_and_strip_spell(owner, spell)

    assert cluster.get_shared_spells() == {}


def test_share_to_borrower_no_shared_indices_no_calls() -> None:
    """Verify share_to_borrower does nothing when no shared roots exist."""
    cluster = _make_cluster("cluster")
    owner = _ConduitStub("owner-1", _SpellbookStub([]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))

    cluster.share_to_borrower(owner, borrower)

    assert borrower.contract_calls == []


def test_share_to_borrower_skips_unresolvable_index() -> None:
    """Verify share_to_borrower skips roots that cannot be resolved to spells."""
    cluster = _make_cluster("cluster")
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    cluster.add_shared_spell(owner._id, SpellIndex("missing"))

    cluster.share_to_borrower(owner, borrower)

    assert borrower.contract_calls == []


def test_share_to_borrower_uses_default_frame_when_owner_missing_attr() -> None:
    """Verify share_to_borrower defaults aetheric_frame when owner lacks metadata."""
    cluster = _make_cluster("cluster")
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitNoFrameStub("owner-1", _SpellbookStub([spell]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    cluster.add_shared_spell(owner._id, spell.spell_index)

    cluster.share_to_borrower(owner, borrower)

    assert borrower.contract_calls[0]["aetheric_frame"] == "default"


def test_remove_shared_from_borrower_continues_after_exception() -> None:
    """Verify remove_shared_from_borrower continues after a removal error."""
    cluster = _make_cluster("cluster")
    spell_one = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    spell_two = _SpellStub("spell-2", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell_one, spell_two]))
    borrower = _ConduitStub(
        "borrower-1",
        _SpellbookStub([]),
        raise_on={"remove": {spell_one.spell_id}},
    )
    cluster.add_shared_spell(owner._id, spell_one.spell_index)
    cluster.add_shared_spell(owner._id, spell_two.spell_index)

    cluster.remove_shared_from_borrower(owner, borrower)

    assert {call["root_spell_id"] for call in borrower.remove_root_calls} == {
        cluster._cluster_root_id(owner._id, spell_one.spell_id),
        cluster._cluster_root_id(owner._id, spell_two.spell_id),
    }


def test_remove_shared_from_borrower_uses_normal_borrower() -> None:
    """Verify remove_shared_from_borrower operates on a normal borrower conduit."""
    cluster = _make_cluster("cluster")
    spell = _SpellStub("spell-1", Existence.unique_per_conduit_cluster)
    owner = _ConduitStub("owner-1", _SpellbookStub([spell]))
    borrower = _ConduitStub("borrower-1", _SpellbookStub([]))
    cluster.add_shared_spell(owner._id, spell.spell_index)

    cluster.remove_shared_from_borrower(owner, borrower)

    assert borrower.remove_root_calls == [
        {
            "root_spell_id": cluster._cluster_root_id(owner._id, spell.spell_id),
            "conduit": owner,
            "aetheric_frame": "default",
        }
    ]


# ----------------------------------------------------------------------
# Team-store facade: single-member bind / unbind (bind_member, unbind_member)
# ----------------------------------------------------------------------
class _FacadeConduit:
    """Minimal root conduit exposing the team-store facade and its own store."""

    def __init__(self, conduit_id: str) -> None:
        """Initialize with an id, an opaque creation store, and an inert facade."""
        self._id = conduit_id
        # Opaque per-conduit creation store; its identity is all the facade needs.
        self._creations = object()
        self._cluster_creations = ClusterCreations()


def _make_facade_cluster(*conduits: _FacadeConduit) -> ConduitCluster:
    """Build a cluster whose registry resolves the given facade conduits by id."""
    registry: Dict[str, Any] = {conduit._id: conduit for conduit in conduits}
    return _make_cluster("facade-cluster", registry=registry)


def test_bind_member_binds_joiner_facade_to_leader_store() -> None:
    """bind_member activates a joiner's facade and points it at the leader store."""
    leader = _FacadeConduit("leader")
    joiner = _FacadeConduit("joiner")
    cluster = _make_facade_cluster(leader, joiner)
    cluster.master_conduit_id = leader._id

    cluster.bind_member(joiner)

    assert joiner._cluster_creations.is_active() is True
    assert joiner._cluster_creations.resolved_store() is leader._creations


def test_bind_member_is_noop_when_cluster_inert() -> None:
    """bind_member leaves the joiner inert when no leader is elected."""
    leader = _FacadeConduit("leader")
    joiner = _FacadeConduit("joiner")
    cluster = _make_facade_cluster(leader, joiner)

    cluster.bind_member(joiner)

    assert joiner._cluster_creations.is_active() is False


def test_bind_member_leaves_master_unchanged() -> None:
    """bind_member does not alter master_conduit_id (the leader is unchanged)."""
    leader = _FacadeConduit("leader")
    joiner = _FacadeConduit("joiner")
    cluster = _make_facade_cluster(leader, joiner)
    cluster.master_conduit_id = leader._id

    cluster.bind_member(joiner)

    assert cluster.master_conduit_id == leader._id


def test_bind_member_binds_to_the_current_leader_store() -> None:
    """bind_member resolves master_conduit_id, binding to the current leader."""
    leader_a = _FacadeConduit("leader-a")
    leader_b = _FacadeConduit("leader-b")
    joiner = _FacadeConduit("joiner")
    cluster = _make_facade_cluster(leader_a, leader_b, joiner)
    cluster.master_conduit_id = leader_b._id

    cluster.bind_member(joiner)

    assert joiner._cluster_creations.resolved_store() is leader_b._creations
    assert joiner._cluster_creations.resolved_store() is not leader_a._creations


def test_bind_member_raises_after_cleanup() -> None:
    """bind_member is guarded by check_cleaned after the cluster is cleaned."""
    leader = _FacadeConduit("leader")
    joiner = _FacadeConduit("joiner")
    cluster = _make_facade_cluster(leader, joiner)
    cluster.master_conduit_id = leader._id
    cluster.cleanup()

    with pytest.raises(RuntimeError):
        cluster.bind_member(joiner)


def test_unbind_member_deactivates_bound_leaver_facade() -> None:
    """unbind_member disables a bound leaver's facade so resolve hard-errors."""
    leader = _FacadeConduit("leader")
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leader, leaver)
    cluster.master_conduit_id = leader._id
    leaver._cluster_creations.bind(leader._creations)

    cluster.unbind_member(leaver)

    assert leaver._cluster_creations.is_active() is False
    with pytest.raises(RuntimeError):
        leaver._cluster_creations.resolved_store()


def test_unbind_member_does_not_touch_master_or_other_members() -> None:
    """A non-leader unbind leaves master and the other members' facades intact."""
    leader = _FacadeConduit("leader")
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leader, leaver)
    cluster.master_conduit_id = leader._id
    leader._cluster_creations.bind(leader._creations)
    leaver._cluster_creations.bind(leader._creations)

    cluster.unbind_member(leaver)

    assert cluster.master_conduit_id == leader._id
    assert leader._cluster_creations.is_active() is True


def test_unbind_member_is_unconditional_when_master_cleared() -> None:
    """unbind_member drops a still-bound facade even after the cluster dissolved.

    Mirrors the leader-leave path: `unelect_leader` already cleared
    master_conduit_id and the cloud removed the leader from `members`, so the
    departed leader's own facade must still be dropped unconditionally.
    """
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)
    leaver._cluster_creations.bind(leaver._creations)
    cluster.master_conduit_id = None

    cluster.unbind_member(leaver)

    assert leaver._cluster_creations.is_active() is False


def test_unbind_member_is_idempotent_on_inert_facade() -> None:
    """unbind_member is a no-op (no raise) when the leaver's facade is inert."""
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)

    cluster.unbind_member(leaver)

    assert leaver._cluster_creations.is_active() is False


def test_unbind_member_raises_after_cleanup() -> None:
    """unbind_member is guarded by check_cleaned after the cluster is cleaned."""
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)
    cluster.cleanup()

    with pytest.raises(RuntimeError):
        cluster.unbind_member(leaver)

