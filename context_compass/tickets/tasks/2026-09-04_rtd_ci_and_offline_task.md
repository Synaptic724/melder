# Task: Implement docs CI parity, RTD configuration, and offline outputs

## Metadata
- Task ID: TASK-2026-09-04-rtd-ci-and-offline
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Story: STORY-2026-09-04-rtd-build-and-hosting
- Story Path: ../stories/2026-09-04_rtd_build_and_hosting_story.md
- Status: review
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T22:07:46Z
- Updated: 2026-09-05T09:49:19Z

## Objective
Wire the proven local command into CI and RTD configuration, implement version/canonical/source behavior, and build offline formats.

## Ticket Contract
- ENTRY_GATE: Parent story/blueprint read, dependency milestone available, and this task actively routed.
- EXECUTION_BOUNDARY: .readthedocs.yaml, docs workflow and its required-CI integration, docs dependency
  locks/configuration, offline builders, version/source-link code, docs/maintaining.md, and the
  owner-requested prominent README documentation entry (2026-09-05).
- DEPENDENCIES: Local foundation/catalog; content and reference contracts; live hosting activation is the separate hosted-project task.
- EXIT_GATE: Acceptance checks have evidence; delivery state and parent story are synchronized.
- FAILURE_ESCALATION: Record concrete failures and preserve unaffected progress; do not infer success.

## Scope Boundaries
- In scope: the declared documentation task and necessary focused validation.
- Out of scope: unrelated runtime changes, other agents' assignments, and unrequested account actions.
- User authorization: implementation requested on 2026-09-04; ordinary scoped edits/checks may proceed.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Local builds, source links, offline formats, staging, and generated assets have
  evidence. Owner-requested README entry links are implemented; hosted verification remains separate.

## Steps / Checklist
- [x] Read the exact inputs and record one bounded implementation decision.
- [x] Complete required patch contracts when the change is system-impacting.
- [x] Implement the scoped deliverable with notes before the next tranche.
- [x] Validate meaningful behavior/content and record actual outcomes.
- [x] Synchronize parent story and hand off; closure still requires acceptance.

## Acceptance Criteria
- [x] Local/CI/RTD configuration share deterministic source assembly and dependencies.
- [x] Docs dependencies remain separate from runtime dependencies.
- [x] HTML and defined PDF/ePub handbook outputs are valid and revision-labeled.
- [x] Public-content selection, redirects/canonical inputs, and recovery steps are explicit.
- [x] Workflow/static checks and local output review are recorded.

## Validation
- Normal HTML build and independent validation pass: 294 pages and 35,119 local links, with canonical
  source equality. The earlier 19 cached source-page backlink failures are fixed and regression-tested.
- Documentation tests: 36 passed; removing the fix reproduces the backlink defect in the new test.
- Recorded focused CI workflow suite: 127 tests, zero failures/errors/skips (`ci.xml`).
- Final PDF: 103 pages, all level bookmarks, no blank/clipped pages; visual review recorded.
- Final ePub: 62 XHTML documents and 1,077 internal links pass format/navigation checks.
- HTML archive and all four RTD staging formats match their source bytes; 945 complete-site files.
- All three source build-asset exact checks pass. Repository LLM bundles were regenerated and checked;
  other-corpus bootstrap includes docs/.gitignore without staging unrelated work. See the evidence report.
- These results qualify the recorded inputs. HEAD subsequently advanced to f35b1517863a846b35b7411c27c60b3547fa9cba,
  including concurrent runtime changes; the final hosted candidate needs a fresh build/asset check.
- Hosted project setup, live previews, versions, search, and downloads were not performed.

## Risks / Mitigations
- Canonical source and existing lessons can change concurrently; verify relevant inputs before edits.
- Hosting/dependency availability is an external-state check, not permission to invent completion.
- Keep the four owner-defined learning levels and prominent examples invariant.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-09-05_rtd_local_build_validation.md
  - artifacts/rtd_validation_20260904/rebuild_regression_20260905.log
  - artifacts/rtd_validation_20260904/rebuild_negative_20260905.log
  - artifacts/rtd_validation_20260904/docs_tests_20260905.log
  - artifacts/rtd_validation_20260904/html_20260905.log
  - artifacts/rtd_validation_20260904/links_20260905.log
  - artifacts/rtd_validation_20260904/epub_20260905.log
  - artifacts/rtd_validation_20260904/pdf_20260905.log
  - artifacts/rtd_validation_20260904/pdf_metadata_20260905.json
  - artifacts/rtd_validation_20260904/epub_check_20260905.json
  - artifacts/rtd_validation_20260904/staging_20260905.json
  - artifacts/rtd_validation_20260904/source_check_20260905.log
  - artifacts/rtd_validation_20260904/repo_check_before_20260905.log
  - artifacts/rtd_validation_20260904/repo_build_20260905.log
  - artifacts/rtd_validation_20260904/repo_check_20260905.log
  - artifacts/rtd_validation_20260904/readme_bundle_20260905.log
  - artifacts/rtd_validation_20260904/final_html.log
  - artifacts/rtd_validation_20260904/site_check.log
  - artifacts/rtd_validation_20260904/ci.xml
  - artifacts/rtd_validation_20260904/source_assets.log
  - artifacts/rtd_validation_20260904/handbook_pdf.log
  - artifacts/rtd_validation_20260904/handbook_epub.log
  - artifacts/rtd_validation_20260904/fresh_html_20260905.log
  - artifacts/rtd_validation_20260904/fresh_links_20260905.log
  - artifacts/rtd_validation_20260904/fresh_links_20260905.json
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Record task-owned artifact disposition before accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Implement docs CI parity, RTD configuration, and offline outputs
- IF_UNKNOWN: none

## Noting Behavior
- Finish a coherent read/work unit and append evidence, impact, and one next action.
- Keep notes append-only; label unverified claims explicitly.

## Notes
- DATETIME: 2026-09-04T22:07:46Z
  TYPE: PLAN
  CLAIM: Implement this bounded part of the accepted documentation program under its existing story.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:293-344
  - Owner implementation instruction on 2026-09-04.
  IMPACT: The complete program now has explicit execution tasks and dependency boundaries.
  NEXT: Activate this task when its dependency milestone is available.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T00:50:29Z
  TYPE: DECISION
  CLAIM: Add a reusable docs workflow to the existing required CI graph, including the exact job
    evidence list in ci_policy.py. Keep runtime verification in its existing 3.14t workflow.
    RTD supports Python 3.14 and per-format build.jobs overrides; outputs must be staged under
    READTHEDOCS_OUTPUT for html/htmlzip/pdf/epub. Local and hosted formats must share the same builders.
    The handbook will contain the four guide levels, glossary, and selected complete examples.
  EVIDENCE:
  - .github/workflows/ci.yml:1-82
  - .github/scripts/ci_policy.py:16-25
  - .github/scripts/ci_policy.py:96-117
  - https://docs.readthedocs.com/platform/stable/config-file/v2.html
  - https://docs.readthedocs.com/platform/stable/build-customization.html
  IMPACT: A docs failure must block merge-ready just like the existing mandatory checks; account setup
    remains separate from checked-in configuration. Owner retains all commits and pushes.
  NEXT: Implement the curated handbook and format staging, then wire CI and RTD configuration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T01:14:35Z
  TYPE: MEASURE
  CLAIM: Native Sphinx ePub builds 59 selected source documents. The compiled PDF is 106 letter-sized
    pages with bookmarks, no missing-glyph/font warnings, and two small vertical layout warnings pending
    visual review. Tectonic 0.17.0 was downloaded from the official release and verified by archive SHA256;
    its pinned Linux/Windows installer is now checked in for reproducible CI/RTD use.
    Added per-format RTD commands and a mandatory documentation job to CI and its exact evidence policy.
  EVIDENCE:
  - docs/handbook.toml
  - docs/tools/handbook.py
  - docs/tools/install_tectonic.py
  - .readthedocs.yaml
  - .github/workflows/docs.yml
  - artifacts/rtd_validation_20260904/handbook_epub.log
  - artifacts/rtd_validation_20260904/handbook_pdf.log
  IMPACT: Offline artifacts are real, with visual/link checks still required. Source-asset check identified
    two stale generated manifests after the documentation-only source edits; regenerate them before handoff.
  NEXT: Add deterministic site checks, review rendered PDF pages, and run the CI policy tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T01:52:29Z
  TYPE: FACT
  CLAIM: The full HTML build passes at 294 pages, but the new independent link validator found
    nine broken viewcode back-links on ResearchLane. Sphinx stores one reference-module prefix per
    physical module; mixing root aliases for its enums with a concrete returned class gives incorrect
    anchors. Render all objects at their canonical import origins and register only real facade aliases
    in the Python domain, preserving public names without inventing a melder.ResearchLane export.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/site_check.log
  - docs/tools/api_reference.py
  - Sphinx 9.1.0 sphinx/ext/viewcode.py:125-180
  IMPACT: Strict rendering alone does not prove navigation. Keep the link gate mandatory.
  NEXT: Correct canonical API source rendering and validate every public alias/back-link.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T08:58:00Z
  TYPE: MEASURE
  CLAIM: Re-entry checked HEAD 15e06e7de1de68b1af150eabc7e978ead6155c76 and the saved validation artifacts.
    The site contains 294 declared pages and 360 HTML files. Its 35,119 checked local links expose 19
    broken viewcode backlinks across ResearchLane/LaneState/LaneType and ULID_Factory/new_ulid.
    The focused CI workflow report records 127 passing tests. Source assets were regenerated.
    Owner paused implementation for committing and has now instructed continue. Earlier Notes remain
    intact; misplaced notes were consolidated here and the duplicate handoff heading removed.
  EVIDENCE:
  - docs/_build/site-check.json:1-26
  - artifacts/rtd_validation_20260904/site_check.log:1-20
  - artifacts/rtd_validation_20260904/ci.xml:1-1
  - artifacts/rtd_validation_20260904/source_assets.log:1-3
  - Owner pause instruction and subsequent continue instruction on 2026-09-05.
  IMPACT: Implementation exists but is not accepted or release-ready. A fresh Sphinx environment is
    the next diagnostic for stale viewcode module prefixes, not an established fix.
  NEXT: Inspect the current docs builder and API alias extension, then run a fresh-environment HTML build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:03:00Z
  TYPE: DECISION
  CLAIM: The builder deletes its HTML output but reuses docs/_build/doctrees. Sphinx viewcode retains
    each physical module's original refname while source code is unchanged; current generated API
    directives already use canonical origins. Test that exact cache boundary with a separate fresh
    environment/output before changing the API adapter or runtime. Source-link correctness remains
    mandatory; suppressing these links or changing Melder exports is outside the chosen fix.
  EVIDENCE:
  - docs/tools/build_docs.py:231-249
  - docs/tools/api_reference.py:96-125
  - docs/tools/api_aliases.py:29-49
  - Sphinx 9.1.0 sphinx/ext/viewcode.py:111-181
  - Sphinx 9.1.0 sphinx/ext/viewcode.py:300-337
  - https://www.sphinx-doc.org/en/master/man/sphinx-build.html#cmdoption-sphinx-build-E
  IMPACT: Patch rtd_site_2026_09_04 maps validated preparation to DocumentationBuilder.prepare,
    source/revision rendering to ApiReference and PublicApiAliases, and link fidelity to SiteCheck.
    The patch's same-command reproducibility contract requires cache-independent output.
  NEXT: Prepare current sources, build isolated fresh HTML, and run the same SiteCheck against it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:07:00Z
  TYPE: MEASURE
  CLAIM: Isolated fresh-environment rendering succeeds and SiteCheck reports zero errors across
    294 declared pages and 35,119 local links, with exact canonical lesson/helper source equality.
    The 19 prior source-page backlink failures disappear without changing API aliases or runtime
    exports. The PDF compiler's retained log confirms the revised handbook has 101 pages.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/fresh_links_20260905.log:1-1
  - artifacts/rtd_validation_20260904/fresh_links_20260905.json:1-6
  - docs/tools/build_docs.py:231-249
  - docs/tools/handbook.py:134-151
  IMPACT: Make both normal site and handbook Sphinx invocations use fresh environments so output
    depends on current source, not stale extension cache state. Add one real rebuild regression.
  NEXT: Update DocumentationBuilder.build and Handbook.build with -E and prove changed canonical
    API imports retain correct source-to-documentation backlinks across consecutive builds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:10:00Z
  TYPE: MEASURE
  CLAIM: Both site and handbook builders now request a fresh Sphinx environment. The maintainer
    guide explains why. All 13 build/presentation tests pass, including a real two-build regression:
    two classes move from facade to canonical module directives and both generated backlinks resolve.
  EVIDENCE:
  - docs/tools/build_docs.py:231-254
  - docs/tools/handbook.py:134-154
  - docs/tests/test_build_docs.py:106-150
  - artifacts/rtd_validation_20260904/rebuild_regression_20260905.log:1-7
  IMPACT: The normal command now enforces the cache-independent behavior proven by the diagnostic.
    Full-site and final packaging checks must run through that command before acceptance.
  NEXT: Confirm the regression fails without fresh environments, then run the full docs checks and
    final HTML/handbook builds; keep live hosting setup with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:09:00Z
  TYPE: MEASURE
  CLAIM: The new real-rendering regression fails exactly as intended when -E is removed from the
    Sphinx subprocess arguments: the source page links to fixture_api.Primary while the target only
    contains fixture_api.impl.Primary. Restoring the unchanged builder passes the same test.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/rebuild_negative_20260905.log:1-18
  - artifacts/rtd_validation_20260904/rebuild_regression_20260905.log:1-7
  IMPACT: This is a reproduced reader-navigation regression with a verified fix, not an assertion
    about a particular command flag. Broader local qualification can proceed.
  NEXT: Run the full docs test suite, then the normal HTML build and site validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:11:37Z
  TYPE: MEASURE
  CLAIM: The normal documented build command now passes the full site check: 294 pages, 35,119 local
    links, exact lesson/helper bytes, zero errors. All 36 documentation tests passed. PDF metadata and
    its retained compiler log both confirm the corrected 101-page handbook, whose final rebuild and
    visual inspection remain. Current branch is codex_features2; the owner is configuring hosted RTD.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/docs_tests_20260905.log:1-7
  - artifacts/rtd_validation_20260904/links_20260905.log:1-1
  - docs/_build/site-check.json:1-6
  - docs/tools/handbook.py:134-176
  IMPACT: The source-link blocker is resolved through the normal pipeline. Continue with final offline
    build/review, staging, and generated-asset checks before handing over the signed-commit boundary.
  NEXT: Rebuild ePub/PDF through the updated handbook command and validate their navigation and layout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:15:07Z
  TYPE: MEASURE
  CLAIM: Final ePub and PDF compilation completed successfully through the updated fresh-environment
    handbook builder. The selection now has 60 source pages including the separate selected-examples
    contents page. TeX still reports small vertical overflows that need visual inspection; successful
    compilation is not layout acceptance. RTD documentation confirms _readthedocs/<format> staging.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/epub_20260905.log:1-1
  - artifacts/rtd_validation_20260904/pdf_20260905.log:1-296
  - docs/tools/handbook.py:81-158
  - https://docs.readthedocs.com/platform/stable/build-customization.html#where-to-put-files
  IMPACT: Review actual final files, check ePub navigation/manifest and PDF page bounds, and compare
    each staged output with its locally validated origin before making a download-readiness claim.
  NEXT: Inspect the final offline files and render PDF pages for layout review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:17:28Z
  TYPE: FACT
  CLAIM: The latest rebuilt PDF is 103 pages, superseding the earlier 101-page artifact. It has no
    blank or near-empty pages; bookmarks preserve Beginner, Intermediate, Advanced, Expert, selected
    examples, and glossary. All pages were rendered to PNG for review. Owner requested a visual
    preview; the local HTTP server was restarted on loopback port 8765 and GET /index.html returned 200.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/pdf_metadata_20260905.json:1-32
  - docs/_build/pdf-review/page-001.png
  - Local preview command: python -m http.server 8765 --bind 127.0.0.1 --directory docs/_build/html
  - Owner preview request on 2026-09-05.
  IMPACT: Owner can inspect http://127.0.0.1:8765/ while final download checks continue. Leave this
    preview available and preserve the generated HTML during handbook review.
  NEXT: Review rendered PDF pages and verify ePub/archive/staged download contents.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:22:19Z
  TYPE: MEASURE
  CLAIM: Reviewed all 103 PDF pages through contact sheets and full-page renders for the three
    small TeX overflow locations. No overlap, clipping, missing-glyph boxes, or blank pages were
    observed. Text geometry checks found zero clipped or narrow-margin pages. The ePub contains
    62 XHTML documents and 61 spine entries; all 1,077 local links, manifest/spine references, and
    mimetype placement/compression checks passed.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/pdf_metadata_20260905.json:1-32
  - artifacts/rtd_validation_20260904/epub_check_20260905.json:1-6
  - docs/_build/pdf-review/page-035.png
  - docs/_build/pdf-review/page-048.png
  - docs/_build/pdf-review/page-073.png
  IMPACT: Final local handbook artifacts have rendering/navigation evidence. The small TeX warnings
    remain visible in logs; they were investigated, not suppressed. Hosted companion URLs still
    depend on the owner's actual RTD project and published revision.
  NEXT: Build the full HTML archive, stage all four formats locally, and compare every staged byte.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:23:35Z
  TYPE: MEASURE
  CLAIM: The complete HTML archive matches all 945 files in the built tree byte-for-byte. Local RTD
    staging also matches the HTML tree and each archive/ePub/PDF origin exactly. Formats are 12,266,441
    bytes (HTML zip), 211,427 bytes (ePub), and 481,533 bytes (PDF), with hashes retained in the report.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/staging_20260905.json:1-20
  - docs/tools/build_docs.py:266-319
  IMPACT: All four local format outputs and RTD copy locations are validated. This proves staging,
    not account configuration or hosted publication. Final generated-asset checks remain.
  NEXT: Check source/repository build assets, refresh stale documentation corpus inputs, and record
    any concurrent-lane changes before handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:25:06Z
  TYPE: DECISION
  CLAIM: All three package source-asset checks pass. Repository LLM src/tests/other fingerprints are
    stale after the earlier committed implementation. There are no tracked src/tests edits in the
    current worktree, but codex_1 has an untracked ordered-disposal component test. The only untracked
    eligible docs input outside ContextCompass is docs/.gitignore.
  EVIDENCE:
  - artifacts/rtd_validation_20260904/source_check_20260905.log:1-3
  - artifacts/rtd_validation_20260904/repo_check_before_20260905.log:1-7
  - llm_support/README.md:55-94
  - Read-only git diff --name-only -- src tests and untracked-path inventory on 2026-09-05.
  IMPACT: Regenerate existing tracked src/tests inputs; finish this docs bootstrap's other corpus with
    --include-untracked so docs/.gitignore is included without staging. Do not capture or change the
    other agent's unfinished untracked test; its owner will refresh that corpus at their own handoff.
  NEXT: Regenerate the three LLM corpora and run their matching checks without changing the Git index.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:30:16Z
  TYPE: DECISION
  CLAIM: Owner reviewed the local preview positively and explicitly requested a prominent direct
    documentation link in README. The header currently has only a small RTD status badge; its
    documentation table is near the end. Add a centered Read the Documentation heading plus Examples
    and Full Contents links below the badges, using the existing public melder.readthedocs.io base.
  EVIDENCE:
  - README.md:1-17
  - README.md:1036-1052
  - Owner README direct-link request on 2026-09-05.
  IMPACT: This is an authorized publication-entry scope addition. Keep the four-level curriculum intact,
    preserve the existing badge, and do not put a localhost address in the public README. The RTD
    project is being added by the owner; current hosted reachability remains unverified.
  NEXT: Add the README entry links and refresh the affected repository documentation bundle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:39:40Z
  TYPE: MEASURE
  CLAIM: README now has a centered Read the Documentation heading directly below the badges,
    followed by Browse Examples, Full Table of Contents, and the exact four-level progression.
    The lower documentation table now describes the complete site. Navigation validates 294 pages
    and 54 assets after the edit; the affected LLM other corpus was refreshed and its check passes.
    Browser checks confirmed catalog filtering/reset and completed Spellbook search. Local builds,
    downloads, source-asset checks, and repository bundle evidence are consolidated in the report.
  EVIDENCE:
  - README.md:9-23
  - README.md:1043-1056
  - artifacts/rtd_validation_20260904/readme_bundle_20260905.log:1-3
  - artifacts/2026-09-05_rtd_local_build_validation.md:1-62
  IMPACT: Local implementation is ready for owner review and signing. Account setup is owner-run;
    comprehensive S9 interaction/accessibility and live hosted verification remain open. No commit,
    push, account mutation, publication, or ticket closure was performed.
  NEXT: Owner reviews/commits the local result; resume hosted verification when the project URL/branch
    is confirmed, and finish the S9 quality audit against that candidate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:49:19Z
  TYPE: FACT
  CLAIM: Consumed codex_1's notice that ordered-disposal producer changes landed in Spellbook, Bind,
    Spell, and focused tests after this task's earlier qualification. Read-only Git inspection now
    shows HEAD f35b1517863a846b35b7411c27c60b3547fa9cba. README/docs/LLM edits are included in that
    commit. Remaining worktree changes include other agents' tests and final coordination/ignore files.
    No commit or push was attempted by codex_2.
  EVIDENCE:
  - tickets/tasks/2026-09-04_ordered_disposal_bind_and_spell_task.md
  - artifacts/2026-09-05_rtd_local_build_validation.md:1-70
  - Read-only git log -1, git status --short, and git diff --stat -- README.md docs llm_support.
  IMPACT: Keep the existing preview available as the validated snapshot. Do not present its earlier
    source/asset proofs as qualification of newer runtime changes. Rebuild the final candidate once
    concurrent source work settles; each owning lane retains its source/test/asset responsibility.
  NEXT: Finish S9 and hosted verification against the owner's chosen final revision/project.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Applicable Anti-Patterns
- [ ] No silently omitted content or invented validation.
- [ ] No unrecorded scope changes or interference with another agent's work.

## Context / Handoff Summary
CI/RTD per-format configuration, required CI documentation integration, and native handbook builders
are implemented. The local site has 294 declared pages, including the four exact README levels,
48 guide chapters, all 133 saved lesson pages, and expanded references.
The source-link blocker is fixed: normal builds now pass all 35,119 local links and 36 docs tests.
Final PDF/ePub visual/structural checks and complete HTML archive/RTD staging comparisons pass.
Repository LLM bundles are refreshed and checked. README has prominent public docs/example/contents links.
This task is in review, not closed. Next: owner review/signing, hosted-project verification, and S9 audit.
HEAD is now f35b1517863a846b35b7411c27c60b3547fa9cba and includes newer concurrent runtime work.
Rebuild/recheck the final candidate after it settles; recorded green results describe the earlier inputs.
Hosted project/account setup and live feature verification remain separate unfinished work.
The local preview remains available on http://127.0.0.1:8765/. Owner handles every commit/push;
preserve the concurrent disposal and workflow lanes. No completion or launch acceptance is claimed.
