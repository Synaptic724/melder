# Epic: Deliver Melder documentation through Beginner, Intermediate, Advanced, and Expert

## Metadata
- Epic ID: EPIC-2026-09-04-readthedocs-documentation
- Status: in_progress
- Owner: codex
- Agent Name: codex_2
- Priority: p2
- Created: 2026-09-04T21:06:12Z
- Updated: 2026-09-05T08:58:00Z
- Target Window: Complete scope definition now; nine delivery stories govern implementation and launch.
- Related Program/Initiative: Melder public documentation.

## Problem / Opportunity
Melder needs a complete Read the Docs experience built around the owner's established learning levels:
Beginner, Intermediate, Advanced, Expert. The site must make its 133 saved examples prominent and give
readers a complete table of contents for freely exploring any topic. ThreadFactory's build mechanics
have been investigated; Melder's information architecture is defined independently here.

The local Sphinx site now builds 294 pages, including all four learning levels, 48 guide chapters,
all 133 saved lesson pages, and expanded references. CI/RTD configuration and offline builders exist;
source-link validation, final packaging/quality checks, and hosted verification remain.

## MRP Alignment
Establish an understood, reproducible authoring/build/publishing model before committing to a site
structure. Melder's reader journeys, API selection, existing guides, and release workflow must drive
the design. ThreadFactory provides a concrete working example of the mechanisms.

## Ticket Contract
- ENTRY_GATE: Certified codex_2 with this epic routed; implementation uses bounded child-story tasks.
- EXECUTION_BOUNDARY: Implement the accepted four-level site through the existing eleven bounded tasks.
  Local documentation/source corrections and validation are authorized. Owner handles commits and
  pushes; actual account configuration and publication require verified service access.
- DEPENDENCIES: Linked reference-discovery task, ThreadFactory checkout, official Sphinx/RTD docs,
  and Melder's existing authored documentation and packaging metadata.
- EXIT_GATE: Owner accepts the eventual Melder strategy and its implementation/hosting validation;
  all required child work and closure synchronization are complete.
- FAILURE_ESCALATION: Record unknown hosting ownership, incompatible build requirements, or unclear
  audience/API boundaries. Resolve those at the relevant stage without inventing service state.

## Goals (Outcomes)
- Four complete learning levels with the README's exact names, order, and level identifiers.
- A complete navigable contents map, searchable references, and all saved examples as first-class pages.
- Source-backed architecture/API material and trustworthy run/output evidence.
- Reproducible local/CI/RTD builds, previews, releases, downloads, accessibility, and maintenance checks.
- Durable findings, explicit ownership/dependencies, and measurable acceptance for every delivery story.

## Non-Goals (Explicit Exclusions)
- Copying ThreadFactory's documentation tree or imposing its information architecture on Melder.
- Introducing a replacement curriculum taxonomy above or instead of the four owner-defined levels.
- Editing ThreadFactory or taking over codex_1's active work.
- Treating a published URL, badge, or configuration file as proof of current account settings.

## Scope Boundaries
- Current: Implement the product/build/quality contract in the linked blueprint and nine stories.
- Completed investigation: ThreadFactory source/config/build/hosting mechanics are recorded below.
- Defined delivery: site foundation, catalog, four curricula, references, CI/hosting, quality/launch.
- Excluded now: Unrelated runtime changes, credential handling, commits, and pushes.

## State Transition Event
- from_state: in_progress
- to_state: in_progress
- transition_reason: Owner resumed after a commit pause and is adding the RTD project. Local content
  and pipeline implementation exist; finish their validation while owner handles hosting setup.

## Success Metrics
- Exactly four primary learning sections, with their established names/order/identifiers.
- Zero unexplained missing or duplicate lesson pages against the current numbered-script inventory.
- Every published guide, lesson, and selected reference page is reachable from Full Contents.
- Complete public API inventory/dispositions, current example evidence, and successful strict builds.
- Reader navigation/accessibility, hosted version/search/download behavior, and maintenance are verified.

## Requirements (Functional + Non-Functional)
- Use exactly the README's four learning levels in order: Beginner, Intermediate, Advanced, Expert.
- Preserve their green/yellow/orange/blue labels and the owner's progression as the site hierarchy.
- The earlier two-part proposal is superseded; the four levels are the primary learning sections.
- Provide a complete table of contents and persistent navigation for unrestricted topic browsing.
- Put saved runnable examples prominently on the homepage and in primary navigation.
- Use ContextCompass as the only durable work record.
- Record tactical detail in the child task and program decisions/findings here.
- Keep local source evidence, public rendered-page evidence, and service defaults distinct.
- Preserve preexisting authored documents and other agents' concurrent work.
- Keep any eventual documentation dependencies separate from Melder runtime requirements.

## Constraints / Assumptions
- Owner-selected reference: ../ThreadFactory (C:/Users/Mark/PycharmProjects/ThreadFactory).
- Melder package metadata requires Python >=3.14 and declares zero runtime dependencies.
- No child agents have been authorized.
- Strict Sphinx builds and isolated Python 3.14t example checks are operational.

## Dependencies / External References
- ../tasks/2026-09-04_readthedocs_sphinx_reference_discovery_task.md
- https://threadfactory.readthedocs.io/en/latest/
- https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
- https://docs.readthedocs.com/platform/stable/config-file/v2.html
- https://docs.readthedocs.com/platform/stable/intro/add-project.html
- https://docs.readthedocs.com/platform/stable/versions.html

## Milestones (Track Progress)
- [x] Reference inspected: file responsibilities and authoring/build/publication/update explanation ready.
- [x] Owner direction fixed: four levels, full contents, prominent examples, comprehensive scope definition.
- [x] Product blueprint and nine delivery stories defined with boundaries, dependencies, and acceptance.
- [x] Foundation and complete catalog delivered (S1-S2).
- [ ] All four curricula and reference layer delivered (S3-S7).
- [ ] CI/RTD features and offline formats demonstrated (S8).
- [ ] Integrated quality, launch, and maintenance accepted (S9).

## Stories (Required to Complete)
| Part | Story | Deliverable | Dependencies |
| --- | --- | --- | --- |
| S1 | [Navigation and site foundation](../stories/2026-09-04_rtd_navigation_and_site_shell_story.md) | Local build, homepage, four levels, full contents, accessible shell | Blueprint |
| S2 | [Complete example catalog](../stories/2026-09-04_rtd_example_catalog_story.md) | Canonical source inclusion and all 133 lesson routes | S1 |
| S3 | [Beginner curriculum](../stories/2026-09-04_rtd_beginner_curriculum_story.md) | Complete Beginner chapters and 41 saved lessons | S1-S2 |
| S4 | [Intermediate curriculum](../stories/2026-09-04_rtd_intermediate_curriculum_story.md) | Complete Intermediate chapters and 37 saved lessons | S1-S2; Beginner vocabulary |
| S5 | [Advanced curriculum](../stories/2026-09-04_rtd_advanced_curriculum_story.md) | Complete Advanced chapters and 19 saved lessons | S1-S2; Intermediate vocabulary |
| S6 | [Expert curriculum](../stories/2026-09-04_rtd_expert_curriculum_story.md) | Complete Expert chapters and 36 saved lessons | S1-S2; Advanced vocabulary |
| S7 | [Reference and architecture](../stories/2026-09-04_rtd_reference_and_architecture_story.md) | API, diagrams, glossary, troubleshooting, source links | S1-S2; curriculum link map |
| S8 | [Build and hosting](../stories/2026-09-04_rtd_build_and_hosting_story.md) | CI/RTD parity, previews, versions, search, downloads, redirects | S1-S7 |
| S9 | [Quality and launch](../stories/2026-09-04_rtd_quality_and_launch_story.md) | Integrated evidence, publication verification, maintenance | S1-S8 |

All nine stories have bounded execution tasks. Foundation, catalog, and all curricula are implemented;
reference content and pipeline implementation exist; final packaging, hosting, and quality verification
remain. Keep one documentation task actively routed.

## Tasks (Cross-Cutting or Epic-Level)
- [ ] [Understand ThreadFactory's Sphinx/RTD setup](../tasks/2026-09-04_readthedocs_sphinx_reference_discovery_task.md).

## Acceptance Criteria (Epic Done)
- [ ] Exactly Beginner, Intermediate, Advanced, Expert drive the learning hierarchy.
- [ ] Homepage and every page expose the complete contents and example routes clearly.
- [ ] Every saved numbered lesson and required chapter is accounted for with source/run fidelity.
- [ ] Architecture/public API/reference coverage is complete with no unexplained omissions.
- [ ] Build, navigation, images, examples, accessibility, search, versions, and downloads pass defined checks.
- [ ] All nine stories and their tasks have accepted evidence and truthful validation status.
- [ ] Owner confirms acceptance and associated boards are synchronized.

## Risks / Mitigations
- Reference drift: local package version and the docs release label differ; record them independently.
- Autodoc imports code: assess package import behavior before choosing Melder's API extraction strategy.
- Existing guide links/images need a deliberate publishing plan if they enter Sphinx.
- Account/branch/webhook state is external: inspect it separately when hosting configuration is in scope.
- Avoid losing findings when direction changes: append corrections and retain prior investigation notes.

## Applicable Anti-Patterns
- [ ] No copying-driven strategy without establishing Melder's requirements.
- [ ] No hosted-build success claim based only on configuration or a reachable landing page.
- [ ] No automatic full-package API dump used as a substitute for useful documentation design.
- [ ] No epic closure while downstream work remains unaccepted.

## Validation / Test Approach
- Current evidence: complete reference build/config reads and representative API page reads.
- Public ThreadFactory landing and ConcurrentDict pages were retrieved and contain rendered API data.
- Local Sphinx rendering builds 294 pages; independent navigation validation currently fails on 19 backlinks.
- Focused CI workflow checks: 127 passed. Offline artifacts built; final review and packaging remain.
- Saved lesson execution: all 133 scripts have passed; Expert ProtocolCrafter needed one unchanged
  retry outside the sandbox for Windows temporary-directory ACLs. This verifies executed assertions
  and handled outcomes, not every prose claim or universal runtime correctness.
- An existing architecture-doc check was run; its result and a line-ending diagnosis are retained below.
- Delivery validation is defined in blueprint section 15 and in every story's acceptance/test plan.
- Definition checks: nine linked story files resolve; distinct IDs/status/parent pointers inspected;
  active definition contains no retired layout paths; whitespace checks reported no findings.

## Rollout / Adoption Plan
S1 proves a real local foundation. S2 establishes complete example coverage. S3-S6 deliver the four
curricula and S7 closes the reference layer. S8 demonstrates CI/RTD parity, previews, releases, and
downloads. S9 audits the complete experience, launch candidate, and maintenance procedure.

## Open Questions
- UNKNOWN: ThreadFactory's configured RTD default branch, enabled versions, and webhook state today.
- UNKNOWN: Ownership, repository association, and build state of the advertised Melder RTD project.
- Execution verification: exact API inventory, current lesson outcomes, compatible pins, and build costs.
- Hosting selection: intended public branch, supported release tags, and optional custom domain.

## Decision Log
- 2026-09-04: Owner retains all commits and pushes; do not attempt signing or request the PGP passphrase.
- 2026-09-04: Owner clarified that the purpose is understanding how RTD works in ThreadFactory;
  Melder will use its own strategy. Early Melder probe work is deferred.
- 2026-09-04: Owner requested this epic and ongoing findings recorded in its notes.
- 2026-09-04: Owner fixed the four learning levels as the primary hierarchy and rejected the earlier
  two-part proposal; latest blueprint/current definition supersede historical planning notes.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Parent epic closure after all dependent stories; retain the shared blueprint until then.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: README progression, saved lessons, complete navigation, and documentation build strategy.
- IF_UNKNOWN: none

## Current Site Definition
The [site blueprint](../../artifacts/2026-09-04_readthedocs_site_blueprint.md) is the detailed product
contract. The story table above owns delivery routing. The latest owner direction takes precedence
over historical proposals retained in Notes.

| Learning level | Curriculum outcome | Source collection |
| --- | --- | --- |
| 🟢 Beginner | Useful first graph, addressing, core lifetimes, scopes, cleanup, errors, capstone | 41 lessons |
| 🟡 Intermediate | Configuration, registration, DI, hooks, lineage/spell spaces, links, permissions, late binding | 37 lessons |
| 🟠 Advanced | World isolation, posture, precise overrides, clusters, rooms/viewers, inspection and entry-point continuity | 19 lessons |
| 🔵 Expert | Agent codegen, transactions, record/restore, external storage, research, previews, governed change | 36 lessons |

Homepage: purpose/three verbs, Start Beginner, Browse Examples, Full Contents, four level cards,
featured useful applications, architecture/reference routes, and version context. All four level
names/order/identifiers remain explicit. There is no replacement partition above them.

Navigation: one registry drives stable page IDs, hierarchy, sidebar, breadcrumbs, previous/next,
and the complete contents page. Each lesson/guide is directly reachable; topic links add free
exploration without duplicating content. Keep search and on-page contents available throughout.

Examples: all current numbered scripts are reconciled, source-included, and independently addressable.
Each page states goal, prerequisites, run command, code, expected outcomes, and related guide/API links.
Use current execution evidence for verification claims; preserve helper/run requirements and source identity.

Reference: canonical architecture prose/SVGs, complete public API inventory, glossary, troubleshooting,
release/migration guidance, and explicitly audited agent-document routes.

Build/features: Sphinx/MyST with a purposeful extension set, one local/CI/RTD command, PR previews,
search, versions, notifications, canonical links, redirects, HTML/PDF/ePub downloads, and maintenance.
Pin dependencies after a real build; verify actual hosted settings and outputs at their delivery stage.

Quality: chapter/lesson/API completeness, source fidelity, strict builds, links/images/downloads,
real example outcomes, accessible mobile/keyboard/zoom reading, version correctness, and a maintainer runbook.
Blueprint sections 4-7 define every level's required chapters; sections 8-15 define shared contracts and gates.

File layout uses docs/beginner/, docs/intermediate/, docs/advanced/, docs/expert/, docs/examples/,
docs/reference/, shared configuration/assets/tools, and explicit navigation/catalog registries.
Canonical scripts remain in UX_and_AIX_experiences and architecture material remains in its existing tree.

## Notes
- DATETIME: 2026-09-04T21:06:12Z
  TYPE: DECISION
  CLAIM: The owner narrowed the current work to understanding the reference. The epic spans the
    future Melder strategy, but this stage must not choose or implement that strategy prematurely.
  EVIDENCE:
  - Owner clarification: understand Read the Docs in ThreadFactory; implement our own Melder strategy.
  - Owner instruction: make an epic and add findings to its notes.
  IMPACT: Retain all findings already gathered and finish the reference explanation before design.
  NEXT: Complete the source-backed account of how documentation updates reach the hosted site.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:06:12Z
  TYPE: FACT
  CLAIM: ThreadFactory separates source content, Sphinx build policy, and hosting configuration.
    docs/index.rst and nested toctrees define navigation; module pages select APIs with automodule.
    docs/conf.py enables autodoc (signatures/docstrings), napoleon (docstring formatting), and
    viewcode (source links), and selects sphinx_rtd_theme for presentation.
  EVIDENCE:
  - ../ThreadFactory/docs/index.rst:1-20
  - ../ThreadFactory/docs/concurrency/index.rst:1-15
  - ../ThreadFactory/docs/concurrency/concurrent_dict.rst:1-7
  - ../ThreadFactory/docs/conf.py:7-28
  - https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
  IMPACT: Updating a documented API docstring can change its generated page on the next build;
    adding a new module to navigation still needs an authored page and toctree entry.
  NEXT: Explain the RTD build environment and the separate service-side Git integration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:06:12Z
  TYPE: FACT
  CLAIM: ThreadFactory's .readthedocs.yaml specifies Ubuntu 24.04, Python 3.13, docs/conf.py, and
    docs/requirements.txt. Its GitHub workflow publishes the Python distribution, while RTD owns
    documentation building/hosting. The public ConcurrentDict page contains signatures, methods,
    docstrings, and source links. RTD's documented Git integration handles rebuild triggers and
    version routing; the actual ThreadFactory dashboard values remain UNKNOWN.
  EVIDENCE:
  - ../ThreadFactory/.readthedocs.yaml:1-22
  - ../ThreadFactory/.github/workflows/python-publish.yml:1-67
  - https://threadfactory.readthedocs.io/en/latest/concurrency/concurrent_dict.html
  - https://docs.readthedocs.com/platform/stable/intro/add-project.html
  - https://docs.readthedocs.com/platform/stable/versions.html
  IMPACT: An RTD YAML file describes a build, but a connected/imported RTD project supplies hosting
    and Git event integration. A package release workflow is not the documentation deployment.
  NEXT: Record the update workflow and configuration caveats without assuming dashboard state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:06:12Z
  TYPE: FACT
  CLAIM: Reference details to remember: docs release is hardcoded to 1.1.0 while pyproject is 1.5.2;
    sphinx-autodoc-typehints is listed but not enabled; the livehtml batch target invokes
    sphinx-autobuild, which is not in docs/requirements.txt; RTD installs only docs requirements.
    Melder-specific observations already collected are retained in the child task for later design.
  EVIDENCE:
  - ../ThreadFactory/docs/conf.py:14-22
  - ../ThreadFactory/pyproject.toml:5-10
  - ../ThreadFactory/docs/requirements.txt:1-3
  - ../ThreadFactory/docs/make.bat:12-15
  - ../ThreadFactory/.readthedocs.yaml:20-22
  - tickets/tasks/2026-09-04_readthedocs_sphinx_reference_discovery_task.md:167-224
  IMPACT: These are maintenance details and future design inputs, not proof the hosted reference is
    currently broken. A fresh local build has not been run.
  NEXT: Present the reference explanation and carry unresolved design questions into the next stage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:06:12Z
  TYPE: MEASURE
  CLAIM: The early Melder probe created an isolated environment using uv after ensurepip failed.
    Dependency download then failed with a network/proxy connection error; Sphinx never ran.
    The unrelated architecture check reported ten source hash mismatches. All ten source files are
    LF in Git and CRLF in the worktree; for system_context.mmd, normalizing CRLF to LF exactly
    reproduces the manifest hash. Only that sample's normalized hash was compared.
  EVIDENCE:
  - artifacts/rtd_probe_20260904/README.md
  - architecture_and_design/tools/architecture_docs.py:209-255
  - Command: git ls-files --eol architecture_and_design/diagrams/source/*.mmd
  - system_context.mmd normalized SHA256: 955bca1501d7accb1f5b99ac8444f30fcbc695ba4d913e7190f0e6dabacd6eab
  IMPACT: Preserve the observation for later cross-platform docs validation; no diagram regeneration
    or environment-download retry is needed for the clarified reference-understanding task.
  NEXT: Keep the probe deferred and finish the ThreadFactory explanation.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-04T21:11:55Z
  TYPE: FACT
  CLAIM: Reference operating model: authors edit .rst pages/toctrees and Python docstrings; local
    make html or make.bat html invokes Sphinx and writes docs/_build/html. On the service, an RTD
    project connected to Git checks out the selected branch/tag, applies .readthedocs.yaml, installs
    docs requirements, runs Sphinx with docs/conf.py, and serves the generated HTML. With Git
    integration, later pushes rebuild active versions. latest/stable URL routing is service-level;
    the 1.1.0 label is independently hardcoded in conf.py. The reference build files are tracked in
    Git. There are 51 .rst files, with API selection/navigation authored explicitly rather than an
    enabled autosummary/apidoc extension. Public project-dashboard retrieval was unavailable, so
    actual branch/webhook settings remain UNKNOWN.
  EVIDENCE:
  - ../ThreadFactory/docs/Makefile:7-20
  - ../ThreadFactory/docs/make.bat:3-15
  - ../ThreadFactory/docs/make.bat:31-40
  - ../ThreadFactory/docs/conf.py:7-28
  - ../ThreadFactory/.readthedocs.yaml:1-22
  - ../ThreadFactory/docs/index.rst:6-14
  - ../ThreadFactory/docs/concurrency/concurrent_dict.rst:1-7
  - https://docs.readthedocs.com/platform/stable/intro/add-project.html
  - https://docs.readthedocs.com/platform/stable/versions.html
  - Scoped git ls-files and rg inventory of reference docs and build entrypoints.
  IMPACT: The mechanism is understood and ready for owner review. Melder can choose a different
    content architecture while separately selecting its builder, presentation, and hosting policy.
  NEXT: Discuss Melder's reader journeys and documentation boundaries with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:20:50Z
  TYPE: DECISION
  CLAIM: The owner requested a Melder implementation recommendation, then explicitly required a full
    README read first. The site must follow that kind of structure, provide a table of contents for
    free exploration, and put the saved examples front and center. These are confirmed design inputs;
    detailed implementation choices are still proposals.
  EVIDENCE:
  - Owner instructions on 2026-09-04 following the reference explanation.
  IMPACT: The README's learning progression and examples determine the site architecture.
  NEXT: Read the example hub and level indexes before writing the proposed navigation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:20:50Z
  TYPE: FACT
  CLAIM: Read all 1,081 lines of the current README in sequential 1-400, 401-800, and 801-1081 chunks.
    Its structure starts with product purpose, bind/conjure/meld, audience, and low-floor/high-ceiling
    framing; offers Beginner/Intermediate/Advanced/Expert routes linked to saved example folders;
    then divides Part I (human-oriented basics) from Part II (optional expert/agent-facing ceiling).
    The same document places architectural drawings, runnable examples, example verification, hosted
    reference, and video in an explicit documentation routing table.
  EVIDENCE:
  - README.md:27-227
  - README.md:229-271
  - README.md:274-670
  - README.md:672-1030
  - README.md:1034-1049
  IMPACT: Recommend both a guided progression and freely accessible complete navigation. The simple
    path must stand alone, while advanced capabilities and saved examples remain directly discoverable.
  NEXT: Inspect UX_and_AIX_experiences guidance and the existing example indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:24:55Z
  TYPE: FACT
  CLAIM: The example inventory contains 133 numbered .py lessons: 41 beginner, 37 intermediate,
    19 advanced, and 36 expert. Read the full beginner/intermediate/advanced concept maps, only
    lines 1-150 of the 1,265-line expert map, and complete Hello Melder, beginner capstone, expert
    lesson 36, and example-contract test files. The source headers carry TIER/GOAL/SURFACE metadata.
    The contract test checks those headers and behavioral-check presence; its own docs distinguish
    that mechanical floor from teaching quality. Expert 36's header says not yet run.
  EVIDENCE:
  - UX_and_AIX_experiences/AGENTS.md:1-44
  - UX_and_AIX_experiences/01_beginner/_concept_map.txt:1-54
  - UX_and_AIX_experiences/02_intermediate/_concept_map.txt:1-177
  - UX_and_AIX_experiences/03_advanced/_concept_map.txt:1-321
  - UX_and_AIX_experiences/04_expert/_concept_map.txt:1-150
  - UX_and_AIX_experiences/01_beginner/01_hello_meld.py:1-35
  - UX_and_AIX_experiences/01_beginner/40_beginner_capstone.py:1-65
  - UX_and_AIX_experiences/04_expert/36_an_agent_builds_a_working_system.py:1-247
  - UX_and_AIX_experiences/pytest_examples/test_example_contract.py:1-121
  - Scoped rg filename inventory grouped by tier; no example execution in this turn.
  IMPACT: A first-class lesson catalog can use actual metadata and code, while publication checks
    must establish current run status instead of inheriting old header claims. Internal concept-map
    history is useful for curation but is not public instructional prose.
  NEXT: Review the README-shaped navigation and example-first strategy with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:24:55Z
  TYPE: PLAN
  CLAIM: Proposed the site structure in Proposed Melder Strategy: a README-shaped tour, independent
    Basics and Ceiling parts, prominent four-level example access, complete free-roam contents,
    architecture/drawings, and curated public API reference. Propose Sphinx/MyST, source-included
    lesson code, a generated catalog from actual files, and one shared local/CI/RTD build entrypoint.
    This is a recommendation for review, not a claim that the strategy was accepted or implemented.
  EVIDENCE:
  - README.md:229-271
  - README.md:274-1030
  - UX_and_AIX_experiences/AGENTS.md:1-44
  - https://myst-parser.readthedocs.io/en/latest/intro.html
  - https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
  - https://docs.readthedocs.com/platform/stable/build-customization.html
  - https://docs.readthedocs.com/platform/stable/pull-requests.html
  IMPACT: Owner requirements now have a concrete site/navigation/content/build proposal, preserved
    alongside the prior findings. The first implementation proof should exercise real content and API
    imports before the complete catalog is published.
  NEXT: Review the proposed homepage, full contents, and lesson page structure with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:30:46Z
  TYPE: DECISION
  CLAIM: Owner requires the exact four README learning levels, in their established order, as the
    primary documentation structure. The earlier Basics/Ceiling partition is rejected. Owner also
    requires a clear complete table of contents, prominent saved examples, and a thoroughly defined
    epic that makes strong use of Sphinx/Read the Docs. Update this existing epic and define its
    delivery stories rather than creating a competing epic.
  EVIDENCE:
  - Owner instruction on 2026-09-04 after reviewing the strategy.
  - README.md:229-260
  IMPACT: All current navigation, file layout, curriculum, and acceptance criteria must use the
    four levels. Historical notes remain preserved and are superseded by this decision where needed.
  NEXT: Define the complete site blueprint and the bounded delivery stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:53:49Z
  TYPE: FACT
  CLAIM: Completed the program definition: a 16-section site blueprint and nine draft delivery stories
    cover navigation/foundation, the full example catalog, each of the four curricula, reference and
    architecture, build/hosting, and quality/launch. Each story has scope, prerequisites, tasks,
    acceptance criteria, validation approach, findings, and a handoff. The shared design is indexed
    for the parent and all nine stories; its lifecycle remains owned by the parent epic.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:10-356
  - tickets/epics/2026-09-04_readthedocs_documentation_epic.md:107-121
  IMPACT: The owner's established four levels now control every current navigation and curriculum
    definition. Prior two-part recommendations survive only as superseded history in Notes.
  NEXT: Open a bounded S1 implementation task when execution begins.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:53:49Z
  TYPE: MEASURE
  CLAIM: Definition review read the blueprint and all nine story files. The epic's nine story links
    resolve, the story identities are distinct, and the active definition has no retired Part I/II
    navigation or docs/part_i/ and docs/part_ii/ paths. Whitespace search returned no matches and board
    diff checking reported no issues. S7's entry dependency was clarified to the topic/API target map,
    rather than requiring all curriculum prose complete before reference destinations can be authored.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:293-344
  - tickets/stories/2026-09-04_rtd_reference_and_architecture_story.md:49-54
  - Scoped local link, metadata, retired-layout, and whitespace checks on the definition files.
  IMPACT: Planning artifacts are connected and reviewable without implying implementation or a working
    hosted site. The definition is ready for owner review and subsequent S1 execution.
  NEXT: Review the epic and blueprint, then route the selected implementation task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T08:58:00Z
  TYPE: DECISION
  CLAIM: The local program has reached 294 declared pages with expanded references, mandatory docs CI,
    RTD per-format configuration, and native PDF/ePub builders. It is not release-ready: independent
    validation found 19 source-page backlinks to incorrect API fragments. The owner paused to commit,
    then instructed continue and is now adding the project on the Read the Docs website.
  EVIDENCE:
  - tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md:73-174
  - docs/_build/site-check.json:1-26
  - Owner continue and RTD website setup instructions on 2026-09-05.
  IMPACT: Agent finishes local build/download validation while owner handles account setup and all
    commits/pushes. A configured project alone does not prove a hosted build or working reader features.
  NEXT: Finish the active CI/offline task and record the owner's project URL/branch when supplied.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user.
- [ ] Acceptance criteria confirmed by user.
- [ ] Required downstream stories/tasks accepted and boards synchronized.

## Noting Behavior
- Capture program direction, stage transitions, findings, and unresolved decisions here.
- Keep tactical evidence and command details in the linked investigation task.
- Append corrections when new evidence or owner direction changes earlier conclusions.

## Context / Handoff Summary
codex_2 owns this implementation. The local Sphinx build has 294 pages: exactly Beginner,
Intermediate, Advanced, Expert; 48 guide chapters; all 133 canonical lesson pages; full contents and
filterable examples. All saved scripts have passed their harness checks, with one environment-only
ProtocolCrafter retry. All 36 Expert sources were read and limits recorded in its task.
Reference/API/architecture integration, CI/RTD configuration, and offline builders exist.
Next: resolve 19 source-page backlinks, finish offline review/staging and bundle checks, then perform
integrated quality/hosted verification. The owner resumed after pausing and is adding the RTD project.
Owner handles all commits/pushes and account setup. Preserve other agents' CI/disposal work.
