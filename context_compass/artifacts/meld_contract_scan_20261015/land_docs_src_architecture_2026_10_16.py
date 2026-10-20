"""Promote meld_state_gate_2026_10_15 (rule 1, 0.2.8247) into src_architecture (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC timestamp> [--check]
Exact-text edits; each anchor must occur once. The numeric spellbook.py citations were remapped beforehand by
remap_citations_2026_10_16.py; this script edits the prose, the code map and the handoff.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_lib import one  # the lane's exact-text replacement (refuses a missing or repeated anchor)


def apply(root, rel, steps, check_only):
    """Like apply_lib.apply, but a new line may pass 120 characters when it holds one unbreakable token
    (an EVIDENCE path citation), as the documentation standard allows; other long lines are refused."""
    path = root / rel
    raw = path.read_bytes().decode("utf-8")
    crlf = raw.count("\r\n") > 0 and raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    for kind, a, b, c in steps:
        for line in b.splitlines():
            body = line.strip()
            if body.startswith("EVIDENCE:"):
                body = body[len("EVIDENCE:"):].strip()
            if len(line) > 120 and len(body.split()) != 1:
                raise SystemExit(f"{rel}: new prose line longer than 120 characters ({len(line)}): {line!r}")
        text = one(text, a, b, rel)
    if not check_only:
        path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(("checked " if check_only else "applied ") + rel + (" (CRLF kept)" if crlf else ""))

TS = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
ROOT = pathlib.Path(".")
DOC = "context_compass/system_docs/src_architecture.md"

GATE_STEP_OLD = (
    "   again under the same content-stable id reads `unknown` in each conduit and step 3 runs for it there.\n"
    "\n"
    "### Sequence: Create Lesser Conduit\n"
)
GATE_STEP_NEW = (
    "   again under the same content-stable id reads `unknown` in each conduit and step 3 runs for it there.\n"
    "7. A meld enters this gate only while its Book's validation-required flag is up, and the warm meld doors serve a\n"
    "   meld only while it is down. RiskManager raises the flag while a conduit of the Book holds a risky lineage,\n"
    "   except one whose state carries `SpellState.non_resolvable` - a lineage whose selected version was bound\n"
    "   resolvable=False, which every meld door refuses before this gate (0.2.8247). Such a definition never receives\n"
    "   a resolution verdict, so until 0.2.8247 one of them kept the flag up for the Book's life and sent every meld\n"
    "   of the Book through steps 1-3.\n"
    "\n"
    "### Sequence: Create Lesser Conduit\n"
)

INVARIANT_ANCHOR = "## Operational Invariants\n- Managed pools follow an ownership transfer's owner stamps (2026-10-15, 0.2.8246):"
INVARIANT_NEW = (
    "## Operational Invariants\n"
    "- Non-resolvable definitions hold no Book flag (2026-10-16, 0.2.8247): `SpellState.non_resolvable` is the capability\n"
    "  flag on the explanation axis, set exactly while a lineage's registered selected version was bound resolvable=False.\n"
    "  `SpellSystemStates.register_index(..., *, resolvable=None)` writes it from the caller's `Spell.resolvable` - bind\n"
    "  and `_apply_notch` pass it, as do the ownership transfer's flip and its rollback; the transfer's disable step\n"
    "  passes none - under the registry lock and before `mark_structural_change` publishes: False sets it, True clears\n"
    "  it, None keeps it only while the index still selects the version the state tracked (a new state or another\n"
    "  selection clears it), and a non-bool raises TypeError before anything is registered. Validation never clears it\n"
    "  and it changes no validity, verdict or other flag. In the same locked section the registry mirrors the flagged\n"
    "  lineages into `non_resolvable_index_ids`, a frozenset replaced whole (never mutated) and read without a lock;\n"
    "  `unregister_index` takes a lineage out, and cleanup leaves an empty set as the tombstone for lock-free readers.\n"
    "  RiskManager's risk sets track exactly as before; only `_refresh_spellbook_flag` leaves a flagged lineage out, with\n"
    "  one subset test of the conduit's risky keys against that set (`_has_unexcluded_risk`; a `spell:` key or a removed\n"
    "  lineage is never excluded), so the Book flag no longer stays up for a definition that owes no verdict, and a\n"
    "  notch back to a resolvable version counts the lineage again with the risk the sets kept. When the capability\n"
    "  write changes the flag on a lineage already `gated` - a repeat notch, since a notch commit runs phases 1-4 only\n"
    "  for a member never compiled - the gate publishes nothing, so `register_index` re-publishes the current validity\n"
    "  (`SpellSystemState._republish_validity`) and every conduit holding the lineage refreshes, an index-linked\n"
    "  borrower whose copy came back by reactivation included. `register_conduit` seeds every visible spell and\n"
    "  refreshes once. No meld path reads the flag; the lock order stays registry -> state, the registry calls\n"
    "  RiskManager under its lock and RiskManager never takes it. Measured on 3.14t with the GIL off: a warm meld in a\n"
    "  Book holding one Protocol definition went from 15.1 to 0.26 us (automatic) and from 16.4 to 0.73 us (dynamic);\n"
    "  worlds without a definition are unchanged.\n"
    "  EVIDENCE: `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:SpellSystemStates.register_index`,\n"
    "  `SpellSystemStates._record_selected_capability`, `SpellSystemStates._publish_non_resolvable_membership_locked`,\n"
    "  `SpellSystemStates.non_resolvable_index_ids`, `SpellSystemStates.unregister_index`,\n"
    "  `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:SpellSystemState.update_flags`,\n"
    "  `SpellSystemState._republish_validity` and\n"
    "  `src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:RiskManager._refresh_spellbook_flag`,\n"
    "  `RiskManager._has_unexcluded_risk`.\n"
    "- Managed pools follow an ownership transfer's owner stamps (2026-10-15, 0.2.8246):"
)

FAILURE_ANCHOR = "## Failure Modes and Error Paths\n- A managed meld can refuse (0.2.8243-0.2.8245):"
FAILURE_NEW = (
    "## Failure Modes and Error Paths\n"
    "- A Book holding a definition bound resolvable=False - a Protocol or abstract base kept for discovery, whose\n"
    "  consumers receive the value by override - no longer runs the meld-time validation gate on every meld (fixed in\n"
    "  0.2.8247). The definition never receives a resolution verdict, so RiskManager counted it as risk and kept the\n"
    "  Book's validation-required flag up for the Book's life: every meld paid the gate (about 15 us instead of 0.3 us)\n"
    "  and no warm meld took the fast door. A meld of the definition itself is still refused before the gate with the\n"
    "  same MeldExecutionError. `SpellSystemStates.register_index` raises TypeError for a `resolvable` that is neither\n"
    "  None nor a bool.\n"
    "  EVIDENCE: `src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:RiskManager._has_unexcluded_risk`,\n"
    "  `src/melder/aether/conduit/meld/conduit_meld.py:ConduitMeld.meld` and\n"
    "  `src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:SpellSystemStates.register_index`.\n"
    "- A managed meld can refuse (0.2.8243-0.2.8245):"
)

SPELLBOOK_OLD = (
    "  end_line: 7613\n"
    "  loc: 7613\n"
    "  verified_at: 2026-10-15T21:20:35Z\n"
    "  note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps (0.2.8229); bind publishes\n"
)
SPELLBOOK_NEW = (
    "  end_line: 7615\n"
    "  loc: 7615\n"
    f"  verified_at: {TS}\n"
    "  note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps (0.2.8229); bind publishes\n"
)
SPELLBOOK_NOTE_OLD = (
    "    held (0.2.8232); `cleanup_and_remove_spell` re-checks a Book torn down while it waits (0.2.8233); bind and\n"
    "    bind_inactive take the four `managed_spell_*` options (0.2.8242).\n"
)
SPELLBOOK_NOTE_NEW = (
    "    held (0.2.8232); `cleanup_and_remove_spell` re-checks a Book torn down while it waits (0.2.8233); bind and\n"
    "    bind_inactive take the four `managed_spell_*` options (0.2.8242); bind and `_apply_notch` pass the selected\n"
    "    version's `resolvable` to `register_index` (0.2.8247).\n"
)
SSS_OLD = (
    "  end_line: 1654\n"
    "  loc: 1654\n"
    "  verified_at: 2026-10-15T21:20:35Z\n"
    "  note: lineage registry; retires a spell id's per-conduit verdicts on unregister and on register (0.2.8219).\n"
)
SSS_NEW = (
    "  end_line: 1886\n"
    "  loc: 1886\n"
    f"  verified_at: {TS}\n"
    "  note: lineage registry; retires a spell id's per-conduit verdicts on unregister and on register (0.2.8219);\n"
    "    writes `SpellState.non_resolvable` from the registration's capability and publishes the flagged lineages\n"
    "    (`non_resolvable_index_ids`, 0.2.8247).\n"
)
SS_OLD = (
    "  end_line: 676\n"
    "  loc: 676\n"
    "  verified_at: 2026-08-02T13:00:45Z\n"
    "  note: lineage state.\n"
)
SS_NEW = (
    "  end_line: 806\n"
    "  loc: 806\n"
    f"  verified_at: {TS}\n"
    "  note: lineage state; `update_flags`, `has_flag` and `_republish_validity` (0.2.8247).\n"
)
STATE_OLD = (
    "  end_line: 75\n"
    "  loc: 75\n"
    "  verified_at: 2026-08-02T13:00:45Z\n"
    "  note: lineage flags.\n"
)
STATE_NEW = (
    "  end_line: 93\n"
    "  loc: 93\n"
    f"  verified_at: {TS}\n"
    "  note: lineage flags; `non_resolvable`, the capability flag (0.2.8247).\n"
)
RISK_OLD = (
    "  end_line: 655\n"
    "  loc: 655\n"
    "  verified_at: 2026-08-02T13:00:45Z\n"
    "  note: risk gating.\n"
)
RISK_NEW = (
    "  end_line: 751\n"
    "  loc: 751\n"
    f"  verified_at: {TS}\n"
    "  note: risk gating; the Book flag leaves out lineages flagged `non_resolvable` (one subset test) and\n"
    "    `register_conduit` refreshes once (0.2.8247).\n"
)
TOO_OLD = (
    "  end_line: 2154\n"
    "  loc: 2154\n"
    "  verified_at: 2026-10-15T21:20:35Z\n"
    "  note: ownership transfer; moves by default and disposes nothing (0.2.8239); the owner stamp follows the lineage both\n"
    "    ways (`_restamp`, 0.2.8246).\n"
)
TOO_NEW = (
    "  end_line: 2155\n"
    "  loc: 2155\n"
    f"  verified_at: {TS}\n"
    "  note: ownership transfer; moves by default and disposes nothing (0.2.8239); the owner stamp follows the lineage both\n"
    "    ways (`_restamp`, 0.2.8246); the flip and its rollback pass the moved version's `resolvable` to\n"
    "    `register_index` (0.2.8247).\n"
)
SOURCES_OLD = "- `src/melder/aether/conduit/meld/meld.py`\n- `src/melder/aether/spellbook/spellbook_creation_system.py`\n"
SOURCES_NEW = (
    "- `src/melder/aether/conduit/meld/meld.py`\n"
    "- `src/melder/aether/conduit/meld/conduit_meld.py`\n"
    "- `src/melder/aether/spellbook/spellbook_creation_system.py`\n"
)
HANDOFF_ANCHOR = "## Context / Handoff Summary\n\n2026-10-15 managed spells (0.2.8241-0.2.8246; promoted at the end of their lane):"
HANDOFF_NEW = (
    "## Context / Handoff Summary\n"
    "\n"
    "2026-10-16 non-resolvable definitions leave the Book flag (0.2.8247): a lineage whose selected version was bound\n"
    "resolvable=False carries the new capability flag `SpellState.non_resolvable`, written by `register_index` from its\n"
    "callers' `Spell.resolvable` and published as the registry's frozenset `non_resolvable_index_ids`; RiskManager's\n"
    "Book flag leaves such lineages out with one subset test, so one Protocol or abstract definition no longer sends\n"
    "every meld of its Book through the validation gate (15-16 us -> 0.3-0.7 us per warm meld). The meld-time gate\n"
    "sequence, an operational invariant, a failure mode, the code map (six files remeasured) and the sources carry it;\n"
    "the component map carries the per-component contracts. Numeric citations into spellbook.py moved one or two lines\n"
    "with the two call-site keywords and point at their code again. Open for the owner: whether the meld's contract\n"
    "check should run only when the melded spell's state calls for it (a contract consumer in a borrower Book still\n"
    "costs about 2 ms a meld).\n"
    "\n"
    "2026-10-15 managed spells (0.2.8241-0.2.8246; promoted at the end of their lane):"
)

STEPS = [
    ("one", "- Updated: 2026-10-15\n", "- Updated: 2026-10-16\n", ""),
    ("one", "(the three seams, remeasured 2026-10-15);", "(the three seams, remeasured 2026-10-16);", ""),
    ("one", "in-place settle :6818-6830,", "in-place settle :6820-6832,", ""),
    ("one", "effective-mode return :6831; remeasured 2026-10-15 at 0.2.8246)",
     "effective-mode return :6833; remeasured 2026-10-16 at 0.2.8247)", ""),
    ("one", GATE_STEP_OLD, GATE_STEP_NEW, ""),
    ("one", INVARIANT_ANCHOR, INVARIANT_NEW, ""),
    ("one", FAILURE_ANCHOR, FAILURE_NEW, ""),
    ("one", SPELLBOOK_OLD, SPELLBOOK_NEW, ""),
    ("one", SPELLBOOK_NOTE_OLD, SPELLBOOK_NOTE_NEW, ""),
    ("one", SSS_OLD, SSS_NEW, ""),
    ("one", SS_OLD, SS_NEW, ""),
    ("one", STATE_OLD, STATE_NEW, ""),
    ("one", RISK_OLD, RISK_NEW, ""),
    ("one", TOO_OLD, TOO_NEW, ""),
    ("one", SOURCES_OLD, SOURCES_NEW, ""),
    ("one", HANDOFF_ANCHOR, HANDOFF_NEW, ""),
]

apply(ROOT, DOC, STEPS, CHECK)
