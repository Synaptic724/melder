# system_doc_index_usage

## Purpose

Define how to CONSUME a line-range index over a large system document: prove it is
current, resolve the sections you need, and read only those lines.

## When To Use

Whenever you need something from an indexed system document and do not need the whole
document. That is the normal case, not the exception.

Skip the index and read the document in full only when:

- you are onboarding and the document is a required baseline read, or
- you need a global property of the document (for example, auditing every cited path).

## The Read Order

1. Read the index. It is small; this is the cheap step.
2. **Verify it** (next section). Non-negotiable.
3. Select sections by `path` or `title`.
4. Slice those line ranges out of the document.
5. Read the slices.

Never skip to step 4. A range from an unverified index is not a shortcut, it is a guess
wearing a line number.

## VERIFY BEFORE YOU SLICE

An index is a claim about a document as it was at generation time. Documents move. If
the document changed, every range below the change is wrong, and the index will still
hand you plausible-looking numbers.

Before trusting any range, confirm all four:

| check | index field | how to verify |
|---|---|---|
| schema is known | `index_version` | MAJOR matches a version you support |
| document identity | `document` | resolves to the file you intend to read |
| length unchanged | `line_count` | recount the document's lines |
| bytes unchanged | `content_sha256` | rehash the document's exact bytes |

Also read `line_ending` and split the document on THAT terminator. Splitting CRLF content
on `\n` leaves stray `\r` and shifts nothing, but splitting LF content while expecting
CRLF collapses the file to one line and every range becomes meaningless.

**On any mismatch: STOP.** Do not slice. Do not "adjust" a range by eyeballing an offset.
Either regenerate the index (`system_doc_index_generation.md`) or read the document
directly and say which you did. Silently proceeding on a stale index is the one failure
this whole contract exists to prevent.

```python
import hashlib, json, pathlib

doc = pathlib.Path("context_compass/system_docs/src_components.md")
idx = json.loads(doc.with_name(doc.stem + "_index.json").read_text(encoding="utf-8"))

assert idx["index_version"].split(".")[0] == "1", "unsupported index schema"

raw_bytes = doc.read_bytes()
nl = "\r\n" if idx["line_ending"] == "crlf" else "\n"
lines = raw_bytes.decode("utf-8").split(nl)
if lines and lines[-1] == "":
    lines.pop()

stale = []
if len(lines) != idx["line_count"]:
    stale.append(f"line_count {idx['line_count']} -> {len(lines)}")
if hashlib.sha256(raw_bytes).hexdigest() != idx["content_sha256"]:
    stale.append("content_sha256 mismatch")
if stale:
    raise SystemExit("INDEX STALE, refusing to slice: " + "; ".join(stale))
```

## Selecting Sections

Each section carries exactly four fields: `level`, `path`, `start`, `end`. Two things you
might expect are absent on purpose and you derive them:

- title  -> `path.split(" > ")[-1]`
- length -> `end - start + 1`

Select on `path`, not on line numbers. The breadcrumb is stable across regenerations in a
way that line numbers are not.

- Working a subsystem: match `path` against the subsystem name.
- Answering one specific question: match the narrowest path segment that covers it.
- Needing a whole catalog: take the parent `level`-2 section rather than stitching its
  children together.

Prefer the NARROWEST section that answers the question. Taking a parent because it is
easier to name defeats the purpose - a `level`-2 catalog can be 1,900 lines.

**NORMALISE BEFORE MATCHING.** Headings use prose and CamelCase; you will search with
identifiers. A raw case-insensitive substring test for `mutation_research` returns ZERO
hits against a heading that says `MutationResearch`. Fold case AND strip separators on
both sides:

```python
norm = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())
hits = [s for s in idx["sections"] if norm("mutation_research") in norm(s["path"])]
```

**IGNORE ONE- AND TWO-LINE SECTIONS.** They are almost never real. They appear where a
document has a heading WRAPPED across consecutive heading lines, like:

```text
## Crystallizer Persistence & Restore (promoted from patch
## restore_engine_2026_07_07 + successor lanes, 2026-07-07)
```

The generator faithfully emits each line as its own section, so the first is 1 line long
and sorts FIRST under "narrowest wins" - handing you a heading fragment and nothing else.
Both current target documents contain these (4 in `src_architecture.md`, 8 in
`src_components.md`).

Filter them, and treat a hit of `<= 2` lines as a REPORTABLE DOCUMENT DEFECT rather than
a section: the fix belongs in the document's heading, not in your selection logic.

```python
span = lambda s: s["end"] - s["start"] + 1
real = [s for s in hits if span(s) > 2]
if len(real) < len(hits):
    print(f"NOTE: {len(hits) - len(real)} wrapped-heading fragment(s) skipped; "
          f"document headings need repair")
```

Putting both rules together:

```python
span = lambda s: s["end"] - s["start"] + 1
norm = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())

want = "crystallizer"
hits = [s for s in idx["sections"]
        if norm(want) in norm(s["path"]) and span(s) > 2]
hits.sort(key=span)                          # narrowest real section first
for s in hits[:5]:
    print(f"{span(s):5} lines  {s['start']}-{s['end']}  {s['path'].split(' > ')[-1]}")
```

## Slicing And Chunking

Slice with `lines[start-1:end]` - the index is 1-based and inclusive on both ends.

`codex.read_loc_max` (500) still applies to what you actually read. A section larger than
that is chunked WITHIN its own range, sequentially:

```python
LOC_MAX = 500
s = hits[0]
body = lines[s["start"] - 1 : s["end"]]
for off in range(0, len(body), LOC_MAX):
    chunk = body[off : off + LOC_MAX]
    lo = s["start"] + off
    print(f"--- {s['path']}  lines {lo}-{lo + len(chunk) - 1}")
    print(nl.join(chunk))
```

The index does not exempt you from chunking. It tells you WHICH 500 lines are worth
chunking through, instead of all 5,176.

## Citing What You Read

Cite the real line range you consumed, in the repository's existing convention:
`path:start_line-end_line`. Ranges taken from an index are as citable as ranges found by
reading - but cite the range you actually READ, not the section's full extent if you only
consumed part of it.

## Rules

- Verify before slicing. Always. Cheap check, expensive failure.
- Select by `path`; never hardcode a line number into a ticket, note, or another document.
  Line numbers are generation-time facts and go stale on the next edit.
- Prefer the narrowest sufficient section.
- Chunk within a range at `codex.read_loc_max`.
- If the index lacks a section you need, that is a signal the DOCUMENT lacks a heading
  there. Fix the document's structure rather than reading around the gap.
- After editing an indexed document, its index is stale by definition. Regenerate it in
  the same pass, or say plainly that you did not.

## Conflict Handling

If a sliced section contradicts source code, source wins - the same precedence
`graph_details_usage.md` applies to a stale graph. Treat the document as stale, and do
not promote a doc claim to fact on the strength of having read it from an index.

If a sliced section contradicts ANOTHER section of the same document, you have found a
self-contradiction rather than drift. Record it; do not silently pick one. Path- and
symbol-resolution checks cannot detect this class of defect, so a human or a targeted
read is the only thing that will.

## Anti-Patterns

- Slicing on an unverified index.
- Nudging a range by a few lines because the slice "looks close".
- Reading a `level`-2 parent when a `level`-3 child answers the question.
- Copying an index line number into durable prose.
- Editing an indexed document and leaving its index stale without saying so.
- Treating an index hit as evidence: the citation is the document, never the index.

## References

- `system_doc_index_generation.md` - the schema, and how to regenerate when stale.
- `agent_onboarding/default/general/skills/context_window_budget.md` - bounded discovery,
  which this skill is the practical mechanism for.
- `agent_onboarding/default/engineer/skills/graph_details_usage.md` - the
  read-in-bounded-chunks and source-wins precedents.
