"""
Audit probe (TASK-2026-10-14-audit_slotted_lifetime_ownership): which object ends each slotted instance, and does
anything still hold it when that happens?

Every case builds a fresh world (Aether reset), creates the instance through one route, then runs one event that
ends or moves an owner and prints what a caller can observe: whether the same instance is still served, how many
times Melder ran each disposal method (`closes`), and what a later meld does. The owner's rule being audited: the
object a lifetime names owns the instance and everything built for it, which lives exactly as long as that object.

Cases:
  c1 cluster leader torn down while elected      - a member's per-conduit holder depends on the cluster instance
  c2 cluster leader (not the spell's owner) leaves, a member is elected
  c3 a non-leader member root is torn down without leaving; the cluster then unelects and elects
  t3 ownership transfer, default (move_creations=False) - a disposal-bearing unique holder
  t4 ownership transfer, move_creations=True     - a unique holder with a disposal-bearing many child, with its deps
  t4b ownership transfer, move_creations=True    - the same holder alone (the many child's spell stays)
  p5 purge and re-meld a per-conduit holder five times - its disposal-bearing many child
  u6 lesser upgrade                              - the lesser's per-conduit holder over a lineage instance
  b7 lender torn down                            - a borrower's per-conduit holder over the lender's contracted unique
  r8 lineage holder first melded in a lesser's spellspace - its many child (route without a dedicated probe)
  r9 cluster holder first melded in a member's spellspace - its many child (route without a dedicated probe)

Run (from a tree root that has src/ and tests/):  PYTHONPATH=src:. python probe_lifetime_owners.py
"""
import sys
import traceback
from typing import Any, Callable, Dict, List, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Closable:
    """Base of every probe object: `close` is the declared disposal method and `closes` counts Melder's calls."""

    def __init__(self) -> None:
        self.closes = 0

    def close(self) -> None:
        self.closes += 1


class C1Leaf(Closable):
    """`unique_per_conduit_cluster` instance (c1)."""


class C1Parent(Closable):
    """`unique_per_conduit` holder on a member root, over the cluster instance (c1)."""

    def __init__(self, dep=SpellContract(spell=C1Leaf)) -> None:
        super().__init__()
        self.dep = dep


class C2Leaf(Closable):
    """`unique_per_conduit_cluster` instance (c2)."""


class C2Parent(Closable):
    """`unique_per_conduit` holder on a member root, over the cluster instance (c2)."""

    def __init__(self, dep=SpellContract(spell=C2Leaf)) -> None:
        super().__init__()
        self.dep = dep


class T3Holder(Closable):
    """`unique` holder whose ownership is transferred (t3)."""


class T4Child(Closable):
    """`many` child of the transferred holder (t4)."""


class T4Holder(Closable):
    """`unique` holder transferred with move_creations=True (t4)."""

    def __init__(self, child: T4Child) -> None:
        super().__init__()
        self.child = child


class P5Child(Closable):
    """`many` child of the purged holder (p5)."""


class P5Holder(Closable):
    """`unique_per_conduit` holder purged and melded again (p5)."""

    def __init__(self, child: P5Child) -> None:
        super().__init__()
        self.child = child


class U6Lineage(Closable):
    """`unique_per_conduit_lineage` instance of the old root's lineage (u6)."""


class U6Holder(Closable):
    """`unique_per_conduit` holder melded in the lesser that is upgraded (u6)."""

    def __init__(self, lineage: U6Lineage) -> None:
        super().__init__()
        self.lineage = lineage


class B7Resource(Closable):
    """`unique` instance owned by the lender and contracted to the borrower (b7)."""


class B7Holder(Closable):
    """`unique_per_conduit` holder on the borrower, over the lender's resource (b7)."""

    def __init__(self, dep=SpellContract(spell=B7Resource)) -> None:
        super().__init__()
        self.dep = dep


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


def attempt(action: Callable[[], Any]) -> Tuple[bool, Any]:
    """Run one action; return (True, value) or (False, 'ExceptionType: message')."""
    try:
        return True, action()
    except BaseException as error:  # the probe reports every outcome, including ExceptionGroup
        return False, f"{type(error).__name__}: {str(error).splitlines()[0][:140] if str(error) else ''}"


def stored(conduit: Conduit, spell_id: str) -> Any:
    """What one conduit's own store holds under a spell id (None when absent or the store is gone)."""
    try:
        return conduit._creations._creations.get(spell_id)
    except AttributeError:
        return None


def bind(book: Spellbook, spell: type, existence: Existence) -> str:
    """Bind one probe class with its `close` disposal method."""
    return book.bind(spell=spell, existence=existence, permissions="create", disposal_method_names=["close"])


def case_c1() -> Dict[str, Any]:
    """Cluster leader torn down while elected; a member's holder depends on the cluster instance."""
    frame = "audit-c1"
    provider_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    leaf_id = bind(provider_book, C1Leaf, Existence.unique_per_conduit_cluster)
    provider = provider_book.conjure(dynamic=True, name="c1-leader")
    member_book = Spellbook(aetheric_frame=frame)
    parent_id = bind(member_book, C1Parent, Existence.unique_per_conduit)
    member = member_book.conjure(dynamic=True, name="c1-member")
    out: Dict[str, Any] = {}
    try:
        provider.link(member)
        cloud = Spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("c1")
        for root in (provider, member):
            cloud.add_conduit_to_cluster(root, "c1")
        for root in (provider, member):
            cloud.refresh_cluster_shares_for_conduit(root)
        cluster = cloud.get_cluster("c1")
        cluster.elect_leader(provider.id)
        parent = member.meld(spell_id=parent_id)
        leaf = parent.dep
        out["setup_leaf_in_leader_store"] = stored(provider, leaf_id) is leaf
        leader_id = provider.id
        provider.cleanup()
        out["after_leader_teardown_leaf_closes"] = leaf.closes
        ok, value = attempt(lambda: member.meld(spell_id=parent_id))
        out["after_member_holder_still_served"] = ok and value is parent
        out["after_member_holder_dep_is_disposed_leaf"] = parent.dep is leaf and leaf.closes > 0
        ok, value = attempt(lambda: member.meld(spell_id=leaf_id))
        out["after_member_meld_cluster_spell"] = "same leaf" if ok and value is leaf else (
            "new instance" if ok else value)
        out["after_cluster_master_conduit_id_is_dead_leader"] = cluster.master_conduit_id == leader_id
        out["after_cluster_members_still_list_leader"] = leader_id in cluster.get_members()
    finally:
        attempt(member.cleanup)
        attempt(provider.cleanup)
    out["final_parent_closes"] = parent.closes
    out["final_leaf_closes"] = leaf.closes
    return out


def case_c2() -> Dict[str, Any]:
    """The elected leader (not the spell's owner) leaves the cluster and a member is elected."""
    frame = "audit-c2"
    owner_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    leaf_id = bind(owner_book, C2Leaf, Existence.unique_per_conduit_cluster)
    owner = owner_book.conjure(dynamic=True, name="c2-owner")
    leader_book = Spellbook(aetheric_frame=frame)
    leader = leader_book.conjure(dynamic=True, name="c2-leader")
    member_book = Spellbook(aetheric_frame=frame)
    parent_id = bind(member_book, C2Parent, Existence.unique_per_conduit)
    member = member_book.conjure(dynamic=True, name="c2-member")
    out: Dict[str, Any] = {}
    try:
        owner.link(leader)
        owner.link(member)
        cloud = Spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("c2")
        for root in (owner, leader, member):
            cloud.add_conduit_to_cluster(root, "c2")
        for root in (owner, leader, member):
            cloud.refresh_cluster_shares_for_conduit(root)
        cluster = cloud.get_cluster("c2")
        cluster.elect_leader(leader.id)
        parent = member.meld(spell_id=parent_id)
        leaf = parent.dep
        out["setup_leaf_in_leader_store"] = stored(leader, leaf_id) is leaf
        cloud.remove_conduit_from_cluster(leader, "c2")
        ok, value = attempt(lambda: member.meld(spell_id=leaf_id))
        out["after_leave_member_meld_cluster_spell"] = "same leaf" if ok and value is leaf else (
            "new instance" if ok else value)
        cluster.elect_leader(member.id)
        ok, second = attempt(lambda: member.meld(spell_id=leaf_id))
        out["after_reelect_cluster_instance_is_old_leaf"] = ok and second is leaf
        out["after_reelect_old_leaf_still_in_departed_leader_store"] = stored(leader, leaf_id) is leaf
        out["after_reelect_member_holder_dep_is_old_leaf"] = parent.dep is leaf
        leader.cleanup()
        out["after_departed_leader_teardown_old_leaf_closes"] = leaf.closes
        ok, value = attempt(lambda: member.meld(spell_id=parent_id))
        out["after_member_holder_still_served_with_disposed_dep"] = ok and value is parent and leaf.closes > 0
    finally:
        attempt(member.cleanup)
        attempt(leader.cleanup)
        attempt(owner.cleanup)
    out["final_old_leaf_closes"] = leaf.closes
    out["final_second_instance_closes"] = second.closes if isinstance(second, Closable) else None
    return out


def case_t3() -> Dict[str, Any]:
    """Ownership transfer with the default move_creations=False of a disposal-bearing unique holder."""
    frame = "audit-t3"
    source_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    holder_id = bind(source_book, T3Holder, Existence.unique)
    source = source_book.conjure(dynamic=True, name="t3-source")
    target_book = Spellbook(aetheric_frame=frame)
    target = target_book.conjure(dynamic=True, name="t3-target")
    out: Dict[str, Any] = {}
    try:
        holder = source.meld(spell_id=holder_id)
        out["setup_holder_in_source_store"] = stored(source, holder_id) is holder
        source.transfer_spell_ownership(spell=holder_id, target_conduit=target)
        out["after_transfer_holder_closes"] = holder.closes
        out["after_transfer_holder_in_source_store"] = stored(source, holder_id) is holder
        out["after_transfer_holder_in_target_store"] = stored(target, holder_id) is holder
        ok, value = attempt(lambda: target.meld(spell_id=holder_id))
        out["after_transfer_target_meld"] = "same holder" if ok and value is holder else (
            "new holder" if ok else value)
        source.cleanup()
        out["after_source_teardown_holder_closes"] = holder.closes
    finally:
        attempt(source.cleanup)
        attempt(target.cleanup)
    out["final_holder_closes"] = holder.closes
    return out


def case_t4() -> Dict[str, Any]:
    """Ownership transfer with move_creations=True of a unique holder with a disposal-bearing many child."""
    frame = "audit-t4"
    source_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    child_id = bind(source_book, T4Child, Existence.many)
    holder_id = bind(source_book, T4Holder, Existence.unique)
    source = source_book.conjure(dynamic=True, name="t4-source")
    target_book = Spellbook(aetheric_frame=frame)
    target = target_book.conjure(dynamic=True, name="t4-target")
    out: Dict[str, Any] = {}
    try:
        holder = source.meld(spell_id=holder_id)
        child = holder.child
        out["setup_child_in_source_store"] = child in list(stored(source, child_id) or [])
        source.transfer_spell_ownership(
            spell=holder_id, target_conduit=target, move_creations=True, include_dependencies=True,
        )
        out["after_transfer_holder_in_target_store"] = stored(target, holder_id) is holder
        out["after_transfer_child_in_source_store"] = child in list(stored(source, child_id) or [])
        out["after_transfer_child_in_target_store"] = child in list(stored(target, child_id) or [])
        ok, value = attempt(lambda: target.meld(spell_id=holder_id))
        out["after_transfer_target_meld"] = "same holder" if ok and value is holder else (
            "new holder" if ok else value)
        source.cleanup()
        out["after_source_teardown_child_closes"] = child.closes
        ok, value = attempt(lambda: target.meld(spell_id=holder_id))
        out["after_source_teardown_target_serves_holder_with_disposed_child"] = (
            ok and value is holder and child.closes > 0)
    finally:
        attempt(source.cleanup)
        attempt(target.cleanup)
    out["final_holder_closes"] = holder.closes
    out["final_child_closes"] = child.closes
    return out


class T4bChild(Closable):
    """`many` child of the transferred holder; its spell stays with the source (t4b)."""


class T4bHolder(Closable):
    """`unique` holder transferred alone with move_creations=True (t4b)."""

    def __init__(self, child: T4bChild) -> None:
        super().__init__()
        self.child = child


def case_t4b() -> Dict[str, Any]:
    """Ownership transfer with move_creations=True of a unique holder alone (its many child's spell stays)."""
    frame = "audit-t4b"
    source_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    child_id = bind(source_book, T4bChild, Existence.many)
    holder_id = bind(source_book, T4bHolder, Existence.unique)
    source = source_book.conjure(dynamic=True, name="t4b-source")
    target_book = Spellbook(aetheric_frame=frame)
    target = target_book.conjure(dynamic=True, name="t4b-target")
    out: Dict[str, Any] = {}
    try:
        holder = source.meld(spell_id=holder_id)
        child = holder.child
        ok, value = attempt(lambda: source.transfer_spell_ownership(
            spell=holder_id, target_conduit=target, move_creations=True,
        ))
        out["transfer"] = "ok" if ok else value
        out["after_transfer_holder_in_target_store"] = stored(target, holder_id) is holder
        out["after_transfer_child_in_source_store"] = child in list(stored(source, child_id) or [])
        out["after_transfer_child_in_target_store"] = child in list(stored(target, child_id) or [])
        ok, value = attempt(lambda: target.meld(spell_id=holder_id))
        out["after_transfer_target_meld"] = "same holder" if ok and value is holder else (
            "new holder" if ok else value)
        source.cleanup()
        out["after_source_teardown_child_closes"] = child.closes
        ok, value = attempt(lambda: target.meld(spell_id=holder_id))
        out["after_source_teardown_target_meld"] = "same holder" if ok and value is holder else (
            "new holder" if ok else value)
    finally:
        attempt(source.cleanup)
        attempt(target.cleanup)
    out["final_holder_closes"] = holder.closes
    out["final_child_closes"] = child.closes
    return out


def case_p5() -> Dict[str, Any]:
    """Purge and re-meld a per-conduit holder five times; its many child is disposal-bearing."""
    book = Spellbook()
    child_id = bind(book, P5Child, Existence.many)
    holder_id = bind(book, P5Holder, Existence.unique_per_conduit)
    root = book.conjure(name="p5-root")
    out: Dict[str, Any] = {}
    holders: List[P5Holder] = []
    try:
        for _ in range(5):
            holder = root.meld(spell_id=holder_id)
            holders.append(holder)
            root.purge(spell_id=holder_id)
        out["purged_holders_closed"] = sum(holder.closes for holder in holders)
        out["children_of_purged_holders_closed"] = sum(holder.child.closes for holder in holders)
        out["children_still_registered_in_root_store"] = len(list(stored(root, child_id) or []))
    finally:
        attempt(root.cleanup)
    out["final_children_closed"] = sum(holder.child.closes for holder in holders)
    return out


def case_u6() -> Dict[str, Any]:
    """Upgrade a lesser that holds a per-conduit holder over the old lineage's instance."""
    frame = "audit-u6"
    book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    lineage_id = bind(book, U6Lineage, Existence.unique_per_conduit_lineage)
    holder_id = bind(book, U6Holder, Existence.unique_per_conduit)
    root = book.conjure(dynamic=True, name="u6-root")
    out: Dict[str, Any] = {}
    lesser = root.create_lesser_conduit()
    try:
        holder = lesser.meld(spell_id=holder_id)
        lineage = holder.lineage
        out["setup_lineage_in_root_store"] = stored(root, lineage_id) is lineage
        out["setup_holder_in_lesser_store"] = stored(lesser, holder_id) is holder
        lesser.upgrade_to_normal("u6-upgraded")
        out["after_upgrade_holder_retained_in_upgraded_store"] = stored(lesser, holder_id) is holder
        root.cleanup()
        out["after_old_root_teardown_lineage_closes"] = lineage.closes
        out["after_old_root_teardown_retained_holder_closes"] = holder.closes
    finally:
        attempt(lesser.cleanup)
        attempt(root.cleanup)
    out["final_holder_closes"] = holder.closes
    out["final_lineage_closes"] = lineage.closes
    return out


def case_b7() -> Dict[str, Any]:
    """The lender is torn down while a borrower's per-conduit holder holds its contracted unique."""
    frame = "audit-b7"
    lender_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    resource_id = bind(lender_book, B7Resource, Existence.unique)
    lender = lender_book.conjure(dynamic=True, name="b7-lender")
    borrower_book = Spellbook(aetheric_frame=frame)
    holder_id = bind(borrower_book, B7Holder, Existence.unique_per_conduit)
    borrower = borrower_book.conjure(dynamic=True, name="b7-borrower")
    out: Dict[str, Any] = {}
    try:
        lender.link(borrower)
        with borrower.transaction("link", conduits=[borrower, lender]):
            borrower.add_spell_to_contract(spell_id=resource_id, conduit=lender, permissions="create")
        out["setup_contracts_valid"] = borrower.validate_contracts_and_define()
        holder = borrower.meld(spell_id=holder_id)
        resource = holder.dep
        out["setup_resource_is_lenders"] = lender.meld(spell_id=resource_id) is resource
        lender.cleanup()
        out["after_lender_teardown_resource_closes"] = resource.closes
        out["after_lender_teardown_holder_in_borrower_store"] = stored(borrower, holder_id) is holder
        ok, value = attempt(lambda: borrower.meld(spell_id=holder_id))
        out["after_lender_teardown_borrower_meld_holder"] = "same holder" if ok and value is holder else (
            "new holder" if ok else value)
        out["after_lender_teardown_holder_closes"] = holder.closes
    finally:
        ok, value = attempt(borrower.cleanup)
        out["borrower_cleanup"] = "ok" if ok else value
        attempt(lender.cleanup)
    out["final_holder_closes"] = holder.closes
    out["final_resource_closes"] = resource.closes
    return out


class C3Leaf(Closable):
    """`unique_per_conduit_cluster` instance (c3)."""


class R8Child(Closable):
    """`many` child of a lineage holder (r8)."""


class R8Holder(Closable):
    """`unique_per_conduit_lineage` holder first melded in a lesser's spellspace (r8)."""

    def __init__(self, child: R8Child) -> None:
        super().__init__()
        self.child = child


class R9Child(Closable):
    """`many` child of a cluster holder (r9)."""


class R9Holder(Closable):
    """`unique_per_conduit_cluster` holder first melded in a member's spellspace (r9)."""

    def __init__(self, child: R9Child) -> None:
        super().__init__()
        self.child = child


def case_c3() -> Dict[str, Any]:
    """A non-leader member root is torn down without leaving; the cluster then elects and unelects."""
    frame = "audit-c3"
    provider_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    leaf_id = bind(provider_book, C3Leaf, Existence.unique_per_conduit_cluster)
    provider = provider_book.conjure(dynamic=True, name="c3-leader")
    first_book = Spellbook(aetheric_frame=frame)
    first = first_book.conjure(dynamic=True, name="c3-member-1")
    second_book = Spellbook(aetheric_frame=frame)
    second = second_book.conjure(dynamic=True, name="c3-member-2")
    out: Dict[str, Any] = {}
    try:
        provider.link(first)
        provider.link(second)
        cloud = Spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("c3")
        for root in (provider, first, second):
            cloud.add_conduit_to_cluster(root, "c3")
        for root in (provider, first, second):
            cloud.refresh_cluster_shares_for_conduit(root)
        cluster = cloud.get_cluster("c3")
        cluster.elect_leader(provider.id)
        shared = first.meld(spell_id=leaf_id)
        second_id = second.id
        second.cleanup()
        out["after_member_teardown_cluster_still_lists_it"] = second_id in cluster.get_members()
        ok, value = attempt(cluster.unelect_leader)
        out["after_member_teardown_unelect"] = "ok" if ok else value
        ok, value = attempt(lambda: cluster.elect_leader(provider.id))
        out["after_member_teardown_elect"] = "ok" if ok else value
        ok, value = attempt(lambda: first.meld(spell_id=leaf_id))
        out["after_member_teardown_member_meld"] = "same leaf" if ok and value is shared else (
            "new instance" if ok else value)
    finally:
        attempt(second.cleanup)
        attempt(first.cleanup)
        attempt(provider.cleanup)
    return out


def case_r8() -> Dict[str, Any]:
    """A lineage holder first melded in a lesser's spellspace keeps its child until the lineage root ends."""
    book = Spellbook()
    child_id = bind(book, R8Child, Existence.many)
    holder_id = bind(book, R8Holder, Existence.unique_per_conduit_lineage)
    root = book.conjure(name="r8-root")
    out: Dict[str, Any] = {}
    try:
        lesser = root.create_lesser_conduit()
        with lesser.enter_spellspace() as space:
            holder = space.meld(spell_id=holder_id)
        child = holder.child
        out["after_space_exit_child_closes"] = child.closes
        lesser.cleanup()
        out["after_lesser_return_child_closes"] = child.closes
        out["root_serves_same_holder"] = root.meld(spell_id=holder_id) is holder
        out["child_in_root_store"] = child in list(stored(root, child_id) or [])
    finally:
        attempt(root.cleanup)
    out["final_child_closes"] = child.closes
    out["final_holder_closes"] = holder.closes
    return out


def case_r9() -> Dict[str, Any]:
    """A cluster holder first melded in a member's spellspace keeps its child until the leader ends."""
    frame = "audit-r9"
    provider_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    child_id = bind(provider_book, R9Child, Existence.many)
    holder_id = bind(provider_book, R9Holder, Existence.unique_per_conduit_cluster)
    provider = provider_book.conjure(dynamic=True, name="r9-leader")
    member_book = Spellbook(aetheric_frame=frame)
    member = member_book.conjure(dynamic=True, name="r9-member")
    out: Dict[str, Any] = {}
    try:
        provider.link(member)
        cloud = Spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("r9")
        for root in (provider, member):
            cloud.add_conduit_to_cluster(root, "r9")
        for root in (provider, member):
            cloud.refresh_cluster_shares_for_conduit(root)
        cloud.get_cluster("r9").elect_leader(provider.id)
        with member.enter_spellspace() as space:
            holder = space.meld(spell_id=holder_id)
        child = holder.child
        out["after_space_exit_child_closes"] = child.closes
        out["child_in_leader_store"] = child in list(stored(provider, child_id) or [])
        member.cleanup()
        out["after_member_teardown_child_closes"] = child.closes
        out["leader_serves_same_holder"] = provider.meld(spell_id=holder_id) is holder
    finally:
        attempt(member.cleanup)
        attempt(provider.cleanup)
    out["final_child_closes"] = child.closes
    out["final_holder_closes"] = holder.closes
    return out


CASES: List[Tuple[str, Callable[[], Dict[str, Any]]]] = [
    ("c1", case_c1),
    ("c2", case_c2),
    ("c3", case_c3),
    ("t3", case_t3),
    ("t4", case_t4),
    ("t4b", case_t4b),
    ("p5", case_p5),
    ("u6", case_u6),
    ("b7", case_b7),
    ("r8", case_r8),
    ("r9", case_r9),
]


def main() -> int:
    """Run each case in a fresh world and print its observations, one line per fact."""
    selected = set(sys.argv[1:])
    for name, case in CASES:
        if selected and name not in selected:
            continue
        reset_world()
        try:
            observations = case()
        except BaseException:
            print(f"{name}: CASE FAILED")
            traceback.print_exc(limit=6)
            continue
        for key, value in observations.items():
            print(f"{name}.{key} = {value}")
    reset_world()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
