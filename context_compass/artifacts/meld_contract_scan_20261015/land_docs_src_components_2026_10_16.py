"""Promote meld_state_gate_2026_10_15 (rule 1, 0.2.8247) into src_components (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC timestamp> [--check]
Exact-text edits; each anchor must occur once. Numeric spellbook.py citations were remapped beforehand by
remap_citations_2026_10_16.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_lib import one  # the lane's exact-text replacement (refuses a missing or repeated anchor)

TS = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
DOC = pathlib.Path("context_compass/system_docs/src_components.md")
P = "src/melder/aether/aetheric_frame/dev_ops/"


def apply(path, steps, check_only):
    """Exact-text steps; a new line may pass 120 characters only when it holds one unbreakable token."""
    raw = path.read_bytes().decode("utf-8")
    crlf = raw.count("\r\n") > 0 and raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    for old, new in steps:
        for line in new.splitlines():
            body = line.strip()
            if body.startswith("EVIDENCE:"):
                body = body[len("EVIDENCE:"):].strip()
            if len(line) > 120 and len(body.split()) != 1 and line not in old:
                raise SystemExit(f"{path}: new prose line longer than 120 characters ({len(line)}): {line!r}")
        text = one(text, old, new, str(path))
    if not check_only:
        path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(("checked " if check_only else "applied ") + str(path) + (" (CRLF kept)" if crlf else ""))


RISK_RESP_OLD = (
    "- RiskManager tracks per-conduit risk and toggles Spellbook validation gating. EVIDENCE: "
    f"{P}risk_manager/risk_manager.py:register_conduit + on_resolution_validity_change.\n"
)
RISK_RESP_NEW = RISK_RESP_OLD + (
    "- The Book flag ignores a risky lineage whose state carries `SpellState.non_resolvable` (its selected version was\n"
    "  bound resolvable=False): `RiskManager._refresh_spellbook_flag` snapshots the conduit's risky keys under its lock\n"
    "  and, outside it, tests them as a subset of `SpellSystemStates.non_resolvable_index_ids` (`_has_unexcluded_risk`:\n"
    "  no lock, no work per key; a `spell:` key or a removed lineage is never excluded). The risk sets track as before,\n"
    "  so a notch back to a resolvable version counts the lineage again at once, and `register_conduit` seeds every\n"
    "  visible spell and refreshes once (0.2.8247). EVIDENCE:\n"
    f"  {P}risk_manager/risk_manager.py:RiskManager._has_unexcluded_risk.\n"
)
INV_OLD = (
    "- DevOps dirty roots are conduit-scoped revalidation state and are separate from\n"
    "  SpellCompilerArtifact `phase8_11` IR freshness dirty tracking.\n"
)
INV_NEW = INV_OLD + (
    "- A lineage whose selected version was bound resolvable=False carries `SpellState.non_resolvable` from its\n"
    "  registration (bind, notch, the transfer flip and its rollback pass the capability to `register_index`) until a\n"
    "  resolvable version is selected. It never holds its Book's validation flag up, and its validity and verdicts stay\n"
    "  truthful: the flag changes neither, and validation never clears it (0.2.8247).\n"
)
KEYS_OLD = (
    f"- `{P}spell_system_states/conduit_resolution_state.py`\n"
    f"- `{P}change_control_manager/change_control_manager.py`\n"
)
KEYS_NEW = (
    f"- `{P}spell_system_states/conduit_resolution_state.py`\n"
    f"- `{P}spell_system_states/spell_state.py`\n"
    f"- `{P}change_control_manager/change_control_manager.py`\n"
    f"- `{P}risk_manager/risk_manager.py`\n"
)
REG_CONTRACT_OLD = (
    f"  {P}spell_system_states/spell_system_states.py:SpellSystemStates.forget_spell_resolution_verdicts.\n"
    "Scope:\n"
)
REG_CONTRACT_NEW = (
    f"  {P}spell_system_states/spell_system_states.py:SpellSystemStates.forget_spell_resolution_verdicts.\n"
    "- `register_index(spell_index, owner_spellbook_id=None, *, resolvable=None)` also records the selected version's\n"
    "  capability as `SpellState.non_resolvable` before it gates: False sets the flag, True clears it, None keeps it only\n"
    "  while the index still selects the version the state tracked; a non-bool raises TypeError before anything is\n"
    "  registered. It then mirrors the lineage into or out of `non_resolvable_index_ids` (a frozenset replaced whole,\n"
    "  read without a lock), and when the flag changed on a lineage already `gated` it re-publishes the validity\n"
    "  (`SpellSystemState._republish_validity`), because the gate then publishes nothing. `unregister_index` takes the\n"
    "  lineage out of the set; `index_has_flag(index_id, flag)` is the per-lineage read (0.2.8247). EVIDENCE:\n"
    f"  {P}spell_system_states/spell_system_states.py:SpellSystemStates.register_index.\n"
    "Scope:\n"
)
REG_DATA_OLD = "- `_states_by_index_id`, `_states_by_spell_id`, `_dirty_indexes`, `_resolution_by_conduit_id`.\n"
REG_DATA_NEW = (
    "- `_states_by_index_id`, `_states_by_spell_id`, `_dirty_indexes`, `_resolution_by_conduit_id`.\n"
    "- `_non_resolvable_index_ids`: the published frozenset of flagged lineages, replaced whole; an empty set is left\n"
    "  as a tombstone at cleanup (0.2.8247).\n"
)
REG_CONC_OLD = "  pop a state under the same lock before cleaning it, so the retirement never visits a cleaned state.\n"
REG_CONC_NEW = (
    "  pop a state under the same lock before cleaning it, so the retirement never visits a cleaned state.\n"
    "- `non_resolvable_index_ids` is replaced under the registry lock before the gate publishes and read with no lock,\n"
    "  so the RiskManager refresh a registration's event runs reads the new set, and a read racing cleanup finds the\n"
    "  tombstone (0.2.8247).\n"
)
GATING_OLD = (
    "  root, 0.2.8215).\n"
    "Data Structures:\n"
    "- SpellSystemStates lineage validity and change-control dirty-root state.\n"
)
GATING_NEW = (
    "  root, 0.2.8215).\n"
    "- The gate is entered only while the Book's `_spellbook_validation_required` is up (`ConduitMeld.meld`,\n"
    "  `SpellSpaceMeld.meld`), which RiskManager raises for a risky lineage unless it is flagged\n"
    "  `SpellState.non_resolvable`; a resolvable=False target is refused before the gate either way (0.2.8247).\n"
    "Data Structures:\n"
    "- SpellSystemStates lineage validity and change-control dirty-root state.\n"
)
FLOW_OLD = "   same-address rebind takes step 3 in every conduit that resolved the removed definition (0.2.8219).\n"
FLOW_NEW = FLOW_OLD + (
    "6. The gate runs only while `Spellbook._spellbook_validation_required` is up (`ConduitMeld.meld`).\n"
    "   `RiskManager._refresh_spellbook_flag` raises it while the conduit holds a risky key outside\n"
    "   `SpellSystemStates.non_resolvable_index_ids` (`_has_unexcluded_risk`), so a resolvable=False definition, refused\n"
    "   at the door before step 1, no longer keeps every meld of its Book in this flow (0.2.8247).\n"
)


def c1(path, old_end, old_verified, new_end):
    return (
        f"- path: `{path}`\n  start_line: 1\n  end_line: {old_end}\n  loc: {old_end}\n  verified_at: {old_verified}\n",
        f"- path: `{path}`\n  start_line: 1\n  end_line: {new_end}\n  loc: {new_end}\n  verified_at: {TS}\n",
    )


CRS = f"- path: `{P}spell_system_states/conduit_resolution_state.py`\n  start_line: 1\n  end_line: 922\n  loc: 922\n"
CRS_NEW = CRS + (
    "  verified_at: 2026-10-03T20:50:00Z\n"
    f"- path: `{P}spell_system_states/spell_state.py`\n  start_line: 1\n  end_line: 93\n  loc: 93\n  verified_at: {TS}\n"
)
CCM = (
    f"- path: `{P}change_control_manager/change_control_manager.py`\n  start_line: 1\n  end_line: 1679\n  loc: 1679\n"
    "  verified_at: 2026-08-02T13:00:45Z\n"
)
CCM_NEW = CCM + f"- path: `{P}risk_manager/risk_manager.py`\n  start_line: 1\n  end_line: 751\n  loc: 751\n  verified_at: {TS}\n"
SOURCES_OLD = (
    f"- `{P}information_strategies/transfer_blast_radius_strategy.py`\n"
    f"- `{P}spell_system_states/conduit_resolution_state.py`\n"
    f"- `{P}spell_system_states/spell_system_state.py`\n"
)
SOURCES_NEW = (
    f"- `{P}information_strategies/transfer_blast_radius_strategy.py`\n"
    f"- `{P}risk_manager/risk_manager.py`\n"
    f"- `{P}spell_system_states/conduit_resolution_state.py`\n"
    f"- `{P}spell_system_states/spell_state.py`\n"
    f"- `{P}spell_system_states/spell_system_state.py`\n"
)
HANDOFF_ANCHOR = (
    "## Context / Handoff Summary\n\n"
    "2026-10-15 managed spells (0.2.8241-0.2.8246; promoted at the end of their lane):"
)
HANDOFF_NEW = (
    "## Context / Handoff Summary\n\n"
    "2026-10-16 non-resolvable definitions leave the Book flag (0.2.8247): the DevOps Control Plane carries the\n"
    "capability flag `SpellState.non_resolvable` and RiskManager's exclusion (one subset test against the registry's\n"
    "published `non_resolvable_index_ids`); the SpellSystemStates Registry carries `register_index`'s capability write,\n"
    "the published set, the re-publication for an already gated lineage and `index_has_flag`; Meld Runtime Gating and\n"
    "the Meld-Time Validation Gate flow name the Book flag that admits the gate. The code map adds spell_state.py and\n"
    "risk_manager.py (now Key Files of the control plane) and remeasures four extents; numeric citations into\n"
    "spellbook.py moved one or two lines with the call-site keywords. The seam citations of Spellbook Core and the\n"
    "SpellIndex Mutation Surface (spellbook.py and the three Conduit verbs) had drifted since earlier lanes and are\n"
    "remeasured. Still stale from earlier lanes and not re-audited here: spellbook.py:7233-7244, :286 and :5713-5719\n"
    "(Spellbook Core), :5273-5285 (Binding Pipeline), :6546 (Promoted Patch Detail) and transfer_of_ownership.py:953\n"
    "and :1444 (the SafeGuard order note).\n"
    "\n"
    "2026-10-15 managed spells (0.2.8241-0.2.8246; promoted at the end of their lane):"
)

STEPS = [
    ("- Updated: 2026-10-15\n", "- Updated: 2026-10-16\n"),
    (RISK_RESP_OLD, RISK_RESP_NEW),
    (INV_OLD, INV_NEW),
    (KEYS_OLD, KEYS_NEW),
    (REG_CONTRACT_OLD, REG_CONTRACT_NEW),
    (REG_DATA_OLD, REG_DATA_NEW),
    (REG_CONC_OLD, REG_CONC_NEW),
    (GATING_OLD, GATING_NEW),
    (FLOW_OLD, FLOW_NEW),
    c1("src/melder/aether/spellbook/spellbook.py", 7613, "2026-10-15T21:40:35Z", 7615),
    c1(f"{P}spell_system_states/spell_system_states.py", 1654, "2026-10-15T21:40:35Z", 1886),
    c1(f"{P}spell_system_states/spell_system_state.py", 676, "2026-08-02T13:00:45Z", 806),
    c1("src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py", 2154, "2026-10-15T21:40:35Z", 2155),
    (CRS + "  verified_at: 2026-10-03T20:50:00Z\n", CRS_NEW),
    (CCM, CCM_NEW),
    (SOURCES_OLD, SOURCES_NEW),
    (HANDOFF_ANCHOR, HANDOFF_NEW),
    # Seam citations that had drifted since earlier lanes; remeasured against the landed tree.
    ("  - src/melder/aether/spellbook/spellbook.py:3706, 3757 (`_notch_spell` -> `_apply_notch`)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3775, 3826 (`_notch_spell` -> `_apply_notch`)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3899, 3933 (`_add_to_spell_index` -> `_apply_add_to_index`)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3969, 4002 (`_add_to_spell_index` -> `_apply_add_to_index`)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:4076, 4108 (`_remove_from_spell_index` -> `_apply_remove_from_index`)\n",
     "  - src/melder/aether/spellbook/spellbook.py:4145, 4177 (`_remove_from_spell_index` -> `_apply_remove_from_index`)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3742 (states the Conduit admits it)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3811-3813 (states the Conduit admits it)\n"),
    ("  - src/melder/aether/conduit/conduit.py:5396, 5472, 5552 (notch/add/remove\n",
     "  - src/melder/aether/conduit/conduit.py:5671, 5747, 5827 (notch/add/remove\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3757-3897 (`_apply_notch`)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3826-3967 (`_apply_notch`)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3933-4027 (`_apply_add_to_index`)\n",
     "  - src/melder/aether/spellbook/spellbook.py:4002-4096 (`_apply_add_to_index`)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:4108-4193 (`_apply_remove_from_index`)\n",
     "  - src/melder/aether/spellbook/spellbook.py:4177-4262 (`_apply_remove_from_index`)\n"),
    ("`src/melder/aether/spellbook/spellbook.py:3742`\n  states it correctly.",
     "`src/melder/aether/spellbook/spellbook.py:3811-3813`\n  states it correctly."),
    ("  - src/melder/aether/conduit/conduit.py:5347, 5437, 5515 (public verbs)\n",
     "  - src/melder/aether/conduit/conduit.py:5622, 5712, 5790 (public verbs)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3757, 3933, 4108 (applied seams)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3826, 4002, 4177 (applied seams)\n"),
]

apply(DOC, STEPS, CHECK)
