"""Append the docs-pass part-1 MEASURE note to the lane task and bump its Updated stamp.

Usage: python record_docs_part1.py <context_compass root> <UTC timestamp>
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
NOW = sys.argv[2]
TICKET = ROOT / "tickets/tasks/2026-09-30_resolve_injected_provider_on_first_direct_meld_task.md"
NOTE = f"""- DATETIME: {NOW}
  TYPE: MEASURE
  CLAIM: Docs pass, part 1: src_architecture (meld-time gate step 5, the invariant, the failure mode, the code
    map, remeasured citations, the handoff entry) and src_components (the rebuild-window producers, a dated
    "Injected dependencies" block and a lazy-validation bullet in Meld Resolution Runtime, a Phase-5 publication
    bullet in SpellCompiler, the Meld Runtime Gating contract, step 4 of the meld-time flow, the code-map
    extents of spellbook.py and meld.py, the handoff entry) carry option B; both indexes --check OK. The
    src_components edit ran before this session's re-onboarding (disclosed in the attestation). Re-verified: it
    had put the new block between the rebuild-window EVIDENCE and a trailing unresolved-input EVIDENCE bullet,
    so the block now follows that bullet and the old adjacency is restored. Every line citation into
    spellbook.py, spellbook_creation_system.py and meld.py in the four system docs was re-checked by symbol on
    the landed files (spellbook.py 267, 286, 667, 725, 1055-1066, 3650-4136, 5176, 5615-5621, 6448, 6516-6559,
    6772, 7135/7146; the creation system 2055-2083; meld.py 24-27, 276-377, 1134, 1167-1175, 1481-1679). The
    added text names no tooling path.
  EVIDENCE:
  - system_docs/src_architecture.md:728-743
  - system_docs/src_architecture.md:909-923
  - system_docs/src_architecture.md:1398-1402
  - system_docs/src_components.md:3194-3198
  - system_docs/src_components.md:3220-3245
  - system_docs/src_components.md:3514-3520
  - system_docs/src_components.md:3709-3720
  - system_docs/src_components.md:6112-6127
  - system_docs/src_components.md:6933-6942
  IMPACT: The two source documents describe the landed behaviour; tests_components (the two new test files),
    the graph descriptors, the release note, the patch archive and the rebuild remain.
  NEXT: Add the new component and unit test files to tests_components (Protects bullets, Key Files, code map,
    counts) and regenerate its index.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

"""
raw = TICKET.read_bytes()
assert b"\r\n" not in raw
text = raw.decode("utf-8")
anchor = "## Context / Handoff Summary\n"
assert text.count(anchor) == 1
text = text.replace(anchor, NOTE + anchor)
old_updated = "- Updated: 2026-09-30T19:56:47Z\n"
assert text.count(old_updated) == 1
text = text.replace(old_updated, f"- Updated: {NOW}\n")
long = [l for l in NOTE.split("\n") if len(l) > 120]
assert not long, long
TICKET.write_bytes(text.encode("utf-8"))
print("noted", NOW)
