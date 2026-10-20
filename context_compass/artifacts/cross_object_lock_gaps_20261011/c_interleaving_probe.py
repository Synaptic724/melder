"""
Item (c), deterministic interleaving. Can Spellbook.bind fail because its cross-frame duplicate sweep
(Aether._check_for_spell) walks the frame registry while another thread births a frame?

The binding thread is parked inside the sweep, right after it has asked frame-b, by a wrapper around
AethericFrame.has_spell that only pauses (the real has_spell runs first, nothing is skipped). The main thread then
constructs a Spellbook for a new frame through the public constructor - Aether._ensure_frame, the aetheric plane's
FRAME_CREATE claim and the Aether lock, exactly as in production - and the binder resumes.

Usage: python c_interleaving_probe.py <path to a copy of src/>
"""
import sys
import threading

sys.path.insert(0, sys.argv[1])
from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.spellbook.existence.existence import Existence

Aether._reset_singleton_for_tests()
aether = Aether()
Spellbook._aether = aether
Conduit._aether = aether

book_a = Spellbook(aetheric_frame="frame-a")
book_b = Spellbook(aetheric_frame="frame-b")
print("frames:", list(aether._aetheric_frames), "process_wide_unique_spell_ids:", aether.process_wide_unique_spell_ids)
frame_b = aether._aetheric_frames["frame-b"]


class ServiceA:
    """Spell bound in frame-a while frame-c is born."""


parked, release, frame_born = threading.Event(), threading.Event(), threading.Event()
original_has_spell = AethericFrame.has_spell
outcome = {}


def parking_has_spell(self, spell_id):
    answer = original_has_spell(self, spell_id)
    if threading.current_thread() is binder and self is frame_b and not parked.is_set():
        parked.set()                      # the binder is inside the cross-frame sweep, after frame-b
        assert release.wait(timeout=30)
    return answer


AethericFrame.has_spell = parking_has_spell


def bind_in_frame_a():
    try:
        outcome["spell_id"] = book_a.bind(spell=ServiceA, existence=Existence.unique, permissions="create")
    except BaseException as exc:
        outcome["error"] = repr(exc)


binder = threading.Thread(target=bind_in_frame_a, name="binder")
binder.start()
assert parked.wait(timeout=30), "binder never reached the cross-frame sweep"


def birth_frame_c():
    outcome["book_c"] = Spellbook(aetheric_frame="frame-c")   # real frame creation: plane claim + Aether lock
    frame_born.set()


creator = threading.Thread(target=birth_frame_c, name="creator")
creator.start()
born_while_parked = frame_born.wait(timeout=10)
print("frame-c born while the binder was parked in the sweep:", born_while_parked)
release.set()
binder.join(timeout=30)
creator.join(timeout=30)
AethericFrame.has_spell = original_has_spell
print("bind outcome:", outcome.get("error") or "ok")
print("ServiceA registered in frame-a after the failed bind:", ServiceA in [s.spell for s in book_a._spells.values()])
print("frames now:", list(aether._aetheric_frames))
