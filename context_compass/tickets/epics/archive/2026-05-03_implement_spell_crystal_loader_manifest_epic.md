# Epic: Implement Spell Crystal Loader Manifest

## Metadata
- Epic ID: EPIC-2026-05-03-implement-spell-crystal-loader-manifest
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-03T19:14:05Z
- Updated: 2026-05-03T19:14:05Z
- Target Window: 2026-Q2
- Related Program/Initiative: Crystallizer retained module truth and loader activation

## Problem / Opportunity
The current `SpellCrystal` shape still carries the wrong center of gravity for
the loader-oriented direction we settled on. The system does not need a crystal
that mirrors the live mutable `Spell` object. It needs a crystal that starts
from one concrete spell SHA and turns that spell into a stable module/resource
manifest the loaders can validate and activate before bind/conjure work begins.

The immediate opportunity is to narrow the crystal around:
- the root spell SHA
- the root module identity
- recursive dependency discovery
- classification of user-source, site-package, and synthetic-module targets
- flat target lists and mappings that loaders can consume directly

## MRP Alignment (Most Reasonable Product)
The MRP is not "solve the entire crystal system at once."
The MRP is:
- a `SpellCrystal` that can be built from `ISpell`
- a bounded dependency walk over the module world that spell depends on
- enough classified output that loaders know what modules/assets must exist
- no accidental expansion into bind replay, mutation semantics, or live runtime
  ownership mirroring

## Ticket Contract
- ENTRY_GATE: the user explicitly asked to start with the `SpellCrystal`
  implementation plan and confirmed the crystal should stay focused on module
  mapping from one concrete spell.
- EXECUTION_BOUNDARY: spell-crystal planning only, with immediate emphasis on
  constructor input, dependency walk semantics, and retained manifest fields.
- DEPENDENCIES:
  - `src/melder/crystallizer/spell_crystal.py`
  - `src/melder/crystallizer/synthetic_module.py`
  - `src/melder/utilities/interfaces/interfaces.py`
  - crystallizer philosophy and configuration artifacts
  - physical/synthetic experimentation results
- EXIT_GATE: the epic holds a concrete implementation plan for the first
  `SpellCrystal` slice and is specific enough to drive task-level code changes
  without drifting back into broader crystal speculation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if implementing the manifest
  slice would require reintroducing broad live spell replay semantics.

## Goals (Outcomes)
- Define the narrow first-class job of `SpellCrystal`.
- Define exactly what the constructor should capture from `ISpell`.
- Define the private dependency-walk helpers and classification rules.
- Define the retained manifest fields loaders need.
- Keep bind replay, mutation semantics, and live runtime ownership out of scope.

## Non-Goals (Explicit Exclusions)
- Full bind replay object design.
- MutationResearch branch/fork semantics.
- Loader implementation details beyond what fields the manifest must expose.
- Broad asset-store refactors.

## Scope Boundaries
- In scope:
  - `ISpell`-based constructor input
  - root module resolution
  - recursive module dependency walk
  - module/path/classification target retention
  - synthetic-module detection support
- Out of scope:
  - replaying full bind metadata
  - live runtime ownership mirroring
  - conduit snapshot semantics beyond crystal manifest consumption

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a new epic and asked to
  begin the implementation plan for the narrowed `SpellCrystal` design.

## Success Metrics
- The implementation slice is sharply defined and loader-oriented.
- The constructor input is reduced to `ISpell` plus internal resolution work.
- The retained fields are clear enough to patch `spell_crystal.py` directly.
- The plan stays narrow and does not drift back into replaying all spell state.

## Requirements (Functional + Non-Functional)
- Functional:
  - `SpellCrystal` starts from `ISpell`
  - captures root spell SHA and root module identity
  - walks module dependencies recursively
  - keeps flat loader-facing targets and lookup maps
  - distinguishes user-source, site-package, synthetic-module, and unknown
    targets
- Non-functional:
  - no live object retention beyond the constructor call
  - no reliance on mutable runtime ownership state
  - explicit cycle protection during dependency walk
  - clear diagnostics for unresolved modules/paths

## Constraints / Assumptions
- The root spell SHA remains the concrete spell-version identity for this slice.
- `SpellCrystal` is being used as a loader asset and module manifest, not as a
  live spell replay artifact.
- Module/path targets are more important than broad spell metadata here.
- Synthetic modules need an easy sentinel so the walker can classify them
  without guesswork.

## Dependencies / External References
- `codex/context_compass/artifacts/2026-04-26_crystallizer_philosophy.md`
- `codex/context_compass/artifacts/crystallizer_configuration.md`
- `tests/experimentation/physical_to_synthetic_module_swap_semantics_testbench.py`
- `tests/experimentation/synthetic_module_import_testbench.py`

## Milestones (Track Progress)
- [ ] Milestone 1: settle constructor input and retained field set
- [ ] Milestone 2: settle module resolution and dependency walk behavior
- [ ] Milestone 3: settle loader-facing target lists and diagnostics

## Stories (Required to Complete)
- [ ] Story: define the `ISpell`-driven constructor contract
- [ ] Story: define the recursive module dependency walker and classification
- [ ] Story: define the first loader-facing manifest fields and maps

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: decide the exact retained field list for the narrowed crystal
- [ ] Task: decide synthetic-module detection rules for the dependency walker
- [ ] Task: stage the first code patch against `spell_crystal.py`

## Acceptance Criteria (Epic Done)
- The first spell-crystal implementation slice is defined narrowly enough to
  patch in code.
- The slice is explicitly loader-oriented.
- The retained manifest fields are clear and finite.
- The plan avoids re-expanding crystal scope into live spell replay.

## Risks / Mitigations
- Risk: the slice drifts back into deep spell snapshot semantics.
  Mitigation: keep the plan centered on module/path/dependency targets only.
- Risk: dependency discovery becomes too broad or noisy.
  Mitigation: keep the tracked universe limited to user-source, site-packages,
  synthetic modules, and unresolved diagnostics.

## Applicable Anti-Patterns
- [ ] No epic-state transition without evidence-backed scope.
- [ ] No re-expansion into full spell replay without explicit user decision.
- [ ] No loader-facing plan that depends on retaining live object references.

## Validation / Test Approach
- Design-only in this epic.
- Validation is coherence of the implementation plan and readiness for the
  first `spell_crystal.py` patch.
- Loader-manifest test split to preserve once the code lane is active:
  - unit:
    synthetic-module and direct manifest-helper behavior
  - component:
    real physical and mixed physical/synthetic module graphs without full
    Melder binding
  - integration:
    real `Spellbook.bind(...)` producing a live spell that
    `SpellCrystal` crystallizes into a dependency manifest

## Rollout / Adoption Plan
- First define the narrow crystal manifest slice here.
- Then open task-level code edits against `spell_crystal.py` and
  `synthetic_module.py` as needed.
- Then validate the slice against existing crystallizer and import experiments.

## Open Questions
- Which of the root target fields are truly necessary in v1 of the manifest?
- Do we keep only flat lists, or also direct-dependency maps by module name?
- How much unresolved/diagnostic state is worth retaining in the crystal?

## Decision Log
- 2026-05-03T19:14:05Z: Opened to hold the narrowed spell-crystal
  implementation plan after the user requested we begin with the constructor
  and dependency-mapping slice.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-03T19:14:05Z
  TYPE: PLAN
  CLAIM: The narrowed implementation slice starts with `ISpell` input, root
    spell SHA capture, root module resolution, recursive dependency walking,
    and flat loader-facing module/path/classification targets. No other spell
    semantics are required in the first cut.
  EVIDENCE:
  - user_instruction: "make an epic, and begin your implementation plan for this"
  - user_instruction: "we just need private methods to run during the init to
    find the module data using AST searches"
  - user_instruction: "we just want to map the assets the kind of modules they
    are and the file extensions too"
  IMPACT: The next code work can stay tightly bounded and loader-oriented.
  NEXT: use this epic as the implementation plan anchor before touching
    `spell_crystal.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T23:50:01Z
  TYPE: FACT
  CLAIM: The first loader-manifest test ring is now explicit and green. The
    unit layer covers direct synthetic-module dependency walking and honest
    unknown-target recording, the component layer covers real physical graphs
    plus mixed physical/synthetic dependency classification, and the
    integration layer covers the real `Spellbook.bind(...)` path before
    crystallization. This matches the current loader-facing crystal contract:
    dependency walking and mapping correctness first, not broad live-spell
    replay behavior.
  EVIDENCE:
  - tests/unit/melder/crystallizer/test_spell_crystal.py:1-175
  - tests/component/melder/crystallizer/test_spell_crystal_component.py:1-124
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py:1-98
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_spell_crystal.py` -> `3 passed`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/component/melder/crystallizer/test_spell_crystal_component.py` -> `2 passed`
  - validation_result:
    `python.exe -m pytest -q -p no:cacheprovider tests/integration/melder/crystallizer/test_spell_crystal_integration.py` -> `1 passed`
  IMPACT: The epic now has a concrete test plan and a first live proving ring
    for the current SpellCrystal manifest slice.
  NEXT: keep future crystal changes centered on dependency walking, target
    mapping, and loader-facing manifest integrity unless the scope explicitly
    widens.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, slice boundaries, and field/helper scope.
- Add notes when the retained field set or helper behavior changes materially.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
This epic holds the narrowed implementation plan for turning `SpellCrystal`
into a spell-targeted module dependency manifest for loaders.
