# Task: Understand ThreadFactory's Sphinx and Read the Docs pipeline

## Metadata
- Task ID: TASK-2026-09-04-readthedocs-sphinx-reference-discovery
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Epic Path: ../epics/2026-09-04_readthedocs_documentation_epic.md
- Story: none; epic-level discovery task
- Status: review
- Owner: codex
- Agent Name: codex_2
- Priority: p2
- Created: 2026-09-04T20:56:31Z
- Updated: 2026-09-04T21:11:55Z

## Objective
Explain how ThreadFactory authors, builds, publishes, and updates its Sphinx documentation.
Preserve findings as inputs to a later, independently designed Melder documentation strategy.

## Problem / Context
The owner selected the sibling ThreadFactory repository as a reference and wants its documentation
setup understood before deciding how to implement the equivalent capability in Melder.

## MRP Alignment
Prefer a reproducible documentation build with explicit dependency, import, and hosting boundaries.
Preserve existing authored documentation and avoid a publishing setup that needs immediate rework.

## Ticket Contract
- ENTRY_GATE: Certified codex_2, active routing row, and evidence-backed notes before each next tranche.
- EXECUTION_BOUNDARY: Inspect documentation, Sphinx/Read the Docs configuration, packaging, build
  scripts, and related workflows in Melder and the owner-named sibling ThreadFactory checkout.
  Write only this task, its parent epic, associated ContextCompass artifacts, and own routing state.
- DEPENDENCIES: Current official Sphinx and Read the Docs documentation; local reference checkout.
- EXIT_GATE: Reference file responsibilities, authoring/build/publication/update flow, maintenance
  caveats, and dashboard-only unknowns are documented with evidence and delivered for review.
- FAILURE_ESCALATION: Record inaccessible required sources, ambiguous ownership, or a proposal that
  would require runtime/public API changes; continue unaffected investigation within scope.

## Scope Boundaries
- In scope: Read-only inspection of ThreadFactory at ../ThreadFactory, local documentation and
  packaging inspection, official documentation research, and explanation of the reference pipeline.
- Deferred after owner clarification: Melder compatibility probes and strategy selection.
- Out of scope: Product source changes, copying reference files into Melder's live documentation,
  publishing, account linking, changing repository permissions, or editing ThreadFactory.
- Out of scope: codex_1's ordered Spell disposal work and other existing assignments.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Reference configuration, authored API/navigation pages, and published output
  have been inspected; findings and the update workflow are recorded in the parent epic.

## Steps / Checklist
- [x] Inspect the reference Sphinx configuration, source structure, dependencies, and hosting flow.
- [x] Preserve already-collected Melder observations for later strategy work.
- [x] Check official Sphinx and Read the Docs build, integration, and versioning behavior.
- [x] Explain the reference authoring/build/update workflow and dashboard-only unknowns.
- [x] Record findings before moving to each subsequent investigation or validation tranche.

## Deliverables
- Evidence-backed explanation of ThreadFactory's documentation pipeline.
- Reference file map and update workflow.
- Preserved Melder design inputs and clearly marked unresolved hosting questions.

## Files / Paths Impacted
- This ticket and its optional linked report artifact.
- context_compass/attention_board.md: codex_2's investigation routing only.
- context_compass/mailbox_board.md: codex_2's own last_checked timestamp.
- context_compass/artifact_board.md: only if a supporting report or probe is created.

## Acceptance Criteria
- [x] Explanation distinguishes Sphinx, the theme, API generation, and Read the Docs.
- [x] Local configuration and build behavior are supported by complete relevant file reads.
- [x] Findings are retained for Melder's own subsequent strategy without selecting it prematurely.
- [x] Verification status distinguishes inspected configuration from commands actually executed.

## Validation
- Sphinx build: Not run. An isolated environment was created, but docs dependency download failed;
  the build probe was then deferred following the owner's scope clarification.
- Runtime tests: Not run; outside this task.
- Reference configuration and representative API pages read; public rendered API page retrieved.
- Existing architecture check: exit 1, ten source hash mismatches. One normalized-hash comparison
  proves a CRLF/LF cause for the sampled diagram; see the later MEASURE note.

## Risks / Rollback Notes
- Local reference files may not match the hosted site's active branch or dashboard settings.
- Sphinx extensions that import Melder may trigger package initialization or annotation issues.
- Python and dependency versions must be checked rather than copied from the reference blindly.
- This lane initially changes durable investigation records only; product files remain outside edits.

## Applicable Anti-Patterns
- [ ] Do not treat configuration existence as proof of a successful hosted build.
- [ ] Do not treat generated API pages as the full authored documentation strategy.
- [ ] Do not overwrite another agent's board rows or concurrent source changes.
- [ ] Do not close without owner acceptance and synchronized board state.

## Done Checklist
- [x] Reference investigation and explanation complete.
- [x] Evidence and validation status recorded.
- [x] Relevant unknowns and next action explicit.
- [ ] Acceptance criteria reviewed with the owner.
- [x] Routing synchronized for handoff; closure acceptance remains pending.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/rtd_probe_20260904/README.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Apply disposition to any later linked artifacts at accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Sphinx reference pipeline and Read the Docs integration design
- IF_UNKNOWN: none

## Noting Behavior
- Finish each coherent read unit, then append its findings, evidence, impact, and next single step.
- Keep unverified build and hosting behavior UNKNOWN until checked at the appropriate source.
- Ticket notes are the durable record; the attention board holds routing only.

## Notes
- DATETIME: 2026-09-04T20:56:31Z
  TYPE: PLAN
  CLAIM: Inspect the owner's ThreadFactory reference first, then compare Melder and current official
    hosting requirements before proposing live documentation changes. No child agents are authorized.
  EVIDENCE:
  - User request on 2026-09-04 naming C:/Users/Mark/PycharmProjects/ThreadFactory.
  - context_compass/mailbox_board.md:80-86
  IMPACT: The investigation is separately owned by codex_2 and does not take over codex_1's assignments.
  NEXT: Locate reference documentation configuration and read the full build-entry files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T20:59:10Z
  TYPE: FACT
  CLAIM: ThreadFactory uses a v2 RTD config selecting Ubuntu 24.04/Python 3.13 and docs/conf.py;
    its install list contains docs/requirements.txt only. Sphinx enables autodoc, napoleon, and
    viewcode with sphinx_rtd_theme. The configured release is 1.1.0 but package metadata is 1.5.2.
    The dependency sphinx-autodoc-typehints is listed but its extension is not enabled. make.bat's
    livehtml target invokes sphinx-autobuild, which is absent from the three docs requirements.
  EVIDENCE:
  - ../ThreadFactory/.readthedocs.yaml:1-22
  - ../ThreadFactory/docs/conf.py:7-28
  - ../ThreadFactory/docs/requirements.txt:1-3
  - ../ThreadFactory/pyproject.toml:5-10
  - ../ThreadFactory/docs/make.bat:12-15
  IMPACT: Reuse the simple source/config/hosting structure, but do not copy stale version metadata
    or assume installed extras and package dependencies are sufficient for a reproducible build.
  NEXT: Read representative API pages and reference package initialization to establish autodoc inputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:00:29Z
  TYPE: FACT
  CLAIM: ThreadFactory's navigation is authored reStructuredText toctrees; individual seven-line
    pages use automodule directives with members, undoc-members, and inheritance. Package imports
    eagerly re-export runtime classes and invoke the no-GIL warning function. Its sole checked-in
    GitHub workflow builds/publishes the Python distribution and does not build documentation.
    Melder declares Python >=3.14, zero runtime dependencies, a static version attribute for builds,
    and a Documentation URL at melder.readthedocs.io. Its existing public guides are authored Markdown
    under architecture_and_design with relative page/image/source links. No docs directory or RTD
    configuration was found by the scoped file inventory.
  EVIDENCE:
  - ../ThreadFactory/docs/index.rst:6-14
  - ../ThreadFactory/docs/concurrency/index.rst:1-15
  - ../ThreadFactory/docs/concurrency/concurrent_dict.rst:1-7
  - ../ThreadFactory/src/thread_factory/__init__.py:27-70
  - ../ThreadFactory/src/thread_factory/__init__.py:122-146
  - ../ThreadFactory/.github/workflows/python-publish.yml:1-67
  - pyproject.toml:1-12
  - pyproject.toml:72-86
  - pyproject.toml:143-152
  - architecture_and_design/README.md:1-79
  - Scoped rg --files inventory of docs/config/workflow files; docs path reported absent.
  IMPACT: Sphinx and RTD are separate from PyPI publishing. Melder needs Python 3.14-compatible docs
    tooling and a Markdown publishing strategy; copying the RST-only reference would discard useful
    existing guide structure. Autodoc import effects must be assessed from Melder source.
  NEXT: Verify current official hosting/build requirements and the public reference documentation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:01:18Z
  TYPE: FACT
  CLAIM: Current RTD documentation lists Python 3.14 as a supported build.tools.python value;
    no 3.14t value appears in that documented list. Official Sphinx documentation confirms autodoc
    imports documented modules and executes their import side effects. The public ThreadFactory
    landing page is retrievable and labels itself 1.1.0. The first web-tool request for Melder's
    configured documentation URL returned an internal retrieval error, which does not establish
    whether the project exists or who owns its hosting settings.
  EVIDENCE:
  - https://docs.readthedocs.com/platform/stable/config-file/v2.html#build-tools-python
  - https://docs.readthedocs.com/platform/stable/config-file/index.html
  - https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
  - https://threadfactory.readthedocs.io/en/latest/
  IMPACT: A Python 3.14 docs builder is available. Free-threaded runtime tests and documentation
    generation should be evaluated separately; hosted-project state remains UNKNOWN.
  NEXT: Inspect Melder's package import boundary and existing Markdown link/build conventions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:03:24Z
  TYPE: FACT
  CLAIM: Melder's package root eagerly imports public collaborators, constructs Aether(), then emits
    interpreter/no-GIL warnings. The canonical version module currently declares 0.2.3. The public
    guide tree already uses Markdown, relative page links, SVG images, Mermaid source links, and
    source/test evidence links. ArchitectureDocsTool.check validates registered page metadata,
    local file existence, evidence files, accessibility text, and diagram hashes without rendering.
    Its local-link check strips fragments, so it cannot prove that a Markdown heading anchor exists.
    The default python command is 3.13.5; py also exposes installed 3.14 and 3.14t interpreters.
  EVIDENCE:
  - src/melder/__init__.py:48-201
  - src/melder/__version__.py:1-12
  - architecture_and_design/03_usage/compose_an_application.md:16-72
  - architecture_and_design/diagrams/README.md:13-43
  - architecture_and_design/tools/architecture_docs.py:155-287
  - README.md:1034-1049
  - Local python --version and py -0p interpreter inventory.
  IMPACT: Prefer MyST for existing guides, shipped SVGs for hosted images, an import-free version
    read, and a documentation-only smoke build on 3.14. A Sphinx link pass must supplement the
    existing diagram/Markdown check because anchors and hosted link targets are a separate concern.
  NEXT: Establish a disposable Sphinx environment and probe curated API plus Markdown rendering.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:04:26Z
  TYPE: MEASURE
  CLAIM: Python 3.14.0 is installed but contains none of sphinx, myst_parser, or sphinx_rtd_theme.
    Running the existing architecture documentation check returned exit 1 with ten stale Mermaid
    source hashes and no other reported errors. The cause of those hash mismatches is not yet known.
  EVIDENCE:
  - architecture_and_design/tools/architecture_docs.py:209-287
  - Command: py -3.14 -B architecture_and_design/tools/architecture_docs.py check
  - artifacts/rtd_probe_20260904/README.md:1-14
  IMPACT: Use a disposable virtual environment for docs dependencies; investigate line endings before
    treating the hash failures as changed diagrams or proposing any regeneration.
  NEXT: Create the isolated docs environment and compare one affected source's normalized hash.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:06:12Z
  TYPE: DECISION
  CLAIM: Owner clarified that the immediate goal is understanding ThreadFactory's RTD flow; Melder
    will have its own strategy later. Owner then requested a parent epic with findings in its notes.
    Created that epic, linked this task, and retained the earlier observations without deleting them.
  EVIDENCE:
  - Owner clarification and epic request on 2026-09-04.
  - tickets/epics/2026-09-04_readthedocs_documentation_epic.md
  IMPACT: Earlier proposal/probe NEXT fields are superseded by this scope correction.
  NEXT: Finish and deliver the reference explanation, then await the Melder strategy discussion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:06:12Z
  TYPE: MEASURE
  CLAIM: uv created the isolated 3.14 environment after ensurepip failed. Sphinx dependency download
    failed after connection retries, so no Sphinx build ran. Ten diagram sources have i/lf and w/crlf;
    normalizing system_context.mmd to LF matches its manifest SHA256 exactly. No other normalized
    hashes were compared and no diagrams were changed.
  EVIDENCE:
  - artifacts/rtd_probe_20260904/README.md
  - Command: git ls-files --eol architecture_and_design/diagrams/source/*.mmd
  - system_context.mmd normalized SHA256: 955bca1501d7accb1f5b99ac8444f30fcbc695ba4d913e7190f0e6dabacd6eab
  IMPACT: Retain this cross-platform validation observation for later; the probe is deferred.
  NEXT: Complete the ThreadFactory reference summary.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-04T21:11:55Z
  TYPE: FACT
  CLAIM: Reference build/config/API stub files are tracked in Git. The docs tree has 51 .rst files.
    The inspected docs/config/workflows enable neither autosummary generation nor sphinx-apidoc;
    page selection is explicit. Local html targets write docs/_build/html. The parent epic now
    records the complete content-to-Sphinx-to-RTD flow and separates version labels from RTD routes.
    Public dashboard requests were unavailable; no live project settings were verified.
  EVIDENCE:
  - ../ThreadFactory/docs/conf.py:17-22
  - ../ThreadFactory/docs/Makefile:7-20
  - ../ThreadFactory/docs/make.bat:7-15
  - tickets/epics/2026-09-04_readthedocs_documentation_epic.md
  - https://docs.readthedocs.com/platform/stable/versions.html
  - Scoped git ls-files and rg inventory of reference docs/config/workflows.
  IMPACT: Reference discovery is ready for review. The next stage is a Melder-specific strategy
    discussion; no further build probing is needed to deliver the clarified task.
  NEXT: Review the reference findings with the owner and define Melder's documentation audience.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Reference files and public API output have been inspected. This task belongs to the Read the Docs
epic and is in review. The reference explanation is ready; the owner will develop Melder's own
strategy afterwards. Prior Melder observations are retained above. No Sphinx build, product edits,
or publication occurred. The early isolated dependency probe is deferred.
