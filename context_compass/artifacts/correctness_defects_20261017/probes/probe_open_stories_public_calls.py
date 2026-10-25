"""Probe (melder_1, 2026-10-24; EPIC-2026-10-17-correctness_defects): the open stories through public calls only.

The owner asked for the three open stories to be checked again. The artifact probes read private state to show WHY
each one breaks; this probe makes only the calls an agent would make and prints what Melder answers, so it shows
whether each defect is visible from the outside. One case per process (a spell_id is the class's code, so a class is
bound once per process); S5 records in one process and restores or grafts in a second, a real fresh boot.

    python probe_open_stories_public_calls.py S2_C5
    python probe_open_stories_public_calls.py S2_C7_fresh        # French never compiled before the notch
    python probe_open_stories_public_calls.py S2_C7_compiled     # French compiled by a notch to it and back first
    python probe_open_stories_public_calls.py S5_R2_record <state.json>, then S5_R2_restore <state.json>
    python probe_open_stories_public_calls.py S5_G2_capture <state.json>, then S5_G2_graft <state.json>

S11 is not here: its own probe (probe_notch_back_lineage_dependencies.py) already melds through public calls.
Run with src/ first on sys.path (and the repository root for S5's importable targets), the GIL off and on.
"""
import json
import sys
from typing import Protocol

import melder as md
from melder.aether.aether import Aether
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer


class Greeter(Protocol):
    """The contract every greeter implements."""

    def greet(self) -> str: ...


class English:
    """Active at (Greeter, 'greeter')."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """A second version of English's index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Spanish:
    """A version at another address."""

    def greet(self) -> str:
        """Return the Spanish greeting."""
        return "hola"


class Italian:
    """Another Book's spell taking the old address."""

    def greet(self) -> str:
        """Return the Italian greeting."""
        return "ciao"


class Portuguese:
    """A spell taking the old address after the lender's teardown."""

    def greet(self) -> str:
        """Return the Portuguese greeting."""
        return "ola"


def show(label: str, call) -> None:
    """Print what `call` returns, or the type and first line of what it raises."""
    try:
        print("  %s -> %s" % (label, call()))
    except Exception as error:
        first = str(error).splitlines()[0] if str(error) else ""
        print("  %s -> raises %s: %s" % (label, type(error).__name__, first[:260]))


def bind(book, cls, name: str) -> str:
    """Bind `cls` active at (Greeter, name) as `many`; return its spell_id."""
    return book.bind(spell=cls, spellframe=Greeter, binding_name=name, existence="many", permissions="create")


def stage(conduit, cls, name: str, index) -> str:
    """Stage `cls` parked at (Greeter, name) on `index`; return its spell_id."""
    return conduit.bind_inactive(spell=cls, spell_index=index, spellframe=Greeter, binding_name=name,
                                 existence="many", permissions="create")


def greeting(conduit, **where) -> str:
    """Meld a greeter and say what it is."""
    obj = conduit.meld(**where)
    return "%s says %r" % (type(obj).__name__, obj.greet())


def s2_c5() -> None:
    """A notch across addresses, then a bind of the old address by another Book, before and after a teardown."""
    book = md.Spellbook()
    english_id = bind(book, English, "greeter")
    lender = book.conjure(dynamic=True, name="lender")
    index = lender.get_spell_by_spell_id(english_id).spell_index
    spanish_id = stage(lender, Spanish, "spanish", index)
    show("notch English ('greeter') -> Spanish ('spanish')",
         lambda: lender.notch_spell(spell_index=index, spell_id=spanish_id).spell_name)
    show("lender meld at 'spanish'", lambda: greeting(lender, spellframe=Greeter, binding_name="spanish"))
    show("lender meld at 'greeter' (nothing should answer)",
         lambda: greeting(lender, spellframe=Greeter, binding_name="greeter"))
    other_book = md.Spellbook()
    show("another Book binds Italian at 'greeter'", lambda: bind(other_book, Italian, "greeter")[:12])
    show("tear the lender's root down", lambda: lender.cleanup())
    show("a new Book binds Portuguese at 'greeter'", lambda: bind(md.Spellbook(), Portuguese, "greeter")[:12])


def s2_c7(compiled_before: bool) -> None:
    """French split into its own index at English's address, then notched active there."""
    book = md.Spellbook()
    english_id = bind(book, English, "greeter")
    lender = book.conjure(dynamic=True, name="lender")
    index = lender.get_spell_by_spell_id(english_id).spell_index
    french_id = stage(lender, French, "greeter", index)
    if compiled_before:
        show("notch to French", lambda: lender.notch_spell(spell_index=index, spell_id=french_id).spell_name)
        show("lender meld at 'greeter'", lambda: greeting(lender, spellframe=Greeter, binding_name="greeter"))
        show("notch back to English", lambda: lender.notch_spell(spell_index=index, spell_id=english_id).spell_name)
    show("remove French into its own index",
         lambda: lender.remove_from_spell_index(spell_id=french_id, source_index=index) or "done")
    minted = lender.get_spell_by_spell_id(french_id).spell_index
    show("notch French active in its own index",
         lambda: lender.notch_spell(spell_index=minted, spell_id=french_id).spell_name)
    show("lender meld at 'greeter'", lambda: greeting(lender, spellframe=Greeter, binding_name="greeter"))
    show("lender meld English by spell_id", lambda: greeting(lender, spell_id=english_id))
    show("lender meld French by spell_id", lambda: greeting(lender, spell_id=french_id))


def activate_crystallizer() -> Crystallizer:
    """Activate the hosted Crystallizer with its default configuration."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def recorded_book() -> Spellbook:
    """A Book for a recorded dynamic world: configuration finalized and the frame made dynamic before the first bind.

    The frame is made dynamic here, not by `conjure(dynamic=True)`: binds made before the world settles dynamic were
    not in the checkpoint on 0.2.8267 (a separate finding, recorded on the epic), and S5 needs them recorded.
    """
    configuration = SpellbookConfiguration()
    configuration.with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    book = Spellbook(configuration=configuration)
    book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None)
    return book


def split_world():
    """English active at 'english', French staged at 'french' and split into its own index."""
    from restore_targets import English as TEnglish, French as TFrench, Greeter as TGreeter
    crystallizer = activate_crystallizer()
    book = recorded_book()
    english_id = book.bind(spell=TEnglish, spellframe=TGreeter, binding_name="english", existence="many",
                           permissions="create")
    conduit = book.conjure(dynamic=True, name="root")
    index = conduit.get_spell_by_spell_id(english_id).spell_index
    french_id = conduit.bind_inactive(spell=TFrench, spell_index=index, spellframe=TGreeter,
                                      binding_name="french", existence="many", permissions="create")
    conduit.remove_from_spell_index(spell_id=french_id, source_index=index)
    minted = conduit.get_spell_by_spell_id(french_id).spell_index
    print("  recorded: English active in its index; French parked alone in its own index: %s"
          % (minted is not index))
    return crystallizer, conduit, english_id, french_id, minted


def where_is(conduit, spell_id: str, name: str) -> str:
    """Say whether `spell_id` is in the conduit's world and whether it melds (active) or not (parked)."""
    try:
        conduit.get_spell_by_spell_id(spell_id)
    except ValueError as error:
        return "%s is gone (%s)" % (name, str(error).splitlines()[0][:80])
    try:
        conduit.meld(spell_id=spell_id)
        return "%s is there and ACTIVE (melds)" % name
    except KeyError:
        return "%s is there, parked (does not meld)" % name


def s5_r2_record(state_path: str) -> None:
    """Record the split world, checkpoint it and flush the checkpoint to the cache."""
    crystallizer, conduit, english_id, french_id, minted = split_world()
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    with open(state_path, "w", encoding="utf-8") as handle:
        json.dump({"checkpoint_id": checkpoint_id, "english": english_id, "french": french_id}, handle)
    print("  checkpoint flushed")


def s5_r2_restore(state_path: str) -> None:
    """In a fresh process: reload the flushed checkpoint and restore it."""
    with open(state_path, encoding="utf-8") as handle:
        state = json.load(handle)
    crystallizer = activate_crystallizer()
    crystallizer.reload_cached_checkpoint(state["checkpoint_id"])
    report = crystallizer.load_checkpoint(state["checkpoint_id"])
    print("  restore status: %s" % report.get("status"))
    for shortfall in report.get("shortfalls", []) or []:
        if shortfall.get("kind") != "crystallizer":
            print("  shortfall: %s" % shortfall.get("reason"))
    conduit = Aether().get_root_conduit_by_name("root")
    print("  " + where_is(conduit, state["english"], "English"))
    print("  " + where_is(conduit, state["french"], "French"))


def s5_g2_capture(state_path: str) -> None:
    """Record the split world and capture French's own index as a graft record."""
    crystallizer, conduit, english_id, french_id, minted = split_world()
    record = crystallizer.capture_index_graft(minted.id)
    with open(state_path, "w", encoding="utf-8") as handle:
        json.dump({"record": record, "french": french_id}, handle)
    print("  graft record of French's index captured (JSON: ok)")


def s5_g2_graft(state_path: str) -> None:
    """In a fresh process: graft the record into a new host Book."""
    with open(state_path, encoding="utf-8") as handle:
        state = json.load(handle)
    crystallizer = activate_crystallizer()
    host = recorded_book()
    host_conduit = host.conjure(dynamic=True, name="host")
    report = crystallizer.graft_index(state["record"], host)
    print("  graft status: %s; bound active %s; parked %s" % (report["status"], report["members_bound"],
                                                             report["members_parked"]))
    print("  " + where_is(host_conduit, state["french"], "French"))


def main() -> None:
    """Run the case named on the command line."""
    case = sys.argv[1]
    print("case %s" % case)
    if case == "S2_C5":
        s2_c5()
    elif case == "S2_C7_fresh":
        s2_c7(compiled_before=False)
    elif case == "S2_C7_compiled":
        s2_c7(compiled_before=True)
    elif case == "S5_R2_record":
        s5_r2_record(sys.argv[2])
    elif case == "S5_R2_restore":
        s5_r2_restore(sys.argv[2])
    elif case == "S5_G2_capture":
        s5_g2_capture(sys.argv[2])
    elif case == "S5_G2_graft":
        s5_g2_graft(sys.argv[2])
    else:
        raise SystemExit("unknown case %s" % case)


if __name__ == "__main__":
    main()
