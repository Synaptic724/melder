# Architecture patch: Sphinx publication metadata and validation

## Scope and non-goals
- Patch ID: sphinx_seo_2026_09_26
- Scope: existing documentation generators, metadata and publication verification.
- No Melder runtime API/ownership changes, homepage redesign, route renames or new tutorials.

## Changed-components matrix
| Component | Delta | Canonical destination |
| --- | --- | --- |
| Documentation sources/renderers | Explicit descriptions and a local guide link | docs/maintaining.md |
| SEO publication validation | Local generated-HTML checks and pipeline integration | docs/maintaining.md |

## Interface and boundary deltas
- Optional nonempty chapter descriptions belong to README-derived chapters in curriculum.toml.
- Authored guide descriptions stay in their own MyST frontmatter.
- Optional lesson descriptions extend the value-only Lesson metadata and catalog overrides.
- A shared pure metadata formatter emits safe MyST frontmatter without changing body text.
- The new checker reads generated HTML/XML and writes only an optional report; it makes no network calls.
- The checker complements check_site and accepts explicit canonical/preview policy.

## Cross-component invariants
- One description owner and at most one emitted description tag per page.
- Missing optional metadata keeps existing output behavior; malformed supplied metadata fails early.
- Existing page IDs, homepage heading/banner, four levels, downloads and example bytes stay intact.
- Root README links remain useful on GitHub; known matching guide links become local in Sphinx.
- RTD-managed robots.txt remains authoritative; its current HTTP 200 behavior is recorded separately.

## Migration / rollout order
1. Verify build blockers are repaired.
2. Add metadata helper/data fields, selected descriptions and the one link rewrite with tests.
3. Render and inspect the real site.
4. Add the adapted checker and pipeline configuration with deliberate preview handling.
5. Promote the contracts into docs/maintaining.md and retain/archive this patch at owner acceptance.

## Rollback
Revert the affected docs source/tool/workflow changes together. Retain the independent API manifest
and archived-path repairs. No persisted runtime data or public URL migration exists.

## Validation expectations
Existing docs suite/model/build/site checks, rendered metadata escaping, generated local-link checks,
negative checker cases, and browser verification of representative pages.

## Ticket coverage map
- EPIC-2026-09-26-sphinx-publication-quality
- STORY-2026-09-26-refine-sphinx-discoverability
- TASK-2026-09-26-apply-sphinx-metadata-and-links
- TASK-2026-09-26-integrate-sphinx-seo-checks

## Unknowns
No Search Console/ranking claims. Remote publication and hosting setting changes remain owner actions.
