from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Iterable, Optional, Tuple, Union

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_cluster import ConduitCluster
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_conduit_cluster() -> None:
    """
    Purpose:
        Ensure component ConduitCluster tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class _ContractingConduitStub:
    """
    Purpose:
        Provide a minimal conduit stub for component ConduitCluster tests.
    Contract:
        - Exposes _id, _spellbook, and _aetheric_frame_name for cluster lookups.
        - Records contract and removal calls for assertions.
    """

    def __init__(
        self,
        *,
        conduit_id: str,
        spellbook: Spellbook,
        aetheric_frame: str = "default",
    ) -> None:
        """
        Purpose:
            Initialize the conduit stub with identity and spellbook references.
        Contract:
            - Stores the provided identifiers.
            - Initializes call logs for contract/removal tracking.
        Args:
            conduit_id: Identifier to expose as _id.
            spellbook: Spellbook used for resolving SpellIndex objects.
            aetheric_frame: Frame name used in contract calls.
        Returns:
            None.
        """
        self._id = conduit_id
        self._spellbook = spellbook
        self._aetheric_frame_name = aetheric_frame
        self._conduit_state = ConduitState.normal
        self.contract_calls: list[dict[str, object]] = []
        self.remove_root_calls: list[dict[str, object]] = []

    def add_spell_to_contract(
        self,
        *,
        spell: object,
        conduit: object,
        permissions: str,
        aetheric_frame: str,
        reason: DetailReason,
        root_spell_id: str,
        link_dependencies: bool,
    ) -> None:
        """
        Purpose:
            Record contract calls issued by ConduitCluster.
        Contract:
            - Appends a dict snapshot of the call inputs for assertions.
        Args:
            spell: Spell object being contracted.
            conduit: Conduit that owns the spell.
            permissions: Permissions string applied to the contract.
            aetheric_frame: Frame name used for the contract.
            reason: DetailReason for the contract.
            root_spell_id: Cluster-scoped root identifier for teardown.
            link_dependencies: Whether dependency closure is included.
        Returns:
            None.
        """
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

    def remove_root_from_contracts(
        self,
        *,
        root_spell_id: str,
        conduit: object,
        aetheric_frame: str,
    ) -> None:
        """
        Purpose:
            Record removal calls issued by ConduitCluster.
        Contract:
            - Appends a dict snapshot of the removal inputs for assertions.
        Args:
            root_spell_id: Cluster-scoped root identifier for teardown.
            conduit: Conduit that owns the spell.
            aetheric_frame: Frame name used for removal.
        Returns:
            None.
        """
        self.remove_root_calls.append(
            {
                "root_spell_id": root_spell_id,
                "conduit": conduit,
                "aetheric_frame": aetheric_frame,
            }
        )

    @contextmanager
    def transaction(
        self,
        transaction_type: Union[ChangeTransactionType, str],
        *,
        conduit_ids: Optional[Iterable[str]] = None,
        conduits: Optional[Iterable[object]] = None,
        scope_keys: Optional[Iterable[str]] = None,
        scope_hashes: Optional[Iterable[str]] = None,
        binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
        contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "_ContractingConduitStub":
        """
        Purpose:
            Provide a no-op transaction context manager for cluster component tests.
        Contract:
            - Accepts change-control parameters but does not enforce them.
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
            _ContractingConduitStub: The stub conduit instance.
        """
        yield self


class _FrameStub:
    """
    Purpose:
        Provide a minimal frame-local registry stub for ConduitCluster.
    Contract:
        - Exposes `_conduits` and `frame_name`.
    """

    def __init__(
            self,
            conduits: list[_ContractingConduitStub],
            frame_name: str = "default",
    ) -> None:
        """
        Purpose:
            Initialize the stub with a conduit registry and frame name.
        Contract:
            - Builds a dict map of conduit id to conduit instance.
        Args:
            conduits: Conduits to register in the frame map.
        Returns:
            None.
        """
        self.frame_name = frame_name
        self._conduits = {conduit._id: conduit for conduit in conduits}

def _make_cluster(
        name: str = "cluster-a",
        registry: Optional[Dict[str, _ContractingConduitStub]] = None,
        aetheric_frame_name: str = "default",
        auto_link_dependencies: bool = True,
) -> ConduitCluster:
    """
    Purpose:
        Build a ConduitCluster using the narrow registry plus frame-name contract.
    Contract:
        - Uses an empty registry by default for tests that do not need peer lookup.
    """
    if registry is None:
        registry = {}
    return ConduitCluster(
        name,
        registry,
        aetheric_frame_name,
        DevopsInformationRegistry(aetheric_frame_name),
        auto_link_dependencies,
    )


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component ConduitCluster tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the first local spell whose SpellIndex.selected_spell_id matches `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.selected_spell_id == spell_id:
            return spell
    return None


def test_component_cluster_refresh_shareable_roots_filters_real_spells() -> None:
    """
    Purpose:
        Validate refresh_shareable_roots records only cluster-scoped spells.
    Contract:
        - Existence.unique_per_conduit_cluster spells are captured.
        - Other existence scopes are ignored.
    Returns:
        None.
    Raises:
        AssertionError: If non-cluster spells are recorded as shareable.
    """
    spellbook = _make_spellbook()
    cluster_spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    spellbook.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )
    owner = _ContractingConduitStub(conduit_id="owner-1", spellbook=spellbook)
    cluster = _make_cluster("cluster-a")

    cluster.refresh_shareable_roots(owner)

    shareable_spell = _get_spell_by_version_id(spellbook, cluster_spell_id)
    assert shareable_spell is not None
    shared = cluster.get_shared_spells()
    assert shared[owner._id] == {shareable_spell.spell_index}


def test_component_cluster_share_to_borrower_contracts_real_spell() -> None:
    """
    Purpose:
        Validate share_to_borrower contracts a real spell object to a borrower.
    Contract:
        - Borrower receives a contract call with DetailReason.root.
        - root_spell_id is cluster-scoped for the owner.
        - link_dependencies reflects the cluster configuration.
    Returns:
        None.
    Raises:
        AssertionError: If contract calls do not match expectations.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = _ContractingConduitStub(
        conduit_id="owner-1",
        spellbook=spellbook,
        aetheric_frame="frame-a",
    )
    borrower = _ContractingConduitStub(
        conduit_id="borrower-1",
        spellbook=_make_spellbook(),
    )
    cluster = _make_cluster(
        "cluster-a",
        aetheric_frame_name="frame-a",
    )
    spell = _get_spell_by_version_id(spellbook, spell_id)
    assert spell is not None
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
            "link_dependencies": True,
        }
    ]


def test_component_cluster_remove_and_strip_spell_uses_real_spell() -> None:
    """
    Purpose:
        Validate remove_and_strip_spell removes cluster roots and re-adds manually.
    Contract:
        - Borrower receives a removal for the cluster-scoped root id.
        - Borrower receives a manual contract for the raw spell id.
    Returns:
        None.
    Raises:
        AssertionError: If removal or manual re-add calls are missing.
    """
    spellbook = _make_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = _ContractingConduitStub(conduit_id="owner-1", spellbook=spellbook)
    borrower = _ContractingConduitStub(
        conduit_id="borrower-1",
        spellbook=_make_spellbook(),
    )
    frame = _FrameStub([owner, borrower], frame_name="frame-1")
    cluster = _make_cluster("cluster-a", frame._conduits, frame.frame_name)
    cluster.add_member(owner._id)
    cluster.add_member(borrower._id)
    spell = _get_spell_by_version_id(spellbook, spell_id)
    assert spell is not None
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


def test_component_cluster_handle_join_shares_real_spells_between_peers() -> None:
    """
    Purpose:
        Validate handle_join shares real spells between cluster members.
    Contract:
        - Second join triggers cross-sharing in both directions.
        - Borrowers receive contract calls with cluster-scoped root ids.
    Returns:
        None.
    Raises:
        AssertionError: If cross-sharing does not occur as expected.
    """
    owner_book = _make_spellbook()
    owner_spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    peer_book = _make_spellbook()
    peer_spell_id = peer_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = _ContractingConduitStub(
        conduit_id="owner-1",
        spellbook=owner_book,
        aetheric_frame="frame-owner",
    )
    peer = _ContractingConduitStub(
        conduit_id="peer-1",
        spellbook=peer_book,
        aetheric_frame="frame-peer",
    )
    frame = _FrameStub([owner, peer], frame_name="frame-owner")
    cluster = _make_cluster("cluster-a", frame._conduits, frame.frame_name)

    cluster.handle_join(owner)
    cluster.handle_join(peer)

    owner_spell = _get_spell_by_version_id(owner_book, owner_spell_id)
    peer_spell = _get_spell_by_version_id(peer_book, peer_spell_id)
    assert owner_spell is not None
    assert peer_spell is not None
    assert peer.contract_calls == [
        {
            "spell": owner_spell,
            "conduit": owner,
            "permissions": owner_spell.permissions,
            "aetheric_frame": "frame-owner",
            "reason": DetailReason.root,
            "root_spell_id": cluster._cluster_root_id(owner._id, owner_spell.spell_id),
            "link_dependencies": True,
        }
    ]
    assert owner.contract_calls == [
        {
            "spell": peer_spell,
            "conduit": peer,
            "permissions": peer_spell.permissions,
            "aetheric_frame": "frame-owner",
            "reason": DetailReason.root,
            "root_spell_id": cluster._cluster_root_id(peer._id, peer_spell.spell_id),
            "link_dependencies": True,
        }
    ]


def test_component_cluster_add_member_registers_registry_membership() -> None:
    """
    Purpose:
        Validate cluster member adds are mirrored into the dev-ops registry.
    Contract:
        - get_clusters_for_conduit reflects the added membership.
    Returns:
        None.
    Raises:
        AssertionError: If registry membership is missing.
    """
    cluster = _make_cluster("cluster-a")

    cluster.add_member("conduit-1")

    assert cluster._devops_information_registry.get_clusters_for_conduit("conduit-1") == (
        cluster.id,
    )


def test_component_cluster_remove_member_unregisters_registry_membership() -> None:
    """
    Purpose:
        Validate cluster member removals are mirrored into the dev-ops registry.
    Contract:
        - Removing the member clears conduit -> cluster lookup.
    Returns:
        None.
    Raises:
        AssertionError: If registry membership survives removal.
    """
    cluster = _make_cluster("cluster-a")
    cluster.add_member("conduit-1")

    cluster.remove_member("conduit-1")

    assert cluster._devops_information_registry.get_clusters_for_conduit("conduit-1") == ()


def test_component_cluster_cleanup_unregisters_member_registry_edges() -> None:
    """
    Purpose:
        Validate cleanup clears member registry edges through the cluster identity.
    Contract:
        - Member conduit -> cluster registry lookups are empty after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup leaves registry membership behind.
    """
    cluster = _make_cluster("cluster-a")
    cluster.add_member("conduit-1")
    cluster.add_member("conduit-2")

    cluster.cleanup()

    assert cluster._cleaned is True


def test_component_cluster_set_auto_link_dependencies_updates_runtime_policy() -> None:
    """
    Purpose:
        Validate dependency-link policy can be toggled on the live cluster.
    Contract:
        - set_auto_link_dependencies updates the live policy bit.
    Returns:
        None.
    Raises:
        AssertionError: If the policy bit does not update.
    """
    cluster = _make_cluster("cluster-a", auto_link_dependencies=True)

    cluster.set_auto_link_dependencies(False)

    assert cluster.auto_link_dependencies is False


def test_component_cluster_describe_reports_current_members_and_policy() -> None:
    """
    Purpose:
        Validate describe returns current members and policy state.
    Contract:
        - describe reports auto_link_dependencies and member ids.
    Returns:
        None.
    Raises:
        AssertionError: If describe omits current runtime state.
    """
    cluster = _make_cluster("cluster-a", auto_link_dependencies=True)
    cluster.add_member("conduit-1")
    cluster.add_member("conduit-2")

    described = cluster.describe()

    assert described["auto_link_dependencies"] is True
    assert set(described["members"]) == {"conduit-1", "conduit-2"}


def test_component_cluster_refresh_member_shares_replays_owner_roots_to_existing_peer() -> None:
    """
    Purpose:
        Validate refresh_member_shares replays recorded roots to peers.
    Contract:
        - Existing peers receive contract calls for the refreshed member's roots.
    Returns:
        None.
    Raises:
        AssertionError: If refresh_member_shares does not replay root contracts.
    """
    owner_book = _make_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = _ContractingConduitStub(conduit_id="owner-1", spellbook=owner_book)
    peer = _ContractingConduitStub(conduit_id="peer-1", spellbook=_make_spellbook())
    frame = _FrameStub([owner, peer], frame_name="frame-owner")
    cluster = _make_cluster("cluster-a", frame._conduits, frame.frame_name)
    cluster.add_member(owner._id)
    cluster.add_member(peer._id)
    spell = _get_spell_by_version_id(owner_book, spell_id)
    assert spell is not None
    cluster.add_shared_spell(owner._id, spell.spell_index)

    cluster.refresh_member_shares(owner)

    assert peer.contract_calls == [
        {
            "spell": spell,
            "conduit": owner,
            "permissions": spell.permissions,
            "aetheric_frame": "frame-owner",
            "reason": DetailReason.root,
            "root_spell_id": cluster._cluster_root_id(owner._id, spell.spell_id),
            "link_dependencies": True,
        }
    ]


def test_component_cluster_handle_leave_strips_roots_in_both_directions() -> None:
    """
    Purpose:
        Validate handle_leave removes shared roots in both ownership directions.
    Contract:
        - Remaining peers remove roots owned by the leaver.
        - The leaver removes roots owned by remaining peers.
    Returns:
        None.
    Raises:
        AssertionError: If leave teardown is one-sided.
    """
    owner_book = _make_spellbook()
    peer_book = _make_spellbook()
    owner_spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    peer_spell_id = peer_book.bind(
        spell=BasicConfig,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = _ContractingConduitStub(conduit_id="owner-1", spellbook=owner_book)
    peer = _ContractingConduitStub(conduit_id="peer-1", spellbook=peer_book)
    frame = _FrameStub([owner, peer], frame_name="frame-owner")
    cluster = _make_cluster("cluster-a", frame._conduits, frame.frame_name)
    cluster.add_member(owner._id)
    cluster.add_member(peer._id)
    owner_spell = _get_spell_by_version_id(owner_book, owner_spell_id)
    peer_spell = _get_spell_by_version_id(peer_book, peer_spell_id)
    assert owner_spell is not None
    assert peer_spell is not None
    cluster.add_shared_spell(owner._id, owner_spell.spell_index)
    cluster.add_shared_spell(peer._id, peer_spell.spell_index)

    cluster.handle_leave(owner)

    assert peer.remove_root_calls == [
        {
            "root_spell_id": cluster._cluster_root_id(owner._id, owner_spell.spell_id),
            "conduit": owner,
            "aetheric_frame": "frame-owner",
        }
    ]
    assert owner.remove_root_calls == [
        {
            "root_spell_id": cluster._cluster_root_id(peer._id, peer_spell.spell_id),
            "conduit": peer,
            "aetheric_frame": "frame-owner",
        }
    ]


def test_component_cluster_add_and_share_spell_uses_cluster_policy_when_override_missing() -> None:
    """
    Purpose:
        Validate add_and_share_spell uses the cluster's dependency-link policy by default.
    Contract:
        - link_dependencies on the borrower-side contract call mirrors auto_link_dependencies.
    Returns:
        None.
    Raises:
        AssertionError: If default policy forwarding drifts.
    """
    owner_book = _make_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = _ContractingConduitStub(conduit_id="owner-1", spellbook=owner_book)
    peer = _ContractingConduitStub(conduit_id="peer-1", spellbook=_make_spellbook())
    frame = _FrameStub([owner, peer], frame_name="frame-owner")
    cluster = _make_cluster(
        "cluster-a",
        frame._conduits,
        frame.frame_name,
        auto_link_dependencies=False,
    )
    cluster.add_member(owner._id)
    cluster.add_member(peer._id)
    spell = _get_spell_by_version_id(owner_book, spell_id)
    assert spell is not None

    cluster.add_and_share_spell(owner, spell)

    assert peer.contract_calls == []


def test_component_cluster_remove_member_drops_shared_spell_bucket() -> None:
    """
    Purpose:
        Validate member removal drops that owner's shared-spell bucket.
    Contract:
        - shared_spells no longer contains the removed owner id.
    Returns:
        None.
    Raises:
        AssertionError: If shared-spell buckets survive member removal.
    """
    owner_book = _make_spellbook()
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = _ContractingConduitStub(conduit_id="owner-1", spellbook=owner_book)
    cluster = _make_cluster("cluster-a")
    spell = _get_spell_by_version_id(owner_book, spell_id)
    assert spell is not None
    cluster.add_member(owner._id)
    cluster.add_shared_spell(owner._id, spell.spell_index)

    cluster.remove_member(owner._id)

    assert owner._id not in cluster.get_shared_spells()



