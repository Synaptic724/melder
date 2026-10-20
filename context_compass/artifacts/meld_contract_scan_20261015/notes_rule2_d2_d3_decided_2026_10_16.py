"""Record the owner's D2 and D3 decisions in rule 2's ticket (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
CP = "context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner decided D2 and D3 (chat 2026-10-16, answering the explanation above). D2: fold the dependency
    notch into rule 2 - a notch flags for revalidation every spell that depends on the notched one, in its Book
    through the dependency walk and in other Books through the contract consumers of an impacted provider (owner:
    "if the spell being notched is a dependency for something else it should flag their spells for revalidation").
    D3: on a notch back, the borrower's parked copy of the incoming version becomes usable again and its consumers
    are marked, so their next meld revalidates and rebuilds; built objects are untouched. D1 (B), D4 (the backlog
    investigation task) and D5 (wait for melder_0) stand.
  EVIDENCE:
  - {CP}architecture_patch.md:139-159
  - {CP}component_patch_notch_reactivation.md:1-70
  IMPACT: The patch grows a component for the notch's dependent walk; it goes back to the owner for approval before
    any `src/` edit, and the build still waits for melder_0.
  NEXT: Read how a resolution pass treats a dependency whose own lineage is stale (the transitive case), then write
    the D2 component patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

text = TICKET.read_bytes().decode("ascii")
anchor = "\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
assert "CLAIM: The owner decided D2 and D3" not in text
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
