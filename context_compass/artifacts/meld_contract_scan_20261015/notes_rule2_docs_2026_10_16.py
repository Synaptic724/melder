"""Record rule 2's system-docs pass and the rubric scores; resync the handoff Next and the board row (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"
SD = "context_compass/system_docs"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The four system documents carry rule 2, D1-B, D2 and D3 (0.2.8250), read back from disk with every index
    regenerated and `--check` OK. src_architecture (4696 -> 4854 lines, 62 sections): the Architecture Summary, the
    Meld-Time Validation Gate (steps 8-9) and SpellIndex Mutation Entry (steps 5-6) sequences, a new operational
    invariant (the marks, the downstream walk, D3, the catch-up, cost and lock order), four failure modes (two
    Breaking, one fixed, the known race), the code map (five extents remeasured, two files added), the sources and
    a handoff entry. src_components (11695 -> 11848, 154 sections): dated paragraphs in Spellbook Core, Conduit
    Runtime, ConduitWard and Contracts, Meld Resolution Runtime and SpellCompiler and Validation Pipeline, the Meld
    Runtime Gating and SpellSystemStates Registry C2 entries, the gate and notch flows, seven extents remeasured, the
    sources and a handoff entry. Every numeric citation into the seven changed src files (19 and 26) was remapped
    line by line against the pristine tree with difflib, all exact. tests_components (3584 -> 3697, 69 sections):
    the walk's unit file and the notch-revalidation integration file catalogued as key files with code-map records,
    the Book marks, the gate's catch-up, the report and the explicit mark named in their clusters, four records
    remeasured, counts recounted; it also corrects counts the 0.2.8248-0.2.8249 entries left behind (unit spellbook
    157 -> 158, integration spellbook 50 -> 51, the core section's 838 test modules, a core set of 252 while the
    catalog held 256); the core set is now 258 paths, equal to the code map. tests_architecture (973 -> 988, 32
    sections): the recount, the known race as a non-strict xfail under Failure Modes, a source and a handoff entry.
    After the tests script, one phrase of the walk bullet (a contract cycle) was corrected and two of its lines
    rewrapped by hand on disk. Checks: no package or absolute path; no new line over 120 characters; content
    preservation - every changed or removed baseline multiset entry (51 / 57 / 3 / 23) is a remapped citation, a
    remeasured extent, a recount or a sentence the new text rewrites; the in-bounds recipe over the src pair's 1416
    citations reports only the two bare file names in the 0.2.8247 handoff prose (known).
  EVIDENCE:
  - {SD}/src_architecture.md:1104-1148
  - {SD}/src_architecture.md:2109-2151
  - {SD}/src_architecture.md:4332-4343
  - {SD}/src_components.md:11312-11322
  - {SD}/tests_components.md:952-986
  - {SD}/tests_components.md:3471-3484
  - {SD}/tests_architecture.md:592-598
  - {ART}/land_docs_src_architecture_rule2_2026_10_16.py:1-395
  - {ART}/land_docs_src_components_rule2_2026_10_16.py:1-329
  - {ART}/land_docs_tests_rule2_2026_10_16.py:1-314
  - {ART}/remap_citations_rule2_2026_10_16.py:1-73
  - {ART}/runs/docs_preservation_rule2_2026_10_16.txt:1-138
  - {ART}/runs/citation_bounds_rule2_2026_10_16.txt:1-3
  IMPACT: The documentation half of the turn-in is done; the graph, the patch promotion, the release note, the
    notch, NOTICE M1-21, the owner's acceptance, closure and the rebuild remain.
  NEXT: Re-extract the graph with --strict, re-read the stale nodes of the seven changed files and accept or rewrite
    their prose, then assemble.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rubric scores, from disk after the index rebuilds (self-scored; no independent reviewer), unchanged from the
    0.2.8247 and 0.2.8249 passes: src_architecture 83 (B) - fidelity 4, contract 5, depth 4, addressability 4, join
    4, mirror 4; src_components 83 (B) - 4, 5, 4, 4, 4, 4; tests_architecture 83 (B) - 4, 5, 4, 4, 4, 4;
    tests_components 77 (B) - 4, 4, 3, 4, 4, 4. Basis: src_architecture was re-read whole after this session's
    compaction; in the other three the sections this landing wrote were re-read from disk, and the src_components
    claims spot-checked against the source (`Conduit._activate_borrowed_spell`, `Meld._may_compile`,
    `Meld._is_stale`) hold; the unchanged remainder keeps the earlier judgment. The measurable half (the same
    script, rerun): one H1 each, no duplicate indexed name, no unclosed heading, contracts complete and in order, no
    portability or absolute-path hit, 162 / 36 / 234 / 258 code-map records complete with every extent equal to its
    file today, every Key Files path resolving. Why not 5: fidelity - both src meld-flow diagrams still name
    "Phase12 Compiled Executors" and some older one-line failure modes carry no citation; depth - those lines and
    four src_components entries with thin fields (PhaseScheduler); addressability - container H2s that hold only
    sub-headings; join - 148 of 162, 36 of 36, 221 of 234 and 240 of 258 verified_at stamps carried forward
    although every extent measured equal today; mirror - each pair shares its contract and adds different
    non-contract sections. tests_components contract 4: a Table of Contents and a Component Template sit among its
    sections; depth 3: its Mock Fixture Corpus entry has five thin fields.
  EVIDENCE:
  - {ART}/runs/rubric_checks_rule2_2026_10_16.txt:1-52
  - {ART}/rubric_checks_2026_10_16.py:1-173
  - {SD}/src_architecture.md:4116-4116
  - {SD}/src_components.md:11051-11051
  - {SD}/src_architecture.md:743-743
  - {SD}/src_components.md:5818-5891
  - {SD}/tests_components.md:156-189
  - {SD}/tests_components.md:650-739
  - src/melder/aether/conduit/conduit.py:6267-6310
  - src/melder/aether/conduit/meld/meld.py:1353-1425
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:43-54
  IMPACT: All four documents stay band B and usable as inputs; their weak points predate this landing.
  NEXT: Re-extract the graph with --strict and read its drift report.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
"""

OLD_NEXT_START = "Next: rule 2 with D3 is applied to the real tree"
OLD_NEXT_END = "\n\n## Project-Specific Additions"
NEW_NEXT = """Next: rule 2 with D3 is applied to the real tree - 18 files, byte-identical to the fresh tree that passed every
suite chunk with the GIL off and on; the race test is xfail naming
TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (the owner's decision B). The four system docs
and their indexes carry it (rubric 83 / 83 / 83 / 77, band B). Remaining, in the turn-in order: (1) the graph
descriptors and assembly, the patch docs promoted; (2) the release note, one notch above 0.2.8249 and NOTICE M1-21;
(3) the owner's acceptance, closure and board sync, then the rebuild and its checks last."""

ROW_PREFIX = "| meld_contract_scan | in_progress | implementation | claude | melder_1 | none | "
ROW_NEXT = ("Regenerate the graph and promote the patch docs; then the release note, the notch above 0.2.8249, NOTICE, "
            "owner acceptance, closure, rebuild last.")


def read(path):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("utf-8")


def replace_once(text, old, new, path):
    assert text.count(old) == 1, (str(path), old[:80], text.count(old))
    return text.replace(old, new)


def check_lengths(text, path):
    bad = [l for l in text.split("\n")
           if len(l) > 120 and not l.startswith("|") and not (l.startswith("  - ") and " " not in l[4:])]
    assert not bad, (path, bad)


text = read(TICKET)
assert "The four system documents carry rule 2, D1-B, D2 and D3" not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, TICKET)
i = text.index(OLD_NEXT_START)
j = text.index(OLD_NEXT_END, i)
assert text.count(OLD_NEXT_START) == 1
text = text[:i] + NEW_NEXT + text[j:]
check_lengths(text, TICKET)

board = read(BOARD)
rows = [l for l in board.split("\n") if l.startswith(ROW_PREFIX)]
assert len(rows) == 1, rows
cells = rows[0].split(" | ")
assert cells[9] == "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md", cells[9]
cells[6] = ROW_NEXT
cells[10] = NOW
board = board.replace(rows[0], " | ".join(cells), 1)

print(("CHECK " if CHECK else "WRITE ") + str(TICKET), len(text.split("\n")))
print(("CHECK " if CHECK else "WRITE ") + str(BOARD))
if not CHECK:
    TICKET.write_bytes(text.encode("utf-8"))
    BOARD.write_bytes(board.encode("utf-8"))
