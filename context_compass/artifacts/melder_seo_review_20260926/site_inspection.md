# Direct inspection of Melder's Sphinx site

## Published homepage and Beginner entry

- Observed in the browser on 2026-09-26, https://melder.readthedocs.io/en/latest/.
- The page renders the Melder banner, slogan, a plain-language dependency-graph explanation,
  three-verb summary, install command, and Python requirement.
- It already links directly to Hello Melder, examples, Full Contents, all four levels, and four
  substantial walkthroughs/capstones. It also links architecture and API reference.
- Clicking Beginner works. The level page provides a Start here link, learning outcomes, all
  twelve chapter routes, and a link to all 41 beginner lessons.
- The browser visibly identifies the published site as Melder 0.2.50 / latest.
- The HTML/browser title repeats the slogan, as previously recorded. That title issue is not
  evidence that the homepage layout or navigation needs replacement.
- Conclusion for this route: navigation and the existing entry structure work; no redesign
  requirement established. The guide content and version freshness still need direct inspection.

## Beginner guides and the linked injection example

- Read the full rendered constructor-injection, lifetime, and cleanup pages.
- Constructor injection is a short concept explanation with a partial snippet, followed by a
  working link to Intermediate 15. That linked page includes the full 37-line script: import,
  Database, ReportService, main, binding, conjure, name-based meld, assertion, and entrypoint.
- The lifetime page has the six-mode comparison table and five linked examples. Its four table
  columns render correctly; the unnamed tier-indicator header is simply omitted in AX text.
- Cleanup covers per-spell disposal vocabulary, matched-method ordering, the configuration-wide
  block, exceptions, and four runnable examples. It is not an empty or missing guide.
- The cleanup guide's inline "configuration guide" link opens the GitHub source Markdown on prod,
  rather than its existing Sphinx chapter. This is a concrete continuity issue to trace in source.
- The three concept guides and injection example publish source links pinned to commit
  9c3ca5ff527903f5cb83f0b7ff8ad7033abb0ef9 and display Melder 0.2.50 / latest.
- Local src/melder/__version__.py declares 0.2.74. This establishes a version difference, not a
  failed deployment; the intended publication revision still needs checking.
- Conclusion: the site's deliberate concept-to-runnable-example structure already supplies the
  material the earlier proposal claimed should be newly written. Withdraw the blanket rewrite.

Observed routes:
- https://melder.readthedocs.io/en/latest/beginner/dependency-injection.html
- https://melder.readthedocs.io/en/latest/examples/intermediate/15-constructor-di-by-annotation.html
- https://melder.readthedocs.io/en/latest/beginner/lifetimes.html
- https://melder.readthedocs.io/en/latest/beginner/cleanup.html

## Existing complete walkthroughs

- Read the entire rendered beginner capstone. It already teaches a four-file orders application:
  models, bootstrap, typed consumer, and entrypoint. All four sources appear on the page, along with
  expected output, download instructions, identity assertions, and guaranteed shutdown.
- This capstone already covers constructor injection, shared/fresh lifetimes, resource ownership,
  and cleanup together. Creating another new tutorial for the same work is not the starting plan.
- Read the rendered inspection walkthrough. It is an explicit ordered route through five saved
  examples, covering world isolation, Rift startup/attachment, viewer navigation, and visibility.
- Read the rendered expert codegen guide. It contains the verb/result table, policy limits,
  complete-application explanation, 126-line main-function extract, and six linked full examples.
- Capstone HTML has a valid version-local canonical and no robots noindex tag. No description meta
  element was found in that page's head.
- Local HEAD is 4647d50d0ea43bcb9e05f3dd2b9785ec7c92e769 (2026-09-26). The reviewed docs,
  README, and version file have no uncommitted Git diff; publication/source-revision alignment
  is therefore a distinct item to check before proposing content changes.

Observed routes:
- https://melder.readthedocs.io/en/latest/beginner/capstone.html
- https://melder.readthedocs.io/en/latest/advanced/inspection-walkthrough.html
- https://melder.readthedocs.io/en/latest/expert/codegen.html

## Search, metadata, and revision alignment

- The catalog displays 138 saved examples. Entering "cleanup" in its filter produces
  "33 of 138 examples" and relevant disposal/cleanup/capstone results.
- The Read the Docs search modal returns the cleanup guide first, then the explicit cleanup
  example and scoped-cleanup lesson for "cleanup". The route works; no search replacement is indicated.
- Direct DOM inspection of six rendered pages found no description meta tag: capstone, injection
  example, lifetimes, cleanup, inspection walkthrough, and expert codegen.
- All six had the expected corresponding canonical URL and no robots/googlebot noindex metadata.
- The repeated site slogan is present in each browser title. It can be removed from the suffix
  without changing the visible homepage heading or layout.
- Revision check resolved the apparent freshness issue: local branch is codex_features2; both
  local prod and origin/prod point to 9c3ca5ff5, the full hash printed by the published source links.
  The live 0.2.50 site therefore matches the known publication branch. Local 0.2.74 is on the feature
  branch. Do not classify this as a failed/stale deployment.
- Read current authored capstone/install/errors/configuration/inspection/codegen sources in full,
  and generated injection/lifetimes/cleanup/Hello pages in full. The guide/example structure is explicit.
- Read README lines 391-510: the external configuration link is authored at line 496, then retained
  by the curriculum renderer. Keep GitHub's README link useful; localize it when generating Sphinx.

## Verification limits

- robots.txt navigation was blocked by the browser client; the web fetch tool also could not
  retrieve robots.txt or the root sitemap. Their deployed contents remain unverified. These tool
  failures do not establish an HTTP failure or crawler problem on the site.
- The stored local site-check.json says 300 declared pages, 366 HTML files, 36,469 local links,
  and zero errors. It is historical output; no fresh whole-site link check is claimed in this pass.
- Read the current curriculum/catalog test modules and docs workflow in full. Existing CI already
  runs source-model checks, Sphinx with warnings treated as errors, site checks, and offline builds.
- No browser layout defect or failed reader route was found in the inspected desktop paths.
- No claim is made about Google indexing/ranking, all pages, mobile layout, HTTP headers, or
  example runtime execution. These are different checks from reading the docs in a browser.
