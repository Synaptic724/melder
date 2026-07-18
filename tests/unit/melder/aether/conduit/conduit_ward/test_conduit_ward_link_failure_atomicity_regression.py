"""Regression: BUG-004 (2026-07-17 audit) - failed link leaves no half-created contract.

Symptom:
    `ConduitWard._create_new_contract` used to insert the Contract into both
    ward registries and indexes FIRST, then create the two spellbook buckets
    sequentially. When the second bucket create raised, the public
    ``a.link(b)`` raised too - yet both wards still reported the link, the
    contract survived, and only A's spellbook bucket existed.

Contract under test:
    Link creation is atomic from the caller's view. Every fallible step (both
    spellbook bucket creates, ``Contract`` construction) runs before ward
    registry/index publication; a failed link leaves zero observable topology
    or sharing state on either side, and only buckets the call itself created
    are rolled back.
"""

import threading
from typing import Dict, List, Optional, Set, Tuple

import pytest

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from types import SimpleNamespace


class FakeLogger:
    """Minimal logger that absorbs ConduitWard logging calls.

    Contract:
        - Accepts the ward's keyword-heavy logging signature.
        - Records (level, message) pairs for optional inspection.
    """

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


class FakeSpellbook:
    """Contracted-bucket fake mirroring the real Spellbook's four-map lockstep.

    Contract:
        - `_create_link_contract` / `_remove_link_contract` mirror the real
          semantics: no-op when the bucket exists / is absent, RuntimeError on
          inconsistent map state, all four maps mutated in lockstep.
        - `fail_create_for` injects one targeted failure so tests can raise on
          exactly the bucket create they choose (the audit's trigger is the
          SECOND create failing).
    """

    def __init__(self) -> None:
        """Initialize the four contracted maps and the failure injector."""
        self._lock = threading.RLock()
        self._contracted_spells: Dict[str, Dict[object, object]] = {}
        self._lookup_contracted_spells: Dict[str, Dict[Tuple[str, str], object]] = {}
        self._contracted_spell_ids: Dict[str, Set[str]] = {}
        self._contracted_spells_by_id: Dict[str, Dict[str, object]] = {}
        self.fail_create_for: Optional[str] = None
        self.create_calls: List[str] = []
        self.remove_calls: List[str] = []

    def _create_link_contract(self, conduit_id: str) -> None:
        """Create the four-bucket structure for one peer, or fail on command.

        Raises:
            RuntimeError: When armed via `fail_create_for` for this peer, or
                when the four maps disagree about the bucket's existence.
        """
        self.create_calls.append(conduit_id)
        if self.fail_create_for == conduit_id:
            raise RuntimeError(
                f"injected: bucket create refused for peer {conduit_id}"
            )
        exists = [
            conduit_id in self._contracted_spells,
            conduit_id in self._lookup_contracted_spells,
            conduit_id in self._contracted_spell_ids,
            conduit_id in self._contracted_spells_by_id,
        ]
        if len(set(exists)) != 1:
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}."
            )
        if not exists[0]:
            with self._lock:
                self._contracted_spells[conduit_id] = {}
                self._lookup_contracted_spells[conduit_id] = {}
                self._contracted_spell_ids[conduit_id] = set()
                self._contracted_spells_by_id[conduit_id] = {}

    def _remove_link_contract(self, conduit_id: str) -> None:
        """Remove the four-bucket structure for one peer in lockstep.

        Raises:
            RuntimeError: When the four maps disagree about the bucket's
                existence (mirrors the real inconsistency guard).
        """
        self.remove_calls.append(conduit_id)
        exists = [
            conduit_id in self._contracted_spells,
            conduit_id in self._lookup_contracted_spells,
            conduit_id in self._contracted_spell_ids,
            conduit_id in self._contracted_spells_by_id,
        ]
        if len(set(exists)) != 1:
            raise RuntimeError(
                f"Inconsistent link contract state for conduit ID {conduit_id}."
            )
        if exists[0]:
            with self._lock:
                self._contracted_spells.pop(conduit_id, None)
                self._lookup_contracted_spells.pop(conduit_id, None)
                self._contracted_spell_ids.pop(conduit_id, None)
                self._contracted_spells_by_id.pop(conduit_id, None)

    def has_bucket_for(self, conduit_id: str) -> bool:
        """Return whether any of the four maps holds a bucket for the peer."""
        return (
            conduit_id in self._contracted_spells
            or conduit_id in self._lookup_contracted_spells
            or conduit_id in self._contracted_spell_ids
            or conduit_id in self._contracted_spells_by_id
        )


class FakeConduit:
    """Minimal conduit host carrying one real `ConduitWard` for link tests.

    Contract:
        - Exposes the runtime conduit surface the ward's link path reads
          (`_id`, `_conduit_ward`, `_conduit_state`, `_aetheric_frame_name`,
          `_spellbook`, `_crystallizer`, `_transaction_identity`).
        - The crystallizer stub reports `activated=False` so every record
          seam in the ward self-gates off.
    """

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
def linked_pair() -> "tuple[FakeConduit, FakeConduit]":
    """Yield two unlinked dynamic conduit shells, cleaned after the test."""
    conduit_a = FakeConduit("conduit-a")
    conduit_b = FakeConduit("conduit-b")
    yield conduit_a, conduit_b
    conduit_a.cleanup()
    conduit_b.cleanup()


def _assert_zero_link_state(conduit_a: FakeConduit, conduit_b: FakeConduit) -> None:
    """Assert no observable topology or sharing state exists on either side.

    Contract:
        This is the BUG-004 acceptance surface: after a failed link, wards,
        indexes, and spellbook buckets must all agree the link never happened.
    """
    ward_a = conduit_a._conduit_ward
    ward_b = conduit_b._conduit_ward
    assert ward_a._find_contract(conduit_b) is None
    assert ward_b._find_contract(conduit_a) is None
    assert ward_a._contracts == {}
    assert ward_b._contracts == {}
    assert conduit_b._id not in ward_a._initiated_index
    assert conduit_a._id not in ward_b._received_index
    assert not conduit_a._spellbook.has_bucket_for(conduit_b._id)
    assert not conduit_b._spellbook.has_bucket_for(conduit_a._id)


def test_failed_target_bucket_create_leaves_no_link_state(
    linked_pair: "tuple[FakeConduit, FakeConduit]",
) -> None:
    """The audited trigger: the SECOND bucket create raises mid-link.

    Contract assertions:
        - The public link raises the injected error.
        - Zero observable state remains on wards, indexes, and both books.
        - After disarming, the same link succeeds fully (recoverability).
    """
    conduit_a, conduit_b = linked_pair
    conduit_b._spellbook.fail_create_for = conduit_a._id

    with pytest.raises(RuntimeError, match="injected"):
        conduit_a._conduit_ward._link(conduit_b)

    _assert_zero_link_state(conduit_a, conduit_b)

    conduit_b._spellbook.fail_create_for = None
    assert conduit_a._conduit_ward._link(conduit_b) is True
    assert conduit_a._conduit_ward._find_contract(conduit_b) is not None
    assert conduit_b._conduit_ward._find_contract(conduit_a) is not None
    assert conduit_a._spellbook.has_bucket_for(conduit_b._id)
    assert conduit_b._spellbook.has_bucket_for(conduit_a._id)


def test_failed_own_bucket_create_leaves_no_link_state(
    linked_pair: "tuple[FakeConduit, FakeConduit]",
) -> None:
    """A failure on the initiating side's own bucket also leaves zero state."""
    conduit_a, conduit_b = linked_pair
    conduit_a._spellbook.fail_create_for = conduit_b._id

    with pytest.raises(RuntimeError, match="injected"):
        conduit_a._conduit_ward._link(conduit_b)

    _assert_zero_link_state(conduit_a, conduit_b)


def test_rollback_preserves_preexisting_residue_bucket(
    linked_pair: "tuple[FakeConduit, FakeConduit]",
) -> None:
    """Rollback removes only buckets the failed call itself created.

    Contract assertions:
        - A bucket that existed BEFORE the failed link (fault residue from an
          earlier incident) survives the rollback untouched.
        - The target side's freshly attempted bucket does not exist.
    """
    conduit_a, conduit_b = linked_pair
    conduit_a._spellbook._create_link_contract(conduit_b._id)
    assert conduit_a._spellbook.has_bucket_for(conduit_b._id)

    conduit_b._spellbook.fail_create_for = conduit_a._id
    with pytest.raises(RuntimeError, match="injected"):
        conduit_a._conduit_ward._link(conduit_b)

    assert conduit_a._spellbook.has_bucket_for(conduit_b._id), (
        "pre-existing residue bucket must survive a failed link's rollback"
    )
    assert not conduit_b._spellbook.has_bucket_for(conduit_a._id)
    assert conduit_a._conduit_ward._contracts == {}
    assert conduit_b._conduit_ward._contracts == {}
