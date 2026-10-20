"""Record the scratch-tree red/green and the test doubles the call sites reach (melder_1, 2026-10-15)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
A = "context_compass/artifacts/meld_contract_scan_20261015"

FACT = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The four call-site keywords reach five test doubles in melder_0's lanes that mirror the old signature or lack
    `Spell.resolvable`: two `register_index` lambdas in test_spellbook.py, the fake registry and `build_spell` of both
    transfer unit files, and the fake registries of two component spellbook files. With only the keywords applied, 45
    unit tests failed (AttributeError 'resolvable' on a SimpleNamespace spell, TypeError on the lambdas). A real Spell
    always carries `resolvable` (default True) and the real registry takes the keyword, so the doubles are corrected
    to mirror that (keyword accepted, `resolvable=True` on the built spell; the bind lambda records the value and
    the test asserts bind passes it). No production fallback is added. These five test files join the handoff.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook.py:2435-2435
  - tests/unit/melder/spellbook/test_spellbook.py:2503-2503
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:122-135
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1069-1108
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:120-133
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:1020-1059
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:555-566
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:110-121
  - {A}/runs/callsites_gil0.txt:1-2
  IMPACT: The handoff covers the four keyword lines plus the doubles in these five test files; apply_call_sites.py
    applies both.
  NEXT: Component tests D on the scratch tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
"""

MEASURE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Scratch tree (synced to the real tree at 0.2.8246 first; Python 3.14.7t), red then green. Unit test A (28:
    flags, `register_index`, the re-publication, `index_has_flag`) and B (11: the distillation on a real registry)
    were red - A 28 failed; B 11 failed, then 8 failed and 3 passed after the state-model change (the 3 are the
    unchanged-behaviour guards). The stub C gained `index_has_flag`. The four melder_1 files are written by
    apply_state_model.py and apply_risk_manager.py, the call sites and doubles by apply_call_sites.py (exact-text
    edits that refuse a missing anchor, to be re-run on the real tree). Green: A 28, risk_manager 32, dev_ops unit
    742 with the GIL off and on; with the call sites, GIL off: unit_aether 4460 (4421 + 39 new), unit_sb 2560,
    comp_sb 819, comp_aether 1377 + 1 xfailed, int_aether 785 + 5 xfailed, int_conduit 335 - the baseline counts.
  EVIDENCE:
  - {A}/runs/red_gil0.txt:1-5
  - {A}/runs/green_gil0.txt:1-3
  - {A}/runs/green_gil1.txt:1-1
  - {A}/runs/callsites_gil0.txt:3-8
  - {A}/runs/baseline_gil0.txt:1-6
  - {A}/apply_state_model.py:1-460
  - {A}/apply_risk_manager.py:1-252
  IMPACT: The change holds on the unit, component and integration chunks run so far; the rest of the tree and GIL on
    are still to run.
  NEXT: Component tests D (worlds, notch both ways, transfer, borrower notch-back, races), then every chunk GIL 0 and 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HANDOFF = (
    f"In progress ({NOW}). Option A approved for rule 1, mapped and specified: patch docs under\n"
    "system_docs/patches/active/meld_state_gate_2026_10_15/ (linked; mapping in the PLAN Note; the re-publication for a\n"
    "lineage already gated in the two Notes after it). On the scratch tree /tmp/cc_res/nonres/tree the four melder_1\n"
    "files, the four call-site keywords and the five test doubles they reach are applied (apply_*.py in the artifacts)\n"
    "and the unit, component and integration chunks run so far are green. The call sites and those test files are\n"
    "melder_0's: handoff through the owner; nothing lands in the real tree before it. Items (2)-(3), the contract\n"
    "check, still await his answer. Next: component tests D, then every chunk with the GIL off and on, the probe.\n"
)


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Append the two notes, refresh the handoff and the Updated stamp, refresh the board row."""
    for block in (FACT, MEASURE, HANDOFF):
        for line in block.splitlines():
            s = line.lstrip()
            assert len(line) <= 120 or s.startswith(("- src/", "- tests/", "- context_compass/")), (len(line), line)
    text = T.read_text(encoding="utf-8")
    text = one(text, "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n",
               "  SCORE_0_TO_10: 9\n" + FACT + MEASURE + "\n## Context / Handoff Summary\n")
    h0 = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    h1 = text.index("\n## Project-Specific Additions")
    text = text[:h0] + HANDOFF + text[h1:]
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    board = CC / "attention_board.md"
    b = board.read_text(encoding="utf-8")
    b = one(b, "| Test B and the stub update, then the four melder_1 files on the scratch tree; suites GIL off and on. |",
            "| Component tests D on the scratch tree, then every chunk with the GIL off and on and the probe. |")
    i = b.index("| meld_contract_scan | in_progress |")
    j = b.index("\n", i)
    cells = b[i:j].split(" | ")
    cells[-2] = NOW
    b = b[:i] + " | ".join(cells) + b[j:]
    board.write_bytes(b.encode("utf-8"))
    print("recorded", NOW)


if __name__ == "__main__":
    main()
