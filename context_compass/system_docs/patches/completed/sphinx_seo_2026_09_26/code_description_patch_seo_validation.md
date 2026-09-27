# Code-description patch: SEO validation flow

## Trigger
A new publication check has multiple input/error branches and must distinguish policy failures
from an unreadable audit. Its behavior needs an explicit contract before CI integration.

## Control flow
1. Validate root directory and absolute HTTP(S) canonical base with no query/fragment.
2. Parse the expected page-level sitemap; report duplicates, out-of-base URLs and absent destinations.
3. Iterate content HTML in deterministic path order; skip utility/source/download pages.
4. Reject output-escaping symlinks before reading; parse head metadata and visible heading counts.
5. Check one title/canonical, description ownership/requiredness, and intentional indexing mode.
6. Compare each content page/canonical to the sitemap and collect title/description duplicate groups.
7. Refuse empty audits and unmatched required-description globs.
8. Optionally write JSON and return the documented exit code; never mutate generated pages.

## Edge/error behavior
- Parsing or I/O failures produce exit 2 with actionable context.
- Validly read but invalid publication data produces exit 1 with per-page evidence.
- Optional missing descriptions and editorial conventions warn without failing the build.
- Noindex is accepted only in the explicitly chosen preview mode.
- A local absence of robots.txt is not failure: RTD serves its own root crawler file.

## Invariants / idempotency
Identical HTML/base/options yield identical issue ordering and counts. No source mutation,
subprocess execution, crawler request, or shared state occurs in the audit.

## Non-goals
No accessibility certification, security sandboxing, HTTP header checks, live redirect crawling,
ranking score, arbitrary word limits or automated rewrite of page content.

## Validation focus
Real HTML title/description parsing, escaped content, strict input boundaries, missing sitemap,
wrong destinations, required globs, duplicate titles, preview noindex and CLI exit/report behavior.
