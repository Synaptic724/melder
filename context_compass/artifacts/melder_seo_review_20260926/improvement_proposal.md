# Melder documentation improvement plan — revised after direct inspection

Prepared by seo_0 on 2026-09-26. This replaces the earlier homepage-first proposal.
Task: TASK-2026-09-26-review-melder-seo-starter.

## What the inspection changed

The existing homepage, guide structure, examples, and capstones are doing their jobs. I had
proposed new content before reading the complete material already linked from those guides.
That recommendation is withdrawn. Do not apply homepage-proposal.patch or its draft source copies.

Direct browser inspection covered the homepage, Beginner entry, injection/lifetimes/cleanup guides,
the full linked injection example, beginner capstone, inspection walkthrough, expert codegen guide,
the example catalog filter, and Read the Docs search. The relevant authored/generated sources,
renderers, tests, and docs workflow were also read.

The capstone already contains a complete four-module application with constructor injection,
shared and fresh instances, typed consumption, assertions, expected output, and explicit shutdown.
The small concept pages deliberately link runnable source; they do not need to become duplicate
capstones. The catalog has 138 examples, and its cleanup filter and hosted search worked.

## Confirmed findings

| Finding | Evidence | Meaning |
| --- | --- | --- |
| Repeated slogan in browser titles | Live title plus docs/conf.py:57 | A small title-template cleanup; it does not justify a new visible homepage. |
| Missing description metadata on six sampled pages | DOM inspection of capstone, injection example, lifetimes, cleanup, inspection walkthrough, codegen | Opportunity to supply page-specific snippet copy; absence does not mean the page cannot rank. |
| Cleanup's configuration link leaves the docs for GitHub | README.md:496, generated cleanup page, live link | Keep readers on the matching version's Sphinx chapter while retaining the README's useful GitHub link. |
| Canonicals and indexing metadata on those six pages | Each canonical matches its page; no robots/googlebot noindex found | No repair justified for these observed tags. |
| Live site uses 0.2.50 while the current checkout uses 0.2.74 | Live source hash matches local prod and origin/prod, both 9c3ca5ff5; checkout is codex_features2 | Expected branch distinction, not evidence of failed deployment. |

## First change: narrow fixes to the existing site

### 1. Shorten the shared browser-title suffix

- Change only html_title in docs/conf.py from the full slogan to "Melder".
- Keep the visible homepage heading, banner, cards, learning levels, and walkthroughs.
- Result: the current homepage title becomes "A runtime you can build on — Melder"; a guide title
  becomes "Constructor dependency injection — Melder".
- The separate html_short_title already equals Melder.

Why: this removes actual repeated boilerplate. Choosing a new slogan is a separate editorial
choice; it is not a prerequisite for improving the site's metadata.

### 2. Keep the configuration cross-link inside Sphinx

- Extend docs/tools/curriculum.py::Curriculum._rewrite_tour_links for the known existing
  configuration-guide URL so the generated cleanup chapter links to ../intermediate/configuration.md.
- Retain the GitHub destination in the root README, where that link has a different audience.
- Add a focused docs/tests/test_curriculum.py regression that verifies the generated local route
  and preservation of the canonical README text.
- Validate the resulting anchor/link through the existing site checker.

This fixes a demonstrated detour without replacing the guide or changing public URLs.

## Second change: add descriptions through the existing source model

Start with the homepage, the inspected guide pages, and the constructor-injection example. Author
short descriptions of the content already present. This is metadata work, not a guide rewrite.

Use each existing source owner:

- Authored pages: MyST description frontmatter, with visible body content retained.
- README-derived chapters: optional chapter description in docs/curriculum.toml, emitted by
  docs/tools/curriculum.py. Do not fork those chapters just to add metadata.
- Generated examples: optional editorial description on Lesson and its TOML override, consumed by
  docs/tools/example_catalog.py. Do not add a config field that the renderer ignores.
- Keep one description owner per page; test the final HTML for exactly one nonempty tag and correct
  escaping. Do not repeat one generic description on every page.

Likely source scope for this change:
- docs/index.md (metadata only)
- docs/beginner/capstone.md, docs/advanced/inspection-walkthrough.md, docs/expert/codegen.md
  (metadata only)
- docs/curriculum.toml and docs/tools/curriculum.py
- docs/catalog.toml and docs/tools/example_catalog.py
- docs/tests/test_curriculum.py and docs/tests/test_example_catalog.py

Google may use a meta description or choose page text for its snippet. This work gives it useful,
page-specific copy; it does not establish a ranking increase.
[Google snippet guidance](https://developers.google.com/search/docs/appearance/snippet).

## Third change: adapt the starter's checker to the actual pipeline

Use it to catch regressions in the metadata we have deliberately added. Preserve the existing
site checker, whose link/source-fidelity work is already part of CI.

- Integrate the supplied tests under the existing docs test discovery and import conventions.
- Bring new checker code into the selected role's typing/docstring conventions.
- Require descriptions only for the reviewed pages initially.
- Use an explicit base URL for a local/CI audit. The current builder emits a sitemap only when
  READTHEDOCS_CANONICAL_URL is supplied; do not bolt on a check that assumes every local build has it.
- Respect RTD's supplied base and intentional preview/version indexing policies.
- Review sitemap/root-URL behavior before making the supplied exact self-canonical assumptions
  a hard publication gate. The checker is an input, not an authority over hosting policy.

Relevant files: docs/tools/check_seo.py and docs/tests/test_check_seo.py (new, adapted), the docs
workflow, .readthedocs.yaml, and docs/maintaining.md. Final integration scope belongs in its own
implementation ticket after the first metadata change is verified.

## Verification

Run the established docs workflow after implementation:

1. python -m unittest discover -s docs/tests -q
2. python docs/tools/build_docs.py check
3. python docs/tools/build_docs.py build
4. python docs/tools/check_site.py

Inspect the rendered title, descriptions, and corrected cross-link in a browser. Existing handbook
checks remain part of CI. These changes do not require new application examples or runtime changes.

No test suite or full build was run during this inspection. Browser route/filter/search checks
were actually performed; the historical local report is identified separately in site_inspection.md.

## What remains unknown

- The deployed robots.txt and root sitemap could not be retrieved through the available browser/web
  tools. This is unverified, not evidence that either is broken. Inspect them before changing policy.
- Google indexing, query impressions, click-through, and selected canonicals need actual Search
  Console evidence. No diagnosis of poor rankings is established by this inspection.
- The feature branch should reach the normal prod publication flow when the owner intends it to;
  a private/local version increase alone does not justify changing RTD settings.

## Scope decision

Retain the existing homepage layout, guides, four levels, capstones, example catalog, search,
URLs, and sitemap generator. Implement the title/cross-link corrections first, then descriptions,
then enforce the verified metadata with the adapted checker. Select any later content work from
observed reader questions or search data rather than assuming the current documentation is missing.

Detailed observed pages and limits: site_inspection.md. Earlier review/proposal artifacts are
retained as history; their homepage and guide-rewrite recommendations are superseded here.