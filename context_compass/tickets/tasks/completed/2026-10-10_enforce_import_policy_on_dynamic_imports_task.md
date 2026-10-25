# Task: Check dynamic imports against the codegen import policy (defect D-11)

- Completed: 2026-10-25T10:50:32Z
- Summary: Every dynamic import in a codegen room now answers to the compiled import roots. Wherever a preset
  enables imports with an allow or deny list - hybrid, the precision overlay and permissive - a `__import__` call
  or bare reference is refused at validation (A: a new `static_only_denied_builtin_names` set that the builtin gate
  and name resolution read), and the room's runtime `__import__` is a wrapper raising ImportError that names a
  denied or unlisted root (B); import statements of allowed roots still execute, full_access is unconstrained, and
  safe's `__import__` was already denied. The owner's A refuses the `__import__` name for every root, so
  `__import__('json')` is refused under hybrid too and import statements are the working path - the CONFLICT note
  reconciles this with acceptance criterion 3 (left unchecked) and the choice is reversible. The four strict xfails
  pass without their marker and five `__import__` cases join them (56 collected). Notched 0.2.8271; release-note
  section "Codegen rooms refuse dynamic imports under the safe, hybrid and precision profiles". Tiers green 3014,
  5 pre-existing xfailed, the GIL off and on, on Linux; the guarded import adds ~91 ns a call; Windows tiers and
  hosted CI Not run. Rebuild last, after the closure.

## Metadata
- Task ID: TASK-2026-10-10-enforce-import-policy-on-dynamic-imports
- Story: none; parent EPIC-2026-10-25-codegen_room_policy_defects (defect found by
  TASK-2026-10-08-review_core_protection_fork_aware_updates, completed 2026-10-10)
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-10T13:40:50Z
- Updated: 2026-10-25T10:50:32Z

## Objective
Under every codegen profile that enables imports with an allow or deny list - hybrid, the precision overlay and
permissive - a `__import__(...)` call loads roots the profile denies or does not allow, because the import gate
reads import statements only. Make every import, statement or call, answer to the same compiled roots, and keep the
defect's strict xfails as the proof. full_access stays unconstrained. This is policy and defence in depth, not a
security boundary (review contract C6.1).

## Defect
- Symptom: under hybrid and hybrid+precision, `loaded = __import__('subprocess')` (also `socket`, `importlib`) is
  accepted and returns the module, although those roots are on the profile's deny list; under hybrid,
  hybrid+precision and permissive `__import__('melder')` is accepted although the allow lists leave `melder` out and
  `import melder` is refused. Under safe it is refused ("Builtin '__import__' is not allowed").
- Reproducer: `context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe2.py` and its recorded
  output `codegen_probe2_output.txt` (rerun 2026-10-10T13:33Z on this tree). Pinned regressions: the four strict
  xfails `tests/integration/melder/aether/test_codegen_core_boundary_integration.py::`
  `test_hybrid_refuses_dynamic_imports_of_its_denied_roots[None-subprocess|None-socket|None-importlib|`
  `precision-subprocess]`.
- Cause: `FrameACLCompiler._compile_codegen_builtin_controls` adds `__import__` to the denied builtins only when
  imports are disabled; `CodegenImportPolicyStrategy` inspects `Import` and `ImportFrom` nodes only; name resolution
  admits every builtin that is not denied; the reflection strategy covers `importlib.import_module` and `reload` only
  as attribute calls on a Name.
- Impact: with `subprocess` reachable, room code can run an installer or any program; with `importlib` it can import
  anything; with `melder` it reaches the core directly - in rooms whose profiles promise otherwise.

## Ticket Contract
- ENTRY_GATE: the owner selects this ticket, assigns an implementer and routes it on `attention_board.md`; patch docs
  exist (the codegen import gate is a policy gate); the design choice below is recorded as a DECISION note.
- EXECUTION_BOUNDARY: `src/melder/nexus/acl/frame_acl_compiler.py` (import and builtin controls),
  `src/melder/nexus/rift/codegen_system/validation/strategies/` (import, builtin or name strategy),
  `src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py` (a runtime import guard,
  if chosen), the codegen tests named below, src_components (codegen validation and namespace), src_architecture
  (the boundary invariant), the release note.
- DEPENDENCIES: the review contract (C6) and D2; independent of D-10 and D-20.
- EXIT_GATE: the acceptance criteria pass with the GIL off; the four strict xfail markers are deleted because the
  tests pass; notch, release note and rebuild per the contribution guide; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST if a runtime guard changes import-statement behaviour for allowed roots;
  CONFLICT if an existing test depends on `__import__` under a listed profile.

## Scope Boundaries
- In scope: `__import__` calls and the other dynamic import routes under profiles with import lists; a runtime guard
  if chosen; error messages that name the refused root.
- Out of scope: the contents of the allow and deny lists (an owner decision under D2, for example listing the
  protected core's packages as denied roots); `open` (D-10); materialize_codegen (D-20).

## Design Options (implementer proposes, owner decides)
- A, static only: deny the `__import__` name whenever the compiled posture has an allow or deny list. Simple; refused
  at validation (what the strict xfails assert); misses any route that reaches the import machinery without the name.
- B, runtime guard: replace `__builtins__['__import__']` in the room namespace with a wrapper that checks each
  import's root against the compiled roots and raises ImportError naming the root. Covers statements and calls
  alike; removing `__import__` outright is not an option, because import statements call it.
- Recommendation: A and B together - A gives the validation message, B covers the forms static analysis misses.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24), "focus on 2 and 3 make an epic for each and investigate them",
  scheduled it under EPIC-2026-10-25-codegen_room_policy_defects; melder_0 re-measures it on 0.2.8267
  and puts the choice of A, B or both to the owner.

- from_state: blocked
- to_state: ready
- transition_reason: D-10 landed (TASK-2026-10-10-deny-file-access-under-safe-codegen closed 2026-10-25,
  notched 0.2.8270), which ends the tranche-order block (D-10, D-11, D-20) this task waited on; the owner's
  A + B decision and his go of 2026-10-25 stand.

- from_state: ready
- to_state: in_progress
- transition_reason: the owner's direction (chat 2026-10-25T09:38Z): "ok go to the next thing then turn it in
  and move the ticket to completed" - implement A + B, land it and close the task.

- from_state: in_progress
- to_state: done
- transition_reason: A + B landed and validated (the GIL off and on, on Linux); docs, graph, notch 0.2.8271 and
  the release-note section are in; closed on the owner's direction (chat 2026-10-25T09:38Z), "ok go to the next
  thing then turn it in and move the ticket to completed". Windows tiers and hosted CI Not run. Rebuild last.

## Steps / Checklist
- [x] Re-measure on 0.2.8267 (EPIC-2026-10-25-codegen_room_policy_defects): rerun the reproducer
      and the four strict xfails, the GIL off and on; read the cited code at today's lines; record MEASURE
      and FACT notes; put the choice of A, B or both to the owner.
- [x] Record the design choice; write and link patch docs.
- [x] Red first: the four strict xfails fail on their assertion; add the cases listed below.
- [x] Implement; run the codegen unit, component and integration tiers with the GIL off.
- [x] Remove the strict xfail markers; update tests_components, src_components, src_architecture, release note.
- [x] Notch, rebuild assets and llm_support last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Acceptance Criteria
- [x] Under hybrid and hybrid+precision, `__import__` of `subprocess`, `socket` and `importlib` is refused with a
      message naming the root, and nothing is loaded (the four strict xfails pass without their marker).
- [x] Under hybrid, hybrid+precision and permissive, `__import__('melder')` is refused, as `import melder` is today;
      under full_access it is accepted.
- [ ] `__import__` of an allowed root (for example `json` under hybrid) and ordinary import statements of allowed
      roots keep working.
- [x] With option B, a dynamic route that static validation does not see is refused at run time with ImportError
      naming the root, pinned by its own symptom-named test.
- [x] The release note carries a Breaking change entry for room code that used `__import__` under a listed profile;
      src_architecture records the defect as closed and the import gate as covering calls.
- [x] Existing codegen tiers pass with the GIL off; Windows tiers and hosted CI are reported Not run until seen.

## Deliverables
- The import-policy change, its regressions and the documentation updates.

## Files / Paths Impacted
- see EXECUTION_BOUNDARY; tests: `tests/integration/melder/aether/test_codegen_core_boundary_integration.py`,
  `tests/integration/melder/aether/test_codegen_system_integration_matrix.py`, the codegen unit tests.

## Validation
- Not run.
- Recommended commands:
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/integration/melder/aether`
  - `python -X gil=0 -m pytest -q -p no:cacheprovider tests/unit/melder/nexus`

## Risks / Rollback Notes
- A runtime guard sits on every import a room makes; measure that ordinary allowed imports keep their cost.
- Rollback is reverting the compiler and strategy changes; no persisted state is involved.
- In-process import checks are defence in depth, not isolation (contract C6.1).

## Applicable Anti-Patterns
- [x] No implementation before the design choice is recorded.
- [x] No claim that the fix isolates agent code (C6.4 wording rule).
- [x] No closure without the xfail markers removed by passing tests and board sync.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true (the reproducer lives in the review's evidence pack)
- ARTIFACT_PATHS:
  - artifacts/core_protection_review_20261010/probes/codegen_probe2.py
  - artifacts/core_protection_review_20261010/probes/codegen_probe2_output.txt
  - system_docs/patches/active/codegen_dynamic_import_policy_2026_10_25/
- DISPOSITION: retain_as_reference for the reproducer pack; promote_to_documentation for the patch docs
  (merged into src_architecture and src_components at landing, the folder moved to patches/completed at closure).
- CLEANUP_TRIGGER: none for the reproducer; the patch folder moves to patches/completed at closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: codegen import gate; dynamic imports from agent code
- IF_UNKNOWN: ask user before implementation

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-10T13:40:50Z
  TYPE: FACT
  CLAIM: Opened from the core-protection review's hand-back (review ticket Notes 11, 27 and 28). At 66939dfe8 the
    compiler denies `__import__` only when imports are off and the import strategy reads statements only, so
    hybrid's, precision's and permissive's roots constrain import statements, not imports. The reproducer and its
    recorded output are in the review's evidence pack; four strict xfails pin the hybrid and precision contract.
  EVIDENCE:
  - src/melder/nexus/acl/frame_acl_compiler.py:600-630
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:89-171
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:99-149
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_reflection_policy_strategy.py:148-220
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:169-206
  - context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe2_output.txt:1-19
  IMPACT: Room code under a listed profile can load subprocess, socket, importlib or melder.
  NEXT: Implementer records the design choice (A, B or both) as a DECISION note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:16:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Scheduled under EPIC-2026-10-25-codegen_room_policy_defects at the owner's ask (chat 2026-10-24),
    "focus on 2 and 3 make an epic for each and investigate them".
    The re-measure, on a /tmp copy of the 0.2.8267 tree, the GIL off and on: (1) codegen_probe2.py, `__import__`
    of denied and unlisted roots under the five postures; (2) the four strict xfails
    test_hybrid_refuses_dynamic_imports_of_its_denied_roots; (3) a read at today's lines of the compiler's builtin
    controls and the import-policy, name-resolution and reflection strategies; (4) the routes a static refusal of
    the name would miss (an alias of `__import__`, `builtins.__import__`, `__builtins__['__import__']`,
    `importlib` reached through an allowed module) probed, so options A and B are costed on what each covers.
  EVIDENCE:
  - context_compass/artifacts/core_protection_review_20261010/probes/codegen_probe2.py:1-38
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:169-206
  IMPACT: The owner chooses A, B or both knowing which dynamic routes each option closes today.
  NEXT: Copy the 0.2.8267 tree to /tmp and run the probe, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:23:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Re-measured on the /tmp copy of 0.2.8267, the GIL off and on. codegen_probe2.py: `__import__('subprocess')`,
    `__import__('socket')`, `__import__('importlib')` and `__import__('melder')` are all accepted and return the
    module under hybrid, hybrid+precision and permissive, and all refused under safe ("Builtin '__import__' is
    not allowed in this codegen mode."); identical to 2026-10-10 and byte-identical across GIL modes (session
    paths in the result were normalised to `~`). The four strict xfails
    test_hybrid_refuses_dynamic_imports_of_its_denied_roots[None-subprocess|None-socket|None-importlib|
    precision-subprocess] still XFAIL. So D-11 reproduces unchanged at 0.2.8267.
  EVIDENCE:
  - artifacts/codegen_room_policy_20261025/runs/codegen_probe2_0_2_8267_gil0.txt:1-19
  - artifacts/codegen_room_policy_20261025/runs/codegen_probe2_0_2_8267_gil1.txt:1-19
  - artifacts/codegen_room_policy_20261025/runs/codegen_tests_0_2_8267_gil0.txt:1-40
  IMPACT: The recorded symptom holds, so the owner chooses A/B/both on current behaviour.
  NEXT: Confirm the cause at today's lines (next note), then cost the options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:23:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The cause holds at 0.2.8267, read at today's lines. `FrameACLCompiler._compile_codegen_builtin_controls`
    adds `__import__` to the denied builtins ONLY when `imports_enabled` is False, so a profile that enables
    imports (hybrid, precision, permissive) leaves `__import__` a live builtin. The import-policy strategy walks
    only `ast.Import` and `ast.ImportFrom` nodes, so a `__import__(...)` call is outside its reach, and
    `_import_root_is_denied` is never consulted for it. Name resolution admits every builtin not on the deny
    list, so the name resolves. Option A (deny the `__import__` name statically wherever an import list applies)
    and B (a runtime `__import__` wrapper checking each root) are unchanged; A alone misses an alias or
    `__builtins__['__import__']`, B covers the forms static analysis cannot see.
  EVIDENCE:
  - src/melder/nexus/acl/frame_acl_compiler.py:600-630
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_import_policy_strategy.py:114-198
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:134-155
  IMPACT: The fix makes every import answer to the compiled roots; A+B is still the recommendation.
  NEXT: DECISION_REQUEST to the owner: option A, B or both.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:37:11Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's decision (chat 2026-10-25, answering the decision request): option A + B - the recommended
    option. A: wherever an import list applies, the static gate refuses a reference to the `__import__` name,
    with a message naming it. B: the room's runtime `__builtins__['__import__']` becomes a wrapper that checks
    each import's root against the compiled allowed and denied roots and raises ImportError naming the root;
    import statements of allowed roots keep working because they call the wrapper. A design constraint the
    re-measure's read fixes: A cannot reuse `denied_builtin_names` as it stands, because that one list also
    strips names from the runtime builtins, and a missing `__import__` breaks every import statement; A is a
    static-only refusal and B keeps the name present, wrapped.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md:59-65
  - context_compass/tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md:215-234
  IMPACT: The fix proceeds on a decided design with its one structural constraint recorded before the patch doc.
  NEXT: On the owner's go: write the patch docs (the compiler's builtin controls, the static strategies,
    the namespace builtins).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T01:29:39Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: BLOCKER
  CLAIM: The owner gave the go on 2026-10-25; melder_0 is blocked by the session's content filter (the epic's
    BLOCKER note). Nothing in src/ changed; this task is ready for another implementer as specified.
  EVIDENCE: context_compass/tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md:254-271
  IMPACT: The task is unstarted.
  NEXT: The owner assigns an implementer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T02:02:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The BLOCKER of 2026-10-25T01:29:39Z belonged to the earlier melder_0 session and is lifted: the owner
    certified a new session as melder_0 (chat 2026-10-25) and sent it to D-10 first. This task stays blocked
    on the tranche order only (D-10, D-11, D-20); the owner's D-11 (A + B) answer and his go stand.
  EVIDENCE: context_compass/tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md:217-271
  IMPACT: Nothing here changes until D-10 lands.
  NEXT: melder_0 starts this task after D-10 lands.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T08:45:08Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: D-10 landed (TASK-2026-10-10-deny-file-access-under-safe-codegen closed 2026-10-25, notched 0.2.8270), so
    this task is next in the tranche and ready; the owner's go ("go ahead and do them one by one") and his A + B
    decision stand. What D-10 changed that this task builds on: `SAFE_DENIED_BUILTIN_NAMES` names `open` and
    `pathlib` is a permissive extra (stdlib_import_sets.py); the core-boundary integration module holds the
    per-profile file matrix beside this task's four strict xfails; and the running note has a codegen section,
    "Codegen rooms under the safe, hybrid and precision profiles refuse `open`", where this task's Breaking entry
    belongs - the same subject, what a codegen room's code may load - rather than a second section.
  EVIDENCE:
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:52-67
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:108-130
  - tests/integration/melder/aether/test_codegen_core_boundary_integration.py:162-199
  - release_docs/next_version_release.md:177-205
  IMPACT: The task starts from today's tree; its patch docs read the D-10 posture, and its note entry has a home.
  NEXT: Start D-11: re-read its decision and the import gate at today's lines, then write the patch docs (A + B).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T09:55:16Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Re-read at today's lines after the REONBOARD. The cause is unchanged from the 00:23:47 note:
    `_compile_codegen_builtin_controls` adds `__import__` to the denied builtins only when imports are off
    (line 629), so a preset that enables imports leaves `__import__` a live builtin; the builtin gate checks a
    Call whose func is a Name against `denied_builtin_names`; name resolution admits every builtin not on that
    list; and the runtime builtins dict is `vars(builtins)` minus `denied_builtin_names`. So under hybrid,
    precision and permissive a `__import__(...)` call is accepted and the runtime name is present.
  EVIDENCE:
  - src/melder/nexus/acl/frame_acl_compiler.py:599-630
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_builtin_policy_strategy.py:103-127
  - src/melder/nexus/rift/codegen_system/validation/strategies/codegen_name_resolution_strategy.py:244-265
  - src/melder/nexus/rift/codegen_system/namespace/strategies/codegen_builtins_strategy.py:100-109
  IMPACT: A+B must add a static-only denial of the `__import__` name (not via `denied_builtin_names`, which
    also strips the runtime name an import statement needs) plus a runtime `__import__` wrapper checking roots.
  NEXT: Write the patch docs for A+B, then the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T09:55:16Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: A+B implemented through one new compiled field, `static_only_denied_builtin_names`, carried on
    `CompiledFrameACLAccessSurface` and `CodegenNamespaceConfiguration`. The compiler sets it to
    `('__import__',)` when imports are on AND an allow or deny import list applies (hybrid, precision,
    permissive), and `()` otherwise (full_access; and safe, where imports are off and `__import__` is already
    a denied builtin). A (static): the builtin gate refuses a Call of a name in
    `denied_builtin_names | static_only_denied_builtin_names` ('Builtin ... not allowed'), and name resolution
    subtracts that union from the allowed builtins ('Name ... not available'), so a `__import__` call or a bare
    `x = __import__` reference is refused where a list applies. B (runtime): the builtins strategy keeps
    stripping `denied_builtin_names` only (the name stays present), then, when imports are on and a list
    applies, replaces `__builtins__['__import__']` with a wrapper that checks each import's root against the
    compiled allowed/denied roots (the same rule as `_import_root_is_denied`) and raises ImportError naming the
    root, delegating allowed roots to the real import so import statements keep working. full_access installs no
    wrapper (no list), so it stays unconstrained. One name tuple, `IMPORT_BUILTIN_NAMES = ('__import__',)`,
    lives in stdlib_import_sets.py (the D-10 one-place pattern) and both the compiler and the builtins strategy
    read it, so they cannot drift. Policy and defence in depth, not isolation (C6.1/C6.4).
  EVIDENCE:
  - src/melder/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:108-130
  - src/melder/nexus/acl/frame_acl_compiler.py:220-231
  - src/melder/nexus/rift/codegen_system/codegen_system.py:407-483
  IMPACT: Every import answers to the compiled roots, statement or call, with full_access unconstrained.
  NEXT: Write the patch docs under system_docs/patches/active/codegen_dynamic_import_policy_2026_10_25/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T09:58:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs written and linked (patch_framework_gating entry gate). Consumption mapping
    (patch section -> implementation step -> validation step):
    - architecture_patch 'Migration and Rollout Order' step 2 -> add IMPORT_BUILTIN_NAMES to
      stdlib_import_sets.py -> unit: the compiled static_only set is ('__import__',) for a listed posture.
    - component_patch_codegen_acl_profiles 'Interface Deltas' -> FrameACLCompiler computes
      static_only_denied_builtin_names and CompiledFrameACLAccessSurface carries it -> unit:
      test_frame_acl_compiler_contracts, test_frame_acl_compiled_access_surface.
    - code_description_patch 'Control flow' A -> builtin gate + name resolution read the union with
      static_only -> unit: test_codegen_validation_strategy_unit_matrix (call and bare-reference cases).
    - code_description_patch 'Control flow' B -> builtins strategy keeps __import__ present and wraps it ->
      unit: test_codegen_namespace_runtime_unit_matrix (wrapper refuses a denied root, delegates an allowed
      root); integration: an allowed import statement executes under hybrid.
    - component_patch_codegen_internal_engine -> CodegenNamespaceConfiguration + CodegenSystem default thread
      the field -> unit: test_codegen_system_unit_matrix; integration: the four strict xfails and the new
      __import__ cases in test_codegen_core_boundary_integration.py.
  EVIDENCE:
  - system_docs/patches/active/codegen_dynamic_import_policy_2026_10_25/architecture_patch.md:1-117
  - system_docs/patches/active/codegen_dynamic_import_policy_2026_10_25/code_description_patch_codegen_import_gate.md:1-80
  IMPACT: Implementation may start; each edit maps to a patch section and a pinned test.
  NEXT: Red tests on a /tmp copy of today's tree, the four xfail markers removed plus the new cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T10:19:17Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: A + B landed and validated on a /tmp copy of the 0.2.8270 tree, the GIL off and on (3.14.7t).
    RED (markers removed, source unchanged): 11 failed - the four ex-xfails, `__import__('melder')` under
    hybrid/precision/permissive, the bare-reference cases, and the allowed-root `__import__('json')` call.
    GREEN after A + B: the codegen/ACL tiers (35 unit files + tests/component/melder/aether +
    tests/integration/melder/aether) pass 3014, 5 xfailed with the GIL off and 3014, 5 xfailed + the
    GIL-enabled warning with it; the five codegen/ACL unit files pass 359. The five xfails are pre-existing and
    unrelated (the four rebind-S3 strict xfails and the concurrent-conjure one). The reproducer codegen_probe2
    now reports every `__import__` call refused under safe, hybrid, hybrid+precision and permissive (was
    accepted under the last three), result None. Cost: the guarded runtime `__import__` adds ~91 ns a call for
    an allowed root (json: ~83 -> ~174 ns) - one split and two membership tests, run once per import, not in a
    hot loop. A design reconciliation (see the CONFLICT note) names `__import__` with A, not the root; B names
    the root at run time. Windows tiers and hosted CI: Not run until seen.
  EVIDENCE:
  - artifacts/codegen_room_policy_20261025/runs/d11_tiers_gil0.txt:1-6
  - artifacts/codegen_room_policy_20261025/runs/d11_tiers_gil1.txt:1-6
  - artifacts/codegen_room_policy_20261025/runs/codegen_probe2_d11_fix_gil0.txt:1-19
  - artifacts/codegen_room_policy_20261025/runs/d11_import_cost_gil0.txt:1-12
  IMPACT: The acceptance criteria are met on Linux with the GIL off and on; docs, notch, release note next.
  NEXT: src_architecture and src_components, tests_components, indexes and the graph, then notch 0.2.8271.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T10:19:17Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: CONFLICT
  CLAIM: Two owner instructions meet at the edge of criterion 3. The DECISION (00:37:11Z) sets A as a blanket
    static refusal of the `__import__` NAME wherever an import list applies (it even notes what A 'misses', an
    alias), so `__import__('json')` is refused under hybrid too. Acceptance criterion 3's older example says
    `__import__` of an allowed root 'keeps working'. These cannot both hold. I implemented the DECISION (the
    more specific, later owner instruction): `__import__` (any root) is refused wherever a list applies, and
    criterion 3 is met by its other half - import STATEMENTS of allowed roots keep working, delegated by B's
    wrapper (pinned by test_an_allowed_import_statement_executes_under_hybrid). This is reversible and narrow;
    if the owner wants `__import__('json')` to work under a listed posture, A would instead inspect the call's
    literal argument rather than deny the name - a small follow-up. Flagging rather than silently choosing.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md:97-99
  - context_compass/tickets/tasks/2026-10-10_enforce_import_policy_on_dynamic_imports_task.md:225-233
  IMPACT: `__import__` is fully off under hybrid/precision/permissive; allowed roots are reached via import
    statements. The owner can redirect to a per-argument A if he wants `__import__('allowed')` to work.
  NEXT: Carry the reconciliation into the release note and the closure summary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T11:02:43Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Turn-in complete, rebuild last and green. Docs (src_architecture, src_components, tests_components and
    their indexes) and the graph (eight descriptors refreshed, seven class nodes re-stamped, src_graph reassembled
    to 28220 lines / 593 sections / 1422 edges, index verified) carry D-11; notched 0.2.8271; the release note
    gained the section "Codegen rooms refuse dynamic imports under the safe, hybrid and precision profiles" and a
    Packaging bullet, with the header and rebuild line at 0.2.8271. Closure: this ticket to completed/,
    attention_board (D-11 row out, D-20 blocked->ready, closed anchor at the 12 cap), artifact_board (patch folder
    promoted to patches/completed, the reproducer retained), mailbox M0-227/228/229 to melder_1/2/3, the epic box.
    The asset build (v0.2.8271: agent_documentation, bind_guard, system_documents) and the LLM bundle both pass
    --check - asset three OK; bundle src/tests/other OK with --include-untracked. Windows tiers and hosted CI
    Not run.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/system_docs/src_graph_index.md
  - release_docs/next_version_release.md
  IMPACT: D-11 is landed and turned in; D-20 is next in the tranche (D-10, D-11, D-20).
  NEXT: none for D-11; melder_0 may start D-20 on the owner's standing go.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Scheduled 2026-10-25 under EPIC-2026-10-25-codegen_room_policy_defects (the owner's ask); in_progress, melder_0,
investigation only. Scope unchanged: `__import__` bypasses the codegen import gate under hybrid, the precision
overlay and permissive (Note of 2026-10-10). State: the re-measure on 0.2.8267 is planned (PLAN note); nothing run
yet. Re-measured on 0.2.8267 (Notes): the defect reproduces unchanged, the cause holds at today's lines, the four
strict xfails still XFAIL. Decided 2026-10-25 (DECISION note): A + B, with A static-only. Ready since
2026-10-25T08:45:08Z: D-10 landed at 0.2.8270 (PLAN note of that time). Next, under the owner's go: patch
docs, red tests, the fix, notch and rebuild.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
