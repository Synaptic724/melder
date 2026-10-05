"""
Promote the injected_provider_first_direct_meld patch (0.2.8215) into src_components.md and remeasure the
citations into the files the landing touched.

Usage: python apply_docs_components.py <repository root>
Every anchor must match exactly once; nothing is written unless all do.
"""
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

ROOT = sys.argv[1]
DOC = "context_compass/system_docs/src_components.md"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s = ApplySession(ROOT)

# Meld Resolution Runtime: the rebuild-window producers, then the new block.
s.replace(
    DOC,
    "  `_ensure_resolution_resolvable` (5-11) and `_ensure_runtime_resolution_ready` (deferred 8-11) run inside\n",
    "  `_ensure_resolution_resolvable` (5-11) and `_ensure_runtime_resolution_ready` (the deferred lane: 8-11, or\n"
    "  5-11 for a spell that is not its Phase 5 root, 0.2.8215) run inside\n",
)
s.insert_after(
    DOC,
    "  `src/melder/aether/spellbook/spell.py:Spell._configure_creation_context_factory`.\n",
    "\n"
    "Injected dependencies (2026-09-30, 0.2.8215):\n"
    "- Symptom fixed: a spell bound on a live dynamic root after conjure and first built as a consumer's dependency\n"
    "  failed its first direct meld with \"Cannot build CreationContext before spell_codegen_creation exists.\" The\n"
    "  consumer's target-local pass compiled it only inside the consumer's plan and its local Phase 6 left it\n"
    "  stamped valid, so neither the Book validation flag nor its verdict routed it anywhere before the builder.\n"
    "- Producer: on success `SpellbookCreationSystem.run_resolution_phases_for_target_spell` calls\n"
    "  `flag_dependencies_without_own_plan` over its scope (the target plus its Phase 5 system-index nodes). Each\n"
    "  id other than the target that the Book owns, that is resolvable and not an existing creation, and that has\n"
    "  no phase-11 plan, no published CreationContext and no flag yet gets `resolution_complete=False`,\n"
    "  `resolution_required=True` and a `_door_epoch` bump, written under its spell lock after the target's.\n"
    "- Consumer: both doors (ConduitMeld, SpellSpaceMeld) and `_execute_admitted` already call\n"
    "  `_ensure_runtime_resolution_ready` while the flag is set. Inside the spell's rebuild window and lock the lane\n"
    "  runs `_run_deferred_resolution_phases_for_target_spell` (8-11) for an existing creation or a spell that is\n"
    "  its current Phase 5 root (`_requires_own_target_pass` is False), and otherwise\n"
    "  `_run_resolution_phases_for_target_spell` (5-11), after which the spell must read resolution-valid for the\n"
    "  conduit (`_raise_unless_resolution_valid`, SpellbookValidationError). The window then publishes the new\n"
    "  context, and the executor returns the instance the consumer's plan stored under the dependency's id\n"
    "  (unique_per_conduit, unique) or builds one (many). Sibling lessers share the root's resolution conduit id,\n"
    "  so the dependency is compiled once.\n"
    "- Unchanged: verdicts and the Book validation flag, warm melds (the door read already existed), the\n"
    "  conduit-wide pass (it publishes to every owned spell), bind, notch, transfer and the conjure cache (a\n"
    "  cache-loaded context is never flagged).\n"
    "- EVIDENCE:\n"
    "  `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem.flag_dependencies_without_own_plan`,\n"
    "  `src/melder/aether/conduit/meld/meld.py:Meld._ensure_runtime_resolution_ready`,\n"
    "  `Meld._requires_own_target_pass` and `Meld._raise_unless_resolution_valid`.\n",
)
s.insert_after(
    DOC,
    "- If per-conduit resolution validity is UNKNOWN or GATED, it runs phases 5-11\n"
    "  via `spell._spellbook._run_resolution_phases_for_target_spell(...)`.\n",
    "- A spell flagged `resolution_required` runs the deferred lane instead: 8-11 for its own Phase 5 root or an\n"
    "  existing creation, otherwise its full target pass 5-11 (0.2.8215; see Injected dependencies above).\n",
)

# SpellCompiler: the publication authority block.
s.insert_after(
    DOC,
    "  providers in the same book during target-local compilation. Selected targets still invalidate normally.\n",
    "- A dependency compiled only inside a local target's plan therefore keeps no plan of its own. The target pass\n"
    "  flags the ones its Book owns (`SpellbookCreationSystem.flag_dependencies_without_own_plan`, 0.2.8215), so\n"
    "  their first direct meld runs their own full pass (Meld Resolution Runtime, Injected dependencies).\n",
)

# C2 gating contract and the C1 flow.
s.replace(
    DOC,
    "- `Meld._ensure_lineage_resolvable(...)` and `Meld._gated_validation_required(...)`.\n",
    "- `Meld._ensure_lineage_resolvable(...)`, `Meld._gated_validation_required(...)` and the deferred lane\n"
    "  `Meld._ensure_runtime_resolution_ready(...)` (8-11, or the full 5-11 pass for a spell that is not its Phase 5\n"
    "  root, 0.2.8215).\n",
)
s.replace(
    DOC,
    "3. If per-conduit resolution validity is UNKNOWN/GATED:\n"
    "   - `spell._spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)` executes.\n",
    "3. If per-conduit resolution validity is UNKNOWN/GATED:\n"
    "   - `spell._spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)` executes.\n"
    "4. If the spell is flagged `resolution_required` (a dependency a consumer's target pass compiled without a plan\n"
    "   of its own, 0.2.8215, or an invalidated spell):\n"
    "   - `Meld._ensure_runtime_resolution_ready(spell)` runs 8-11 for its Phase 5 root or an existing creation,\n"
    "     otherwise `spell._spellbook._run_resolution_phases_for_target_spell(conduit_id, spell)` and a verdict check.\n",
)

# Citations into the touched files, checked by symbol against the landed tree.
CITATIONS = [
    ("  - src/melder/aether/spellbook/spellbook.py:3644, 3695 (`_notch_spell` -> `_apply_notch`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:3835, 3868 (`_add_to_spell_index` -> `_apply_add_to_index`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:4011, 4043 (`_remove_from_spell_index` -> `_apply_remove_from_index`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:3680 (states the Conduit admits it)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3650, 3701 (`_notch_spell` -> `_apply_notch`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:3843, 3876 (`_add_to_spell_index` -> `_apply_add_to_index`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:4019, 4051 (`_remove_from_spell_index` -> `_apply_remove_from_index`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:3686 (states the Conduit admits it)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:7121-7132 (`_run_structural_phases`\n"
     "    at :7121; the caller-held-lock precondition is stated at :7132; remeasured 2026-09-30)\n",
     "  - src/melder/aether/spellbook/spellbook.py:7135-7146 (`_run_structural_phases`\n"
     "    at :7135; the caller-held-lock precondition is stated at :7146; remeasured 2026-09-30 at 0.2.8215)\n"),
    ("  - src/melder/aether/spellbook/spellbook_creation_system.py:2000 (the only\n",
     "  - src/melder/aether/spellbook/spellbook_creation_system.py:2083 (the only\n"),
    ("  - src/melder/aether/spellbook/spellbook_creation_system.py:1972-2000\n",
     "  - src/melder/aether/spellbook/spellbook_creation_system.py:2055-2083\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:1053-1063 (the cache-emit flag re-checked and set under `_lock`)\n",
     "  - src/melder/aether/spellbook/spellbook.py:1055-1066 (the cache-emit flag re-checked and set under `_lock`)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3695-3833 (`_apply_notch`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:3868-3962 (`_apply_add_to_index`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:4043-4128 (`_apply_remove_from_index`)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3701-3841 (`_apply_notch`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:3876-3970 (`_apply_add_to_index`)\n"
     "  - src/melder/aether/spellbook/spellbook.py:4051-4136 (`_apply_remove_from_index`)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:5601-5607\n",
     "  - src/melder/aether/spellbook/spellbook.py:5615-5621\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:5166-5178 (`Spellbook.bind\n",
     "  - src/melder/aether/spellbook/spellbook.py:5176-5188 (`Spellbook.bind\n"),
    ("  EVIDENCE: src/melder/aether/conduit/meld/meld.py:322-363 and\n"
     "  src/melder/aether/conduit/meld/meld.py:1364-1589 (every `self._lock` site).\n",
     "  EVIDENCE: src/melder/aether/conduit/meld/meld.py:276-377 and\n"
     "  src/melder/aether/conduit/meld/meld.py:1481-1679 (every `self._lock` site; remeasured 2026-09-30).\n"),
    ("  - src/melder/aether/conduit/meld/meld.py:1054-1068\n",
     "  - src/melder/aether/conduit/meld/meld.py:1167-1175\n"),
    ("  - `src/melder/aether/conduit/meld/meld.py:1033`\n",
     "  - `src/melder/aether/conduit/meld/meld.py:1134`\n"),
    ("a few lines further down. `src/melder/aether/spellbook/spellbook.py:3680`\n",
     "a few lines further down. `src/melder/aether/spellbook/spellbook.py:3686`\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3695, 3868, 4043 (applied seams)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3701, 3876, 4051 (applied seams)\n"),
    ("  `src/melder/aether/spellbook/spellbook.py:6434`; the patch-lane copy cited\n",
     "  `src/melder/aether/spellbook/spellbook.py:6448`; the patch-lane copy cited\n"),
]
for old, new in CITATIONS:
    s.replace(DOC, old, new)

ENTRY = r"- path: `{0}`\n  start_line: 1\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n"
for touched in ("src/melder/aether/spellbook/spellbook.py", "src/melder/aether/conduit/meld/meld.py"):
    matches = re.findall(ENTRY.format(re.escape(touched)), s._load(DOC))
    if len(matches) != 1:
        raise AssertionError(f"code map entry for {touched}: {len(matches)} matches")
    loc = len((pathlib.Path(ROOT) / touched).read_bytes().decode("utf-8").splitlines())
    s.replace(
        DOC,
        matches[0],
        f"- path: `{touched}`\n  start_line: 1\n  end_line: {loc}\n  loc: {loc}\n  verified_at: {NOW}\n",
    )

s.replace(
    DOC,
    "## Context / Handoff Summary\n\n2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214):",
    "## Context / Handoff Summary\n\n"
    "2026-09-30 injected dependencies (0.2.8215): the Meld Resolution Runtime entry carries a dated block (the\n"
    "target pass's flag, the deferred lane's full pass for a spell that is not its Phase 5 root, what is unchanged)\n"
    "and its lazy-validation list; the SpellCompiler entry's Phase-5 publication block, the Meld Runtime Gating\n"
    "subcomponent and the meld-time validation flow follow. Remeasured: the code-map extents of spellbook.py and\n"
    "meld.py, and every citation into spellbook.py, spellbook_creation_system.py and meld.py (several were already\n"
    "2-14 lines stale; meld.py's lock-site ranges had drifted off its lock sites).\n\n"
    "2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214):",
)

long_lines = [
    line for line in s.long_added_lines()
    if "`src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem." not in line
    and "(`_remove_from_spell_index` -> `_apply_remove_from_index`)" not in line
]
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written)
