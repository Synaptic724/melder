"""Append the design-phase findings to the successor task and refresh its handoff and the board's next (melder_1)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
R = "src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py"
M = "src/melder/aether/conduit/meld/meld.py"
S = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"
W = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
B = "src/melder/aether/spellbook/spellbook.py"
A = "context_compass/artifacts/meld_contract_scan_20261015"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: RiskManager, read whole. Spells enter a conduit's bucket only through `register_spell` (conjure end via
    `register_conduit`, bind, notch, contract add, transfer), always with the actual Spell object, so the active
    version's `resolvable` is at hand; later changes arrive as structural and resolution validity events keyed by
    lineage. Nothing reads `resolvable`, and `_is_risky` counts anything but `valid`. A resolvable=False version gets
    no verdict (left out of planning, refused at meld), so it reads `unknown` for good; a dependency or bind change can
    also gate it structurally, and nothing ever revalidates it. The same flag guards the fast doors: ConduitMeld,
    SpellSpaceMeld, SpellSpace and Conduit only serve a warm meld from the door while the flag is down, so one such
    definition also takes every automatic meld off the fast door.
  EVIDENCE:
  - {R}:251-283
  - {R}:320-366
  - {R}:410-471
  - {R}:574-655
  - src/melder/aether/spellbook/spell.py:767-784
  - src/melder/aether/conduit/meld/conduit_meld.py:436-500
  - {B}:3906-3919
  IMPACT: Rule 1 fits RiskManager alone: track the lineages whose active version is resolvable=False and let them hold
    no risk on either axis; no other surface changes, and Nexus reads none of this.
  NEXT: Measure the cost the rule removes, with the exclusion emulated in a probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The contract state already exists, and one path bypasses it. Phase 3 records each SpellContract socket in a
    per-Book reverse index (key -> consumer lineages); Phase 4 marks a consumer `gated` + `contract_unvalidated` when
    its provider is missing and clears the flag when present; `mark_contract_dependents_dirty` gates the consumers of a
    key, and it runs on link (change-control commit hook), grant, uncontract, sever and remove-all (ward invalidation).
    Phase 9 bakes the provider's spell id into the consumer's plan, so a provider change needs a rebuild. When a lender
    notches an index-linked spell, or parks a version-anchored copy, the owner's fan-out ends in the borrower Book's
    contracted-map mutators (park, reactivate, add), and none of them marks the key's consumers. Today the meld's
    unconditional scan papers over that: it forces a 5-11 rebuild of every contract consumer on every gated meld.
  EVIDENCE:
  - {S}:1309-1389
  - {S}:1391-1447
  - {S}:1532-1556
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:147-177
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:840-873
  - {W}:2682-2740
  - {W}:2316-2380
  - src/melder/aether/conduit/conduit.py:5907-5936
  - {B}:1623-1751
  - {B}:1809-1842
  - {B}:3155-3214
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:185-298
  - {M}:933-988
  - {M}:1311-1474
  IMPACT: Rule 2 is safe only if the borrower marks the key's consumers wherever its active contracted copy changes;
    then the structural branch (Phase 4 presence, structure_changed rebuild) does everything the scan did.
  NEXT: Measure today's consumer cost and whether a consumer follows a lender notch without the scan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Design probe (live repo, Python 3.14.7t, GIL off / on; monkeypatches only). A Protocol definition bound
    resolvable=False pins the flag in automatic worlds too: 22.8 / 19.1 us per meld, 0.3 us with the exclusion
    emulated (the fast door comes back); dynamic 27.9 / 20.7 -> 0.9 / 0.8 us. A SpellContract consumer in a borrower
    Book costs 2663 / 2354 us per meld today: the borrowed provider's lineage stays `unknown` in the borrower and pins
    its flag, and every meld forces the consumer's 5-11 rebuild; with the scan removed it is 2.0 / 1.9 us. But with the
    scan removed the consumer keeps getting version A after the lender notches to B (and its lineage reads `valid`):
    today the consumer follows a notch only through the per-meld rebuild.
  EVIDENCE:
  - {A}/runs/probe_design_baseline_gil0.txt:1-21
  - {A}/runs/probe_design_baseline_gil1.txt:5-25
  - {A}/probe_design_baseline.py:1-269
  IMPACT: Both rules are large wins (60x for automatic worlds with a definition, ~1300x for contract consumers); rule 2
    needs the borrower-side marking or consumers stop following a notch.
  NEXT: Propose the design to the owner with the decisions it needs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Proposed design, for the owner. (1) RiskManager keeps a per-conduit set of lineages whose active version is
    resolvable=False; `register_spell` puts a lineage there (or takes it out when a resolvable version becomes active)
    and clears its risk, and both validity updates ignore lineages in it. (2) The meld drops the unconditional scan and
    the forced rebuild; a contract change reaches the meld through the consumer's state, and the scan runs only on the
    failure path, to raise today's MeldExecutionError ("SpellContract could not be resolved ... param ... key") when a
    rerun leaves the lineage `contract_unvalidated`. (3) The borrower Book marks the key's consumers `gated` +
    `contract_unvalidated` wherever its active contracted copy changes (add, park, reactivate, remove), which covers
    notch, notch back, park and destroy; gate only, so stored consumer objects keep their provider, as today. Asks:
    approve (1)-(3); gate-only on a notch rather than also dropping stored consumers as grant and sever do; and the
    handoff of spellbook.py (melder_0's file; (3) is about ten lines there). Borrowed spells still hold a borrower's
    flag until melded there; that is correct and costs about 2 us per meld after the fix; no change proposed.
  EVIDENCE:
  - {A}/runs/probe_design_baseline_gil0.txt:1-21
  - {M}:933-988
  - {R}:320-366
  - {B}:1623-1751
  IMPACT: Rules 1 and 2 hold without new states; files: RiskManager, Meld, the Book's contracted maps, their tests,
    system docs, release note, notch, rebuild.
  NEXT: The owner's answers; then the patch docs under system_docs/patches/active/meld_state_gate_2026_10_15/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HANDOFF = (
    f"In progress ({NOW}). Design proposed to the owner (last Note): RiskManager ignores\n"
    "resolvable=False active versions; the meld drops the per-meld contract scan; the borrower Book marks contract\n"
    "consumers when its active contracted copy changes. Measured by emulation: 22.8 -> 0.3 us (automatic world with a\n"
    "definition), 2663 -> 2.0 us (contract consumer). Nothing in `src/` has changed. Next: the owner's answers, then\n"
    "the patch docs; spellbook.py needs melder_0's handoff.\n"
)


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Write the notes, the handoff, the Updated stamp and the board's next."""
    for line in NOTES.splitlines() + HANDOFF.splitlines():
        assert len(line) <= 120 or line.lstrip().startswith(("- src/", "- context_compass/")), (len(line), line)
    text = T.read_text(encoding="utf-8")
    text = one(text, "  SCORE_0_TO_10: 8\n\n## Context / Handoff Summary\n",
               "  SCORE_0_TO_10: 8\n" + NOTES + "\n## Context / Handoff Summary\n")
    h0 = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    h1 = text.index("\n## Project-Specific Additions")
    text = text[:h0] + HANDOFF + text[h1:]
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    board = CC / "attention_board.md"
    b = board.read_text(encoding="utf-8")
    old_next = ("| Read RiskManager's callers and the contract state machinery whole; propose the design to the owner. |")
    new_next = ("| Owner answers the design (last Note): exclusion, no per-meld scan, borrower-side marking; then patch "
                "docs. |")
    b = one(b, old_next, new_next)
    i = b.index("| meld_contract_scan | in_progress |")
    j = b.index("\n", i)
    row = b[i:j]
    cells = row.split(" | ")
    cells[-2] = NOW
    b = b[:i] + " | ".join(cells) + b[j:]
    board.write_bytes(b.encode("utf-8"))
    print("notes written", NOW)


if __name__ == "__main__":
    main()
