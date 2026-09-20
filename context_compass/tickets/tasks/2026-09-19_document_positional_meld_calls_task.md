# Task: Use positional meld targets throughout published examples

## Metadata
- Task ID: TASK-2026-09-19-document-positional-meld-calls
- Story: none
- Status: review
- Owner: codex
- Agent Name: workflows_1
- Priority: p2
- Created: 2026-09-19T21:44:14Z
- Updated: 2026-09-19T21:56:08Z

## Objective
Replace the documented `meld(spell=target)` example spelling with `meld(target)` through a
deterministic codemod, including the saved lesson sources used by Read the Docs and its downloads.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested this documentation/README sweep using a code generator.
- EXECUTION_BOUNDARY: README and authored docs, the four published UX/AIX lesson collections and
  helpers, the package introductory docstring, derived documentation/assets and task evidence.
- DEPENDENCIES: Existing docs catalog/curriculum, public Conduit/SpellSpace meld contracts and builders.
- EXIT_GATE: No old spelling remains in publication inputs; codemod is idempotent and changes only
  the approved argument spelling; relevant example/docs checks pass or unrelated failures are evidenced.
- FAILURE_ESCALATION: Preserve concurrent source/compiler work; do not alter runtime semantics or
  publication settings to make documentation checks pass.

## Scope Boundaries
- In scope: positional human-target examples, string-embedded code, rendered lesson downloads and docs.
- Out of scope: runtime implementation/API changes, unrelated keyword calls, test-only keyword
  coverage, historical tickets, commits or deployment to Read the Docs.
- Keep `spell_id=`, `spellframe=`, `binding_name=` and bind's `spell=` arguments unchanged.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Positional spelling sweep, strict docs build, source-fidelity/link audit and
  generated assets are complete. Three runtime-example failures are recorded during concurrent code work.

## Steps / Checklist
- [x] Inspect README, docs assembly, lesson input roots and applicable example instructions.
- [x] Generate a bounded dry-run codemod report and verify its proposed syntax-only changes.
- [x] Apply the codemod and confirm idempotence and no remaining publication-input matches.
- [x] Run documentation/example checks, rebuild generated publication outputs and refresh needed assets.
- [x] Record final diff, validation evidence and handoff.

## Deliverables
- Consistent positional target spelling in the published tutorials and package quickstart.
- Auditable codemod with an explicit changed-file/call inventory.
- Rebuilt local documentation and validation results.

## Validation
- 150 occurrences changed in 66 files; AST verification and zero-change repeat scans pass.
- 39 existing documentation tests pass; strict Sphinx build passes for 294 pages.
- Site validation passes with 35,501 local links and matching downloaded sources.
- 557 rendered code blocks, 137 Python downloads and four example ZIPs contain no old spelling.
- Source assets and src/other corpora regenerated and verified; scoped whitespace checks pass.
- Existing lesson harness: 130 passed, three failed (one permission error, two cache assertions).
  Owner confirms concurrent runtime work; failures are retained separately and not repaired here.

## Risks / Rollback Notes
- Read the Docs copies real example sources byte-for-byte, including helper files in downloads.
- README currently already uses positional targets; do not manufacture an unrelated edit.
- The owner/another agent has substantial compiler/source changes in flight; preserve those edits.
- Record original bytes/hashes for changed files and refuse concurrent edits during codemod application.

## Applicable Anti-Patterns
- [x] No blind repository-wide spelling replacement or hand-editing generated HTML.
- [x] No conversion of explicit machine IDs or changes to runtime API definitions.
- [x] No successful build/test claim without executed results.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/positional_meld_docs_20260919/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain codemod/inventory/validation; transient build environment may be removed at closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
- Record the scope, audited replacement counts and build/example results before the next work tranche.

## Notes
- DATETIME: 2026-09-19T21:44:14Z
  TYPE: FACT
  CLAIM: README already uses positional human targets. The old spelling appears throughout the
    published lesson sources and in the package quickstart. ExampleCatalog copies those scripts
    and helpers into downloads and literalinclude pages; Curriculum selects README sections or
    authored guides. Conduit.meld and SpellSpace.meld both take spell as their first positional slot.
  EVIDENCE:
  - README.md:304-378
  - docs/tools/example_catalog.py:201-257
  - docs/tools/curriculum.py:112-149
  - src/melder/aether/conduit/conduit.py:3967-4117
  - src/melder/aether/conduit/spell_space/spell_space.py:443-495
  - src/melder/__init__.py:9-15
  IMPACT: Fix the canonical sources so every generated chapter/download receives the same correction.
    A mechanical first-keyword removal is behavior-preserving; existing explicit identity forms remain.
  NEXT: Generate the codemod's reviewed inventory and AST equivalence proof before applying it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:44:14Z
  TYPE: MEASURE
  CLAIM: The dry-run scans 204 publication inputs and identifies 150 spelling replacements across
    66 files. Every Python input parses and passes AST equivalence after moving only the leading
    spell keyword into the first argument and applying the same textual correction to docstrings
    or embedded code. Non-leading spell arguments refuse automation instead of reordering evaluation.
  EVIDENCE:
  - artifacts/positional_meld_docs_20260919/codemod.py:20-142
  - artifacts/positional_meld_docs_20260919/dry-run.json:1-8
  IMPACT: The mechanical change is bounded and reviewable; README has no matching old spelling.
    The docs builder validates output containment and regenerates source/HTML from canonical inputs.
  NEXT: Apply the codemod, verify a zero-change second pass and build through the locked docs toolchain.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:44:14Z
  TYPE: MEASURE
  CLAIM: Applied all 150 replacements in 66 files. A second scan of the same 204 publication inputs
    reports zero changes and passes AST verification. The README needed no edit; named target
    lessons now show positional strings/classes while explicit IDs and frame/binding arguments remain.
    Created a task-owned Python 3.14.7t docs environment with all 32 pinned documentation dependencies.
  EVIDENCE:
  - artifacts/positional_meld_docs_20260919/changes.json:1-8
  - artifacts/positional_meld_docs_20260919/idempotence.json:1-8
  - UX_and_AIX_experiences/01_beginner/26_meld_address_forms.py:32-51
  IMPACT: Canonical inputs are corrected; validate actual lesson execution and generated publication outputs.
  NEXT: Run existing documentation and lesson checks, then build the corrected site.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:53:13Z
  TYPE: MEASURE
  CLAIM: All 39 documentation tests pass. Strict Sphinx HTML build succeeds for 294 pages and the
    site checker validates 35,501 local links with matching downloaded sources. The lesson harness
    reports 130 passed and three failures: expert 05 raises Windows temporary-directory PermissionError;
    expert 09 and 27 fail checkpoint-cache membership assertions. Expert 05/09 were not changed.
    Owner confirms another runtime change is in progress, so attribution of the cache failures is
    unresolved and runtime repair is outside this documentation task.
  EVIDENCE:
  - artifacts/positional_meld_docs_20260919/docs-tests.log:1-7
  - artifacts/positional_meld_docs_20260919/html-build.log:1-1
  - artifacts/positional_meld_docs_20260919/site-check.log:1-1
  - artifacts/positional_meld_docs_20260919/examples.xml:1-1
  IMPACT: Documentation publication checks pass. Preserve the failed example evidence without claiming
    the runtime suite is green. Source-asset checks report stale agent-documentation/bind-guard fingerprints.
  NEXT: Audit the rendered code/downloads and refresh the derived documentation assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T21:56:08Z
  TYPE: MEASURE
  CLAIM: Final rendered audit finds zero old calls in 557 code blocks across 360 HTML files,
    137 Python downloads and all four example ZIPs. Source asset regeneration used current checkout
    version 0.2.43; all three source assets and both affected corpus fingerprints pass. Reviewed the
    complete 66-file diff and repeated the codemod check successfully. Runtime failures remain recorded
    separately, consistent with the owner's notice that runtime implementation is in progress.
  EVIDENCE:
  - artifacts/positional_meld_docs_20260919/publication-audit.json:1-8
  - artifacts/positional_meld_docs_20260919/source-assets-check.log:1-3
  - artifacts/positional_meld_docs_20260919/corpora-check.log:1-2
  - artifacts/positional_meld_docs_20260919/validation.md:1-49
  IMPACT: The requested documentation correction is complete and ready for owner review/commit;
    runtime implementation and hosted publication remain with their existing workflows.
  NEXT: Owner reviews and promotes the documentation changes with the ongoing runtime work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed the owner-authorized positional meld spelling sweep with a deterministic codemod: 150
replacements in 65 published lesson/helper scripts and the package quickstart. README already matched.
Canonical inputs, strict 294-page local HTML build, 39 docs tests, 35,501 links, rendered code and
downloads all pass. Source assets and src/other corpora are refreshed against the current checkout.
The lesson harness has 130 passes and three file/cache failures; one is confirmed permissions and
two remain unattributed while the owner's other runtime change is active. No runtime fix was made.
The task is in review; changes are uncommitted and no hosted documentation deployment occurred.
