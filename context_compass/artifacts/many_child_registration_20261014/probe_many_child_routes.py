"""
Probe: which holder lifetimes and first-meld routes dispose a holder's disposal-bearing `many` child
while the holder is still alive? (TASK-2026-10-14-prove_many_child_registration_bug)

Each case builds a fresh world (Aether reset), melds a holder FIRST through one route, ends that route's
scope, reads the holder again from the scope that owns it, then tears the owning root down. Reported:
    same       - the owning scope returns the same holder object after the route's scope ended
    at_exit    - times the child's disposal method had run right after the route's scope ended (defect if > 0
                 while `same` is True)
    at_end     - times it had run once the owning root was torn down (1 is the corrected behaviour)
    built      - Child constructions in the case

Run on a copy of `src` and of `tests/_frame_posture_test_support.py` (a conjure writes its cache under the
package root):
    PYTHONPATH=<copy>/src:<copy> PYTHONDONTWRITEBYTECODE=1 PYTHON_GIL=0 python probe_many_child_routes.py
"""
import sys
import traceback
from typing import Callable, Dict, List, Optional, Tuple

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Child:
    """`many` dependency whose one disposal method counts its runs."""

    built = 0

    def __init__(self) -> None:
        """Count the construction and start open."""
        Child.built += 1
        self.closes = 0

    def close(self) -> None:
        """Disposal method Melder calls when the store recording this child is disposed."""
        self.closes += 1


class Other:
    """`many` dependency without disposal methods; the override case supplies it."""

    def __init__(self) -> None:
        """Mark construction."""
        self.marker = "built"


class HolderU:
    """`unique` holder of one Child."""

    def __init__(self, child: Child) -> None:
        """Keep the child."""
        self.child = child


class HolderPC:
    """`unique_per_conduit` holder of one Child."""

    def __init__(self, child: Child) -> None:
        """Keep the child."""
        self.child = child


class HolderL:
    """`unique_per_conduit_lineage` holder of one Child."""

    def __init__(self, child: Child) -> None:
        """Keep the child."""
        self.child = child


class HolderS:
    """`unique_per_spell_space` holder of one Child (control)."""

    def __init__(self, child: Child) -> None:
        """Keep the child."""
        self.child = child


class HolderUO:
    """`unique` holder of one Child and one Other (the override case supplies Other)."""

    def __init__(self, child: Child, other: Other) -> None:
        """Keep both."""
        self.child = child
        self.other = other


class Outer:
    """`unique_per_conduit` consumer of a `unique` HolderU (nested case)."""

    def __init__(self, inner: HolderU) -> None:
        """Keep the inner holder."""
        self.inner = inner


class HolderC:
    """`unique_per_conduit_cluster` holder of one Child."""

    def __init__(self, child: Child) -> None:
        """Keep the child."""
        self.child = child


def reset_world() -> None:
    """Fresh Aether, as the component tests do."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    Child.built = 0


def automatic_book(specialize: bool = False) -> Spellbook:
    """A fresh world and one automatic Spellbook (optionally with the singleton specializer on)."""
    reset_world()
    if not specialize:
        return Spellbook()
    configuration = SpellbookConfiguration()
    configuration.with_defaults()
    configuration.set_property("generalized_singleton_specialization_enabled", True)
    return Spellbook(configuration=configuration)


def dynamic_configuration(frame: Optional[str] = None) -> SpellbookConfiguration:
    """A dynamic configuration with one phase worker."""
    configuration = SpellbookConfiguration() if frame is None else SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def bind_child(book: Spellbook) -> str:
    """Bind Child as a disposal-bearing many spell."""
    return book.bind(spell=Child, existence=Existence.many, disposal_method_names=["close"])


Result = Tuple[bool, int, int, int]


def case_unique_via_lesser() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderU, existence=Existence.unique)
    root = book.conjure(name="probe_root")
    try:
        lesser = root.create_lesser_conduit()
        first = lesser.meld(spell_id=holder_id)
        lesser.cleanup()
        at_exit = first.child.closes
        same = root.meld(spell_id=holder_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_unique_via_root_spellspace() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderU, existence=Existence.unique)
    root = book.conjure(name="probe_root")
    try:
        with root.enter_spellspace() as space:
            first = space.meld(spell_id=holder_id)
        at_exit = first.child.closes
        same = root.meld(spell_id=holder_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_unique_via_lesser_spellspace() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderU, existence=Existence.unique)
    root = book.conjure(name="probe_root")
    try:
        lesser = root.create_lesser_conduit()
        with lesser.enter_spellspace() as space:
            first = space.meld(spell_id=holder_id)
        at_exit = first.child.closes
        same = lesser.meld(spell_id=holder_id) is first and root.meld(spell_id=holder_id) is first
        lesser.cleanup()
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_per_conduit_via_root_spellspace() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderPC, existence=Existence.unique_per_conduit)
    root = book.conjure(name="probe_root")
    try:
        with root.enter_spellspace() as space:
            first = space.meld(spell_id=holder_id)
        at_exit = first.child.closes
        same = root.meld(spell_id=holder_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_per_conduit_via_lesser_spellspace() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderPC, existence=Existence.unique_per_conduit)
    root = book.conjure(name="probe_root")
    try:
        lesser = root.create_lesser_conduit()
        with lesser.enter_spellspace() as space:
            first = space.meld(spell_id=holder_id)
        at_exit = first.child.closes
        same = lesser.meld(spell_id=holder_id) is first
        lesser.cleanup()
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_lineage_via_lesser() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderL, existence=Existence.unique_per_conduit_lineage)
    root = book.conjure(name="probe_root")
    try:
        lesser = root.create_lesser_conduit()
        first = lesser.meld(spell_id=holder_id)
        lesser.cleanup()
        at_exit = first.child.closes
        same = root.meld(spell_id=holder_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_lineage_via_root_spellspace() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderL, existence=Existence.unique_per_conduit_lineage)
    root = book.conjure(name="probe_root")
    try:
        with root.enter_spellspace() as space:
            first = space.meld(spell_id=holder_id)
        at_exit = first.child.closes
        same = root.meld(spell_id=holder_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_nested_unique_under_per_conduit_via_lesser() -> Result:
    book = automatic_book()
    bind_child(book)
    inner_id = book.bind(spell=HolderU, existence=Existence.unique)
    outer_id = book.bind(spell=Outer, existence=Existence.unique_per_conduit)
    root = book.conjure(name="probe_root")
    try:
        lesser = root.create_lesser_conduit()
        outer = lesser.meld(spell_id=outer_id)
        first = outer.inner
        lesser.cleanup()
        at_exit = first.child.closes
        same = root.meld(spell_id=inner_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_unique_override_first_build_via_lesser() -> Result:
    book = automatic_book()
    bind_child(book)
    book.bind(spell=Other, existence=Existence.many)
    holder_id = book.bind(spell=HolderUO, existence=Existence.unique)
    root = book.conjure(name="probe_root")
    try:
        lesser = root.create_lesser_conduit()
        first = lesser.meld(spell_id=holder_id, override={"other": Other()})
        lesser.cleanup()
        at_exit = first.child.closes
        same = root.meld(spell_id=holder_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_unique_via_lesser_specialized() -> Result:
    book = automatic_book(specialize=True)
    bind_child(book)
    holder_id = book.bind(spell=HolderU, existence=Existence.unique)
    root = book.conjure(name="probe_root")
    try:
        lesser = root.create_lesser_conduit()
        first = lesser.meld(spell_id=holder_id)
        lesser.cleanup()
        at_exit = first.child.closes
        same = all(root.meld(spell_id=holder_id) is first for _ in range(5))
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_unique_via_borrower() -> Result:
    reset_world()
    configuration = dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    bind_child(owner_book)
    holder_id = owner_book.bind(spell=HolderU, existence=Existence.unique, permissions="create")
    borrower_book = Spellbook(configuration=configuration)
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(spell_id=holder_id, conduit=owner, permissions="create")
        borrower.validate_contracts_and_define()
        first = borrower.meld(spell_id=holder_id)
        borrower.cleanup()
        at_exit = first.child.closes
        same = owner.meld(spell_id=holder_id) is first
    finally:
        owner.cleanup()
    return same, at_exit, first.child.closes, Child.built


def case_cluster_via_member() -> Result:
    reset_world()
    frame = "probe-cluster"
    provider_book = Spellbook(aetheric_frame=frame, configuration=dynamic_configuration(frame))
    bind_child(provider_book)
    holder_id = provider_book.bind(spell=HolderC, existence=Existence.unique_per_conduit_cluster, permissions="create")
    provider = provider_book.conjure(dynamic=True, name="provider")
    member_book = Spellbook(aetheric_frame=frame)
    member = member_book.conjure(dynamic=True, name="member")
    try:
        provider.link(member)
        cloud = provider._spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("probe")
        for root in (provider, member):
            cloud.add_conduit_to_cluster(root, "probe")
        for root in (provider, member):
            cloud.refresh_cluster_shares_for_conduit(root)
        cloud.get_cluster("probe").elect_leader(provider.id)
        first = member.meld(spell_id=holder_id)
        member.cleanup()
        at_exit = first.child.closes
        same = provider.meld(spell_id=holder_id) is first
    finally:
        provider.cleanup()
    return same, at_exit, first.child.closes, Child.built


def control_unique_at_root() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderU, existence=Existence.unique)
    root = book.conjure(name="probe_root")
    try:
        first = root.meld(spell_id=holder_id)
        lesser = root.create_lesser_conduit()
        lesser.meld(spell_id=holder_id)
        lesser.cleanup()
        with root.enter_spellspace() as space:
            space.meld(spell_id=holder_id)
        at_exit = first.child.closes
        same = root.meld(spell_id=holder_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def control_per_conduit_at_root() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderPC, existence=Existence.unique_per_conduit)
    root = book.conjure(name="probe_root")
    try:
        first = root.meld(spell_id=holder_id)
        with root.enter_spellspace() as space:
            space.meld(spell_id=holder_id)
        at_exit = first.child.closes
        same = root.meld(spell_id=holder_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def control_per_conduit_at_lesser() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderPC, existence=Existence.unique_per_conduit)
    root = book.conjure(name="probe_root")
    try:
        lesser = root.create_lesser_conduit()
        first = lesser.meld(spell_id=holder_id)
        same = lesser.meld(spell_id=holder_id) is first
        lesser.cleanup()
        at_exit = first.child.closes
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def control_lineage_at_root() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderL, existence=Existence.unique_per_conduit_lineage)
    root = book.conjure(name="probe_root")
    try:
        first = root.meld(spell_id=holder_id)
        lesser = root.create_lesser_conduit()
        lesser.meld(spell_id=holder_id)
        lesser.cleanup()
        at_exit = first.child.closes
        same = root.meld(spell_id=holder_id) is first
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


def control_spellspace_holder() -> Result:
    book = automatic_book()
    bind_child(book)
    holder_id = book.bind(spell=HolderS, existence=Existence.unique_per_spell_space)
    root = book.conjure(name="probe_root")
    try:
        with root.enter_spellspace() as space:
            first = space.meld(spell_id=holder_id)
            same = space.meld(spell_id=holder_id) is first
        at_exit = first.child.closes
    finally:
        root.cleanup()
    return same, at_exit, first.child.closes, Child.built


CASES: List[Tuple[str, Callable[[], Result]]] = [
    ("unique_via_lesser", case_unique_via_lesser),
    ("unique_via_root_spellspace", case_unique_via_root_spellspace),
    ("unique_via_lesser_spellspace", case_unique_via_lesser_spellspace),
    ("per_conduit_via_root_spellspace", case_per_conduit_via_root_spellspace),
    ("per_conduit_via_lesser_spellspace", case_per_conduit_via_lesser_spellspace),
    ("lineage_via_lesser", case_lineage_via_lesser),
    ("lineage_via_root_spellspace", case_lineage_via_root_spellspace),
    ("nested_unique_under_per_conduit_via_lesser", case_nested_unique_under_per_conduit_via_lesser),
    ("unique_override_first_build_via_lesser", case_unique_override_first_build_via_lesser),
    ("unique_via_lesser_specialized", case_unique_via_lesser_specialized),
    ("unique_via_borrower", case_unique_via_borrower),
    ("cluster_via_member", case_cluster_via_member),
    ("control_unique_at_root", control_unique_at_root),
    ("control_per_conduit_at_root", control_per_conduit_at_root),
    ("control_per_conduit_at_lesser", control_per_conduit_at_lesser),
    ("control_lineage_at_root", control_lineage_at_root),
    ("control_spellspace_holder", control_spellspace_holder),
]


def main() -> int:
    """Run every case and write one line each; the lines are the evidence."""
    failures = 0
    for name, case in CASES:
        try:
            same, at_exit, at_end, built = case()
            sys.stdout.write(f"{name}: same={same} at_exit={at_exit} at_end={at_end} built={built}\n")
        except BaseException as error:  # probe: report and continue
            failures += 1
            first_line = str(error).splitlines()[0] if str(error) else ""
            sys.stdout.write(f"{name}: ERROR {type(error).__name__}: {first_line[:300]}\n")
            traceback.print_exc(limit=3, file=sys.stderr)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
