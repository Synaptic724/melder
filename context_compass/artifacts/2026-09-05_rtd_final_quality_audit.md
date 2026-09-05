# Final documentation quality audit

- Task: TASK-2026-09-04-rtd-quality-audit
- Agent: codex_2
- Started: 2026-09-05T12:06:59Z
- Local preview: http://127.0.0.1:8765/
- Local implementation: complete and verified; hosted launch remains blocked.
- Final review: 2026-09-05T14:03:49Z
- Package: 0.2.3. Built source revision label: 0e8e66e48bd6c12a0b24a11580df92a01f3657dd.
- Final presentation/runbook changes and regenerated other corpus still require the owner's commit.
- Git comparison confirms runtime/lesson inputs did not change between tested 20123b8a and built 0e8e66e4.
- Temporary no-custom-JS preview server was stopped; the main 8765 preview remains available.

| Requirement | Evidence/status |
| --- | --- |
| Four exact levels, order, and indicators | Passed desktop/320px homepage and sidebar review: Beginner, Intermediate, Advanced, Expert |
| Homepage examples and Full Contents prominence | Passed desktop/320px homepage, direct mobile links, skip link and keyboard/card focus |
| Every declared page reachable | 294 declared pages, including 48 guide chapters; no missing/duplicate IDs or orphan contents routes |
| All 133 lessons and helper downloads | 41/37/19/36 lessons; all 137 lesson/helper files and four collection ZIPs match source bytes. 132 lessons passed normally; unchanged Expert 05 passed outside the sandbox after a temporary-file ACL failure |
| Complete public API dispositions | Every root export reconciled: 60 documented objects + eight values; eight additional returned surfaces, 76 total dispositions |
| Strict HTML, local links, images, source bytes | Final build and all 35,499 local links pass; no missing images/alt attributes or private input directories |
| Catalog filters, empty results, reset, deep links | Passed 41 Beginner, five combined disposal results, reload persistence, 0-result live status, keyboard reset to 133 |
| Search by API/task and no-result behavior | Passed SpellSpace result navigation, cleanup/request scope searches, and explicit no-match guidance |
| Mobile, keyboard/focus, zoom/reflow | Reflow passed 320/375/640/768/1024px; menu/skip/card/copy focus fixed. Native 200% zoom unavailable; do not equate reflow with a zoom test |
| No-custom-JavaScript browsing | Separate strict build omits navigation.js/catalog.js; Full Contents and all 133 visible lessons work at 320px |
| Text and control contrast | Article links 5.697:1; inline literals 5.939:1; filter border 3.725:1; sidebar focus 10.238:1 |
| Diagrams and long code | 17 SVGs loaded at 375px; full-size/download actions present; Tab/Right scrolls long code without page overflow |
| HTML/PDF/ePub output and source identity | HTML archive/staging matches all 948 files; 107-page PDF visually reviewed and long table identifiers fixed; ePub has 62 XHTML documents, valid links/mimetype, and no scripts. All four staging formats match local bytes |
| Maintainer add/update/recover workflow | docs/maintaining.md covers page/lesson/API updates, prerequisites, build/preview, source drift, version/redirect handling, and reviewed recovery of a published regression |
| Build checks and generated assets | 36 documentation tests pass; three package build assets and all three LLM corpora pass exact checks. Only other corpus was regenerated after the final runbook/config changes |
| Version and canonical plumbing | Separate local RTD-environment simulation confirms page-specific canonical URLs, version label, and 294 sitemap URLs; this is not hosted service evidence |
| Public RTD build/project/revision | Fresh browser reload still displays 404 at the advertised latest URL; actual project identity/access requested |
| Hosted versions/search/canonical/redirects/downloads | Pending actual hosted build and project access |

## Current evidence

Use artifacts/rtd_validation_20260904/release_qualification_20260905.json for the final format hashes
and staging/canonical results. release_links_20260905.log is the final HTML check; final_inventory_20260905.json
records every API disposition and lesson/helper fingerprint. final_examples_20260905.xml plus
final_protocol_retry_20260905.xml record all 133 successful lesson outcomes across the normal run and retry.
The earlier final_offline_20260905.json predates the PDF wrapping correction and is retained as history.
The owning tasks list every log and the durable PDF before/after images.

## Remaining release checks

- The actual RTD project, repository/branch, build commit, addons, versions, canonical/sitemap service
  behavior, redirects, PR previews, and hosted downloads need a real successful hosted build.
- Automatic approval review rejected the dashboard read for possible private project/account access.
  Owner authorization is pending. No alternate dashboard/API access was attempted.
- Native 200% browser zoom was unavailable through the in-app browser controls. Responsive reflow
  is verified separately and does not substitute for that manual check.
- The copy button becomes visible on keyboard focus and reports Copied on Enter. The browser's
  virtual clipboard returned no payload, so exact copied-byte readback remains unverified.
- Owner retains all commits, pushes, publication choices, and final acceptance. Other agents'
  runtime/CI changes retain their own qualification and ownership.
