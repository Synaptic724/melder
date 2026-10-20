"""Promote contract_recheck_on_notch_2026_10_16 (rule 2, 0.2.8250) into src_architecture (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC timestamp> [--check]
Exact-text edits; each anchor must occur once. The numeric citations into the seven changed source files were
remapped beforehand by remap_citations_rule2_2026_10_16.py; this script edits the prose, the code map, the sources
and the handoff.
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
    for a, b in steps:
        for line in b.splitlines():
            body = line.strip()
            for prefix in ("EVIDENCE:", "- "):
                if body.startswith(prefix):
                    body = body[len(prefix):].strip()
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
SSS = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"

STEPS = []

# 1. Architecture Summary: the borrower update and the marks.
STEPS.append((
    "window the conduit has every linked borrower park its copy of the outgoing version and moves\n"
    "index-link borrowers to the new one, which they build at their next meld. MutationResearch records\n",
    "window the conduit has every linked borrower park its copy of the outgoing version, makes a parked copy of\n"
    "the incoming version active again (a version grant, 0.2.8250) and moves index-link borrowers to the new\n"
    "one, which they build at their next meld: each change of a borrower's active copy marks that copy's\n"
    "SpellContract consumers, and the notch marks everything downstream of the notched lineage, for\n"
    "revalidation at their next meld (0.2.8250). MutationResearch records\n",
))
STEPS.append((
    "`Conduit._resolve_spell_to_move` (the index moves' spell_id), `Conduit._deactivate_borrowed_spell` and\n"
    "`src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._emit_index_notch` (the borrowers).\n",
    "`Conduit._resolve_spell_to_move` (the index moves' spell_id), `Conduit._deactivate_borrowed_spell`,\n"
    "`Conduit._activate_borrowed_spell` and\n"
    "`src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._emit_index_notch` (the borrowers); the marks:\n"
    "`src/melder/aether/spellbook/spellbook.py:Spellbook._mark_contract_dependents_dirty` and\n"
    f"`{SSS}:SpellSystemStates.mark_dependents_for_revalidation`.\n",
))

# 2. Meld-time validation gate: rule 2's recheck and the catch-up.
STEPS.append((
    "   of the Book through steps 1-3.\n"
    "\n"
    "### Sequence: Create Lesser Conduit\n",
    "   of the Book through steps 1-3.\n"
    "8. A satisfied SpellContract is not checked on every meld (0.2.8250, rule 2). A change of the provider a contract\n"
    "   consumer resolves marks the consumer `gated` + `contract_unvalidated` - the borrower Book's contracted-map\n"
    "   mutators (`Spellbook._mark_contract_dependents_dirty`) and a notch's downstream walk do - so step 2 is its\n"
    "   recheck: Phase 4's presence check finds the provider, the lineage becomes `valid` and step 2 gates the conduit\n"
    "   verdict (`structure_changed`), so step 3 rebuilds against the provider now active; a missing provider leaves the\n"
    "   lineage `gated` and step 2 raises SpellbookValidationError naming the contract and its remedy. Until 0.2.8250\n"
    "   every gated meld of a consumer read its signature, looked each contract up in the Book's contracted maps\n"
    "   (MeldExecutionError on a miss) and forced step 3 (`Meld._check_contracts_and_force_revalidation`, retired):\n"
    "   1668 us a warm meld of a borrower's consumer on 3.14t with the GIL off, 2.6 us now.\n"
    "9. The catch-up (0.2.8250): before step 2 when the spell will compile at this meld (`Meld._may_compile`: its\n"
    "   lineage unregistered, `unknown` or `gated`, or its verdict for the resolution conduit `unknown` or `gated`;\n"
    "   never for a `resolution_required` spell), and first in step 5's deferred lane,\n"
    "   `Meld._refresh_stale_dependencies` walks the dependencies its plan will expand - every socket target of its\n"
    "   recorded topology and, for a SpellContract socket, the provider the Book's active contracted maps hold, each at\n"
    "   the version its lineage selects now - and refreshes each stale one (`gated` or `unknown`) under that\n"
    "   dependency's rebuild window and lock: phases 1-4 with its owner Book; broken -> `invalid` and\n"
    "   SpellbookValidationError naming it; not `valid` -> the same error; `valid` -> its own plan is reset\n"
    "   (CreationContext cleaned, Phase 5+ artifacts cleared, `resolution_required`), so its own next meld runs its\n"
    "   full target pass. A dependent two hops from a notch thus compiles over its dependency's current structure\n"
    "   instead of a version id the notch parked.\n"
    "\n"
    "### Sequence: Create Lesser Conduit\n",
))

# 3. SpellIndex Mutation Entry: the walk (step 5) and the activate fan-out and the marks (step 6).
STEPS.append((
    "   - notch parks the outgoing active member, promotes the incoming parked\n"
    "     member, repoints the index pointer and the framewide binding signature,\n"
    "     and re-registers the index gated + dirty for lazy meld-time recompile;\n",
    "   - notch parks the outgoing active member, promotes the incoming parked\n"
    "     member, repoints the index pointer and the framewide binding signature,\n"
    "     re-registers the index gated + dirty for lazy meld-time recompile (with\n"
    "     the version's binding key), then marks everything downstream of the\n"
    "     lineage for revalidation - its dependents by registry edge in any Book\n"
    "     and the SpellContract consumers of its binding key, transitively\n"
    "     (`SpellSystemStates.mark_dependents_for_revalidation`, 0.2.8250);\n",
))
STEPS.append((
    "6. After the window the conduit updates its borrowers, by design (corrected 2026-10-15; this step\n"
    "   called it a missing fan-out): `Conduit._deactivate_borrowed_spell` has every linked peer park its\n"
    "   contracted copy of the outgoing version, and `ConduitWard._emit_index_notch` moves each index-link\n"
    "   contract's subscription to the new version, parking the old copy and activating the new one on\n"
    "   the receiver. Borrowers build the new version at their next meld; objects built from older\n"
    "   versions stay alive, so agents iterating on one object keep their work while it converges.\n",
    "6. After the window the conduit updates its borrowers, by design (corrected 2026-10-15; this step\n"
    "   called it a missing fan-out): `Conduit._deactivate_borrowed_spell` has every linked peer park its\n"
    "   contracted copy of the outgoing version, `Conduit._activate_borrowed_spell` has every linked peer make\n"
    "   a parked copy of the incoming version active again - a version grant parked by an earlier notch away\n"
    "   comes back (0.2.8250) - and `ConduitWard._emit_index_notch` moves each index-link contract's\n"
    "   subscription to the new version, parking the old copy and activating the new one on the receiver.\n"
    "   Every change of a borrower's active copy marks that copy's SpellContract consumers (0.2.8250), so\n"
    "   borrowers build the new version at their next meld; objects built from older versions stay alive, so\n"
    "   agents iterating on one object keep their work while it converges.\n",
))
STEPS.append((
    "   - src/melder/aether/conduit/conduit.py:6236-6265\n",
    "   - src/melder/aether/conduit/conduit.py:6236-6265\n"
    "   - src/melder/aether/conduit/conduit.py:6267-6310\n",
))
STEPS.append((
    "   - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2322-2387\n"
    "\n"
    "### Sequence: Change-Control Revalidation\n",
    "   - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2322-2387\n"
    f"   - {SSS}:921-1036\n"
    "\n"
    "### Sequence: Change-Control Revalidation\n",
))

# 4. Operational invariant.
STEPS.append((
    "## Operational Invariants\n"
    "- The notch names its target and checks it (2026-10-16, 0.2.8249):",
    "## Operational Invariants\n"
    "- Contract consumers and dependents follow a provider change (2026-10-16, 0.2.8250; rule 2 of the owner's\n"
    "  2026-10-15 direction): a satisfied SpellContract is not checked on every meld, and a change of what a spell\n"
    "  resolves marks it for revalidation instead. Every change of a conjured Book's ACTIVE contracted copy - added,\n"
    "  parked, reactivated, removed, cleared, by `_add_contracted_spell`, `_deactivate_contracted_spell`,\n"
    "  `_reactivate_contracted_spell`, `_remove_contracted_spell` (its active branch) and\n"
    "  `_clear_contracted_spells_for_conduit` - marks the Book's consumers of the copy's key `gated` +\n"
    "  `contract_unvalidated` through `Spellbook._mark_contract_dependents_dirty`, after the map change is published and\n"
    "  the Book lock released; a parked copy's change, and any change before conjure, marks nothing. Every path that\n"
    "  changes an active copy ends in those five: a grant and its dependency copies, an index link and its members, a\n"
    "  lender's notch on its linked peers and on its index-link receivers, a member's removal, an index destroy, an\n"
    "  uncontract, a remove-all, a root's dependency fallout and an ownership transfer; a sever marks both sides\n"
    "  through `ConduitWard._invalidate_contract_consumers`. A version grant's copy is active exactly while its version\n"
    "  is the lineage's active member: a notch away parks it on every linked peer, and a notch to it - back, or to a\n"
    "  version granted while parked - makes it active again (`Conduit._activate_borrowed_spell`, after the deactivate\n"
    "  fan-out and before the index emission; D3). A notch also marks everything downstream of the notched lineage\n"
    "  (`SpellSystemStates.mark_dependents_for_revalidation`, D2): a lineage reached by a registry edge (frame-wide, so\n"
    "  through borrowed spells too) goes `gated` + `impacted_by_dependency`, transitively dirty; a consumer, in any Book,\n"
    "  of the binding key of a lineage reached gets the contract mark - `register_index(binding_key=...)` records one\n"
    "  key per lineage, `Spell._key`, the normalization `SpellContract.canonical_key` uses; the walk goes on from each,\n"
    "  visits each lineage once and marks no seed, and every contract mark walks on the same way. Mark only: nothing\n"
    "  is built, disposed or extracted, and objects already built keep what they were built with. A marked lineage's\n"
    "  next meld enters the gate (its mark raises the Book flag): the catch-up first refreshes every stale lineage the\n"
    "  plan will expand (phases 1-4 with its owner Book under its window and lock, then its own plan reset), then the\n"
    "  structural branch reruns the spell - Phase 4's presence check is the contract recheck - and a `valid` result\n"
    "  gates the verdict, so phases 5-11 rebuild once; the CreationContext is per spell, so one rebuild serves every\n"
    "  conduit. A warm meld whose lineage and verdict are `valid` reads no signature and walks nothing: on 3.14t a\n"
    "  borrower's contract consumer went from 1668 to 2.6 us a warm meld with the GIL off and from 1705 to 2.7 us with\n"
    "  it on; a provider change costs one more structural rerun (0.8-1.1 ms) and a notch's walk 0.2-0.5 ms more at 200\n"
    "  dependents. Locks: every mark runs with the Book lock free (registry -> state, then RiskManager under the\n"
    "  registry lock); callers may hold a ward lock (the index emissions), a contract lock\n"
    "  (`_remove_root_from_contracts`) or the notch window, and nothing under the registry, state or RiskManager lock\n"
    "  takes a ward, contract, conduit or Book lock, so no cycle closes; the catch-up holds no lock while it walks and\n"
    "  one dependency's window and lock at a time, before the melded spell's own. Not covered, pre-existing: a lent\n"
    "  consumer's Book-local provider loss, `Conduit.validate_resolution`'s conduit-wide pass (it runs no catch-up),\n"
    "  and melds already in flight when a notch fans out (see Failure Modes and Error Paths).\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._mark_contract_dependents_dirty`,\n"
    "  `Spellbook._deactivate_contracted_spell`, `Spellbook._reactivate_contracted_spell`,\n"
    "  `Spellbook._add_contracted_spell`, `Spellbook._remove_contracted_spell`,\n"
    "  `Spellbook._clear_contracted_spells_for_conduit`, `Spellbook._apply_notch`,\n"
    f"  `{SSS}:SpellSystemStates.mark_dependents_for_revalidation`,\n"
    "  `SpellSystemStates._mark_dependents_locked`, `SpellSystemStates.mark_contract_dependents_dirty`,\n"
    "  `SpellSystemStates.register_index`, `src/melder/aether/conduit/meld/meld.py:Meld._ensure_lineage_resolvable`,\n"
    "  `Meld._may_compile`, `Meld._refresh_stale_dependencies`, `Meld._iter_planned_dependencies`,\n"
    "  `Meld._refresh_dependency_structure`, `Meld._ensure_runtime_resolution_ready` and\n"
    "  `src/melder/aether/conduit/conduit.py:Conduit._activate_borrowed_spell`.\n"
    "- The notch names its target and checks it (2026-10-16, 0.2.8249):",
))

# 5. Failure modes.
STRATEGY = "src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py"
STEPS.append((
    "## Failure Modes and Error Paths\n"
    "- `Conduit.notch_spell` refuses its target before anything moves (0.2.8249):",
    "## Failure Modes and Error Paths\n"
    "- Breaking (0.2.8250): a meld of a SpellContract consumer whose provider is gone - an index destroy or unlink, a\n"
    "  version grant parked by a notch away, an uncontract, a remove-all - raises SpellbookValidationError from the\n"
    "  gate's structural branch, the first meld's error, where the per-meld scan raised MeldExecutionError\n"
    "  \"SpellContract could not be resolved. Missing contracted provider for key (frame_key=..., binding_key=...) on\n"
    "  param ...\" (both are RuntimeError). The consumer's block names the contract and the remedy: \"  - Spell\n"
    "  'Consumer' parameter 'service' has no provider for its SpellContract (frame_key='iservice', binding_key='svc'):\n"
    "  no active spell with that frame and binding name is contracted to this Spellbook. Contract one from a linked\n"
    "  conduit (add_index_to_contract, or add_spell_to_contract for one version) and meld again.\n"
    "  [SPELL_CONTRACT_MISSING_PROVIDER]\" - the one Phase-4 warning that holds a lineage gated is shown as the spell's\n"
    "  reason (`SpellbookValidationError.GATING_WARNING_CODES`); before, such a consumer read \"No validation error was\n"
    "  recorded for this spell; ...\".\n"
    "  EVIDENCE: `src/melder/aether/conduit/meld/meld.py:Meld._ensure_lineage_resolvable`,\n"
    f"  `{STRATEGY}:ContractProviderPresenceStrategy.validate`\n"
    "  and `src/melder/utilities/custom_exceptions/spellbook_validation_error.py:SpellbookValidationError._compose`.\n"
    "- Breaking (0.2.8250): a spell that depends on a notched one - by annotation or through a SpellContract, directly\n"
    "  or through others, in its Book or another - builds the version now active at its next meld, or raises the first\n"
    "  meld's error: UnresolvedInputError naming the parameter when the new version no longer resolves it (a class\n"
    "  annotation the kind rule does not select it for), SpellbookValidationError naming a dependency whose refreshed\n"
    "  structure is broken or not valid. Before, one built before the notch went on building the old version, and one\n"
    "  never built raised RuntimeError \"many_only manifest references unknown spell_id '<the old version id>'\" on\n"
    "  every meld; a dependent two hops away that did compile recorded a visibility failure and stayed refused.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._apply_notch` and\n"
    "  `src/melder/aether/conduit/meld/meld.py:Meld._refresh_stale_dependencies`.\n"
    "- Fixed in 0.2.8250: a contract consumer whose borrowed provider changed without a notch of the owner's index kept\n"
    "  its plan - after `remove_index_from_contract` it stayed `valid` and built the released provider; after a link or\n"
    "  a grant its dependents kept a plan compiled while the provider was missing, built with the raw `SpellContract`\n"
    "  default (AttributeError \"'SpellContract' object has no attribute '<method>'\"); and a version grant parked by a\n"
    "  notch away stayed parked after the notch back, so its consumer had no provider until the version was granted\n"
    "  again.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._remove_contracted_spell`,\n"
    f"  `{SSS}:SpellSystemStates.mark_contract_dependents_dirty`\n"
    "  and `src/melder/aether/conduit/conduit.py:Conduit._activate_borrowed_spell`.\n"
    "- Known, not fixed (pre-existing; filed as TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout): a\n"
    "  meld of a borrower's contract consumer on another thread while its lender notches the provider, on a\n"
    "  free-threaded build, can return the consumer built with its raw `SpellContract` default (a target pass compiled\n"
    "  while the copy was parked; calling it raises AttributeError) or raise RuntimeError \"many_only manifest\n"
    "  references unknown spell_id\" (the plan named the parked version), \"Cannot build CreationContext before\n"
    "  spell_codegen_creation exists.\" or \"Spell creation context was not published: ...\" (a meld admitted after\n"
    "  another meld's pass failed). `notch_spell` fans out after its transaction ends, so a meld already past the gate\n"
    "  is not ordered against the park and the activation; the marks make the next meld correct, not one in flight.\n"
    "  Measured: 7 of 20 runs of four meld threads against 20 notches end a thread with one of these before and after\n"
    "  0.2.8250 (the scan's MeldExecutionError is no longer among them); 0 of 20 with the GIL on.\n"
    "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.notch_spell`.\n"
    "- `Conduit.notch_spell` refuses its target before anything moves (0.2.8249):",
))

# 6. Code map: five files remeasured, two added.
STEPS.append((
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 7618\n"
    "  loc: 7618\n"
    "  verified_at: 2026-10-16T11:03:50Z\n",
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 7759\n"
    "  loc: 7759\n"
    f"  verified_at: {TS}\n",
))
STEPS.append((
    "    conjure holds since conjure stamps them (0.2.8248).\n"
    "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`\n",
    "    conjure holds since conjure stamps them (0.2.8248); the five contracted-map mutators mark their key's\n"
    "    SpellContract consumers (`_mark_contract_dependents_dirty`), bind and `_apply_notch` record the binding key,\n"
    "    and `_apply_notch` marks everything downstream of the notched lineage (0.2.8250).\n"
    "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`\n",
))
STEPS.append((
    "- path: `src/melder/aether/conduit/conduit.py`\n"
    "  start_line: 1\n"
    "  end_line: 7784\n"
    "  loc: 7784\n"
    "  verified_at: 2026-10-16T15:44:44Z\n",
    "- path: `src/melder/aether/conduit/conduit.py`\n"
    "  start_line: 1\n"
    "  end_line: 7837\n"
    "  loc: 7837\n"
    f"  verified_at: {TS}\n",
))
STEPS.append((
    "    and `add_to_spell_index` / `remove_from_spell_index` take `spell_id=` too (0.2.8249).\n"
    "- path: `src/melder/aether/conduit/conduit_pool.py`\n",
    "    and `add_to_spell_index` / `remove_from_spell_index` take `spell_id=` too (0.2.8249); after a notch every\n"
    "    linked peer's parked copy of the incoming version is made active again (`_activate_borrowed_spell`,\n"
    "    0.2.8250).\n"
    "- path: `src/melder/aether/conduit/conduit_pool.py`\n",
))
STEPS.append((
    "- path: `src/melder/aether/conduit/conduit_ward/conduit_ward.py`\n"
    "  start_line: 1\n"
    "  end_line: 3957\n"
    "  loc: 3957\n"
    "  verified_at: 2026-10-14T23:59:35Z\n"
    "  note: contracts and lineage; owner-side emissions under the ward lock, contract reads under the contract\n"
    "    lock, the listing resolved through the Book (0.2.8231).\n",
    "- path: `src/melder/aether/conduit/conduit_ward/conduit_ward.py`\n"
    "  start_line: 1\n"
    "  end_line: 3965\n"
    "  loc: 3965\n"
    f"  verified_at: {TS}\n"
    "  note: contracts and lineage; owner-side emissions under the ward lock, contract reads under the contract\n"
    "    lock, the listing resolved through the Book (0.2.8231); the version grant's docstring says what a notch does\n"
    "    to its copy (0.2.8250).\n",
))
STEPS.append((
    "- path: `src/melder/aether/conduit/meld/meld.py`\n"
    "  start_line: 1\n"
    "  end_line: 2150\n"
    "  loc: 2150\n"
    "  verified_at: 2026-10-15T21:20:35Z\n"
    "  note: meld orchestration; the live probes' managed-pool answer (0.2.8243).\n",
    "- path: `src/melder/aether/conduit/meld/meld.py`\n"
    "  start_line: 1\n"
    "  end_line: 2378\n"
    "  loc: 2378\n"
    f"  verified_at: {TS}\n"
    "  note: meld orchestration; the live probes' managed-pool answer (0.2.8243); the per-meld contract scan retired\n"
    "    and the catch-up of stale dependencies before a plan compiles (0.2.8250).\n",
))
STEPS.append((
    f"- path: `{SSS}`\n"
    "  start_line: 1\n"
    "  end_line: 1886\n"
    "  loc: 1886\n"
    "  verified_at: 2026-10-16T01:12:19Z\n"
    "  note: lineage registry; retires a spell id's per-conduit verdicts on unregister and on register (0.2.8219);\n"
    "    writes `SpellState.non_resolvable` from the registration's capability and publishes the flagged lineages\n"
    "    (`non_resolvable_index_ids`, 0.2.8247).\n",
    f"- path: `{SSS}`\n"
    "  start_line: 1\n"
    "  end_line: 2052\n"
    "  loc: 2052\n"
    f"  verified_at: {TS}\n"
    "  note: lineage registry; retires a spell id's per-conduit verdicts on unregister and on register (0.2.8219);\n"
    "    writes `SpellState.non_resolvable` from the registration's capability and publishes the flagged lineages\n"
    "    (`non_resolvable_index_ids`, 0.2.8247); records a binding key per lineage, marks everything downstream of a\n"
    "    notch (`mark_dependents_for_revalidation`) and walks on from every contract mark (0.2.8250).\n",
))
STEPS.append((
    "  note: Phase-4 refusal of a single typed parameter with several providers; names every candidate's address (0.2.8224).\n"
    "- path: `src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py`\n",
    "  note: Phase-4 refusal of a single typed parameter with several providers; names every candidate's address (0.2.8224).\n"
    f"- path: `{STRATEGY}`\n"
    "  start_line: 1\n"
    "  end_line: 264\n"
    "  loc: 264\n"
    f"  verified_at: {TS}\n"
    "  note: Phase-4 SpellContract presence check, the recheck a marked consumer's next meld runs; walks snapshots of\n"
    "    the contracted maps and names a lost provider's contract and remedy (0.2.8250).\n"
    "- path: `src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py`\n",
))
STEPS.append((
    "  note: `ManagedSpellExhaustedError`, a MeldExecutionError raised before a refused managed meld builds\n"
    "    anything (0.2.8243).\n",
    "  note: `ManagedSpellExhaustedError`, a MeldExecutionError raised before a refused managed meld builds\n"
    "    anything (0.2.8243).\n"
    "- path: `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`\n"
    "  start_line: 1\n"
    "  end_line: 493\n"
    "  loc: 493\n"
    f"  verified_at: {TS}\n"
    "  note: `SpellbookValidationError`; a gating Phase-4 warning (`GATING_WARNING_CODES`) is shown as a spell's\n"
    "    reason (0.2.8250).\n",
))

# 7. Information sources.
STEPS.append((
    "- `src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py`\n"
    "- `src/melder/aether/conduit/meld/meld.py`\n",
    "- `src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py`\n"
    "- `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`\n"
    "- `src/melder/aether/conduit/meld/meld.py`\n",
))

# 8. Handoff.
STEPS.append((
    "## Context / Handoff Summary\n"
    "\n"
    "2026-10-16 public notch target (0.2.8249):",
    "## Context / Handoff Summary\n"
    "\n"
    "2026-10-16 contract recheck on notch (0.2.8250; rule 2 of the owner's 2026-10-15 direction, his decisions D1-D5):\n"
    "a satisfied SpellContract is no longer checked on every meld. A change of what a spell resolves marks it instead -\n"
    "the borrower Book's five contracted-map mutators mark their key's consumers, a notch marks everything downstream\n"
    "of the notched lineage (registry edges and contract keys, transitively; D2) and every contract mark walks on -\n"
    "and before a plan compiles the meld refreshes each stale lineage the plan expands (D2); a lost provider is named\n"
    "with its remedy (D1-B); a notch back makes a parked version grant active again (D3). The boundary summary, the\n"
    "meld-time gate and SpellIndex mutation sequences, a new operational invariant, four failure modes (two Breaking,\n"
    "one known race), the code map (five files remeasured, two added) and the sources carry it; the component map\n"
    "carries the per-component contracts. Every numeric citation into the seven changed files was remapped line by\n"
    "line across the edit. Open: in-flight borrower melds racing a notch's fan-out\n"
    "(TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout) and a lent consumer's Book-local provider\n"
    "loss (TASK-2026-10-16-investigate_lent_consumer_provider_loss).\n"
    "\n"
    "2026-10-16 public notch target (0.2.8249):",
))

apply(ROOT, DOC, STEPS, CHECK)
