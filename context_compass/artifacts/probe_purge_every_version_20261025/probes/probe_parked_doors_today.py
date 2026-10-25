"""Probe (melder_1, 2026-10-25; STORY-2026-10-25-probe_and_purge_reach_every_version): what purge and the
live-creation probes answer today for the cases whose answer the tests must pin as it is. Public calls only, one
case per process:

    python probe_parked_doors_today.py <case>

Cases: existing (F9), instance (F14), spell_object (F22), unstamped (F17), split (F19), transfer (F20),
borrowers (F10), active_existing (purge of an active existing object, for F9's contrast).
Each world is dynamic, disposal names ["cleanup"], caching off; versions are `version_of(Res, version=2)`, bound bare
at the class's own address, so the probe stays valid under the S2 story's option (A).
"""
import sys
from typing import Any, List

import melder as md
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spell import Spell

from tests._spell_identity_test_support import version_of  # the runner puts the repository root on PYTHONPATH

JOURNAL: List[str] = []


class Res:
    """A version-1 resource; its cleanup records into JOURNAL."""

    def cleanup(self) -> None:
        """Record one disposal with the version's tag."""
        JOURNAL.append("cleanup %s %x" % (type(self).__dict__.get("version", 1), id(self) & 0xFFFFF))


def show(label: str, call) -> Any:
    """Print what `call` returns, or the type and first line of what it raises; return the result or None."""
    try:
        result = call()
        print("  %-62s -> %r" % (label, result))
        return result
    except Exception as error:
        first = str(error).splitlines()[0] if str(error) else ""
        print("  %-62s -> raises %s: %s" % (label, type(error).__name__, first[:150]))
        return None


def book(frame: str, *, first: bool = True) -> md.Spellbook:
    """A Book with disposal names ["cleanup"]; the frame's first Book makes it dynamic with caching off."""
    configuration = SpellbookConfiguration(frame)
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["cleanup"])
    configuration.load_default_dictionary()
    spellbook = md.Spellbook(aetheric_frame=frame, configuration=configuration)
    if first:
        spellbook.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                         system_caching_enabled=False)
    return spellbook


def world(frame: str, existence: str = "unique"):
    """Res active, `version_of(Res, version=2)` parked on its index; return (book, root, v1_id, v2_id, index)."""
    lender = book(frame)
    v1_id = lender.bind(spell=Res, existence=existence, permissions="create")
    root = lender.conjure(dynamic=True, name="root_" + frame)
    index = root.get_spell_by_spell_id(v1_id).spell_index
    v2_id = root.bind_inactive(spell=version_of(Res, version=2), spell_index=index, existence=existence,
                               permissions="create")
    return lender, root, v1_id, v2_id, index


def case_instance() -> None:
    """F14: an instance of a parked version given to purge with purge_all=False."""
    _, root, v1_id, v2_id, index = world("instance")
    obj = root.meld(spell_id=v1_id)
    root.notch_spell(spell_index=index, spell_id=v2_id)
    show("purge(spell=<v1 object>, purge_all=False)", lambda: root.purge(spell=obj, purge_all=False))
    show("purge(spell=<v1 object>) (purge_all=True)", lambda: root.purge(spell=obj))
    show("journal", lambda: list(JOURNAL))


def case_spell_object() -> None:
    """F22: the Spell object get_spell_by_spell_id returns, given as `spell`."""
    _, root, v1_id, v2_id, index = world("spell_object")
    root.meld(spell_id=v1_id)
    v1 = root.get_spell_by_spell_id(v1_id)
    show("has_live_creation(spell=<v1 Spell>) while active", lambda: root.has_live_creation(spell=v1))
    show("purge(spell=<v1 Spell>) while active", lambda: root.purge(spell=v1))
    show("has_live_creation(spell=<v1 id>) while active", lambda: root.has_live_creation(spell=v1_id))


def case_existing() -> None:
    """F9: a parked existing-object version, never active; then notched to and back."""
    lender = book("existing")
    first = Res()
    v1_id = lender.bind(spell=first, existence="unique", permissions="create")
    root = lender.conjure(dynamic=True, name="root_existing")
    index = root.get_spell_by_spell_id(v1_id).spell_index
    second = version_of(Res, version=2)()
    v2_id = root.bind_inactive(spell=second, spell_index=index, existence="unique", permissions="create")
    show("describe(spell=<v1 id>) active existing", lambda: root.describe_live_creation_status(spell=v1_id))
    show("describe(spell=<v2 id>) parked existing", lambda: root.describe_live_creation_status(spell=v2_id))
    show("notch to v2", lambda: root.notch_spell(spell_index=index, spell_id=v2_id).spell_id == v2_id)
    show("meld(spell_id=<v2>) is the supplied object", lambda: root.meld(spell_id=v2_id) is second)
    show("describe(spell=<v2 id>) active existing", lambda: root.describe_live_creation_status(spell=v2_id))
    show("purge(spell_id=<v2>) active existing", lambda: root.purge(spell_id=v2_id))
    show("meld(spell_id=<v2>) after the purge is the supplied object", lambda: root.meld(spell_id=v2_id) is second)
    show("describe(spell=<v2 id>) after the purge", lambda: root.describe_live_creation_status(spell=v2_id))
    show("journal", lambda: list(JOURNAL))


def case_unstamped() -> None:
    """F17: a unique version staged before conjure whose owner stamp raised at conjure."""
    lender = book("unstamped")
    v1_id = lender.bind(spell=Res, existence="unique", permissions="create")
    index = lender.find_spell_by_spell_id(v1_id).spell_index
    v2_id = lender.bind_inactive(spell=version_of(Res, version=2), spell_index=index, existence="unique",
                                 permissions="create")
    original = Spell._add_owned_conduit

    def refusing(self, *args, **kwargs):
        if self.spell_id == v2_id:
            raise RuntimeError("probe: the owner stamp raised")
        return original(self, *args, **kwargs)

    Spell._add_owned_conduit = refusing
    try:
        root = lender.conjure(dynamic=True, name="root_unstamped")
    finally:
        Spell._add_owned_conduit = original
    show("v2 _owner_creations after conjure", lambda: lender.find_spell_by_spell_id(v2_id)._owner_creations)
    show("notch to v2", lambda: root.notch_spell(spell_index=index, spell_id=v2_id).spell_id == v2_id)
    show("has_live_creation(spell=<v2>) active, unstamped", lambda: root.has_live_creation(spell=v2_id))
    show("purge(spell_id=<v2>) active, unstamped", lambda: root.purge(spell_id=v2_id))
    show("meld(spell_id=<v2>) active, unstamped", lambda: type(root.meld(spell_id=v2_id)).__name__)


def case_split() -> None:
    """F19: a version built while active, parked, then split into an index of its own."""
    _, root, v1_id, v2_id, index = world("split")
    root.notch_spell(spell_index=index, spell_id=v2_id)
    root.meld(spell_id=v2_id)
    root.notch_spell(spell_index=index, spell_id=v1_id)
    minted = show("remove_from_spell_index(spell_id=<v2>)",
                  lambda: root.remove_from_spell_index(spell_id=v2_id, source_index=index))
    show("get_spell_by_spell_id(<v2>).spell_index is not the source",
         lambda: root.get_spell_by_spell_id(v2_id).spell_index is not index)
    show("has_live_creation(spell=<v2>) split, parked", lambda: root.has_live_creation(spell=v2_id))
    show("purge(spell_id=<v2>) split, parked", lambda: root.purge(spell_id=v2_id))


def case_transfer() -> None:
    """F20: v1 built, notched to v2, then the index transferred to another root (move_creations default)."""
    _, root, v1_id, v2_id, index = world("transfer")
    root.meld(spell_id=v1_id)
    root.notch_spell(spell_index=index, spell_id=v2_id)
    root.meld(spell_id=v2_id)
    target_book = book("transfer", first=False)  # the same frame: a transfer is same-frame
    target_book.bind(spell=version_of(Res, version=9), existence="unique", permissions="create",
                     binding_name="anchor")
    target = target_book.conjure(dynamic=True, name="target_transfer")
    show("transfer_spell_ownership(spell=<v2>, target)",
         lambda: sorted(root.transfer_spell_ownership(spell=v2_id, target_conduit=target).keys()))
    for name, conduit in (("source", root), ("target", target)):
        show("%s has_live_creation(spell=<v1>) (parked)" % name, lambda c=conduit: c.has_live_creation(spell=v1_id))
        show("%s has_live_creation(spell=<v2>) (active)" % name, lambda c=conduit: c.has_live_creation(spell=v2_id))


def case_borrowers() -> None:
    """F10: an index-link borrower and a version-grant borrower after the lender notches away from v1."""
    lender, root, v1_id, v2_id, index = world("borrowers", existence="unique")
    linked = book("borrowers", first=False).conjure(dynamic=True, name="index_borrower")
    root.link(linked)
    linked.add_index_to_contract(index=index, conduit=root, permissions="create")
    granted = book("borrowers", first=False).conjure(dynamic=True, name="grant_borrower")
    root.link(granted)
    granted.add_spell_to_contract(spell_id=v1_id, conduit=root, permissions="create")
    obj = linked.meld(spell_id=v1_id)
    show("grant borrower meld(spell_id=<v1>) is the same unique object", lambda: granted.meld(spell_id=v1_id) is obj)
    root.notch_spell(spell_index=index, spell_id=v2_id)
    for name, conduit in (("index", linked), ("grant", granted), ("lender", root)):
        show("%s has_live_creation(spell=<v1>) (parked)" % name, lambda c=conduit: c.has_live_creation(spell=v1_id))
        show("%s purge(spell_id=<v1>) (parked)" % name, lambda c=conduit: c.purge(spell_id=v1_id))


def case_active_existing() -> None:
    """Contrast for F9: purge of an ACTIVE existing-object version that was registered at conjure."""
    lender = book("active_existing")
    first = Res()
    v1_id = lender.bind(spell=first, existence="unique", permissions="create")
    root = lender.conjure(dynamic=True, name="root_active_existing")
    show("describe(spell=<v1>) active existing", lambda: root.describe_live_creation_status(spell=v1_id))
    show("purge(spell_id=<v1>) active existing", lambda: root.purge(spell_id=v1_id))
    show("meld(spell_id=<v1>) after the purge is the supplied object", lambda: root.meld(spell_id=v1_id) is first)
    show("journal", lambda: list(JOURNAL))


def main() -> None:
    """Run the case named on the command line."""
    case = sys.argv[1]
    print("case %s" % case)
    globals()["case_" + case]()


if __name__ == "__main__":
    main()
