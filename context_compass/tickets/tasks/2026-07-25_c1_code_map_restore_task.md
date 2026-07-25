

# Task: Rebuild the src_components.md C1 Code Map as a full package inventory

## Metadata
- Task ID: TASK-2026-07-25-c1-code-map-restore
- Story: STORY-2026-07-25-guard-manifest-truth
- Status: ready
- Owner: melder_1
- Agent Name: melder_1
- Priority: p2
- Created: 2026-07-25T18:19:28Z
- Updated: 2026-07-25T18:19:28Z

## Objective
Replace the two-entry truncation stub at `src_components.md:3714` with a complete,
filesystem-verified C1 inventory of the `src/melder` package.

## Ticket Contract
- ENTRY_GATE: story routed on `attention_board.md`; owner ruling recorded choosing
  full package inventory over an architecture-map mirror.
- EXECUTION_BOUNDARY: the `## C1 Code Map (Core)` section of
  `system_docs/src_components.md`. No other section, no other file.
- DEPENDENCIES: none blocking; independent of the guard-truth task.
- EXIT_GATE: every listed path exists on disk; no truncation note remains standing in
  for content; section heading matches its new scope.
- FAILURE_ESCALATION: DECISION_REQUEST if inventory size makes the section unusable and
  a grouped/summarized form is preferable.

## Scope Boundaries
- In scope: enumerating package modules with a one-line purpose each, grouped by
  subsystem, generated from a filesystem walk.
- Out of scope: the `src_architecture.md` C1 map (already current at :1500-1646);
  test-tree inventory; regenerating any graph artifact.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner selected full package inventory; source of truth is the
  filesystem, which is directly readable, so no unknowns block the work.

## Steps / Checklist
- [ ] Walk `src/melder` and capture the module inventory programmatically.
- [ ] Group by subsystem boundary (root, aether, spellbook, conduit, dev_ops, nexus,
      crystallizer, mutation_research, utilities, cache).
- [ ] Write one accurate purpose line per module; mark anything unverified `UNKNOWN`
      rather than guessing from the filename.
- [ ] Reconcile against `src_architecture.md:1500-1646` so the two maps do not
      contradict each other.
- [ ] Replace the section body; remove the 2026-07-07 truncation note only once real
      content stands in its place, and preserve the historical fact that a truncation
      occurred.
- [ ] Update the section heading if "Core" no longer describes the scope.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A complete, verified C1 Code Map section in `src_components.md`.

## Files / Paths Impacted
- context_compass/system_docs/src_components.md

## Validation
- Not run.
- Recommended commands:
  - path-existence check of every listed file against `src/melder`
  - `rg -n "TAIL REPAIR" context_compass/system_docs/src_components.md`

## Risks / Rollback Notes
- RISK: a full inventory is the fastest-drifting doc section in the repo. Mitigation:
  produce it from a walk so it can be regenerated rather than hand-maintained.
- Rollback: git revert of the single file.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No path listed that was not filesystem-verified.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >= 7)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: FACT
  CLAIM: The section currently holds two entries plus a 2026-07-07 tail-repair note
    recording that the remainder was lost to a pre-git-history truncation. A required
    section of the components contract is therefore effectively absent, while
    `src_architecture.md` retains a full and current C1 map covering the same package.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:3714-3719
  - context_compass/system_docs/src_architecture.md:1500-1646
  IMPACT: The architecture map is a reconciliation source, so the rebuild is a
    verification exercise rather than a reconstruction from nothing.
  NEXT: Produce the filesystem walk and diff it against the architecture C1 map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-25T18:19:28Z
  TYPE: DECISION
  CLAIM: Purpose text is sourced from each module's OWN self-description via AST, in
    priority order module docstring -> `__agent_purpose__` -> first class docstring.
    Hand-authoring 553 purpose lines would have required either reading 553 files
    (blows the context budget) or inferring from filenames (forbidden outright).
    Coverage measured before committing to the approach: module docstrings alone cover
    only 66/554, but the waterfall resolves 536/553.
  EVIDENCE:
  - context_compass/agent_onboarding/default/general/skills/unknowns_gate_reference.md:19-21
  - context_compass/agent_onboarding/default/engineer/AGENTS.MD:137-143
  IMPACT: The inventory is reproducible rather than hand-maintained, which is the only
    way a 553-entry section survives contact with a moving package.
  NEXT: None; regeneration instructions are embedded in the section itself.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: MEASURE
  CLAIM: Section rebuilt and verified. 553 entries against a filesystem count of 553
    modules; seven group headers summing to 553 (10 root, 5 cache, 295 aether, 122
    nexus, 59 crystallizer, 20 mutation_research, 42 utilities); 17 entries honestly
    marked UNKNOWN; zero prose lines over the 120 cap; 5189/5189 CRLF lines with zero
    bare LF and zero NUL bytes.
  EVIDENCE:
  - context_compass/system_docs/src_components.md:3714-4719
  IMPACT: A required components-contract section is real content again instead of a
    truncation marker, and the encoding faults this repo has hit before did not recur.
  NEXT: Await owner acceptance.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-07-25T18:19:28Z
  TYPE: RISK
  CLAIM: Two incidental findings surfaced by the walk, both out of scope here.
    (1) `generalized_cache_runtime_rows_SCRATCH.py` ships inside `src/melder`, where
    engineer policy puts scratch work under `workspace/agent/`.
    (2) `utilities/helpers/class_wraps.py` still exists on disk although the epic
    recorded its removal from the package root, so it is now an unexported orphan.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_cache_runtime_rows_SCRATCH.py
  - src/melder/utilities/helpers/class_wraps.py
  IMPACT: Both are shipped-package hygiene items, not doc defects; neither blocks this
    lane, and neither should be silently absorbed into it.
  NEXT: Raise both to the owner at story walkthrough for a routing decision.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Section is a two-entry stub. Owner ruled full package inventory. `src_architecture.md`
:1500-1646 is a current partial map to reconcile against. Nothing may be listed that
was not verified to exist on disk.
