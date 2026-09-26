"""Compare fast-arm shapes in one process (run from the base tree root, PYTHONPATH=src:.).

base: today's Conduit-level plain arm. slot: after the guards read `door_spell.user_created_object`, call the door only
when it is None. flag: the entry carries a bool (object bound at build time); only flagged entries read the slot.
Each shape reads the real meld door's entries (flag builds a 4-tuple copy). Cases: an existing object, a class bound
unique (reuse), a class bound many. Interleaved rounds, median of 9 x 200k calls per shape, ns, main thread.
"""
import statistics, sys, time, warnings
warnings.simplefilter("ignore")
from melder import Aether, Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Plain:
    def __init__(self) -> None:
        self.value = 0


def base(conduit, spell_id, entries):
    if conduit._cleaned:
        conduit.check_cleaned()
    m = conduit._meld
    fast_entry = entries.get(spell_id)
    if fast_entry is not None:
        (door_spell, captured_context, captured_epoch) = fast_entry
        fast_executor = None
        try:
            if (not m._meld_hooks and door_spell._door_epoch == captured_epoch
                    and door_spell._creation_context is captured_context
                    and not m._spellbook._spellbook_validation_required):
                fast_executor = captured_context._no_overrides_instance_executor
        except AttributeError:
            fast_executor = None
        if fast_executor is not None:
            instance = fast_executor(m)
            spellbook = m._spellbook
            if spellbook._cache_emit_required:
                spellbook._emit_cache_file_if_required()
            return instance
    return None


def slot(conduit, spell_id, entries):
    if conduit._cleaned:
        conduit.check_cleaned()
    m = conduit._meld
    fast_entry = entries.get(spell_id)
    if fast_entry is not None:
        (door_spell, captured_context, captured_epoch) = fast_entry
        existing_instance = None
        fast_executor = None
        try:
            if (not m._meld_hooks and door_spell._door_epoch == captured_epoch
                    and door_spell._creation_context is captured_context
                    and not m._spellbook._spellbook_validation_required):
                existing_instance = door_spell.user_created_object
                if existing_instance is None:
                    fast_executor = captured_context._no_overrides_instance_executor
        except AttributeError:
            fast_executor = None
        if existing_instance is not None:
            spellbook = m._spellbook
            if spellbook._cache_emit_required:
                spellbook._emit_cache_file_if_required()
            return existing_instance
        if fast_executor is not None:
            instance = fast_executor(m)
            spellbook = m._spellbook
            if spellbook._cache_emit_required:
                spellbook._emit_cache_file_if_required()
            return instance
    return None


def flag(conduit, spell_id, entries):
    if conduit._cleaned:
        conduit.check_cleaned()
    m = conduit._meld
    fast_entry = entries.get(spell_id)
    if fast_entry is not None:
        (door_spell, captured_context, captured_epoch, captured_existing) = fast_entry
        fast_executor = None
        try:
            if (not m._meld_hooks and door_spell._door_epoch == captured_epoch
                    and door_spell._creation_context is captured_context
                    and not m._spellbook._spellbook_validation_required):
                if captured_existing:
                    fast_executor = door_spell.user_created_object
                else:
                    fast_executor = captured_context._no_overrides_instance_executor
        except AttributeError:
            fast_executor = None
        if fast_executor is not None:
            if captured_existing:
                instance = fast_executor
            else:
                instance = fast_executor(m)
            spellbook = m._spellbook
            if spellbook._cache_emit_required:
                spellbook._emit_cache_file_if_required()
            return instance
    return None


def world(spell, existence):
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook(aetheric_frame="shapes")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    sid = book.bind(spell=spell, existence=existence, permissions="create")
    conduit = book.conjure(name="shapes")
    conduit.meld(spell_id=sid)
    entries3 = conduit._meld._fast_meld_doors
    e = entries3[sid]
    entries4 = {sid: (e[0], e[1], e[2], e[0].user_created_object is not None)}
    return conduit, sid, entries3, entries4


def per_call(fn, conduit, sid, entries, n=200000):
    s = time.perf_counter_ns()
    for _ in range(n):
        fn(conduit, sid, entries)
    return (time.perf_counter_ns() - s) / n


print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
for label, spell, existence in (("existing object", Plain(), Existence.unique),
                                ("class unique", Plain, Existence.unique),
                                ("class many", Plain, Existence.many)):
    conduit, sid, e3, e4 = world(spell, existence)
    ref = conduit.meld(spell_id=sid)
    if existence is not Existence.many:
        assert base(conduit, sid, e3) is ref and slot(conduit, sid, e3) is ref and flag(conduit, sid, e4) is ref
    samples = {"base": [], "slot": [], "flag": []}
    for _ in range(9):
        samples["base"].append(per_call(base, conduit, sid, e3))
        samples["slot"].append(per_call(slot, conduit, sid, e3))
        samples["flag"].append(per_call(flag, conduit, sid, e4))
    med = {k: statistics.median(v) for k, v in samples.items()}
    print(f"  {label:16} base {med['base']:6.1f} | slot {med['slot']:6.1f} ({med['slot'] - med['base']:+5.1f}) | "
          f"flag {med['flag']:6.1f} ({med['flag'] - med['base']:+5.1f})")
    conduit.cleanup()
