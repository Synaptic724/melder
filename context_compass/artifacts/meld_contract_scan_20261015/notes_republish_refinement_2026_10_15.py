"""Record the already-gated gap and its re-publication refinement; amend the patch docs (melder_1, 2026-10-15)."""
import pathlib
import sys

NOW = sys.argv[1]
ROOT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(".")
CC = ROOT / "context_compass"
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
T_REL = "context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
P = "system_docs/patches/active/meld_state_gate_2026_10_15"
PC = "context_compass/" + P
ARCH = CC / P / "architecture_patch.md"
MODEL = CC / P / "component_patch_spell_state_model.md"
RISK = CC / P / "component_patch_risk_manager.md"
CODE = CC / P / "code_description_patch_risk_distillation.md"

FACT = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Gap in the mapped design, found while writing the risk tests: `set_validity` publishes only a changed
    validity, so `register_index` on a lineage already `gated` publishes no event and the other conduits holding the
    lineage keep their Book flags. That is the normal notch-back case: v1 (True) -> v2 (False) gates the lineage and
    nothing revalidates it (a False version is refused before the gate, and a notch recompiles lazily), so the notch
    back to v1 finds it `gated`. The owner's bucket is refreshed by the `register_spell` that follows the notch, but
    an index-linked borrower gets v1 back through `_reactivate_contracted_spell`, which never calls RiskManager: its
    flag, down while the lineage was flagged, would stay down, and its first meld of v1 would skip the gate although
    `register_index` retired v1's verdicts there. Today that flag stays up and the gate runs.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:349-417
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:517-549
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:307-374
  - src/melder/aether/spellbook/spellbook.py:3826-3920
  - src/melder/aether/spellbook/spellbook.py:1690-1757
  - src/melder/aether/spellbook/spellbook.py:3155-3214
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:410-437
  IMPACT: Unfixed, the exclusion would let a borrower skip the gate after a notch back; invariant 5 must not depend
    on the validity changing.
  NEXT: Amend the patch docs with the re-publication, then the tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

DECISION_TEMPLATE = """- DATETIME: {now}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Refinement inside Option A (same flag, same reader): `register_index` notes whether its capability write
    changed the flag (`update_flags` returns that) and whether the lineage was already `gated`; when both hold it
    calls a new `SpellSystemState._republish_validity()` after the gate, still under the registry lock, which
    publishes the current validity to RiskManager the way `set_validity` does (read under the state lock, published
    outside it, contained). `on_structural_validity_change` then refreshes every conduit holding the lineage, the
    reactivated borrower included. No extra event when the flag did not change or when the gate event fired. Patch
    docs amended (architecture invariant 5 and interface deltas, the state-model and RiskManager component patches,
    the code description); tests gain a unit case for the re-publication and a component notch-back with an
    index-linked borrower.
  EVIDENCE:
  - {t_rel}:{a}-{b}
  - {pc}/architecture_patch.md:1-{n1}
  - {pc}/component_patch_spell_state_model.md:1-{n2}
  - {pc}/component_patch_risk_manager.md:1-{n3}
  - {pc}/code_description_patch_risk_distillation.md:1-{n4}
  IMPACT: A notch back to a resolvable version counts the lineage again in every conduit, whether or not its gate
    was already closed.
  NEXT: Test B (RiskManager on a real registry) and the stub update, then the four melder_1 files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HANDOFF = (
    f"In progress ({NOW}). Option A approved for rule 1, mapped and specified: patch docs under\n"
    "system_docs/patches/active/meld_state_gate_2026_10_15/ (linked; mapping in the PLAN Note; the re-publication for a\n"
    "lineage already gated in the last two Notes). The four call sites (bind, notch, transfer flip and rollback) are\n"
    "melder_0's: handoff through the owner; until then the change is built and validated on the scratch tree\n"
    "/tmp/cc_res/nonres/tree and nothing lands in the real tree. Unit test A is written there and red. Items (2)-(3),\n"
    "the contract check, still await his answer. Next: test B and the stub update, then the four melder_1 files.\n"
)

EDITS = {
    ARCH: [
        ("- Updated: 2026-10-15T21:00:00Z", f"- Updated: {NOW}"),
        ("| SpellSystemState | `update_flags` (flags only, publishes nothing) and `has_flag` | melder_1 |",
         "| SpellSystemState | `update_flags` (flags only, publishes nothing, says whether they changed), `has_flag` "
         "and `_republish_validity` | melder_1 |"),
        ("5. Transitions take effect at the gated event `register_index` already publishes: a notch to a resolvable=False\n"
         "   version excludes the lineage, and a notch back counts it again with the risk the sets kept.\n",
         "5. Transitions take effect at the gated event `register_index` already publishes: a notch to a resolvable=False\n"
         "   version excludes the lineage, and a notch back counts it again with the risk the sets kept. `set_validity`\n"
         "   publishes only a changed validity, so when the lineage was already `gated` and the capability write changed\n"
         "   the flag, `register_index` re-publishes the current validity itself (`SpellSystemState._republish_validity`):\n"
         "   every bucket holding the lineage refreshes, a borrower whose copy came back by reactivation (no\n"
         "   `register_spell`) included. A notch back after a notch to a False version is that case: nothing revalidates\n"
         "   a False version, so the lineage is still `gated`.\n"),
        ("- Internal: `SpellState.non_resolvable`; `SpellSystemState.update_flags(*, flags_to_add=None, flags_to_remove=None)`\n"
         "  and `SpellSystemState.has_flag(flag)`; `SpellSystemStates.register_index(spell_index, owner_spellbook_id=None, *,\n"
         "  resolvable=None)` (TypeError for a non-bool) and `SpellSystemStates.index_has_flag(index_id, flag)`; two private\n"
         "  RiskManager helpers.\n",
         "- Internal: `SpellState.non_resolvable`; `SpellSystemState.update_flags(*, flags_to_add=None, flags_to_remove=None)\n"
         "  -> bool`, `SpellSystemState.has_flag(flag)` and `SpellSystemState._republish_validity()`;\n"
         "  `SpellSystemStates.register_index(spell_index, owner_spellbook_id=None, *, resolvable=None)` (TypeError for a\n"
         "  non-bool) and `SpellSystemStates.index_has_flag(index_id, flag)`; two private RiskManager helpers.\n"),
        ("| 5 | unit: a False -> True registration raises the flag at the gated event; component: notch both ways |",
         "| 5 | unit: a False -> True registration raises the flag at the gated event; a flag change on a lineage already "
         "gated re-publishes once and refreshes every bucket; component: notch both ways, and a notch back with an "
         "index-linked borrower |"),
        ("- What changed: the patch is written; nothing in `src/` yet.\n",
         f"- What changed: the patch is written; nothing in `src/` yet. Amended {NOW}: invariant 5 re-publishes when\n"
         "  the gate was already closed (found while writing the risk tests).\n"),
    ],
    MODEL: [
        ("- Updated: 2026-10-15T21:00:00Z", f"- Updated: {NOW}"),
        ("    `transitively_dirty` and `last_validated_at` alone. It publishes nothing: flag-only updates stay local, as\n"
         "    `set_validity`'s contract already says.\n",
         "    `transitively_dirty` and `last_validated_at` alone. It publishes nothing: flag-only updates stay local, as\n"
         "    `set_validity`'s contract already says. It returns whether the flag set changed.\n"
         "  - `SpellSystemState._republish_validity()`: reads the validity under the state lock and publishes it to the\n"
         "    attached RiskManager outside that lock, contained like `set_validity`'s publication; it changes nothing. The\n"
         "    registry calls it when a flag that RiskManager reads changed while the validity did not.\n"),
        ("    a different version than the state tracked, and keeps it otherwise. Everything else is unchanged: the spell-id\n"
         "    index, the verdict retirement, the owner index, the gate and the dirty set.\n",
         "    a different version than the state tracked, and keeps it otherwise. Everything else is unchanged: the spell-id\n"
         "    index, the verdict retirement, the owner index, the gate and the dirty set. When the write changed the flag\n"
         "    and the lineage was already `gated` (so the gate publishes no event), it then calls `_republish_validity()`,\n"
         "    still under the registry lock.\n"),
        ("1. The flag is written before `mark_structural_change`, so the RiskManager callback that the gate publishes already\n"
         "   sees it.\n",
         "1. The flag is written before `mark_structural_change`, so the RiskManager callback that the gate publishes already\n"
         "   sees it; a gate that publishes nothing (already `gated`) is followed by `_republish_validity()` when the flag\n"
         "   changed.\n"),
        ("  a new state, TypeError leaves the registry unchanged; `unregister_index` removes it; `index_has_flag` for empty,\n"
         "  unknown and registered ids.\n",
         "  a new state, TypeError leaves the registry unchanged; `unregister_index` removes it; `index_has_flag` for empty,\n"
         "  unknown and registered ids; a flag change on a lineage already `gated` publishes exactly one event, carrying the\n"
         "  new flag, and an unchanged flag publishes none.\n"),
        ("- What changed: written before any edit.\n- Remaining risks: none in these files;",
         f"- What changed: written before any edit; amended {NOW} with `_republish_validity` and the result of\n"
         "  `update_flags`.\n- Remaining risks: none in these files;"),
    ],
    RISK: [
        ("- Updated: 2026-10-15T21:00:00Z", f"- Updated: {NOW}"),
        ("  registration that clears the flag raises the flag at the gated event with the kept resolution risk; register_conduit\n"
         "  sets the flag once.\n",
         "  registration that clears the flag raises the flag at the gated event, or at the re-published one when the\n"
         "  lineage was already gated, with the kept resolution risk; register_conduit sets the flag once.\n"),
    ],
    CODE: [
        ("- Updated: 2026-10-15T21:00:00Z", f"- Updated: {NOW}"),
        ("3. Still under the registry lock, write the capability (`update_flags`, state lock inside): False -> add\n"
         "   `non_resolvable`; True -> remove; None -> remove unless the selection was kept. No publication.\n",
         "3. Still under the registry lock, write the capability (`update_flags`, state lock inside): False -> add\n"
         "   `non_resolvable`; True -> remove; None -> remove unless the selection was kept. No publication; note whether\n"
         "   the flag set changed and whether the validity is already `gated`.\n"),
        ("   lock. Add to the dirty set (as before).\n",
         "   lock. Add to the dirty set (as before).\n"
         "5. When step 3 changed the flag and the validity was already `gated` (step 4 published nothing), call\n"
         "   `state._republish_validity()`: the same callback with the current validity, under the registry lock and\n"
         "   contained like step 4's, so every bucket holding the lineage refreshes with the new flag.\n"),
        ("  lineage again, with the resolution risk the sets kept while it was flagged (a reactivated borrowed copy is never\n"
         "  re-registered, so nothing else would restore it).\n",
         "  lineage again, with the resolution risk the sets kept while it was flagged (a reactivated borrowed copy is never\n"
         "  re-registered, so nothing else would restore it). The lineage is usually still `gated` then (nothing\n"
         "  revalidates a False version), so step 4 publishes nothing and step 5 is that refresh.\n"),
        ("- Registering again with the same capability changes nothing on the flag; `update_flags` is idempotent.\n",
         "- Registering again with the same capability changes nothing on the flag and publishes nothing extra;\n"
         "  `update_flags` is idempotent.\n"),
        ("- Notch False -> True on a borrower whose copy is reactivated: the borrower's flag rises.\n",
         "- Notch False -> True on a borrower whose copy is reactivated: the borrower's flag rises, also when the lineage was\n"
         "  already `gated` (step 5).\n"),
        ("- What changed: written before any edit.\n- Remaining unknowns: none.\n",
         f"- What changed: written before any edit; step 5 added {NOW} (found while writing the risk tests).\n"
         "- Remaining unknowns: none.\n"),
    ],
}


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:70])
    return text.replace(old, new, 1)


def check_width(block: str) -> None:
    """Prose lines stay within the 120-character hard cap; path lines and table rows are exempt."""
    for line in block.splitlines():
        s = line.lstrip()
        if s.startswith(("- src/", "- context_compass/", "EVIDENCE:", "|")):
            continue
        assert len(line) <= 120, (len(line), line)


def main() -> None:
    """Amend the patch docs, append the two notes, refresh the handoff and the board row."""
    for path, edits in EDITS.items():
        text = path.read_text(encoding="utf-8")
        for old, new in edits:
            check_width(new)
            text = one(text, old, new)
        path.write_bytes(text.encode("utf-8"))
    check_width(FACT)
    check_width(HANDOFF)
    text = T.read_text(encoding="utf-8")
    anchor = "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n"
    text = one(text, anchor, "  SCORE_0_TO_10: 9\n" + FACT + "\n## Context / Handoff Summary\n")
    fact_start = text[:text.index(FACT)].count("\n") + 1
    fact_end = fact_start + FACT.count("\n") - 1
    counts = [len(p.read_text(encoding="utf-8").splitlines()) for p in (ARCH, MODEL, RISK, CODE)]
    decision = DECISION_TEMPLATE.format(now=NOW, t_rel=T_REL, a=fact_start, b=fact_end, pc=PC,
                                        n1=counts[0], n2=counts[1], n3=counts[2], n4=counts[3])
    check_width(decision)
    text = one(text, FACT + "\n## Context / Handoff Summary\n", FACT + decision + "\n## Context / Handoff Summary\n")
    h0 = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    h1 = text.index("\n## Project-Specific Additions")
    text = text[:h0] + HANDOFF + text[h1:]
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    board = CC / "attention_board.md"
    b = board.read_text(encoding="utf-8")
    b = one(b, "| Red tests and the SpellState.non_resolvable change on the scratch tree; suites GIL off and on. |",
            "| Test B and the stub update, then the four melder_1 files on the scratch tree; suites GIL off and on. |")
    i = b.index("| meld_contract_scan | in_progress |")
    j = b.index("\n", i)
    cells = b[i:j].split(" | ")
    cells[-2] = NOW
    b = b[:i] + " | ".join(cells) + b[j:]
    board.write_bytes(b.encode("utf-8"))
    print("recorded", NOW, "fact", fact_start, fact_end, "docs", counts)


if __name__ == "__main__":
    main()
