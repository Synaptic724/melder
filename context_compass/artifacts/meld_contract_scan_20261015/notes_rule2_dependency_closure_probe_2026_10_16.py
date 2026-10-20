"""Record the D2 dependency-closure probe in rule 2's ticket (melder_1, 2026-10-16).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
A = "context_compass/artifacts/meld_contract_scan_20261015/"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: D2 probe (0.2.8248 tree, Python 3.14.7t, GIL off and on, same results; monkeypatches only). A chain
    Q -> P -> Dep in one Book with Dep bound under a Protocol and notched to another implementer, and the same
    across Books (the lender's P and Dep index-linked into a Book whose Consumer holds a SpellContract on P's key
    and whose User depends on Consumer). Today and with rule 2 alone: Q keeps building the old Dep when it was
    melded before the notch, otherwise fails with RuntimeError "many_only manifest references unknown spell_id";
    P's first meld fails with the visibility error naming Dep's parked version; across Books the User is broken
    from the start (AttributeError "'SpellContract' object has no attribute 'ping'": linking marked Consumer, not
    User, whose conjure-time plan built Consumer with its SpellContract default). With the notch marking its
    closure (registry edges plus contract keys; a mutator's mark walks on from the consumers it marks), mark only:
    P follows (one 5-11), User works before the notch, but Q fails with that visibility error and then stays
    refused ("No validation error was recorded") even after P is rebuilt; across Books User and Consumer stay
    refused too. With a meld-time catch-up added (every stale lineage the plan expands gets phases 1-4 with its
    owner Book under its rebuild window and lock, then its own plan reset and `resolution_required`): Q follows
    with one refresh and one 5-11, the next melds take the fast door, P's own meld then runs its full pass, and the
    Book flag comes down; across Books User, Consumer and the lender's P follow (two refreshes). A notch to a class
    the kind rule does not select for `dep: Dep` gives Q and P the first meld's UnresolvedInputError "PClass.dep
    expects Dep, but nothing registered provides it", not the old version. The borrower's flag stays up for a
    reason present before any meld: its conduit holds index-linked copies it never resolved.
  EVIDENCE:
  - {A}probe_rule2_dependency_closure.py:1-367
  - {A}runs/probe_rule2_dependency_closure_gil0.txt:1-173
  - {A}runs/probe_rule2_dependency_closure_gil1.txt:5-177
  IMPACT: D2 needs both halves: the closure mark (from the notch and from rule 2's marks) and the catch-up before a
    plan compiles; marking alone strands a dependent two hops away. The walk also fixes a live defect: a contract
    consumer's dependents kept a plan built without the provider after a link or grant.
  NEXT: Write the D2 component patch and update the architecture and code-description patches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

text = TICKET.read_bytes().decode("ascii")
anchor = "\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
assert "CLAIM: D2 probe (0.2.8248 tree" not in text
updated = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(updated) == 1
text = text.replace(updated[0], f"- Updated: {NOW}", 1)
text = text.replace(anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, 1)
too_long = [l for l in text.split("\n") if len(l) > 120 and not (l.startswith("  - ") and " " not in l[4:])]
assert not too_long, too_long
text.encode("ascii")
if not CHECK:
    TICKET.write_bytes(text.encode("ascii"))
print("checked" if CHECK else "written", len(text.split("\n")), "lines")
