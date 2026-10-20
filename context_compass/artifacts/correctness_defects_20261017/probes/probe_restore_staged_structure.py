"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A5): does a restore rebuild the structure
a world with staged versions recorded?

Each case records a dynamic world with the Crystallizer active, seals and flushes a checkpoint into a scratch cache,
resets every world singleton (a fresh boot), reloads the checkpoint and restores it with `load_checkpoint`.
  R1  English active, French staged on its index under the SAME binding signature: the restored frame's claim.
  R2  English active (Greeter, 'english'), French staged under (Greeter, 'french') and then separated into its own
      index with `remove_from_spell_index`: is French rebuilt?
  R3  as R2, then French notched active inside its minted index: is the world rebuilt?
It prints the report's status, built counts and shortfalls, and the restored Book's structure.

Read-only on src/: run from this folder with the repository's src first on sys.path; the cache goes under TMPDIR:
    PYTHONPATH=<repo>/src:<repo> python -X gil=0 probes/probe_restore_staged_structure.py
"""
import os
import pathlib
import tempfile

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.asset_management import crystallizer_cache
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

from restore_targets import English, French, Greeter

CACHE = pathlib.Path(tempfile.mkdtemp(prefix="m0_restore_probe_", dir=os.environ.get("TMPDIR")))
crystallizer_cache.CrystallizerCache.resolve_cache_root_path = staticmethod(lambda: CACHE)


def boot() -> Crystallizer:
    """Reset every world singleton and return a freshly activated Crystallizer."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def recorded_book() -> Spellbook:
    """A dynamic Book with its configuration finalized first (the recorded lane's discipline)."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(configuration=configuration)


def restore(crystallizer: Crystallizer) -> dict:
    """Seal, flush, boot fresh, reload and restore; return the report."""
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    rebooted = boot()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    return rebooted.load_checkpoint(checkpoint_id)


def show(report: dict) -> None:
    """Print the report's status, counts and shortfalls."""
    print(f"    restore status: {report.get('status')}; built: {report.get('built_counts')}")
    for shortfall in report.get("shortfalls", []) or []:
        print(f"    shortfall: {shortfall}")


def live_book() -> Spellbook:
    """The Book of the rebuilt root conduit named "root" in the default frame."""
    return Spellbook._aether.get_root_conduit_by_name("root").spellbook


def classes(book: Spellbook) -> str:
    """Name the rebuilt Book's active and parked versions by class."""
    active = sorted(spell.spell.__name__ for spell in book._spells.values())
    parked = sorted(spell.spell.__name__ for spell in book._inactive_spells.values())
    return f"active={active} parked={parked}"


def r1() -> None:
    """Same signature: what the restored frame claims."""
    print("R1 English active and French staged under the same signature (Greeter, 'greeter')")
    crystallizer = boot()
    book = recorded_book()
    english_id = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence=Existence.many,
                           permissions="create")
    conduit = book.conjure(dynamic=True, name="root")
    english = book._spells_by_id[english_id]
    conduit.bind_inactive(spell=French, spell_index=english.spell_index, spellframe=Greeter, binding_name="greeter",
                          existence=Existence.many, permissions="create")
    report = restore(crystallizer)
    show(report)
    rebuilt = live_book()
    key = next(iter(rebuilt._spells.values()))._key
    holder = rebuilt._aetheric_frame.get_lookup(key)
    names = {spell.spell_id: spell.spell.__name__ for spell in rebuilt._spells.values()}
    print(f"    rebuilt Book: {classes(rebuilt)}; frame claim {key}: {names.get(holder, holder)}")


def r2() -> None:
    """French separated into its own index before the checkpoint."""
    print("R2 French staged under (Greeter, 'french'), then separated into its own index")
    crystallizer = boot()
    book = recorded_book()
    english_id = book.bind(spell=English, spellframe=Greeter, binding_name="english", existence=Existence.many,
                           permissions="create")
    conduit = book.conjure(dynamic=True, name="root")
    english = book._spells_by_id[english_id]
    french_id = conduit.bind_inactive(spell=French, spell_index=english.spell_index, spellframe=Greeter,
                                      binding_name="french", existence=Existence.many, permissions="create")
    conduit.remove_from_spell_index(spell_id=french_id, source_index=english.spell_index)
    print(f"    recorded Book: {classes(book)}")
    report = restore(crystallizer)
    show(report)
    print(f"    rebuilt Book: {classes(live_book())}")


def r3() -> None:
    """French separated, then notched active inside its own index."""
    print("R3 as R2, then French notched active inside its own index")
    crystallizer = boot()
    book = recorded_book()
    english_id = book.bind(spell=English, spellframe=Greeter, binding_name="english", existence=Existence.many,
                           permissions="create")
    conduit = book.conjure(dynamic=True, name="root")
    english = book._spells_by_id[english_id]
    french_id = conduit.bind_inactive(spell=French, spell_index=english.spell_index, spellframe=Greeter,
                                      binding_name="french", existence=Existence.many, permissions="create")
    conduit.remove_from_spell_index(spell_id=french_id, source_index=english.spell_index)
    minted = book._inactive_spells[french_id].spell_index
    conduit.notch_spell(spell_index=minted, spell_id=french_id)
    print(f"    recorded Book: {classes(book)}")
    report = restore(crystallizer)
    show(report)
    print(f"    rebuilt Book: {classes(live_book())}")


def main() -> None:
    """Run every case from a fresh boot."""
    for case in (r1, r2, r3):
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    boot()


if __name__ == "__main__":
    main()
