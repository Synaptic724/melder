"""Diagnostic (melder_1, 2026-10-24): which difference makes a restore build no spells?

    A <state>: record with the frame posture made dynamic BEFORE the first bind (the artifact probe's set-up)
    B <state>: record with plain public calls (the world settles dynamic at conjure)
    C <state>: as B, but Spellbook.configure_aether_frame(system_state='dynamic') before the first bind
    R <state>: restore in this (fresh) process and print what was built
"""
import json
import sys

import melder as md
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from restore_targets import English, French, Greeter


def activate():
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def record(dynamic_first: str, path: str) -> None:
    crystallizer = activate()
    configuration = SpellbookConfiguration()
    if dynamic_first == "A":
        from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        configuration.with_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    book = Spellbook(configuration=configuration)
    if dynamic_first == "C":
        book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None)
    english_id = book.bind(spell=English, spellframe=Greeter, binding_name="english", existence="many",
                           permissions="create")
    conduit = book.conjure(dynamic=True, name="root")
    print("recorded: English melds:", type(conduit.meld(spell_id=english_id)).__name__)
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    json.dump({"checkpoint_id": checkpoint_id, "english": english_id}, open(path, "w", encoding="utf-8"))


def restore(path: str) -> None:
    state = json.load(open(path, encoding="utf-8"))
    crystallizer = activate()
    crystallizer.reload_cached_checkpoint(state["checkpoint_id"])
    report = crystallizer.load_checkpoint(state["checkpoint_id"])
    print("restore:", report["status"], report["built_counts"],
          [s["reason"] for s in report["shortfalls"] if s["kind"] != "crystallizer"])


mode, path = sys.argv[1], sys.argv[2]
if mode in ("A", "B", "C"):
    record(mode, path)
else:
    restore(path)
