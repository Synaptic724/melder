

# Task: Make function spell ids stable across processes

## Metadata
- Task ID: TASK-2026-09-26-stabilize-function-spell-ids-across-processes
- Story: none (follow-up of TASK-2026-09-26-fix-inspect-signature-nameerror-on-type-checking-annotations)
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T10:27:30Z
- Updated: 2026-09-26T10:38:29Z

## Objective
A function (and other callable) spell's id changes every process because its bind fingerprint hashes the
callable's `repr()`, which carries a memory address (`<function f at 0x...>`). Establish from source exactly
which fingerprint inputs are process-dependent, what consumes spell ids across processes (creation cache,
crystallizer records, restore, Nexus), and propose a stable fingerprint with its migration consequences.

## Ticket Contract
- ENTRY_GATE: Owner selected this lane 2026-09-26 (chat choice "Function spell IDs"); board row
  function_spell_ids routes here.
- EXECUTION_BOUNDARY: Investigation reads src/ and runs probes on VM copies. src edits need owner
  confirmation of a DECISION_REQUEST (propose -> confirm -> implement); a fingerprint change alters every
  affected spell id once, which is a public-behaviour change.
- DEPENDENCIES: Bind v4 fingerprint (Bind.sha256_profile), BindingProfileStrategy callable profile,
  creation-cache and crystallizer consumers of spell ids.
- EXIT_GATE: Root cause and consumer inventory evidenced; plan approved; implementation with regression
  tests (id identical across two fresh processes); suites green on the device tree; docs/graph/assets updated.
- FAILURE_ESCALATION: DECISION_REQUEST for the fingerprint change and its migration; CONFLICT if stability
  and identity semantics (two distinct callables must not collide) cannot both hold; BLOCKER if persisted
  records cannot be migrated safely.

## Scope Boundaries
- In scope: fingerprint inputs for function, method, lambda, partial and other callable spells; every
  process-dependent value in them; consumers that compare spell ids across processes.
- Out of scope: class-spell fingerprints (fixed in the previous task), typing-policy sweep, ProtocolCrafter.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner chose this lane on 2026-09-26; investigation starts.
- from_state: in_progress
- to_state: blocked
- transition_reason: Root cause, consumers and a pre-existing cache defect evidenced; DECISION_REQUEST 2026-09-26T10:34:14Z.
- from_state: blocked
- to_state: in_progress
- transition_reason: Owner approved option 1 plus the cache fix (DECISION 2026-09-26T10:38:29Z).

## Steps / Checklist
- [x] Reproduce: same function spell, two fresh processes, different ids; record the differing input.
- [x] Read Bind.sha256_profile and the callable binding-profile path; list every fingerprint input.
- [x] Inventory consumers of spell ids across processes (cache, crystallizer, restore, Nexus).
- [x] Propose the stable fingerprint and migration (DECISION_REQUEST).
- [ ] Implement with regression tests after approval; validate on the device tree.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Evidence and probes under artifacts/function_spell_ids_20260926/; a fix proposal; after approval, the
  fix, regression tests, docs and rebuilt assets.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/inspector_utility.py
- src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py
- src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py
- src/melder/aether/spellbook/bind/bind.py
- src/melder/aether/spellbook/spellbook_creation_system.py
- src/melder/utilities/caching_system/caching_system.py

## Validation
- Not run.
- Recommended commands:
  - python -X gil=0 -m pytest -q tests/unit tests/component tests/integration

## Risks / Rollback Notes
- Changing the fingerprint changes every affected spell id once; persisted records and caches keyed by the
  old ids must be handled (cache generation bump, crystallizer record compatibility).
- Too little input in the fingerprint risks two distinct callables sharing one id.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behavior claim cited only to a document or a one-line search hit.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/function_spell_ids_20260926/
  - system_docs/patches/active/stable_callable_spell_ids_2026_09_26/
- DISPOSITION: retain_as_reference (evidence); promote_to_documentation (patch lane)
- CLEANUP_TRIGGER: ticket closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - Process-independent bind fingerprints for callable spells.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T10:27:30Z
  TYPE: FACT
  CLAIM: Carried from the closed inspect.signature task (MEASURE 08:47:27Z): a plain function spell
    (make_engine, no TYPE_CHECKING names) got different ids in two fresh processes; the callable
    fingerprint hashes repr_string ("<function f at 0x...>"). Reproduction and root-cause reading are the
    first steps here; the old evidence is the starting point, not the conclusion.
  EVIDENCE:
  - context_compass/artifacts/inspect_signature_nameerror_20260926/results/spell_id_stability_before.txt:1-14
  - src/melder/aether/spellbook/bind/bind.py:890-996
  IMPACT: Function spell ids are random per process; anything that keys persisted or cached state on
    them cannot match across runs.
  NEXT: Read Bind.sha256_profile and the callable profile path in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T10:28:05Z
  TYPE: FACT
  CLAIM: Fingerprint inputs, read in full. Bind._bind_logic uses Bind.sha256_profile as the SpellIndex initial
    id (the spell id). Callable profiles hash name, qualname, module, signature text, each parameter as
    name:kind=default_repr, repr_string, type_name and three flags; instance and "other" profiles hash
    type_name, module and repr_string; all add spell_name, str(spellframe), binding_name, existence and
    disposal names. BindingProfileStrategy routes every non-class callable (functions, lambdas, bound
    methods, partials, callable instances) to the callable profile after InspectorUtility.unwrap_callable,
    and every non-callable object to the instance profile. repr_string and default_repr are
    InspectorUtility.safe_repr (plain repr(), truncated at 120). Process-dependent candidates, pending
    measurement: the default repr of functions/methods/partials/instances ("at 0x..."), and default
    values without a custom __repr__. object_id=id() is stored on the profile but not hashed.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:890-994
  - src/melder/aether/spellbook/bind/bind.py:707-716
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:44-66
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:148-240
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/inspector_utility.py:26-120
  IMPACT: Not only functions: existing-object (instance) spells and callable-instance spells hash their repr
    too, so any object with the default repr gets a new id per process.
  NEXT: Probe every callable/instance shape in two fresh processes and record which ids move and why.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T10:29:00Z
  TYPE: MEASURE
  CLAIM: Two fresh processes (3.14.7t, device-tree src): 10 of 14 candidate shapes get a different spell id
    each run. Unstable: plain function, decorated function, lambda, static method, partial (all via
    "<function ... at 0x...>" in repr_string), bound method and callable instance (the owning instance's
    "object at 0x..."), a function whose default is object() (default_repr carries an address), and an
    existing instance with the default repr (InstanceBindingProfile). Stable: class, class method (repr names
    the class), instances with a custom or dataclass repr, and a SpellContract default (its repr is
    field-based). Every unstable input is a memory address inside a repr() string.
  EVIDENCE:
  - context_compass/artifacts/function_spell_ids_20260926/results/spell_id_shapes_before.txt:1-16
  - context_compass/artifacts/function_spell_ids_20260926/probes/probe_user_shapes.py:1-101
  - context_compass/artifacts/function_spell_ids_20260926/probes/probe_spell_ids.py:1-20
  IMPACT: The defect covers every non-class callable spell and every existing-object spell with the default
    repr, not only functions. Classes (the common case) are already stable.
  NEXT: Inventory the consumers that compare spell ids across processes (creation cache, crystallizer,
    MutationResearch, contracts) from source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T10:31:32Z
  TYPE: MEASURE
  CLAIM: Consumer 1, the conjure creation cache, is hit twice. (a) A book holding any unstable spell never
    reaches full_hit: _build_conjure_cache_state compares live resolvable non-existing-creation ids with the
    cached ids, the function's new id is always missing, so every conjure is "mixed" and recompiles phases
    8-11 (cached payloads load only on full_hit). (b) The bundle grows without bound: conjure stages the
    missing payload and emit() rewrites everything in memory, and nothing removes stale ids (no prune in
    CachingSystem). Measured over three processes: payloads 2 -> 3 -> 4, bytes 2990 -> 3402 -> 3814; the
    class spell's id stayed fixed. Correctness is not at risk: stale payloads are never loaded because
    loading happens only on a full hit.
  EVIDENCE:
  - context_compass/artifacts/function_spell_ids_20260926/results/cache_growth_before.txt:1-15
  - src/melder/aether/spellbook/spellbook_creation_system.py:504-580
  - src/melder/aether/spellbook/spellbook_creation_system.py:1086-1100
  - src/melder/utilities/caching_system/caching_system.py:461-473
  IMPACT: Any book with a function spell pays full phase 8-11 compilation every run and leaks one cache
    payload per unstable spell per process into src/melder/__melder_cache__ (or site-packages).
  NEXT: Read the crystallizer restore and MutationResearch handling of changed ids, then the bind
    collision rule, before proposing the fingerprint.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T10:32:43Z
  TYPE: FACT
  CLAIM: Consumers 2-3 and the collision rule, from source. Crystallizer restore rebinds through
    spellbook.bind and records old->new ids with map_identity when they differ, so restore already tolerates a
    changed id. MutationResearch.record_world_entry is keyed by the binding SHA and treats a known SHA as a quiet
    rediscovery, so a spell whose SHA moves per process is declared as a new version each time recorded
    research is carried into a new process (read, not probed). Bind collision rule: the lookup key is
    (normalize(spellframe or spell_name), normalize(binding_name)) and every raw component of it is a
    fingerprint input, so two binds can share a fingerprint only if they already share a lookup key, which
    Spellbook rejects. One behaviour does depend on the address today: a second object with identical
    fingerprint inputs (for example a re-defined function, or another instance of the same type) can be
    parked as a new version of the same index only because its address differs.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1975-2018
  - src/melder/mutation_research/mutation_research.py:1234-1310
  - src/melder/utilities/helpers/general_helpers.py:333-369
  - src/melder/aether/spellbook/spellbook.py:2335-2385
  - src/melder/aether/spellbook/bind/bind.py:687-716
  IMPACT: Removing the address cannot create a new collision between different binding keys, but it does
    decide what makes two function versions distinct; that needs an owner choice.
  NEXT: Check whether a consumer's cached payload embeds provider spell ids (stable provider ids would make
    full hits reachable for the first time for these books).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T10:33:42Z
  TYPE: MEASURE
  CLAIM: PRE-EXISTING CACHE DEFECT, reproduced with classes only. A consumer's cached manifest stores its
    plan's step_spell_ids (provider ids). When a provider's constructor signature changes, its id changes;
    the next conjure is "mixed", recompiles everything in memory, but stages ONLY the missing (new provider)
    payload, so the consumer's payload from the old world stays. The following process sees every live id
    cached, takes full_hit, and the consumer's first meld raises RuntimeError("generalized manifest
    references unknown spell_id '<old provider id>'") from lazy hydration - in every later process, until the
    cache file is deleted. Sequence measured: variant A ok, B ok, B fails, B fails.
  EVIDENCE:
  - context_compass/artifacts/function_spell_ids_20260926/results/stale_consumer_payload_before.txt:1-53
  - context_compass/artifacts/function_spell_ids_20260926/probes/probe_stale_consumer_payload.py:1-43
  - src/melder/aether/spellbook/spellbook_creation_system.py:1152-1194
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:410-422
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_binding_resolver.py:224-231
  IMPACT: Any edit to a provider's constructor signature breaks melds of its consumers two runs later, with
    caching on by default. Today function-provider books never full-hit, which hides it for them; making
    function ids stable would expose it there too, so the cache fix has to land with (or before) the
    fingerprint fix.
  NEXT: Record the root cause and fix options as a DECISION_REQUEST for the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T10:34:14Z
  TYPE: DECISION_REQUEST
  CLAIM: Root cause: every unstable id comes from a memory address inside a repr() string that
    Bind.sha256_profile hashes (repr_string, default_repr). Proposed fix, two parts, no src edit before owner
    confirmation. PART 1, fingerprint (bind.py sha256_profile only; display reprs unchanged; "v4-binding"
    prefix kept so class ids do not move): option 1 - drop " at 0x..." from the hashed repr text; identity
    stays signature-shaped like classes (a body edit keeps the id; a re-defined same-signature function
    cannot be parked as a separate version of the same index). Option 2 - option 1 plus a hash of the
    function's code object (bytecode, constants, names) for Python functions, so a body edit makes a new
    version; ids then also move on a Python bytecode change. Recommend option 1 (same rule as classes, no
    interpreter coupling). PART 2, conjure cache (needed with either option, and it fixes the pre-existing
    class-provider crash): on every non-full-hit conjure re-stage payloads for ALL live payload-eligible
    spells (phases 8-11 just rebuilt them all) and drop payloads for ids that are not live before emitting,
    so the bundle always equals the current world; bump the creation-cache generation to 12 so existing
    bundles that already hold stale consumer payloads cold-reset once. Files: bind.py,
    spellbook_creation_system.py (_stage_spell_payloads_at_conjure_end), spellbook.py (_emit_spell_cache
    replace path), caching_system.py (generation 12). Tests: unit fingerprint normalization per shape;
    subprocess id-stability for every probe shape; component A/B/B provider-change sequence; bundle size
    stable across runs. Then docs, graph and asset rebuild. One-time effects: function, lambda, method,
    partial, callable-instance and default-repr instance ids change once to their stable values; caches
    cold-reset once; restore already maps changed ids; MutationResearch declares one last new version each.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:938-994
  - src/melder/aether/spellbook/spellbook.py:975-1010
  - src/melder/utilities/caching_system/caching_system.py:151-151
  - context_compass/artifacts/function_spell_ids_20260926/results/stale_consumer_payload_before.txt:1-53
  IMPACT: Implementation waits for the owner's choice of option and confirmation of both parts.
  NEXT: Ask the owner: option 1 or 2, and whether the cache fix lands in this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T10:38:29Z
  TYPE: DECISION
  CLAIM: Owner approved the DECISION_REQUEST as recommended ("yeah go ahead and fix that fable_0 might be
    working on something similar just let him know"): option 1 (drop memory addresses from the hashed repr
    text; signature-shaped identity; "v4-binding" prefix kept) plus the conjure-cache fix in this lane
    (re-stage every live payload-eligible spell on a non-full-hit conjure, drop payloads for non-live ids,
    creation-cache generation 12). Design refinement to stay off fable_0's hunk: spellbook.py
    _emit_spell_cache (fable_0's replayability gate, in review) is NOT edited; the re-stage removes the old
    payload through CachingSystem.remove_spell_payload before calling _emit_spell_cache unchanged.
  EVIDENCE:
  - tickets/tasks/2026-09-26_gate_cache_emission_on_replayable_payloads_task.md:20-40
  - src/melder/aether/spellbook/spellbook.py:975-1010
  IMPACT: Implementation starts after a NOTICE to fable_0 and the patch lane.
  NEXT: Send fable_0 M1-11, then read the conjure cache path in full before the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T10:40:52Z
  TYPE: DECISION
  CLAIM: Owner chose "Hash the full repr": binding profiles carry an address-free, untruncated repr used
    only by the fingerprint (display repr_string unchanged). Reason: safe_repr truncates at 120 characters,
    so stripping addresses from the cut text alone leaves ids unstable when an address inside the cut
    window changes digit count between processes. File set grows by three:
    inspector_utility.py (one pure static helper), binding_profile.py (fingerprint fields on the callable,
    instance and other profiles and on the parameter summary), binding_profile_strategy.py (fills them).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/inspectors/inspector_utility.py:26-60
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py:234-460
  IMPACT: Final src set: bind.py, inspector_utility.py, binding_profile.py, binding_profile_strategy.py,
    spellbook_creation_system.py, caching_system.py (spellbook.py untouched).
  NEXT: Check the mailbox for fable_0, author the patch lane, then implement in a VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T10:43:26Z
  TYPE: PLAN
  CLAIM: Patch lane stable_callable_spell_ids_2026_09_26 authored and linked (architecture, three component
    patches, code description for the conjure restage). Read order done. Mapping (patch -> implementation ->
    validation): spell_examination_profiles -> InspectorUtility.stable_repr, profile fingerprint fields,
    strategy fills them -> helper unit tests. binding_pipeline -> sha256_profile hashes fingerprint text with
    address-stripped fallback -> unit equality/difference tests, in-process distinct-object equality, one
    cross-process id check. spellbook_core_creation_cache + code description -> remove-all then re-stage
    sorted live ids, emission flag on removal, generation 12 -> provider A/B/B/B component sequence and bundle
    count. Then full suites on the device tree, promotion, graph, assets. Implementation happens in a VM copy
    first; device files are patched in place only after the copy is green.
  EVIDENCE:
  - system_docs/patches/active/stable_callable_spell_ids_2026_09_26/architecture_patch.md:1-81
  - system_docs/patches/active/stable_callable_spell_ids_2026_09_26/code_description_patch_conjure_cache_restage.md:1-31
  IMPACT: Patch-framework entry gate satisfied.
  NEXT: Implement in the VM copy (profiles/helper/strategy, bind, creation system, caching system).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T10:46:20Z
  TYPE: MEASURE
  CLAIM: Implemented in a VM copy only (script artifacts/function_spell_ids_20260926/stable_ids_patch.py,
    per-anchor CRLF/LF). One finding during the probe: the signature TEXT also carries addresses (a default
    such as object() renders "<object object at 0x...>" inside str(signature)), so sha256_profile strips
    addresses from the callable signature and the class init_signature as well; a class with such a
    default was unstable before (15th probe shape). After, two fresh processes each: all 15 shapes stable;
    the 11 unstable ones get new ids once; the 4 already-stable ids did not move. Cache: bundle stays at 2
    payloads / 2990 bytes over three processes (was 2 -> 3 -> 4); provider A, B, B, B melds succeed every
    time (was: third and fourth failed).
  EVIDENCE:
  - context_compass/artifacts/function_spell_ids_20260926/results/spell_id_shapes_after.txt:1-17
  - context_compass/artifacts/function_spell_ids_20260926/results/cache_after.txt:1-27
  IMPACT: Both defects are fixed in the copy; class init_signature stripping widens the "class ids do not
    move" invariant to "stable class ids do not move" (patch docs to update).
  NEXT: Add the regression tests in the VM copy, then run unit, component and integration suites there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Opened 2026-09-26T10:27:30Z on owner selection. Investigation first; no src edits until the owner approves a plan.
Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
