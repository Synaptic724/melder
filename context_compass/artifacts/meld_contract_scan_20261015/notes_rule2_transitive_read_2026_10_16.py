"""Record how a dependent's resolution pass reads its dependencies (the D2 transitive case) in rule 2's ticket.

melder_1, 2026-10-16. usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
SB = "src/melder/aether/spellbook/"
SC = SB + "spell_compiler/"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: How a dependent's resolution pass reads its dependencies (read whole). A target pass (Phases 5-7 local,
    then 8-11) never reruns a dependency's structural phases. Phase 5 builds the target's scope from the frame-wide
    registry: each lineage's current id and the direct dependency version ids its own last Phase 3 recorded; an id
    that is no longer current (a version a notch parked) is dropped from the scope. Phase 8 expands every
    dependency occurrence from the topology that dependency's own last Phase 3 registered (normal sockets carry
    resolved version ids; contract sockets resolve through the melding Book's contracted maps). Phase 3 refreshes
    only its own spell's registry entries and leaves the plan, the CreationContext and the Phase 5 artifacts alone.
    So after a notch of Dep, a dependent Q two hops away (Q -> P -> Dep) compiles P's stale topology: the lookup of
    Dep's parked version misses, the pass records a visibility failure that sets every scoped spell (Q and P)
    `invalid` for the conduit, and the gate's resolution branch raises on an `invalid` verdict without rerunning -
    Q stays refused there until something gates it again. The deferred lane (`resolution_required`) runs 8-11 over
    the spell's existing Phase 5 artifacts when it is its own Phase 5 root, and the full 5-11 pass otherwise.
  EVIDENCE:
  - {SB}spellbook_creation_system.py:1722-1835
  - {SB}spellbook_creation_system.py:2411-2576
  - {SB}spellbook_creation_system.py:2599-2660
  - {SC}phases/compiler_phase_5.py:222-264
  - {SC}phases/compiler_phase_5.py:628-729
  - {SC}system/spell_system_adjacency_builder.py:31-95
  - {SC}spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:924-1014
  - {SC}spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1060-1225
  - {SC}phases/compiler_phase_3.py:1193-1318
  - {SC}spell_compiler_system.py:771-822
  - src/melder/aether/conduit/meld/meld.py:933-988
  - src/melder/aether/conduit/meld/meld.py:1006-1102
  - src/melder/aether/conduit/meld/meld.py:1248-1309
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_design_gil0.txt:26-31
  IMPACT: Marking the closure is not enough for a dependent two hops away: before a plan compiles, every stale
    lineage it expands needs its structure refreshed, and a refreshed dependency's own plan must be reset so no
    door serves the old one.
  NEXT: Probe the chain in one Book and across Books with the closure emulated, with and without a meld-time
    structural catch-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

text = TICKET.read_bytes().decode("ascii")
anchor = "\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
assert "CLAIM: How a dependent's resolution pass reads its dependencies" not in text
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
