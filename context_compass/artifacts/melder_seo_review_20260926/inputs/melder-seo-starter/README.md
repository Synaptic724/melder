# Melder SEO starter kit

Prepared 2026-09-26 from the `prod` Sphinx source inspected through the connected
GitHub service and selected live Read the Docs pages.

## Scope and test status

A normal `git clone` was attempted, but the execution environment could not resolve
github.com. The source was reviewed via GitHub instead. This is not a repository
clone, a complete crawl, or a completed Sphinx build. No remote files were changed.
No Google Search Console, live HTTP headers, robots.txt, or live sitemap results
were verified. Those retrieval failures are not evidence that the site is broken.

- `homepage-seo.patch` changes the homepage title/intro and adds a MyST description;
  it also replaces the repeated sitewide title slogan with `Melder` and retains
  the old homepage heading anchor as an explicit MyST target.
- `check_seo.py` audits the locally built HTML and page-level sitemap using only
  Python's standard library. It complements the existing `check_site.py`.
- `test_check_seo.py` contains nine synthetic tests; all nine passed here.

The patch was checked against reconstructed excerpts of the inspected files, not
against a full checkout. Run `git apply --check` and the real documentation tests
before adopting it. It intentionally does not rename URLs, change version policy,
edit generated output, add dependencies, or modify any runtime behavior.

## Apply the small patch

From a clean repository checkout, review the patch, then run (adjust its path):

```bash
git apply --check /path/to/melder-seo-starter/homepage-seo.patch
git apply /path/to/melder-seo-starter/homepage-seo.patch
```

## Build and audit

Use the Python 3.14 documentation environment required by this repository.
Copy `check_seo.py` to `docs/tools/check_seo.py` before using these commands.
The environment variable below is for this local audit or GitHub CI only. On
Read the Docs, preserve the platform-provided value rather than hardcoding it.

```bash
python -m pip install -r docs/requirements.txt
python -m unittest discover -s docs/tests -q
python docs/tools/build_docs.py check
export READTHEDOCS_CANONICAL_URL="https://melder.readthedocs.io/en/latest/"
python docs/tools/build_docs.py build
python docs/tools/check_site.py
python docs/tools/check_seo.py docs/_build/html \
  --base-url "$READTHEDOCS_CANONICAL_URL" \
  --require-description index.html \
  --json docs/_build/seo-report.json
```

The checker is intentionally strict about version-local self-canonicals and
Melder's existing `html` builder, which uses `index.html` paths in its sitemap.
It is not a universal SEO validator. Review intentional exceptions before making
it a deployment gate. It assumes audited content pages are intended for indexing;
it should not be used unchanged for intentionally noindexed preview builds.

Descriptions are warnings except for explicitly required page globs. After adding
summaries to a group of pages, add an argument such as
`--require-description 'beginner/*.html'`. Duplicate titles, duplicate description
tags, missing/wrong canonicals, missing local sitemap destinations, and accidental
noindex on an audited content page are errors. An unmatched required-description
glob is an error so a misspelled route cannot silently bypass the policy.

A single H1 and an HTML language declaration are useful documentation conventions;
the checker does not pretend either is a guaranteed Google ranking rule. It does
not enforce a magic title length, description length, or word count.

Run its fixture tests from this starter-kit directory:

```bash
python -m unittest -v test_check_seo.py
```

## Highest-value next changes

1. Expand `beginner/dependency-injection` into a self-contained constructor-injection
   tutorial, and distinguish `intermediate/dependency-injection` as explicit and
   collection injection. Both currently select the same README section, with the
   beginner chapter taking a truncated part.
2. Expand lifetimes, scoped cleanup, and override guides around complete runnable
   tasks. Use source-backed code and actual recorded test output; do not fabricate
   execution output, performance wins, or security guarantees.
3. Use existing `docs/catalog.toml` lesson `title` overrides rather than renaming
   source files or public page IDs. Add per-lesson description support to the
   `Lesson` model and renderer before inventing a new config field.
4. Keep the four required tier labels. `DocumentationBuilder.load()` enforces them.
   Add a task-oriented navigation layer without replacing that contract.
5. Make metadata part of generation. `docs/_build/source` is replaced on every
   build. Edit authored files or their manifest/renderer, never generated pages.
6. Verify the actual robots.txt, root sitemap, response headers, redirects, and
   Google-selected canonicals. The existing custom `_sitemap()` and
   `READTHEDOCS_CANONICAL_URL` support should be tested, not replaced blindly.

## Important distinctions

The `.readthedocs.yaml` `search.ranking` and `search.ignore` settings control
Read the Docs search, not Google ranking or Google indexing. Canonical base URLs
provided by Read the Docs are version-specific, not an automatic consolidation of
all versions into `/latest/`. Melder's own custom sitemap includes its declared
pages and can replace Read the Docs' generated sitemap at the domain root when
served from the default version; check the deployed result.

Search intent recommendations are hypotheses, not measured keyword-volume data.
Meta descriptions primarily help describe a page in search snippets; Google can
choose other text. Do not sell them as a direct ranking boost. Prioritize complete
answers, descriptive titles, contextual internal links, reliable examples, and
measurement over metadata busywork.

## Primary references consulted

```text
https://docs.readthedocs.com/platform/stable/guides/technical-docs-seo-guide.html
https://docs.readthedocs.com/platform/stable/reference/environment-variables.html
https://docs.readthedocs.com/platform/stable/reference/sitemaps.html
https://docs.readthedocs.com/platform/stable/config-file/v2.html
https://developers.google.com/search/docs/appearance/title-link
https://developers.google.com/search/docs/appearance/snippet
https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
https://developers.google.com/search/docs/fundamentals/creating-helpful-content
https://developers.google.com/search/docs/crawling-indexing/links-crawlable
https://developers.google.com/search/docs/appearance/ai-features
https://myst-parser.readthedocs.io/en/latest/configuration.html
```
