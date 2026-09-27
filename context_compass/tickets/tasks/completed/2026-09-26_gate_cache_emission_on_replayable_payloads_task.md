# Task: Refuse creation-cache emission for spells whose rows cannot replay their contract payload

- Completed: 2026-09-26T13:14:31Z
- Summary: Option-B emission gate implemented, then retired the same day by task 5 (rows carry value-only refs,
  so every plan packages); the scalar classifier survives on the leaf. Closed with the story as the decision
  record; owner accepted 2026-09-26T13:14:31Z.

## Metadata
- Task ID: TASK-2026-09-26-gate-cache-emission-on-replayable-payloads
- Story: STORY-2026-09-26-signature-determinism-phase8-digest
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T10:19:43Z
- Updated: 2026-09-26T13:14:31Z

## Objective
Owner option B (2026-09-26): a spell whose phase-11 step rows carry a contract payload value that the
cache path cannot replay faithfully (anything but `None`/`bool`/`int`/`float`/`str` and tuples of those)
is never emitted into the conduit creation cache. Such spells always recompile phases 8-11 in-process
(correct values); the cross-process hit is lost only for them. No row-format change, no `.melc`
generation bump.

## Ticket Contract
- ENTRY_GATE: Owner ruling B recorded on the story and epic; the patch docs carry the emission-gate
  delta; the story boundary is extended to the emission seam; the active board row routes here.
- EXECUTION_BOUNDARY: `codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py`
  (two new pure static helpers: value predicate, plan predicate),
  `codegen_creation_system/shared_assets/manifest_creation_cache.py` (`build_package` returns `None`
  when the plan is not replayable), `codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py`
  (`build_package`, same rule), `spellbook.py` (`_emit_spell_cache`: a `None` payload stages nothing
  and returns False; one hunk), tests. No row builder, manifest schema, hydration or `caching_system.py`
  change.
- DEPENDENCIES: task 2 (the freeze rule that makes the marker deterministic); the emission entry
  `SpellbookCreationSystem._stage_spell_payloads_at_conjure_end` (unchanged; it calls
  `_emit_spell_cache` per missing spell).
- EXIT_GATE: both `build_package`s refuse non-replayable plans; `_emit_spell_cache` handles the refusal;
  unit tests for the predicate and both gates; a component test that a real object-payload plan is
  refused and a string-payload plan is packaged; "Not run." until the owner reports; status review.
- FAILURE_ESCALATION: CONFLICT if `spellbook.py` is under concurrent edit at patch time (melder_0's lane
  touched it today); RISK if any family builds its rows from a source other than `plan.steps`.

## Scope Boundaries
- In scope: the replayability predicate, the two package builders, the emission call site, tests.
- Out of scope: making the rows lossless (a replay format is the structural snapshot's problem);
  `SpellMap` overrides (phase 3, not contract payloads); the cache classification; hydration code.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner chose option B and said "send it" (2026-09-26); the files and symbols were
  named in the decision request.
- from_state: in_progress
- to_state: review
- transition_reason: G1-G5 complete on the extended boundary; nothing executed here ("Not run.").
- from_state: review
- to_state: done
- transition_reason: Owner accepted tasks 1-5 and the story after the third owner-run green suite report
  ("yeah sure looks good", 2026-09-26T13:14:31Z); canonical docs promoted, patch folder archived, boards synced.

## Steps / Checklist
- [x] G1: patch-doc delta (component + architecture) and story boundary extension.
- [x] G2: `CodegenCreationSchemaHelpers.is_replayable_contract_payload_value` and
      `plan_contract_payloads_are_replayable` (pure, slot-only static helpers).
- [x] G3: both `build_package`s return `None` for a non-replayable plan; `_emit_spell_cache` stages
      nothing, logs once at info level and returns False.
- [x] G4: tests - unit (predicate matrix; both gates with a probe artifact; `_emit_spell_cache` on a
      refused payload) and component (real contract-payload plan refused; string payload packaged).
- [x] G5: docstring ritual; notes; task -> review with "Not run." and the exact commands.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The gate in both package builders and the call site; tests; patch-doc delta.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/manifest_creation_cache.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py
- src/melder/aether/spellbook/spellbook.py (`_emit_spell_cache` only)
- tests/unit/melder/spellbook/spell_compiler/shared_assets/test_contract_payload_replayability.py (new)
- tests/component/melder/spellbook/test_codegen_signature_determinism.py (one gate test added)
- tests/component/melder/spellbook/test_spellbook_component_caching_system.py (one refusal test added)
- artifacts/codegen_signature_determinism_20260926/scaling_conjure_probe.py (M7, owner-run, task 3)

## Validation
- Not run. (VM interpreter is 3.10 against a 3.14 floor.)
- Recommended commands (owner-run, 3.14t):
  - `python -m pytest -q tests/unit/melder/spellbook/spell_compiler/shared_assets`
  - `python -m pytest -q tests/component/melder/spellbook/test_codegen_signature_determinism.py tests/component/melder/spellbook/test_spellbook_component_caching_system.py`
  - `python -m pytest -q tests/component/melder/aether/conduit/test_conduit_component_unresolved_inputs.py tests/component/melder/aether/conduit/test_conduit_component_non_resolvable_overrides.py`

## Risks / Rollback Notes
- Rollback: delete the two helpers, restore both `build_package` bodies and the call-site hunk.
- Books whose rows carry a non-replayable payload lose the cross-process full hit (they were hitting
  with wrong values before); the classification turns `mixed` for them, which is the honest state.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No edit under `src/` before the owner confirms the file/symbol proposal.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed) - patch docs carry Interface delta 4 / Invariant 5
- [x] Validation status recorded ("Not run.")
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_signature_determinism_2026_09_26/
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: creation cache emission; contract payload replay; phase-11 rows.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T10:19:43Z
  TYPE: FACT
  CLAIM: Emission seam, read from source. Conjure end stages every constructed spell through
    `SpellbookCreationSystem._stage_spell_payloads_at_conjure_end` -> `Spellbook._emit_spell_cache`
    (:949-1019), which dedupes on `caching_system.has_spell_payload`, then calls
    `manifest_creation_cache.build_package` when the creation carries `MANIFEST_METADATA_KEY`, else
    `spell_codegen_creation_cache.build_package`; the payload goes to `upsert_spell_payload` and the
    bundle is written at conjure end. Both builders run with `artifact._spell_codegen_plan` live (the
    legacy one raises without it), so the raw `step.contract_payload` values of both lanes are readable
    at emission time - the rows only carry the frozen projections, which cannot be told apart from
    legitimate tuple values, so the verdict must come from the plan, not the rows. Contract payloads
    only enter a conjure-time plan when a contracted provider already exists (`upgrade_to_normal` and
    restore flows); ordinary link/validate/meld flows compile them after conjure and the dedupe keeps
    the conjure-time package, so the exposure is narrower than the row shape suggests, but not zero.
    Replayable = `None`/`bool`/`int`/`float`/`str`, or a `tuple` of replayable values: exactly the set
    `freeze_phase11_schema_value` returns unchanged and `_hydrate_steps_from_rows` passes through.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:949-1019
  - src/melder/aether/spellbook/spellbook_creation_system.py:1152-1193
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/manifest_creation_cache.py:37-68
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:99-135
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:309-395
  - src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py:181-273
  IMPACT: The gate is four small hunks behind one predicate; no persisted format moves.
  NEXT: G1 patch-doc delta and story boundary extension, then G2/G3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:28:51Z
  TYPE: FACT
  CLAIM: G1-G5 landed on the working tree (not run). Helpers on `CodegenCreationSchemaHelpers`:
    `is_replayable_contract_payload_value` :99-141 (None; EXACT bool/int/float/str; exact tuples of
    replayable items - subclasses such as IntEnum members are refused because freeze passes them
    through but marshal cannot persist them), `plan_contract_payloads_are_replayable` :143-172,
    `spell_codegen_plan_is_replayable` :174-202 (None plan -> False; both lanes; a None lane is
    ignored). Gates: `manifest_creation_cache.build_package` :44-90 and
    `spell_codegen_creation_cache.build_package` :101-146 return `Optional[Dict]` (None after the
    phase-11 presence checks, before any subpackage build). Call site `Spellbook._emit_spell_cache`
    :949-1040: `None` -> one info log, return False, nothing staged. `git diff -w --stat`: four src
    files, 164 insertions, 7 deletions. Tests: unit
    `tests/unit/melder/spellbook/spell_compiler/shared_assets/test_contract_payload_replayability.py`
    (267 lines: 11 accepted values that are freeze fixed points, 15 refused values, plan and both-lane
    verdicts, manifest envelope built/refused/still-raising, legacy builder refused before any
    subpackage build and built for a replayable plan); component
    `test_codegen_signature_determinism.py` :526-556 (object-payload consumer refused, string-payload
    sibling packaged, on the real linked plan) and `test_spellbook_component_caching_system.py`
    :604-655 (refused package stages nothing at conjure end: no payload, no bundle, `emit_cache()`
    False). The only producer of `step.contract_payload` is the injection processor
    (`spell_injection_processor_strategy.py:297`), so books without SpellContract payloads cache as
    before. M7 scaling probe written for task 3 under the artifact directory.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:99-202
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/manifest_creation_cache.py:44-90
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:101-146
  - src/melder/aether/spellbook/spellbook.py:949-1040
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:297-297
  - tests/unit/melder/spellbook/spell_compiler/shared_assets/test_contract_payload_replayability.py:1-267
  - tests/component/melder/spellbook/test_codegen_signature_determinism.py:271-556
  - tests/component/melder/spellbook/test_spellbook_component_caching_system.py:604-655
  - artifacts/codegen_signature_determinism_20260926/scaling_conjure_probe.py:1-197
  IMPACT: No persisted format moves; spells with a non-replayable payload are simply absent from the
    bundle and recompile per process. `spellbook.py` received one hunk in a file melder_0 also edited
    today (their lane is paused); NOTICE sent.
  NEXT: Task -> review; owner runs the three command lines under Validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:42:09Z
  TYPE: DECISION_REQUEST
  CLAIM: The gate's premise needs a correction, found by the owner's suite run: the generalized family
    (and every manifest-first family) hydrates its executors from the manifest rows IN-PROCESS - the
    lazy doors run "the exact same assembly program the cache-load path runs" - so the frozen payload
    projection reaches the constructor on the hot path too; only the legacy plan compiler binds raw
    values. The gate (unchanged, still correct as cache policy) keeps lossy plans out of the bundle,
    but a SpellContract override whose value is a dict, list, enum, callable or object is constructed
    from its frozen projection in-process today (before task 2: `repr` text). Docstrings in the five
    touched files now say so. Owner options for the in-process seam: (1) fail fast at phase 9/11 with
    a `MeldExecutionError` naming consumer, parameter and value type when a contract payload value is
    not replayable (small; breaks books that "worked" with corrupted values); (2) carry the raw payload
    values beside the marshal-safe manifest (a live side table keyed by step index, used by in-process
    hydration; cache loads keep the row values and the emission gate keeps non-replayable plans out of
    the bundle) - restores object payloads in-process; touches the generalized/solo/many_only hydrators
    and manifest builders, which sit in the override lanes' files (NOTICE to updater_1/melder_0 first).
    Recommended: (2), because `SpellContract.spell_override` documents arbitrary values.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_lazy_door_step.py:15-130
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:974-1037
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:163-268
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:120-196
  - tests/component/melder/spellbook/test_codegen_signature_determinism.py:271-365
  IMPACT: Task 4 stays in review as the cache half of the fix; the in-process half is a new task once
    the owner picks (1) or (2).
  NEXT: Owner picks (1) or (2); fable_0 opens the task, sends the NOTICEs and proposes files/symbols.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T10:44:38Z
  TYPE: FACT
  CLAIM: Mailbox M1-11 (melder_1, owner-directed) consumed: melder_1 is (1) stabilizing function/method/
    lambda/partial and default-repr instance SPELL IDS (`Bind.sha256_profile` hashes address-bearing
    `repr` text) and (2) fixing a conjure-cache defect where a mixed conjure stages only the missing
    payload while a consumer keeps a manifest referencing a provider's old id - files `bind.py`,
    `spellbook_creation_system.py` (`_stage_spell_payloads_at_conjure_end` re-stages all live spells and
    drops non-live payloads) and `caching_system.py` (generation 12). None of those files or the
    generation is in this lane; the re-stage calls `_emit_spell_cache` unchanged, and a spell the gate
    refuses returns False there, so after their drop-then-restage a lossy plan is absent from the
    bundle - the two changes compose. Their (1) is the bind-side twin of task 2's freeze rule (address
    text out of identities vs out of signatures). ACK sent (F0-4).
  EVIDENCE:
  - tickets/tasks/2026-09-26_stabilize_function_spell_ids_across_processes_task.md
  - src/melder/aether/spellbook/spellbook.py:949-1040
  IMPACT: No file collision; no generation change on my side; task 4's gate remains valid under
    melder_1's re-stage semantics.
  NEXT: Owner picks (1)/(2) for the in-process projection; nothing to rebase.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T10:56:37Z
  TYPE: CONFLICT
  CLAIM: Owner chose option (2) (raw-value side table for in-process hydration). Reading the seam
    before editing shows it is larger than proposed and sits inside the live override lanes: the
    no-overrides lane binds payload values through the namespace (`step_contract_values`,
    `_build_step_bindings` :974-1037, also the specializer `build_specialized_no_overrides_executor`
    :1377), so a live table would fit there; but the OVERRIDES lane embeds the frozen payload items as
    SOURCE LITERALS - `kwargs_N = {dict(contract_payload_items)!r}` in
    `generalized_overrides_codegen_creation_compiler.py` :1385-1398, emitted through
    `emit_overrides_codegen_creation_executor_shape_source` :236 and memoized process-wide by plan
    signature in `generalized_manifest_overrides_runtime.py` :527-568 - so raw objects cannot ride that
    lane without changing the emitter's binding shape. The `many_only` family hydrates payloads from
    rows the same way (`many_only_no_overrides_codegen_creation_compiler.py` :479-483). Those emitters
    are the files updater_0/updater_1 have review-stage proposals on and melder_0's override design
    targets. A no-overrides-only (2) would leave the two lanes constructing the same spell with
    different values, which is worse than today.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1348-1398
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_overrides_runtime.py:527-568
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:974-1037
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:163-410
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_runtime_rows.py:187-264
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:454-500
  IMPACT: (2) as a coherent change = both lanes of both families plus the manifest/lazy-door plumbing,
    i.e. the override emitters mid-flight. Compliant paths: (1) fail fast at phase 9 now - in
    `_normalize_contract_override_payload`, raise `MeldExecutionError` naming consumer, parameter and
    value type for any value that is not a freeze fixed point; breaks nothing that works today, since
    every such value is already corrupted; one file in the compiler phases, no lane collision; then
    (2) becomes a requirement filed into melder_0's override design (emitter binds payload values via
    the namespace instead of literals) and the fail-fast is lifted when it lands. Or (2) now across
    the emitters, with NOTICEs to updater_0/updater_1/melder_0 and their rebases.
  NEXT: Owner picks; recommended (1) now + (2) as an override-design requirement. No edit until then.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:00:07Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner pushed back on "fail fast": the compiler was just changed so that spells absent from the
    design are conjure WARNINGS (`validation_warnings`), not failures. Scope restated for the owner: this
    item is not about missing spells or unresolved inputs at all - it is about the VALUES inside a
    `SpellContract(spell_override={...})` payload that are not plain scalars (objects, dicts, lists,
    enums, callables); manifest-first execution mangles them before the constructor sees them (silent
    today). The non-fatal option consistent with the new mode: a Phase-4 validation WARNING
    (`ContractProviderPresenceStrategy` already walks every SpellContract default; add issue code
    `SPELL_CONTRACT_OVERRIDE_VALUE_NOT_REPLAYABLE`, severity warning, surfaced by
    `conjure(validation_warnings=True)`), the task-4 gate keeps such plans out of the cache, and the
    real fix (emitters bind payload values instead of literalizing them) is filed into the override
    design. The predicate moves to the leaf (`CodegenSignature.is_freeze_fixed_point`) so phase 4 can
    import it without touching the phase-11 subsystem (only `compiler_phase_11.py` imports it today).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:72-235
  - src/melder/aether/spellbook/spellbook_creation_system.py:300-340
  IMPACT: No raise anywhere; nothing that conjures today stops conjuring; users learn about mangled
    override values through the same channel as missing providers.
  NEXT: Owner confirms the warning route (W) or leave-as-is (L); fable_0 implements W in the validation
    lane if confirmed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T11:26:15Z
  TYPE: DECISION
  CLAIM: Owner direction (2026-09-26, chat): `SpellContract.spell_override` values are NOT restricted to
    literals - "assume it could be anything and run with it"; deviating from the normal overrides path
    "is a different problem", so contract override values ride the same path as meld overrides; rename
    `spell_override` -> `override` "while we're at it"; check whether `SpellMap` overrides are similar.
    The in-process side table (option 2) and the Phase-4 warning route (W) are superseded: the plan must
    stop carrying override values in rows or generated source and resolve them live at meld. Reading
    expansion recorded and owner-directed (read-only here): the meld overrides branch in `meld.py` and
    `creation_context.py`, the overrides-lane emitter and runtime, `spell_map.py`, `spell_contract.py`,
    melder_0's design v2 and melder_1's spell-id task. No src edit before a task-5 Propose -> Confirm and
    NOTICEs to the lane owners (updater_0, updater_1, melder_0, melder_1).
  EVIDENCE:
  - tickets/tasks/2026-09-26_gate_cache_emission_on_replayable_payloads_task.md
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:120-196
  IMPACT: Task 4's gate stays as the cache half (still correct); the in-process half becomes task 5 under
    a live-resolution design aligned with the override lanes, not an emitter patch in this lane.
  NEXT: Read `spell_contract.py` and `spell_map.py` whole, then the meld overrides path by function.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:35:29Z
  TYPE: FACT
  CLAIM: Task-5 investigation, read from source. (1) `SpellContract` and `SpellMap` carry the same
    `spell_override` slot (dict = kwargs, list/tuple = positional, values uninterpreted); the ONLY
    compiler of the payload is the phase-9 contract processor, which iterates the consumer's live
    SpellContract defaults (phase-1 `default_value`, else `inspect.signature(..., FORWARDREF)`),
    normalizes each payload and records it against the PROVIDER's child occurrence; a shared provider
    must see one distinct payload or `MeldExecutionError` is raised. `SpellMap.spell_override` is read
    only by phase 3, to refuse it on a non-resolvable definition; it is never applied (dead today).
    (2) The injection processor turns payload keys into `param_sources[kind="contract"]` of the
    provider's instance spec (a key on a dependency parameter keeps the dependency and gains
    `contract_key`); precedence override > contract payload > dependency; `__args__` is positional.
    (3) The meld path: `Conduit.meld(override=...)` -> `ConduitMeld.meld(spell_override=...)`;
    `_normalize_spell_override` (dict, or `{"__args__": [...]}`); a caller payload REPLACES
    `Spell._mutation_override` (persistent per-spell default, same map shape); `override_map is None`
    selects the no-overrides instance executor, otherwise `_overrides_executor(self, override_map)`;
    `SpellOverrider.apply` maps keys (PATH `a>b>c` > UNIQUE `*p` > BROADCAST `**p`) to sockets over the
    root blueprint's DAG index; values are arbitrary and never inspected. (4) melder_0's design v2
    (in review) keeps "override > contract payload value > dependency", treats a contract payload
    value as a supplied operand that cuts what it replaces, reads supplied operands as literal
    `ov["key"]` lookups, and retires the override emitters and targeting runtime in S3; its U1 asks
    how the normal lowering orders a contract payload against a dependency. (5) `bind.py` on the
    device tree hashes `init_signature` address-free (`strip_memory_addresses`), so the object-payload
    spell id is now process-stable and the strict xfail in the determinism test will XPASS.
  EVIDENCE:
  - src/melder/aether/conduit/meld/contracts/spell_contract.py:120-196
  - src/melder/aether/conduit/meld/contracts/spell_map.py:122-195
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:126-260
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_injection_processor_strategy.py:174-360
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:900-912
  - src/melder/aether/conduit/conduit.py:4521-4566
  - src/melder/aether/conduit/meld/conduit_meld.py:471-536
  - src/melder/aether/conduit/meld/meld.py:1506-1575
  - src/melder/aether/conduit/meld/overrides/spell_overrider.py:159-217
  - src/melder/aether/spellbook/spell_compiler/dag/target_spec.py:60-129
  - src/melder/aether/spellbook/bind/bind.py:892-1044
  - artifacts/melder_override_design_20260926/design_v2.md:1-459
  IMPACT: The "normal overrides path" is the supplied-operand path: the design for task 5 is to make a
    contract payload value a LIVE supplied operand (read from the consumer's descriptor at meld) instead
    of a compile-time constant, which fits v2 unchanged; SpellMap payloads can join the same path.
  NEXT: Write the task-5 ticket with the design and the Propose -> Confirm; NOTICE melder_0 (v2 S2/S3
    requirement) and melder_1 (xfail removal).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T11:35:29Z
  TYPE: RISK
  CLAIM: Incident: `git --no-optional-locks status --porcelain` issued from this VM at 11:34Z timed out
    on the mount and left a stale 0-byte `.git/index.lock` that the VM cannot unlink (`Operation not
    permitted`); `.git/index` is untouched (11:26). The owner was told to `Remove-Item .git\index.lock`
    before the next index-writing git command. Rule tightened: no `git status` or `git diff` of any kind
    from the VM; only `git --no-optional-locks show` and `log` reads.
  EVIDENCE:
  - tickets/tasks/2026-09-26_hoist_phase8_pool_digest_task.md
  IMPACT: One owner action; no repository content changed.
  NEXT: Owner removes the lock; fable_0 continues with the task-5 ticket.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T12:45:19Z
  TYPE: FACT
  CLAIM: The gate is retired by task 5: both `build_package`s return `Dict` again, `_emit_spell_cache` binds
    the payload unconditionally, `plan_contract_payloads_are_replayable` and `spell_codegen_plan_is_replayable`
    are removed, and the unit gate file is replaced by `test_contract_override_refs.py`. What survives:
    `is_replayable_contract_payload_value` (now on the leaf `CodegenSignature`, facade delegating) as the
    row builders' scalar classifier, and the component fixtures. This task stays in review as the record of
    option B; its acceptance is the story's.
  EVIDENCE:
  - tickets/tasks/2026-09-26_live_contract_override_operands_task.md
  - src/melder/aether/spellbook/spell_compiler/shared_assets/codegen_signature.py:127-170
  IMPACT: No emission gate exists; every plan packages because rows are replayable by construction.
  NEXT: None here; closure with the story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
STATE 2026-09-26T10:19:43Z: opened on owner option B; investigation note recorded; G1 next.
STATE 2026-09-26T10:28:51Z: REVIEW. Owner-run suites pending; NOTICE to melder_0 about the spellbook.py hunk.
STATE 2026-09-26T10:42:09Z: REVIEW. Unit gate file and the caching component test passed in the owner's run; the
object-payload component case failed on the fixture (fixed, not re-run). Decision (1)/(2) open.
STATE 2026-09-26T10:56:37Z: REVIEW. Owner picked (2); seam read shows the overrides emitter literalizes payload values
(CONFLICT note); asking (1)-now + (2)-via-override-design vs (2)-in-emitters. No src edit made.
STATE 2026-09-26T11:26:15Z: REVIEW. Owner: override values may be anything, same path as meld overrides, rename to
`override`; task-5 investigation (read-only) opens on the overrides path, SpellMap and the peer lanes' designs.
STATE 2026-09-26T11:35:29Z: REVIEW. Investigation read (descriptors, phase-9 producers, meld path, design v2, bind.py);
next: create task 5 with the live-operand design and the Propose -> Confirm; NOTICEs to melder_0 and melder_1.
STATE 2026-09-26T12:45:19Z: REVIEW. Gate retired by task 5 (rows carry refs; every plan packages); this ticket is the option-B
record only. Closure with the story.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
