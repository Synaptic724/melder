"""Record the owner's redirect, the intent of `resolvable`, the state model and the options (melder_1, 2026-10-15)."""
import pathlib
import sys

NOW = sys.argv[1]
CC = pathlib.Path("context_compass")
T = CC / "tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
TASK = "context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
EPIC = "context_compass/tickets/epics/completed/2026-09-19_discoverable_non_resolvable_registrations_epic.md"
S4 = "context_compass/tickets/stories/completed/2026-09-19_discoverable_resolution_runtime_story.md"
ST = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states"
A = "context_compass/artifacts/meld_contract_scan_20261015"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner ruling (chat 2026-10-15): "discuss a way to introduce a new systemspellstate that can exclude objects
    that have no intention of being resolved, and thus must be overriden thats the point of resolvable, you don't need
    to invent a new solution please explore these options first". Item (1) of the design request (a RiskManager-private
    set) is withdrawn: the exclusion belongs in the spell-state model, chosen after reading its existing options and
    the intent of `resolvable`. Items (2) and (3) (the contract check) are unchanged and still await his answer.
  EVIDENCE: {TASK}:222-246
  IMPACT: Discussion only; no patch docs or `src/` edits until the owner picks the option.
  NEXT: Read the intent of `resolvable` and the state model, record them, bring the options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The intent of `resolvable` (EPIC-2026-09-19-discoverable-non-resolvable-registrations, owner-directed):
    abstract bases, Protocols and internal helpers are registered so agents can discover, inspect, version and
    navigate them in Nexus, while Melder never resolves them - "graph membership must describe the actual
    architecture while execution membership states what Melder may resolve". The capability is per Spell version
    (default True; a notch can flip it; a Protocol target must be False). A consumer parameter whose only match is a
    False definition compiles as an OVERRIDE_REQUIRED socket that keeps the reference for the graph; the value is
    supplied by override at construction. Direct meld and reuse refuse a False version at the door, before the
    validation gate and independently of the Book flag; planning (Phase 5 snapshot, phases 8-11, cache ids) leaves
    it out; Nexus publishes it; the Crystallizer replays the bool. That lane changed registration, compiler,
    runtime, Nexus and records, but not the state model: SpellSystemState and RiskManager have no notion of it.
  EVIDENCE:
  - {EPIC}:19-42
  - {EPIC}:105-153
  - {EPIC}:289-300
  - {S4}:37-37
  - src/melder/aether/spellbook/spellbook.py:5477-5479
  - src/melder/aether/conduit/meld/conduit_meld.py:559-561
  - src/melder/aether/conduit/meld/meld.py:812-838
  - src/melder/aether/spellbook/spellbook_creation_system.py:2855-2895
  - context_compass/system_docs/src_components.md:4020-4040
  - context_compass/system_docs/src_components.md:864-864
  IMPACT: A False lineage is a declared absence of resolution, not pending work; any state check that waits for its
    verdict waits forever.
  NEXT: Read the state model for where that declaration belongs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The state model has three axes: `SpellValidity`, the coarse gate meld reads, one enum for the structural
    verdict (SpellSystemState) and the per-conduit resolution verdict (ConduitResolutionState); `SpellState` flags, the
    accumulating explanation of why a lineage is in its state, each owned by the subsystem that sets it (validation
    clears only the topology flags); and `SpellStateChangeReason`, the last event. `unknown` means never validated -
    work still owed. A False definition never receives a resolution verdict, so each conduit answers its initial
    `unknown` forever and RiskManager, which counts anything but `valid`, reads that as risk; nothing in the model can
    say that no verdict is owed. The flag axis already carries this pattern twice: transfer sets `disabled` +
    `transfer_in_progress` and clears it; Phase 4 and contract marking set `gated` + `contract_unvalidated`.
    `register_index` is where a lineage's selected version is (re)registered (bind and notch change it; transfer
    re-registers the same one). Flags are not persisted: no Crystallizer, Nexus or MutationResearch reader, and the
    structural snapshot reads only `contract_unvalidated`.
  EVIDENCE:
  - {ST}/spell_state.py:1-75
  - {ST}/spell_validity.py:1-85
  - {ST}/spell_state_change_reason.py:1-99
  - {ST}/spell_system_state.py:349-417
  - {ST}/spell_system_state.py:613-666
  - {ST}/spell_system_states.py:307-374
  - {ST}/conduit_resolution_state.py:230-247
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:643-655
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:855-891
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:147-177
  - src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:424-424
  IMPACT: The missing state is an explanation ("excluded by declaration"), so it belongs on the flag axis; the gate
    axis stays truthful.
  NEXT: Weigh a new flag, a new validity value and reuse of an existing state; bring them to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: STRATEGY_DISCUSSION
  CLAIM: (A, recommended) A new `SpellState` flag, `non_resolvable` (or `override_required`): the selected version is a
    resolvable=False definition, kept for discovery and versioning and supplied to its consumers by override; it owes
    no resolution verdict. Producer: `register_index` takes the selected version's capability and sets or clears the
    flag before its own `mark_structural_change`, so every bucket already sees it when that gated event publishes; bind
    and notch pass it, transfer keeps it; validation never clears it (existing rule). Consumer: RiskManager reads the
    flag from the lineage's state in `register_spell` and in both validity events and gives a flagged lineage no risk;
    validity stays truthful and RiskManager keeps no set of its own. Meld, Nexus and records are unchanged; the meld
    hot path does not read it. (B) A new `SpellValidity` value: every validity writer (Phase 4, dependency and contract
    marking, transfer) would have to respect it, per-conduit states are created lazily and cannot know the
    capability, and the meld raises on an unrecognised value. (C) Reuse `disabled` or `anchored_component`: `disabled`
    is the transfer window's refusal and must stay risky; `anchored_component` means a non-mutable infrastructure
    component. Emulated effect of the exclusion: 22.8 -> 0.3 us per meld (automatic), 27.9 -> 0.9 us (dynamic).
  EVIDENCE:
  - {A}/runs/probe_design_baseline_gil0.txt:2-9
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:320-471
  - {ST}/spell_system_states.py:307-374
  - src/melder/aether/spellbook/spellbook.py:3906-3919
  - src/melder/aether/spellbook/spellbook.py:5686-5694
  - src/melder/aether/conduit/meld/meld.py:1174-1244
  IMPACT: Files for (A): spell_state.py, spell_system_states.py, risk_manager.py, two call sites in spellbook.py
    (melder_0's file), tests, docs, release note, notch, rebuild.
  NEXT: The owner picks the option and the flag's name.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HANDOFF = (
    f"In progress ({NOW}). The owner redirected item (1): the exclusion of resolvable=False lineages goes\n"
    "into the spell-state model. Options recorded (last Note); recommended: a new SpellState flag set by\n"
    "register_index and read by RiskManager. Items (2)-(3), the contract check, still await his answer. Nothing in\n"
    "`src/` has changed. Next: the owner's pick and the flag's name, then the patch docs; spellbook.py is melder_0's.\n"
)


def one(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence."""
    assert text.count(old) == 1, (text.count(old), old[:60])
    return text.replace(old, new, 1)


def main() -> None:
    """Append the notes, refresh the handoff and the Updated stamp, and the board's next."""
    for line in NOTES.splitlines() + HANDOFF.splitlines():
        assert len(line) <= 120 or line.lstrip().startswith(("- src/", "- context_compass/", "EVIDENCE:")), (
            len(line), line)
    text = T.read_text(encoding="utf-8")
    text = one(text, "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n",
               "  SCORE_0_TO_10: 9\n" + NOTES + "\n## Context / Handoff Summary\n")
    h0 = text.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
    h1 = text.index("\n## Project-Specific Additions")
    text = text[:h0] + HANDOFF + text[h1:]
    start = text.index("- Updated: ")
    end = text.index("\n", start)
    text = text[:start] + f"- Updated: {NOW}" + text[end:]
    T.write_bytes(text.encode("utf-8"))
    board = CC / "attention_board.md"
    b = board.read_text(encoding="utf-8")
    b = one(b, "| Owner answers the design (last Note): exclusion, no per-meld scan, borrower-side marking; then patch "
               "docs. |",
            "| Owner picks the spell-state option for resolvable=False (last Note) and answers the contract-check "
            "items. |")
    i = b.index("| meld_contract_scan | in_progress |")
    j = b.index("\n", i)
    cells = b[i:j].split(" | ")
    cells[-2] = NOW
    b = b[:i] + " | ".join(cells) + b[j:]
    board.write_bytes(b.encode("utf-8"))
    print("recorded", NOW)


if __name__ == "__main__":
    main()
