# Task: Design the LLM support compilation pipeline

- Completed: 2026-08-30T22:07:25Z
- Summary: Owner accepted the three-corpus design, exclusions, manifest/index
  contract, and check-only CI recommendation; implementation promoted to
  STORY-2026-08-30-llm-support-compilation-pipeline.

## Metadata
- Task ID: TASK-2026-08-30-llm-support-compilation-pipeline-discovery
- Story: none
- Status: done
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T21:48:32Z
- Updated: 2026-08-30T22:07:25Z

## Objective
Design a deterministic, incremental repository-external build lane that compiles
full source, test, and other text corpora into three indexed LLM support bundles
with a maintainable manifest, README guidance, and commit-time GitHub Action.

## Ticket Contract
- ENTRY_GATE: Owner requested investigation and `attention_board.md` routes here.
- EXECUTION_BOUNDARY: Read-only inspection of `llm_support/`, repository
  workflow/build conventions, repository topology/configuration, and the external
  `code_grabber.py` reference. Only ContextCompass tracking/artifact files are writable.
- DEPENDENCIES: Existing build-asset runner, GitHub workflows, ignore rules,
  package metadata, and owner-defined three-corpus outcome.
- EXIT_GATE: Discovery specifies corpus boundaries, file/header/index formats,
  manifest schema, incremental algorithm, workflow triggers, exclusions,
  validation, and implementation file plan.
- FAILURE_ESCALATION: Record a decision request if corpus ownership is ambiguous
  or efficient regeneration requires behavior outside the owner-defined outputs.

## Scope Boundaries
- In scope:
  - `llm_full_src`, `llm_full_tests`, and `llm_full_other`
  - one text bundle and one index per corpus
  - `llm_support/README.md` and a shared manifest
  - deterministic exclusions for caches, generated outputs, binary assets, and noise
  - smart per-corpus regeneration and commit-time GitHub Action design
- Out of scope:
  - implementing the generator or workflow in this discovery task
  - publishing artifacts outside the repository
  - changing source, tests, or existing build-asset semantics

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepted the design and authorized implementation
  with the recommended check-only workflow.

## Steps / Checklist
- [x] Read the external code-grabber reference and current repository build/workflow conventions.
- [x] Inventory repository roots and classify source, tests, and other corpus membership.
- [x] Define bundle headers, exact index addressing, manifest schema, and exclusions.
- [x] Define per-corpus fingerprinting, selective regeneration, and GitHub Action triggers.
- [x] Produce and validate an implementation-ready discovery artifact.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- An implementation-ready LLM support pipeline design and exact file plan.
- `artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md`

## Files / Paths Impacted
- `context_compass/attention_board.md`
- `context_compass/artifact_board.md`
- This task.
- `context_compass/artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md`
- Product/repository files are read-only during discovery.

## Validation
- Tracked corpus census and encoding scan: pass.
- Artifact: 496 lines, zero prose lines over 120 characters.
- Machine-local path scan: zero matches.
- EOL-aware diff hygiene: pass.
- Implementation validation matrix is specified in the artifact.

## Risks / Rollback Notes
- A vague “other” corpus can accidentally include private, generated, binary,
  cache, or recursive LLM-support content; classification must be explicit.
- Commit-time regeneration can create a dirty working tree after a push unless
  the workflow contract clearly chooses check-only CI versus controlled write-back.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed
- [x] Notes quality maintained
- [x] Applicable anti-pattern checks are clear or escalated.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: implementation-lane acceptance

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - corpus classification and exclusions
  - deterministic indexed concatenation
  - manifest-driven incremental generation
  - GitHub Actions regeneration semantics
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: evidence-backed boundaries, format decisions, efficiency, and one-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-08-30T22:07:25Z
  TYPE: DECISION
  CLAIM: Owner accepted check-only CI and requested implementation with the
    generic build-repo-assets workflow plus build-src-assets rename.
  EVIDENCE:
  - Owner approval in the active conversation, 2026-08-30T22:07:25Z
  IMPACT: Discovery closes and routes to the implementation story/task.
  NEXT: Implement TASK-2026-08-30-implement-llm-support-compilation-pipeline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:01:52Z
  TYPE: DECISION_REQUEST
  CLAIM: Use a check-only GitHub Action by default. A GitHub Action runs after
    the commit exists, so auto-write-back cannot repair that commit; it creates
    a second bot commit and requires write permission, recursion controls,
    branch-policy exceptions, and race handling.
  EVIDENCE:
  - `.github/workflows/build-assets.yml:1-139`
  - `context_compass/artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md:350-395`
  IMPACT: Implementation can follow the safe existing pattern immediately once
    the owner confirms check-only versus bot write-back.
  NEXT: Obtain owner approval for the check-only workflow contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T22:01:52Z
  TYPE: MEASURE
  CLAIM: The implementation-ready discovery artifact is 496 lines, has zero
    over-120-character prose lines, contains no machine-local path, and passes
    EOL-aware diff hygiene. It records measured corpus counts, byte/line totals,
    encoding edge cases, exclusions, and a complete validation matrix.
  EVIDENCE:
  - `context_compass/artifacts/2026-08-30_llm_support_compilation_pipeline_discovery.md:1-496`
  IMPACT: The discovery exit gate is met and no implementation guess remains
    except the explicitly surfaced workflow write-policy decision.
  NEXT: Present the recommendation and exact file plan for owner review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:58:58Z
  TYPE: MEASURE
  CLAIM: Final proposed corpora are source 584 files/10.66 MB/270,707 content
    lines, tests 793/10.34 MB/298,535 lines, and other 2,269/21.19 MB/
    414,714 lines. A full tracked-file eligibility, byte-read, strict-decode,
    newline-normalization, and line-count pass completed in about 2.25 seconds
    locally over 42.19 MB.
  EVIDENCE:
  - `git ls-files`
  - `src/`
  - `tests/`
  - `context_compass/`
  IMPACT: Correct full input hashing is cheap enough for every CI run. Efficiency
    should target corpus-level write avoidance: unchanged bundle/index pairs are
    hash-checked but never rendered or rewritten. A changed monolithic corpus
    must be rewritten atomically; finer write granularity conflicts with the
    owner's one-file-per-corpus requirement.
  NEXT: Write the implementation-ready discovery artifact with exact formats,
    manifest schema, CLI, CI policy, and validation matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:55:25Z
  TYPE: FACT
  CLAIM: Proposed eligibility yields 3,647 files/42.19 MB: source 585/
    10.66 MB, tests 793/10.34 MB, other 2,269/21.19 MB. It excludes 651
    tracked assets/7.05 MB: eight generated source manifest/payload files,
    592 graph descriptors, 44 rendered SVG/placeholders, and seven non-code
    source assets. Encoding census is 3,534 strict UTF-8, 110 UTF-8 BOM, two
    UTF-16LE BOM artifacts, and one CP1252 Markdown ticket (the invalid UTF-8
    byte is the CP1252 `ç` in “façade”).
  EVIDENCE:
  - `git ls-files`
  - `context_compass/artifacts/dev_ops_typecheck_scan.json`
  - `context_compass/artifacts/spellbook_typecheck_report.txt`
  - `context_compass/tickets/tasks/completed/2026-05-20_lay_spell_compiler_foundation_task.md`
  IMPACT: The generator can be fail-loud and lossless at the text level with
    four explicit decoders (UTF-8, UTF-8 BOM, UTF-16LE BOM, CP1252 fallback);
    `errors="ignore"` is unnecessary and prohibited.
  NEXT: Define exact bundle/index/manifest records, fingerprint rules, selective
    write behavior, and CI versus auto-commit semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:53:21Z
  TYPE: FACT
  CLAIM: Raw tracked topology is 600 source files/14.51 MB, 793 test files/
    10.34 MB, and 2,905 other files/24.39 MB. The other corpus is dominated by
    ContextCompass (2,617 files/21.80 MB), which matches the owner's full-repo
    intent but requires README authority warnings. Source contains eight
    generated manifest/payload Python files totaling 3.80 MB; they duplicate
    canonical documents and are assets rather than source code. The generated
    graph descriptor lane contributes most of the repository's 601 JSON files.
  EVIDENCE:
  - `git ls-files`
  - `src/melder/_build_assets/`
  - `context_compass/system_docs/graph/`
  - `context_compass/system_docs/src_graph.md`
  IMPACT: Corpus rules must exclude generated source payload/manifests, graph
    descriptors, rendered SVGs, and `llm_support/` itself while retaining the
    assembled graph, ContextCompass policy/tickets, UX, architecture docs,
    workflows, and benchmark source in `other`.
  NEXT: Apply the proposed eligibility rules read-only, measure resulting
    counts/bytes/encodings, and identify any unsupported text.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:50:24Z
  TYPE: FACT
  CLAIM: Repository conventions support a tracked-file-first design.
    `.gitignore` already excludes caches, environments, build outputs, binary
    competitors, profiles, and runtime cache families; `.gitattributes`
    proves EOL must be handled explicitly. The system indexer supplies the
    reusable trust contract: 1-based inclusive ranges plus line count, exact
    byte SHA256, line-ending proof, idempotent write-if-changed, and stale
    refusal.
  EVIDENCE:
  - `.gitignore:1-225`
  - `.gitattributes:1-46`
  - `context_compass/tools/system_documents/index_document.py:1-527`
  - `pyproject.toml:120-240`
  IMPACT: Starting from sorted `git ls-files` removes ignored/untracked noise
    by construction; explicit rules are still required for tracked generated
    assets, binary/text eligibility, and recursive `llm_support` exclusion.
  NEXT: Measure tracked paths, extensions, sizes, and largest files by proposed
    source/test/other corpus.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:49:32Z
  TYPE: FACT
  CLAIM: The external reference supplies the desired full-file header pattern
    and basic extension/directory filters, but it walks unsorted filesystem
    state, decodes with `errors="ignore"`, swallows per-file failures, and has
    no index, manifest, fingerprint, self-output exclusion, or stale-check mode.
    Melder's build-asset lane provides the stronger maintenance model:
    deterministic render/write, source fingerprints, fast check mode, path-
    filtered CI, and explicit local regeneration.
  EVIDENCE:
  - `C:/Users/Mark/PycharmProjects/priv_commandops/Plans/code_grabber.py:1-194`
  - `.github/workflows/build-assets.yml:1-139`
  - `src/melder/_build_assets/_build_asset_runner.py:1-399`
  IMPACT: The new system should reuse the reference's readable file headers but
    adopt Melder's fail-loud deterministic/checkable asset contract instead of
    copying its traversal/error behavior.
  NEXT: Read ignore/EOL/package/index conventions, then inventory tracked
    repository paths and classify the three corpora.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T21:48:32Z
  TYPE: PLAN
  CLAIM: Inspect the external full-file concatenator, then compare it with the
    repository's deterministic build-asset and workflow patterns before defining
    the three corpus contracts and incremental manifest.
  EVIDENCE:
  - Owner-supplied path `C:/Users/Mark/PycharmProjects/priv_commandops/Plans/code_grabber.py`
  - `llm_support/`
  IMPACT: The design will reuse proven local conventions while preventing
    recursive output capture and unnecessary full rebuilds.
  NEXT: Read the reference implementation and current build/workflow entrypoints.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Discovery accepted and promoted. Recommended implementation is a stdlib-only
`llm_support/_builder.py`, three committed UTF-8/LF text bundles, three
Markdown range indexes, one deterministic JSON manifest, a ContextCompass-first
README, contract tests, and a check-only push/PR/manual GitHub Action. Continue
from the linked implementation task.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
