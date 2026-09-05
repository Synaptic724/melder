# Melder local documentation validation

- Recorded: 2026-09-05T09:39:40Z
- Owning task: TASK-2026-09-04-rtd-ci-and-offline
- Base revision: 15e06e7de1de68b1af150eabc7e978ead6155c76
- Branch: codex_features2
- Changes after that revision: fresh Sphinx environments, a real rebuild regression, maintainer
  guidance, prominent README links, and generated repository bundles. Owner handles commits/pushes.
- Tools: Python 3.14 documentation environment, Sphinx 9.1.0, Tectonic 0.17.0.

## Measured local outputs

| Check | Result | Evidence under rtd_validation_20260904/ |
| --- | --- | --- |
| Documentation tests | 36 passed | docs_tests_20260905.log |
| Rebuild regression with fresh environment | Passed | rebuild_regression_20260905.log |
| Same regression without fresh environment | Expected stale-backlink failure reproduced | rebuild_negative_20260905.log |
| Full HTML rendering | 294 declared pages | html_20260905.log |
| HTML links and source equality | 35,119 local links; zero errors | links_20260905.log |
| PDF | 103 pages, all four level bookmarks, no blank pages | pdf_metadata_20260905.json |
| ePub | 62 XHTML documents, 61 spine entries, 1,077 valid internal links | epub_check_20260905.json |
| HTML archive | Exact match for all 945 files, including assets/downloads | staging_20260905.json |
| RTD staging | All four formats match their local origins byte-for-byte | staging_20260905.json |
| Package source assets | All three exact checks pass | source_check_20260905.log |
| Repository LLM assets | src/tests tracked inputs pass; other bootstrap inputs pass | repo_check_20260905.log |
| README update | 294-page navigation model still validates; refreshed other corpus passes | readme_bundle_20260905.log |
| Existing CI workflow suite | 127 passed before this continuation; workflow source unchanged by this task | ci.xml |

The four levels retain Beginner, Intermediate, Advanced, and Expert, with 48 guide chapters and
all 133 saved lesson pages. Historical example execution is recorded in the individual curriculum
tasks; it was not repeated during this continuation because runtime/example code was not changed here.

## Layout and browser observations

All final PDF pages were reviewed in rendered contact sheets. Full-page inspection of pages 35, 48,
and 73 covered the three small vertical TeX overflow locations. No clipped text, overlaps, blank pages,
or missing-glyph boxes were observed. An independent text geometry pass found no characters outside
page bounds or within the outer 25/35-point margin limits. TeX warnings remain in the retained log.

The local preview responds at http://127.0.0.1:8765/. Browser checks confirmed the four-level navigation,
133-example catalog, Expert filter (36 results), empty filter result (0), clear-filter recovery (133),
and a completed Spellbook search with its API page as a leading result. The sidebar Examples route
works. The first attempt to click an off-screen homepage card timed out; this is not recorded as a
passed card interaction. Comprehensive mobile/zoom/focus and hosted-addon checks remain in S9.

## Reproduction and boundaries

Run the documented commands in docs/maintaining.md using the locked documentation environment.
Use the normal build command; it now rebuilds Sphinx's reference environment on every run.
The defect was cached viewcode module prefixes after changing facade imports to canonical origins.
No runtime exports or API contracts were changed to fix it.

Repository bundle checks used tracked inputs for src/tests. The other corpus used
`--corpus other --include-untracked` for this documentation bootstrap's new docs/.gitignore;
the Git index was not modified. Other agents' unfinished untracked tests were excluded. Their later
source/test changes require the usual corpus refresh before committing those inputs.

Raw local logs are retained through a scoped .gitignore exception. Final PDF/ePub/HTML files and PNG
review intermediates remain generated under docs/_build. Staged formats remain under _readthedocs.

The owner is adding the Read the Docs project. Hosted builds, Git integration, PR previews, versions,
canonical URLs, hosted search/downloads, and redirects are not verified. README uses its existing
public https://melder.readthedocs.io/en/latest/ address; no localhost link was added to the README.

## Later shared-checkout movement

At 2026-09-05T09:49:19Z, HEAD was f35b1517863a846b35b7411c27c60b3547fa9cba. It includes the README/docs
changes and newer ordered-disposal runtime work reported by codex_1. This report remains evidence for
the inputs tested above. The final hosted candidate requires a fresh docs/source-asset/bundle check after
the concurrent work settles; it is not qualified merely by this earlier green snapshot.
