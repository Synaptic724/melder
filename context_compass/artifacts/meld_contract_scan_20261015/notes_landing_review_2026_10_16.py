"""Record the 0.2.8247 landing's docs, graph, release note and rubric, and move the ticket to review (melder_1).

usage (from the repository root): python <this script> <UTC now> [--check]
Five Notes before the handoff summary, the State Transition Event, Status/Updated, Validation, Artifact Links and the
handoff summary. Every anchor must occur exactly once; new lines stay within 120 characters and ASCII; --check
writes nothing.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
PATH = pathlib.Path("context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md")
A = "context_compass/artifacts/meld_contract_scan_20261015/"
D = "context_compass/system_docs/"


def note(kind, claim, evidence, impact, nxt, reread, score):
    lines = [f"- DATETIME: {NOW}", "  AUTHOR: melder_1", "  AUTHOR_ROLE: synaptic_python_developer", f"  TYPE: {kind}"]
    lines.append("  CLAIM: " + claim[0])
    lines += ["    " + c for c in claim[1:]]
    lines.append("  EVIDENCE:")
    lines += ["  - " + e for e in evidence]
    lines.append("  IMPACT: " + impact[0])
    lines += ["    " + c for c in impact[1:]]
    lines.append("  NEXT: " + nxt)
    lines += [f"  REREAD: {reread}", f"  SCORE_0_TO_10: {score}"]
    return "\n".join(lines) + "\n"


NOTE_DOCS = note("FACT", [
    "The four system documents carry rule 1, read back from disk after their index rebuilds. src_architecture:",
    "step 7 of the meld-time gate, the first operational invariant (the flag and its writer, the published set, the",
    "subset test, the repeat-notch re-publication, the lock order, the measurements), the first failure mode, six",
    "code-map extents remeasured (spellbook.py 7615, transfer_of_ownership.py 2155, spell_system_states.py 1886,",
    "spell_system_state.py 806, spell_state.py 93, risk_manager.py 751) and the notch-seam and settle citations into",
    "spellbook.py remeasured. src_components: the DevOps Control Plane, the SpellSystemStates Registry, Meld Runtime",
    "Gating, flow step 6, two new code-map entries and the touched blocks' seam and Conduit citations remeasured; its",
    "handoff names spellbook.py:7233-7244, :286, :5713-5719, :5273-5285, :6546 and transfer_of_ownership.py:953,",
    ":1444 as stale from earlier lanes and not re-audited. tests_components: the DevOps Control Plane Unit Cluster",
    "(A, B), D in the Aether Component Cluster, five C1 entries, 250 core paths; tests_architecture: the recount (836",
    "test modules). Every line that left the four documents is an edit (a remeasured number, extent, stamp, date or",
    "count), the four indexes are current, and there is no portability or absolute-path hit.",
], [
    D + "src_architecture.md:839-845",
    D + "src_architecture.md:1034-1062",
    D + "src_architecture.md:1938-1947",
    D + "src_architecture.md:4052-4061",
    D + "src_components.md:4719-4829",
    D + "src_components.md:6986-7039",
    D + "src_components.md:11033-11043",
    D + "tests_components.md:931-952",
    D + "tests_architecture.md:884-887",
    A + "runs/docs_preservation_2026_10_16.txt:1-76",
    A + "runs/docs_index_check_2026_10_16.txt:1-8",
    A + "land_docs_src_architecture_2026_10_16.py:1-237",
    A + "land_docs_src_components_2026_10_16.py:1-214",
    A + "land_docs_tests_2026_10_16.py:1-171",
    A + "remap_citations_2026_10_16.py:1-72",
], [
    "The packaged documents describe the landed behaviour; the stale citations named above are earlier lanes'",
    "drift, recorded here and left for a citation pass (outside this change).",
], "The graph descriptors and the assembled graph.", "HELPFUL", 8)

NOTE_GRAPH = note("MEASURE", [
    "The graph carries rule 1. Authored fields were written, then tightened after re-reading each node's source",
    "against them: SpellState (owns_state `new_index` for the stale `new_lineage`, plus `non_resolvable`; the",
    "capability flag), SpellSystemState (`update_flags`; `_republish_validity` on the registry's request),",
    "SpellSystemStates (the capability write, the re-publication, the published set; owns",
    "`_non_resolvable_index_ids`), RiskManager (the subset test; `register_conduit` refreshes once) and Spellbook (bind",
    "and notch pass the capability). Those five nodes were stamped against the pristine 0.2.8246 source, so each was",
    "re-read against the diff from that copy and accepted (`graph_walker --accept --apply`). TransferOfOwnership stays",
    "SEMANTICS_STALE: its stamp predates melder_0's 0.2.8246 change, so verifying it is not this lane's. Re-extracted",
    "with --strict (591 descriptors, nothing skipped; it also restores the extractor's indent=1, which the walker's",
    "accept writes as indent=2): census 9 unsemantic, 221 stale, 0 orphaned; walker 1074 AUTHORED (+5), 144 stale.",
    "Assembled 591 sections, 1227 nodes, 1415 edges, 28063 lines; --check and the index proof pass; no portability",
    "hit. The sections that changed are the six source files, `__version__.py` and six generated system-document",
    "assets whose bytes moved since the previous assembly.",
], [
    D + "src_graph_index.md:101-106",
    D + "src_graph_index.md:144-144",
    D + "src_graph_index.md:362-362",
    A + "graph_semantics_2026_10_16.py:1-76",
    A + "graph_semantics_refine_2026_10_16.py:1-56",
    A + "runs/graph_accept_2026_10_16.txt:1-7",
    A + "runs/extract_graph_2026_10_16.txt:1-46",
    A + "runs/graph_walker_report_2026_10_16.txt:1-110",
    A + "runs/assemble_graph_2026_10_16.txt:1-4",
    A + "runs/assemble_graph_check_2026_10_16.txt:1-4",
], [
    "The wiring slices for the six files describe the landed code, and the five nodes read as verified against it;",
    "the graph's stale count fell by the five this lane had made stale.",
], "The release note, the notch notice and the patch lane.", "HELPFUL", 8)

NOTE_RELEASE = note("FACT", [
    "Release note, notch notice and records. release_docs/next_version_release.md reads \"# Melder 0.2.8247\" and",
    "gains \"A non-resolvable definition no longer sends every meld of its Book through validation\" (the symptom, a",
    "Protocol example, the measurements, the notch-back behaviour, what stays the same), a packaging bullet and the",
    "rebuild line for 0.2.8247. Its example was run as written on the pristine 0.2.8246 code and on the landed code: a",
    "warm override meld 12.9 -> 0.39 us with the GIL off and 13.2 -> 0.40 us with it on, and a meld of the definition",
    "is refused with the same MeldExecutionError on both (the landed copy's version file predates the notch). The",
    "attention board carries \"Notch notice (melder_1, 2026-10-16)\". The five patch docs moved (mv -n) to",
    "system_docs/patches/completed/meld_state_gate_2026_10_15/; the artifact board clears them as one",
    "promote_to_documentation row, and the folder row names the landing's evidence.",
], [
    "release_docs/next_version_release.md:1-3",
    "release_docs/next_version_release.md:487-527",
    "release_docs/next_version_release.md:585-589",
    A + "release_note_2026_10_16.py:1-83",
    A + "release_example_2026_10_16.py:1-56",
    A + "runs/release_example_2026_10_16.txt:1-12",
    "context_compass/attention_board.md:302-305",
    "context_compass/artifact_board.md:96-96",
    "context_compass/artifact_board.md:103-103",
], [
    "Users read the change, with a checked example; other lanes see the notch to build above; the patch lane is",
    "closed out as promoted.",
], "Score the four system documents with the quality rubric, from disk.", "HELPFUL", 8)

NOTE_RUBRIC = note("MEASURE", [
    "Rubric scores, from disk after the index rebuilds (self-scored; no independent reviewer): src_architecture 83",
    "(B) - fidelity 4, contract 5, depth 4, addressability 4, join 4, mirror 4; src_components 83 (B) - 4, 5, 4, 4,",
    "4, 4; tests_architecture 83 (B) - 4, 5, 4, 4, 4, 4; tests_components 77 (B) - 4, 4, 3, 4, 4, 4. Basis:",
    "src_architecture was re-read whole in this session; for the other three the sections this landing edited were",
    "re-read from disk and the measurable half rerun (one H1 each, no duplicate indexed name, no unclosed heading,",
    "contracts complete and in order, no portability or absolute-path hit, 160 / 36 / 234 / 250 C1 records complete",
    "with every extent equal to its file today, every Key Files path resolving), while their unchanged remainder",
    "keeps melder_0's S7 judgment of 2026-10-15T23:39:29Z. Why not 5: fidelity - uncited older bullets",
    "(src_architecture.md:2229, :2241, :2250) and a meld-flow diagram that still names \"Phase12 Compiled",
    "Executors\" in both src documents; depth - one-clause lines remain (src_architecture.md:2229) and four",
    "src_components entries have thin fields (PhaseScheduler at :5641); addressability - container H2s that hold only",
    "sub-headings (src_architecture.md:724, :3556; src_components.md:193); join - 154 of 160, all 36, 228 of 234 and",
    "245 of 250 verified_at stamps are carried forward although every extent measured equal today; mirror - each",
    "pair shares its contract and adds different non-contract sections. tests_components depth 3: its Mock Fixture",
    "Corpus entry has five thin fields.",
], [
    A + "runs/rubric_checks_2026_10_16.txt:1-52",
    A + "rubric_checks_2026_10_16.py:1-173",
    D + "src_architecture.md:2229-2229",
    D + "src_architecture.md:2241-2241",
    D + "src_architecture.md:2250-2251",
    D + "src_architecture.md:3831-3848",
    D + "src_components.md:5641-5714",
    D + "src_components.md:10767-10784",
    D + "tests_components.md:629-718",
    "context_compass/tickets/stories/2026-10-15_managed_docs_release_story.md:498-545",
    "context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:43-54",
], [
    "All four documents are band B and usable as inputs; their weak points predate this landing, which",
    "changed none of the scores melder_0 recorded at S7.",
], "Move the ticket to review.", "HELPFUL", 8)

NOTE_REVIEW = note("DECISION", [
    "The ticket moves from in_progress to blocked (board row `review`, mode handoff). Rule 1 is landed as 0.2.8247",
    "with its tests green in both GIL modes, the four system documents and their indexes, the graph, the release",
    "note, the notch notice, the archived patch lane and the rubric scores, and the rebuild runs last. The EXIT_GATE's",
    "remaining conditions are the owner's: accepting rule 1 (reserved), and answering items (2)-(3) of the design",
    "request - rule 2's \"no signature scan when the spell's state needs no contract check\", which waits on him (a",
    "borrower SpellContract consumer still costs about 2 ms a meld). After the rebuild, M1-19 tells melder_0 that",
    "the landing is done and its files are released. Recorded and left alone (outside this change): the notch-swap",
    "KeyError race (Note 2026-10-15T21:41:50Z), the stale citations named in src_components' handoff, and",
    "TransferOfOwnership's unverified graph node.",
], [
    "{NOTES_RANGE}",
    "context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:31-33",
    "context_compass/attention_board.md:{ROW_LINE}",
], [
    "Rule 1 is done from melder_1's side; what remains is the owner's.",
], "Rebuild the assets and the LLM bundles with both checks, then send M1-19.", "REQUIRED", 9)

TRANSITION_OLD = """## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner directed the fix (chat 2026-10-15: "thats an issue we need to address ... lets figure
  this out").
"""
TRANSITION_NEW = """## State Transition Event
- from_state: in_progress
- to_state: blocked
- transition_reason: rule 1 is landed as 0.2.8247 - code, tests (green with the GIL off and on), the four system
  docs and their indexes, the graph, the release note, the notch notice, the archived patch lane, rubric scores -
  and the rebuild runs last. The EXIT_GATE's remaining conditions are the owner's: accepting rule 1 (reserved) and
  answering items (2)-(3), on which rule 2's "no signature scan" condition waits. Unblock: the owner accepts and
  answers, or redirects. The board row reads `review`.
- prior: draft -> in_progress (2026-10-15T18:46:58Z): the owner directed the fix (chat 2026-10-15: "thats an issue
  we need to address ... lets figure this out").
"""

VALIDATION_OLD = """## Validation
- Not run.
"""
VALIDATION_NEW = """## Validation
- Run: every chunk of the test tree (23) with the GIL off and on, on the scratch tree and on a copy of the landed
  tree; the unit, component and mutation checks of each part; the probes before and after; the release-note
  example (Notes 2026-10-15T21:32:39Z to 2026-10-16T01:05:44Z and the Notes of 2026-10-16 below).
- Not run: coverage (pytest --cov); hosted CI.
"""

LINKS_OLD = """  - system_docs/patches/active/meld_state_gate_2026_10_15/architecture_patch.md
  - system_docs/patches/active/meld_state_gate_2026_10_15/component_patch_spell_state_model.md
  - system_docs/patches/active/meld_state_gate_2026_10_15/component_patch_risk_manager.md
  - system_docs/patches/active/meld_state_gate_2026_10_15/component_patch_registration_call_sites.md
  - system_docs/patches/active/meld_state_gate_2026_10_15/code_description_patch_risk_distillation.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure (the patch docs are promoted to documentation)
"""
LINKS_NEW = """  - system_docs/patches/completed/meld_state_gate_2026_10_15/
- DISPOSITION: retain_as_reference for the artifact folder; promote_to_documentation for the five patch docs
  (promoted at 0.2.8247 to src_architecture, src_components, tests_components, tests_architecture and the graph,
  then archived under system_docs/patches/completed/)
- CLEANUP_TRIGGER: none left - the patch docs are archived; the artifact folder stays as the lane's evidence
"""

HANDOFF_NEW = """## Context / Handoff Summary
Blocked on the owner's acceptance (board: review; {NOW}). Rule 1, Option A, is landed as 0.2.8247:
`register_index` writes `SpellState.non_resolvable` from the selected version's `Spell.resolvable` (bind, notch, the
transfer flip and its rollback pass it) and mirrors it in the registry's published `non_resolvable_index_ids`;
RiskManager's Book flag leaves flagged lineages out with one subset test, and `register_index` re-publishes the
validity when the flag changes on a lineage already gated. Tests A (34), B (11), C (the stub) and D (9) are in the
tree; all 23 chunks passed on a copy of the landed tree with the GIL off and on; a warm meld in a Book with a
definition 15.1 -> 0.26 us (automatic), 16.4 -> 0.73 us (dynamic). Docs: src_architecture, src_components,
tests_components, tests_architecture and their indexes, the graph (five nodes re-accepted), the release note
(0.2.8247), the notch notice; the patch lane is archived under
system_docs/patches/completed/meld_state_gate_2026_10_15/; rubric 83 / 83 / 83 / 77 (B). Rebuild: pending, last.
Holds: the owner's acceptance of rule 1 (reserved); items (2)-(3) (the contract check; a borrower SpellContract
consumer costs about 2 ms a meld) await his answer. melder_0 takes back the four call-site lines and five test
doubles at M1-19. Recorded, not fixed (outside this change): the notch-swap KeyError race, the stale spellbook.py
and transfer_of_ownership.py citations named in src_components' handoff, TransferOfOwnership's unverified graph
node. Not run: coverage.
Next: (1) the owner accepts rule 1 -> closure (completion summary, move to completed/, closed anchor, the artifact
folder kept as reference); (2) the owner's answer on items (2)-(3) opens a successor task or retires them.
"""


def replace_once(text, old, new):
    assert text.count(old) == 1, (old[:70], text.count(old))
    return text.replace(old, new)


raw = PATH.read_bytes()
assert b"\r" not in raw
text = raw.decode("ascii")
text = replace_once(text, "- Status: in_progress\n", "- Status: blocked\n")
text = replace_once(text, "- Updated: 2026-10-16T01:05:44Z\n", f"- Updated: {NOW}\n")
text = replace_once(text, TRANSITION_OLD, TRANSITION_NEW)
text = replace_once(text, VALIDATION_OLD, VALIDATION_NEW)
text = replace_once(text, LINKS_OLD, LINKS_NEW)
start = text.index("## Context / Handoff Summary\n")
end = text.index("\n## Project-Specific Additions")
text = text[:start] + HANDOFF_NEW.replace("{NOW}", NOW) + text[end:]
notes = NOTE_DOCS + NOTE_GRAPH + NOTE_RELEASE + NOTE_RUBRIC + NOTE_REVIEW
anchor = "\n\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
text = text.replace(anchor, "\n" + notes + "\n## Context / Handoff Summary\n")
lines = text.split("\n")
first = next(i for i, l in enumerate(lines, 1) if l == f"- DATETIME: {NOW}")
rubric_end = next(i for i, l in enumerate(lines, 1) if i > first and l == "  NEXT: Move the ticket to review.") + 2
board = pathlib.Path("context_compass/attention_board.md").read_text(encoding="utf-8").split("\n")
row = next(i for i, l in enumerate(board, 1) if l.startswith("| meld_contract_scan |"))
text = text.replace("{NOTES_RANGE}", f"context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_"
                                     f"task.md:{first}-{rubric_end}")
text = text.replace("{ROW_LINE}", f"{row}-{row}")
too_long = [l for l in text.split("\n") if len(l) > 120 and l not in raw.decode("ascii").split("\n")]
assert not too_long, too_long
text.encode("ascii")
if not CHECK:
    PATH.write_bytes(text.encode("ascii"))
print(("checked" if CHECK else "written"), "notes from line", first, "rubric note ends", rubric_end, "board row", row)
