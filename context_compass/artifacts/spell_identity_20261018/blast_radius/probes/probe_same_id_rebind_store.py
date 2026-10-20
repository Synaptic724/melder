"""S3 evidence (mirror, S1+S2 digest): does a slotted store entry kept under a spell_id reach a rebind of the same
class under another existence? Cases: unique -> unique_per_conduit on a root; unique_per_conduit -> many; unique ->
unique (control, the 2026-10-03 surviving-product ruling)."""
import sys
sys.path.insert(0, "src")
sys.path.insert(0, ".")
from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.aether.conduit.test_conduit_component_creations import _make_spellbook


def fresh() -> None:
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()


def case(first: str, second: str) -> str:
    fresh()

    class Widget:
        def __init__(self) -> None:
            self.marker = object()

    book = _make_spellbook(disposal=False)
    root = book.conjure(dynamic=True, name=f"probe-{first}-{second}")
    try:
        sid1 = root.bind(spell=Widget, existence=first)
        obj1 = root.meld(spell_id=sid1)
        root.cleanup_spell(spell=root.get_spell_by_spell_id(sid1))
        sid2 = root.bind(spell=Widget, existence=second)
        obj2 = root.meld(spell_id=sid2)
        obj3 = root.meld(spell_id=sid2)
        return (f"{first:>20} -> {second:<20} same_id={sid1 == sid2} second_meld_is_old_object={obj2 is obj1} "
                f"two_melds_same_object={obj2 is obj3}")
    finally:
        root.permanent_cleanup()


for first, second in (("unique", "unique"), ("unique", "unique_per_conduit"), ("unique_per_conduit", "unique"),
                      ("unique_per_conduit", "many"), ("many", "unique_per_conduit")):
    try:
        print(case(first, second))
    except Exception as exc:  # probe: report and go on
        print(f"{first:>20} -> {second:<20} RAISED {type(exc).__name__}: {str(exc)[:160]}")
