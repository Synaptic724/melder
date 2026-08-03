# Task: Stop Windows checkouts from breaking the system-document integrity gate

## Metadata
- Task ID: TASK-2026-08-03-system-document-line-ending-gate
- Story: none (standalone repo-hygiene fix found while triaging a test run)
- Status: completed
- Owner: cowork
- Agent Name: bootstrap_0
- Priority: p2
- Created: 2026-08-03T04:10:00Z
- Updated: 2026-08-03T04:10:00Z

## Problem

Two unit tests were red:

- `test_shipped_entries_carry_sections_and_a_digest` - `assert shipped` on `[]`
- `test_unavailable_entry_matches_a_live_entry_key_for_key` - `StopIteration`,
  because `next(e for e in entries.values() if e["available"])` found nothing

Both had the same cause and neither error message pointed at it.

**EVERY system document was failing its own integrity gate.** Each
`<name>_index.md` records the `content_sha256` of `<name>.md`, and
`_builder.py:361-368` refuses to ingest a document whose bytes do not hash to
that value. All four were being refused, so `ingest()` reported nothing
available and the tests failed far from the cause.

The signature was distinctive and is worth remembering: **line counts matched
EXACTLY while every sha differed.** A content change moves both numbers. Only a
byte change that preserves line structure moves one - which means line endings.

Measured:

| document | index claims | working tree | CRLF present |
| --- | --- | --- | --- |
| `src_architecture.md` | `d252983338c5a644...` | `4495674d50d646ec...` | 2297 |
| `src_components.md` | `c7701f1174533ef2...` | `ed30da2700ecc7b0...` | 8370 |
| `src_graph.md` | `2943c887be9e7fcf...` | `a7cb8315049e5932...` | 25586 |

Re-hashing each file with CRLF normalised to LF reproduced the index's claimed
value EXACTLY, for all three. So the indexes were correct and the working tree
was wrong - not the other way round.

Confirmed at the git layer: the stored blobs contain zero CR bytes. Git holds
them LF; a Windows checkout with `core.autocrlf=true` converts on the way out.
The repo had NO `.gitattributes`, so nothing prevented it.

## Why this was not obvious

The failure surfaces as "no build-asset entries exist", which reads like a
builder bug or a missing document. Nothing in either error mentions hashing,
line endings, or the checkout. The gate is working exactly as designed - it
refused unverified bytes - but the refusal is silent at the point of failure and
only visible if you go and compare the hashes yourself.

## Fix

1. **`.gitattributes` added at the repo root.** `context_compass/system_docs/**/*.md`
   pinned `text eol=lf`, so the bytes on disk are the bytes that were hashed
   regardless of platform or `core.autocrlf`. The generated payload/manifest
   modules that embed those documents verbatim get the same rule for the same
   reason, and `*.py` is pinned LF so a cross-platform diff never becomes a
   whole-file rewrite.
2. **Working tree renormalised.** `.gitattributes` governs FUTURE checkouts, not
   files already on disk, so the 11 CRLF files under `system_docs/` were
   converted to LF in place. Without this step the fix would appear to do
   nothing until someone re-cloned.

## Validation

Gate re-checked per document after the fix - all five doc/index pairs PASS on
both line count and `content_sha256`, zero CRLF remaining:

    src_architecture     PASS   lines=2298   crlf=False
    src_components       PASS   lines=8370   crlf=False
    src_graph            PASS   lines=25586  crlf=False
    tests_architecture   PASS   lines=710    crlf=False
    tests_components     PASS   lines=1579   crlf=False

Then the builder itself was driven directly rather than inferred:

    ingest() -> available: ['__architecture__', '__components__',
                            '__graph_network__', '__graph_details__']
                unavailable: none

Both failing tests assert exactly that condition, so both should now pass.

NOT RUN BY ME: pytest. The 3.10 sandbox cannot import the package. The builder
was executed directly by path, which is what produced the `ingest()` output
above - that IS real execution of the code under test, but it is not the suite.

## Notes

- A CONTRIBUTOR ON A WINDOWS CHECKOUT WILL HIT THIS AGAIN the moment they add a
  new hashed document without a matching `.gitattributes` rule. The rule is a
  glob over `system_docs/**/*.md` rather than a file list, so new documents in
  that tree are covered automatically.
- An existing clone may still hold CRLF for files outside `system_docs/`. The
  one-time renormalisation for the whole repo is `git add --renormalize .`,
  which is recorded in the `.gitattributes` header rather than run here - it
  restages every file in the repo and that is an owner-scale decision, not a
  side effect of a test triage.
- FOUND WHILE TRIAGING, NOT WHILE LOOKING FOR IT. The same run carried 11 other
  failures which are NOT this and NOT mine: they trace to the process-wide
  spell_id regime (owner ruling 2026-08-02, `aether.py:1826-1840`), which makes
  the same class bound in two frames collide and `inspect_spell` answer at
  process scope. Those tests assert the older frame-scoped semantics.
  `STORY-2026-08-02-aether-unified-spell-id-set` is the open lane for it, and
  `test_component_concurrent_conjures_across_frames_admit_at_most_one`
  documents itself as a known red in its own docstring.
