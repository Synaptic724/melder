# Task: Use positional meld targets throughout published examples

## Metadata
- Task ID: TASK-2026-09-19-document-positional-meld-calls
- Story: none
- Status: in_progress
- Owner: codex
- Agent Name: workflows_1
- Priority: p2
- Created: 2026-09-19T21:44:14Z
- Updated: 2026-09-19T21:44:14Z

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
- from_state: ready
- to_state: in_progress
- transition_reason: Publication sources and the public positional target contract were verified.

## Steps / Checklist
- [x] Inspect README, docs assembly, lesson input roots and applicable example instructions.
- [ ] Generate a bounded dry-run codemod report and verify its proposed syntax-only changes.
- [ ] Apply the codemod and confirm idempotence and no remaining publication-input matches.
- [ ] Run documentation/example checks, rebuild generated publication outputs and refresh needed assets.
- [ ] Record final diff, validation evidence and handoff.

## Deliverables
- Consistent positional target spelling in the published tutorials and package quickstart.
- Auditable codemod with an explicit changed-file/call inventory.
- Rebuilt local documentation and validation results.

## Validation
- Planned: AST-preserving call normalization, zero remaining spell-keyword calls in publication
  inputs, codemod second pass, existing docs tests, relevant example harness and strict docs build.
- Source and generated-asset freshness checked through existing builders.

## Risks / Rollback Notes
- Read the Docs copies real example sources byte-for-byte, including helper files in downloads.
- README currently already uses positional targets; do not manufacture an unrelated edit.
- The owner/another agent has substantial compiler/source changes in flight; preserve those edits.
- Record original bytes/hashes for changed files and refuse concurrent edits during codemod application.

## Applicable Anti-Patterns
- [x] No blind repository-wide spelling replacement or hand-editing generated HTML.
- [x] No conversion of explicit machine IDs or changes to runtime API definitions.
- [ ] No successful build/test claim without executed results.

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

## Context / Handoff Summary
Owner authorized the documentation spelling sweep and codemod. README is already correct. Update
the four published lesson directories and package quickstart; docs builders generate the site and
downloads from those inputs. Leave runtime and test-only keyword coverage unchanged.
