# Component patch: SEO publication validation

## Purpose / boundary
Add a local generated-HTML/XML audit alongside the existing site checker. It neither crawls the web
nor predicts Google indexing/ranking. RTD-managed robots is verified/documented outside local HTML.

## Before / after
- Before: CI checks navigation/source fidelity but no title/description/canonical contracts.
- After: reviewed SEO requirements fail explicitly; uncovered descriptions remain warnings.

## Interfaces
- CLI takes HTML directory, canonical base URL, required-description globs, optional report path,
  and an explicit allowance for intentionally noindexed previews.
- Report includes deterministic page/issue records and counts.
- An optional schema-versioned TOML policy supplies shared required-description globs to both
  publication pipelines. Additional CLI globs extend that list; malformed policy is an input error.
- Exit 0 means no policy errors, 1 means policy errors, and 2 means inputs/audit could not be read.

## State / lifecycle
Each run owns only parsed values. File handles close immediately; no global registry or network I/O.

## Failure deltas
- Error: absent/duplicate/empty titles, duplicate descriptions, missing required description,
  missing/wrong canonical, malformed or absent expected sitemap, missing sitemap destinations,
  unintended noindex and unmatched required globs.
- Warning: optional absent/repeated description and editorial H1/language issues.
- Exclude Sphinx utility/source/download pages from content requirements.
- Never read a resolved HTML/sitemap destination that escapes the output root.

## Dependency / ordering
Metadata must exist before descriptions become required. CI sets an explicit canonical test base;
RTD uses its platform-provided base. External previews may retain intentional noindex.

## Validation
Synthetic positive/negative cases plus a real full build, canonical/sitemap/metadata verification,
and unchanged existing link/source checks. Document commands and preview behavior in maintaining.md.

## Open decisions
Google-selected canonicals and ranking remain outside the checker's claim boundary.
