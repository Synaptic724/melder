"""Probe (melder_1, 2026-10-25; STORY-2026-10-17-notch_moves_signature_by_incoming_key_only): a record holding a mixed
index, replayed under option (A).

Option (A) makes an index the owner of one binding signature: a version staged or added onto it must carry the
index's spellframe and binding name. Records made before that can hold an index whose versions sit at different
addresses (the owner allowed it on 2026-10-17). This probe records such an index in one process - English active at
(Greeter, 'english'), French staged parked on its index at (Greeter, 'french') - as a checkpoint and as an index graft
record, then replays each in a fresh process: run the record case on the 0.2.8267 tree and the replay cases on a tree
with the (A) way-in check, to see what a replay of today's records meets.

    python probe_mixed_record_under_option_a.py record <state.json>
    python probe_mixed_record_under_option_a.py restore <state.json>   # a fresh process; the checkpoint file copied
    python probe_mixed_record_under_option_a.py graft <state.json>     # a fresh process

The checkpoint lands in the Crystallizer cache under the melder package that ran the record case
(<package>/__melder_cache__/__crystallizer_cache__); copy it under the replaying tree's package before `restore`.
Run with that tree's src/ first on sys.path and this folder on it (restore_targets.py is the importable targets).
"""
import json
import sys

from melder.aether.aether import Aether
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer


def activate_crystallizer() -> Crystallizer:
    """Activate the hosted Crystallizer with its default configuration."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def recorded_book() -> Spellbook:
    """A Book whose frame is dynamic before the first bind, so the Crystallizer records the binds."""
    configuration = SpellbookConfiguration()
    configuration.with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    book = Spellbook(configuration=configuration)
    book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None)
    return book


def first_line(error: BaseException) -> str:
    """The type and first line of an error, and of its cause when it has one."""
    text = "%s: %s" % (type(error).__name__, (str(error).splitlines() or [""])[0][:300])
    cause = error.__cause__
    if cause is not None:
        text += "\n    caused by %s: %s" % (type(cause).__name__, (str(cause).splitlines() or [""])[0][:300])
    return text


def where_is(conduit, spell_id: str, name: str) -> str:
    """Say whether `spell_id` is in the conduit's world, and whether it melds (active) or not (parked)."""
    try:
        spell = conduit.get_spell_by_spell_id(spell_id)
    except ValueError as error:
        return "%s is gone (%s)" % (name, str(error).splitlines()[0][:80])
    address = "%s/%s" % spell._key
    try:
        conduit.meld(spell_id=spell_id)
        return "%s is there at %s and ACTIVE (melds)" % (name, address)
    except KeyError:
        return "%s is there at %s, parked (does not meld)" % (name, address)


def record(state_path: str) -> None:
    """Record English active at 'english' and French parked on its index at 'french'."""
    from restore_targets import English, French, Greeter
    crystallizer = activate_crystallizer()
    book = recorded_book()
    english_id = book.bind(spell=English, spellframe=Greeter, binding_name="english", existence="many",
                           permissions="create")
    conduit = book.conjure(dynamic=True, name="root")
    index = conduit.get_spell_by_spell_id(english_id).spell_index
    french_id = conduit.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="french",
                                      existence="many", permissions="create")
    print("  recorded: English active at greeter/english, French parked on the same index at greeter/french")
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    graft_record = crystallizer.capture_index_graft(index.id)
    with open(state_path, "w", encoding="utf-8") as handle:
        json.dump({"checkpoint_id": checkpoint_id, "english": english_id, "french": french_id,
                   "graft_record": graft_record}, handle)
    print("  checkpoint %s flushed; the index captured as a graft record" % checkpoint_id)


def restore(state_path: str) -> None:
    """In a fresh process: reload the flushed checkpoint and restore it."""
    with open(state_path, encoding="utf-8") as handle:
        state = json.load(handle)
    crystallizer = activate_crystallizer()
    crystallizer.reload_cached_checkpoint(state["checkpoint_id"])
    try:
        report = crystallizer.load_checkpoint(state["checkpoint_id"])
    except Exception as error:
        print("  restore raises " + first_line(error))
        return
    print("  restore status: %s" % report.get("status"))
    for shortfall in report.get("shortfalls", []) or []:
        if shortfall.get("kind") != "crystallizer":
            print("  shortfall: %s" % shortfall.get("reason"))
    conduit = Aether().get_root_conduit_by_name("root")
    print("  " + where_is(conduit, state["english"], "English"))
    print("  " + where_is(conduit, state["french"], "French"))


def graft(state_path: str) -> None:
    """In a fresh process: graft the captured index into a new host Book."""
    with open(state_path, encoding="utf-8") as handle:
        state = json.load(handle)
    crystallizer = activate_crystallizer()
    host = recorded_book()
    host_conduit = host.conjure(dynamic=True, name="host")
    try:
        report = crystallizer.graft_index(state["graft_record"], host)
    except Exception as error:
        print("  graft raises " + first_line(error))
        return
    print("  graft status: %s; bound active %s; parked %s" % (report["status"], report["members_bound"],
                                                             report["members_parked"]))
    print("  " + where_is(host_conduit, state["english"], "English"))
    print("  " + where_is(host_conduit, state["french"], "French"))


def main() -> None:
    """Run the case named on the command line."""
    case = sys.argv[1]
    print("case %s" % case)
    if case == "record":
        record(sys.argv[2])
    elif case == "restore":
        restore(sys.argv[2])
    elif case == "graft":
        graft(sys.argv[2])
    else:
        raise SystemExit("unknown case %s" % case)


if __name__ == "__main__":
    main()
