"""Diagnose: a consumer's meld after its index link is released (remove_index_from_contract), today."""
import sys
sys.path[:0] = ["/tmp/cc_res/rule2/tree/src", "/tmp/cc_res/rule2/tree"]
from tests.integration.melder.conduit import test_conduit_integration_notch_revalidation as t
from melder.aether.aether import Aether
from melder.aether.spellbook.spellbook import Spellbook
from melder.aether.conduit.conduit import Conduit

Aether._reset_singleton_for_tests(); a = Aether(); Spellbook._aether = a; Conduit._aether = a
w = t._lend("diag_unc", t.ImplA)
print("first", w.meld_ping())
bb = w.borrower_book
print("before: lookup", {k: dict(v) for k, v in bb._lookup_contracted_spells.items()})
r = w.borrower.remove_index_from_contract(index_id=w.index.id, conduit=w.lender)
print("remove returned", r)
print("after: lookup", {k: dict(v) for k, v in bb._lookup_contracted_spells.items()})
print("after: contracted", {k: {str(i)[:8]: s.spell_name for i, s in v.items()} for k, v in bb._contracted_spells.items()})
print("after: inactive", {k: len(v) for k, v in bb._inactive_contracted_spells.items()} if isinstance(bb._inactive_contracted_spells, dict) else bb._inactive_contracted_spells)
st = bb.find_spell_by_id(w.consumer_id).system_state
print("consumer validity", st.validity, "flags", getattr(st, "_flags", "?"))
try:
    obj = w.borrower.meld(spell=t.Consumer)
    print("meld returned service", type(obj.service).__name__)
except Exception as e:
    print("raised", type(e).__name__, str(e)[:240])
w.cleanup()
