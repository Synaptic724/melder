"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A12): does a graft rebuild an index's
parked members as parked?

Each case records a dynamic world with the Crystallizer active, captures one index (`capture_index_graft`), boots
fresh (every world singleton reset), conjures a host Book and grafts the record into it (`graft_index`, the default
fresh-index mode). English is bound active under (Greeter, 'english'), French staged on its index under
(Greeter, 'french'):
  G1  capture English's index (English active, French parked).
  G2  French first separated into its own index with `remove_from_spell_index`; capture that minted index (French
      alone, parked) - what the record says is selected, and what the graft makes of French.
  G3  as G2; capture English's index (English alone) - control.
  G4  French staged under English's own signature (Greeter, 'english'); capture English's index - who holds
      that signature in the host frame after the graft (STORY-2026-10-17-staged_version_releases_active_signature).
It prints the record's selection and each member's custody location, the report, and the host Book's structure.

Read-only on src/: run from this folder with the repository's src (and the repository root, for the test helpers)
on sys.path; the record never leaves memory:
    PYTHONPATH=<repo>/src:<repo> python -X gil=0 probes/probe_graft_parked_members.py
"""
from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

from restore_targets import English, French, Greeter


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


def classes(book: Spellbook) -> str:
    """Name a Book's active and parked versions by class."""
    active = sorted(spell.spell.__name__ for spell in book._spells.values())
    parked = sorted(spell.spell.__name__ for spell in book._inactive_spells.values())
    return f"active={active} parked={parked}"


def source_world(separate: bool, french_name: str = "french"):
    """Record English active and French staged; optionally separate French. Return the Book and both indexes."""
    crystallizer = boot()
    book = recorded_book()
    english_id = book.bind(spell=English, spellframe=Greeter, binding_name="english", existence=Existence.many,
                           permissions="create")
    conduit = book.conjure(dynamic=True, name="root")
    english_index = book._spells_by_id[english_id].spell_index
    french_id = conduit.bind_inactive(spell=French, spell_index=english_index, spellframe=Greeter,
                                      binding_name=french_name, existence=Existence.many, permissions="create")
    if separate:
        conduit.remove_from_spell_index(spell_id=french_id, source_index=english_index)
    french_index = book._inactive_spells[french_id].spell_index
    names = {english_id: "English", french_id: "French"}
    print(f"    source Book: {classes(book)}")
    return crystallizer, english_index, french_index, names


def capture(crystallizer: Crystallizer, index, names: dict) -> dict:
    """Capture `index`'s graft record; print its selection and members."""
    record = crystallizer.capture_index_graft(index.id)
    payload = record["index_payload"]
    selected = payload.get("selected_spell_id")
    members = dict(sorted((names.get(sid, sid[:10]), entry["custody_state"])
                          for sid, entry in record["members"].items()))
    print(f"    record: selected {names.get(selected, selected)}; members {members}")
    return record


def graft(record: dict) -> Spellbook:
    """Boot fresh, conjure a host Book and graft the record into it; print the report and the host's structure."""
    crystallizer = boot()
    host = recorded_book()
    host.conjure(dynamic=True, name="host")
    report = crystallizer.graft_index(record, host)
    print(f"    graft: status {report['status']}; bound {report['members_bound']}; parked {report['members_parked']};"
          f" shortfalls {report['shortfalls']}")
    print(f"    host Book: {classes(host)}")
    return host


def g1() -> None:
    """English's index with French parked on it."""
    print("G1 graft of English's index (English active, French parked)")
    crystallizer, english_index, french_index, names = source_world(separate=False)
    graft(capture(crystallizer, english_index, names))


def g2() -> None:
    """The minted index holding French alone, parked."""
    print("G2 graft of the index remove_from_spell_index minted (French alone, parked)")
    crystallizer, english_index, french_index, names = source_world(separate=True)
    print(f"    live minted index selects: {names.get(french_index.selected_spell_id)}")
    graft(capture(crystallizer, french_index, names))


def g3() -> None:
    """English's index after French left it."""
    print("G3 control: graft of English's index after French was separated (English alone)")
    crystallizer, english_index, french_index, names = source_world(separate=True)
    graft(capture(crystallizer, english_index, names))


def g4() -> None:
    """French staged under English's own signature."""
    print("G4 graft of English's index with French staged under English's signature (Greeter, 'english')")
    crystallizer, english_index, french_index, names = source_world(separate=False, french_name="english")
    host = graft(capture(crystallizer, english_index, names))
    english = next(spell for spell in host._spells.values() if spell.spell is English)
    holder = host._aetheric_frame.get_lookup(english._key)
    held_by = {s.spell_id: s.spell.__name__ for s in list(host._spells.values()) + list(host._inactive_spells.values())}
    print(f"    host frame claim {english._key}: {held_by.get(holder, holder)}")


def main() -> None:
    """Run every case from a fresh boot."""
    for case in (g1, g2, g3, g4):
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    boot()


if __name__ == "__main__":
    main()
