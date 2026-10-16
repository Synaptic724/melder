"""Promote contract_recheck_on_notch_2026_10_16 (rule 2, 0.2.8250) into src_components (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC timestamp> [--check]
Exact-text edits; each anchor must occur once. The numeric citations were remapped beforehand by
remap_citations_rule2_2026_10_16.py; this script edits the component prose, the C2 entries, two call flows, the code
map, the sources and the handoff.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from land_docs_src_architecture_rule2_2026_10_16_lib import apply  # noqa: shared long-line policy

TS = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
ROOT = pathlib.Path(".")
DOC = "context_compass/system_docs/src_components.md"
SSS = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"
STRATEGY = "src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py"
ERR = "src/melder/utilities/custom_exceptions/spellbook_validation_error.py"

STEPS = []

# 1. Spellbook Core: the five mutators' marks, the binding key, the notch's walk, the seal docstrings.
STEPS.append((
    "### Component: Spellbook Core (Binding and Conjure)\n"
    "Parked versions wired at conjure (2026-10-16, 0.2.8248):",
    "### Component: Spellbook Core (Binding and Conjure)\n"
    "Contract consumers marked on a provider change (2026-10-16, 0.2.8250; rule 2 of contract_recheck_on_notch): the five\n"
    "mutators of a Book's ACTIVE contracted (borrowed) copies - `_add_contracted_spell`, `_deactivate_contracted_spell`,\n"
    "`_reactivate_contracted_spell`, `_remove_contracted_spell` (its active branch) and\n"
    "`_clear_contracted_spells_for_conduit` - read `_conjured` and the copy's key inside the critical section that changes\n"
    "the maps and, once the Book lock is released, call `_mark_contract_dependents_dirty({key})` (the clear: the key of\n"
    "every active copy it dropped, `_make_spell_key` as `_add_contracted_spell` files them). The helper is a no-op for no\n"
    "keys; otherwise one `SpellSystemStates.mark_contract_dependents_dirty(spellbook_id=..., contract_keys=...)` call,\n"
    "which gates the Book's consumers of those keys (`contract_unvalidated`) and walks on to what depends on them;\n"
    "RuntimeError when the registry is missing, and a registry failure is logged and re-raised after the map change,\n"
    "which stays published (the policy of `_mark_collection_dependents_dirty`). A parked copy's change\n"
    "(`_add_inactive_contracted_spell`, the parked branch of `_remove_contracted_spell`) and any change before conjure\n"
    "mark nothing. `_add_contracted_spell` marks after its collection mark; every mark comes before the mutator's\n"
    "staged-key refresh and RiskManager call where it has them. `bind` and `_apply_notch` pass `binding_key=spell._key`\n"
    "to `register_index`, and `_apply_notch`, right after its `register_index` and outside the Book lock, calls\n"
    "`mark_dependents_for_revalidation((spell_index.id,))`: a notch marks everything downstream of the notched lineage,\n"
    "its comment \"so dependents revalidate\" now holds, its step list gains the mark, and its docstring says the owning\n"
    "Conduit updates borrowers after the window. `_notch_spell`'s and `_apply_notch`'s docstrings no longer say the notch\n"
    "claims the Book INTENT: the notch strategy's seal claims the Book, the acting conduit, the conduits linked to it and\n"
    "the binding key EXCLUSIVE (corrected 2026-10-16).\n"
    "EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._mark_contract_dependents_dirty`,\n"
    "`Spellbook._deactivate_contracted_spell`, `Spellbook._reactivate_contracted_spell`, `Spellbook._add_contracted_spell`,\n"
    "`Spellbook._remove_contracted_spell`, `Spellbook._clear_contracted_spells_for_conduit`, `Spellbook.bind`,\n"
    "`Spellbook._notch_spell` and `Spellbook._apply_notch`.\n"
    "\n"
    "Parked versions wired at conjure (2026-10-16, 0.2.8248):",
))

# 2. Conduit Runtime: D3.
STEPS.append((
    "- Execution scope for resolving spells and managing object lifecycles.\n"
    "\n"
    "Notch target (2026-10-16, 0.2.8249):",
    "- Execution scope for resolving spells and managing object lifecycles.\n"
    "\n"
    "Notch fan-out reactivates version grants (2026-10-16, 0.2.8250; D3 of contract_recheck_on_notch): when a notch\n"
    "changed the active version, `notch_spell` - after its transaction ends - calls\n"
    "`_deactivate_borrowed_spell(outgoing_id)`, then the new `_activate_borrowed_spell(spell.spell_id)`, then\n"
    "`ConduitWard._emit_index_notch`. `_activate_borrowed_spell`\n"
    "(`check_cleaned` first, no lock of its own) walks `ConduitWard._get_links()` and calls each peer Book's\n"
    "`_activate_contract_spell(owner_id, spell_id)`, a no-op unless that peer holds a parked copy of the version, which it\n"
    "then reactivates through `_reactivate_contracted_spell` - whose rule-2 mark sends the copy's consumers to\n"
    "revalidation. So a version grant (`add_spell_to_contract`) is active exactly while its version is the lineage's active\n"
    "member: parked by a notch away, active again on the notch back, and a grant of a version parked when it was made\n"
    "becomes active on the notch to it. Outgoing first, so no peer holds two active copies under one key; an index-link\n"
    "receiver holding a parked copy of the incoming version gets it back here, and the index emission then finds it active.\n"
    "Objects already built are untouched. RuntimeError when this conduit or a linked peer's Book has been cleaned.\n"
    "EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.notch_spell`, `Conduit._activate_borrowed_spell` and\n"
    "`src/melder/aether/spellbook/spellbook.py:Spellbook._activate_contract_spell`.\n"
    "\n"
    "Notch target (2026-10-16, 0.2.8249):",
))

# 3. ConduitWard and Contracts: the version grant's semantics.
STEPS.append((
    "### Component: ConduitWard and Contracts\n"
    "Purpose:\n"
    "- Control-plane manager for conduit contracts and lineage links.\n"
    "\n",
    "### Component: ConduitWard and Contracts\n"
    "Purpose:\n"
    "- Control-plane manager for conduit contracts and lineage links.\n"
    "\n"
    "Version grants and notches (2026-10-16, 0.2.8250): `_add_spell_to_contract` contracts one version of the spell's\n"
    "SpellIndex lineage - the borrower's copy is active while that version is the lineage's active member and parked while\n"
    "it is not (parked by a notch away on every linked peer, active again on a notch back through\n"
    "`Conduit._activate_borrowed_spell`; a grant of a parked version starts parked and becomes active on the notch to it) -\n"
    "while an index link (`_add_index_to_contract`) follows the lineage to every new version (`_emit_index_notch`). The\n"
    "grant's docstring said lookups resolve to each new version, which only an index link does (corrected 2026-10-16), and\n"
    "`_emit_index_notch`'s docstring names both conduit fan-outs. Every change these make to a borrower's active copy ends\n"
    "in the borrower Book's contracted-map mutators, which mark the copy's SpellContract consumers for revalidation (rule\n"
    "2; see Spellbook Core). `_invalidate_contract_consumers` keeps marking and extracting on grant, uncontract, sever and\n"
    "remove-all, and its registry mark now walks on to what depends on the consumers. `_get_spell_contract_keys`'s\n"
    "comment names the Phase 8 analyzer's signature read it mirrors, since Meld's copy is gone.\n"
    "EVIDENCE: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._add_spell_to_contract`,\n"
    "`ConduitWard._emit_index_notch`, `ConduitWard._get_spell_contract_keys` and\n"
    "`src/melder/aether/conduit/conduit.py:Conduit._activate_borrowed_spell`.\n"
    "\n",
))

# 4. Meld Resolution Runtime: the scan retired, the catch-up.
STEPS.append((
    "### Component: Meld Resolution Runtime\n"
    "Managed doors, probes and purge (2026-10-15, 0.2.8243-0.2.8245):",
    "### Component: Meld Resolution Runtime\n"
    "Contract recheck and the catch-up (2026-10-16, 0.2.8250; rule 2 and D2 of contract_recheck_on_notch): the per-meld\n"
    "SpellContract scan is retired - `_check_contracts_and_force_revalidation` and Meld's `_iter_spell_contract_defaults`\n"
    "are gone, with the `annotationlib.Format` and `SpellContract` imports (the Phase 8 analyzer and the Phase 9 processor\n"
    "keep their own signature reads). A contract consumer is rechecked by the gate's structural branch when a change of\n"
    "its provider has marked it `gated` + `contract_unvalidated`: Phase 4's presence check, then `structure_changed` gates\n"
    "its verdict so 5-11 rebuild once; a lost provider leaves it `gated` and the branch raises\n"
    "`SpellbookValidationError([spell])`, which names the contract (D1-B). `_ensure_lineage_resolvable` first runs the\n"
    "catch-up when `_may_compile(spell)` says the spell will compile at this meld - False for a `resolution_required`\n"
    "spell, whose deferred lane runs its own catch-up first; True for an unregistered, `unknown` or `gated` lineage and\n"
    "for a `valid` one whose effective verdict (`_get_resolution_validity`) is `unknown` or `gated`; False otherwise, so\n"
    "a valid spell with a valid verdict pays two state reads and nothing more - and `_ensure_runtime_resolution_ready`\n"
    "runs it for a flagged spell before its own window. `_refresh_stale_dependencies(spell)` walks depth first from the\n"
    "spell's recorded topology through `_iter_planned_dependencies` (every socket's `target_spell_ids` and, for a\n"
    "SPELL_CONTRACT socket, the provider the compiling Book's active contracted maps hold for its key - the lookup map\n"
    "through a one-call snapshot, then the index, then the copy - each taken to its lineage's current version by\n"
    "`_current_in_pool` and skipped when the Book's pool lacks it), visits each spell once and refreshes a dependency only\n"
    "when `_is_stale` (registered and `gated` or `unknown`). `_refresh_dependency_structure` enters the dependency's\n"
    "rebuild window, then its lock, re-checks staleness and runs phases 1-4 with the dependency's own Book (a borrowed\n"
    "provider is refreshed by its lender's Book); a broken result pins it `invalid` and raises\n"
    "`SpellbookValidationError([dependency])`, as does one still not `valid`; a valid existing creation or\n"
    "non-resolvable definition is left as it is, and any other gets `resolution_complete=False`,\n"
    "`resolution_required=True`, its CreationContext cleaned (which moves its door epoch) and its Phase 5+ artifacts\n"
    "cleared with `requires_spellspace_request` kept, so its next own meld runs its full target pass. The walk holds no\n"
    "lock; a refresh holds one dependency's window and lock; the melded spell's own window and lock come after.\n"
    "EVIDENCE: `src/melder/aether/conduit/meld/meld.py:Meld._ensure_lineage_resolvable`, `Meld._may_compile`,\n"
    "`Meld._is_stale`, `Meld._refresh_stale_dependencies`, `Meld._iter_planned_dependencies`, `Meld._current_in_pool`,\n"
    "`Meld._refresh_dependency_structure` and `Meld._ensure_runtime_resolution_ready`.\n"
    "\n"
    "Managed doors, probes and purge (2026-10-15, 0.2.8243-0.2.8245):",
))
STEPS.append((
    "  _force_resolution_revalidation helper accepts the reason; contract callers retain their default.\n",
    "  _force_resolution_revalidation helper accepts the reason; its `contract_unvalidated` default has no Meld caller\n"
    "  since the per-meld contract scan was retired (0.2.8250; this said contract callers retain their default).\n",
))
STEPS.append((
    "- A spell flagged `resolution_required` runs the deferred lane instead: 8-11 for its own Phase 5 root or an\n"
    "  existing creation, otherwise its full target pass 5-11 (0.2.8215; see Injected dependencies above).\n",
    "- A spell flagged `resolution_required` runs the deferred lane instead: 8-11 for its own Phase 5 root or an\n"
    "  existing creation, otherwise its full target pass 5-11 (0.2.8215; see Injected dependencies above).\n"
    "- Before a plan compiles, the gate and the deferred lane refresh the structure of every stale dependency the plan\n"
    "  expands (`Meld._refresh_stale_dependencies`, 0.2.8250); a SpellContract consumer is rechecked by the structural\n"
    "  rerun once a provider change has marked it, never by a per-meld scan.\n",
))

# 5. SpellCompiler and Validation Pipeline: the strategy's snapshot and message, the renderer.
STEPS.append((
    "- Compile per-spell artifacts and validate correctness before resolution.\n"
    "\n"
    "Managed sites (2026-10-15, 0.2.8241 and 0.2.8245):",
    "- Compile per-spell artifacts and validate correctness before resolution.\n"
    "\n"
    "Contract presence recheck and the lost-provider report (2026-10-16, 0.2.8250; D1-B of contract_recheck_on_notch):\n"
    "`ContractProviderPresenceStrategy` is now also the recheck a marked consumer's next meld runs, so it builds its\n"
    "pass-cached provider map from one-call snapshots of the Book's contracted maps (`list(...values())`,\n"
    "`list(...items())`): a recheck can run while the provider change that marked it is still writing them under the Book\n"
    "lock. Its SPELL_CONTRACT_MISSING_PROVIDER warning, the one Phase 4 gates a lineage on, names the contract and the\n"
    "remedy - \"Spell 'Consumer' parameter 'service' has no provider for its SpellContract (frame_key='iservice',\n"
    "binding_key='svc'): no active spell with that frame and binding name is contracted to this Spellbook. Contract one\n"
    "from a linked conduit (add_index_to_contract, or add_spell_to_contract for one version) and meld again.\" - with code,\n"
    "severity and details unchanged. `SpellbookValidationError.GATING_WARNING_CODES` is\n"
    "`frozenset({\"SPELL_CONTRACT_MISSING_PROVIDER\"})`, pinned by a unit test to the codes `CompilerPhase4.run` gates on:\n"
    "`_spell_errors` returns a spell's errors, its gating warnings in issue order and the count of its other warnings;\n"
    "`_compose` lists a spell's gating warnings as its reasons (\"  - <message> [CODE]\", never `[internal]`) when it\n"
    "shows no error and counts them with the hidden warnings when it does, and shows a block when it has errors or gating\n"
    "warnings, or when no diagnostics were handed in, where a spell with neither still reads \"No validation error was\n"
    "recorded\". The first line and the type are unchanged.\n"
    f"EVIDENCE: `{STRATEGY}:ContractProviderPresenceStrategy.validate`,\n"
    f"`{ERR}:SpellbookValidationError._spell_errors` and\n"
    "`SpellbookValidationError._compose`.\n"
    "\n"
    "Managed sites (2026-10-15, 0.2.8241 and 0.2.8245):",
))

# 6. C2 Meld Runtime Gating.
STEPS.append((
    "  `SpellState.non_resolvable`; a resolvable=False target is refused before the gate either way (0.2.8247).\n"
    "Data Structures:\n"
    "- SpellSystemStates lineage validity and change-control dirty-root state.\n",
    "  `SpellState.non_resolvable`; a resolvable=False target is refused before the gate either way (0.2.8247).\n"
    "- Before a plan compiles, `Meld._refresh_stale_dependencies(...)` - run by `_ensure_lineage_resolvable` when\n"
    "  `Meld._may_compile` and by the deferred lane for a flagged spell - refreshes the stale lineages the plan expands;\n"
    "  there is no per-meld SpellContract scan: a provider change marks the consumer and the structural rerun rechecks\n"
    "  it (0.2.8250).\n"
    "Data Structures:\n"
    "- SpellSystemStates lineage validity and change-control dirty-root state.\n",
))

# 7. C2 SpellSystemStates Registry.
STEPS.append((
    "  lineage out of the set; `index_has_flag(index_id, flag)` is the per-lineage read (0.2.8247). EVIDENCE:\n"
    "  src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:SpellSystemStates.register_index.\n"
    "Scope:\n",
    "  lineage out of the set; `index_has_flag(index_id, flag)` is the per-lineage read (0.2.8247). EVIDENCE:\n"
    "  src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:SpellSystemStates.register_index.\n"
    "- `register_index(..., *, resolvable=None, binding_key=None)` records the selected version's normalized\n"
    "  `(frame_key, binding_key)` (`Spell._key`; bind and `_apply_notch` pass it) in `_binding_key_by_index`; None keeps\n"
    "  the recorded key, a value that is not a pair of strings raises TypeError before anything is registered, and\n"
    "  `unregister_index` and `cleanup` drop it (0.2.8250). `mark_dependents_for_revalidation(index_ids) -> Set[str]`\n"
    "  (`check_cleaned` before and under the registry lock) walks from the seeds over `direct_dependents` and, through a\n"
    "  reached lineage's recorded key, over its SpellContract consumers in every Book's contract index; it marks every\n"
    "  reached lineage but the seeds - edge-reached `mark_transitively_dirty()`, contract-reached `gated` +\n"
    "  `contract_unvalidated` (not transitively dirty), both when reached both ways - adds them to the dirty set, skips a\n"
    "  lineage with no state, visits each once (a cycle ends the walk) and returns the ids it marked.\n"
    "  `mark_contract_dependents_dirty` walks on from the consumers it gates through the same body\n"
    "  (`_mark_dependents_locked`) and still returns only those consumers, so `ConduitWard._invalidate_contract_consumers`\n"
    "  extracts only theirs. `Spellbook._apply_notch` calls the walk with the notched lineage. EVIDENCE:\n"
    f"  {SSS}:SpellSystemStates.mark_dependents_for_revalidation.\n"
    "Scope:\n",
))
STEPS.append((
    "- `_non_resolvable_index_ids`: the published frozenset of flagged lineages, replaced whole; an empty set is left\n"
    "  as a tombstone at cleanup (0.2.8247).\n",
    "- `_non_resolvable_index_ids`: the published frozenset of flagged lineages, replaced whole; an empty set is left\n"
    "  as a tombstone at cleanup (0.2.8247).\n"
    "- `_binding_key_by_index`: lineage id -> the binding key its selected version was registered under (0.2.8250).\n",
))
STEPS.append((
    "  so the RiskManager refresh a registration's event runs reads the new set, and a read racing cleanup finds the\n"
    "  tombstone (0.2.8247).\n",
    "  so the RiskManager refresh a registration's event runs reads the new set, and a read racing cleanup finds the\n"
    "  tombstone (0.2.8247).\n"
    "- The downstream walk runs under the registry lock (an RLock: `mark_contract_dependents_dirty` already holds it when\n"
    "  it walks on); each mark takes the state's lock and publishes to RiskManager outside it, under the registry lock;\n"
    "  it takes no Book, conduit, ward or contract lock, so its callers may hold those (0.2.8250).\n",
))

# 8. Flows: the meld-time gate and the notch.
STEPS.append((
    "   at the door before step 1, no longer keeps every meld of its Book in this flow (0.2.8247).\n"
    "\n"
    "### Flow: Create Lesser Conduit\n",
    "   at the door before step 1, no longer keeps every meld of its Book in this flow (0.2.8247).\n"
    "7. Catch-up first (0.2.8250): when `Meld._may_compile(spell)`, `Meld._refresh_stale_dependencies(spell)` ->\n"
    "   `Meld._iter_planned_dependencies` (the registry topology; the Book's contracted maps for SPELL_CONTRACT keys;\n"
    "   `Meld._current_in_pool`) -> for each stale one `Meld._refresh_dependency_structure` (its rebuild window, its lock,\n"
    "   `SpellCompilerSystem.run_structural_phases(dependency._spellbook, dependency)`, the plan reset); step 4's deferred\n"
    "   lane runs it before its own window.\n"
    "8. Step 2 is a SpellContract consumer's recheck (0.2.8250): its mark (`Spellbook._mark_contract_dependents_dirty` or\n"
    "   `SpellSystemStates.mark_dependents_for_revalidation`) left it `gated`; Phase 4's `ContractProviderPresenceStrategy`\n"
    "   finds the provider, or step 2 raises SpellbookValidationError naming the contract. The former step between 2 and\n"
    "   3, `Meld._check_contracts_and_force_revalidation`, is retired.\n"
    "\n"
    "### Flow: Create Lesser Conduit\n",
))
STEPS.append((
    "   `Spellbook._apply_notch` (park the outgoing version, `_reactivate_owned_spell` the incoming one, repoint the\n"
    "   index and the framewide lookup, re-register the index gated). Any raise -> `end_transaction(success=False)`\n",
    "   `Spellbook._apply_notch` (park the outgoing version, `_reactivate_owned_spell` the incoming one, repoint the\n"
    "   index and the framewide lookup, re-register the index gated with its binding key, then\n"
    "   `SpellSystemStates.mark_dependents_for_revalidation` from the notched lineage, 0.2.8250). Any raise ->\n"
    "   `end_transaction(success=False)`\n",
))
STEPS.append((
    "5. `end_transaction(success=True)`; when the version changed, `Conduit._deactivate_borrowed_spell(outgoing_id)` and\n"
    "   `ConduitWard._emit_index_notch(spell_index, outgoing_id, spell.spell_id)`; returns the now-active Spell.\n",
    "5. `end_transaction(success=True)`; when the version changed, `Conduit._deactivate_borrowed_spell(outgoing_id)`,\n"
    "   `Conduit._activate_borrowed_spell(spell.spell_id)` (0.2.8250) and `ConduitWard._emit_index_notch(spell_index,\n"
    "   outgoing_id, spell.spell_id)` - each borrower Book's mutator marks the changed copy's consumers; returns the\n"
    "   now-active Spell.\n",
))

# 9. Code map (core): seven files remeasured.
def entry(path, old_end, old_ts, new_end, note_old=None, note_new=None):
    old = (f"- path: `{path}`\n  start_line: 1\n  end_line: {old_end}\n  loc: {old_end}\n  verified_at: {old_ts}\n")
    new = (f"- path: `{path}`\n  start_line: 1\n  end_line: {new_end}\n  loc: {new_end}\n  verified_at: {TS}\n")
    if note_old is not None:
        old += note_old
        new += note_new
    return old, new


STEPS.append(entry("src/melder/aether/spellbook/spellbook.py", 7618, "2026-10-16T11:09:31Z", 7759))
STEPS.append(entry("src/melder/aether/conduit/conduit.py", 7784, "2026-10-16T15:47:00Z", 7837))
STEPS.append(entry("src/melder/aether/conduit/conduit_ward/conduit_ward.py", 3957, "2026-10-14T23:59:35Z", 3965))
STEPS.append(entry("src/melder/aether/conduit/meld/meld.py", 2150, "2026-10-15T21:40:35Z", 2378))
STEPS.append(entry(SSS, 1886, "2026-10-16T01:15:52Z", 2052))
STEPS.append(entry(STRATEGY, 248, "2026-09-26T20:10:34Z", 264))
STEPS.append(entry(
    ERR, 448, "2026-10-01T11:06:26Z", 493,
    "  note: `SpellbookValidationError`: names the spells conjure cannot build (SpellCompiler).\n",
    "  note: `SpellbookValidationError`: names the spells conjure cannot build (SpellCompiler); a gating Phase-4\n"
    "    warning is a spell's reason (0.2.8250).\n",
))

# 10. Information sources.
STEPS.append((
    "- `src/melder/utilities/custom_exceptions/spell_space_scope_error.py`\n"
    "- `src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py`\n",
    "- `src/melder/utilities/custom_exceptions/spell_space_scope_error.py`\n"
    "- `src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py`\n"
    f"- `{ERR}`\n",
))

# 11. Handoff.
STEPS.append((
    "## Context / Handoff Summary\n"
    "\n"
    "2026-10-16 public notch target (0.2.8249):",
    "## Context / Handoff Summary\n"
    "\n"
    "2026-10-16 contract recheck on notch (0.2.8250; rule 2 of the owner's 2026-10-15 direction, his decisions D1-D5):\n"
    "Spellbook Core carries the five contracted-map mutators' marks, the binding key at bind and notch, the notch's\n"
    "downstream walk and the seam docstrings' seal, corrected from spellbook INTENT to EXCLUSIVE (the 0.2.8249 entry's\n"
    "open item); Conduit Runtime and ConduitWard carry the notch fan-out that makes a parked version grant active again\n"
    "and the grant's corrected semantics (D3); Meld Resolution Runtime carries the retired per-meld scan and the catch-up\n"
    "of stale dependencies before a plan compiles (D2), with Meld Runtime Gating, the meld-time gate flow and an\n"
    "invariant updated; SpellCompiler carries the contract presence recheck and the lost-provider report (D1-B); the\n"
    "SpellSystemStates Registry carries the binding key per lineage and the downstream walk; the notch flow, the code\n"
    "map (seven files remeasured) and the sources follow. Every numeric citation into the seven changed files was\n"
    "remapped line by line across the edit. Open: in-flight borrower melds racing a notch's fan-out and a lent\n"
    "consumer's Book-local provider loss (src_architecture, failure modes; each has its own task).\n"
    "\n"
    "2026-10-16 public notch target (0.2.8249):",
))

apply(ROOT, DOC, STEPS, CHECK)
