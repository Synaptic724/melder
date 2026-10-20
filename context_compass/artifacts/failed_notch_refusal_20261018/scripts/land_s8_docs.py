"""Land S8's document edits in the four system documents (melder_1; STORY-2026-10-17-failed_notch_keeps_switch_
without_borrowers, patch failed_notch_refusal_2026_10_18). Each old text must occur exactly once; every new line
stays within 120 characters (a lone unbreakable token excepted); files must be LF; every write is read back.
{now} is the UTC time of the run and {V} the notch the docs name, checked against `__version__` (the notch before
it, or it). The three citations remap_s8_citations.py widened to 4022-4041 cite the comment's first three lines.
Usage: land_s8_docs.py --root <tree> --version <V> --check|--apply
"""
import datetime
import pathlib
import re
import sys

ARCH = "context_compass/system_docs/src_architecture.md"
COMP = "context_compass/system_docs/src_components.md"
TCOMP = "context_compass/system_docs/tests_components.md"
TARCH = "context_compass/system_docs/tests_architecture.md"
VERSION_FILE = "src/melder/__version__.py"

# ---- src_architecture ------------------------------------------------------------------------------------------
ARCH_CITE = (
    "same thing and are also wrong - see `src/melder/aether/spellbook/spellbook.py:4022-4041`, which states the",
    "same thing and are also wrong - see `src/melder/aether/spellbook/spellbook.py:4022-4024`, which states the",
)
ARCH_BOUNDARY = (
    "  Book's spell or target index, a non-member or only member on removal). Since 0.2.8253 the spell_id lookups\n",
    "  Book's spell or target index, a non-member or only member on removal). A notch whose incoming version fails\n"
    "  its structural check is refused with nothing moved ({V}): SpellbookValidationError, its first line saying the\n"
    "  notch did not happen and naming the version still active. Since 0.2.8253 the spell_id lookups\n",
)
ARCH_SUMMARY = (
    "index before anything moves; the two index moves take a spell_id the same way (0.2.8249).\n",
    "index before anything moves; the two index moves take a spell_id the same way (0.2.8249). A notch whose\n"
    "incoming version fails its structural check is undone inside the window and refused, its borrowers untouched\n"
    "({V}).\n",
)
ARCH_STEP = (
    "6. After the window the conduit updates its borrowers, by design (corrected 2026-10-15; this step\n",
    "6. A notch then checks the version it made active, still inside the window ({V}): when the Book is conjured\n"
    "   and that version was never compiled - no Phase-4 result and no Phase-5 root blueprint, the test the commit's\n"
    "   structural validator uses - `Spellbook._check_notched_version` runs its phases 1-4 there, while it is active\n"
    "   and so in the pool Phase 3 resolves against. A version that passes, or needs no check, is journaled to the\n"
    "   research record (`_record_research_promotion`), and the commit validator finds its Phase-4 result and skips\n"
    "   it. A version that fails is refused: `Spellbook._revert_refused_notch` runs the seam back toward the outgoing\n"
    "   version (change reason `mutation_rolled_back`), registers the lineage's dependencies and the outgoing\n"
    "   version's topology again, sets a refused version's own address back when it differs, and resets the refused\n"
    "   version's Phase 1-4 artifacts; `_notch_spell` then raises SpellbookValidationError whose first line says the\n"
    "   notch did not happen and names the version still active, the transaction ends as failed, and step 7 never\n"
    "   runs. Until {V} the check ran at the transaction's commit, after the switch, and nothing undid it.\n"
    "7. After the window the conduit updates its borrowers, by design (corrected 2026-10-15; this step\n",
)
ARCH_STEP_EVIDENCE = (
    "   - src/melder/aether/spellbook/spellbook.py:4087-4248\n",
    "   - `src/melder/aether/spellbook/spellbook.py:Spellbook._notch_spell`, `Spellbook._check_notched_version`,\n"
    "     `Spellbook._revert_refused_notch` (step 6)\n"
    "   - src/melder/aether/spellbook/spellbook.py:4087-4248\n",
)
ARCH_INVARIANT = (
    "## Operational Invariants\n",
    "## Operational Invariants\n"
    "- A notch either stands or leaves the structure as it was (2026-10-19, {V};\n"
    "  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers; the owner's answer, chat 2026-10-17: \"Yeah sure you\n"
    "  can refuse it and throw and move on if you mean it couldn't notch\", and his go, chat 2026-10-19: \"it should roll\n"
    "  back properly\"): `Spellbook._notch_spell`, inside the conduit's held window, reads the before-state under the\n"
    "  Book lock - the index's active version, its selected spell_id, the Book lookup and the frame claim of the\n"
    "  incoming version's key - then whether SpellSystemStates tracks the lineage, its direct dependencies and the\n"
    "  outgoing version's registered topology; runs the seam (`_apply_notch`); and checks the incoming version\n"
    "  (`_check_notched_version`: phases 1-4 when the Book is conjured and the version has neither a Phase-4 result\n"
    "  nor a Phase-5 root blueprint - the structural commit validator's own test - while it is active, so it is in\n"
    "  the pool Phase 3 resolves against). A version that passes, or needs no check, is journaled to the research\n"
    "  record and the notch stands; a notch to the active version is a no-op that journals nothing. A version that\n"
    "  fails is refused before the error leaves the window (`_revert_refused_notch`): the seam runs back toward the\n"
    "  outgoing version (change reason `mutation_rolled_back`), which is active, selected, claimed and routed by its\n"
    "  key again, registered with SpellSystemStates and the RiskManager and published to Nexus, the refused version\n"
    "  parked with its creation context cleaned; the lineage's dependencies (`update_dependencies`) and the outgoing\n"
    "  version's topology (`register_local_topology`) are registered again, since the check's Phase 3 wrote the\n"
    "  refused version's on the lineage; and a refused version keyed at another address has that key's lookup and\n"
    "  claim set back (`_restore_binding_key`). A key the two share is left as the promotion set it: setting it back\n"
    "  would release the restored version's claim wherever staging the refused one had dropped it\n"
    "  (STORY-2026-10-17-staged_version_releases_active_signature). On an index with no active version (one\n"
    "  `remove_from_spell_index` minted) `_revert_refused_activation` parks the refused version again, puts the\n"
    "  selection back, unregisters a lineage SpellSystemStates did not track (with the RiskManager entry the seam\n"
    "  added for it) and removes the Nexus record the seam published, and the key is set back. Last the refused\n"
    "  version's Phase 1-4 artifacts are reset, so a retry is checked, and refused, again. The error is\n"
    "  SpellbookValidationError with the refusal line as its preface (`_notch_refusal_line`), chained from the\n"
    "  check's; any other error from the check is re-raised as it is after the reversal; a reversal that fails\n"
    "  raises RuntimeError naming both versions (a Melder bug). Borrowers are untouched: the conduit's fan-out runs\n"
    "  only after a notch that returns, and a refusal ends the transaction as failed. Not restored, by design: the\n"
    "  restored version's creation context and its per-conduit verdicts - it is left `gated`, as after any notch,\n"
    "  so its next meld revalidates it (the owner's ask, chat 2026-10-19) - the marks the switch left on dependents\n"
    "  (mark only), the Crystallizer's twins (they take the switch, then its reversal) and the refused version's own\n"
    "  topology under its spell_id (nothing reads it while it is parked). Locks: the check and the reversal run on\n"
    "  the notch thread inside the window - the Book, the acting conduit and the conduits linked to it EXCLUSIVE,\n"
    "  their creation gates frozen - and take the locks a notch commit took; no lock or lock-order edge is added. A\n"
    "  notch that stands runs the same steps, its journal entry after the check.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._notch_spell`, `Spellbook._check_notched_version`,\n"
    "  `Spellbook._notch_refusal_line`, `Spellbook._revert_refused_notch`, `Spellbook._revert_refused_activation`,\n"
    "  `Spellbook._restore_binding_key`, `Spellbook._apply_notch`,\n"
    "  `src/melder/aether/conduit/conduit.py:Conduit.notch_spell` and\n"
    "  `src/melder/utilities/custom_exceptions/spellbook_validation_error.py:SpellbookValidationError._check_preface`.\n",
)
ARCH_FAILURE = (
    "## Failure Modes and Error Paths\n",
    "## Failure Modes and Error Paths\n"
    "- Fixed in {V}: a notch whose incoming version fails its structural check no longer leaves a half-made switch.\n"
    "  The check ran at the transaction's commit, after the seam had switched the index, and nothing undid it:\n"
    "  `notch_spell` raised SpellbookValidationError \"Spellbook validation failed. Broken spells: <name>.\" while the\n"
    "  lender's index selected the broken version, its borrowers kept the old one, the lender's meld by address\n"
    "  raised the same error and its meld of the old version's spell_id raised KeyError (probe N2; any failing check -\n"
    "  a self-dependency, an ambiguous provider). Now the first line reads \"notch_spell refused: '<name>' (spell_id\n"
    "  <id>) failed its structural check, so the notch did not happen; '<name>' (spell_id <id>) is still the active\n"
    "  version of the index.\" (\"...; the index still has no active version.\" for an index with none), the validation\n"
    "  report follows, and nothing has moved. `SpellbookValidationError` takes a keyword-only `preface=`, one line\n"
    "  placed before the report (without it the message is unchanged; a non-str, empty or multi-line preface raises\n"
    "  TypeError). A reversal that fails raises RuntimeError \"notch_spell refused '<name>' (spell_id <id>) but could\n"
    "  not put the index back to ...: <error>. ... This is a Melder bug; please report it with this message.\"\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._notch_spell`, `Spellbook._revert_refused_notch`\n"
    "  and `src/melder/utilities/custom_exceptions/spellbook_validation_error.py:SpellbookValidationError._check_preface`.\n",
)
ARCH_MAP_BOOK = (
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 7945\n"
    "  loc: 7945\n"
    "  verified_at: 2026-10-19T12:09:01Z\n"
    "  note: Spellbook core and conjure pipeline;",
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 8344\n"
    "  loc: 8344\n"
    "  verified_at: {now}\n"
    "  note: Spellbook core and conjure pipeline;",
)
ARCH_MAP_BOOK_NOTE = (
    "    between its decision and its disposal (0.2.8261).\n"
    "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`\n",
    "    between its decision and its disposal (0.2.8261). `_notch_spell` checks a version it makes active and, when\n"
    "    the check fails, puts the structure back before it raises (`_check_notched_version`, `_revert_refused_notch`);\n"
    "    `_apply_notch` no longer journals ({V}).\n"
    "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`\n",
)
ARCH_MAP_CONDUIT = (
    "- path: `src/melder/aether/conduit/conduit.py`\n"
    "  start_line: 1\n"
    "  end_line: 7892\n"
    "  loc: 7892\n"
    "  verified_at: 2026-10-19T12:09:01Z\n",
    "- path: `src/melder/aether/conduit/conduit.py`\n"
    "  start_line: 1\n"
    "  end_line: 7907\n"
    "  loc: 7907\n"
    "  verified_at: {now}\n",
)
ARCH_MAP_CONDUIT_NOTE = (
    "    member id (0.2.8261).\n"
    "- path: `src/melder/aether/conduit/conduit_pool.py`\n",
    "    member id (0.2.8261). `notch_spell`'s docstring and comments say a version that fails its structural check\n"
    "    is refused with nothing moved ({V}).\n"
    "- path: `src/melder/aether/conduit/conduit_pool.py`\n",
)
ARCH_MAP_CCM = (
    "  end_line: 1679\n"
    "  loc: 1679\n"
    "  verified_at: 2026-08-02T13:00:45Z\n"
    "  note: change control.\n",
    "  end_line: 1683\n"
    "  loc: 1683\n"
    "  verified_at: {now}\n"
    "  note: change control; the structural commit validator's docstring says a notched member reaches it checked\n"
    "    by the notch entry ({V}).\n",
)
ARCH_MAP_ERROR = (
    "  end_line: 493\n"
    "  loc: 493\n"
    "  verified_at: 2026-10-16T16:48:16Z\n"
    "  note: `SpellbookValidationError`; a gating Phase-4 warning (`GATING_WARNING_CODES`) is shown as a spell's\n"
    "    reason (0.2.8250).\n",
    "  end_line: 541\n"
    "  loc: 541\n"
    "  verified_at: {now}\n"
    "  note: `SpellbookValidationError`; a gating Phase-4 warning (`GATING_WARNING_CODES`) is shown as a spell's\n"
    "    reason (0.2.8250); the keyword-only `preface`, one line placed before the report ({V}).\n",
)
ARCH_HANDOFF = (
    "\n## Context / Handoff Summary\n\n",
    "\n## Context / Handoff Summary\n\n"
    "2026-10-19 a refused notch moves nothing ({V}; STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers,\n"
    "on the owner's answer \"refuse it and throw and move on\" and his go \"it should roll back properly\"): a notch\n"
    "checks a version it makes active inside the window and, when the check fails, puts the structure back before it\n"
    "raises, so the lender and its borrowers stay on the outgoing version; `SpellbookValidationError` takes a one-line\n"
    "`preface`. The boundary list, the summary, the SpellIndex Mutation Entry sequence (a new step 6), a new\n"
    "operational invariant, a fixed failure mode and the code map (four files remeasured) carry it; the component\n"
    "map carries the per-component contracts. Numeric citations into spellbook.py and conduit.py past the edits\n"
    "were remapped line by line; the one the remap widened to the whole new comment block cites its first three\n"
    "lines again (4022-4024).\n\n",
)

# ---- src_components ---------------------------------------------------------------------------------------------
COMP_CITE_1 = (
    "  - src/melder/aether/spellbook/spellbook.py:4022-4041 (states the Conduit admits it)\n",
    "  - src/melder/aether/spellbook/spellbook.py:4022-4024 (states the Conduit admits it)\n",
)
COMP_CITE_2 = (
    "  `src/melder/aether/spellbook/spellbook.py:4022-4041` states it correctly.\n",
    "  `src/melder/aether/spellbook/spellbook.py:4022-4024` states it correctly.\n",
)
COMP_INVARIANT = (
    "- Existing-object spells are registered into Creations on conjure/bind.\n",
    "- Existing-object spells are registered into Creations on conjure/bind.\n"
    "- A notch either stands or leaves the structure as it was ({V};\n"
    "  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers): `_notch_spell` reads the before-state under\n"
    "  `_lock`, runs `_apply_notch`, then `_check_notched_version` - phases 1-4 for a version a conjured Book never\n"
    "  compiled (no Phase-4 result, no Phase-5 root blueprint) - while the version is active. A pass journals the\n"
    "  promotion (`_record_research_promotion`, which `_apply_notch` no longer calls). A failure runs\n"
    "  `_revert_refused_notch` - `_apply_notch` back toward the outgoing version (`mutation_rolled_back`), the\n"
    "  lineage's dependencies and topology registered again, a refused version's own key set back\n"
    "  (`_restore_binding_key`), or `_revert_refused_activation` for an index with no active version - resets the\n"
    "  refused version's Phase 1-4 artifacts and raises SpellbookValidationError with the refusal line\n"
    "  (`_notch_refusal_line`) as its preface, chained from the check's. The restored version is left gated, so its\n"
    "  next meld revalidates it; the Conduit's fan-out never runs. A failing reversal raises RuntimeError naming\n"
    "  both versions. No lock or lock-order edge is added: the check and the reversal take the locks a notch\n"
    "  commit took, inside the notch window.\n"
    "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook._notch_spell`, `Spellbook._check_notched_version`,\n"
    "  `Spellbook._revert_refused_notch` and `Spellbook._revert_refused_activation`.\n",
)
COMP_BOOK_FAILURE = (
    "- `SpellbookValidationError` when Phase 1-4 produces broken spells.\n",
    "- `SpellbookValidationError` when Phase 1-4 produces broken spells.\n"
    "- `_notch_spell` raises SpellbookValidationError when the version it makes active fails its structural check,\n"
    "  with nothing moved ({V}): its first line is \"notch_spell refused: ... so the notch did not happen; ... is\n"
    "  still the active version of the index.\"; RuntimeError when the reversal fails (a Melder bug, both versions\n"
    "  named).\n",
)
COMP_CONDUIT_PARA = (
    "### Component: Conduit Runtime (Normal and Lesser)\n"
    "Purpose:\n"
    "- Execution scope for resolving spells and managing object lifecycles.\n\n",
    "### Component: Conduit Runtime (Normal and Lesser)\n"
    "Purpose:\n"
    "- Execution scope for resolving spells and managing object lifecycles.\n\n"
    "Refused notch (2026-10-19, {V}; failed_notch_refusal_2026_10_18): `notch_spell` changes only in its docstring\n"
    "and comments, which say a version that fails its structural check is refused with nothing moved. Inside the\n"
    "window `Spellbook._notch_spell` checks the version it made active and, when the check fails, puts the structure\n"
    "back and raises SpellbookValidationError; `notch_spell`'s `except` ends the transaction as failed and re-raises,\n"
    "so no commit delta lands and the fan-out to borrowers (`_deactivate_borrowed_spell`, `_activate_borrowed_spell`,\n"
    "`ConduitWard._emit_index_notch`) never runs.\n"
    "EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.notch_spell` and\n"
    "`src/melder/aether/spellbook/spellbook.py:Spellbook._notch_spell`.\n\n",
)
COMP_CONDUIT_FAILURE = (
    "  accepted, corrupting the indexes or leaving the index with no active version (`src_architecture`, Failure\n"
    "  Modes and Error Paths).\n",
    "  accepted, corrupting the indexes or leaving the index with no active version (`src_architecture`, Failure\n"
    "  Modes and Error Paths).\n"
    "- SpellbookValidationError from `notch_spell` when the version fails its structural check ({V}): its first\n"
    "  line says the notch did not happen and names the version still active, the report follows, and nothing has\n"
    "  moved - the transaction ended as failed and no borrower is touched. Until {V} the switch stayed made while\n"
    "  the borrowers kept the old version (`src_architecture`, Failure Modes and Error Paths).\n",
)
COMP_ERROR_CONTRACT = (
    "- `SpellbookValidationError(broken_spells, *, system_diagnostics=None)` renders once, at construction. First\n"
    "  line \"Spellbook validation failed. Broken spells: A, B.\" (names only; the two substrings of earlier releases\n"
    "  are kept for matchers). Then one block per spell with errors, \"Name (frame 'x'):\", each error as\n",
    "- `SpellbookValidationError(broken_spells, *, system_diagnostics=None, preface=None)` renders once, at\n"
    "  construction. First line \"Spellbook validation failed. Broken spells: A, B.\" (names only; the two substrings\n"
    "  of earlier releases are kept for matchers); with `preface` ({V}) one line comes before it - a non-empty str\n"
    "  with no line break, else TypeError before anything renders (`_check_preface`) - and a refused notch passes\n"
    "  one. Then one block per spell with errors, \"Name (frame 'x'):\", each error as\n",
)
COMP_SURFACE_BEHAVIOR = (
    "  checks the incoming one, so it must only ever be handed a parked member of the index it is notching.\n",
    "  checks the incoming one, so it must only ever be handed a parked member of the index it is notching.\n"
    "- A notch's check and reversal ({V}): after `_apply_notch`, still inside the window, `_notch_spell` runs\n"
    "  phases 1-4 for an incoming version never compiled (`_check_notched_version`) and, when they fail, runs the\n"
    "  seam back toward the outgoing version and restores what the check and the seam changed\n"
    "  (`_revert_refused_notch`) before it raises; the research journal entry moved from `_apply_notch` to\n"
    "  `_notch_spell`, written only once the notch stands. A notch either stands or leaves the index as it was\n"
    "  (`src_architecture`, Operational Invariants).\n",
)
COMP_SURFACE_KEYFILE = (
    "- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/"
    "notch_transaction_strategy.py`\n\n### Subcomponent: Parameter DI Shape Classification\n",
    "- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/"
    "notch_transaction_strategy.py`\n"
    "- `src/melder/utilities/custom_exceptions/spellbook_validation_error.py`\n"
    "\n### Subcomponent: Parameter DI Shape Classification\n",
)
COMP_FLOW = (
    "4. Inside the window: `Conduit._owned_notch_target` again, then `Spellbook._notch_spell` ->\n"
    "   `Spellbook._apply_notch` (park the outgoing version, `_reactivate_owned_spell` the incoming one, repoint the\n"
    "   index and the framewide lookup, re-register the index gated with its binding key, then\n"
    "   `SpellSystemStates.mark_dependents_for_revalidation` from the notched lineage, 0.2.8250). Any raise ->\n"
    "   `end_transaction(success=False)`\n"
    "   (`on_end` reopens the gates) and the raise propagates.\n",
    "4. Inside the window: `Conduit._owned_notch_target` again, then `Spellbook._notch_spell`: the before-state under\n"
    "   the Book lock (a notch to the active version returns here), then `Spellbook._apply_notch` (park the outgoing\n"
    "   version, `_reactivate_owned_spell` the incoming one, repoint the index and the framewide lookup, re-register\n"
    "   the index gated with its binding key, then `SpellSystemStates.mark_dependents_for_revalidation` from the\n"
    "   notched lineage, 0.2.8250), then `Spellbook._check_notched_version` (phases 1-4 for a version never compiled,\n"
    "   {V}): a pass -> `_record_research_promotion`; a failure -> `Spellbook._revert_refused_notch` and\n"
    "   SpellbookValidationError with the refusal line. Any raise -> `end_transaction(success=False)`\n"
    "   (`on_end` reopens the gates) and the raise propagates, so step 5 never runs.\n",
)
COMP_MAP_BOOK = (
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 7945\n"
    "  loc: 7945\n"
    "  verified_at: 2026-10-19T12:09:01Z\n"
    "- path: `src/melder/aether/spellbook/spellbinder.py`\n",
    "- path: `src/melder/aether/spellbook/spellbook.py`\n"
    "  start_line: 1\n"
    "  end_line: 8344\n"
    "  loc: 8344\n"
    "  verified_at: {now}\n"
    "- path: `src/melder/aether/spellbook/spellbinder.py`\n",
)
COMP_MAP_CONDUIT = (
    "- path: `src/melder/aether/conduit/conduit.py`\n"
    "  start_line: 1\n"
    "  end_line: 7892\n"
    "  loc: 7892\n"
    "  verified_at: 2026-10-19T12:09:01Z\n",
    "- path: `src/melder/aether/conduit/conduit.py`\n"
    "  start_line: 1\n"
    "  end_line: 7907\n"
    "  loc: 7907\n"
    "  verified_at: {now}\n",
)
COMP_MAP_CCM = (
    "- path: `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`\n"
    "  start_line: 1\n"
    "  end_line: 1679\n"
    "  loc: 1679\n"
    "  verified_at: 2026-08-02T13:00:45Z\n",
    "- path: `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`\n"
    "  start_line: 1\n"
    "  end_line: 1683\n"
    "  loc: 1683\n"
    "  verified_at: {now}\n",
)
COMP_MAP_ERROR = (
    "  end_line: 493\n"
    "  loc: 493\n"
    "  verified_at: 2026-10-16T16:51:53Z\n"
    "  note: `SpellbookValidationError`: names the spells conjure cannot build (SpellCompiler); a gating Phase-4\n"
    "    warning is a spell's reason (0.2.8250).\n",
    "  end_line: 541\n"
    "  loc: 541\n"
    "  verified_at: {now}\n"
    "  note: `SpellbookValidationError`: names the spells conjure cannot build (SpellCompiler); a gating Phase-4\n"
    "    warning is a spell's reason (0.2.8250); a one-line `preface` goes before the report ({V}).\n",
)
COMP_HANDOFF = (
    "\n## Context / Handoff Summary\n\n",
    "\n## Context / Handoff Summary\n\n"
    "2026-10-19 a refused notch moves nothing ({V}; STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers):\n"
    "Spellbook Core gains an invariant (`_notch_spell` checks the version it makes active and, when the check fails,\n"
    "puts the structure back before it raises) and a failure; the Conduit Runtime gains a paragraph and a failure for\n"
    "the refusal; the SpellbookValidationError contract names the `preface`; the SpellIndex Mutation Surface gains a\n"
    "behavior bullet and the error file as a key file; the notch flow's step 4 follows the check and the reversal;\n"
    "the code map remeasures spellbook.py, conduit.py, change_control_manager.py and spellbook_validation_error.py.\n"
    "Numeric citations into spellbook.py and conduit.py past the edits were remapped line by line; the two the remap\n"
    "widened to the whole new comment block cite its first three lines again (4022-4024).\n\n",
)

# ---- tests_components -------------------------------------------------------------------------------------------
TC_UPDATED = ("- Updated: 2026-10-19T12:09:01Z\n", "- Updated: {now}\n")
TC_UTIL_PROTECTS = (
    "  `GATING_WARNING_CODES` is exactly `SPELL_CONTRACT_MISSING_PROVIDER`\n"
    "Key Files (C1):\n"
    "- `tests/unit/melder/utilities/synchronization/test_creation_gate.py`\n",
    "  `GATING_WARNING_CODES` is exactly `SPELL_CONTRACT_MISSING_PROVIDER`\n"
    "- the notch refusal's preface ({V}; `test_spellbook_validation_error_preface.py`, 11 tests): without a preface\n"
    "  the message is unchanged; with one it is the first line and the report follows byte for byte, also for an\n"
    "  error with no broken spells; a non-str, an empty or a multi-line preface (a newline, CRLF, a trailing break,\n"
    "  U+2028) raises TypeError naming what it got\n"
    "Key Files (C1):\n"
    "- `tests/unit/melder/utilities/synchronization/test_creation_gate.py`\n",
)
TC_UTIL_KEYFILE = (
    "- `tests/unit/melder/utilities/custom_exceptions/test_managed_spell_exhausted_error.py` (2026-10-15)\n",
    "- `tests/unit/melder/utilities/custom_exceptions/test_managed_spell_exhausted_error.py` (2026-10-15)\n"
    "- `tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error_preface.py` (2026-10-19)\n",
)
TC_INTEG_PROTECTS = (
    "  version while it is still live; and a refused cleanup of the active English changes no contract\n"
    "Key Files (C1):\n",
    "  version while it is still live; and a refused cleanup of the active English changes no contract\n"
    "- a notch refused at its commit check moves nothing ({V}; `test_notch_refused_at_commit_integration.py`,\n"
    "  14 tests): in a dynamic world with English active on a lender's index, a staged version broken by a\n"
    "  self-dependency (SelfMade) or by an ambiguous provider (TimedGreeter, two Clocks) is refused - the error's\n"
    "  first line says the notch did not happen and names English, the report and the cause follow - and the index,\n"
    "  the active and parked maps, the frame claim and the Book lookup stay on English, which melds by address and by\n"
    "  spell_id; a retry is refused again; a version staged at another address leaves that address unclaimed; an\n"
    "  index-linked borrower keeps its copies and its consumer melds English; a notch back is a no-op and a sound\n"
    "  notch after a refusal moves lender and borrower; the Nexus record stays on English; a minted index refused\n"
    "  stays parked, untracked, unpublished and unclaimed; the Book flag falls after one meld of English; and with\n"
    "  MutationResearch active a refused notch journals nothing while a standing one journals one promotion\n"
    "Key Files (C1):\n",
)
TC_INTEG_KEYFILE = (
    "- `tests/integration/melder/aether/conduit/test_cleanup_releases_contracts_integration.py` (2026-10-19)\n",
    "- `tests/integration/melder/aether/conduit/test_cleanup_releases_contracts_integration.py` (2026-10-19)\n"
    "- `tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py` (2026-10-19)\n",
)
TC_MAP_UNIT = (
    "  note: the exhaustion error's texts and type (0.2.8243).\n",
    "  note: the exhaustion error's texts and type (0.2.8243).\n"
    "- path: `tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error_preface.py`\n"
    "  start_line: 1\n"
    "  end_line: 97\n"
    "  loc: 97\n"
    "  verified_at: {now}\n"
    "  note: SpellbookValidationError's one-line preface and its refusals ({V}).\n",
)
TC_MAP_INTEG = (
    "    version grants, from every door - and a refused cleanup changes none (0.2.8261).\n",
    "    version grants, from every door - and a refused cleanup changes none (0.2.8261).\n"
    "- path: `tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py`\n"
    "  start_line: 1\n"
    "  end_line: 601\n"
    "  loc: 601\n"
    "  verified_at: {now}\n"
    "  note: a notch whose incoming version fails its structural check is refused with nothing moved - lender,\n"
    "    borrower, address claims, Nexus and the research journal ({V}).\n",
)
TC_SOURCES = (
    "- `tests/component/melder/spellbook/test_spellbook_component_dispose_spell_releases_contracts_first.py`\n"
    "- direct filesystem inventory of `tests/`\n",
    "- `tests/component/melder/spellbook/test_spellbook_component_dispose_spell_releases_contracts_first.py`\n"
    "- `tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py`\n"
    "- `tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error_preface.py`\n"
    "- direct filesystem inventory of `tests/`\n",
)
TC_COUNT_AETHER = (
    "- The aether tree carries 49 `test_*.py` modules beneath these; they are the\n",
    "- The aether tree carries 50 `test_*.py` modules beneath these; they are the\n",
)
TC_COUNT_CORE = ("above - 276 paths (recounted 2026-10-19) - and nothing else.",
                 "above - 278 paths (recounted 2026-10-19) - and nothing else.")
TC_HANDOFF = (
    "\n## Context / Handoff Summary\n\n",
    "\n## Context / Handoff Summary\n\n"
    "2026-10-19 a refused notch moves nothing ({V}; STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers):\n"
    "the Spellbook Integration Cluster gains `test_notch_refused_at_commit_integration.py` (14 tests: a\n"
    "self-dependent and an ambiguous-provider version refused with nothing moved - lender, borrower, address claims,\n"
    "Nexus, the research journal - a retry, a notch back, a sound notch after, a minted index, the Book flag) and the\n"
    "Utilities Unit Cluster `test_spellbook_validation_error_preface.py` (11 tests: the preface's place and its\n"
    "refusals), each a key file with a code-map record. Both modules were on disk and counted before (unit 514 of\n"
    "517, integration 178 of 185; 860 test modules in the three tiers); the aether integration tree's count is\n"
    "recounted from disk (50; it read 49). The core key-file union is 278 paths.\n\n",
)

# ---- tests_architecture -----------------------------------------------------------------------------------------
TA_HANDOFF = (
    "\n## Context / Handoff Summary\n\n",
    "\n## Context / Handoff Summary\n\n"
    "2026-10-19 a refused notch moves nothing ({V}): the inventory is unchanged (unit 517 `.py`, 514 of them\n"
    "`test_*.py`; integration 185, 178; 860 test modules in the three tiers) - the lane's two modules, the refused\n"
    "notch's integration module and the validation error's preface unit module, were on disk and counted before this\n"
    "landing and are catalogued in `tests_components` now. No tier, conftest, declared marker or shared support\n"
    "module changes, and no extent in this map moves.\n\n",
)

EDITS = {
    ARCH: [ARCH_CITE, ARCH_BOUNDARY, ARCH_SUMMARY, ARCH_STEP, ARCH_STEP_EVIDENCE, ARCH_INVARIANT, ARCH_FAILURE,
           ARCH_MAP_BOOK, ARCH_MAP_BOOK_NOTE, ARCH_MAP_CONDUIT, ARCH_MAP_CONDUIT_NOTE, ARCH_MAP_CCM, ARCH_MAP_ERROR,
           ARCH_HANDOFF],
    COMP: [COMP_CITE_1, COMP_CITE_2, COMP_INVARIANT, COMP_BOOK_FAILURE, COMP_CONDUIT_PARA, COMP_CONDUIT_FAILURE,
           COMP_ERROR_CONTRACT, COMP_SURFACE_BEHAVIOR, COMP_SURFACE_KEYFILE, COMP_FLOW, COMP_MAP_BOOK, COMP_MAP_CONDUIT,
           COMP_MAP_CCM, COMP_MAP_ERROR, COMP_HANDOFF],
    TCOMP: [TC_UPDATED, TC_UTIL_PROTECTS, TC_UTIL_KEYFILE, TC_INTEG_PROTECTS, TC_INTEG_KEYFILE, TC_MAP_UNIT,
            TC_MAP_INTEG, TC_SOURCES, TC_COUNT_AETHER, TC_COUNT_CORE, TC_HANDOFF],
    TARCH: [TA_HANDOFF],
}
EXTENTS = {
    "src/melder/aether/spellbook/spellbook.py": 8344,
    "src/melder/aether/conduit/conduit.py": 7907,
    "src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py": 1683,
    "src/melder/utilities/custom_exceptions/spellbook_validation_error.py": 541,
    "tests/integration/melder/aether/conduit/test_notch_refused_at_commit_integration.py": 601,
    "tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error_preface.py": 97,
}


def check_lines(old: str, new: str, label: str) -> None:
    """Refuse a new line over 120 characters that the edit adds (lines the old text already had are kept)."""
    kept = set(old.split("\n"))
    for line in new.split("\n"):
        if line in kept:
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and " " not in stripped[2:]:
            continue
        if len(line) > 120:
            raise SystemExit("%s: new line over 120 chars (%d): %s" % (label, len(line), line))


def key_file_union(text: str) -> int:
    """Count the deduplicated union of every `Key Files (C1)` list, as the tests document defines its core."""
    lines = text.split("\n")
    paths = set()
    index = 0
    while index < len(lines):
        if lines[index].startswith("Key Files (C1):"):
            cursor = index + 1
            while cursor < len(lines) and (lines[cursor].startswith("- ") or lines[cursor].startswith("  ")):
                match = re.match(r"- `([^`]+)`", lines[cursor])
                if match:
                    paths.add(match.group(1))
                cursor += 1
            index = cursor
        else:
            index += 1
    return len(paths)


def main() -> None:
    """Apply every edit in memory, report, and write only with --apply."""
    args = sys.argv[1:]
    if len(args) != 5 or args[0] != "--root" or args[2] != "--version" or args[4] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    root = pathlib.Path(args[1])
    version = args[3]
    live = re.search(r'__version__\s*=\s*"([^"]+)"', (root / VERSION_FILE).read_text(encoding="utf-8")).group(1)
    major, minor, notch = version.split(".")
    before = "%s.%s.%d" % (major, minor, int(notch) - 1)
    if live not in (before, version):
        raise SystemExit("__version__ is %s; the docs name %s (expected %s or %s)" % (live, version, before, version))
    for rel, lines in EXTENTS.items():
        measured = len((root / rel).read_bytes().decode("utf-8").splitlines())
        if measured != lines:
            raise SystemExit("%s measures %d lines, the docs say %d" % (rel, measured, lines))
    now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = {}
    for rel, edits in EDITS.items():
        path = root / rel
        raw = path.read_bytes()
        if b"\r\n" in raw:
            raise SystemExit("CRLF in %s" % rel)
        text = raw.decode("utf-8")
        count_before = text.count("\n")
        for number, (old, new) in enumerate(edits, 1):
            new = new.replace("{now}", now).replace("{V}", version)
            check_lines(old, new, "%s edit %d" % (path.name, number))
            if text.count(old) != 1:
                raise SystemExit("%s edit %d: old text found %d times" % (path.name, number, text.count(old)))
            text = text.replace(old, new)
        if "4022-4041" in text:
            raise SystemExit("%s still cites 4022-4041" % path.name)
        results[rel] = text
        print("%s: %d edits, %d -> %d lines" % (path.name, len(edits), count_before, text.count("\n")))
    union = key_file_union(results[TCOMP])
    if union != 278:
        raise SystemExit("the core key-file union counts %d, the document says 278" % union)
    print("tests_components core key-file union:", union, "| version", live, "-> docs name", version)
    if args[4] == "--apply":
        for rel, text in results.items():
            path = root / rel
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % rel)
        print("applied", now)


main()
