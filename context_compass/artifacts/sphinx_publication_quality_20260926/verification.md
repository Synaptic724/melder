# Sphinx publication changes: verification

## Source changes

- Public API selection now includes UnresolvedInputError.
- Twenty archived graph descriptors are flat, collision-safe filenames, with an original-path
  and SHA256 mapping. Their bytes and retired_edges.json are preserved.
- Browser titles use the short Melder suffix; the visible homepage remains the existing page.
- Nine selected pages have descriptions through their existing authored or generated source owners.
- The cleanup guide's configuration link stays in Sphinx; canonical README text is retained.
- The late-binding runnable example has a distinct title from its guide and retains the published
  late-binding-with-spellcontract fragment through an explicit legacy anchor.
- Local SEO checks, a shared description policy, and CI/RTD invocation are implemented.
- Version and release details are 0.2.77. Final asset regeneration is the last build step.

## Checks actually completed

| Check | Result |
| --- | --- |
| Docs model validation | 301 pages, 54 assets; pass |
| Documentation unittest suite | 60 tests; pass |
| GitHub workflow contract tests | 29 tests; pass |
| Full Sphinx HTML build with warnings treated as errors | 301 pages; pass |
| Site link/anchor/source-fidelity check | 36,609 local links; pass |
| SEO audit | 301 content pages; 0 errors |
| Required descriptions | 9 of 9 present |
| Optional metadata warnings | 292 pages have no description yet; no other warning class |
| Windows Git checkout with core.longpaths=false | 20 relocated descriptors; all bytes match |
| Main Git index preservation during checkout probe | Unchanged |
| ePub handbook | 61 source pages; pass |
| PDF handbook | Compiler exit 0; PDF produced with TeX box/fontconfig warnings |
| HTML archive | Built from final HTML |
| Live robots.txt and sitemap | HTTP 200; see crawler_verification.md |

## Browser verification

- Opened the rebuilt homepage at localhost:8765, inspected its screenshot and DOM.
- Title is A runtime you can build on — Melder; heading, banner, guide cards, levels and walkthroughs
  remain visible in the existing layout; the new description is in head metadata.
- Clicked the cleanup page's configuration link; it opens the local configuration chapter.
- Opened the new public UnresolvedInputError reference and read the rendered contract/methods.
- Stopped the temporary localhost server after verification.

## Evidence and limits

- windows-checkout-result.json records the actual Git probe; retired_descriptor_relocation.json
  maps original names and content hashes.
- The current generated reports are docs/_build/site-check.json and docs/_build/seo-report.json.
- No coverage percentage, remote CI success, deployment, or Google ranking result is claimed.
- The entire runtime test suite was not rerun for documentation and archived-path changes.
- PDF compilation succeeded but this task does not claim a new visual-quality audit of every PDF page.
- Final source-asset regeneration ran after release edits: 460 agent-documentation entries,
  619 bind-guard entries, and four system documents at 0.2.77; all freshness checks pass.
- Final LLM regeneration: src 576 files, tests 1,018 files, other 370 files; all fingerprints and
  output/index proofs pass.
- Only ContextCompass work-state/evidence updates followed those final builds; its direct content
  is excluded from the LLM corpora and is not a packaged system-document input.

- The final anchor compatibility fix passed the full HTML/site/SEO checks; the HTML archive was
  refreshed, then source assets and LLM bundles were rebuilt last again. All freshness checks pass.

## Owner-requested turn-in, then rebuild

- Turned in the epic, both stories, three implementation tasks and the starter review at
  2026-09-27T00:30:31Z. All seven tickets are done in their matching completed folders.
- Archived all four promoted SEO patch contracts; attention and artifact boards are synchronized.
- Started the source-asset runner at 00:31:56Z, after closure. It rewrote all three manifests at
  0.2.77: 460 agent-documentation entries, 619 bind-guard entries and four system documents.
- Reran the LLM builder at 00:32:06Z. The src, tests and other bundles already matched their inputs
  and output proofs, so the builder correctly left their bytes unchanged.
- Both freshness checks passed at 00:32:22Z. All four commands exited 0.
- Logs: post_turn_in_assets.log, post_turn_in_llm.log and post_turn_in_asset_checks.log in this folder.
- Only ContextCompass closure/evidence records were updated afterwards. The LLM classifier excludes
  direct ContextCompass paths in llm_support/_builder.py:90-91.

## Requested rebuild after CI reported stale other corpus

- Completed: 2026-09-27T00:38:43Z
- Ran .venv_new/Scripts/python.exe llm_support/_builder.py.
- Rebuilt the other corpus from 375 files and refreshed manifest.json.
- Src and tests fingerprints and output proofs already matched.
- Ran .venv_new/Scripts/python.exe llm_support/_builder.py --check; all three corpora passed.
- Both commands exited 0.
