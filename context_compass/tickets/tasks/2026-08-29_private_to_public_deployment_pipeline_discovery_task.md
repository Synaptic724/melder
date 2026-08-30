# Task: Design the private-to-public Melder deployment pipeline

## Metadata
- Task ID: TASK-2026-08-29-private-to-public-deployment-pipeline-discovery
- Story: none
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p1
- Created: 2026-08-29T21:21:08Z
- Updated: 2026-08-29T22:22:13Z

## Objective
Produce an evidence-backed current-tree and full-history publication audit for
`melder_private`, preserving tickets and meaningful commit history while
identifying only material that must not become public.

## Ticket Contract
- ENTRY_GATE: The task is routed by one active attention-board row before discovery.
- EXECUTION_BOUNDARY: Read the working tree and all reachable Git objects; write
  only this task and ContextCompass routing state during the audit.
- DEPENDENCIES: Canonical AGPL decision and private-to-public dependency direction
  in the project special instructions.
- EXIT_GATE: Named instructions, competitor-source risk, secret shapes, local
  machine data, binary/generated outputs, and suspicious history are classified
  with reproducible automated evidence.
- FAILURE_ESCALATION: Record a BLOCKER if either repository cannot be read; do not
  copy, delete, commit, push, or rewrite either repository.

## Scope Boundaries
- In scope:
  - audit every public top-level surface and non-ignored path
  - identify private-only, generated, stale, sensitive, and publication-safe content
  - determine what must remain available when `melder` becomes the sole code repo
- Out of scope:
  - deleting, moving, staging, committing, pushing, publishing, or changing remotes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Automated path, history, secret, competitor, and large-blob
  audits are complete and the targeted sanitation plan is ready for approval.

## Steps / Checklist
- [x] Verify both repository roots and their Git topology.
- [x] Run the filtered filesystem hash comparison.
- [x] Report matching, changed, missing, extra, and excluded-public paths.
- [x] Inventory every public top-level surface and non-ignored file group.
- [x] Compare source-only and target-only paths without pre-filtering.
- [x] Classify each surface as keep, remove, relocate, or review.
- [x] Report the exact pre-push cleanup boundary.
- [x] Locate named private instructions across current and historical trees.
- [x] Distinguish benchmark adapters from copied competitor source.
- [x] Scan reachable blobs for credential, key, endpoint, and local-path patterns.
- [x] Inventory binary profiles, oversized outputs, and suspicious extensions.
- [x] Report the smallest exact history-removal set, if any.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- Evidence-backed keep/remove/relocate/review inventory for the public repository.

## Files / Paths Impacted
- `context_compass/tickets/tasks/2026-08-29_private_to_public_deployment_pipeline_discovery_task.md`
- `context_compass/attention_board.md`
- Both repository trees remain read-only during comparison.

## Validation
- Read-only PowerShell SHA-256 filesystem comparison completed with exit code 0.
- Gitleaks v8.30.0 scanned all Git history with full redaction: 2,220 commits,
  approximately 260 MB, two findings.
- Both Gitleaks findings were structurally verified false positives: one prose
  list and one `self.<attribute>` assignment with no string literal.
- Tests: Not run; no product code changed.

## Risks / Rollback Notes
- A broad copy can leak ContextCompass state, private artifacts, IDE files, or
  repository history.
- Exclusions are explicit and the script reports excluded private-only paths found
  in the public repository rather than silently ignoring their presence.

## Applicable Anti-Patterns
- [ ] No direct private-branch merge into the public repository.
- [ ] No denylist-only publication boundary.
- [ ] No public-repository writes without explicit owner approval.
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated if needed
- [x] Validation status recorded
- [ ] Unknown-first discipline followed
- [ ] Notes quality maintained
- [ ] Applicable anti-pattern checks are clear or escalated
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - private-to-public repository promotion
  - public packaging, CI, and release boundaries
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes

- DATETIME: 2026-08-29T21:22:38Z
  TYPE: FACT
  CLAIM: The private and public directories are independent Git repositories.
    Private is on `codex_features2` and targets `Synaptic724/melder_private`;
    public is on `dev` and targets `Synaptic724/melder`. The public worktree is
    not a release candidate: the manual copy appears as a large uncommitted replacement,
    including untracked `context_compass/` and `profiles/` trees. This was measured
    with `git status --short --branch` in both roots.
  EVIDENCE:
  - `.git/HEAD:1-1`
  - `.git/config:13-30`
  - `../melder/.git/HEAD:1-1`
  - `../melder/.git/config:10-22`
  IMPACT: Directly committing or pushing the manually copied public worktree risks
    publishing private coordination state and bypasses any reproducible release boundary.
  NEXT: Inventory tracked and untracked top-level surfaces in both repositories and
    classify the intended public allowlist.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:16:40Z
  TYPE: FACT
  CLAIM: The ignored competitor source trees for dependency-injector, Dishka,
    and Lagom are present locally under `benchmarks/competitors/`, but no path
    from that tree or those package names has ever been committed on a reachable
    ref. The committed benchmark code contains adapters and imports, not copied
    competitor source.
  EVIDENCE:
  - `.gitignore:192-192`
  - `git -C . rev-list --objects --all`
  IMPACT: Competitor source requires no history rewrite. Preserve the ignore rule
    and do not force-add that directory.
  NEXT: Keep benchmark harness code; remove only generated benchmark artifacts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:16:40Z
  TYPE: MEASURE
  CLAIM: Gitleaks v8.30.0 scanned approximately 260 MB across 2,220 Git-history
    commits and reported two generic-key candidates. Both are false positives:
    one is unassigned prose and one assigns a `self` attribute with no quoted
    or literal value. No verified plaintext credential, token, or private-key
    finding remains.
  EVIDENCE:
  - `git -C . log -p -U0 --full-history --all`
  IMPACT: There is no evidenced live secret requiring credential rotation. Binary
    historical databases remain opaque and are removed by path rather than trusted.
  NEXT: Purge historical database paths and rerun Gitleaks after rewriting.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T22:16:40Z
  TYPE: FACT
  CLAIM: Historical publication blockers are path-concentrated. They include
    ContextCompass SQLite `user.db`, `system.db`, and `user_defined.db`
    versions; private GTM/mission/psychology documents and repeated GTM detail in
    one ticket; legacy agent trees (`codex*`, `gemini`, old ContextCompass
    copies); raw benchmark profiles/results; a deleted source-snapshot archive;
    and local absolute paths across historical prose/results.
  EVIDENCE:
  - `git -C . rev-list --objects --all`
  - `git -C . cat-file --batch-check`
  - `context_compass/tickets/tasks/2026-07-25_gtm_pivot_merge_task.md:1-204`
  IMPACT: Sanitation can be deterministic and path/text driven. It does not
    require reviewing 2,200 commits individually or removing canonical tickets.
  NEXT: Execute the approved removal manifest only in a disposable fresh clone.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Proposed Targeted Sanitation Plan

### Phase 0: Freeze and prove recoverability
- Keep the current repository private and untouched.
- Create a verified mirror/bundle backup and record current branch SHAs.
- Never run history rewriting in this working directory.

### Phase 1: Owner-approved removal manifest
- Remove all historical SQLite storage beneath
  `context_compass/system/storage/sqlite/`.
- Remove private instruction histories and legacy path variants for
  `<private-strategy-doc>`, `<private-strategy-doc>`, `mission`,
  `psychology`, and `behaviours`.
- Remove `context_compass/tickets/tasks/2026-07-25_gtm_pivot_merge_task.md`,
  which reproduces pricing and proprietary strategy details.
- Redact GTM-only passages from otherwise valuable tickets rather than deleting
  those tickets.
- Remove redundant legacy agent/workspace roots:
  `codex/`, `codex_agent_2/`, `codex_agent_3/`, `codex_todo/`,
  `gemini/`, `ai_agents/`, `.context_compass/`,
  `context_compass_old/`, `_to_delete/`, `workspace/`, `scratch/`,
  `github_intake/`, and `work_management/`.
- Remove machine/output-only roots and history:
  `profiles/`, `baseline.txt`, root `experimentation/`,
  `performance_hunt/`, `.venv_linux/`, and stale diagnostic text dumps.
- Remove generated benchmark result/profile paths while retaining benchmark
  Python harnesses and documentation.
- Replace `<local-path>`, `<local-path>`, and remaining private
  workspace prefixes with a neutral `<local-path>` marker.

### Phase 2: Rehearsal rewrite
- Install `git-filter-repo` only for a disposable fresh clone.
- Run `git filter-repo --analyze`.
- Apply the exact path-removal manifest, then the exact text replacements.
- Inspect only commit subjects matching private GTM/persona terms and rewrite
  those specific subjects; do not blanket-replace ordinary uses of `mission`.
- Push nothing during rehearsal.

### Phase 3: Automated proof
- Rerun Gitleaks across all rewritten refs.
- Require zero forbidden paths, database extensions, private instruction names,
  local absolute paths, and competitor-source paths.
- Re-run the large-blob inventory and confirm only intentional generated Melder
  assets remain.
- Compare the rewritten `prod` source tree with the original `prod` tree
  outside the approved removal/redaction set.
- Run build-asset checks, supported unit/component/integration tests, build the
  wheel and sdist, and inspect archive contents.

### Phase 4: Public cutover
- Preserve the old public repository state on a backup branch.
- Push only the verified rewritten `prod` history to a migration branch in
  `melder`; never use `git push --mirror`.
- Review the migration branch on GitHub before changing the default branch.
- Publish to PyPI only from a tagged, CI-green commit in the sanitized public
  repository.

- DATETIME: 2026-08-29T22:06:21Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: The earlier recommendation treated tickets and broad ContextCompass
    history as private by default. The owner did not authorize that boundary and
    explicitly wants ticket and commit history retained. The audit must be
    content-specific: remove only named private instructions, unauthorized copied
    code, secrets, machine-local data, or other specifically evidenced material.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-29_private_to_public_deployment_pipeline_discovery_task.md:11-37`
  IMPACT: Do not propose a clean slate or directory-wide history purge merely
    because the history is large or messy.
  NEXT: Run automated all-ref path, blob-pattern, binary, and competitor-code scans.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:58:24Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Three paths exist. Publishing the private repository after tip-only
    cleanup is rejected because history remains exposed. A clean public snapshot
    is safest but provides no public evolution history. A positive-path filtered
    history preserves most public source evolution while removing private paths,
    but rewrites commit IDs and requires payload/message audits. Recommendation:
    keep `melder_private` as a frozen private archive, migrate a filtered public
    history into `melder`, then make `melder` the sole active code repository.
  EVIDENCE:
  - `git -C . rev-list prod`
  - `git -C . log prod -- <public paths>`
  - `git -C . log prod -- <private paths>`
  IMPACT: No commits are lost because the original private archive remains intact;
    public users receive meaningful source history without private file history.
  NEXT: Owner chooses filtered-history migration or clean-snapshot migration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:57:47Z
  TYPE: MEASURE
  CLAIM: Private `prod` contains 2,274 commits. Of those, 1,968 touch candidate
    public paths; 249 touch private paths; 147 touch both; and 102 are
    private-only. A positive-path history extraction can therefore retain most
    source evolution while dropping private-only commits. It is not sufficient by
    itself: ten commits changed generated system-document payloads under
    `src/melder`, and commit subjects include private ContextCompass, psychology,
    mission, ticket, and artifact terminology.
  EVIDENCE:
  - `git -C . rev-list prod`
  - `git -C . log prod -- <public paths>`
  - `git -C . log prod -- <private paths>`
  - `src/melder/_build_assets/_system_documents/_builder.py:542-616`
  IMPACT: Making `melder_private` public as-is is unsafe. A filtered-history
    migration is feasible and preserves most useful commits, but it must also
    remove historical generated payloads, re-add clean generated assets, and audit
    or rewrite commit messages. Every resulting commit ID changes.
  NEXT: Present the private-archive, clean-snapshot, and filtered-history options
    with one recommendation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:56:04Z
  TYPE: DECISION_REQUEST
  CLAIM: The owner may replace the two-repository model with one public repository
    but wants to preserve the private repository's commit history. Current-tree
    cleanup and history publication are separate decisions: deleting a path now
    does not remove its earlier blobs or commits.
  EVIDENCE:
  - `.git/HEAD:1-1`
  - `.git/config:13-30`
  IMPACT: Publishing `melder_private` without history filtering exposes all
    historical private paths. A positive-path history extraction may preserve the
    public code's authorship and evolution while changing commit IDs and dropping
    private-only commits.
  NEXT: Measure total history, public-path history, private-path history, branches,
    tags, and commit-message exposure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:50:28Z
  TYPE: PLAN
  CLAIM: The public retention boundary has four classes. REMOVE private
    ContextCompass state, profile/baseline outputs, raw benchmark artifacts, UX
    control maps, and ignored local debris. KEEP source, supported tests and
    fixtures, user documentation, runnable examples, licensing, packaging, and
    benchmark code. RELOCATE the six source-system document/index files plus graph
    maintenance inputs before removing ContextCompass because the build asset
    currently ingests them. REVIEW the generic roadmap and replace the obsolete
    publication workflow with current build/CI workflows.
  EVIDENCE:
  - `../melder/baseline.txt:1-140`
  - `../melder/UX_and_AIX_experiences/AGENTS.md:1-114`
  - `src/melder/_build_assets/_system_documents/_builder.py:80-172`
  - `src/melder/_build_assets/_system_documents/_builder.py:374-498`
  - `.gitattributes:1-45`
  - `pyproject.toml:86-237`
  IMPACT: A blind `git add .` is unsafe. The public repository can become the
    sole code repo after the private state is removed and the small build-input
    dependency is relocated and regenerated.
  NEXT: Ask the owner to approve the retention boundary before any file mutation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:49:40Z
  TYPE: MEASURE
  CLAIM: The unfiltered private-`prod` to public-filesystem comparison contains
    exactly 18 source-only tracked files and one target-only non-ignored file.
    Source-only is one required build-assets workflow, four private special
    instructions, and thirteen root experimentation files. Target-only is
    `tests/experiments/cprofile_testing/results/.gitignore`. The four special
    instructions and thirteen experiments should stay absent; the workflow is the
    only missing public candidate.
  EVIDENCE:
  - `git -C . ls-tree -r --name-only prod`
  - `git -C ../melder ls-files --cached --others --exclude-standard`
  - `git -C . show prod:.github/workflows/build-assets.yml`
  IMPACT: The user's observation was correct: the prior allowlist diff hid the
    missing files. None of the hidden private files should be copied. Only the
    build-assets workflow needs restoration or replacement.
  NEXT: Finish the keep/remove/relocate/review classification for the common
    public tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:45:01Z
  TYPE: DECISION
  CLAIM: The owner corrected the filtered comparison: it suppressed relevant
    filesystem differences before reporting them. The active goal is now a full
    pre-push retention audit because `melder` may replace `melder_private` as
    the sole Melder code repository.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-29_private_to_public_deployment_pipeline_discovery_task.md:11-37`
  IMPACT: Reopen discovery, inventory without an allowlist filter, and classify
    public retention before proposing any cleanup.
  NEXT: Compare all top-level surfaces and all non-ignored paths in both trees.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:37:18Z
  TYPE: MEASURE
  CLAIM: After excluding private-only and generated surfaces, the two working
    filesystems contain 1,943 managed files each. All 1,943 SHA-256 hashes match;
    there are zero changed, source-only, or target-only managed paths. Nine
    excluded paths are present in the public filesystem: `.coverage`, `.idea`,
    `.junie`, `.pytest_cache`, `.ruff_cache`, `.venv_new`, `baseline.txt`,
    `context_compass`, and `profiles`.
  EVIDENCE:
  - `read-only PowerShell Get-FileHash comparison, exit code 0`
  - `../melder/context_compass/AGENTS.MD:1-1`
  - `../melder/baseline.txt:1-1`
  IMPACT: The intended public file content is already identical. No recopy is
    needed. The only filesystem cleanup required before publication is removal or
    exclusion of the nine private/generated paths; `context_compass`, `profiles`,
    and `baseline.txt` are the non-ignored paths visible to Git.
  NEXT: Ask the owner to accept the diff result before any cleanup or copy action.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:35:48Z
  TYPE: DECISION
  CLAIM: The owner narrowed this lane to a read-only filesystem diff script. All
    deployment-pipeline, authentication, CI, PyPI, and publication design is out of
    scope. ContextCompass and its special instructions are private-only and must not
    be treated as public payload.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-08-29_private_to_public_deployment_pipeline_discovery_task.md:11-37`
  IMPACT: Stop architecture discovery and produce only the filtered hash comparison.
  NEXT: Run the comparison script over approved surfaces and report its categories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:31:57Z
  TYPE: FACT
  CLAIM: Private `prod`, `preprod`, and `dev` all resolve to commit
    `660359fb9`; that commit is two commits ahead of the checked-out
    `codex_features2` branch. The candidate public working files match private
    `prod` exactly except that the committed `.github/workflows/build-assets.yml`
    is missing from both working trees. Private `prod` also carries the current
    package version `0.1.2` and AGPL metadata.
  EVIDENCE:
  - `git -C . for-each-ref refs/heads refs/remotes`
  - `git -C . rev-list --left-right --count prod...codex_features2`
  - `git -C . diff --name-status prod -- <candidate public paths>`
  - `src/melder/__version__.py:1-12`
  - `pyproject.toml:1-12`
  IMPACT: Private `prod` is the correct release input, but the exporter must read
    the immutable `prod` commit through Git rather than copy the checked-out
    branch or working tree. This automatically restores committed release files
    that a local working tree may have deleted.
  NEXT: Define the exact allowlist, public-only overlays, audit rules, and
    cross-repository authentication model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:30:52Z
  TYPE: FACT
  CLAIM: The supported test architecture is unit, component, and integration,
    with shared helpers, mocks, and selected experimentation benches feeding those
    tiers. The default pytest configuration roots collection at all of `tests/`
    and does not exclude `tests/experimentation`, where 24 tracked modules match
    pytest's `test*.py` collection pattern. A bare `pytest` therefore includes
    experimental/performance probes beyond the three supported release tiers.
  EVIDENCE:
  - `pyproject.toml:204-223`
  - `context_compass/system_docs/tests_architecture.md:10-23`
  - `context_compass/system_docs/tests_architecture.md:200-346`
  - `context_compass/system_docs/tests_components.md:277-484`
  IMPACT: The public export must retain helper and mock dependencies, including
    experimentation modules imported by supported tests, but CI should invoke
    `pytest tests/unit tests/component tests/integration` explicitly. Profiling
    tools and untracked result folders under `tests/experiments` should not enter
    the release gate.
  NEXT: Inspect private branch promotion topology and version/build behavior to
    choose the source ref and public release-branch model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:28:39Z
  TYPE: FACT
  CLAIM: A clean public checkout cannot currently reproduce the committed system
    document build asset. The universal runner discovers every immediate
    `_builder.py` and checks it. The system-document builder hard-codes
    `context_compass/system_docs` as its input, fingerprints those indexes, and
    embeds verified documents verbatim into tracked Python payload modules. When
    that source tree is absent, the builder renders unavailable entries whose
    fingerprint differs from the committed available-document manifest.
  EVIDENCE:
  - `src/melder/_build_assets/_build_asset_runner.py:189-317`
  - `src/melder/_build_assets/_system_documents/_builder.py:80-172`
  - `src/melder/_build_assets/_system_documents/_builder.py:374-498`
  - `src/melder/_build_assets/_system_documents/_builder.py:542-616`
  IMPACT: Excluding ContextCompass while retaining the current builder makes the
    public build-asset check fail. Excluding only the directory also does not remove
    its content: generated payloads presently retain ContextCompass source labels
    and 28 `artifacts/` references. Public source maps must be deliberately
    promoted and audited, then the builder and line-ending rule must point at the
    public location.
  NEXT: Verify the supported test tiers and package-build behavior, then define the
    positive export manifest and CI stages around the promoted system-map inputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:26:18Z
  TYPE: MEASURE
  CLAIM: The manual copy is byte-for-byte complete across the candidate public
    surfaces, including ignored build/runtime debris. Hash comparison found zero
    differing paths across 2,497 source files, 4,019 test files, 327 benchmark
    files, 467 example files, and 77 architecture files. Git classifies 5,598 of
    those copied files as ignored; only 1,788 corresponding candidate files are
    tracked by the private repository, plus one untracked test-results path.
  EVIDENCE:
  - `Get-FileHash SHA256 across candidate surfaces in both repository roots`
  - `git -C . ls-files --others --ignored --exclude-standard`
  - `git -C ../melder ls-files --others --ignored --exclude-standard`
  IMPACT: The copied content is not corrupt, but filesystem copying transfers far
    more than the release payload. The exporter should select committed paths from
    a source commit, not walk the private working directory.
  NEXT: Inspect packaging metadata, test collection boundaries, build-asset inputs,
    ignore rules, and absent CI workflows to define the release gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-29T21:23:39Z
  TYPE: MEASURE
  CLAIM: The public repository baseline tracks only seven top-level release files
    or groups, while the current worktree overlays most of the private repository.
    The private tracked tree includes 2,617 ContextCompass files, 25 profile files,
    173 benchmark files, 790 test files, and 600 source files. The public manual copy
    therefore has no enforceable publication boundary; it is a broad filesystem copy
    placed over a minimal historical repository.
  EVIDENCE:
  - `git -C . ls-files | group by top-level path`
  - `git -C ../melder ls-files | group by top-level path`
  - `git -C ../melder diff --stat`
  IMPACT: Publication must be rebuilt around an explicit positive export manifest.
    Cleaning the current public worktree with a denylist would be difficult to prove
    complete and would remain unsafe as the private repository evolves.
  NEXT: Hash-compare only candidate public surfaces and identify copied caches,
    experiments, and private-only dependencies inside those surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Ticket history and meaningful commits remain presumptive KEEP. The owner approved
local execution against `melder_private`, with no commit or remote action. Active
implementation routes through
`tickets/tasks/2026-08-29_sanitize_publication_history_task.md`.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
