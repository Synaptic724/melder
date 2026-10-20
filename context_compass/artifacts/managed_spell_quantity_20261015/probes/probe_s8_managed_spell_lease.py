"""S8 check (melder_0, 2026-10-16): ManagedSpellLease works as built (owner: "1. is fine leave it as is but just do
make sure it works fine"). Each case prints PASS or FAIL with what it saw; the last line counts them.

Run from a scratch directory: PYTHONPATH=<repo>/src:<repo> python -X gil=0 <this file>
"""
import traceback
from typing import Callable, List, Tuple

from melder import ManagedSpellLease, ReleaseManagedSpell
from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Parser:
    resets: List[int] = []
    built = 0

    def __init__(self) -> None:
        Parser.built += 1
        self.serial = Parser.built

    def reset(self) -> None:
        Parser.resets.append(self.serial)


class Other:
    pass


def fresh() -> None:
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    Parser.resets = []
    Parser.built = 0


def root_with(**options: object) -> Tuple[Spellbook, Conduit, str]:
    fresh()
    book = Spellbook()
    spell_id = book.bind(spell=Parser, existence=Existence.managed_spell_quantity, permissions="create",
                         managed_spell_reset_methods=["reset"], **options)
    return book, book.conjure(name="root"), spell_id


def pool_of(root: Conduit, spell_id: str):
    return root._creations.get_managed_quantity(spell_id)


def case_with_releases_on_exit() -> str:
    book, root, sid = root_with()
    pool = pool_of(root, sid)
    with root.managed_spell_meld(Parser) as parser:
        inside = (pool.count, pool.idle_count, pool.describe()["out_count"])
    after = (pool.count, pool.idle_count)
    again = root.meld(spell=Parser)
    ok = inside == (1, 0, 1) and after == (1, 1) and again is parser and Parser.resets == [parser.serial]
    root.cleanup(); book.cleanup()
    return f"{'PASS' if ok else 'FAIL'} with-exit: inside count/idle/out={inside}, after={after}, reused={again is parser}, resets={Parser.resets}"


def case_with_releases_on_exception() -> str:
    book, root, sid = root_with()
    pool = pool_of(root, sid)
    raised = None
    try:
        with root.managed_spell_meld(Parser):
            raise ValueError("boom")
    except ValueError as exc:
        raised = str(exc)
    seen = (pool.count, pool.idle_count)
    ok = raised == "boom" and seen == (1, 1)
    root.cleanup(); book.cleanup()
    return f"{'PASS' if ok else 'FAIL'} with-exception: propagated={raised!r}, count/idle after the block={seen}"


def case_managed_on_a_plain_meld() -> str:
    book, root, sid = root_with()
    pool = pool_of(root, sid)
    obj = root.meld(spell=Parser)
    lease = ReleaseManagedSpell().managed(obj)
    with lease as held:
        same = held is obj
    idle = pool.idle_count
    ok = isinstance(lease, ManagedSpellLease) and same and lease.released and idle == 1
    root.cleanup(); book.cleanup()
    return f"{'PASS' if ok else 'FAIL'} ReleaseManagedSpell().managed(obj): same object={same}, released={lease.released}, idle={idle}"


def case_release_once() -> str:
    book, root, sid = root_with()
    pool = pool_of(root, sid)
    lease = root.managed_spell_meld(Parser)
    lease.release()
    lease.release()
    try:
        lease.object
        object_raises = False
    except RuntimeError:
        object_raises = True
    try:
        with lease:
            pass
        enter_raises = False
    except RuntimeError:
        enter_raises = True
    idle = pool.idle_count
    ok = idle == 1 and len(Parser.resets) == 1 and object_raises and enter_raises
    root.cleanup(); book.cleanup()
    return (f"{'PASS' if ok else 'FAIL'} release-once: idle={idle}, resets={len(Parser.resets)}, "
            f"object raises after={object_raises}, with on a released lease raises={enter_raises}")


def case_limited_place_freed() -> str:
    book, root, sid = root_with(managed_spell_mode="limited_quantity", managed_spell_limit=1)
    with root.managed_spell_meld(Parser) as first:
        pass
    with root.managed_spell_meld(Parser) as second:
        pass
    ok = second is first and Parser.built == 1
    root.cleanup(); book.cleanup()
    return f"{'PASS' if ok else 'FAIL'} limited_quantity(1): second with-lease reuses the first object={second is first}, built={Parser.built}"


def case_lease_after_root_teardown() -> str:
    book, root, sid = root_with()
    lease = root.managed_spell_meld(Parser)
    root.cleanup()
    try:
        lease.release()
        message = "no error"
    except RuntimeError as exc:
        message = str(exc)
    ok = "torn down with its root" in message and lease.released
    book.cleanup()
    return f"{'PASS' if ok else 'FAIL'} release after root teardown: {message[:90]!r}, released={lease.released}"


def case_other_existence_refused() -> str:
    fresh()
    book = Spellbook()
    book.bind(spell=Other, existence=Existence.unique, permissions="create")
    root = book.conjure(name="root")
    try:
        root.managed_spell_meld(Other)
        message = "no error"
    except ValueError as exc:
        message = str(exc)
    ok = message.startswith("managed_spell_meld leases a managed spell")
    root.cleanup(); book.cleanup()
    return f"{'PASS' if ok else 'FAIL'} managed_spell_meld of a unique spell: {message[:80]!r}"


def case_staged_before_conjure() -> str:
    fresh()
    configuration = SpellbookConfiguration(aether_frame="default")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    book = Spellbook(aetheric_frame="default", configuration=configuration)
    active = book.bind(spell=Other, existence=Existence.managed_spell_quantity, permissions="create")
    index = book.find_spell_by_id(active).spell_index
    staged = book.bind_inactive(spell=Parser, spell_index=index, existence=Existence.managed_spell_quantity,
                                permissions="create", binding_name="parser", managed_spell_reset_methods=["reset"])
    root = book.conjure(dynamic=True, name="root")
    root.notch_spell(spell_index=index, spell=book._get_owned_spell(staged))
    pool = pool_of(root, staged)
    with root.managed_spell_meld(spell_id=staged) as parser:
        pass
    seen = (pool.count, pool.idle_count)
    ok = isinstance(parser, Parser) and seen == (1, 1)
    root.cleanup(); book.cleanup()
    return f"{'PASS' if ok else 'FAIL'} a version staged before conjure, notched in, leased with `with`: count/idle={seen}"


CASES: List[Callable[[], str]] = [
    case_with_releases_on_exit,
    case_with_releases_on_exception,
    case_managed_on_a_plain_meld,
    case_release_once,
    case_limited_place_freed,
    case_lease_after_root_teardown,
    case_other_existence_refused,
    case_staged_before_conjure,
]


if __name__ == "__main__":
    results = []
    for case in CASES:
        try:
            results.append(case())
        except Exception:
            results.append(f"FAIL {case.__name__}: {traceback.format_exc(limit=3)}")
    for line in results:
        print(line)
    print(f"{sum(line.startswith('PASS') for line in results)} of {len(results)} cases pass")
