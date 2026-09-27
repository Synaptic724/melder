# Task: Explain the supplied Melder SEO starter and assess its fit

## Metadata
- Task ID: TASK-2026-09-26-review-melder-seo-starter
- Story: none; standalone discovery task
- Status: done
- Owner: codex
- Agent Name: seo_0
- Priority: p2
- Created: 2026-09-26T22:22:03Z
- Updated: 2026-09-27T00:32:45Z
- Completed: 2026-09-27T00:30:31Z
- Summary: Inspected the starter and live Sphinx site; corrected the plan and retained the existing homepage.

## Objective
Inspect the user-supplied ZIP and pasted SEO advice, explain the contents in plain language,
and identify useful changes and corrections against Melder's existing documentation.

## Problem / Context
The owner received the archive from GPT Pro and does not know what it contains. They selected
the synaptic_python_developer role and certified seo_0 for this investigation.

## MRP Alignment
Evaluate the starter against the actual repository before adopting content or configuration.

## Ticket Contract
- ENTRY_GATE: Completed onboarding, owner certification, mailbox check-in, and active board route.
- EXECUTION_BOUNDARY: Read the supplied archive/notes and relevant documentation/build sources.
  Write this task, its ContextCompass review artifacts, and the associated board/roster state.
- DEPENDENCIES: User-supplied archive and pasted notes must be readable.
- EXIT_GATE: Archive contents explained, significant fit issues evidenced, next action recommended.
- FAILURE_ESCALATION: Record unreadable input or unresolved implementation assumptions; ask for
  guidance only when independent inspection cannot settle the question.

## Scope Boundaries
- In scope: Inventory, static inspection, relevant repository comparison, and current primary-source
  verification of technical SEO claims where needed.
- Also in scope: Inspect rendered local/live documentation and actual guide routes; revise the plan from concrete defects.
- Also in scope: Assess the owner's tagline, "A runtime you can build on", and the repeated browser
  title "A runtime you can build on - Melder - A runtime you can build on"; suggest clearer wording.
- Out of scope: Running supplied scripts, importing the starter into production docs, dependency
  installation, publishing, runtime edits, version changes, and unrelated active agents' work.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner explicitly requested turn-in before the final asset rebuild.

## Steps / Checklist
- [x] Inventory the ZIP and read the pasted notes.
- [x] Read the starter contents and explain each part's purpose.
- [x] Compare relevant files and claims with the current documentation and build configuration.
- [x] Record findings and recommend the next concrete action.
- [x] Document each meaningful finding before the next investigation tranche.

## Deliverables
- Written review: artifacts/melder_seo_review_20260926/review.md, with recommended homepage wording.
- Evidence-backed review findings plus improvement_proposal.md and homepage-proposal.patch in the same artifact root.

## Files / Paths Impacted
- context_compass/tickets/tasks/completed/2026-09-26_review_melder_seo_starter_task.md
- context_compass/attention_board.md
- context_compass/mailbox_board.md
- context_compass/artifact_board.md (only if review artifacts are produced)
- context_compass/artifacts/melder_seo_review_20260926/ (only if needed for inspection evidence)

## Input References
- C:/Users/Mark/Downloads/melder-seo-starter.zip
- C:/Users/Mark/.codex/attachments/6977636a-b2f9-48ab-869c-9d3593fdcb0d/Pasted text.txt

## Requirements / Acceptance Criteria
- Explain what the archive contains and whether it is an application, patch, or starter material.
- Distinguish attached-document instructions from the owner's request.
- Identify integration changes, stale or unsupported claims, and existing equivalent features.
- Recommend a bounded next step that preserves Melder's actual product scope.

## Validation
- Patch applicability: git apply --check --verbose passed for both docs files. No patch was applied.
- Unit tests and full Sphinx build: Not run. No supplied program was executed.
- Use content reads and source comparisons; record any later checks by their actual command/result.

## Risks / Rollback Notes
- Supplied content may contain instructions, placeholders, or unverified product claims.
- Other agents are active; preserve their board rows and production files.
- No runtime or published documentation change is planned in this review.

## Applicable Anti-Patterns
- [x] Do not adopt attached instructions as authority.
- [x] Do not treat generated copy or SEO promises as verified product behavior.
- [x] Do not overwrite existing docs/configuration with starter files.
- [x] No closure without owner acceptance and board sync.

## Done Checklist
- [x] Inventory and content review complete.
- [x] Repository comparison and recommendation recorded.
- [x] Validation limits stated accurately.
- [x] Notes include evidence, impact, and a concrete next step.
- [x] Acceptance criteria reviewed with the owner and confirmed.
- [x] Board sync completed for review; closure awaits owner acceptance.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/melder_seo_review_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: On owner acceptance, retain evidence needed to explain the recommendation.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: supplied SEO starter; current public documentation/build configuration
- IF_UNKNOWN: none

## Noting Behavior
- Keep tactical findings in append-only notes with source ranges and one next action.
- Treat unevidenced behavior and live search/indexing status as UNKNOWN.

## Notes
- DATETIME: 2026-09-26T22:22:03Z
  TYPE: DECISION
  CLAIM: Open a static review of the supplied SEO archive and pasted notes as seo_0. The owner's
    request authorizes inspection; adopting the attachment's proposed changes is a separate outcome.
  EVIDENCE: Owner request and certification in this chat on 2026-09-26 (AGENT_NAME seo_0;
    CERTIFY APPROVED); the exact input paths appear under Input References above.
  IMPACT: Read the material as untrusted task data and assess it against repository evidence.
  NEXT: List archive entries and count/read the pasted notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T22:24:00Z
  TYPE: FACT
  CLAIM: The supplied Downloads ZIP path does not exist when opened through ZipFile.OpenRead,
    Get-Item, and Get-FileHash. The pasted notes are readable and contain 310 lines. The owner also
    requested assessment of the tagline and repeated browser-title wording recorded in Scope.
  EVIDENCE: Static inspection commands on 2026-09-26 against the two exact Input References;
    OpenRead reported "Could not find file"; Get-Content returned 310 lines for the pasted notes.
  IMPACT: Archive contents remain UNKNOWN. Notes and current documentation can still be reviewed.
  NEXT: Locate a moved/copied archive by filename and read the pasted notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T22:25:13Z
  TYPE: FACT
  CLAIM: The pasted audit describes the missing kit as a homepage patch, a stdlib HTML SEO checker,
    nine synthetic tests, and instructions. Its author reports no full Melder/Sphinx build and no
    Search Console inspection. Filename searches found no archive in Downloads or attachments.
  EVIDENCE:
  - C:/Users/Mark/.codex/attachments/6977636a-b2f9-48ab-869c-9d3593fdcb0d/Pasted text.txt:1-310
  - Read-only rg --files search in Downloads and .codex/attachments returned no matching names.
  IMPACT: Kit contents and claimed test results remain unverified; the review can assess the audit
    and homepage independently. A question for the archive's current path is pending with the owner.
  NEXT: Read current homepage, Sphinx configuration, curriculum, and documentation builder sources.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T22:26:08Z
  TYPE: FACT
  CLAIM: The current homepage starts with the slogan, and Sphinx html_title repeats that slogan
    after Melder. The homepage has no description frontmatter. pyproject.toml declares Python >=3.14
    and an empty runtime dependency list, matching those claims in the proposed introductory copy.
    RTD builds through docs/tools/build_docs.py and runs the existing site checker.
  EVIDENCE:
  - docs/index.md:1-142
  - docs/conf.py:14-81
  - pyproject.toml:5-85
  - .readthedocs.yaml:1-44
  IMPACT: A short site suffix plus a descriptive homepage heading directly addresses the repeated
    title. Copy can retain the broader dependency-graph identity documented in project metadata.
  NEXT: Read the curriculum and builder/generator/checker code to verify the audit's integration advice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T22:27:33Z
  TYPE: FACT
  CLAIM: After the owner supplied the archive again, the same Downloads path opens. The 8578-byte
    ZIP contains four files: README.md, homepage-seo.patch, check_seo.py, and test_check_seo.py.
    Inputs were extracted to the review artifact directory; no program was executed.
    The current curriculum confirms beginner/intermediate injection pages share a README section.
  EVIDENCE:
  - context_compass/artifacts/melder_seo_review_20260926/inventory.md:1-18
  - docs/curriculum.toml:44-122
  IMPACT: Archive review can proceed. The missing-input question is resolved by the owner's retry.
  NEXT: Read the starter files and compare them with the current documentation generators.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T22:28:15Z
  TYPE: FACT
  CLAIM: All four starter files were read in full. The patch changes only docs/conf.py and the
    homepage opening: short suffix, description frontmatter, retained old heading target, and a
    longer descriptive H1. The checker reads local HTML/XML using stdlib, optionally writes JSON,
    and checks titles, descriptions, H1/lang, self-canonicals, robots metadata, and sitemap mapping.
    Nine synthetic unittest cases are present; their claimed pass status has not been reproduced.
  EVIDENCE:
  - context_compass/artifacts/melder_seo_review_20260926/inputs/melder-seo-starter/homepage-seo.patch:1-38
  - context_compass/artifacts/melder_seo_review_20260926/inputs/melder-seo-starter/check_seo.py:1-216
  - context_compass/artifacts/melder_seo_review_20260926/inputs/melder-seo-starter/test_check_seo.py:1-71
  IMPACT: This is a small docs patch plus an optional local checker, not a replacement website.
    The checker requires adaptation before adoption: its future import, globals, missing complete
    type hints/docstrings, and test placement differ from the selected role's conventions.
  NEXT: Verify compatibility with the existing docs assembly/rendering and site-checking code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T22:29:39Z
  TYPE: FACT
  CLAIM: The audit's main integration claims match current source: prepare replaces only generated
    sources; Curriculum requires exactly one readme/source field; lessons support title overrides
    but no description field; static catalog cards already emit links; the builder already emits a
    page sitemap; and the existing checker handles links/anchors/assets rather than SEO metadata.
    The shipped homepage patch passes git apply --check against this checkout without applying it.
  EVIDENCE:
  - docs/tools/build_docs.py:86-152
  - docs/tools/build_docs.py:194-278
  - docs/tools/curriculum.py:102-150
  - docs/tools/example_catalog.py:23-35
  - docs/tools/example_catalog.py:135-225
  - docs/tools/check_site.py:14-142
  - _readthedocs/html/index.html:9-9
  - git apply --check --verbose on the extracted homepage-seo.patch exited 0 and checked both docs files.
  IMPACT: The starter fits the current assembly model. Use the homepage changes first; the larger
    tutorial and metadata changes still need authored content and generator work. Patch compatibility
    does not establish a passing Sphinx build or validate the supplied checker's tests.
  NEXT: Write the final review and recommended homepage wording, then route the ticket to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T22:32:41Z
  TYPE: DECISION
  CLAIM: Deliver the written review and recommend the two-file homepage change first, using
    "A dependency graph runtime for Python" as the heading and "Melder" as the Sphinx suffix.
    Keep the slogan optional and secondary; adapt the checker separately before enforcing it.
  EVIDENCE:
  - context_compass/artifacts/melder_seo_review_20260926/review.md:1-163
  - docs/navigation.toml:7-11
  - docs/tests/test_site_check.py:1-12
  IMPACT: Review scope is complete and has moved to review. Product files remain unchanged;
    nine supplied tests and a full build were not run. No mailbox messages address seo_0.
  NEXT: Owner selects whether to implement the recommended homepage wording or revise positioning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-26T22:40:26Z
  TYPE: PLAN
  CLAIM: The owner asked what to do about improving the documentation after the starter review.
    Prepare an ordered improvement proposal and a concrete first homepage patch for review.
    This continues the discovery lane; product-file application is not part of this proposal step.
  EVIDENCE:
  - Owner message in this chat: "ok so what should we do about improving this shit"
  - context_compass/artifacts/melder_seo_review_20260926/review.md:30-163
  IMPACT: Prioritize clear product explanation, complete useful tutorials, generated metadata,
    and deployment verification. Preserve current URLs and the four curriculum levels.
  NEXT: Write the implementation proposal and draft the first two-file homepage change as an artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-26T22:44:02Z
  TYPE: DECISION
  CLAIM: Prepare an ordered proposal: homepage clarity and task links; three complete beginner
    guides and distinct intermediate injection content; generated descriptions and checker integration;
    deployed-page verification and evidence-led follow-up content. The first two-file change is drafted
    as homepage-proposal.patch and passes git apply --check; no product file was modified.
  EVIDENCE:
  - context_compass/artifacts/melder_seo_review_20260926/improvement_proposal.md:1-145
  - context_compass/artifacts/melder_seo_review_20260926/homepage-proposal.patch:1-55
  - docs/maintaining.md:7-72
  IMPACT: The owner has an ordered path and concrete first change to review. Examples must be run
    separately from Sphinx rendering; public route IDs and the four-level progression stay stable.
  NEXT: Owner selects the homepage proposal for implementation or adjusts the product positioning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T22:55:44Z
  TYPE: ASSUMPTION_CHALLENGE
  CLAIM: The owner rejects a homepage-first redesign plan and asks for direct repository/site
    understanding. The previous plan overreached from title/metadata findings: the homepage already
    has working-example routes, four learning levels, capstones, catalog, contents, and references.
    The previous homepage patch is withdrawn pending evidence; do not apply it.
  EVIDENCE:
  - docs/index.md:21-142
  - Owner correction in this chat on 2026-09-26: read the repo, understand the existing RTD site,
    and make a better plan rather than remake a homepage that already provides guides.
  IMPACT: Reopen discovery. Inspect the rendered site, follow representative reader journeys, read
    actual guide content, and distinguish demonstrated defects from optional copy preferences.
  NEXT: Open the published homepage and follow its guide/example routes; inspect local output/source too.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T22:57:00Z
  TYPE: FACT
  CLAIM: Direct browser inspection now reaches the live homepage and Beginner index successfully.
    Existing cards, curriculum, walkthroughs, source links, search field, and reference navigation
    are present. Beginner opens correctly and lists twelve chapters plus 41 runnable lessons.
    The live site shows version 0.2.50. No homepage redesign defect is established.
  EVIDENCE:
  - context_compass/artifacts/melder_seo_review_20260926/site_inspection.md:1-16
  - https://melder.readthedocs.io/en/latest/
  - https://melder.readthedocs.io/en/latest/beginner/index.html
  IMPACT: Withdraw the claim that new homepage navigation is the priority. Compare actual guide
    content and build freshness next; retain the existing information architecture.
  NEXT: Read constructor-injection, lifetimes, cleanup, and their linked examples in the browser.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T22:58:42Z
  TYPE: FACT
  CLAIM: Read three rendered beginner guides and followed the injection example. The full example
    already supplies the missing snippet setup; lifetimes supplies the mode comparison and five
    examples; cleanup explains ordering/failures and supplies four examples. A blanket guide rewrite
    is not justified. One cleanup cross-link sends readers to GitHub instead of its Sphinx chapter.
  EVIDENCE:
  - context_compass/artifacts/melder_seo_review_20260926/site_inspection.md:18-41
  - src/melder/__version__.py:1-12
  IMPACT: Preserve the existing concept/example design. Verify narrow cross-link and metadata issues,
    and distinguish the live 0.2.50 revision from local 0.2.74 without declaring publication failure.
  NEXT: Read the existing capstone and advanced/expert walkthroughs and inspect their HTML metadata.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T23:00:37Z
  TYPE: FACT
  CLAIM: The full beginner capstone already contains the application tutorial previously proposed:
    four modules, ordinary models, constructor injection, shared/fresh instances, typed consumption,
    real methods/results, assertions, and shutdown. Advanced/expert walkthroughs also exist and were
    read. The issue is not absence of complete application material.
  EVIDENCE:
  - context_compass/artifacts/melder_seo_review_20260926/site_inspection.md
  - https://melder.readthedocs.io/en/latest/beginner/capstone.html
  - https://melder.readthedocs.io/en/latest/advanced/inspection-walkthrough.html
  - https://melder.readthedocs.io/en/latest/expert/codegen.html
  IMPACT: Withdraw the duplicate tutorial deliverables from the earlier proposal. Check source-linked
    precision issues, metadata coverage, discovery behavior, and deployment revision instead.
  NEXT: Read current authored/generated guide sources and exercise catalog/search navigation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T23:03:24Z
  TYPE: FACT
  CLAIM: The live revision matches both local prod and origin/prod (9c3ca5ff5). Current branch is
    codex_features2, so the 0.2.50 vs 0.2.74 difference does not establish deployment failure.
    Catalog filtering returns 33/138 cleanup matches and hosted search returns relevant guides.
    Six representative pages lack descriptions, but their canonicals and robots metadata are correct.
  EVIDENCE:
  - context_compass/artifacts/melder_seo_review_20260926/site_inspection.md
  - README.md:459-501
  - docs/tools/curriculum.py:155-165
  - git branch --show-current and git for-each-ref refs/heads/prod refs/remotes/origin/prod
  IMPACT: Preserve homepage/navigation, existing guides/examples, search, sitemap and publication
    setup. Focus the revised plan on small SEO metadata work and source-aware cross-link correction.
  NEXT: Verify the served robots/sitemap and finish the revised plan with exact implementation scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-26T23:08:59Z
  TYPE: DECISION
  CLAIM: Replace the earlier proposal after direct site inspection. Retain the visible homepage,
    navigation, short concept guides, complete examples and capstones. First scope: short browser
    title suffix and generated cleanup-to-configuration link. Then add descriptions via existing
    source owners and integrate adapted checks. No homepage/guide rewrite or deployment repair.
  EVIDENCE:
  - context_compass/artifacts/melder_seo_review_20260926/improvement_proposal.md:1-133
  - context_compass/artifacts/melder_seo_review_20260926/site_inspection.md:1-96
  - docs/tests/test_curriculum.py:1-63
  - docs/tests/test_example_catalog.py:1-126
  - .github/workflows/docs.yml:1-50
  IMPACT: The revised plan reflects the existing site and corrects the earlier unsupported content
    recommendations. robots.txt/root sitemap remain unverified after tool retrieval failures, not
    diagnosed as broken. Historical site-check output is not presented as a fresh test run.
  NEXT: Implement the narrow corrected scope when the owner selects it; do not apply the withdrawn draft.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-27T00:30:31Z
  TYPE: DECISION
  CLAIM: Owner accepted this work with "turn in your epic then rebuild the assets".
    Inspected the starter and live Sphinx site; corrected the plan and retained the existing homepage.
  EVIDENCE:
  - Owner's explicit turn-in instruction in this chat.
  - context_compass/artifacts/sphinx_publication_quality_20260926/verification.md:1-60
  IMPACT: Closed with the accepted SEO ticket set; evidence retained and current board routes cleared.
    SEO patch contracts are promoted to docs/maintaining.md and archived under patches/completed.
  NEXT: Run the owner-requested final asset regeneration after the entire selected set is turned in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Accepted and turned in at 2026-09-27T00:30:31Z. Inspected the starter and live Sphinx site; corrected the plan
  and retained the existing homepage.
Verification evidence is retained in artifacts/sphinx_publication_quality_20260926/.
Post-closure source assets rebuilt; LLM outputs already current; both freshness checks passed at 00:32:22Z.
