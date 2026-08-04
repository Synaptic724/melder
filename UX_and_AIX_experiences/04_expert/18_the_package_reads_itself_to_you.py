"""
TIER: expert (18)
GOAL: THE PACKAGE DOCUMENTS ITSELF, AND IT PAGES. Four system documents
      hang off the package root and answer AT IMPORT - before Aether
      boots, before a Spellbook exists, before anything is conjured.

        melder.__architecture__
        melder.__components__
        melder.__graph_network__
        melder.__graph_details__

      The class says why in its own System Context: these sit "entirely
      outside the runtime graph and BEFORE IT IN TIME... an agent
      orients itself on system structure before it has a Spellbook, a
      Conduit, or any live object world."

      So the expert tier ends where an agent begins.

      THE FULL-READ DOOR IS THE FAILURE MODE, AND MELDER SAYS SO
      `render_markdown()` returns the entire payload in one call. The
      `reader()` docstring calls that "the whole point of failure" for a
      populated document - not a warning bolted on afterwards, but the
      stated reason the paging API exists. Advanced 14 taught graded
      resolution as a CONTEXT BUDGET CONTROL on describe(); this is the
      same law at document scale, where the blast radius is megabytes.

      SIZE THE READ BEFORE YOU SPEND ANYTHING ON IT
        document.line_count / document.char_count
      "Let an agent size a read BEFORE committing any context to it."
      That is the cheapest possible call and it is the one to make first.

      THEN PICK A RUNG, CHEAPEST FIRST
        head(lines)          orientation - what does this cover?
        lines(start, count)  random access - I know where to look
        reader(...)          a resumable cursor - I need all of it,
                             in bounded bites

      `has_more` IS THE FIELD TO BRANCH ON, and the NamedTuple's own
      docs explain why you must not improvise a substitute:
      `end_line == total_lines` is NOT a reliable end test, because the
      final line can be partial. The library computes the answer in one
      place and hands it to you; deriving your own is how you get an
      off-by-one that only shows up on documents that do not end in a
      newline.

      PROGRESS ALWAYS BEATS THE BUDGET. A single line longer than the
      whole char budget is returned WHOLE rather than split. Otherwise a
      cursor could return an empty chunk forever and a well-written loop
      would hang on a pathological document - so the budget yields.

      TWO REFUSALS THAT LOOK INCONSISTENT AND ARE NOT
        reader(line_target=1)   raises  - a budget outside 2..100 is a
                                          CALLER ERROR
        lines(start, huge)      clamps  - reading past the end is a
                                          LEGITIMATE QUESTION
      Melder refuses a malformed request and answers a reasonable one at
      the edge. Same distinction expert 12 drew between a malformed
      REQUEST and disallowed CODE.

      AND IT COSTS NOTHING UNTIL YOU ASK
      The line index is built on FIRST BOUNDED READ, never at
      construction, and the `IndexedText` import sits INSIDE the method.
      Stated reason: `melder/__init__.py` imports all four documents at
      package scope, so anything done eagerly is paid by every `import
      melder` - including the majority of processes that never ask a
      document anything.

      The index is also built WITHOUT A LOCK, deliberately: two threads
      racing first access build equivalent indexes over the same
      immutable string, so the race is benign and a lock would add
      contention to a path that settles after one call. A documented
      benign race is a different thing from an overlooked one.
SURFACE EXERCISED: melder.__architecture__ / __components__ /
                   __graph_network__ / __graph_details__,
                   StaticSystemDocument line_count / char_count / head /
                   tail / lines / reader, and TextChunk.has_more
VERIFY: rides the owner's 3.14t run; asserts are the contract.
"""
import melder as md


DOCUMENT_NAMES = (
    "__architecture__", "__components__",
    "__graph_network__", "__graph_details__",
)


def main() -> None:
    # THESE ANSWER AT IMPORT. Nothing has been conjured; no Aether call
    # has been made by this lesson at all.
    documents = {name: getattr(md, name) for name in DOCUMENT_NAMES}
    for name, document in documents.items():
        assert document.document_name
        print(f"{name:<20} ->", type(document).__name__)
    print()
    print("four documents, queryable with no Spellbook and no Conduit")
    print("  they sit outside the runtime graph and BEFORE it in time")

    architecture = documents["__architecture__"]

    # 1. SIZE IT FIRST. The cheapest call in the API, and the one that
    #    decides whether any of the others are affordable.
    print()
    print("__architecture__ is", architecture.line_count, "lines /",
          architecture.char_count, "chars")
    print("  sizing a read before committing context to it is the whole")
    print("  reason these two properties exist")

    # 2. ORIENTATION. The top of the document, for the price of the top
    #    of the document.
    opening = architecture.head(10)
    assert opening.total_lines == architecture.line_count
    assert opening.start_line == 0
    print()
    print("head(10): lines", opening.start_line, "->", opening.end_line,
          " has_more =", opening.has_more,
          " truncated_by =", opening.truncated_by)

    # `has_more` IS THE END TEST. Not an end_line comparison - the last
    # line may be partial, and the library computes this in one place
    # precisely so callers do not each invent a slightly wrong version.
    if architecture.line_count > 10:
        assert opening.has_more is True

    # A tail reaches the end by definition, so has_more is always False.
    closing = architecture.tail(5)
    assert closing.has_more is False
    print("tail(5):  has_more =", closing.has_more,
          "  (a tail is at the end by definition)")

    # 3. RANDOM ACCESS when you already know where to look.
    middle = architecture.lines(2, 3)
    assert isinstance(middle, str)
    print()
    print("lines(2, 3) returned", len(middle), "chars of exact span")

    # ...and it CLAMPS rather than raising. Reading past the end is a
    # reasonable question with a reasonable answer.
    past_end = architecture.lines(architecture.line_count + 500, 10)
    assert past_end == "" or isinstance(past_end, str)
    print("lines(past the end) clamped instead of raising")

    # 4. THE CURSOR. Each caller gets its OWN, over a SHARED index - so
    #    many agents can page one document concurrently, unlocked.
    reader = architecture.reader(line_target=25, char_target=4096)
    chunks = 0
    consumed_lines = 0
    while True:
        chunk = reader.read()
        chunks += 1
        consumed_lines = chunk.end_line
        if not chunk.has_more:
            break
        if chunks > 10_000:
            raise AssertionError("cursor failed to make progress")
    assert reader.exhausted is True
    assert consumed_lines == architecture.line_count
    print()
    print("cursor consumed the document in", chunks, "bounded reads")
    print("  every read advanced - a line longer than the char budget is")
    print("  returned WHOLE, so progress always beats the budget")

    # Two cursors are independent; the indexed document behind them is
    # not copied.
    first = architecture.reader(line_target=10)
    second = architecture.reader(line_target=10)
    first.read()
    assert first.exhausted is False or architecture.line_count <= 10
    assert second.document is first.document, (
        "the index is SHARED; only the cursor is private"
    )
    print("two cursors, one shared index - private position, no copy")

    # 5. A BAD BUDGET IS A CALLER ERROR AND IS REFUSED. Note the contrast
    #    with the clamping above: melder answers an edge question and
    #    refuses a malformed one.
    for bad in (1, 101):
        try:
            architecture.reader(line_target=bad)
            raise AssertionError("expected ValueError on line_target")
        except ValueError:
            pass
    print()
    print("line_target outside 2..100 raises - a budget is not a")
    print("suggestion, and clamping it would hide the caller's mistake")

    # 6. THE RAW ENVELOPE IS STILL THERE for a caller that wants to parse
    #    structure rather than read prose - synthesised lazily, so nobody
    #    who never asks for it pays to build it.
    assert isinstance(architecture.render_json(), str)
    print()
    print("render_json() available, built on demand")
    print("render_markdown() returns EVERYTHING - the door that exists")
    print("  so the paging API has something to be better than")

    print()
    print("the package explains itself before it runs")
    print("size it, then page it; has_more is the end, not arithmetic")
    print("a bad budget refuses, a long read clamps - different mistakes")


if __name__ == "__main__":
    main()
