"""Instrumented bind -> meld -> cleanup_spell -> bind -> meld (the failing [True-False] case)."""
from melder import Aether, Cleanable, Conduit, Spellbook


class RebindProbe(Cleanable):
    def __init__(self, value: int = 1) -> None:
        super().__init__(); self.value = value
    def cleanup(self) -> None:
        if self._cleaned: return
        self._cleaned = True; del self.value

Aether._reset_singleton_for_tests(); world = Aether(); Spellbook._aether = world; Conduit._aether = world

book = Spellbook(aetheric_frame="rebind-probe")
book.configure_aether_frame(system_state="dynamic", system_caching_enabled=False, disposal=None, disposal_method_names=None)
book.get_configuration().freeze()
root = book.conjure(dynamic=True, name="action_definitions")
scope = root.create_lesser_conduit(name="center_actions")
meld_obj = scope._meld
rcid = meld_obj._resolution_conduit_id
print("root conduit id      :", root._id)
print("scope resolution cid :", rcid, "(== root id:", rcid == root._id, ")")

def snap(tag, spell):
    sss = spell._spell_system_states
    st = spell.system_state
    rs = sss.get_conduit_resolution_state(rcid)
    sid = spell.spell_id
    art = spell._compiler_artifact
    print(f"--- {tag}")
    print("  spell obj id       :", hex(id(spell)), "spell_id:", sid[:12], "index:", spell.spell_index.id[:12])
    print("  structural validity:", None if st is None else st.validity, "| flags:", None if st is None else sorted(f.name for f in st.flags))
    print("  conduit res state  :", "None" if rs is None else f"root_validity={rs.get_root_validity(sid)} spell_validity={rs.get_spell_validity(sid)}")
    print("  resolution_required:", spell.resolution_required, "complete:", spell.resolution_complete)
    print("  compiler artifact  :", None if art is None else f"phase5_root={'set' if art._root_blueprint_phase5 is not None else None} codegen={'set' if art._spell_codegen_creation is not None else None}")
    print("  is_phase5_root     :", meld_obj._get_spell_compiler_system().is_current_spell_phase5_root(spell))
    print("  gated_validation_required:", meld_obj._gated_validation_required(spell))
    print("  effective res validity   :", meld_obj._get_resolution_validity(spell, rs))

ident = root.bind(spell=RebindProbe, existence="many", spellframe="actions", binding_name="probe", disposal_method_names=["cleanup"])
old = root.get_spell_by_id(ident, "rebind-probe")
snap("after bind #1", old)
original = scope.meld(spellframe="actions", binding_name="probe")
print("meld #1 ->", original.value)
snap("after meld #1", old)
root.cleanup_spell(spell=old)
print("--- after cleanup_spell: old cleaned:", old.cleaned, "| original product live:", not original.cleaned)
rs = book._spell_system_states.get_conduit_resolution_state(rcid)
print("  conduit res state for OLD id after cleanup_spell:", f"root_validity={rs.get_root_validity(ident)} spell_validity={rs.get_spell_validity(ident)}")
rep = root.bind(spell=RebindProbe, existence="many", spellframe="actions", binding_name="probe", disposal_method_names=["cleanup"])
new = root.get_spell_by_id(rep, "rebind-probe")
print("--- rebind: same spell_id as before:", rep == ident, "| same Spell object:", new is old, "| same index id:", new.spell_index.id == old.spell_index.id if not old.cleaned else "old cleaned")
snap("after bind #2 (before meld #2)", new)
try:
    out = scope.meld(spellframe="actions", binding_name="probe", override={"value": 2})
    print("meld #2 ->", out.value)
except Exception as e:
    print("meld #2 RAISED:", type(e).__name__, str(e)[:90])
    snap("after failed meld #2", new)
finally:
    root.cleanup()
