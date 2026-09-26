# Task: Survey the compiler driver and phases 1-4 for inputs, outputs and live-object holds

## Metadata
- Task ID: TASK-2026-09-25-survey-compiler-phases-1-4
- Story: STORY-2026-08-03-phase-pipeline-survey
- Status: in_progress
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-25T21:23:55Z
- Updated: 2026-09-26T00:08:30Z

## Objective
Produce source-backed records for the phase driver (`spell_compiler.py`, `spell_compiler_artifact.py`)
and phases 1-4 (requirements, symbolic graph, local frame, validation): what each consumes, what it
produces, where it holds a live object, and what runtime state it mutates.

## Ticket Contract
- ENTRY_GATE: Active board row routes here; owner approved the story scope.
- EXECUTION_BOUNDARY: Read-only over `src/melder/aether/spellbook/spell_compiler/**` and `tests/`.
  Writes limited to this ticket, the story, and `artifacts/ir_phase_survey_20260925/`.
- DEPENDENCIES: STORY-2026-08-03-phase-pipeline-survey; epic scope ruling (1-10 IR, 11 hydrates).
- EXIT_GATE: `driver.md` and `phase_01.md` .. `phase_04.md` exist with evidence ranges covering the
  cited logic; every hold classified or marked UNKNOWN; status review.
- FAILURE_ESCALATION: BLOCKER if behavior cannot be established from source; DECISION_REQUEST for
  any hold that appears identity-bearing; CONFLICT when source contradicts the architecture doc.

## Scope Boundaries
- In scope: `spell_compiler.py`, `spell_compiler_artifact.py`, `phases/compiler_phase_1.py` through
  `compiler_phase_4.py`, `phases/utility.py`, the parts of `phases/shared_compiler_executions.py`
  these phases call, and delegates (`spell_requirements_finder/`, `symbolic_graph/`, `dag/`,
  `validation/`) to the depth needed to name the crossing type.
- Out of scope: phases 5-11 (later tasks), Spellbook internals beyond the conjure call into the
  driver, any edit under `src/` or `tests/`.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Created with the story; moves to in_progress on owner approval.
- from_state: ready
- to_state: in_progress
- transition_reason: Owner said to go read the src_components details (2026-09-25); step 1 began.

## Steps / Checklist
- [x] Verify `src_components_index.md` (line_count, content_sha256), then slice
      `Component: SpellCompiler and Validation Pipeline` and
      `Subcomponent: SpellCompiler Phase Artifacts` for navigation only.
- [x] Read `spell_compiler.py` and `spell_compiler_artifact.py` in full; write `driver.md`:
      phase sequencing, the artifact container, and what it stores.
- [x] Read `compiler_phase_1.py` in full plus its delegations; write `phase_01.md`. (finder trio
      read whole 2026-09-26; phase_01.md COMPLETE)
- [ ] Read `compiler_phase_2.py` in full plus its delegations; write `phase_02.md`.
- [ ] Read `compiler_phase_3.py` in full (1035 lines, three sequential chunks) plus delegations;
      write `phase_03.md`.
- [ ] Read `compiler_phase_4.py` in full plus its delegations; write `phase_04.md`.
- [x] Add the `artifact_board.md` row when the first record lands.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/ir_phase_survey_20260925/driver.md
- artifacts/ir_phase_survey_20260925/phase_01.md through phase_04.md
- Notes carrying `path:start-end` evidence for every recorded hold.

## Record Shape (one file per phase)
- Entry: symbol(s) and caller.
- Consumes: each input with its type, producer, and where it is stored when the phase starts.
- Produces: each output with its type, where it is stored, and which later phase reads it.
- Holds: each live object the phase reads or stores, classified value-expressible,
  identity-bearing, or runtime-only, with the reason from the code that uses it.
- Mutates: runtime objects the phase writes (Spell, Spellbook, SpellSystemStates, frame).
- Reflection points: every `inspect`/annotation/`__dict__`/attribute read of a USER object.
- Python-callback points: every call into a user callable, hook or factory mid-phase.
- World reads: every registry or spellbook-state lookup the phase performs (the query surface).
- Contradictions: where source disagrees with `src_architecture.md` or the epic text.
- UNKNOWN: each open item with the file:symbol to investigate.

## Files / Paths Impacted
- None under `src/` or `tests/`. This ticket, the story, and the artifact directory only.

## Validation
- Not run.
- Recommended commands:
  - none for this read-only task.

## Risks / Rollback Notes
- The VM shell runs Python 3.10.12; the project floor is 3.14. Nothing is executed here.
- `shared_compiler_executions.py` is 1516 lines: read the sections phases 1-4 call in sequential
  chunks of at most 500 lines and record which sections belong to later tranches.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No hold classified from a name or docstring; the classification cites the code that uses it.

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
  - artifacts/ir_phase_survey_20260925/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Story closure; owner decides retention when findings promote to the schema story.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: driver sequencing; phases 1-4 inputs, outputs, holds, side effects.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-25T21:23:55Z
  TYPE: PLAN
  CLAIM: Read order is driver first (spell_compiler.py, spell_compiler_artifact.py), then phases 1-4
    in order, following each delegation only far enough to name the type that crosses the phase
    boundary. One record per file lands before the next phase is opened.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:1-693
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:1-207
  IMPACT: The driver defines the artifact container every phase reads and writes; reading it first
    fixes the vocabulary the four records share.
  NEXT: On approval, verify src_components_index.md and slice the SpellCompiler component section.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7
- DATETIME: 2026-09-25T21:32:40Z
  TYPE: FACT
  CLAIM: src_components.md (index verified: 9004 lines, sha bbbb1404...) states that phases 8-11
    already export a serializable "phase8_11 codegen IR" with a dirty bit on SpellCompilerArtifact,
    capture/flush/reset functions in shared_compiler_executions.py, ordered "IR/hash tuples", and a
    creation cache whose "cached executors hydrate against current bound Spells". Phases 1-7
    artifacts (requirements, symbolic graph, resolution frame, validation results, root blueprints)
    are attached to Spell via SpellCompilerArtifact, keyed by spell_index.selected_spell_id, and
    phase 5 publishes onto spellbook._spells_by_id with attachment setters that invalidate
    downstream codegen. This is document evidence of intent, not yet of behavior.
  EVIDENCE:
  - system_docs/src_components.md:3053-3058
  - system_docs/src_components.md:3067-3087
  - system_docs/src_components.md:3109-3129
  - system_docs/src_components.md:3164-3186
  - system_docs/src_components.md:4507-4527
  IMPACT: The epic's premise "the plan is not an artifact" looks true for phases 1-7 and already
    partially false for 8-11. The value-shaped seam may exist in embryo at the 8-11 export payload.
  NEXT: Read shared_compiler_executions.py:1342-1477 and spell_compiler_artifact.py in full to
    establish what codegen_ir actually contains and how the cache key is formed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-25T21:32:40Z
  TYPE: FACT
  CLAIM: src_components.md states phase 1 requirement metadata "retains the annotation and exact
    default object" (defaults incl. None, falsey scalars, selected instances, collection defaults are
    classified PLAIN before annotation inference), while phase 3 performs world-dependent
    resolution: SpellMap defaults by iterating Spellbook._spell_id_pool and collection DI by
    scanning all spells. Phase 5/8 path handling already uses PathRegistry (PathId interning) and
    DagIndex (SocketRef stores param_path_id).
  EVIDENCE:
  - system_docs/src_components.md:3060-3070
  - system_docs/src_components.md:4436-4451
  - system_docs/src_components.md:4519-4522
  - system_docs/src_components.md:5835-5847
  IMPACT: First concrete live-object hold candidate for the IR identity question (exact default
    objects in phase 1); first evidence that facts (phase 1) and world decisions (phase 3) are
    already separated by phase, which the "level 0" framing depends on; an interned-id scheme
    already exists for paths and sockets and is a candidate symbolic-id base.
  NEXT: Read spell_requirements_finder.py to see whether reflection and classification are
    separable inside phase 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T21:32:40Z
  TYPE: HYPOTHESIS
  CLAIM: The decoupling gap is front-loaded: phases 1-7 carry compile state on runtime Spell
    objects, while 8-11 already have a value-shaped export and a hydrating cache. If source
    confirms this, the epic's tranche order (1-4, 5-7, 8-10) is right for the port but the
    schema story should start from the existing 8-11 payload as the L4 seed rather than invent it.
    Also: existing-creation spells bypass 8-11 and the pipeline runs per-spell units on
    PhaseScheduler worker threads, so IR nodes must be immutable values safe for parallel passes.
  EVIDENCE:
  - system_docs/src_components.md:3109-3121
  - system_docs/src_components.md:4494-4505
  - system_docs/src_components.md:5797-5812
  IMPACT: Changes what the schema story starts from and adds an immutability requirement.
  NEXT: Confirm or refute by reading the driver and phase 1; falsify with source before use.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T22:17:50Z
  TYPE: FACT
  CLAIM: Driver read complete. Phases 1, 2, 9 and 10 take only (spell, artifact); 3-8 and 11 take
    the live spellbook and/or spell_system_states (world reads at signature grain). The artifact
    container holds phase outputs as Cleanable OBJECTS in 27 slots plus an RLock, and a
    value-shaped `_codegen_ir: Dict` with a dirty bit. Phase-1 requirements may be BORROWED from
    the spell's bind-time resolution profile (`_requirements_borrowed`).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:129-158
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:195-261
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:599-660
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:78-146
  IMPACT: Fixes the survey vocabulary and the first cut of the world-read surface; the level-0
    question now has a concrete lead in the bind-time resolution profile.
  NEXT: Read profiles/resolution_profile.py and the borrow path before phase 1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T22:17:50Z
  TYPE: FACT
  CLAIM: A value-only, SHA256-signed export of phases 2-5 already exists
    (`capture_phase2_5_codegen_ir`: symbolic dependency tuples, ordered node ids, validation codes,
    phase-5 socket rows and DAG edge rows, index ids) and is DORMANT BY DESIGN: phase 2 records
    that the eager capture was removed for having no production readers and is kept "as the seam
    for a future incremental recompile path". Phase 8-11 export is a digest; plan content lives in
    `build_phase11_variant_ir_payload` (step rows plus a 40-slot transient plan whose schema is
    "only ints and tuples of ints", call targets dropped). Phase-11 codegen creation CONSUMES the
    step rows, memoized on the plan.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:266-376
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_2.py:179-184
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:503-565
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1278-1345
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:300-345
  IMPACT: The IR is not greenfield. The port is inverting the arrow (phases consume rows) and
    adding readers to a seam the code already reserved for incremental recompile. Contradicts
    the epic's "there is nothing to record" as stated; the working representation is still objects.
  NEXT: Read phases 9 and 10 bodies to test whether they are closed over rows already.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-25T22:17:50Z
  TYPE: HYPOTHESIS
  CLAIM: Two signature-determinism hazards and one duplication: (a) the serializer pickles
    `set`/`frozenset` parts in iteration order (hash-seed dependent for str) unless pre-frozen;
    (b) `freeze_phase11_schema_value` falls back to `repr(value)`, and step rows freeze
    user-supplied contract payload values, so an object-valued payload yields a process-local
    executor signature (cache miss per process; false hit only on identical reprs);
    (c) `CodegenCreationSchemaHelpers` duplicates the serializer/hash/freeze/row builders and is
    imported under the alias `SharedCompilerExecutions`, so two copies must stay byte-identical
    or cache keys diverge silently. Also: `get_phase11_step_ir_rows` probes owned plan objects with
    `getattr(..., None)`, against the overlay's attribute-access rule.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:78-90
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:424-424
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1045-1052
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:1-60
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:337-345
  IMPACT: Cheap, high-value: a determinism test (same plan, two processes, equal signatures) and
    a single serializer would harden the creation cache before the IR builds on it.
  NEXT: Audit `hash_codegen_signature` callers for set-typed parts; propose the test to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T22:19:13Z
  TYPE: FACT
  CLAIM: Conjure classifies the creation cache by spell-id set membership (live resolvable,
    non-existing-creation spell ids vs cached ids): `full_hit` when every live id is cached. A full
    hit passes `force_skip_plan_phases=True` so phases 8-11 are skipped and creation contexts load
    from cache, and the resolution verdict is not re-enforced. The structural phases (1-4) run on
    EVERY conjure via `_prepare_spellbook_for_conjure` -> `run_structural_phases`, then
    `_prepare_resolution_for_conjure` runs the conduit-scoped phases (5-7, and 8-11 unless
    skipped). Phase 10 lazily imports the planner subtree ("~11ms import") precisely because
    full-hit conjures never run it. Phases 9 and 10 gate on `spell.resolvable` and call
    `process(spell, artifact)` / `planner.build(artifact)` - closed at the call level.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:226-247
  - src/melder/aether/spellbook/spellbook_creation_system.py:300-345
  - src/melder/aether/spellbook/spellbook_creation_system.py:412-485
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:44-48
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:100-112
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:64-91
  IMPACT: The warm-conjure regime has a precise gap: 1-7 recompute on a full hit although the
    dormant phase 2-5 signature would key a structural snapshot. That is the epic's hydration
    story made concrete, and the cache key (spell id = bind fingerprint) is already the L0 hash.
  NEXT: Read run_structural_phases (spellbook_creation_system.py:1359+) to see what 1-4 write
    into runtime state, which is what a structural snapshot must hydrate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-25T22:42:24Z
  TYPE: FACT
  CLAIM: System documents corrected from source (owner-authorized 2026-09-25), indexes regenerated
    and verified current (architecture 2708 lines / 53 sections; components 9059 lines / 141
    sections). src_architecture.md: Boot step 1 now lists the six eagerly built roots in
    construction order with the 2026-08-03 MR ruling; the Conjure sequence now records
    cache-path classification and the full-hit skip of phases 8-11 only. src_components.md:
    SpellCompiler component gains "Codegen IR export seams (2026-09-25)" (artifact IR dict,
    dormant signed phase 2-5 export, phase 8-11 digest vs consumed step rows and int-array
    transient schema, signature path and duplicated helper, phase 9/10 closure and lazy import)
    and two Key Files; the Conjure flow records the cache classification. Both handoff summaries
    carry a dated entry. No new prose line exceeds the hard cap; no package path was written into
    either document. Not touched: src_graph.md, src_graph_index.md (their working-tree diff
    predates this session, 2026-09-24T11:11).
  EVIDENCE:
  - system_docs/src_architecture.md:541-551
  - system_docs/src_architecture.md:646-670
  - system_docs/src_components.md:3075-3113
  - system_docs/src_components_index.md:16-18
  - system_docs/src_architecture_index.md:16-18
  IMPACT: The packaged hardcopies under src/melder/_build_assets/_system_documents/payloads/ are
    now behind the documents until the build-asset runner regenerates them (a `src/` change,
    owner-run or approved).
  NEXT: Owner decides when to regenerate build assets; survey resumes at the resolution profile.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-25T22:53:13Z
  TYPE: FACT
  CLAIM: Level 0 at bind exists in source. Phase 1 borrows `spell.profile.resolution_profile
    .requirements` when live and keyed to the same content-SHA spell id; the docstring states bind
    already ran `SpellRequirementsFinder` via `SpellGeneralProfile.complete_with_spell` to avoid
    re-reflecting (`inspect.signature` + annotation resolution) every pass. Phase 1 also emits a
    value-only requirements shape profile (counts, sorted DI-shape histogram). `SpellResolutionProfile`
    is a documented execution-model-independent "how to resolve one Spell" payload spanning phases
    1-4 with placeholder node/edge/frame/validation classes; only `requirements` is populated, and
    it holds a live `spellframe: Any` and a `SpellRequirements` object, so it is a proto-IR in
    intent, not value-only in form. phase_01.md written as PARTIAL (finder unread).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:143-207
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:43-103
  - src/melder/aether/spellbook/spell_compiler/profiles/resolution_profile.py:404-515
  - src/melder/aether/spellbook/spell_compiler/profiles/resolution_profile.py:11-402
  IMPACT: The owner's "level 0 starts at bind" is source-backed: the work is making the existing
    bind-time capture value-shaped and letting the profile family carry phases 2-4 rows, not adding
    a phase. The identity question's first instance (default objects) sits inside the finder.
  NEXT: Read spell_requirements_finder.py (three chunks) and spell_requirements.py; complete
    phase_01.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T00:04:29Z
  TYPE: FACT
  CLAIM: Post-compaction re-entry (REONBOARD 2026-09-26): melder_0 landed the per-slot creation build
    guards and regenerated both system-document indexes at 2026-09-25T23:40:36Z, after this task's
    documentation edits. The edits survived (boot step with six roots, conjure cache paths, the IR
    seams block). src_architecture.md grew 2708 -> 2732 lines and src_components.md 9059 -> 9106, so
    ranges cited into those documents by earlier notes are stale by up to 24 and 47 lines and must
    be re-verified before reuse. The creation cache is now generation 10 (rejects executors emitted
    with the previous locking); notes above that say generation 9 describe the state when written.
    Compiler sources cited by this task are unchanged since they were read (mtimes 2026-08-29 to
    2026-09-20); creation_runtime_door_compiler.py (23:23:03Z) and caching_system.py (22:56:22Z)
    changed and are not cited by range here.
  EVIDENCE:
  - system_docs/src_components_index.md:15-16
  - system_docs/src_architecture_index.md:15-16
  - system_docs/src_architecture.md:541-550
  - system_docs/src_architecture.md:646-670
  - system_docs/src_architecture.md:841-852
  - attention_board.md:111-111
  IMPACT: No survey finding changes; only citation ranges into the two system documents do.
  NEXT: Read spell_requirements_finder.py 1-500, 501-1000, 1001-1333, then spell_requirements.py.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T00:08:30Z
  TYPE: FACT
  CLAIM: Phase 1 read whole (finder 1333 lines, spell_requirements 305, spell_parameter_requirements
    311, parameter_di_shape 70); phase_01.md is COMPLETE. Reflection IS separable from classification:
    the facts (borrowed or fresh `inspect.signature` in FORWARDREF format, best-effort
    `get_annotations(eval_str=True)` in the user's module namespace, default kind, annotation shape)
    are read in `_build_parameter_requirements` and `_resolve_parameter_annotations`, while
    `_classify_parameter`, `_unwrap_optional` and `_looks_like_di_target` are pure over shape
    predicates. World reads: NONE in the four files. Holds: live type objects in `annotation`,
    `collection_element_annotation` and `spellframe` (value-expressible as type refs; identity use
    UNKNOWN until phases 2-3); the EXACT default object on every defaulted parameter, PLAIN included
    (identity candidate #1 if a later phase passes it); SpellMap/SpellContract descriptor instances;
    one RLock per requirements artifact and per parameter row. No runtime mutation. Existing-creation
    spells and call targets without a usable signature yield empty parameter lists.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1019-1098
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:426-552
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1100-1226
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:1287-1333
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements_finder.py:324-349
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements.py:71-114
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_requirements.py:200-291
  - src/melder/aether/spellbook/spell_compiler/spell_requirements_finder/spell_parameter_requirements.py:73-146
  - artifacts/ir_phase_survey_20260925/phase_01.md:1-166
  IMPACT: Level 0 is an extraction with a concrete cut line, and phase 1's closure test is already
    satisfiable for the facts. Open: PLAIN default passing, identity matching in phases 2-3, and the
    descriptor field values (spell_map.py, spell_contract.py).
  NEXT: Read compiler_phase_2.py whole plus its symbolic_graph delegates; write phase_02.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Step 1 done 2026-09-25: components index verified and the SpellCompiler component plus phase
subcomponents and conjure flows sliced. Three findings recorded above (existing 8-11 codegen IR
export and cache; phase-1 exact default objects; phase-3 world decisions). No source read yet.
Step 2 done 2026-09-25: driver.md written (artifacts/ir_phase_survey_20260925/driver.md) with the
world-read surface, the container, the dormant phase 2-5 export seam, the consumed phase-11 rows,
and the hashing hazards. Resume at Step 3 (phase 1), after profiles/resolution_profile.py.
STATE 2026-09-25T22:51:29Z: seven notes recorded; driver.md is the only artifact so far. Read order for
resumption: resolution_profile.py (two chunks, 1-500 and 501-515) -> compiler_phase_1.py (whole)
-> spell_requirements_finder.py (three chunks) -> COMPLETE phase_01.md using the Record Shape
including reflection points, Python-callback points and world reads. Nothing under src/ or
tests/ was edited; system_docs edits were owner-authorized and are indexed.
STATE 2026-09-25T22:53:13Z: resolution_profile.py and compiler_phase_1.py read whole; phase_01.md exists as
PARTIAL. Resume by reading spell_requirements_finder.py 1-500, 501-1000, 1001-1333 and
spell_requirements.py, then finish phase_01.md (Holds, Reflection points, World reads).
STATE 2026-09-26T00:08:30Z: finder trio read whole; phase_01.md COMPLETE (166 lines). Resume at step 4:
`wc -l` compiler_phase_2.py and the symbolic_graph package, read phase 2 whole plus delegates to the
crossing types, write phase_02.md with the full Record Shape.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
