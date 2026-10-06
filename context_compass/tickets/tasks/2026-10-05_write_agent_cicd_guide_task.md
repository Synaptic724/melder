# Task: Give agents a CI/CD guide folder they can read and extend

## Metadata
- Task ID: TASK-2026-10-05-write_agent_cicd_guide
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p2
- Created: 2026-10-05T11:45:56Z
- Updated: 2026-10-05T20:51:52Z

## Objective
A folder, .github/ci_cd/, that explains from the code what every workflow, job, script, Python manifest and
ruleset is for, how they connect, how to extend each of them and how to validate a change; a special
instruction so every onboarding agent learns the guide exists and when to read it; the tests architecture
document's CI section pointing at it; and a contract test that keeps the guide complete as CI grows.

## Ticket Contract
- ENTRY_GATE: Owner chat directives, 2026-10-05 about 11:50Z: "did you add instructions for other agents on how
  to use the CICD and how it works make a folder for that please"; "this way they can easily understand what
  everything is for and extend it"; "you can document that in src_architecture or someshit in a good spot".
  Active board row: agent_cicd_guide.
- EXECUTION_BOUNDARY: new .github/ci_cd/ documents; a new special instruction,
  context_compass/special_instructions/ci_cd_guide.md; the CI section of
  context_compass/system_docs/tests_architecture.md and its index; one pointer line in .github/BRANCH_WORKFLOW.md;
  one guide-coverage test in tests/unit/github_workflows/test_workflow_contracts.py; the build-asset and
  llm_support rebuild as the last write. No workflow or script behaviour changes; no src/ change.
- DEPENDENCIES: describes the manifest-driven CI of
  tickets/tasks/2026-10-04_use_newest_patch_in_single_version_ci_jobs_task.md, uncommitted in the same tree.
- EXIT_GATE: every workflow and script is described (the coverage test passes), every cited path exists, the
  workflow suite passes here, assets and bundles are current, and the owner accepts or redirects.
- FAILURE_ESCALATION: Record CONFLICT if a workflow's behaviour contradicts .github/BRANCH_WORKFLOW.md.

## Scope Boundaries
- In scope: the guide folder, the special instruction, the tests architecture CI section, one coverage test.
- Out of scope: changing CI behaviour; src_architecture (it describes the library runtime and ships in the
  wheel, so CI does not belong there).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-05T12:07:51Z) the guide, the special instruction, the tests architecture section and the
  coverage tests landed and validated here, assets and bundles current (Notes 4-8); the owner's commit, push and
  acceptance remain.
- previous: draft -> in_progress (2026-10-05T11:45:56Z) the owner's directives above.

## Steps / Checklist
- [x] Read every workflow, script and ruleset; note what each is for (Notes 2-3).
- [x] Write .github/ci_cd/ (map, manifests, extending, validating) (Note 4).
- [x] Add the special instruction, the tests architecture section and the BRANCH_WORKFLOW pointer (Note 4).
- [x] Add the guide-coverage tests; run the workflow suite and mutation checks (Note 5).
- [x] Rebuild assets and llm_support last; run both checks (Note 8).
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.
- [ ] Owner: commit (git add -A: the six guide pages are untracked) and push; keep the special instruction local
      or force-add it (Note 6); accept or redirect.

## Deliverables
- .github/ci_cd/ guide documents; context_compass/special_instructions/ci_cd_guide.md; the tests architecture CI
  section; two contract tests.

## Files / Paths Impacted
- .github/ci_cd/ (new)
- context_compass/special_instructions/ci_cd_guide.md (new)
- context_compass/system_docs/tests_architecture.md and tests_architecture_index.md
- .github/BRANCH_WORKFLOW.md
- CONTRIBUTING.md (one pointer; recorded in Note 4)
- tests/unit/github_workflows/test_workflow_contracts.py

## Validation
- 2026-10-05, device VM, CPython 3.14.7t (Notes 5, 7 and 8):
  - tests/unit/github_workflows: 500 passed, before and after the re-onboard; three guide mutations each caught
    and restored byte for byte.
  - tests_architecture_index.md current (32 sections over 933 lines); "CI/CD Pipeline" slices to 232-248.
  - Build assets rebuilt last, --check three OK lines (v0.2.8227); llm_support rebuilt with --include-untracked,
    --check --include-untracked three OK lines. No .git/index.lock.
  - Owner-requested rebuild at 20:50Z (Note 10): asset runner exit 0 in 63 s, llm_support UNCHANGED; both
    checks OK.
- Not run: the hosted workflows (this lane changed no CI behaviour), and a tracked-only llm_support --check
  before the six guide pages are committed.

## Risks / Rollback Notes
- Risk: a guide drifts from the workflows; the coverage test catches missing entries, not wrong prose.
- Rollback: delete .github/ci_cd/ and the special instruction; revert the section, pointer and test.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: not applicable (no artifacts planned)

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
- DATETIME: 2026-10-05T11:45:56Z
  TYPE: DECISION
  CLAIM: Placement. The guide lives in .github/ci_cd/, beside the files it explains, so an agent editing CI finds
    it and the llm_support bundles carry it. A short special instruction tells every onboarding agent it exists
    and to read it before touching .github/, requires-python or Melder's dependencies, without adding the whole
    guide to each onboarding read. The system-document home is tests_architecture.md, which already owns the
    CI entrypoint and the qualification flow; src_architecture.md covers the library runtime and ships in the
    wheel as melder.__architecture__, so CI does not belong there.
  EVIDENCE:
  - context_compass/system_docs/tests_architecture.md:174-189
  - context_compass/special_instructions/README.md:1-16
  IMPACT: Fixes where each piece goes before writing.
  NEXT: Read every workflow, script and ruleset and record what each is for.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T11:49:05Z
  TYPE: FACT
  CLAIM: Read every workflow, script, ruleset and BRANCH_WORKFLOW.md. Three entry workflows start runs: ci.yml
    (PRs into the four permanent branches and manual runs; branch-policy routes, merge-ready is the one required
    status), release-candidate.yml (pushes to release_candidate: authorize, source proof, build, TestPyPI upload,
    per-release install probes, package-ready) and python-publish.yml (published releases or manual prod runs:
    release gate, fresh checks, build, PyPI). Eight reusable workflows each prove one thing. Nine standard-library
    scripts hold the policy, each loaded by path in tests/unit/github_workflows (smoke_wheel.py only through the
    distribution contract test). Rulesets are reviewed payloads, active only once applied with gh api.
  EVIDENCE:
  - .github/workflows/ci.yml:19-158
  - .github/scripts/ci_policy.py:104-174
  - .github/workflows/release-candidate.yml:17-154
  - .github/workflows/python-publish.yml:18-121
  IMPACT: The guide can describe each file from its source.
  NEXT: Record the extension hazards found on the way.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T11:49:05Z
  TYPE: RISK
  CLAIM: Three hazards an extender must know. (1) Melder's first runtime dependency (LogXide) breaks two
    installed-package probes as written: build-distributions installs the wheel with uv pip --no-deps and
    testpypi_candidate.py probe-install with pip --no-deps --no-index, then smoke_wheel.py imports melder; the
    speed jobs import Melder from the checkout through PYTHONPATH, so the speed manifest must pin it too. (2)
    Raising the floor beyond 3.14 also needs verify_distributions.py's literal Requires-Python ">=3.14" check and
    run_runtime_tests.py's (3, 14) check changed. (3) BRANCH_WORKFLOW.md still says the RC probes use a
    "discovered" matrix.
  EVIDENCE:
  - .github/workflows/build-distributions.yml:61-67
  - .github/scripts/testpypi_candidate.py:168-188
  - .github/scripts/verify_distributions.py:72-80
  - .github/scripts/run_runtime_tests.py:10-16
  - .github/BRANCH_WORKFLOW.md:341-343
  IMPACT: The guide records (1) and (2) as checklists; (3) is corrected in this pass. Changing the probes is out
    of scope until the dependency lands.
  NEXT: Write .github/ci_cd/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-05T11:55:39Z
  TYPE: FACT
  CLAIM: Applied. .github/ci_cd/ holds six pages: README (start here, the three entry flows, six rules),
    workflows (every workflow and job, the route table, what each proves), scripts (every script with its
    operations, callers and tests; rulesets; FUNDING), python_versions (manifest format, consumers, recipes for a
    release, the floor, a pin, a runtime dependency, the speed release and the helper release), extending (the
    rules every workflow follows and recipes for a required job, a stage, a route, a speed test, a script) and
    validating (pre-handoff steps, failed-run table, environment notes). A special instruction,
    special_instructions/ci_cd_guide.md, points every onboarding agent at it with four standing rules.
    tests_architecture.md gains "### CI/CD Pipeline" under the system boundary (index regenerated; it slices by
    that name). BRANCH_WORKFLOW.md gains a pointer and loses its stale "discovered" matrix line; CONTRIBUTING.md
    points at the guide. Two contract tests: every workflow, script and ruleset is named in the guide, and the
    README links every page and every relative link resolves.
  EVIDENCE:
  - .github/ci_cd/README.md:1-59
  - .github/ci_cd/python_versions.md:96-109
  - context_compass/special_instructions/ci_cd_guide.md:1-26
  - context_compass/system_docs/tests_architecture.md:232-248
  - tests/unit/github_workflows/test_workflow_contracts.py:776-799
  IMPACT: An agent can find, read and extend CI from one folder, and a new CI file without a guide entry fails.
  NEXT: Validate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T11:55:39Z
  TYPE: MEASURE
  CLAIM: Device VM, CPython 3.14.7t: tests/unit/github_workflows gave 500 passed (the two new guide tests
    included). Mutations, each restored byte for byte and each caught: smoke_wheel.py's backticked entries removed
    (coverage test failed), a link to a missing page (link test failed), the README's link to a page dropped
    (link test failed). The tests_architecture index regenerated with 32 ranges validated, and slicing
    "CI/CD Pipeline" returns lines 232-248.
  EVIDENCE: tests/unit/github_workflows/test_workflow_contracts.py:776-799
  IMPACT: The guide is complete for today's files and stays complete as CI grows.
  NEXT: Run the build-asset runner and the llm_support builder last, with their checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T12:04:32Z
  TYPE: FACT
  CLAIM: The special instruction is local-only and `git add -A` will not pick it up: the owner's
    .git/info/exclude ignores /context_compass/special_instructions/, and README.md is the only tracked file
    there (agent_contribution_guide.md and codex_mcp.md are local too). Every agent on this checkout still reads
    it, because onboarding sweeps the working tree; a fresh clone finds the guide through the tracked pointers in
    BRANCH_WORKFLOW.md, CONTRIBUTING.md and tests_architecture.md. Force-adding it or changing the rule is the
    owner's call. Also corrected Note 4: the file is 26 lines (it cited 1-29). Gate deviation: this check-ignore
    ran right after a compaction, before the REONBOARD (read-only, nothing written); the re-onboard then
    completed and self-certified under the owner's standing rule.
  EVIDENCE:
  - .git/info/exclude:36-36
  - context_compass/special_instructions/ci_cd_guide.md:1-26
  IMPACT: Owner-owed decision: keep the instruction local like its siblings, or `git add -f` it.
  NEXT: Check the tests_architecture CI section for paths into context_compass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T12:05:21Z
  TYPE: FACT
  CLAIM: The tests_architecture additions cite only repository paths a reader of the shipped document can resolve
    (.github/ and tests/), never a path into context_compass: the CI/CD Pipeline section, the
    .github/ci_cd/README.md source line and the handoff entry. A search for the package markers
    (context_compass/, agent_onboarding/, tools/system_documents/, system_docs/, patches/active/,
    special_instructions, index_document.py) finds only two older lines, 42 and 64, that name a sibling index
    file; neither is from this lane. index_document.py --check: current, 32 sections over 933 lines.
  EVIDENCE:
  - context_compass/system_docs/tests_architecture.md:232-248
  - context_compass/system_docs/tests_architecture.md:859-859
  - context_compass/system_docs/tests_architecture.md:872-873
  IMPACT: The section obeys the produced-document portability rule; nothing to fix in this lane.
  NEXT: Run both builder checks for fresh evidence, then move the ticket to review.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-05T12:07:51Z
  TYPE: MEASURE
  CLAIM: Final state, re-measured on the device VM (CPython 3.14.7t) after the re-onboard, with no source,
    workflow or test change since Note 5: tests/unit/github_workflows 500 passed; the build-asset runner
    --check printed three OK lines (agent documentation, bind guard, system documents; v0.2.8227); llm_support
    --check --include-untracked printed three OK lines (src, tests, other). Both builders had been rerun as the
    last writes of the change set before the compaction; the ticket and board edits since are outside every
    bundle, which the checks confirm. Untracked for the owner's commit: the six .github/ci_cd/ pages, the ten
    manifests of the CI ticket and two tickets. No .git/index.lock.
  EVIDENCE: tests/unit/github_workflows/test_workflow_contracts.py:776-799
  IMPACT: The change set is complete and current; the owner's commit, push and acceptance remain.
  NEXT: Owner: git add -A and push; decide on the special instruction (Note 6); accept or redirect.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T20:49:12Z
  TYPE: FACT
  CLAIM: The owner asked for one more asset rebuild because a ticket was made. The only file changed since this
    ticket's last edit (12:08Z) is a new draft epic by opus_command_0,
    tickets/epics/2026-10-05_melder_services_and_pools_epic.md (16:28Z), a planning ticket with no source, docs or
    workflow change. Tickets sit outside every build asset and llm_support bundle (the checks passed after this
    ticket's and the board's edits, Note 8), so the rebuild is expected to change nothing; it runs anyway on the
    owner's word, as the last write of the uncommitted change set.
  EVIDENCE: context_compass/tickets/epics/2026-10-05_melder_services_and_pools_epic.md:1-12
  IMPACT: Keeps the assets and bundles provably current for the owner's commit.
  NEXT: Run the build-asset runner and llm_support (--include-untracked), then both checks; record the result.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-05T20:51:52Z
  TYPE: MEASURE
  CLAIM: Rebuilt on the owner's request (device VM, CPython 3.14.7t, GIT_OPTIONAL_LOCKS=0): the build-asset
    runner exited 0 in 63 s and wrote agent documentation (462 entries), bind guard (622) and system documents (4)
    at v0.2.8227; llm_support --include-untracked exited 0 in 21 s with src, tests, other and manifest.json all
    UNCHANGED, which confirms the new epic is outside every bundle. Both checks then printed only OK lines
    (asset runner --check three; llm_support --check --include-untracked three). No .git/index.lock.
  EVIDENCE: context_compass/tickets/epics/2026-10-05_melder_services_and_pools_epic.md:1-12
  IMPACT: Assets and bundles are current for the owner's commit; nothing in them changed.
  NEXT: Owner: git add -A and push; decide on the special instruction (Note 6); accept or redirect.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Review (Notes 4-8): .github/ci_cd/ holds six pages written from the workflow and script sources - README (start
here), workflows, scripts, python_versions, extending, validating. special_instructions/ci_cd_guide.md points every
onboarding agent at it; it is local-only because the owner's .git/info/exclude ignores that folder (Note 6).
tests_architecture.md has a "CI/CD Pipeline" section, BRANCH_WORKFLOW.md and CONTRIBUTING.md point at the guide,
and two contract tests keep it complete and its links whole. Workflow suite 500 passed; assets and llm_support
current (--include-untracked). Owner-owed: git add -A (six guide pages untracked) and push, keep or force-add the
special instruction, accept or redirect.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
