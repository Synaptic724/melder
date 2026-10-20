"""
Side probe for TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1, 2026-10-16).

Read-only on src/; run from the repository root with PYTHONPATH=src. One dynamic Book, no links: a `many` consumer
P(dep: Dep) and its `many` dependency Dep; the Book notches Dep to Dep2(Dep). Does P's next meld build with Dep2,
keep Dep, or fail - when P was melded before the notch (warm) and when it was not (cold)?
"""
import sys

from melder import Aether, Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Dep:
    def tag(self) -> str:
        return "d1"


class Dep2(Dep):
    def tag(self) -> str:
        return "d2"


class P:
    def __init__(self, dep: Dep) -> None:
        self.dep = dep


def run(warm: bool) -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    frame = "warm" if warm else "cold"
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                system_caching_enabled=False)
    dep_id = book.bind(spell=Dep, existence=Existence.many, permissions="create")
    p_id = book.bind(spell=P, existence=Existence.many, permissions="create")
    root = book.conjure(dynamic=True, name=f"{frame}_root")
    if warm:
        print(f"[{frame}] before notch: P.dep -> {root.meld(spell=P).dep.tag()}")
    index = book.find_spell_by_id(dep_id).spell_index
    new_id = root.bind_inactive(spell=Dep2, spell_index=index, existence=Existence.many, permissions="create")
    root.notch_spell(spell_index=index, spell=book._inactive_spells[new_id])
    state = book._spell_system_states.get_by_index_id(book.find_spell_by_id(p_id).spell_index.id)
    print(f"[{frame}] after notch: P lineage {state.validity.name} {sorted(f.name for f in state.flags)} "
          f"bookflag={book._spellbook_validation_required}")
    for attempt in (1, 2):
        try:
            print(f"[{frame}] meld {attempt} after notch: P.dep -> {root.meld(spell=P).dep.tag()}")
        except Exception as exc:
            print(f"[{frame}] meld {attempt} after notch: {type(exc).__name__}: {' '.join(str(exc).split())[:300]}")
    root.cleanup()


if __name__ == "__main__":
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()}")
    run(warm=True)
    run(warm=False)
