"""Probe (melder_0, 2026-11-28; EPIC-2026-10-17-correctness_defects, item C9, found while testing C8 on #346): can
an index-link borrower meld the version its lender notched to, when the lender staged it after conjure and never
melded it?

One dynamic frame with caching off. The lender binds Resource (version 1) and conjures; after conjure it stages
version 2 on the same index with `bind_inactive` (new code, same name and binding, so the same address). A borrower
root of the frame links to the lender and borrows the index (`add_index_to_contract`), and melds version 1. The
lender notches to version 2. Then the borrower melds version 2 one way, per run:
  by_id         `borrower.meld(spell_id=<version 2's spell_id>)`
  by_class      `borrower.meld(Resource)`
  by_name       `borrower.meld("Resource")`
  lender_first  the lender melds version 2 first, then the borrower by spell_id
Before the borrower's meld the probe prints both Books' `_spellbook_validation_required` flags - the flag that sends a
meld through the meld-time validation gate, which compiles a version the notch compiled only through Phase 4. Every
read is internal, for the diagnosis; the steps are public calls.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_borrower_meld_after_lender_notch.py
"""
from typing import Callable, Dict

from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Resource:
    """Version 1 of the borrowed index, bound bare before conjure."""

    version: int = 1


def resource_version_2() -> type:
    """Version 2: new code under Resource's own name and module, so it is staged at version 1's address."""
    return type("Resource", (), {"version": 2, "__module__": __name__, "__qualname__": "Resource",
                                 "__doc__": "Version 2 of the borrowed index."})


def book(*, first: bool) -> Spellbook:
    """A Book of the default frame with one phase worker; the first settles the frame dynamic, caching off."""
    configuration = SpellbookConfiguration("default")
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    new_book = Spellbook(aetheric_frame="default", configuration=configuration)
    if first:
        new_book.configure_aether_frame(
            system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
        )
    return new_book


def run(form: str) -> None:
    """Build the lender and its borrower, notch the lender to version 2, and meld it from the borrower one way."""
    lender_book = book(first=True)
    v1_id = lender_book.bind(spell=Resource, existence=Existence.unique, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    index = lender.get_spell_by_spell_id(v1_id).spell_index
    v2_id = lender.bind_inactive(spell=resource_version_2(), spell_index=index, existence=Existence.unique,
                                 permissions="create")
    borrower: Conduit = book(first=False).conjure(dynamic=True, name="borrower")
    lender.link(borrower)
    borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    print(f"{form}: the borrower melds version 1 before the notch: version {borrower.meld(spell_id=v1_id).version}")
    lender.notch_spell(spell_index=index, spell_id=v2_id)
    print(f"{form}: after the notch, validation_required - lender Book "
          f"{lender_book._spellbook_validation_required}, borrower Book "
          f"{borrower.spellbook._spellbook_validation_required}")
    melds: Dict[str, Callable[[], object]] = {
        "by_id": lambda: borrower.meld(spell_id=v2_id),
        "by_class": lambda: borrower.meld(Resource),
        "by_name": lambda: borrower.meld("Resource"),
        "lender_first": lambda: (lender.meld(spell_id=v2_id), borrower.meld(spell_id=v2_id))[1],
    }
    try:
        print(f"{form}: the borrower builds version {melds[form]().version}")
    except RuntimeError as error:
        print(f"{form}: the borrower's meld raised {type(error).__name__}: {error}")
    borrower.cleanup()
    lender.cleanup()


def main() -> None:
    """Run every form, each in a fresh world (Aether and Nexus reset between runs)."""
    from melder.aether.aether import Aether
    from melder.nexus.nexus import Nexus

    for form in ("by_id", "by_class", "by_name", "lender_first"):
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether
        run(form)


main()
