# Task: Teach quoted spell-name resolution consistently

## Metadata
- Task ID: TASK-2026-09-20-teach-meld-string-names
- Story: none
- Status: review
- Owner: codex
- Agent Name: workflows_1
- Priority: p2
- Created: 2026-09-20T09:05:25Z
- Updated: 2026-09-20T09:22:39Z

## Objective
Correct the tutorial convention to resolve by quoted spell name, including the owner's Watched
hook example, instead of teaching class/object references as the meld target.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requests finding and patching reference-based meld teaching examples.
- EXECUTION_BOUNDARY: README, authored public docs, catalog lesson/helper sources, package quickstart,
  associated explanations, mechanical codemod and derived publication assets.
- DEPENDENCIES: Earlier positional-call sweep, current bind-name derivation and public meld name lookup.
- EXIT_GATE: Published teaching calls use truthful string names or explicit spell_id/frame addresses;
  prose agrees, relevant lesson/docs checks pass and generated pages/downloads reflect the correction.
- FAILURE_ESCALATION: Do not quote a local variable or guess a generated class name; inspect the
  actual registration first. Preserve runtime implementations and concurrent owner changes.

## Scope Boundaries
- In scope: replace reference targets with registered-name strings and explain registration vs lookup.
- Out of scope: changing supported runtime API forms, bind targets, type annotations, test-only
  reference coverage, benchmark machine-ID paths, publication or commits.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Quoted-name teaching correction is implemented; all 133 lessons, 39 docs tests,
  strict build, links, downloads and derived-asset checks pass.

## Steps / Checklist
- [x] Inventory current reference calls and read the named hook example plus README address guidance.
- [x] Resolve nontrivial names: prebuilt instances, loop variables and codegen-created classes.
- [x] Apply an audited codemod and update explanations that teach reference-based resolution.
- [x] Run lesson/docs validation and rebuild publication outputs and affected derived assets.
- [x] Record the final audited scope and handoff.

## Deliverables
- Consistent quoted-name examples, including conduit.meld("Watched").
- Clarified README and maintainer guidance; no fictional runtime restrictions.
- Codemod inventory, complete scans and executed validation evidence.

## Validation
- Initial inventory: 140 reference targets in published Python lessons plus Worker and MyService examples.
- 138 calls converted by codemod; the remaining batch/address cases received source-backed editorial edits.
- All 137 published Python sources/helpers pass the string-target audit and zero-change repeat scan.
- Full saved-lesson harness: 133 passed in 19.06s on Python 3.14.7t / Melder 0.2.44, GIL off.
- Existing docs tests: 39 passed. Strict HTML build: 294 pages passed.
- Site validation: 35,513 local links and matching sources/downloads passed.
- Publication audit: zero reference-target calls in 495 code blocks, 137 Python downloads and four ZIPs.
- Source assets, src/other corpus freshness and scoped whitespace checks pass.

## Risks / Rollback Notes
- Quoting `prebuilt`, `c`, `worker_class` or `classes[...]` blindly would change lookup meaning.
- Address-law prose and assertions must be rewritten when their object-form example is removed.
- Preserve explicit machine IDs, frame/binding selectors, callable binding and returned-object annotations.
- Use exact source ranges and original-byte checks for codemod application.

## Applicable Anti-Patterns
- [x] No blanket identifier-to-string replacement across unrelated APIs.
- [x] No runtime API narrowing disguised as a documentation fix.
- [x] No validation success claim without executed evidence.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/meld_string_names_20260920/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain the audit/codemod/results; temporary build workspace is disposable after acceptance.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
- Record mapping decisions and validation results before progressing to the next work unit.

## Notes
- DATETIME: 2026-09-20T09:05:25Z
  TYPE: FACT
  CLAIM: The prior codemod removed spell= but preserved class/object references. Published lesson
    ASTs still contain 140 reference targets, including two Watched hook calls. The README already
    uses quoted names; docs/intermediate/registration.md contains a new Worker reference example.
    Current bind logic derives a name from the callable/class __name__ or the instance's type name.
  EVIDENCE:
  - UX_and_AIX_experiences/02_intermediate/32_config_meld_hooks.py:20-37
  - README.md:304-378
  - docs/intermediate/registration.md:33-54
  - src/melder/aether/spellbook/bind/bind.py:418-469
  IMPACT: The requested fix requires semantic name mapping and editorial updates, not just deleting a keyword.
  NEXT: Resolve exceptional target expressions, then prepare the bounded codemod.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T09:05:25Z
  TYPE: DECISION
  CLAIM: The two prebuilt variables contain AlreadyBuilt and PublishedConfig instances; use those
    type-name strings. Expert 36 materializes Tokenizer, Counter, Reporter and Worker; the dictionary
    expressions and worker_class variable map to those exact strings. Replace the beginner batch
    lookup comprehension with three explicit quoted-name assertions. Rewrite the address lesson to
    compare name and explicit-ID lookup, removing its object-target example and corresponding prose.
  EVIDENCE:
  - UX_and_AIX_experiences/01_beginner/03_bind_functions_and_instances.py:16-37
  - UX_and_AIX_experiences/02_intermediate/11_permissions_linking_vocabulary.py:12-26
  - UX_and_AIX_experiences/01_beginner/11_bind_many_at_once.py:22-30
  - UX_and_AIX_experiences/04_expert/36_an_agent_builds_a_working_system.py:49-120
  - UX_and_AIX_experiences/04_expert/36_an_agent_builds_a_working_system.py:154-226
  - UX_and_AIX_experiences/01_beginner/26_meld_address_forms.py:1-51
  IMPACT: All targets have a source-backed name mapping; no local variable spelling is mistaken for a spell name.
  NEXT: Apply the editorial corrections and the remaining mechanically verified target conversions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T09:05:25Z
  TYPE: FACT
  CLAIM: The codemod converts 138 remaining reference targets across 61 lesson files using declared
    class/function names and seven explicitly reviewed instance/generated-class mappings. All 137
    published Python inputs parse; AST comparison permits only the planned argument changes. Repeat
    check finds no remaining conversion. Editorial edits replace the batch loop's one reference call
    with three quoted calls, remove the address lesson's object form, fix Worker and MyService, and
    explain name-based lookup in README, beginner registration and maintainer guidance.
  EVIDENCE:
  - artifacts/meld_string_names_20260920/changes.json:1-8
  - artifacts/meld_string_names_20260920/idempotence.json:1-8
  - UX_and_AIX_experiences/02_intermediate/32_config_meld_hooks.py:30-37
  - UX_and_AIX_experiences/01_beginner/26_meld_address_forms.py:1-50
  IMPACT: Teaching sources now express the intended string-name convention. Validate their actual
    resolution outcomes and rendered code before claiming the examples work.
  NEXT: Run the complete lesson harness and documentation checks on the updated sources.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T09:18:21Z
  TYPE: MEASURE
  CLAIM: All four saved-lesson harnesses pass on Python 3.14.7t with GIL off and filesystem access:
    133 passed in 19.06s, including Watched hooks, prebuilt-name lookup, scoped calls and generated
    classes. All 39 documentation tests pass. Source assets and src/other corpora were regenerated
    against checkout version 0.2.44. No cache reset was needed for this run.
  EVIDENCE:
  - artifacts/meld_string_names_20260920/examples.log:1-3
  - artifacts/meld_string_names_20260920/examples.xml:1-1
  - artifacts/meld_string_names_20260920/docs-tests.log:1-7
  - artifacts/meld_string_names_20260920/source-assets-build.log:1-3
  IMPACT: The name mappings are verified by the real examples. Finish the strict publication build
    and audit its rendered code/downloads for remaining reference targets before handoff.
  NEXT: Verify the built site's links, source fidelity and string-target convention.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T09:22:39Z
  TYPE: MEASURE
  CLAIM: Strict HTML build and source-fidelity check pass for 294 pages and 35,513 local links.
    Rendered-code audit finds no reference targets in 495 teaching blocks; all 137 downloadable
    Python files and four collection ZIPs also use string positional targets. Final codemod scan
    reports zero edits. Source assets and src/other corpora are current for 0.2.44, and scoped diff
    checks pass. These checks complement the earlier 133 passing lessons and 39 passing docs tests.
  EVIDENCE:
  - artifacts/meld_string_names_20260920/publication-audit.json:1-8
  - artifacts/meld_string_names_20260920/html-build.log:1-1
  - artifacts/meld_string_names_20260920/site-check.log:1-1
  - artifacts/meld_string_names_20260920/source-assets-check.log:1-3
  - artifacts/meld_string_names_20260920/corpora-check.log:1-2
  IMPACT: The owner's intended quoted-name convention is complete across the teaching sources
    and generated publication views, without narrowing the runtime API.
  NEXT: Owner reviews and commits the documentation correction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed the owner's correction: tutorial meld calls use quoted registered names, including Watched.
Converted 138 remaining calls by codemod, manually clarified batch/address examples, fixed the Worker
guide and MyService quickstart, and documented the convention in README/registration/maintaining.
All 133 saved examples and 39 docs tests pass. Strict 294-page build, 35,513 links, 495 rendered code
blocks, all 137 Python downloads and four ZIPs pass. Source/other assets are refreshed and verified.
Runtime APIs and test-only reference coverage remain intact. Changes are local and ready for owner signing.
