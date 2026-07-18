"""Regression: BUG-005 (2026-07-17 audit) - failed sever leaves no asymmetric state.

Symptom:
    `ConduitWard._remove_contract` used to sever side A's spellbook bucket,
    then side B's; when B's sever raised, the public ``a.sever_link(b)``
    raised too - yet both wards still reported the contract while A's bucket
    was gone and B's remained (asymmetric split-brain).

Contract under test (two-phase sever):
    Phase 1 detaches both bucket surfaces REVERSIBLY; a failure on the second
    detach restores the first side exactly, so a raised sever leaves the
    contract fully intact on both sides - bucket content included. After both
    detaches succeed the removal commits with non-fallible pops, and the
    destructive per-spell teardown of the detached payloads runs last as a
    loud best-effort step that can no longer split topology truth.
"""

import threading
from types import SimpleNamespace
from typing import Dict, List, Optional, Set, Tuple

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity


class FakeLogger:
    """Minimal logger absorbing the ward's keyword-heavy logging calls."""

    def __init__(self) -> None:
        """Initialize storage for recorded messages."""
        self.messages: List[Tuple[str, str]] = []

    def debug(self, message: str, method_name: Optional[str] = None, **kwargs: object) -> None:
        """Record a debug message."""
        self.messages.append(("debug", message))

    def info(self, message: str, method_name: Optional[str] = None, **kwargs: object) -> None:
        """Record an info message."""
        self.messages.append(("info", message))

    def warning(self, message: str, method_name: Optional[str] = None, **kwargs: object) -> None:
        """Record a warning message."""
        self.messages.append(("warning", message))

    def error(self, message: str, method_name: Optional[str] = None, **kwargs: object) -> None:
        """Record an error message."""
        self.messages.append(("error", message))


class FakeSpellIndex:
    """Hashable spell-index stand-in reporting one selected id.

    Contract:
        - Instances are used as `_contracted_spells` bucket KEYS, so they
          must be hashable. `types.SimpleNamespace` defines `__eq__` and
          therefore has `__hash__ = None`; a plain class keeps default
          identity hashing, matching how real `SpellIndex` objects key
          these maps.
    """

    def __init__(self, spell_id: str) -> None:
        """Record the one selected version id the destroy seam reads."""
        self.selected_spell_id = spell_id


class FakeSpell:
    """Value-light stand-in carrying only what the sever seams read."""

    def __init__(self, spell_id: str) -> None:
        """Create a fake spell whose index reports one selected id."""
        self.spell_id = spell_id
        self.spell_index = FakeSpellIndex(spell_id)


class FakeSpellbook:
    """Bucket fake mirroring the real five-map surface and two-phase seams.

    Contract:
        - `_create_link_contract` / `_remove_link_contract` /
          `_detach_link_contract` / `_reattach_link_contract` /
          `_destroy_detached_link_contract` mirror the real lockstep,
          reversibility, and destroy semantics.
        - `fail_detach_for` / `fail_destroy_for` inject targeted failures so
          tests choose exactly which phase and which peer breaks.
    """

    def __init__(self) -> None:
        """Initialize the five maps, the id pool, and the failure injectors."""
        self._lock = threading.RLock()
        self._contracted_spells: Dict[str, Dict[object, FakeSpell]] = {}
        self._lookup_contracted_spells: Dict[str, Dict[Tuple[str, str], object]] = {}
        self._contracted_spell_ids: Dict[str, Set[str]] = {}
        self._contracted_spells_by_id: Dict[str, Dict[str, FakeSpell]] = {}
        self._inactive_contracted_spells: Dict[str, Dict[str, FakeSpell]] = {}
        self._spell_id_pool: Dict[str, FakeSpell] = {}
        self.fail_detach_for: Optional[str] = None
        self.fail_destroy_for: Optional[str] = None
        self.destroyed_peers: List[str] = []

    def _create_link_contract(self, conduit_id: str) -> None:
        """Create the four-bucket structure for one peer in lockstep."""
        with self._lock:
            if conduit_id not in self._contracted_spells:
                self._contracted_spells[conduit_id] = {}
                self._lookup_contracted_spells[conduit_id] = {}
                self._contracted_spell_ids[conduit_id] = set()
                self._contracted_spells_by_id[conduit_id] = {}

    def _remove_link_contract(self, conduit_id: str) -> None:
        """Remove the bucket structure for one peer in lockstep."""
        with self._lock:
            self._contracted_spells.pop(conduit_id, None)
            self._lookup_contracted_spells.pop(conduit_id, None)
            self._contracted_spell_ids.pop(conduit_id, None)
            self._contracted_spells_by_id.pop(conduit_id, None)
            self._inactive_contracted_spells.pop(conduit_id, None)

    def seed_contracted_spell(self, spell: FakeSpell, conduit_id: str) -> None:
        """Seed one borrowed spell under a peer bucket plus the id pool."""
        with self._lock:
            self._create_link_contract(conduit_id)
            self._contracted_spells[conduit_id][spell.spell_index] = spell
            self._contracted_spell_ids[conduit_id].add(spell.spell_id)
            self._contracted_spells_by_id[conduit_id][spell.spell_id] = spell
            self._spell_id_pool[spell.spell_id] = spell

    def _detach_link_contract(
        self, conduit_id: str
    ) -> Optional[Tuple[
        Dict[object, FakeSpell],
        Dict[Tuple[str, str], object],
        Set[str],
        Dict[str, FakeSpell],
        Optional[Dict[str, FakeSpell]],
    ]]:
        """Reversibly pop the peer's bucket surface, or fail on command."""
        if self.fail_detach_for == conduit_id:
            raise RuntimeError(
                f"injected: detach refused for peer {conduit_id}"
            )
        with self._lock:
            if conduit_id not in self._contracted_spells:
                return None
            return (
                self._contracted_spells.pop(conduit_id),
                self._lookup_contracted_spells.pop(conduit_id),
                self._contracted_spell_ids.pop(conduit_id),
                self._contracted_spells_by_id.pop(conduit_id),
                self._inactive_contracted_spells.pop(conduit_id, None),
            )

    def _reattach_link_contract(
        self,
        conduit_id: str,
        payload: Tuple[
            Dict[object, FakeSpell],
            Dict[Tuple[str, str], object],
            Set[str],
            Dict[str, FakeSpell],
            Optional[Dict[str, FakeSpell]],
        ],
    ) -> None:
        """Restore a detached payload exactly; refuse to overwrite."""
        with self._lock:
            if conduit_id in self._contracted_spells:
                raise RuntimeError(
                    f"Cannot reattach link contract for {conduit_id}."
                )
            active, lookup, spell_ids, by_id, inactive = payload
            self._contracted_spells[conduit_id] = active
            self._lookup_contracted_spells[conduit_id] = lookup
            self._contracted_spell_ids[conduit_id] = spell_ids
            self._contracted_spells_by_id[conduit_id] = by_id
            if inactive is not None:
                self._inactive_contracted_spells[conduit_id] = inactive

    def _destroy_detached_link_contract(
        self,
        conduit_id: str,
        payload: Tuple[
            Dict[object, FakeSpell],
            Dict[Tuple[str, str], object],
            Set[str],
            Dict[str, FakeSpell],
            Optional[Dict[str, FakeSpell]],
        ],
    ) -> None:
        """Pop detached spells from the id pool, or fail on command."""
        if self.fail_destroy_for == conduit_id:
            raise RuntimeError(
                f"injected: destroy refused for peer {conduit_id}"
            )
        active_map = payload[0]
        with self._lock:
            for spell in active_map.values():
                self._spell_id_pool.pop(spell.spell_index.selected_spell_id, None)
        self.destroyed_peers.append(conduit_id)

    def has_bucket_for(self, conduit_id: str) -> bool:
        """Return whether any map holds a bucket for the peer."""
        return (
            conduit_id in self._contracted_spells
            or conduit_id in self._lookup_contracted_spells
            or conduit_id in self._contracted_spell_ids
            or conduit_id in self._contracted_spells_by_id
            or conduit_id in self._inactive_contracted_spells
        )


class FakeConduit:
    """Minimal conduit host carrying one real `ConduitWard` for sever tests."""

    def __init__(self, conduit_id: str, *, dynamic: bool = True) -> None:
        """Create one conduit shell with a real ward and fake spellbook."""
        self._lock = threading.RLock()
        self._id = conduit_id
        self._crystallizer = SimpleNamespace(cleaned=False, activated=False)
        self._name: Optional[str] = None
        self.__debugger_mode__ = False
        self.__dynamic_environment__ = dynamic
        self._aetheric_frame_name = "default"
        self._configuration = None
        self._logger = FakeLogger()
        self._spellbook = FakeSpellbook()
        self._devops_information_registry = DevopsInformationRegistry("default")
        self._ward_frame = SimpleNamespace(
            _conduit_cloud=SimpleNamespace(
                get_conduit_by_id=lambda conduit_id: None,
            ),
            devops_information_registry=self._devops_information_registry,
        )
        self._conduit_state = ConduitState.normal
        self._creations = None
        self._meld = None
        self._cleaned = False
        self._transaction_identity = DevopsIdentity(
            owner_kind="conduit",
            owner_id=self._id,
            aetheric_frame_name=self._aetheric_frame_name,
            metadata={},
            available_transactions=("link", "transfer_ownership"),
        )
        self._transaction_identity.attach_registry(
            self._devops_information_registry,
            object_ref=self,
        )
        self._conduit_ward = ConduitWard(
            self,
            dynamic,
            self._conduit_state,
            Policies.default,
            self._ward_frame,
        )

    def _emit_conduit_twin(self) -> None:
        """No-op record emitter (the stub crystallizer never records)."""
        return None

    @property
    def cleaned(self) -> bool:
        """Return True when this conduit shell has been cleaned."""
        return self._cleaned

    def check_cleaned(self) -> None:
        """Raise when the conduit shell has been cleaned."""
        if self._cleaned:
            raise RuntimeError("Conduit is cleaned.")

    def cleanup(self) -> None:
        """Tear down the ward, identity, and registry owned by this shell."""
        if self._cleaned:
            return
        self._cleaned = True
        try:
            self._conduit_ward.cleanup()
        except Exception:
            pass
        try:
            self._transaction_identity.cleanup()
        except Exception:
            pass
        try:
            self._devops_information_registry.cleanup()
        except Exception:
            pass


@pytest.fixture()
def severable_pair() -> "tuple[FakeConduit, FakeConduit]":
    """Yield two LINKED conduit shells with seeded borrowed spells."""
    conduit_a = FakeConduit("conduit-a")
    conduit_b = FakeConduit("conduit-b")
    assert conduit_a._conduit_ward._link(conduit_b) is True
    conduit_a._spellbook.seed_contracted_spell(
        FakeSpell("spell-borrowed-by-a"), conduit_b._id,
    )
    conduit_b._spellbook.seed_contracted_spell(
        FakeSpell("spell-borrowed-by-b"), conduit_a._id,
    )
    yield conduit_a, conduit_b
    conduit_a.cleanup()
    conduit_b.cleanup()


def test_failed_second_detach_restores_first_side_exactly(
    severable_pair: "tuple[FakeConduit, FakeConduit]",
) -> None:
    """The audited trigger: side B fails after side A was already severed.

    Contract assertions:
        - The public sever raises the injected error.
        - The contract still exists symmetrically on BOTH wards.
        - Side A's bucket is restored WITH its borrowed-spell content
          (the old code left it destroyed).
        - After disarming, the same sever succeeds and zero state remains.
    """
    conduit_a, conduit_b = severable_pair
    conduit_b._spellbook.fail_detach_for = conduit_a._id

    with pytest.raises(RuntimeError, match="injected"):
        conduit_a._conduit_ward._sever_link(conduit_b)

    ward_a = conduit_a._conduit_ward
    ward_b = conduit_b._conduit_ward
    assert ward_a._find_contract(conduit_b) is not None
    assert ward_b._find_contract(conduit_a) is not None
    assert conduit_a._spellbook.has_bucket_for(conduit_b._id), (
        "side A's bucket must be restored after the failed sever"
    )
    assert "spell-borrowed-by-a" in conduit_a._spellbook._contracted_spells_by_id[
        conduit_b._id
    ], "restored bucket must keep its borrowed-spell content"
    assert conduit_b._spellbook.has_bucket_for(conduit_a._id)

    conduit_b._spellbook.fail_detach_for = None
    assert ward_a._sever_link(conduit_b) is True
    assert ward_a._find_contract(conduit_b) is None
    assert ward_b._find_contract(conduit_a) is None
    assert not conduit_a._spellbook.has_bucket_for(conduit_b._id)
    assert not conduit_b._spellbook.has_bucket_for(conduit_a._id)


def test_successful_sever_destroys_both_detached_sides(
    severable_pair: "tuple[FakeConduit, FakeConduit]",
) -> None:
    """A clean sever removes buckets AND runs both destroy passes.

    Contract assertions:
        - Contract gone symmetrically; buckets gone on both books.
        - Both sides' pool ids were released by the destroy phase.
    """
    conduit_a, conduit_b = severable_pair
    assert conduit_a._conduit_ward._sever_link(conduit_b) is True

    assert conduit_a._conduit_ward._find_contract(conduit_b) is None
    assert conduit_b._conduit_ward._find_contract(conduit_a) is None
    assert not conduit_a._spellbook.has_bucket_for(conduit_b._id)
    assert not conduit_b._spellbook.has_bucket_for(conduit_a._id)
    assert "spell-borrowed-by-a" not in conduit_a._spellbook._spell_id_pool
    assert "spell-borrowed-by-b" not in conduit_b._spellbook._spell_id_pool
    assert conduit_a._spellbook.destroyed_peers == [conduit_b._id]
    assert conduit_b._spellbook.destroyed_peers == [conduit_a._id]


def test_destroy_failure_does_not_resurrect_topology(
    severable_pair: "tuple[FakeConduit, FakeConduit]",
) -> None:
    """A destroy-phase failure is best-effort: the sever still commits.

    Contract assertions:
        - The public sever returns True despite the injected destroy failure.
        - The contract is gone symmetrically and no bucket survives.
        - The failure was logged, not raised.
    """
    conduit_a, conduit_b = severable_pair
    conduit_b._spellbook.fail_destroy_for = conduit_a._id

    assert conduit_a._conduit_ward._sever_link(conduit_b) is True

    assert conduit_a._conduit_ward._find_contract(conduit_b) is None
    assert conduit_b._conduit_ward._find_contract(conduit_a) is None
    assert not conduit_a._spellbook.has_bucket_for(conduit_b._id)
    assert not conduit_b._spellbook.has_bucket_for(conduit_a._id)
    # Side A's destroy still ran even though side B's failed (best-effort is
    # per-side, not first-failure-aborts).
    assert conduit_a._spellbook.destroyed_peers == [conduit_b._id]
    assert conduit_b._spellbook.destroyed_peers == []
