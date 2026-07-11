"""
Unit contract tests for ContractCrystal: the record's relationship map
(dispatch, replace-on-emit, eviction + tombstone capture, conduit-edge
sweep net).
"""
import pytest

from melder.crystallizer.crystals.conduit_crystal import ConduitCrystal
from melder.crystallizer.crystals.contract_crystal import (
    ContractCrystal,
)
from melder.crystallizer.persistence.persistence_profile import PersistenceProfile


def _contract(contract_id="ct-1", a="conduit-a", b="conduit-b", details_a=None):
    """Build one relationship twin."""
    return ContractCrystal(
        contract_id=contract_id,
        conduit_a_id=a,
        conduit_b_id=b,
        details_a=list(details_a or []),
        details_b=[],
        index_details_a=[],
        index_details_b=[],
    )


def test_dispatch_describe_and_detachment():
    """
    Purpose:
        Verify record() routes contract twins and describe() detaches.
    Contract:
        The twin lands in its level map (contract_count), journals kind
        "contract", and mutating a described detail list never touches
        the twin.
    Returns:
        None.
    Raises:
        AssertionError: If dispatch or detachment drifts.
    """
    profile = PersistenceProfile("p")
    detail = {"spell_id": "sha-a", "permissions": "create"}
    twin = _contract(details_a=[detail])
    profile.record(twin)
    assert profile.describe()["contract_count"] == 1
    described = twin.describe()
    described["details_a"][0]["permissions"] = "block"
    described["details_a"].append({"spell_id": "sha-x"})
    fresh = twin.describe()
    assert fresh["details_a"] == [{"spell_id": "sha-a", "permissions": "create"}]
    assert fresh["conduit_a_id"] == "conduit-a"
    _payloads, entries, _rng = profile.capture_segment_since(0)
    assert entries == [(1, "contract", "ct-1")]


def test_replace_on_emit_keeps_one_snapshot_per_contract():
    """
    Purpose:
        Verify relationship snapshots replace by contract_id.
    Contract:
        A re-emitted contract displaces + cleans the previous snapshot;
        the capture window reports the CURRENT detail view.
    Returns:
        None.
    Raises:
        AssertionError: If stale snapshots survive.
    """
    profile = PersistenceProfile("p")
    first = _contract()
    profile.record(first)
    profile.record(_contract(details_a=[{"spell_id": "sha-a"}]))
    assert first.cleaned is True
    assert profile.describe()["contract_count"] == 1
    payloads, _entries, _rng = profile.capture_segment_since(0)
    assert payloads["contract"]["ct-1"]["details_a"] == [{"spell_id": "sha-a"}]


def test_removal_evicts_and_captures_tombstone():
    """
    Purpose:
        Verify contract severance leaves the record truthfully.
    Contract:
        remove_contract_crystal cleans + evicts the twin, tolerates an
        unrecorded contract, and captures the {"contract_id", "removed"}
        tombstone.
    Returns:
        None.
    Raises:
        AssertionError: If eviction or capture drifts.
    """
    profile = PersistenceProfile("p")
    twin = _contract()
    profile.record(twin)
    profile.remove_contract_crystal("ct-1")
    assert twin.cleaned is True
    assert profile.describe()["contract_count"] == 0
    profile.remove_contract_crystal("ghost-ct")
    payloads, _entries, _rng = profile.capture_segment_since(0)
    assert payloads["contract_removed"]["ct-1"] == {
        "contract_id": "ct-1", "removed": True,
    }
    assert payloads["contract_removed"]["ghost-ct"] == {
        "contract_id": "ghost-ct", "removed": True,
    }


def test_subtree_sweep_takes_contracts_touching_swept_conduits():
    """
    Purpose:
        Verify the defense net: no relationship outlives its endpoints.
    Contract:
        remove_spellbook_subtree evicts contracts where EITHER endpoint
        is a swept conduit; an unrelated contract survives.
    Returns:
        None.
    Raises:
        AssertionError: If the net misses or over-reaches.
    """
    profile = PersistenceProfile("p")
    profile.record(
        ConduitCrystal(
            conduit_id="conduit-a", spellbook_id="book-1",
            conduit_name="root", policy_name="p", dynamic=True,
        )
    )
    doomed_as_a = _contract(contract_id="ct-1", a="conduit-a", b="conduit-x")
    doomed_as_b = _contract(contract_id="ct-2", a="conduit-y", b="conduit-a")
    survivor = _contract(contract_id="ct-3", a="conduit-y", b="conduit-x")
    profile.record(doomed_as_a)
    profile.record(doomed_as_b)
    profile.record(survivor)
    profile.remove_spellbook_subtree("book-1")
    assert doomed_as_a.cleaned is True
    assert doomed_as_b.cleaned is True
    assert survivor.cleaned is False
    assert profile.describe()["contract_count"] == 1
