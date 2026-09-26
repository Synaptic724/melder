# Melder SEO starter review

Reviewed by seo_0 on 2026-09-26.
Owning task: TASK-2026-09-26-review-melder-seo-starter.

## Recommendation

Use the homepage title/description idea first, with a shorter main heading. The starter's
repository-specific advice largely matches the current source. Its checker is useful input for
a later documentation change, but has not been validated against a fresh Melder build here.

The supplied material was inspected as a proposal. Its instructions were not treated as the
owner's authorization to install, apply, execute, or publish it.

## What is in the ZIP

| File | What it contains | Assessment |
| --- | --- | --- |
| `homepage-seo.patch` | Changes `docs/conf.py` and the opening of `docs/index.md`. | Small, applicable patch; adapt the heading before using it. |
| `check_seo.py` | A standard-library command-line checker for built HTML and `sitemap.xml`. | Useful local publication checks; needs integration and policy review. |
| `test_check_seo.py` | Nine synthetic `unittest` cases for the checker. | Actual test cases, but they do not build Melder or prove deployment behavior. |
| `README.md` | Proposed installation/build commands, limitations, and follow-up priorities. | The scope limitations are explicit and reasonable. |

The archive is 8,578 bytes. Its SHA256 and exact member sizes are in `inventory.md`.
All four files were read completely. No supplied Python program was executed.

The ZIP does not contain the expanded beginner tutorial, rewritten lifecycle guides, a new
documentation generator, or a replacement website. Those are recommendations in the pasted audit.

## The headline and slogan

**"A runtime you can build on" is serviceable but generic.** It conveys confidence, but says
nothing about Python, dependency graphs, inspection, or ownership. Many unrelated runtimes could
use it. Keep it as optional secondary copy if you like it; let the main heading explain Melder.

Recommended main heading:

> A dependency graph runtime for Python

Recommended opening sentence:

> Wire ordinary Python objects with dependency injection, explicit lifetimes, scoped cleanup,
> and runtime inspection.

Optional secondary tagline:

> Melder — a runtime you can build on.

Recommended sitewide Sphinx suffix:

```python
html_title = "Melder"
```

With the recommended heading, the intended browser title is:

> A dependency graph runtime for Python — Melder

The starter's proposed heading, "Python dependency injection and dependency graph runtime",
is informative but repeats "dependency" and is less natural to read. The opening paragraph and
dedicated injection guides can carry the familiar dependency-injection terminology.

This is an editorial recommendation, not a measured keyword-volume or ranking claim.

### Why the existing title repeats

`docs/index.md:1` supplies the slogan as the page heading. `docs/conf.py:57` supplies
"Melder — a runtime you can build on" as the site suffix. The existing staged HTML at
`_readthedocs/html/index.html:9` contains both.

Sphinx documents that `html_title` is appended to individual page titles:
[Sphinx HTML configuration](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_title).
Google recommends concise, descriptive titles and avoiding repeated boilerplate:
[Google title-link guidance](https://developers.google.com/search/docs/appearance/title-link).

The navigation manifest already calls the root page "Melder" (`docs/navigation.toml:7-11`),
so that label needs no change for this proposal.

## What the homepage patch actually does

1. Sets the site suffix to `Melder`.
2. Adds a page-specific description using MyST frontmatter.
3. Preserves the old `a-runtime-you-can-build-on` fragment as an explicit target.
4. Replaces the opening heading and paragraph; the rest of the homepage stays outside the patch.

The metadata syntax is supported by MyST:
[MyST local configuration and HTML metadata](https://myst-parser.readthedocs.io/en/latest/configuration.html).

The proposed Python 3.14+ and zero-runtime-dependency copy agrees with `pyproject.toml:5-85`.
That verifies declared packaging requirements, not runtime compatibility on every Python build.

## Repository checks behind the recommendation

| Audit point | Current source evidence | Result |
| --- | --- | --- |
| Generated source is overwritten on builds. | `docs/tools/build_docs.py:194-237`, `DocumentationBuilder.prepare` | Confirmed. Edit authored input or a renderer. |
| Curriculum chooses a README section or authored page. | `docs/tools/curriculum.py:103-154`, `_source` and `_chapter` | Confirmed. Exactly one selector is required. |
| Beginner and intermediate injection guides overlap. | `docs/curriculum.toml:46-52` and `106-111` | Both select the same README section; beginner truncates it. |
| Lesson titles support overrides. | `docs/tools/example_catalog.py:139-157`, `_lesson` | Confirmed. Public page IDs need not change. |
| Lesson descriptions need generator support. | `docs/tools/example_catalog.py:23-35` and `200-225` | `Lesson` has no description field and its page renderer emits no description metadata. |
| Catalog links already exist as static HTML. | `docs/tools/example_catalog.py:168-185`, `_cards` | Confirmed. No need to redesign it merely for link discovery. |
| Sitemap generation already exists. | `docs/tools/build_docs.py:265-278`, `_sitemap` | Confirmed. It uses the configured canonical base and declared page IDs. |
| Existing checks cover different concerns. | `docs/tools/check_site.py:14-142` | Links, fragments, duplicate IDs, alt attributes, declared pages, publication boundaries, and source fidelity. |

Preserve the four existing curriculum levels. Add direct problem-oriented links alongside them
if navigation changes are adopted; the builder explicitly enforces their labels and order.

## Checker assessment

The checker inspects local files. It makes no network requests. Its optional `--json` argument
writes a report to the chosen path. It does not install anything or change Melder's runtime.

It checks:

- Nonempty, unique page titles.
- Missing or repeated description metadata, with required-page glob support.
- One H1 and an HTML language declaration, reported as editorial/accessibility warnings.
- A single canonical link exactly equal to the supplied base plus the page's `.html` path.
- `noindex`/`none` in HTML robots or googlebot metadata.
- Sitemap shape, duplicate URLs, local destinations, and audited-page inclusion.

Before adopting it:

- Decide canonical and preview-build policy. Exact self-canonicals and indexable content are
  assumptions in this script, not universal requirements for every documentation version.
- Integrate tests deliberately. The supplied test file imports `check_seo` directly; current docs
  tests add `docs/tools` to their import path (`docs/tests/test_site_check.py:1-12`). Copying only
  the checker does not add its nine tests to repository test discovery.
- Bring new source into the selected Python role's conventions: complete annotations/docstrings,
  no new future-annotations import, and class/config-owned constants rather than module globals.
- Validate a fresh build and add cases for the real generated site and intended exceptions before
  using results to fail publication.

The script explicitly cannot check HTTP headers, robots.txt, redirects, Google's selected
canonical, actual indexing, traffic, or performance. A passing local report cannot establish those.

Read the Docs documents the canonical environment variable as version-specific and serves a
custom root sitemap from the project's default version when present:
[RTD environment variables](https://docs.readthedocs.com/platform/stable/reference/environment-variables.html),
[RTD sitemap behavior](https://docs.readthedocs.com/platform/stable/reference/sitemaps.html).
Those policies should guide a later deployment check.

## Verification performed

- ZIP opened successfully after the owner reattached it; four members inventoried and extracted.
- All starter files, the pasted audit, and the relevant current docs/build sources were read.
- `git apply --check --verbose` succeeded for both files in `homepage-seo.patch`.
- The existing staged HTML independently confirms the duplicated homepage title.
- Official Google, Sphinx, MyST, and RTD documentation was consulted for the claims cited above.
- Unit tests: **Not run.** This pass inspected the supplied programs without executing them.
- Full Sphinx build: **Not run.** The patch was not applied and existing build output was not replaced.
- Live deployment/indexing: **Unverified.** The web tool could not retrieve the live homepage;
  no conclusion about site availability or search indexing follows from that failure.

## Suggested next change

Update `docs/conf.py` and the homepage opening in `docs/index.md` with the shorter heading,
one specific description, and the retained old anchor. Then verify the rendered title, metadata,
fragment, and normal docs checks. Keep the checker integration and expanded tutorials as subsequent
changes with their own concrete scope.

No product source, documentation source, installed dependency, release version, or published site
was changed in this review. The written outputs are the ContextCompass task, inputs, and review.
