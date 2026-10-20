"""S8 side probe (melder_0, 2026-10-16): is a notched-in existing-object version registered in its owner store,
so that root teardown runs its disposal methods? Staged after conjure (today's wired path).

Run from a scratch directory: PYTHONPATH=<repo>/src:<repo> python -X gil=0 <this file>
"""
from typing import List

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

CLOSED: List[str] = []


class Resource:
    def __init__(self, label: str) -> None:
        self.label = label

    def close(self) -> None:
        CLOSED.append(self.label)


def fresh() -> None:
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def dynamic_book() -> Spellbook:
    configuration = SpellbookConfiguration(aether_frame="default")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame="default", configuration=configuration)


def case(notch: bool) -> str:
    fresh()
    CLOSED.clear()
    book = dynamic_book()
    first, second = Resource("v1"), Resource("v2")
    id_a = book.bind(spell=first, existence=Existence.unique, permissions="create", binding_name="res",
                     disposal_method_names=["close"])
    root = book.conjure(dynamic=True, name="root")
    index = book.find_spell_by_id(id_a).spell_index
    id_b = root.bind_inactive(spell=second, spell_index=index, existence=Existence.unique, permissions="create",
                              binding_name="res_v2", disposal_method_names=["close"])
    parked = book._get_owned_spell(id_b)
    in_store_before = root._creations._creations.get(id_b) is not None
    if notch:
        root.notch_spell(spell_index=index, spell=parked)
    melded = root.meld(spell_id=id_b if notch else id_a)
    in_store_after = root._creations._creations.get(id_b) is not None
    root.cleanup()
    book.cleanup()
    return (f"notch={notch}: meld -> {melded.label}; v2 in store before notch={in_store_before}, "
            f"after meld={in_store_after}; closed at teardown={CLOSED}")


if __name__ == "__main__":
    print(case(False))
    print(case(True))
