"""Record the state-system map for SpellState.non_resolvable and the refined design (melder_1, 2026-10-15)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
ST = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states"
RM = "src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py"
SB = "src/melder/aether/spellbook/spellbook.py"
TR = "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py"
CM = "src/melder/aether/conduit/meld"
SS = "src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py"
CW = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
TASK = "context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"

MAP_NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: State-system map, producer side (read whole). `SpellSystemStates.register_index` is the only call that
    (re)registers a lineage's selected version: it reuses an existing state (its flags survive) and creates one only
    for a new index, retires the verdicts held for the selected id, then gates the index; the gate publishes to
    RiskManager outside the state lock but inside the registry lock. Callers: bind and notch, each followed by
    `register_spell` for the owner conduit, and three transfer sites - the flip unregisters the lineage and registers
    it again on the same frame registry, so a transferred lineage gets a fresh state and loses every flag; the
    rollback re-registers (a fresh state only when the two Books use different registries); the disable step
    registers a missing state. SpellIndex holds ids only, so the capability must come from the caller, and all five
    call sites are in melder_0's files. Flag writers today: the state's topology helpers and `clear_dirty` (topology
    flags only), contract marking, Phase 4 and the structural-snapshot replay (`contract_unvalidated`), transfer
    (`transfer_in_progress`). Readers: the meld gate (`transfer_in_progress`) and the snapshot capture
    (`contract_unvalidated`). No Crystallizer, Nexus or MutationResearch reader; snapshot rows carry no other flag
    and replay touches no other flag; no test enumerates the members; the graph descriptor lists them (with a stale
    `new_lineage`).
  EVIDENCE:
  - {ST}/spell_system_states.py:307-374
  - {ST}/spell_system_state.py:349-417
  - {ST}/spell_system_state.py:517-549
  - {ST}/spell_system_state.py:613-666
  - {ST}/spell_system_states.py:765-871
  - {SB}:5686-5694
  - {SB}:3904-3919
  - {TR}:855-891
  - {TR}:958-1002
  - {TR}:1443-1491
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:153-177
  - {SS}:388-426
  - {SS}:672-702
  - {CM}/meld.py:1174-1244
  - src/melder/_build_assets/_system_documents/payloads/src_graph_payload.py:3115-3125
  IMPACT: register_index can set the flag before it gates, so every risk bucket sees it when the gated event
    publishes; the transfer flip must pass the capability or a transferred definition pins the flag again.
  NEXT: Map the consumer side (RiskManager, the meld doors, borrowers).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: State-system map, consumer side (read whole). RiskManager mirrors validity per (conduit, lineage) in two
    sets and computes resolution risk for the lineage's selected version id, so a lineage flag that describes the
    selected version matches how risk is already computed. It never holds its lock while calling the registry; the
    registry calls it under the registry lock; ConduitResolutionState publishes outside its lock. The Book flag is
    read only by the meld doors and the gate. Exclusion is safe: every meld door refuses a resolvable=False target
    before the flag-guarded gate (ConduitMeld, SpellSpaceMeld and both reuse paths), and warm doors are minted only
    after admission; a borrower's active copy is the owner's active member when contracted, and after a lender
    notch the conduit parks or moves borrowers' copies once the transaction ends - in that window a borrower can
    meld its old copy, whose plan survives (`_cleanup_creation_context` clears only the context). Today a False
    lineage stays in the resolution-risk set for good, and a reactivated borrowed copy is never re-registered with
    RiskManager: if the exclusion emptied the sets, a notch from a False to a True version would leave reactivated
    borrowers with no resolution risk for the new version. While the flag is up every meld runs
    `_ensure_lineage_resolvable`, whose contract scan rebuilds each SpellContract consumer per meld: a Book held up
    only by False definitions loses that per-meld rebuild and behaves like the same Book without them.
    `register_conduit` refreshes once per seeded spell. Pre-existing: refreshes set the Book flag outside the manager
    lock, so two can land out of order; a removed lineage is risky until `unregister_spell` drops it.
  EVIDENCE:
  - {RM}:251-283
  - {RM}:320-366
  - {RM}:410-471
  - {RM}:527-571
  - {RM}:624-655
  - {ST}/conduit_resolution_state.py:271-325
  - {CM}/conduit_meld.py:436-443
  - {CM}/conduit_meld.py:559-580
  - {CM}/conduit_meld.py:821-822
  - {CM}/spellspace_meld.py:514-526
  - {CM}/spellspace_meld.py:766-767
  - {CW}:1986-1995
  - {CW}:2475-2482
  - src/melder/aether/conduit/conduit.py:5693-5710
  - src/melder/aether/spellbook/spell.py:942-969
  - {SB}:1623-1751
  - {SB}:3155-3214
  - {CM}/meld.py:933-988
  - {SB}:684-712
  IMPACT: The exclusion belongs where the Book flag is distilled: the risk sets keep tracking exactly as today and
    only the flag ignores flagged lineages, so a notch back to a resolvable version counts again at once.
  NEXT: Record the refined design and the call-site handoff, then write the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

DECISION_TEMPLATE = """- DATETIME: {now}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Option A as mapped (refinements inside the approved design; no new concept). (a) `SpellState.non_resolvable`
    is appended and owned by `register_index`; validation never clears it; its only effect is that RiskManager's
    Book flag ignores a flagged lineage's risk - validity, the other flags and every other reader are unchanged.
    (b) `register_index(..., *, resolvable: Optional[bool] = None)`: False sets the flag, True clears it, None keeps
    it only while the selected version is unchanged (a new state, or a changed selection without a capability,
    clears it, so a stale exclusion can never cover a resolvable version); a non-bool raises TypeError; the flag is
    written before `mark_structural_change`, through a new flag-only `SpellSystemState.update_flags` (no publish), and
    read through a new `has_flag`. (c) RiskManager: `_refresh_spellbook_flag` raises the flag only for a risky key
    that is not a lineage whose state has the flag ("spell:" keys and missing states count, as today); the reads run
    outside the manager lock, as its validity reads already do; `register_conduit` seeds and then refreshes once, so
    conjure pays no spells-times-definitions cost. (d) Call sites: bind and notch pass `resolvable=<spell>.resolvable`;
    the transfer flip and its rollback pass `spell_obj.resolvable`; the disable step stays (a missing state is
    conservative). Those are four one-keyword edits in melder_0's files (spellbook.py x2, transfer_of_ownership.py
    x2): the handoff goes through the owner. (e) Until it is granted, the whole change - those four edits included -
    is built and validated on a scratch copy of the tree (suites with the GIL off and on, the probe), and nothing
    lands in the real tree, so no inert half can reach a commit without its notch.
  EVIDENCE: {task}:{start}-{end}
  IMPACT: Patch docs and a validated prototype next; landing (tests, docs, notch, release note, rebuild) follows the
    handoff.
  NEXT: Write the patch docs under system_docs/patches/active/meld_state_gate_2026_10_15/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HANDOFF = (
    f"In progress ({NOW}). Option A approved for rule 1 and mapped (Notes): `SpellState.non_resolvable`, set by\n"
    "register_index from the selected version's capability and honoured where RiskManager distils the Book flag (the\n"
    "risk sets stay as today). The four call sites (bind, notch, transfer flip and rollback) are melder_0's: handoff\n"
    "through the owner; until then the change is built and validated on a scratch tree and nothing lands. Items\n"
    "(2)-(3), the contract check, still await his answer. Next: the patch docs, then the scratch-tree prototype.\n"
)


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Append the notes, refresh the handoff and the Updated stamp, and the board's next."""
    text = T.read_text(encoding="utf-8")
    anchor = "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n"
    start = text[: text.index(anchor)].count("\n") + 2
    end = start + MAP_NOTES.count("\n") - 1
    notes = MAP_NOTES + DECISION_TEMPLATE.format(now=NOW, task=TASK, start=start, end=end)
    for line in notes.splitlines() + HANDOFF.splitlines():
        assert len(line) <= 120 or line.lstrip().startswith(("- src/", "- context_compass/", "EVIDENCE:")), (
            len(line), line)
    text = one(text, anchor, "  SCORE_0_TO_10: 9\n" + notes + "\n## Context / Handoff Summary\n")
    h0 = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    h1 = text.index("\n## Project-Specific Additions")
    text = text[:h0] + HANDOFF + text[h1:]
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    board = CC / "attention_board.md"
    b = board.read_text(encoding="utf-8")
    b = one(b, "| Map the state system for SpellState.non_resolvable (Option A, owner-approved), then write the patch "
               "docs. |",
            "| Write the patch docs for SpellState.non_resolvable (map in Notes), then build it on a scratch tree. |")
    i = b.index("| meld_contract_scan | in_progress |")
    j = b.index("\n", i)
    cells = b[i:j].split(" | ")
    cells[-2] = NOW
    b = b[:i] + " | ".join(cells) + b[j:]
    board.write_bytes(b.encode("utf-8"))
    print("recorded", NOW)


if __name__ == "__main__":
    main()
