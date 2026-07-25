

# Task: Move agent metadata off class bodies into a harvested build asset

## Metadata
- Task ID: TASK-2026-07-25-agent-metadata-build-asset
- Story: none (owner-directed, sibling of EPIC-2026-07-22-agent-metadata-to-docstring)
- Status: in_progress
- Owner: melder_0
- Agent Name: melder_0
- Priority: p2
- Created: 2026-07-25T20:10:00Z
- Updated: 2026-07-25T20:10:00Z

## Objective
Stop 370 class bodies from carrying `__ast_helper_access__` / `__agent_purpose__`.
Author the facts in docstrings, harvest them at build time into a generated asset
under the existing build-asset runner, and let `ClassSurfaceAstDescriber` read the
asset instead of `type(obj).__dict__`.

## Ticket Contract
- ENTRY_GATE: active `attention_board.md` row; the 183-class gap audited (done) and
  the owner's exemption ruling recorded (done).
- EXECUTION_BOUNDARY (PHASE 1 - this pass, ADDITIVE ONLY):
  `src/melder/_build_assets/_agent_metadata/`, plus its tests. Nothing consumes the
  asset yet, so no runtime behaviour changes.
- EXECUTION_BOUNDARY (PHASE 2 - NOT this pass): the docstring codemod across ~370
  files, stripping the 788 assignments, and repointing `ClassSurfaceAstDescriber`.
- DEPENDENCIES: `_build_asset_runner.py` (discovery + gate); owner grammar ruling
  2026-07-25; owner exemption ruling for `spell_compiler`.
- EXIT_GATE (phase 1): runner discovers the asset, `--check` green, tests pass, and
  the asset's counts reconcile with the audit (394 marked / 173 exempt / 10 pending).
- FAILURE_ESCALATION: BLOCKER if harvest cannot reproduce the current attr values
  exactly; DECISION_REQUEST before any phase-2 file sweep.

## Scope Boundaries
- In scope (phase 1): the harvester, its generated asset, tests, runner integration.
- Out of scope (phase 1): editing any class body; changing `ClassSurfaceAstDescriber`;
  the `Registration:` docstring section (different axis - it describes bind guarding,
  which the internal manifest now owns).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved the grammar, the exemption rule, and implementation.

## PATCH GATE ASSESSMENT
`patch_framework_gating.md` applies to system-impacting change. PHASE 1 IS NOT
system-impacting: it adds a generated file that nothing imports and alters no
runtime path, so it proceeds without patch artifacts. PHASE 2 IS system-impacting -
it changes how `ClassSurfaceAstDescriber` resolves metadata and edits ~370 files -
and MUST NOT start until `architecture_patch.md` and
`component_patch_class_surface_ast_describer.md` exist and are linked here.

## Steps / Checklist
- [x] Audit the unmarked gap and confirm the owner's spell_compiler theory (94%).
- [x] Confirm every marked class already has a docstring (394/394 - pure move).
- [x] Settle the grammar with the owner.
- [ ] Build the harvester with dual-source reading (docstring first, attr fallback).
- [ ] Generate the asset; reconcile counts against the audit.
- [ ] Tests for grammar parsing, exemption, pending catalog, and value fidelity.
- [ ] PHASE 2 (separate, patch-gated): codemod, strip, repoint.
- [ ] Document each meaningful finding immediately in `## Notes`.

## Deliverables
- `_build_assets/_agent_metadata/_builder.py` and its generated asset.
- Tests proving harvest fidelity and the three-state catalog.

## Files / Paths Impacted
- src/melder/_build_assets/_agent_metadata/_builder.py
- src/melder/_build_assets/_agent_metadata/agent_metadata.py (GENERATED)
- tests/unit/melder/build_assets/test_agent_metadata_builder.py

## Validation
- Not run (sandbox is Python 3.10; repo floor is 3.14t).
- Recommended (owner, 3.14t):
  - `python src/melder/_build_assets/_build_asset_runner.py --check`
  - `pytest tests/unit/melder/build_assets -q`

## Risks / Rollback Notes
- RISK: harvest silently loses prose. Mitigation: dual-source with attr fallback, and
  a test asserting the harvested value equals the current attr value for every class.
- Rollback: phase 1 is purely additive - delete the directory.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/agent_metadata_asset_2026_07_25/architecture_patch.md (PHASE 2, not yet authored)
  - system_docs/patches/active/agent_metadata_asset_2026_07_25/component_patch_class_surface_ast_describer.md (PHASE 2, not yet authored)
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: at phase-2 closure, once durable deltas merge into the system docs.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Keep notes append-only; promote `UNKNOWN` to `FACT` only with direct evidence.

## Notes
- DATETIME: 2026-07-25T20:10:00Z
  TYPE: MEASURE
  CLAIM: Audit complete, three findings that de-risk the migration. (1) The unmarked
    gap is 183 classes and 94% of it - 173 - sits in `aether/spellbook/spell_compiler`,
    with the remaining 10 in `utilities`. That matches the OCE epic's closure note
    "spell_compiler excluded per owner", so the gap is an EXISTING RULING that was
    never written anywhere a tool could read. (2) All 394 marked classes ALREADY have
    docstrings, so this is a pure MOVE, not an authoring project - the single largest
    risk is gone. (3) Zero classes carry `access=private`; my earlier report of one was
    a grep false positive on doc prose, so the runtime-raise rule for private classes
    has no live subjects.
  EVIDENCE:
  - src/melder/utilities/helpers/class_surface_ast_describer.py:711-716
  IMPACT: The migration is mechanical rather than editorial, and the exemption is a
    path rule over one coherent subtree rather than 173 individual judgements.
  NEXT: Confirm `Registration:` is a different axis before adding a new section.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-07-25T20:10:00Z
  TYPE: FACT
  CLAIM: The existing `Registration:` docstring section (412 classes) does NOT
    duplicate `__ast_helper_access__`. It reads "MELDER KERNEL - guarded. `Aether()`
    returns the process singleton..." - i.e. whether the class may be BOUND as a spell,
    which the internal manifest now owns exactly. `__ast_helper_access__` answers a
    different question: whether agent tooling should surface the class at all. Two axes,
    no collision, so a new section is warranted rather than reusing that one.
  EVIDENCE:
  - src/melder/_build_assets/_init_manifest/internal_manifest.py:20-21
  IMPACT: Avoided conflating bind-guarding with agent visibility, which would have made
    both facts unreadable. Side observation for a later lane: now that the manifest
    guards every class uniformly, the per-class "guarded" prose in 412 `Registration:`
    sections is largely redundant.
  NEXT: Implement the harvester against the agreed grammar.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-25T20:10:00Z
  TYPE: DECISION
  CLAIM: OWNER RULINGS. (1) GRAMMAR: `AGENT_ACCESS: <value>` and `AGENT_PURPOSE:` as
    line-anchored ALL-CAPS docstring sections - deliberately un-prose-like so extraction
    cannot collide with the Title-Case sections (`Purpose:`, `Contract:`, `Threading:`)
    already in use, and visually traceable to the attribute names being retired.
    (2) THREE STATES: marked -> the asset; `exempt` -> catalogued as a deliberate
    ruling; absent -> catalogued as `pending` for later fill-in. This is the point of
    the design: today "excluded on purpose" and "somebody forgot" are indistinguishable
    to every tool and every future agent. (3) EXEMPTION MECHANISM: `spell_compiler` is
    exempted by PATH RULE in the builder, not by stamping 173 files, because it is one
    coherent subtree under an existing owner ruling. Per-class `exempt` stays available
    for one-offs.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-07-25_agent_metadata_build_asset_task.md
  IMPACT: Zero file churn for the exemption; the catalog makes deferred work visible
    instead of invisible.
  NEXT: Build the harvester with dual-source reading so the asset is correct at every
    point of the migration rather than only at the end.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
PHASE 1 (additive, in progress): harvester + generated asset under the build-asset
runner. Nothing consumes it yet, so no runtime behaviour changes and the patch gate
does not fire.

PHASE 2 (patch-gated, NOT started): the ~370-file docstring codemod, stripping the 788
assignments, and repointing `ClassSurfaceAstDescriber` from `__dict__.get` to the asset.
That IS system-impacting and must not begin before its two patch docs exist.

Key design choice: the harvester reads DUAL-SOURCE - docstring section first, class
attribute as fallback - so the asset is complete and correct from the first run, and
the codemod can proceed subtree by subtree instead of as one atomic 370-file cutover.
