"""Link the patch docs, record the patch-section mapping, row the docs on the artifact board (melder_1, 2026-10-15)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
TASK_REL = "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
P = "system_docs/patches/active/meld_state_gate_2026_10_15"
PC = "context_compass/" + P
DOCS = (
    ("architecture_patch.md", "Objective, non-goals, seven invariants, interface deltas, migration order, rollback, "
                              "coverage matrix, risks; the call-site handoff request."),
    ("component_patch_spell_state_model.md", "SpellState.non_resolvable, SpellSystemState.update_flags/has_flag, "
                                             "register_index(resolvable=...) and index_has_flag; before/after, "
                                             "ordering, validation."),
    ("component_patch_risk_manager.md", "The Book flag ignores flagged lineages at distillation (sets unchanged); "
                                        "register_conduit refreshes once; validation."),
    ("component_patch_registration_call_sites.md", "The four register_index keywords in melder_0's files (bind, "
                                                   "notch, transfer flip and rollback); pending the handoff."),
    ("code_description_patch_risk_distillation.md", "Control flow of the write and the distillation, transitions, "
                                                    "locks, edge semantics, invariants."),
)

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written and linked (Artifact Links); read order architecture -> the three component patches -> the
    code description; no conflict with each other or with the canonical docs (src_architecture's meld-time gate and
    RiskManager text describe today's flag, which the landing amends). Mapping, patch section -> implementation ->
    validation: (1) arch invariants 1-2 and component_patch_spell_state_model -> spell_state.py (the member and its
    docstring), spell_system_state.py (`update_flags`, `has_flag`), spell_system_states.py (`register_index`'s
    keyword and its capability write, `index_has_flag`, docstrings) -> unit tests for the state and the registry.
    (2) Invariants 3, 5 and 7, component_patch_risk_manager and the code description -> risk_manager.py
    (`_register_spell_risk`, one refresh in `register_conduit`, the snapshot and `_has_unexcluded_risk` in
    `_refresh_spellbook_flag`, docstrings) -> unit tests on a real registry; the old stub gains `index_has_flag`.
    (3) Invariant 4 and component_patch_registration_call_sites -> the four keywords (scratch tree until the
    handoff) -> component tests: automatic and dynamic worlds, notch both ways, transfer and rollback, an override
    consumer, a borrower, and melds racing notches. (4) Invariant 6 -> review and that race test. (5) Invariant 7 ->
    the probe before and after. (6) Landing -> src_architecture and src_components, the SpellState graph descriptor
    (its stale `new_lineage` too), the release note, the notch, the rebuild.
  EVIDENCE:
  - {PC}/architecture_patch.md:1-103
  - {PC}/component_patch_spell_state_model.md:1-81
  - {PC}/component_patch_risk_manager.md:1-70
  - {PC}/component_patch_registration_call_sites.md:1-65
  - {PC}/code_description_patch_risk_distillation.md:1-72
  IMPACT: The entry gate for the melder_1 files is met; the call sites wait for the owner's handoff.
  NEXT: Red tests and the change on the scratch tree (/tmp/cc_res/nonres/tree), then the suites with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HANDOFF = (
    f"In progress ({NOW}). Option A approved for rule 1, mapped and specified: patch docs under\n"
    "system_docs/patches/active/meld_state_gate_2026_10_15/ (linked; mapping in the last Note). The four call sites\n"
    "(bind, notch, transfer flip and rollback) are melder_0's: handoff through the owner; until then the change is\n"
    "built and validated on the scratch tree /tmp/cc_res/nonres/tree and nothing lands in the real tree. Items (2)-(3),\n"
    "the contract check, still await his answer. Next: red tests and the change on the scratch tree.\n"
)


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Link the docs, append the mapping note, refresh the handoff; row the docs; refresh the board's next."""
    for line in NOTE.splitlines() + HANDOFF.splitlines():
        assert len(line) <= 120 or line.lstrip().startswith(("- src/", "- context_compass/", "EVIDENCE:")), (
            len(line), line)
    text = T.read_text(encoding="utf-8")
    links = "".join(f"  - {P}/{name}\n" for name, _ in DOCS)
    text = one(text, f"  - {P}/ (once written)\n", links)
    text = one(text, "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n",
               "  SCORE_0_TO_10: 9\n" + NOTE + "\n## Context / Handoff Summary\n")
    h0 = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    h1 = text.index("\n## Project-Specific Additions")
    text = text[:h0] + HANDOFF + text[h1:]
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    art = CC / "artifact_board.md"
    a = art.read_text(encoding="utf-8")
    rows = "".join(
        f"| {TASK_REL} | {P}/{name} | patch_doc | active | promote_to_documentation | {desc} | {NOW} | REQUIRED |\n"
        for name, desc in DOCS
    )
    a = one(a, "<!-- END USER-DEFINED: active_artifacts -->", rows + "<!-- END USER-DEFINED: active_artifacts -->")
    art.write_bytes(a.encode("utf-8"))
    board = CC / "attention_board.md"
    b = board.read_text(encoding="utf-8")
    b = one(b, "| Write the patch docs for SpellState.non_resolvable (map in Notes), then build it on a scratch tree. |",
            "| Red tests and the SpellState.non_resolvable change on the scratch tree; suites GIL off and on. |")
    i = b.index("| meld_contract_scan | in_progress |")
    j = b.index("\n", i)
    cells = b[i:j].split(" | ")
    cells[-2] = NOW
    b = b[:i] + " | ".join(cells) + b[j:]
    board.write_bytes(b.encode("utf-8"))
    print("recorded", NOW)


if __name__ == "__main__":
    main()
