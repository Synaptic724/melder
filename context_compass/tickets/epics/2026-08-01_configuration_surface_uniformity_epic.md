# Epic: Configuration surface uniformity - one shape for every config in the repo

## Metadata
- Epic ID: EPIC-2026-08-01-configuration-surface-uniformity
- Status: in_progress
- Owner: cowork
- Agent Name: examples_0
- Priority: p1
- Created: 2026-08-01T13:32:00Z
- Updated: 2026-08-01T13:32:00Z

## Objective
Make every configuration object in `src/melder` share ONE structure: one storage
model, one lifecycle vocabulary, one fluent authoring surface. Today there are
three storage models and an inconsistent verb set across 19 files and ~14,300 LOC.

## Problem / Opportunity
The owner's read is correct and the survey confirms it: the configs are NOT
uniform. They diverge at the most fundamental level - how a value is stored - and
that divergence has already produced at least one shipped defect (the
`with_defaults()` docstring describing frame-config semantics on the spellbook
config, which sent four tier examples into a refusal).

A user or agent who learns one config does not know the next one.

## Context (why now)
The UX/AIX tiers are the evidence lane for the public surface, and the config
lesson block (intermediate 19, 30-35) is where users meet these objects. Four of
the seven harness reds this session were config-shaped. Uniformity here is not
tidying - it is removing a class of user-facing trap.

## MRP Alignment
MRP: the config surface is foundational and public. Getting it coherent before more
surface accretes is exactly the "right the first time" bar; patching each config
individually is the trap MRP refuses.

## Ticket Contract
- ENTRY_GATE: full structural survey of all 19 config files with evidence. The
  first pass is DONE and recorded below; the ACL/codegen family remains.
- EXECUTION_BOUNDARY: survey and DESIGN ONLY until the owner rules the target
  shape. No config file is edited under this epic without that ruling plus patch
  docs - this is public API across nine user-facing objects.
- DEPENDENCIES: owner ruling on the target shape (see the DECISION_REQUEST note).
- EXIT_GATE: every config shares one storage model, one lifecycle verb set, and a
  fluent surface that mypy can see; canonical docs updated; harness green.
- FAILURE_ESCALATION: BLOCKER on anything that would require `type: ignore`,
  `# noqa`, or widening to `Any` - all three are banned by repo policy.

## Goals
- One storage model for every config.
- One lifecycle vocabulary (validate / freeze / finalize / activate / cleanup).
- Fluent `with_*` authoring on every config, uniformly.
- No hand-maintained per-config boilerplate that can drift.

## Non-goals
- Changing what any individual knob DOES.
- Touching `generalized_singleton_specialization_enabled` - internal, owner-only,
  hands off (ruled 2026-08-01).
- Redesigning the ACL chain/versioning model.

## Requirements
- Functional: uniform structure and verbs across all configs.
- Non-functional: MUST satisfy `mypy strict = true` with zero suppressions. MUST
  NOT introduce `__getattr__`/`__setattr__` dispatch - no config uses it today and
  the repo bans defensive introspection in owned code.

## Acceptance Criteria
- [ ] Owner has ruled the target shape.
- [ ] Every config uses the ruled storage model.
- [ ] Every config exposes the ruled lifecycle verbs, or documents why it is exempt.
- [ ] `mypy strict` passes with zero new suppressions.
- [ ] The `with_defaults()` prose defect is resolved as part of the uniform shape.

## Risks / Mitigations
- RISK: this is public API across nine user-facing objects; a wide sweep can break
  users silently. MITIGATION: patch docs first, one family per tranche, harness as
  the canary.
- RISK: uniformity pressure erases a divergence that was deliberate. MITIGATION:
  every divergence found must be classified INTENTIONAL or ACCIDENTAL before it is
  normalized away - see the survey task.

## Child Tasks
- TASK-2026-08-01-config-structural-survey - finish the survey (ACL/codegen family)
  and classify every divergence intentional vs accidental.

## Noting Behavior
- Epic notes: program direction, cross-task tradeoffs, tranche order.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Notes

- DATETIME: 2026-08-01T13:32:00Z
  TYPE: FACT
  CLAIM: SURVEY PASS 1 - the configs are NOT uniform, and they diverge at the
    storage layer, which is the deepest place they could. THREE STORAGE MODELS:
    (1) `_properties` dict PLUS an `available_properties` type registry -
    spellbook, crystallizer, mutation, nexus, rift.
    (2) `_properties` dict with NO registry - aether_configuration (18 `_properties`
    references, ZERO `available_properties`). A third thing, not either camp.
    (3) Private slots, no dict, no registry at all - aetheric_frame_configuration
    (2009 LOC, the largest config in the repo), nexus_frame_configuration,
    external_persistence_manager_configuration.
    LIFECYCLE VERBS ARE INCONSISTENT: `finalize()` exists on 6 of 9, `activate()`
    on only 3 (aether, crystallizer, mutation), `validate()`/`freeze()` on 8 of 9,
    and a recorded-reload lane on 6 of 9. `nexus_frame_configuration` has NONE of
    them - it is a data carrier wearing the "configuration" name.
    FLUENT SURFACE IS WILDLY UNEVEN: nexus 26 `with_*` methods, frame 15, epm 10,
    spellbook 7, crystallizer 6, rift 5, aether 4, mutation 3, nexus_frame 0.
    `_idempotent_keys` EXISTS ON EXACTLY ONE CONFIG - spellbook. The set-once
    concept that caused four harness reds this session is a one-off that no other
    config shares.
  EVIDENCE:
    - src/melder/aether/spellbook/configuration/spellbook_configuration.py
    - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py
    - src/melder/aether/aether_configuration.py
    - src/melder/nexus/configuration/nexus_configuration.py
  IMPACT: This is the mechanical root of the docstring defect found earlier today.
    Two classes carry a `with_defaults()` verb with OPPOSITE semantics (frame's is
    destructive/recomputing, spellbook's preserves), and the spellbook one is
    documented as if it were the frame one. Non-uniformity is already shipping
    wrong prose into user-facing docstrings.
  NEXT: Establish the constraint that bounds the target shape BEFORE proposing one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T13:32:00Z
  TYPE: FACT
  CLAIM: THE CONSTRAINING INVARIANT, established BEFORE any recommendation this
    time. The owner's proposal is "dynamically add setters from the module itself,
    then instance the class for that module". Three repo rules bound it:
    (1) `pyproject.toml` sets `[tool.mypy] strict = true`, and the comment directly
    above it states widening is disallowed by policy "so the checker is configured
    strictly". A setter attached at RUNTIME is invisible to mypy - every
    `config.with_disposal(True)` call site becomes an `attr-defined` error.
    (2) The three escape hatches are ALL banned by the synaptic profile:
    `type: ignore`, `# noqa`, and widening a truthful type to `Any`. So the normal
    way people make dynamic attributes typecheck is unavailable here.
    (3) ZERO configs in the repo currently use `__getattr__` or `__setattr__`. The
    dynamic-dispatch pattern is unprecedented in this codebase, and the profile
    additionally bans defensive introspection in owned code.
  EVIDENCE:
    - pyproject.toml:224-228
    - agent_onboarding/user_defined/synaptic_python_developer/skills/python/banned_patterns.md:56-77
    - src/melder (zero `__getattr__`/`__setattr__` in any *configuration*.py)
  IMPACT: The uniformity goal is sound and overdue. The RUNTIME-dynamic mechanism
    for reaching it collides head-on with three standing rules the owner set.
  NEXT: Propose the shape that keeps the idea and survives the constraints.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-01T13:32:00Z
  TYPE: DECISION_REQUEST
  CLAIM: The owner's idea works if the generation moves from RUNTIME to BUILD TIME,
    and this repo already does exactly that three times over.
    SHAPE 1 - SCHEMA + GENERATED TYPED SETTERS (recommended). Each module declares
    its knobs once as a schema (name, type, default, idempotent yes/no). One shared
    base class owns the storage and the whole lifecycle - validate, freeze,
    finalize, activate, cleanup, recorded-reload - so those stop being reimplemented
    nine times. The fluent `with_*` methods are GENERATED AT BUILD TIME into a
    committed, fully typed file, exactly like `_build_assets/_bind_guard/manifest/`,
    `_agent_documentation/`, and `_system_documents/` already are. Result: one
    declaration per module, uniform surface, zero hand-written boilerplate to drift,
    and mypy sees every setter because the file is real committed Python. This IS
    the owner's proposal - "add the setters from the module itself" - with the
    generation step moved to where the type checker can follow it.
    SHAPE 2 - SHARED BASE, HAND-WRITTEN SETTERS. Same base class and lifecycle, but
    each config keeps explicit `with_*` methods written by hand. Uniform structure,
    no codegen machinery, but the per-config boilerplate stays and can drift.
    SHAPE 3 - RUNTIME DYNAMIC, as literally proposed. Rejected unless the owner
    relaxes the mypy/suppression rules, because it cannot typecheck under the
    current policy without a banned escape hatch.
    I recommend SHAPE 1, and the reason is precedent rather than taste: the repo
    has already solved "generate a typed thing at build time and commit it" three
    times, with a runner (`_build_asset_runner.py`) and a `--check` discipline.
  EVIDENCE:
    - src/melder/_build_assets/_build_asset_runner.py
    - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py
    - pyproject.toml:224-228
  IMPACT: SHAPE 1 also dissolves the two defects found earlier today for free: the
    `with_defaults()` prose defect disappears when the verb is generated from one
    schema, and `_idempotent_keys` stops being a spellbook-only special case.
  NEXT: OWNER RULING on the shape. No config edited until then.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Survey pass 1 done across 9 root configs: three storage models, inconsistent
lifecycle verbs, fluent surfaces from 0 to 26 methods, and a set-once concept
living on exactly one config. The uniformity goal is right. The runtime-dynamic
mechanism collides with `mypy strict`, the suppression bans, and the absence of any
`__getattr__` precedent - so the recommendation is the same idea generated at BUILD
time into committed typed files, matching the `_build_assets` pattern already in
the repo. Nothing edited. Blocked on the shape ruling.
