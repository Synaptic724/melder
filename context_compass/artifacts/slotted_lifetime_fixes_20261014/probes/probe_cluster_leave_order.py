"""
Probe (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, D1): does an explicit cluster leave unshare the leaver's
shared roots from the remaining members?

`ConduitCloud.remove_conduit_from_cluster` calls `ConduitCluster.remove_member` (which pops the leaver's
`shared_spells` entry) before `ConduitCluster.handle_leave`, whose first unshare loop reads that entry to remove the
leaver's roots from every peer. The probe shares one `unique_per_conduit_cluster` root from the leaver to a peer,
then leaves through the cloud and reports whether the peer still holds the leaver's root in a contract.

Run (from a tree root with src/ and tests/):  PYTHONPATH=src:. python probe_cluster_leave_order.py
"""
from typing import Any, Dict

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class SharedLeaf:
    """`unique_per_conduit_cluster` root contributed by the leaving member."""


def reset_world() -> None:
    """Fresh Aether, as the component tests do."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def dynamic_configuration(frame: str) -> SpellbookConfiguration:
    """A dynamic configuration for one frame with one phase worker."""
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def run() -> Dict[str, Any]:
    """Share the leaver's root to a peer, leave through the cloud, report what the peer still holds."""
    frame = "probe-leave-order"
    leaver_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    leaf_id = leaver_book.bind(spell=SharedLeaf, existence=Existence.unique_per_conduit_cluster, permissions="create")
    leaver = leaver_book.conjure(dynamic=True, name="leaver")
    peer_book = Spellbook(aetheric_frame=frame)
    peer = peer_book.conjure(dynamic=True, name="peer")
    out: Dict[str, Any] = {}
    try:
        leaver.link(peer)
        cloud = Spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("k")
        cloud.add_conduit_to_cluster(leaver, "k")
        cloud.add_conduit_to_cluster(peer, "k")
        cluster = cloud.get_cluster("k")
        out["setup_leaver_root_recorded"] = leaver.id in cluster.get_shared_spells()
        out["setup_peer_holds_leaver_root"] = peer.get_spell_in_contracts(leaf_id) is not None
        cloud.remove_conduit_from_cluster(leaver, "k")
        out["after_leave_leaver_in_members"] = leaver.id in cluster.get_members()
        out["after_leave_peer_holds_leaver_root"] = peer.get_spell_in_contracts(leaf_id) is not None
    finally:
        for conduit in (peer, leaver):
            try:
                conduit.cleanup()
            except BaseException as error:
                out[f"cleanup_error_{conduit.id[:6]}"] = type(error).__name__
    return out


def run_control_link_only() -> Dict[str, Any]:
    """Control: a plain link with no cluster contracts nothing, so the peer holds no root of the other side."""
    frame = "probe-leave-order-link"
    leaver_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    leaf_id = leaver_book.bind(spell=SharedLeaf, existence=Existence.unique_per_conduit_cluster, permissions="create")
    leaver = leaver_book.conjure(dynamic=True, name="leaver")
    peer_book = Spellbook(aetheric_frame=frame)
    peer = peer_book.conjure(dynamic=True, name="peer")
    try:
        leaver.link(peer)
        return {"control_link_only_peer_holds_leaver_root": peer.get_spell_in_contracts(leaf_id) is not None}
    finally:
        peer.cleanup()
        leaver.cleanup()


def run_control_leave_before_member_removal() -> Dict[str, Any]:
    """Control: `handle_leave` alone (membership still recorded) unshares the leaver's root from the peer."""
    frame = "probe-leave-order-handle"
    leaver_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    leaf_id = leaver_book.bind(spell=SharedLeaf, existence=Existence.unique_per_conduit_cluster, permissions="create")
    leaver = leaver_book.conjure(dynamic=True, name="leaver")
    peer_book = Spellbook(aetheric_frame=frame)
    peer = peer_book.conjure(dynamic=True, name="peer")
    try:
        leaver.link(peer)
        cloud = Spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("k")
        cloud.add_conduit_to_cluster(leaver, "k")
        cloud.add_conduit_to_cluster(peer, "k")
        cluster = cloud.get_cluster("k")
        cluster.handle_leave(leaver)
        cluster.remove_member(leaver.id)
        return {"control_handle_leave_first_peer_holds_leaver_root": peer.get_spell_in_contracts(leaf_id) is not None}
    finally:
        peer.cleanup()
        leaver.cleanup()


if __name__ == "__main__":
    for case in (run, run_control_link_only, run_control_leave_before_member_removal):
        reset_world()
        for key, value in case().items():
            print(f"{key}: {value}")
