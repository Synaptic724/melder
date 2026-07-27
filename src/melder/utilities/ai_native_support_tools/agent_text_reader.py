"""
Bounded, resumable text reader for agent consumption of large documents.

WHY THIS EXISTS
---------------
Melder's agent-facing surfaces are large. The packaged system documents run to
~1.9 MB across four objects, `src_components.md` alone is 282 KB, and a source
file an agent wants to reason about can be several thousand lines. A reader that
returns "the document" is therefore a footgun: one call blows an agent's entire
context window, and the agent has no way to ask for less.

This module gives an agent the opposite deal - it names a budget, gets exactly
that much, and is told whether more exists. Reading a 5,000-line document in
50-line steps is 100 calls that each cost what the agent asked for, instead of
one call that costs everything.

TWO OBJECTS, DELIBERATELY SPLIT
-------------------------------
    IndexedText     SHARED, immutable, built once per document.
                    Holds the text plus a line-offset index.

    AgentTextReader PRIVATE to one agent. Holds a reference to an `IndexedText`
                    and its own cursor. Cheap to construct; construct one per
                    agent, per read session.

The split is what makes concurrent use safe AND affordable. Ten agents reading
one 750 KB document share ONE copy of it - each holds a reference plus two
integers. Give every agent its own copy instead and that is 7.5 MB. Give them a
shared cursor instead and every read races.

Because the shared half is immutable and the private half is unshared, there is
NO LOCK anywhere in this module. That is not an oversight - it is the reason the
types are shaped this way, and it matters on free-threaded 3.14t where a lock on
a hot read path is contention every agent pays.

WHY AN OFFSET ARRAY AND NOT `splitlines()`
------------------------------------------
`splitlines()` on a 4,263-line document leaves a list of 4,263 `str` objects
resident for the life of the process - and four packaged documents would leave
~17,000. Every one of those is GC-TRACKED. `CachingSystem` already documents
what that costs here: "the free-threaded GC scans the full tracked heap per
collection", measured at ~13% warm wall regression when a decoded bundle was
retained for the process lifetime.

An `array("q")` of line offsets is a single GC-untracked buffer. Lines are
sliced out of the original string on demand and are garbage as soon as the agent
is done with them. Measured on `readable_src_graph.json` (758 KB, 4,263 lines):

    splitlines()    0.5 ms build,  0.97 MB resident,  4,263 tracked objects
    offset index    0.7 ms build,  0.75 MB resident,  2 objects

0.2 ms slower to build, permanently cheaper to keep.

BUDGETS: LINES *AND* CHARACTERS
-------------------------------
Line count alone is a poor budget. In melder's own documents line width varies
by more than 30x - `src_architecture.md` averages 56 characters per line but
peaks at 579. "Give me 100 lines" can therefore mean 5,600 characters or 57,900,
and an agent budgeting context cannot tell which it is about to get.

Every read is bounded by BOTH limits and stops at whichever binds first. An
agent that only cares about one may set the other wide.
"""
import array
import bisect
from typing import Iterator, List, NamedTuple, Optional


class ReaderPolicy:
    """
    Static namespace for the reader's fixed bounds and defaults.

    Contract:
        Class-level constants rather than module globals, per the repo's module
        scope rule. Nothing here is mutated at runtime.

    Attributes:
        MIN_LINE_TARGET: Smallest accepted line budget. Below two lines a reader
            cannot make useful progress and an agent looping on it would spend
            more calls than content.
        MAX_LINE_TARGET: Largest accepted line budget. The cap is the point: an
            unbounded target turns this back into "return the document", which
            is the failure mode the type exists to prevent. An agent needing
            more calls again - that is the design, not a limitation.
        DEFAULT_LINE_TARGET: Used when a caller names no line budget.
        MIN_CHAR_TARGET: Smallest accepted character budget. Must comfortably
            exceed one long line or a read could return nothing but a partial
            line forever.
        MAX_CHAR_TARGET: Largest accepted character budget.
        DEFAULT_CHAR_TARGET: Used when a caller names no character budget.
            Chosen to pair with `DEFAULT_LINE_TARGET` at melder's own average
            line width without truncating typical reads.
        OFFSET_TYPE_CODE: `array` type code for the line index. Signed 64-bit
            so document size is never a correctness question; the index costs
            8 bytes per line, which is 34 KB on a 4,263-line document.
        NEWLINE: The line separator offsets are computed against.
    """

    MIN_LINE_TARGET: int = 2
    MAX_LINE_TARGET: int = 100
    DEFAULT_LINE_TARGET: int = 50

    MIN_CHAR_TARGET: int = 256
    MAX_CHAR_TARGET: int = 65_536
    DEFAULT_CHAR_TARGET: int = 8_192

    OFFSET_TYPE_CODE: str = "q"
    NEWLINE: str = "\n"


class TextChunk(NamedTuple):
    """
    One bounded read result, plus everything needed to decide what to do next.

    Purpose:
        Tell an agent what it got, where it came from, and whether asking again
        will produce anything - without the agent tracking any of that itself.

    Contract:
        Immutable. A `NamedTuple` rather than a `__slots__` class because this
        is a terminal value with no behaviour and no lifecycle: agents compare
        it, unpack it, and discard it, and tuple semantics give all three for
        free.

        `has_more` is the field to branch on. `end_line == total_lines` is NOT
        equivalent - a character-bounded read can stop partway through the final
        line, and `has_more` accounts for that where the line span cannot.

    Attributes:
        text: The content read.
        start_line: Zero-based line the chunk begins on, inclusive.
        end_line: Zero-based line after the last one touched, exclusive.
        start_char: Absolute character offset the chunk begins at, inclusive.
        end_char: Absolute character offset the chunk ends at, exclusive.
        total_lines: Line count of the whole document, for progress reporting.
        total_chars: Character count of the whole document.
        has_more: True when content remains after this chunk.
        truncated_by: Which budget stopped this read - `"lines"`, `"chars"`, or
            `"end"` when the document simply ran out. Lets an agent widen the
            budget that actually bound rather than guessing.
    """

    text: str
    start_line: int
    end_line: int
    start_char: int
    end_char: int
    total_lines: int
    total_chars: int
    has_more: bool
    truncated_by: str


class IndexedText:
    """
    An immutable document plus its line-offset index, shared across readers.

    Purpose:
        Pay the indexing cost ONCE per document and let any number of agents
        read from it concurrently without copying it or locking it.

    Contract:
        - Immutable after construction. Every method is a pure read.
        - Holds the original string unmodified; lines are sliced on demand and
          never retained.
        - The offset array stores the start offset of every line plus a final
          sentinel at the text length, so line `i` spans
          `offsets[i] .. offsets[i + 1]` with no special case for the last line.
        - An empty document has one line of length zero, matching how an empty
          file reads.

    Threading / Concurrency:
        Safe to share across threads with NO synchronization, on free-threaded
        builds included. Nothing here mutates after `__init__` returns, and no
        method writes to `self`. This is the reason the mutable cursor lives in
        `AgentTextReader` instead.

    Lifecycle / Cleanup:
        Plain value object with no cleanup contract. Deliberately NOT
        `Cleanable`: there is nothing to release, and a teardown contract would
        imply these are owned by the runtime graph, which they are not.

    Registration:
        MELDER KERNEL - guarded. Construct one directly; it takes no runtime
        collaborators and asking melder to inject one is a category error.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Immutable indexed document shared by many readers. Query
        line_count/char_count to size a read, head(n)/tail(n) to orient cheaply
        before committing context, line_text/lines_text for direct random
        access, or call reader(...) to get your own resumable cursor. Construct
        one per document and share it; construct a reader per agent.
    """

    __slots__ = ["_text", "_offsets"]

    def __init__(self, text: str) -> None:
        """
        Index one document for bounded reading.

        Args:
            text: The full document text.

        Returns:
            None

        Raises:
            TypeError: If `text` is not a `str`. Checked explicitly because
                passing `bytes` here would otherwise index byte offsets and
                produce silently wrong line spans much later.
        """
        if not isinstance(text, str):
            raise TypeError(f"text must be str, got {type(text).__name__}")
        self._text: str = text
        self._offsets: array.array = self._build_offsets(text)

    @staticmethod
    def _build_offsets(text: str) -> array.array:
        """
        Build the line-start offset index for one document.

        Contract:
            Returns starts for every line plus a trailing sentinel equal to
            `len(text)`, so `offsets[i + 1]` is always valid for any real line
            `i`. A trailing newline does NOT create a phantom final line, which
            matches how editors and `splitlines()` both count.

        Args:
            text: The full document text.

        Returns:
            array.array: Line start offsets, ascending, with an end sentinel.
        """
        offsets = array.array(ReaderPolicy.OFFSET_TYPE_CODE, [0])
        position = text.find(ReaderPolicy.NEWLINE)
        while position >= 0:
            offsets.append(position + 1)
            position = text.find(ReaderPolicy.NEWLINE, position + 1)
        length = len(text)
        # A trailing newline leaves the last recorded start AT the end of the
        # text. That start is the sentinel, not a line - dropping it here is
        # what keeps "a\nb\n" at two lines rather than three.
        if len(offsets) > 1 and offsets[-1] == length:
            return offsets
        offsets.append(length)
        return offsets

    @property
    def line_count(self) -> int:
        """
        Return the number of lines in the document.

        Returns:
            int: Total line count; always at least one.
        """
        return len(self._offsets) - 1

    @property
    def char_count(self) -> int:
        """
        Return the number of characters in the document.

        Returns:
            int: Total character count.
        """
        return len(self._text)

    @property
    def text(self) -> str:
        """
        Return the whole document.

        Contract:
            The ESCAPE HATCH, and deliberately a property rather than a read
            method so it never looks like a budgeted call. On a packaged system
            document this returns hundreds of kilobytes in one go - which is
            exactly what `AgentTextReader` exists to avoid. Prefer a reader
            unless the whole document is genuinely required.

        Returns:
            str: The complete document text.
        """
        return self._text

    def line_start(self, line: int) -> int:
        """
        Return the absolute character offset one line begins at.

        Args:
            line: Zero-based line number, `0 <= line <= line_count`.

        Returns:
            int: Character offset of that line's first character. Passing
                `line_count` returns the document length, which is what makes
                end-exclusive spans work without a special case.

        Raises:
            IndexError: If `line` is outside the document.
        """
        if line < 0 or line > self.line_count:
            raise IndexError(
                f"line {line} out of range for a {self.line_count}-line document"
            )
        return int(self._offsets[line])

    def line_of_offset(self, offset: int) -> int:
        """
        Return the line number containing one character offset.

        Contract:
            Binary search over the offset index - O(log n), no scan. Used to
            keep a chunk's reported line span accurate after a character-bounded
            read has left the cursor mid-line.

        Args:
            offset: Absolute character offset.

        Returns:
            int: Zero-based line containing `offset`, clamped to the document.
        """
        if offset <= 0:
            return 0
        if offset >= self.char_count:
            return max(self.line_count - 1, 0)
        return bisect.bisect_right(self._offsets, offset) - 1

    def line_text(self, line: int) -> str:
        """
        Return one line, including its trailing newline when it has one.

        Args:
            line: Zero-based line number.

        Returns:
            str: That line's text.

        Raises:
            IndexError: If `line` is outside the document.
        """
        if line < 0 or line >= self.line_count:
            raise IndexError(
                f"line {line} out of range for a {self.line_count}-line document"
            )
        return self._text[self._offsets[line]:self._offsets[line + 1]]

    def lines_text(self, start: int, count: int) -> str:
        """
        Return a contiguous run of lines as one string.

        Purpose:
            Direct random access for an agent that already knows where it wants
            to look and does not need a resumable cursor.

        Contract:
            Clamps to the document rather than raising on overrun, so
            `lines_text(4000, 100)` on a 4,263-line document returns the last
            263 lines instead of failing. Reading past the end is a normal
            outcome of paging, not an error.

        Args:
            start: Zero-based first line, inclusive.
            count: How many lines to return.

        Returns:
            str: The requested lines, or `""` when `start` is past the end.

        Raises:
            ValueError: If `start` is negative or `count` is not positive.
        """
        if start < 0:
            raise ValueError(f"start must be >= 0, got {start}")
        if count <= 0:
            raise ValueError(f"count must be > 0, got {count}")
        if start >= self.line_count:
            return ""
        stop = min(start + count, self.line_count)
        return self._text[self._offsets[start]:self._offsets[stop]]

    def split_lines(self, start: int = 0, count: Optional[int] = None) -> List[str]:
        """
        Return a run of lines as a list, newlines stripped.

        Contract:
            Materializes real `str` objects, so the GC-tracking cost this class
            avoids for the DOCUMENT applies to whatever slice is requested. That
            is fine for a bounded run an agent is about to process and discard;
            it is not fine for a whole large document, which is why `count`
            defaults to a bounded read rather than everything.

        Args:
            start: Zero-based first line, inclusive.
            count: How many lines; defaults to `ReaderPolicy.MAX_LINE_TARGET`.

        Returns:
            List[str]: The requested lines without trailing newlines.
        """
        span = ReaderPolicy.MAX_LINE_TARGET if count is None else count
        return self.lines_text(start, span).splitlines()

    def _chunk_for_span(self, start: int, end: int, truncated_by: str) -> TextChunk:
        """
        Build a `TextChunk` describing one absolute character span.

        Contract:
            Shared by every span-producing call so the reported line numbers,
            offsets and `has_more` flag are computed in exactly one place. A
            second implementation of this arithmetic is how `head` and `read`
            would drift into disagreeing about the same document.

        Args:
            start: Absolute start offset, inclusive.
            end: Absolute end offset, exclusive.
            truncated_by: Which budget bound the span.

        Returns:
            TextChunk: The described span.
        """
        total_lines = self.line_count
        total_chars = self.char_count
        if start >= end:
            line = self.line_of_offset(start)
            return TextChunk(
                text="",
                start_line=line,
                end_line=line,
                start_char=start,
                end_char=start,
                total_lines=total_lines,
                total_chars=total_chars,
                has_more=start < total_chars,
                truncated_by=truncated_by,
            )
        return TextChunk(
            text=self._text[start:end],
            start_line=self.line_of_offset(start),
            end_line=self.line_of_offset(end - 1) + 1,
            start_char=start,
            end_char=end,
            total_lines=total_lines,
            total_chars=total_chars,
            has_more=end < total_chars,
            truncated_by=truncated_by,
        )

    def head(
            self,
            lines: int = ReaderPolicy.DEFAULT_LINE_TARGET,
            *,
            chars: Optional[int] = None,
    ) -> TextChunk:
        """
        Return the FIRST lines of the document.

        Purpose:
            The cheapest possible orientation. An agent handed an unfamiliar
            document reads the head to learn what it is before deciding whether
            to spend context on the rest - which for a 282 KB file is the
            difference between 3 KB and everything.

        Contract:
            Stateless and cursor-free. Bounded by the same policy limits as a
            budgeted read, deliberately: an unbounded `head` on a single-line
            750 KB document would return the whole file, which is the failure
            this type exists to prevent.

            `chars` trims from the END of the head, keeping the beginning.

        Args:
            lines: How many leading lines, within `ReaderPolicy` bounds.
            chars: Optional character cap, within `ReaderPolicy` bounds.

        Returns:
            TextChunk: The leading span, with `has_more` set when the document
                continues past it.

        Raises:
            ValueError: If either budget is outside its documented bounds.
        """
        span = AgentTextReader._validated_line_target(lines)
        stop_line = min(span, self.line_count)
        end = self.line_start(stop_line)
        truncated_by = "lines" if stop_line < self.line_count else "end"
        if chars is not None:
            cap = AgentTextReader._validated_char_target(chars)
            if end > cap:
                end = cap
                truncated_by = "chars"
        return self._chunk_for_span(0, end, truncated_by)

    def tail(
            self,
            lines: int = ReaderPolicy.DEFAULT_LINE_TARGET,
            *,
            chars: Optional[int] = None,
    ) -> TextChunk:
        """
        Return the LAST lines of the document.

        Purpose:
            The other end of the same orientation problem - the summary at the
            bottom of a report, the newest entries in a log, the closing section
            of a document whose middle the agent does not need.

        Contract:
            Stateless and cursor-free, bounded by the same policy limits as
            `head`.

            `chars` trims from the START of the tail, keeping the end. That is
            the opposite of `head` on purpose: in both cases the trim discards
            the side furthest from what was asked for.

            `has_more` is always False - a tail reaches the end by definition -
            so use `start_line` to see how much was skipped.

        Args:
            lines: How many trailing lines, within `ReaderPolicy` bounds.
            chars: Optional character cap, within `ReaderPolicy` bounds.

        Returns:
            TextChunk: The trailing span.

        Raises:
            ValueError: If either budget is outside its documented bounds.
        """
        span = AgentTextReader._validated_line_target(lines)
        start_line = max(self.line_count - span, 0)
        start = self.line_start(start_line)
        truncated_by = "lines" if start_line > 0 else "end"
        total_chars = self.char_count
        if chars is not None:
            cap = AgentTextReader._validated_char_target(chars)
            if total_chars - start > cap:
                start = total_chars - cap
                truncated_by = "chars"
        return self._chunk_for_span(start, total_chars, truncated_by)

    def reader(
            self,
            *,
            line_target: int = ReaderPolicy.DEFAULT_LINE_TARGET,
            char_target: int = ReaderPolicy.DEFAULT_CHAR_TARGET,
            start_line: int = 0,
    ) -> "AgentTextReader":
        """
        Build a private, resumable cursor over this document.

        Purpose:
            The intended entry point. Each agent calls this to get its OWN
            cursor; the document behind it stays shared and is never copied.

        Args:
            line_target: Lines per read, within `ReaderPolicy` bounds.
            char_target: Characters per read, within `ReaderPolicy` bounds.
            start_line: Zero-based line to begin at.

        Returns:
            AgentTextReader: A cursor owned solely by the caller.
        """
        return AgentTextReader(
            self,
            line_target=line_target,
            char_target=char_target,
            start_line=start_line,
        )


class AgentTextReader:
    """
    A resumable, budget-bounded cursor over one `IndexedText`.

    Purpose:
        Let one agent walk a document in steps it chose the size of, remembering
        where it stopped, without ever holding more than one step's worth.

    Contract:
        - Every read honours BOTH budgets and stops at whichever binds first.
        - The cursor ADVANCES on `read()` and `next()`, so calling twice returns
          consecutive chunks. That is the "call it again for the next set"
          behaviour; nothing else needs to track position.
        - `peek()` reads without advancing, for an agent deciding whether to
          commit context to the next step.
        - `seek_line()` / `reset()` reposition; `remaining_lines` reports what
          is left.
        - Implements the iterator protocol over the SAME cursor, so a `for` loop
          and manual `read()` calls interleave coherently rather than being two
          independent traversals.
        - Budgets are validated at construction AND at any per-call override, so
          an out-of-range target fails at the call site instead of silently
          clamping and returning a surprising amount of text.

    Threading / Concurrency:
        NOT shared between agents - one reader, one owner. That restriction is
        what removes the lock: the cursor is mutable, so two threads sharing one
        reader would interleave reads and each see gaps. The underlying
        `IndexedText` IS safe to share, which is the whole point of the split.

    Lifecycle / Cleanup:
        Plain object with no cleanup contract, holding one reference and three
        integers. Deliberately NOT `Cleanable`: construct freely, drop when
        done.

    Registration:
        MELDER KERNEL - guarded. Obtained from `IndexedText.reader(...)`.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Your own resumable cursor over a large document. Set
        line_target (2-100) and char_target; call read() repeatedly and each
        call returns the next chunk with has_more telling you whether to
        continue. Use head(n)/tail(n) to orient and peek() to look ahead - none
        of the three move the cursor - and seek_line()/reset() to reposition.
        Iterate it directly to stream. Reads stop at whichever budget binds
        first and the chunk says which one via truncated_by.
    """

    __slots__ = ["_indexed", "_offset", "_line_target", "_char_target"]

    def __init__(
            self,
            indexed: IndexedText,
            *,
            line_target: int = ReaderPolicy.DEFAULT_LINE_TARGET,
            char_target: int = ReaderPolicy.DEFAULT_CHAR_TARGET,
            start_line: int = 0,
    ) -> None:
        """
        Build one private cursor over a shared document.

        Args:
            indexed: The shared document to read.
            line_target: Lines per read, within `ReaderPolicy` bounds.
            char_target: Characters per read, within `ReaderPolicy` bounds.
            start_line: Zero-based line to begin at.

        Returns:
            None

        Raises:
            TypeError: If `indexed` is not an `IndexedText`.
            ValueError: If either budget is outside its documented bounds.
            IndexError: If `start_line` is outside the document.
        """
        if not isinstance(indexed, IndexedText):
            raise TypeError(
                f"indexed must be IndexedText, got {type(indexed).__name__}"
            )
        self._indexed: IndexedText = indexed
        self._line_target: int = self._validated_line_target(line_target)
        self._char_target: int = self._validated_char_target(char_target)
        self._offset: int = indexed.line_start(start_line)

    @staticmethod
    def _validated_line_target(value: int) -> int:
        """
        Validate one line budget against the policy bounds.

        Args:
            value: Requested lines per read.

        Returns:
            int: The validated value.

        Raises:
            ValueError: If outside `MIN_LINE_TARGET..MAX_LINE_TARGET`.
        """
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"line_target must be an int, got {value!r}")
        if not (ReaderPolicy.MIN_LINE_TARGET <= value <= ReaderPolicy.MAX_LINE_TARGET):
            raise ValueError(
                f"line_target must be between {ReaderPolicy.MIN_LINE_TARGET} and "
                f"{ReaderPolicy.MAX_LINE_TARGET}, got {value}"
            )
        return value

    @staticmethod
    def _validated_char_target(value: int) -> int:
        """
        Validate one character budget against the policy bounds.

        Args:
            value: Requested characters per read.

        Returns:
            int: The validated value.

        Raises:
            ValueError: If outside `MIN_CHAR_TARGET..MAX_CHAR_TARGET`.
        """
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"char_target must be an int, got {value!r}")
        if not (ReaderPolicy.MIN_CHAR_TARGET <= value <= ReaderPolicy.MAX_CHAR_TARGET):
            raise ValueError(
                f"char_target must be between {ReaderPolicy.MIN_CHAR_TARGET} and "
                f"{ReaderPolicy.MAX_CHAR_TARGET}, got {value}"
            )
        return value

    @property
    def document(self) -> IndexedText:
        """
        Return the shared document this cursor reads.

        Returns:
            IndexedText: The underlying document.
        """
        return self._indexed

    @property
    def line_target(self) -> int:
        """
        Return the current lines-per-read budget.

        Returns:
            int: Lines per read.
        """
        return self._line_target

    @property
    def char_target(self) -> int:
        """
        Return the current characters-per-read budget.

        Returns:
            int: Characters per read.
        """
        return self._char_target

    @property
    def current_line(self) -> int:
        """
        Return the line the cursor currently sits on.

        Returns:
            int: Zero-based line number.
        """
        return self._indexed.line_of_offset(self._offset)

    @property
    def current_offset(self) -> int:
        """
        Return the absolute character offset the cursor sits at.

        Returns:
            int: Zero-based character offset.
        """
        return self._offset

    @property
    def exhausted(self) -> bool:
        """
        Return whether the cursor has consumed the whole document.

        Returns:
            bool: True when no content remains.
        """
        return self._offset >= self._indexed.char_count

    @property
    def remaining_lines(self) -> int:
        """
        Return how many lines remain from the cursor to the end.

        Returns:
            int: Remaining line count; zero once exhausted.
        """
        if self.exhausted:
            return 0
        return self._indexed.line_count - self.current_line

    @property
    def remaining_chars(self) -> int:
        """
        Return how many characters remain from the cursor to the end.

        Returns:
            int: Remaining character count; zero once exhausted.
        """
        return max(self._indexed.char_count - self._offset, 0)

    def set_targets(
            self,
            *,
            line_target: Optional[int] = None,
            char_target: Optional[int] = None,
    ) -> None:
        """
        Change either budget without disturbing the cursor.

        Purpose:
            Let an agent widen or narrow its step mid-document - typically after
            a chunk reported `truncated_by` and it wants to relieve exactly the
            budget that bound.

        Args:
            line_target: New lines-per-read budget, or `None` to leave it.
            char_target: New characters-per-read budget, or `None` to leave it.

        Returns:
            None

        Raises:
            ValueError: If a supplied budget is outside its documented bounds.
        """
        if line_target is not None:
            self._line_target = self._validated_line_target(line_target)
        if char_target is not None:
            self._char_target = self._validated_char_target(char_target)

    def seek_line(self, line: int) -> None:
        """
        Move the cursor to the start of one line.

        Args:
            line: Zero-based line number, `0 <= line <= line_count`.

        Returns:
            None

        Raises:
            IndexError: If `line` is outside the document.
        """
        self._offset = self._indexed.line_start(line)

    def reset(self) -> None:
        """
        Move the cursor back to the start of the document.

        Returns:
            None
        """
        self._offset = 0

    def peek(
            self,
            *,
            line_target: Optional[int] = None,
            char_target: Optional[int] = None,
    ) -> TextChunk:
        """
        Read the next chunk WITHOUT advancing the cursor.

        Purpose:
            Let an agent size the next step - or check what is coming - before
            committing context to it.

        Args:
            line_target: One-off line budget for this read only.
            char_target: One-off character budget for this read only.

        Returns:
            TextChunk: What `read()` would return next.

        Raises:
            ValueError: If a supplied budget is outside its documented bounds.
        """
        return self._read_from(
            self._offset, line_target=line_target, char_target=char_target
        )

    def read(
            self,
            *,
            line_target: Optional[int] = None,
            char_target: Optional[int] = None,
    ) -> TextChunk:
        """
        Read the next chunk and ADVANCE the cursor past it.

        Purpose:
            The primary call. Invoke it repeatedly; each call continues where
            the last stopped, and `TextChunk.has_more` says whether another is
            worth making.

        Contract:
            Once exhausted, returns an empty chunk with `has_more=False` rather
            than raising. Paging off the end is a normal outcome and an agent
            should not need a try block to finish a document.

        Args:
            line_target: One-off line budget for this read only. Does NOT change
                the reader's standing budget - use `set_targets` for that.
            char_target: One-off character budget for this read only.

        Returns:
            TextChunk: The chunk read.

        Raises:
            ValueError: If a supplied budget is outside its documented bounds.
        """
        chunk = self._read_from(
            self._offset, line_target=line_target, char_target=char_target
        )
        self._offset = chunk.end_char
        return chunk

    def _read_from(
            self,
            offset: int,
            *,
            line_target: Optional[int],
            char_target: Optional[int],
    ) -> TextChunk:
        """
        Compute one bounded chunk starting at an offset, touching no state.

        Contract:
            PURE. `read` and `peek` differ only in whether they store the
            result's `end_char`, so both go through here and cannot drift apart.

            The line budget is applied first, then the character budget trims
            the result. When trimming would return NOTHING - a single line
            longer than the whole character budget - the full line is returned
            anyway. Progress beats the budget: an agent that receives an empty
            chunk while `has_more` is true has no way to advance and would spin.

        Args:
            offset: Absolute character offset to read from.
            line_target: One-off line budget, or `None` for the standing one.
            char_target: One-off character budget, or `None` for the standing one.

        Returns:
            TextChunk: The computed chunk.

        Raises:
            ValueError: If a supplied budget is outside its documented bounds.
        """
        indexed = self._indexed
        lines = (
            self._line_target
            if line_target is None
            else self._validated_line_target(line_target)
        )
        chars = (
            self._char_target
            if char_target is None
            else self._validated_char_target(char_target)
        )

        total_lines = indexed.line_count
        total_chars = indexed.char_count

        if offset >= total_chars:
            end_line = total_lines
            return TextChunk(
                text="",
                start_line=end_line,
                end_line=end_line,
                start_char=total_chars,
                end_char=total_chars,
                total_lines=total_lines,
                total_chars=total_chars,
                has_more=False,
                truncated_by="end",
            )

        start_line = indexed.line_of_offset(offset)
        stop_line = min(start_line + lines, total_lines)
        line_bounded_end = indexed.line_start(stop_line)
        # `offset` may sit mid-line after a character-bounded read, so the span
        # is measured from the cursor, not from the line start.
        end = line_bounded_end

        truncated_by = "lines" if stop_line < total_lines else "end"
        if end - offset > chars:
            end = offset + chars
            truncated_by = "chars"
            if end <= offset:
                # Budget cannot fit even one character of progress. Return the
                # line anyway rather than stalling the agent.
                end = min(indexed.line_start(min(start_line + 1, total_lines)), total_chars)
                if end <= offset:
                    end = total_chars

        return indexed._chunk_for_span(offset, end, truncated_by)

    def stream(
            self,
            *,
            line_target: Optional[int] = None,
            char_target: Optional[int] = None,
    ) -> Iterator[TextChunk]:
        """
        Yield chunks from the cursor to the end of the document.

        Purpose:
            The generator form. Same cursor, same budgets - this is a loop over
            `read()`, not a second traversal, so a partially consumed reader
            streams the REMAINDER rather than restarting.

        Contract:
            Advances the cursor as it goes. Abandoning the generator part-way
            leaves the cursor exactly where it stopped, so an agent can break
            out, do something else, and resume with `read()`.

        Args:
            line_target: One-off line budget applied to every yielded chunk.
            char_target: One-off character budget applied to every yielded chunk.

        Returns:
            Iterator[TextChunk]: Successive chunks until the document ends.
        """
        while not self.exhausted:
            yield self.read(line_target=line_target, char_target=char_target)

    def stream_chars(self, char_target: int) -> Iterator[TextChunk]:
        """
        Yield chunks bounded primarily by CHARACTER count.

        Purpose:
            The character-first generator. Line structure still determines where
            chunks can start, but the character budget is what binds, which is
            the right mode when an agent is budgeting context rather than
            reading structured text.

        Contract:
            Widens the line budget to its maximum for the duration so the
            character budget is the effective limit. The reader's standing
            budgets are NOT modified.

        Args:
            char_target: Characters per chunk, within `ReaderPolicy` bounds.

        Returns:
            Iterator[TextChunk]: Successive character-bounded chunks.

        Raises:
            ValueError: If `char_target` is outside its documented bounds.
        """
        return self.stream(
            line_target=ReaderPolicy.MAX_LINE_TARGET,
            char_target=self._validated_char_target(char_target),
        )

    def stream_lines(self, line_target: int) -> Iterator[TextChunk]:
        """
        Yield chunks bounded primarily by LINE count.

        Contract:
            Widens the character budget to its maximum for the duration so the
            line budget is the effective limit. The reader's standing budgets
            are NOT modified.

        Args:
            line_target: Lines per chunk, within `ReaderPolicy` bounds.

        Returns:
            Iterator[TextChunk]: Successive line-bounded chunks.

        Raises:
            ValueError: If `line_target` is outside its documented bounds.
        """
        return self.stream(
            line_target=self._validated_line_target(line_target),
            char_target=ReaderPolicy.MAX_CHAR_TARGET,
        )

    def head(
            self,
            lines: int = ReaderPolicy.DEFAULT_LINE_TARGET,
            *,
            chars: Optional[int] = None,
    ) -> TextChunk:
        """
        Return the first lines of the document WITHOUT moving the cursor.

        Contract:
            Convenience delegate to `IndexedText.head`. Deliberately does not
            reposition: an agent orienting itself mid-document should not lose
            its place to do so. Use `reset()` if you actually want to restart.

        Args:
            lines: How many leading lines, within `ReaderPolicy` bounds.
            chars: Optional character cap, within `ReaderPolicy` bounds.

        Returns:
            TextChunk: The leading span.

        Raises:
            ValueError: If either budget is outside its documented bounds.
        """
        return self._indexed.head(lines, chars=chars)

    def tail(
            self,
            lines: int = ReaderPolicy.DEFAULT_LINE_TARGET,
            *,
            chars: Optional[int] = None,
    ) -> TextChunk:
        """
        Return the last lines of the document WITHOUT moving the cursor.

        Contract:
            Convenience delegate to `IndexedText.tail`. Deliberately does not
            reposition; use `seek_line()` if you want to continue reading from
            where the tail begins.

        Args:
            lines: How many trailing lines, within `ReaderPolicy` bounds.
            chars: Optional character cap, within `ReaderPolicy` bounds.

        Returns:
            TextChunk: The trailing span.

        Raises:
            ValueError: If either budget is outside its documented bounds.
        """
        return self._indexed.tail(lines, chars=chars)

    def __iter__(self) -> "AgentTextReader":
        """
        Return self, so the reader is directly iterable.

        Returns:
            AgentTextReader: This cursor.
        """
        return self

    def __next__(self) -> TextChunk:
        """
        Return the next chunk, or stop when the document is consumed.

        Returns:
            TextChunk: The next chunk.

        Raises:
            StopIteration: When the cursor is exhausted.
        """
        if self.exhausted:
            raise StopIteration
        return self.read()

    def __repr__(self) -> str:
        """
        Return a diagnostic summary of the cursor's position and budgets.

        Returns:
            str: Debug representation.
        """
        return (
            f"AgentTextReader(line={self.current_line}/{self._indexed.line_count}, "
            f"char={self._offset}/{self._indexed.char_count}, "
            f"line_target={self._line_target}, char_target={self._char_target})"
        )
