# Task: Teach bind hooks in intermediate and expert Read the Docs lessons

- Completed: 2026-09-22T18:47:41Z
- Summary: Intermediate 40, expert 37, linked guides/downloads and release notes accepted;
  examples and local documentation publication checks are qualified.

## Metadata
- Task ID: TASK-2026-09-22-add-bind-hook-intermediate-and-expert-examples
- Epic: EPIC-2026-09-20-bind-lifecycle-hooks-and-reference-strategies
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-22T17:49:29Z
- Updated: 2026-09-22T18:47:41Z

## Objective
Add runnable intermediate and expert bind-hook lessons to the Read the Docs curriculum. Teach the
three stages, then agent-supplied reference admission and actual-Spell adjustment with verified behavior.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requests both levels. Read example instructions and actual hook source.
- EXECUTION_BOUNDARY: New numbered examples, catalog/curriculum, related authored guides and level
  summaries/concept maps, example/docs validation, local HTML inspection and requested release notes.
- DEPENDENCIES: Implemented Book/Conduit bind hooks and configuration seeds; existing docs builder.
- EXIT_GATE: Both runnable lessons pass, navigation/downloads work and prose matches the executed API.
- FAILURE_ESCALATION: Record real public-surface gaps or runtime defects; do not silently change runtime.

## Scope Boundaries
- In scope: Local documentation and runnable examples, using import melder as md and human spell names.
- Out of scope: Runtime changes, dependency upgrades, packaged/LLM asset regeneration, version bump,
  commits, deployment or claims that the hosted Read the Docs site has been published.
- The existing package-asset hold remains; local Sphinx rendering is part of documentation verification.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner accepts the bind-hook epic and its documentation for turn-in.

Release-note follow-up:
- from_state: in_progress
- to_state: review
- transition_reason: Requested release summary added, reread and whitespace-checked.

## Work
- [x] Check whether bind-hook examples already exist and read the example/doc maintenance contracts.
- [x] Trace stage inputs, mutation and failure contracts from source and current tests.
- [x] Add intermediate/expert lessons with catalog and reciprocal curriculum links.
- [x] Run affected examples and docs checks; render and inspect the new local pages/downloads.

## Deliverables
- Intermediate lesson for pre/activation/post stages and Book/Conduit hook setup/clearing.
- Expert lesson for agent proposal checking and actual-Spell adjustment with accepted/refused outcomes.
- Authored guidance that explains bind activation timing and the difference from Meld creation hooks.

## Validation
- Both new lessons passed their first isolated example run on Python 3.14t, GIL disabled.
- 76 unique intermediate/expert examples pass across the main run and two focused reruns. Lesson 28
  was corrected for the completed graduation behavior; existing expert 05 needed sandbox escalation
  for its temporary-file writes. The passing rerun retained a repository-owned TEMP/TMP root.
- All 39 existing documentation tests pass; navigation validates 298 pages and 54 assets.
- Strict HTML build passes; site check validates 36,144 local links and lesson-source fidelity.
- New lesson downloads and both source/HTML collection ZIPs match their canonical scripts byte-for-byte.
- Scoped lint and whitespace checks pass. All 26 held package assets are unchanged.
- No hosted deployment, package/LLM asset regeneration, dependency change or coverage run.

## Risks / Mitigations
- Activation occurs before publication; post-bind is not an outer transaction-commit callback.
- Modification examples must use a verified public surface and must not teach unsafe identity edits.
- Existing intermediate lesson 03 teaches creation hooks, not bind lifecycle hooks; preserve its purpose.

## Applicable Anti-Patterns
- No deep Melder imports or unverified mutation claims in teaching code.
- No hand edits to generated docs, package-asset generation or hosted publication claims.
- No broad runtime or unrelated curriculum changes.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/bind_hook_examples_20260922/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none

## Noting Behavior
Record stage/public-surface findings and qualification results before each next tranche.

## Notes
- DATETIME: 2026-09-22T17:49:29Z
  TYPE: FACT
  CLAIM: docs and saved examples contain no add_bind_hooks, clear_bind_hooks or with_bind_hooks
    usage. Intermediate lesson 03 is about SpellBinder instance-creation hooks. The public docs
    builder consumes numbered scripts, catalog entries and reciprocal curriculum relationships.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/03_registration_hooks.py:1-44
  - docs/intermediate/hooks.md:1-29
  - docs/maintaining.md:52-72
  - UX_and_AIX_experiences/AGENTS.md:1-47
  IMPACT: Add dedicated lessons rather than relabeling runtime creation callbacks as bind callbacks.
  NEXT: Read source and neighboring expert/curriculum inputs to select executable examples.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T17:56:00Z
  TYPE: DECISION
  CLAIM: Source confirms pre receives the exact reference before reflection; activation receives the
    newly constructed Spell before profile completion/publication; post runs after registration and
    normal publication. Return values are ignored and failures wrap the original cause by phase.
    Metadata and tags are public mutable application annotation surfaces, suitable for the examples.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:266-430
  - src/melder/aether/spellbook/bind/bind.py:654-810
  - src/melder/aether/spellbook/spellbook.py:4763-4840
  - src/melder/aether/spellbook/spellbook.py:5290-5460
  - src/melder/aether/spellbook/spell.py:409-445
  - src/melder/aether/conduit/conduit.py:3264-3347
  IMPACT: Add intermediate 40 for configuration seeds plus Book/normal-Conduit add/clear/re-add.
    Add expert 37 for two reference checks, agent metadata validation in activation, post metadata
    update/audit and published-state behavior on a later post failure. Teach these as live annotations,
    not identity changes, source replacement or automatic persistence refresh. Existing expert 36
    remains the code-generation lesson; this example accepts references an agent already supplied.
  NEXT: Write both runnable lessons and their authored/curriculum links, then execute them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T17:59:00Z
  TYPE: MEASURE
  CLAIM: Both new runnable lessons pass through the existing isolated example harness on Python
    3.14t with GIL disabled. Intermediate proves stage order, metadata changes, no repeat on meld,
    and normal-Conduit clearing/re-registration. Expert proves two reference refusals, activation
    metadata refusal, exact supplied-object reuse, post metadata updates and surviving post failure.
  EVIDENCE:
  - artifacts/bind_hook_examples_20260922/lessons.log:1-2
  - UX_and_AIX_experiences/02_intermediate/40_bind_lifecycle_hooks.py:1-105
  - UX_and_AIX_experiences/04_expert/37_review_agent_bindings.py:1-180
  IMPACT: Teaching contracts are executable without runtime edits. Use metadata explicitly as live
    application annotations; no authentication, source rewrite or persistence-refresh promise.
  NEXT: Register both lessons in the catalog/curriculum and write the linked guides.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T18:02:00Z
  TYPE: FACT
  CLAIM: Intermediate 40 and expert 37 are registered in the explicit catalog. The intermediate
    lifecycle guide now explains the bind stages and configuration/runtime setup. A new expert
    bind-hooks chapter teaches proposal checks, actual-Spell updates and failure phases; curriculum,
    level summaries, governed-change cross-link and concept maps connect both lessons.
  EVIDENCE:
  - docs/catalog.toml:53-163
  - docs/curriculum.toml:121-127
  - docs/expert/bind-hooks.md:1-83
  - docs/intermediate/hooks.md:1-77
  IMPACT: Canonical teaching inputs are ready. The documented publication builder writes only its
    verified docs/_build outputs; source/package/LLM asset regeneration remains excluded.
  NEXT: Run intermediate/expert harnesses, documentation unit checks and strict local HTML build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T18:02:08Z
  TYPE: MEASURE
  CLAIM: Full intermediate/expert harness passes 74 cases, including both new lessons. Existing
    intermediate 28 fails because it still expects former definitions after graduation; expert 05
    fails only when writing its TemporaryDirectory under the sandbox's OS temp path. All 39 docs
    tests pass and navigation validates 298 pages/54 assets. Both new scripts pass scoped Ruff.
  EVIDENCE:
  - artifacts/bind_hook_examples_20260922/tier_examples.log:1-35
  - artifacts/bind_hook_examples_20260922/docs_tests.log:1-7
  - artifacts/bind_hook_examples_20260922/docs_check.log:1-1
  - UX_and_AIX_experiences/02_intermediate/28_upgrade_to_normal.py:25-48
  IMPACT: Update the related stale graduation example to teach its new empty Book and retained
    disposal ownership. This corrects the earlier approved graduation behavior in the same curriculum;
    no runtime fix. Retry the independent file-writing lesson with a repository-owned temp root.
  NEXT: Correct lesson 28, rerun those two cases and build local HTML.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T18:05:00Z
  TYPE: MEASURE
  CLAIM: Corrected intermediate graduation lesson 28 passes: old definition lookup refuses, the
    new root binds/melds its own definition, retained creations dispose once, and the former root
    remains usable. Expert 05 still fails in TemporaryDirectory with WinError 5 even when TEMP/TMP
    point inside the task artifact directory. Its failure is environmental, before protocol-file output.
  EVIDENCE:
  - artifacts/bind_hook_examples_20260922/followup.log
  - UX_and_AIX_experiences/02_intermediate/28_upgrade_to_normal.py:1-79
  IMPACT: No protocol runtime or example changes are indicated. Local HTML build is running.
  NEXT: Rerun only expert 05 with elevated sandbox access and the same repository-contained temp root.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T18:07:50Z
  TYPE: MEASURE
  CLAIM: Local publication is qualified. Strict HTML builds 298 pages, site checks validate 36,144
    local links, and both new scripts match individual downloads and source/HTML collection ZIPs.
    All 76 unique intermediate/expert cases pass across the broad run and focused fixes/retries.
    All 39 docs tests and scoped lint/whitespace checks pass. All 26 held package assets are unchanged.
  EVIDENCE:
  - artifacts/bind_hook_examples_20260922/html_build.log:1-1
  - artifacts/bind_hook_examples_20260922/site_check.log:1-1
  - artifacts/bind_hook_examples_20260922/publication_audit.json:1-21
  - artifacts/bind_hook_examples_20260922/protocol_temp_retry.log:1-2
  - artifacts/bind_hook_examples_20260922/held_assets.json:1-5
  IMPACT: Requested documentation and examples are ready in the repository. No hosted publication
    is claimed; normal source links still identify the checkout's committed revision during preview.
  NEXT: Owner reviews the examples or includes them in the normal documentation publication flow.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T18:13:58Z
  TYPE: PLAN
  CLAIM: Owner requests release notes for the new bind-hook examples. Add a concise section to
    release_docs/next_version_release.md covering intermediate 40, expert 37, guides/downloads,
    the related graduation example correction and already-recorded validation.
  EVIDENCE:
  - release_docs/next_version_release.md:1-5
  - artifacts/bind_hook_examples_20260922/publication_audit.json:1-21
  IMPACT: Documentation-only addition to the existing 0.2.45 draft; no version or runtime changes.
  NEXT: Write and reread the release section.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T18:14:51Z
  TYPE: FACT
  CLAIM: Added the bind-hook tutorial section to the top-level release draft. It covers both lesson
    levels, their guides/downloads, the graduation example correction and recorded qualification.
  EVIDENCE:
  - release_docs/next_version_release.md:5-29
  IMPACT: Owner's release-note follow-up is complete. Prose was reread and scoped whitespace check
    passed; no runtime tests were rerun for this documentation-only edit.
  NEXT: Continue with the owner's next selected work item.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Completed by owner instruction with the bind-hook epic. All local teaching and release-note work is
delivered; ordinary repository publication remains outside this task. No build hold was lifted.

Intermediate 40 teaches Bind stages, configuration seeds and Book/normal-Conduit add/clear/re-add.
Expert 37 checks agent-supplied existing objects, updates the actual Spell during activation/post and
proves post failures leave publication intact. docs/intermediate/hooks.md and docs/expert/bind-hooks.md
explain the contracts; catalog/curriculum, level summaries and concept maps are linked. Corrected the
older graduation lesson 28 to match the independently owned empty Book and retained disposal behavior.
Both new lessons and all 76 tier cases qualify across runs. All 39 docs tests, strict HTML and 36,144
local-link/source-fidelity checks pass; new scripts match downloads/ZIPs. No runtime edits, package/LLM
asset regeneration or hosted publication. Task is complete; ordinary commit/publish flow remains.
Both new tutorials are summarized in release_docs/next_version_release.md as requested.
