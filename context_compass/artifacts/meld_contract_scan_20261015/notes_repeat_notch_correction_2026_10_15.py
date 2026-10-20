"""Correct the already-gated claim (repeat notch, not first notch-back); record the component tests (melder_1)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
T_REL = "context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
A = "context_compass/artifacts/meld_contract_scan_20261015"
P = CC / "system_docs/patches/active/meld_state_gate_2026_10_15"

PATCH_EDITS = {
    P / "architecture_patch.md": [
        ("   `register_spell`) included. A notch back after a notch to a False version is that case: nothing revalidates\n"
         "   a False version, so the lineage is still `gated`.\n",
         "   `register_spell`) included. A repeat notch is that case: at a notch commit only a member never compiled runs\n"
         "   phases 1-4 (Phase 4 clears the gate), so a notch to a version compiled before leaves the lineage `gated`,\n"
         "   and the notch after it publishes no gate event.\n"),
    ],
    P / "code_description_patch_risk_distillation.md": [
        ("  re-registered, so nothing else would restore it). The lineage is usually still `gated` then (nothing\n"
         "  revalidates a False version), so step 4 publishes nothing and step 5 is that refresh.\n",
         "  re-registered, so nothing else would restore it). After a repeat notch the lineage is still `gated` then (a\n"
         "  notch commit runs phases 1-4 only for a member never compiled), so step 4 publishes nothing and step 5 is that\n"
         "  refresh.\n"),
    ],
}

CORRECTION = """- DATETIME: {now}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Correction to the FACT at lines {a}-{b}: the first notch back does not find the lineage gated. The notch
    commit runs phases 1-4 for a member never compiled, and Phase 4 clears the gate, so after v1 -> def the lineage
    is `valid` and the notch back publishes its gate event. The `gated` registration comes with a repeat notch: the
    commit skips a member compiled before, so v1 -> def -> v1 -> (melds) -> def leaves the lineage `gated` and the
    next notch back publishes nothing. Traced on the scratch tree: with `_republish_validity` disabled, after that
    sequence the index-linked borrower's flag stays down and its meld of v1 skips the gate (v1's verdict stays
    `unknown`); with it, the flag rises and the meld revalidates (`valid`). The re-publication stands, the patch docs
    now say "repeat notch", and the component test runs that sequence (it fails with the re-publication disabled).
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:783-835
  - {art}/runs/probe_borrower_notch_back_gil0.txt:1-24
  - {art}/probe_borrower_notch_back.py:1-114
  - {t_rel}:{a}-{b}
  IMPACT: The gap is real for agents notching back and forth between versions, which is the intended use; the
    earlier note named the wrong trigger.
  NEXT: Record the component results and the mutation checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

MEASURE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Component tests D (9, real wiring): automatic and dynamic worlds with a Protocol definition (flag down, no
    gate entry on the next melds, the definition still refused), an override consumer of a definition, a notch to a
    definition and back, a borrower after a repeat notch, a transfer and a rolled-back transfer, a contract
    consumer that follows its lender's notch beside a definition, and four melder threads racing 40 notches. Green
    with the GIL off and on. Mutation checks: re-publication disabled -> 3 unit and 1 component fail; exclusion
    disabled -> 7 unit and 7 component fail; call-site keywords removed -> 7 component fail. In the race, a binding
    lookup that lands inside a notch's swap raises KeyError "No spell found" (meld's lookups take no Book lock, and
    `_apply_notch` takes the outgoing version off the maps before it puts the incoming one on) - pre-existing and
    unrelated to this change; the test accepts it and the refused definition, and fails on anything else.
  EVIDENCE:
  - tests/component/melder/aether/dev_ops/spell_system_states/test_non_resolvable_validation_flag_component.py:1-453
  - {A}/runs/component_gil0.txt:1-3
  - {A}/runs/component_gil1.txt:1-2
  - {A}/runs/mutation_gil0.txt:1-7
  - src/melder/aether/conduit/meld/meld.py:1960-2009
  - src/melder/aether/spellbook/spellbook.py:3826-3920
  IMPACT: Each part of the change has a test that fails without it; the race shows no definition build and no
    error class the change could cause.
  NEXT: Every chunk with the GIL off and on on the scratch tree, then the probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Fix the two patch-doc sentences, append the correction and the measure."""
    for path, edits in PATCH_EDITS.items():
        text = path.read_text(encoding="utf-8")
        for old, new in edits:
            for line in new.splitlines():
                assert len(line) <= 120, (len(line), line)
            text = one(text, old, new)
        start = text.index("- Updated: ")
        end = text.index("\n", start)
        text = text[:start] + f"- Updated: {NOW}" + text[end:]
        path.write_bytes(text.encode("utf-8"))
    text = T.read_text(encoding="utf-8")
    marker = "  CLAIM: Gap in the mapped design, found while writing the risk tests:"
    a = text[:text.index(marker)].count("\n")  # the DATETIME line sits four lines above the CLAIM
    a = a - 3
    b = a + 24
    lines = text.splitlines()
    assert lines[a - 1].startswith("- DATETIME:"), lines[a - 1]
    assert lines[b - 1] == "  SCORE_0_TO_10: 9", lines[b - 1]
    correction = CORRECTION.format(now=NOW, a=a, b=b, art=A, t_rel=T_REL)
    for block in (correction, MEASURE):
        for line in block.splitlines():
            s = line.lstrip()
            assert len(line) <= 120 or s.startswith(("- src/", "- tests/", "- context_compass/")), (len(line), line)
    text = one(text, "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n",
               "  SCORE_0_TO_10: 9\n" + correction + MEASURE + "\n## Context / Handoff Summary\n")
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    board = CC / "attention_board.md"
    bt = board.read_text(encoding="utf-8")
    bt = one(bt, "| Component tests D on the scratch tree, then every chunk with the GIL off and on and the probe. |",
             "| Every chunk with the GIL off and on on the scratch tree, then the probe before and after. |")
    i = bt.index("| meld_contract_scan | in_progress |")
    j = bt.index("\n", i)
    cells = bt[i:j].split(" | ")
    cells[-2] = NOW
    bt = bt[:i] + " | ".join(cells) + bt[j:]
    board.write_bytes(bt.encode("utf-8"))
    print("recorded", NOW, "corrects", a, b)


if __name__ == "__main__":
    main()
