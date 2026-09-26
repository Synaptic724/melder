

# Task: Make function spell ids stable across processes

## Metadata
- Task ID: TASK-2026-09-26-stabilize-function-spell-ids-across-processes
- Story: none (follow-up of TASK-2026-09-26-fix-inspect-signature-nameerror-on-type-checking-annotations)
- Status: review
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-09-26T10:27:30Z
- Updated: 2026-09-26T11:22:15Z

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
- from_state: in_progress
- to_state: review
- transition_reason: Fix on the device tree; VM-copy suites green; docs, patch docs, graph and assets current (2026-09-26T11:22:15Z).

## Steps / Checklist
- [x] Reproduce: same function spell, two fresh processes, different ids; record the differing input.
- [x] Read Bind.sha256_profile and the callable binding-profile path; list every fingerprint input.
- [x] Inventory consumers of spell ids across processes (cache, crystallizer, restore, Nexus).
- [x] Propose the stable fingerprint and migration (DECISION_REQUEST).
- [x] Implement with regression tests after approval; validate on the device tree.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

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
- Agent runs (VM copy synced from the device tree, Python 3.14.7t, -X gil=0): tests/unit 8594 passed;
  tests/component 2109 passed; tests/integration 1925 passed (one run also hit the known pre-existing
  concurrency flake, which passes alone); build_assets + llm_support unit 144 passed.
- Owner machine: Not run.
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
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
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
- DATETIME: 2026-09-26T10:50:57Z
  TYPE: MEASURE
  CLAIM: VM-copy suites with the change (device tree re-synced, 3.14.7t): tests/unit 8594 passed (13 new);
    tests/component 2108 passed, 1 failed. The failure is expected and wanted: fable_0's
    test_executor_signatures_are_equal_across_interpreter_processes[probe_contract_payload_book_signatures]
    is xfail(strict=True) because a class whose constructor default is a SpellContract with an object payload
    had a process-local id (SpellContract repr renders the payload's address inside init_signature); it now
    XPASSes. Consumed mailbox F0-4 (fable_0 ACK: none of bind.py, spellbook_creation_system.py,
    caching_system.py or the generation is in their plan; the re-stage composes with their gate) and F0-5
    (the same class-default case; "remove the marker then"). New tests fail on the original tree
    (14 of 15 unit, the cross-process test, 3 of 4 restage cases; the passing ones are guards).
  EVIDENCE:
  - tests/component/melder/spellbook/test_codegen_signature_determinism.py:494-522
  - tests/component/melder/spellbook/test_conjure_cache_restage.py:1-204
  IMPACT: One edit in fable_0's test file (drop the strict xfail marker, as fable_0 asked), then integration.
  NEXT: Drop the marker in the VM copy, rerun component and integration, then patch the device.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T10:57:49Z
  TYPE: MEASURE
  CLAIM: VM copy after dropping fable_0's strict xfail: tests/component 2109 passed. tests/integration run 1:
    12 failed = 11 cases of test_cache_schema_version_integration.py, which pins CACHE_VERSION_HISTORY (the
    generation-12 entry must be added there, as melder_0 did for 10 and 11) + 1 intermittent
    test_conduit_cluster_concurrent_meld_unique_per_conduit_cluster_shared_instance ("Cannot build
    CreationContext before spell_codegen_creation exists"), which passes 3/3 alone and 4/4 as a file and is
    the pre-existing flake recorded by two earlier lanes on pre-change sources. After adding 12 to the pinned
    history: integration run 2 = 1925 passed, 3 skipped, 7 xfailed, 1 xpassed, 0 failed.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:12-24
  - tickets/tasks/completed/2026-09-25_implement_creation_slot_build_guards_task.md:290-300
  - tickets/tasks/completed/2026-09-26_implement_missing_dependency_sockets_task.md:648-656
  IMPACT: Ready to patch the device: 6 src files (base hashes re-verified unchanged), 3 new tests, 2 test edits
    (fable_0's marker, the pinned history).
  NEXT: Apply the scripts to the device tree, copy the new tests (CRLF), verify hashes equal the VM copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T10:58:23Z
  TYPE: FACT
  CLAIM: Device tree patched in place with the same scripts (per-anchor CRLF/LF kept): inspector_utility.py
    (stable_repr, strip_memory_addresses, class pattern), binding_profile.py (fingerprint_repr on three
    profiles, default_fingerprint_repr on the parameter summary), binding_profile_strategy.py (fills them),
    bind.py (sha256_profile hashes address-free repr, default, signature and init_signature text; two helpers),
    spellbook_creation_system.py (_stage_spell_payloads_at_conjure_end: remove all, re-stage sorted live ids,
    flag emit on removal), caching_system.py (generation 12). Tests: 3 new (CRLF); fable_0's strict xfail
    dropped per F0-5; generation 12 added to the pinned history test. All 11 files hash-equal to the validated
    VM copy; focused re-run on the copy: 1245 passed (bind, spell_crafter, new tests, annotation guard,
    determinism, cache history). spellbook.py untouched.
  EVIDENCE:
  - context_compass/artifacts/function_spell_ids_20260926/results/commit_manifest.txt:1-11
  - src/melder/aether/spellbook/bind/bind.py:892-1048
  IMPACT: Code done; docs, graph and asset rebuild remain.
  NEXT: Promote to src_components/src_architecture/tests_components, refresh the graph, rebuild assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T11:03:59Z
  TYPE: FACT
  CLAIM: Canonical docs promoted and read back. src_components: Binding Pipeline "Process-stable
    fingerprints" block, Spellbook Core generation-12 bullet, Spell Examination Profiles fingerprint-text
    bullet. src_architecture: Operational Invariant "Process-stable spell ids and complete cache bundles" plus
    a handoff entry. tests_components: the new unit test in the Spellbook Runtime And Binding Unit Cluster,
    the two new component tests in its Component Cluster, plus a handoff entry. All three indexes --check OK
    (9341, 2825, 1626 lines). Process note: the tests_components edit was made after the compaction but
    before REONBOARD (disclosed in the attestation); it was read back after re-certification and is as intended.
  EVIDENCE:
  - system_docs/src_components.md:600-616
  - system_docs/src_components.md:368-375
  - system_docs/src_components.md:4241-4244
  - system_docs/src_architecture.md:849-856
  - system_docs/tests_components.md:717-717
  - system_docs/tests_components.md:775-776
  - system_docs/tests_components.md:1595-1597
  IMPACT: Documentation promotion is complete apart from the patch-doc wording updates.
  NEXT: Update patch docs (architecture Invariant 4; signature/init_signature stripping in the binding
    pipeline component patch), then refresh the graph for the six src files.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T11:04:44Z
  TYPE: FACT
  CLAIM: Patch docs amended to the implemented behaviour. architecture_patch.md: non-goal and Invariant 4 now
    say already-stable ids do not move, while a class whose constructor default renders an address in its
    init_signature changes once; rollout step 2 names the signature/init_signature stripping; rollback
    trigger and validation evidence (15 shapes, A/B/B/B) updated. component_patch_binding_pipeline.md: the
    after-behaviour records the signature/init_signature stripping and why.
  EVIDENCE:
  - system_docs/patches/active/stable_callable_spell_ids_2026_09_26/architecture_patch.md:16-20
  - system_docs/patches/active/stable_callable_spell_ids_2026_09_26/architecture_patch.md:49-50
  - system_docs/patches/active/stable_callable_spell_ids_2026_09_26/component_patch_binding_pipeline.md:17-26
  IMPACT: Patch lane matches the code and the canonical docs; it can be archived at closure.
  NEXT: Graph refresh: extract the six changed src files into a scratch descriptor copy with --strict, copy
    back only this lane's descriptors, re-read and accept, assemble.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T11:08:50Z
  TYPE: MEASURE
  CLAIM: Graph refreshed for this lane only. Extracted with 3.14.7t --strict into a scratch copy (no skips);
    the six descriptors' old source_sha256 equal the pre-patch base hashes and the new ones equal the
    committed hashes, so their only delta is this lane. Prose updated for Bind (address-free fingerprint),
    InspectorUtility (stable_repr, strip_memory_addresses), the parameter summary and callable, instance and
    other profiles (fingerprint fields in responsibilities and owns_state), BindingProfileStrategy (fills
    them), SpellbookCreationSystem (bundle rebuild) and CachingSystem (generation 12). Accepted after
    re-reading prose against source: Bind, InspectorUtility, the four profile classes, BindingProfileStrategy
    and the two module nodes whose stamps matched the base. NOT accepted, stale before this lane:
    SpellbookCreationSystem and CachingSystem (stamped against spans older than the base, so other lanes'
    changes are unverified) and the unstamped bind and caching_system module nodes. Only the six
    descriptors were copied back (their mtimes predate the scratch copy); assemble_graph --check: 597
    sections, 1238 nodes, all ranges verified, 28121 lines.
  EVIDENCE:
  - system_docs/src_graph.md:5853-5925
  - system_docs/src_graph.md:12767-12793
  - system_docs/src_graph.md:12913-13029
  - system_docs/src_graph.md:13179-13227
  - system_docs/src_graph.md:16018-16086
  - system_docs/src_graph.md:26090-26149
  IMPACT: Graph current for this lane; two class nodes remain SEMANTICS_STALE for pre-existing reasons.
  NEXT: Rebuild packaged assets (_build_asset_runner.py, then --check) and LLM bundles (llm_support
    _builder.py, then --check), then run the asset and llm_support unit tests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-26T11:21:51Z
  TYPE: MEASURE
  CLAIM: Assets rebuilt on the device tree with 3.14.7t. _build_asset_runner.py first failed with
    PermissionError unlinking a stale payload (delete permission did not survive the device reconnect); the
    owner-side prompt granted delete for the melder_private folder and the rerun wrote all three families
    (agent_documentation 454, bind_guard 634, system_documents 4 entries, v0.2.54); --check: all three
    current. llm_support/_builder.py rewrote src 590, tests 865, other 370 files; --check: all proofs match.
    Content diffs vs HEAD are limited to the regenerated manifests and payloads (git diff
    --ignore-cr-at-eol). Refreshed VM copy (src, tests, llm_support, system_docs, docs synced; 3.14.7t):
    tests/unit/melder/build_assets + tests/unit/llm_support 144 passed; tests/unit 8594 passed, 3 skipped,
    7 xfailed; tests/component 2109 passed, 24 skipped, 1 xfailed. Integration not re-run (src/tests
    unchanged since the 1925-passed run). Owner machine: Not run.
  EVIDENCE:
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:1-40
  - llm_support/manifest.json:1-20
  IMPACT: Exit gate met: fix on the device tree, docs, patch docs, graph and assets current.
  NEXT: Move the task to review (status, transition, board, artifact board) and report to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Opened 2026-09-26T10:27:30Z on owner selection. In review since 2026-09-26T11:22:15Z.
- Delivered: address-free bind fingerprints (callables, default-repr instances, classes with
  address-rendering defaults are now process-stable; already-stable ids unchanged) and the conjure cache
  restage (non-full-hit conjure rebuilds the bundle; generation 12), which also fixes the pre-existing
  consumer full-hit crash after a provider id change. 6 src files, 3 new tests, 2 test edits (fable_0's
  strict xfail removed per F0-5; generation 12 in the pinned history).
- One-time effects: affected spell ids change once; caches cold-reset once; MutationResearch records one
  more version per affected spell (read from source, not probed).
- Docs: src_components, src_architecture, tests_components, graph, packaged assets and LLM bundles current.
  Patch lane stays active until closure (promote_to_documentation, then archive).
- Open: owner commit and owner-machine suites; closure after acceptance. SpellbookCreationSystem and
  CachingSystem graph nodes remain SEMANTICS_STALE for pre-existing reasons (other lanes' deltas).
Resume from the latest Notes NEXT.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
