# Melder documentation improvement proposal

Owner-facing proposal from seo_0, 2026-09-26.
Task: TASK-2026-09-26-review-melder-seo-starter.

## Objective

Help an unfamiliar Python developer understand Melder, find the guide for their problem,
and run a complete example. Make that clarity survive future documentation builds.

## 1. Fix the entry page

Use this main heading:

> A dependency graph runtime for Python

Opening:

> Melder wires ordinary Python classes, functions, and instances into a live dependency graph.
> Use dependency injection to connect services, choose when instances are shared or recreated,
> and define how resources are cleaned up.

Keep the existing explanation of connected subsystems, isolated worlds, and agent-operated
infrastructure immediately after it. The broader runtime capabilities remain visible.

Concrete changes are drafted in `homepage-proposal.patch`:

- `docs/conf.py`: use `html_title = "Melder"`.
- `docs/index.md`: add the specific description, use the new heading, retain the old fragment,
  and add six direct guide links before the existing four-level curriculum.

The draft leads with product description. The old slogan can be secondary brand copy elsewhere;
it does not need to occupy the main homepage heading.

The primary starting route remains the existing runnable Hello Melder example. Direct guide
links answer concrete needs: dependency wiring, lifetime selection, cleanup, overrides, inspection,
and agent access. Existing URLs and curriculum labels remain stable.

### Verification before applying/publishing

The proposal passes `git apply --check --verbose`. It has not been applied or rendered.
After adoption, run the documented build pipeline and inspect the resulting title, description,
old heading fragment, and the six destinations. Review the actual browser layout on desktop and
narrow screens. Normal release/version bookkeeping follows the owner's existing repository policy.

## 2. Make the important guides complete

Prioritize these three reader outcomes, in order:

1. **Constructor injection:** take a small application from manual construction to a complete
   Melder graph. Include imports, class definitions, registration, conjure, resolution, an observable
   result, and cleanup. Explain the relevant error and link to explicit selection.
2. **Lifetimes:** show when repeated resolutions return the same or different objects, which scope
   owns each object, and what changes when the scope ends. Describe Melder's exact six lifetimes
   and boundaries; avoid an inaccurate process-global-singleton shorthand.
3. **Cleanup and ownership:** show a scoped resource's full life, explicit disposal, the effect of
   a retained reference, and what the application still owns. Keep the documented disposal contract
   aligned with current implementation and runnable source.

Use separate authored pages where a README excerpt cannot carry the full tutorial:

- `docs/beginner/dependency-injection.md`
- `docs/beginner/lifetimes.md`
- `docs/beginner/cleanup.md`
- `docs/curriculum.toml`: keep each existing ID and select its authored source.

Give the intermediate injection guide its own job: explicit selection and collections. Update its
source/selector deliberately so it no longer repeats the beginner walkthrough.

Use the existing saved examples as the starting evidence and keep executable source in
`UX_and_AIX_experiences`, following that directory's instructions. Read the implementations and
run the applicable examples on Python 3.14t before reporting them as working. Documentation rendering
and runtime example execution are separate checks.

### Acceptance

A reader can start from each guide without undefined variables, missing setup, or invented output.
The guide teaches the result and ownership boundary, and links to the next relevant topic.
The existing inspection walkthrough and agent-access guide remain prominent so the site also
explains the capabilities beyond dependency construction.

## 3. Put descriptions and checks into the build pipeline

Use authored frontmatter for guides. Extend the existing lesson model/loader/renderer with an
optional editorial description for generated examples. A cleaned goal may provide a fallback
only when it accurately describes that page.

Relevant source surfaces are already identified:

- `docs/tools/example_catalog.py`: `Lesson`, `_lesson`, and `_lesson_body`.
- `docs/catalog.toml`: editorial title/description overrides.
- `docs/tests/test_example_catalog.py`: generation and metadata behavior.
- Adapted checker and tests under `docs/tools` and `docs/tests`.
- Existing docs build jobs, reviewed before adding any publication requirement.

Adapt the supplied checker to the repository's source conventions and real generated output.
Make malformed titles/canonicals and unintended indexing directives actionable. Establish intended
version/preview exceptions before treating those assumptions as build failures. Require descriptions
for the homepage and upgraded guides first; expand coverage as good descriptions are authored.

Keep the existing sitemap implementation. Add checks for real defects instead of adding another
sitemap provider. No new SEO dependency has been identified as necessary for this proposal.

### Acceptance

Authored and generated metadata reach the final HTML, meaningful checker tests cover regressions,
and approved preview/version behavior does not fail the build. The current site checker continues
to verify links, anchors, assets, and source fidelity.

## 4. Check what visitors and search engines actually receive

After a reviewed build is published, inspect the homepage, one guide, one example, and one API
page for the intended title, description, canonical URL, and indexing directives. Check the served
root sitemap, redirects, and the published commit/version.

Use Search Console data if available to distinguish branded queries from problem-oriented queries.
Record a baseline before expanding topics. Treat search-result clicks and example downloads as
interest signals; they do not prove successful adoption.

Choose subsequent content from evidence. A worked object-lifecycle/ownership comparison or a live
graph inspection example would expose specific capabilities. Performance comparisons require
equivalent workloads, recorded versions, and actual measured results.

## Order of work

1. Adopt and verify the drafted homepage change.
2. Deliver the three complete guides and distinct intermediate injection material.
3. Add generated descriptions and integrate the reviewed checker.
4. Verify the deployed result and use observed queries/problems to select follow-up content.

The first change is ready for review as a two-file patch. The later changes need their own
implementation tickets and source-level verification before editing. This proposal does not
authorize an automatic publication or runtime API change.

## Evidence and operating constraints

- Existing review and verified source references: `review.md:1-163`.
- Current homepage source: `docs/index.md:1-142`.
- Site title configuration: `docs/conf.py:54-76`.
- Authoring/build and example-execution requirements: `docs/maintaining.md:7-72`.
- Stable chapter routes: `docs/curriculum.toml:46-72`, `106-111`, `137-143`, `270-291`.
- The attached audit is a proposal; no claimed rankings, traffic, or synthetic test results are
  carried forward as independently verified facts.

No product files have been changed. The candidate page/configuration and patch are review artifacts.
