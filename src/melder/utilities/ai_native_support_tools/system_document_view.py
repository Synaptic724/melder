"""
Query objects for melder's shipped system documents.

WHAT THIS IS
------------
The objects returned by `melder.__architecture__`, `__components__`,
`__graph_network__` and `__graph_details__`.

Melder captures its own context maps into generated modules at build time, so
an installed melder can answer questions about itself with nothing but the
package present. These are the objects that answer.

ORIENTATION IS NOT A COST
-------------------------
`__architecture__` is meant to be READ. It is how the system is understood -
boundaries, boot order, invariants, what fails and how - and an agent that
slices two sections out of it and calls that understanding will make confident
decisions on a model of the system it does not have. At 2,298 lines it is the
one document that repays reading broadly.

The index-first discipline exists for the OTHER documents. `__components__` is
a lookup table at 8,370 lines; `__graph_details__` is 25,291 lines of
per-file reference. Nobody reads a reference cover to cover, and handing an
agent that string is not an answer, it is a bill. So those return their INDEX -
what can be asked - and then exactly the span asked for.

WHAT THESE OBJECTS DO FOR YOU
-----------------------------
Reading a context map by hand means: find the index, verify its staleness
proof, locate the row, slice that range, and refuse if the proof does not
match. All of it is done here, once, at build time:

  - The index is already parsed, so finding a row is a dict lookup.
  - The proof was verified during the build. A document that failed
    verification never became an entry; it became a refusal carrying a reason.
  - `verify()` re-checks the shipped bytes at runtime, so a corrupted or
    hand-edited install is caught before a single line is sliced.

THE ACCESS SHAPES
-----------------
  - `index()` / `groups()` - what is here, and what each piece costs
  - `search(needle)`       - which sections discuss a term, ranked
  - `get(key)`             - one target slice
  - `reader(key)` / `stream(key)` - a private cursor when a section is itself
    too large to swallow, so a section is never a second cliff
  - `cite(key)`            - `document:start-end`, ready to use as evidence

`SystemGraphView` adds traversal. Its adjacency was resolved at build time from
the graph document's edge tables, which means the query that layout cannot
answer cheaply - "what points AT this" - costs a dict lookup here, and
`impact()` turns it straight into the files a change would touch.

TRUST IS NOT UNIFORM
--------------------
Every edge carries `origin`. `derived` came from the syntax tree and is rebuilt
on every extraction. `authored` was written by someone who read the code, and
may describe code that has since moved. Authored edges carry `why` - the
argument for a claim the syntax tree cannot support - and it is worth reading
before relying on one. Nodes carry `unsemantic` for the same reason: structure
established, meaning not.

Extractor guesses are absent by construction. They over-generate heavily and
are leads rather than evidence, so no walk can traverse one by accident.

CONCURRENCY
-----------
Views and their adjacency are immutable and shared. Every cursor handed out is
private to its caller. Many agents may read and walk concurrently with no lock,
which is the property the free-threaded build is being aimed at.
"""
from types import MappingProxyType
from typing import Dict, Iterator, List, Mapping, NamedTuple, Optional, Tuple

from melder.utilities.ai_native_support_tools.agent_text_reader import (
    AgentTextReader,
    TextChunk,
)


class Section(NamedTuple):
    """
    One addressable span of a system document.

    Attributes:
        key: How the section is addressed. A heading path for `section`
            addressing (`"Data Flows and Sequences > Sequence: Cleanup"`), a
            repository-relative source path for `source_path` addressing.
        start_line: First line, 1-based and inclusive - the numbering the
            source index uses and the one `path:start-end` citations expect.
            Note that `TextChunk` line numbers are 0-based reader offsets; a
            chunk opening this section reports `start_line - 1`.
        end_line: Last line, 1-based and inclusive.
        line_count: Size of the span, so a caller can budget BEFORE reading.
    """

    key: str
    start_line: int
    end_line: int
    line_count: int


def _is_structural(line: str) -> bool:
    """
    Return whether a line is document scaffolding rather than prose.

    Purpose:
        Used only to choose a search preview. Headings and file delimiters
        restate the section key, so previewing one tells a caller nothing it
        did not already know.

    Args:
        line: A raw document line.

    Returns:
        bool: True for HTML comments, markdown headings, and table rules.
    """
    stripped = line.lstrip()
    return stripped.startswith(("<!--", "#", "| ---", "|---"))


class SearchHit(NamedTuple):
    """
    One section whose BODY matches a search term.

    Attributes:
        key: The section's key, usable directly with `get()`.
        hits: How many lines in the section matched. A ranking signal - the
            section mentioning a term twenty times is usually the one that
            defines it, not the one that name-drops it.
        first_line: 1-based line of the first match, so a citation can be
            written without opening the section.
        preview: The first matching line, whitespace-collapsed and truncated.
            Enough to triage a hit without paying for the section.
    """

    key: str
    hits: int
    first_line: int
    preview: str


class Group(NamedTuple):
    """
    A cluster of sections sharing a prefix.

    Attributes:
        prefix: Directory path for `source_path` addressing, top-level heading
            for `section` addressing.
        sections: How many sections fall under it.
        line_count: Their combined size, so a caller can see what reading the
            whole group would cost before asking for any of it.
    """

    prefix: str
    sections: int
    line_count: int


class Edge(NamedTuple):
    """
    One outbound relationship between two graph nodes.

    Attributes:
        source: Fully qualified id of the node the edge leaves.
        relation: Relationship name, e.g. `owns_lifecycle_of`, `specializes`.
        target: Fully qualified id of the node the edge arrives at.
        cardinality: `one_to_one`, `many_to_one`, ... or `-` when unauthored.
        phase: Lifecycle phases the relationship is live in, or `-`.
        origin: `derived` or `authored`. THE trust discriminator - `derived`
            came from the syntax tree and is rebuilt every extraction;
            `authored` was written by hand and may describe code that has since
            moved. Never collapse the two.
        why: The authored justification for this relationship, or empty.

            READ THIS BEFORE RELYING ON AN AUTHORED EDGE. An authored
            `owns_lifecycle_of` asserts ownership where the syntax tree shows
            only a reference - the why-line is the argument for that claim, and
            without it the edge is an assertion with no support.

            Keyed by endpoints in the source document, so authored edges
            sharing a source and target share one justification.

            ALWAYS empty for `derived` edges. They need no argument - the
            syntax tree is their evidence - and 153 endpoint pairs here carry
            both a derived and an authored edge, so attaching the authored
            justification to its mechanical twin would blur the two tiers.
    """

    source: str
    relation: str
    target: str
    cardinality: str
    phase: str
    origin: str
    why: str


class Impact(NamedTuple):
    """
    One source file affected by changing a node.

    Attributes:
        source: Repository-relative path. Also its section key in the graph
            document, so it can be read immediately.
        hops: Shortest distance from the changed node. 1 is a direct dependent.
        nodes: The dependent node ids defined in this file.
        edges: How many inbound edges reach the changed node from here. A
            rough coupling weight - one reference is not eight.
    """

    source: str
    hops: int
    nodes: Tuple[str, ...]
    edges: int


class Node(NamedTuple):
    """
    One graph node.

    Attributes:
        node_id: Fully qualified id.
        source: Repository-relative path of the file defining it. This is also
            its section key in `__graph_details__`, which is the join between
            the two graph views.
        name: Bare name.
        kind: `module`, `class`, `interface`, `abstract`, `enum`, `record`.
        line: Definition line in the source file.
        unsemantic: True when the node carries mechanical scaffold only. Its
            structure is trustworthy; its MEANING has not been authored. Do not
            infer purpose from the name of an unsemantic node.
    """

    node_id: str
    source: str
    name: str
    kind: str
    line: int
    unsemantic: bool


class SystemDocumentView:
    """
    Indexed, sliceable view over one shipped system document.

    Purpose:
        Give an agent a document it can interrogate rather than a document it
        must consume. Every read is bounded and every bound is stated up front
        by `index()`.

    Contract:
        Immutable and shared. Section lookup is exact by key; `find()` covers
        the substring case. Slicing an unavailable document raises rather than
        returning empty text, because a silent empty slice reads exactly like a
        section that genuinely says nothing.

    Attributes:
        _document: The underlying `StaticSystemDocument`.
        _entry: That document's manifest entry.
        _sections: Ordered sections, as emitted by the build.
        _by_key: Key -> section, for exact lookup.
    """

    __slots__ = ("_document", "_entry", "_sections", "_by_key")

    def __init__(self, entry: Mapping[str, object]) -> None:
        """
        Build a view from one manifest entry.

        Contract:
            Construction touches the MANIFEST only - title, addressing, proof,
            and the section table, all of which are small. The document text
            lives in a separate generated module that is not imported here.

            That split is the point. These four views are built at package
            scope, so anything imported during construction is paid by every
            `import melder`. The graph payload alone is 1.6 MB of source; a
            process that never asks a document anything must not pay to parse
            it.

        Args:
            entry: The manifest entry describing this document.
        """
        self._document = None
        self._entry = entry
        self._sections = None
        self._by_key = None

    def _index(self) -> Tuple[Tuple[Section, ...], Mapping[str, Section]]:
        """
        Return this document's sections, loading the table on first use.

        Purpose:
            The section ranges live in their own generated module, keyed by
            document file so the two graph views share one table. Loading them
            here rather than in `__init__` keeps `import melder` off the hook
            for 756 tuples nothing has asked for yet.

        Returns:
            Tuple: (ordered sections, key -> section).
        """
        if self._sections is None:
            from melder._build_assets._system_documents.manifest import (
                system_documents_index,
            )

            rows = system_documents_index.SECTIONS.get(
                str(self._entry["document_file"]), ()
            )
            sections = tuple(
                Section(key, start, end, end - start + 1) for key, start, end in rows
            )
            self._sections = sections
            self._by_key = MappingProxyType({s.key: s for s in sections})
        return self._sections, self._by_key

    def _doc(self) -> object:
        """
        Return the carrier, importing the payload module on first use.

        Purpose:
            The deferral that keeps `import melder` cheap. Called by every
            method that needs TEXT and by none that only needs the index.

        Returns:
            object: The `StaticSystemDocument` for this document.

        Raises:
            RuntimeError: When the document did not ship, carrying the
                build-time reason.
        """
        if self._document is None:
            self._require_available()
            from importlib import import_module

            from melder.system_document import StaticSystemDocument

            payload = import_module(
                "melder._build_assets._system_documents.payloads."
                f"{self._entry['payload_module']}"
            )
            self._document = StaticSystemDocument.from_markdown(
                document_name=self.name,
                markdown_text=payload.TEXT,
                agent_purpose=self.summary,
            )
        return self._document

    @property
    def name(self) -> str:
        """Return the melder document name, e.g. `__architecture__`."""
        return str(self._entry["name"])

    @property
    def document_name(self) -> str:
        """
        Return the melder document name.

        Contract:
            Alias of `name`, kept because callers written against
            `StaticSystemDocument` already use it. The view now stands where
            the carrier used to, so it answers to both.
        """
        return self.name

    @property
    def title(self) -> str:
        """Return the human-readable document title."""
        return str(self._entry["title"])

    @property
    def summary(self) -> str:
        """Return what this document is for, in one paragraph."""
        return str(self._entry["summary"])

    @property
    def source(self) -> str:
        """Return the repository path this document was captured from."""
        return str(self._entry["source"])

    @property
    def addressing(self) -> str:
        """
        Return how sections are keyed.

        Returns:
            str: `section` when keys are heading paths, `source_path` when
                keys are repository-relative file paths. Determines what a
                caller should pass to `get()`.
        """
        return str(self._entry["addressing"])

    @property
    def available(self) -> bool:
        """
        Return whether this document shipped with content.

        Purpose:
            False means the source pair failed its staleness proof at build
            time or was absent. `reason` says which. An unavailable document is
            NOT an empty document, and the distinction is the whole point:
            empty invites invention, refused does not.
        """
        return bool(self._entry["available"])

    @property
    def reason(self) -> str:
        """Return why an unavailable document is unavailable, else empty."""
        return str(self._entry.get("reason", ""))

    @property
    def line_count(self) -> int:
        """Return the document's line count as recorded by its index."""
        return int(self._entry["line_count"])

    @property
    def content_sha256(self) -> str:
        """Return the SHA-256 the index claimed for this document."""
        return str(self._entry["content_sha256"])

    @property
    def char_count(self) -> int:
        """
        Return the document's character count.

        Contract:
            Needs the text, so this materialises the payload. `line_count`
            comes from the manifest and does not.
        """
        return self._doc().char_count

    def render_markdown(self) -> str:
        """
        Return the ENTIRE document as one string.

        Purpose:
            The unbudgeted escape hatch, kept because tooling that converts or
            re-emits a document legitimately needs all of it.

        Contract:
            No budget. For `__graph_details__` this is 1.6 MB in one value. An
            agent answering a question wants `index()` then `get()`; this is
            for machines, not for reading.

        Returns:
            str: The full document text.

        Raises:
            RuntimeError: When the document is unavailable.
        """
        return self._doc().render_markdown()

    def render_json(self) -> str:
        """
        Return the document's minified JSON hardcopy envelope.

        Contract:
            Synthesised on first call and cached on the carrier - the payload
            ships as a plain string literal, so no envelope exists until
            something asks for one. Same unbudgeted caveat as
            `render_markdown()`.

        Returns:
            str: `{"m": <markdown>}`, minified.

        Raises:
            RuntimeError: When the document is unavailable.
        """
        return self._doc().render_json()

    def index(self) -> Tuple[Section, ...]:
        """
        Return every section, in document order.

        Purpose:
            THE entry point for a lookup document. An agent calls this to see
            what can be asked and what each answer costs in lines, then calls
            `get()` or `reader()` for the one it wants.

            For `__architecture__` this is a table of contents, not a
            substitute for reading it - orientation does not come from two
            sampled sections.

        Returns:
            Tuple[Section, ...]: Ordered sections.
        """
        return self._index()[0]

    def keys(self) -> Tuple[str, ...]:
        """Return every section key, in document order."""
        return tuple(section.key for section in self._index()[0])

    def find(self, needle: str) -> Tuple[Section, ...]:
        """
        Return sections whose key contains `needle`, case-insensitively.

        Purpose:
            Exact keys are long - a full heading path, or a full source path.
            An agent that knows it wants "conduit" should not have to
            reconstruct `src/melder/aether/conduit/conduit.py` to ask.

        Contract:
            Substring match on the key only, never on body text; a body search
            would mean reading the whole document, which is the cost this
            object exists to avoid. Document order is preserved, so for
            `source_path` addressing a directory prefix returns a subsystem's
            files contiguously.

        Args:
            needle: Substring to look for.

        Returns:
            Tuple[Section, ...]: Matching sections, possibly empty.
        """
        lowered = needle.lower()
        return tuple(s for s in self._index()[0] if lowered in s.key.lower())

    def search(
            self, needle: str, *, limit: int = 25, preview_chars: int = 120
    ) -> Tuple[SearchHit, ...]:
        """
        Return sections whose BODY mentions `needle`, ranked by hit count.

        Purpose:
            The one query `find()` cannot answer. `find()` matches section
            KEYS, which is useless for "where is thread safety discussed" - the
            concept lives in the prose, not in a heading. Without this an
            agent's only recourse is pulling a whole document and grepping,
            which for `__components__` is roughly 108k tokens and defeats the
            entire design.

        Contract:
            Returns SECTIONS, never text - the result stays index-shaped, so a
            caller still chooses what to open. A line inside nested sections is
            attributed to the MOST SPECIFIC one containing it, because
            `"Indexing > Verifying citations"` is a more useful answer than
            `"Indexing"`.

            Costs one payload load and one pass over the document, measured at
            4-8 ms on the largest documents here. That is real but it is paid
            once per process; the alternative is paying it in context, every
            time, forever.

            Case-insensitive substring matching. Not tokenised - `"thread"`
            matches `"threading"`, which for a code corpus is usually wanted.

        Args:
            needle: Text to look for.
            limit: Maximum sections to return, highest hit count first.
            preview_chars: How much of the first matching line to include.

        Returns:
            Tuple[SearchHit, ...]: Matching sections, most hits first, ties
                broken by document order.

        Raises:
            RuntimeError: When the document is unavailable.
            ValueError: When `needle` is empty - an empty needle matches every
                line and would return the whole index dressed as a result.
        """
        if not needle:
            raise ValueError("search needle cannot be empty")
        sections, _ = self._index()
        lines = self._doc().render_markdown().split("\n")

        # Most-specific-wins: assign every line to a section, largest spans
        # first, so a nested section overwrites its parent.
        owner: List[int] = [-1] * (len(lines) + 2)
        order = sorted(
            range(len(sections)), key=lambda i: sections[i].line_count, reverse=True
        )
        for position in order:
            span = sections[position]
            for line in range(span.start_line, min(span.end_line, len(lines)) + 1):
                owner[line] = position

        lowered = needle.lower()
        counts: Dict[int, int] = {}
        first: Dict[int, int] = {}
        for number, text in enumerate(lines, 1):
            if lowered not in text.lower():
                continue
            position = owner[number] if number < len(owner) else -1
            if position < 0:
                continue
            counts[position] = counts.get(position, 0) + 1
            # Prefer prose over structure. A match inside `<!-- BEGIN FILE -->`
            # or a `## path` heading previews the section key, which the caller
            # already has - spending the preview on it wastes the one line an
            # agent gets to triage with.
            if position not in first or (
                _is_structural(lines[first[position] - 1])
                and not _is_structural(text)
            ):
                first[position] = number

        ranked = sorted(counts, key=lambda i: (-counts[i], i))[:limit]
        found: List[SearchHit] = []
        for position in ranked:
            line = first[position]
            preview = " ".join(lines[line - 1].split())
            if len(preview) > preview_chars:
                preview = preview[: preview_chars - 1] + "\u2026"
            found.append(
                SearchHit(sections[position].key, counts[position], line, preview)
            )
        return tuple(found)

    def groups(self, depth: int = 3) -> Tuple[Group, ...]:
        """
        Return the index collapsed to one row per prefix.

        Purpose:
            `index()` on `__graph_details__` is 575 rows - roughly 11k tokens,
            enough that an agent reaching for it first has already spent more
            than most answers are worth. This is the cheap overview that says
            where to drill: ~40 rows instead of 575.

        Contract:
            For `source_path` addressing, groups by the first `depth` path
            segments. For `section` addressing, by the first `depth` heading
            levels. Ordered by first appearance, so the grouping reads in
            document order rather than alphabetically.

            DEPTH IS THE DIAL, and the default is deliberately shallow. This
            repo's tree runs eight segments deep in places; grouping at full
            directory depth gives 157 rows, which is a smaller cliff rather
            than no cliff. Start shallow, then re-group deeper on the branch
            you care about, or expand it with `find(prefix)`.

        Args:
            depth: How many path segments or heading levels to keep.

        Returns:
            Tuple[Group, ...]: One row per prefix.

        Raises:
            ValueError: When `depth` is below 1.
        """
        if depth < 1:
            raise ValueError(f"depth must be at least 1, got {depth}")
        separator = "/" if self.addressing == "source_path" else " > "
        by_prefix: Dict[str, List[int]] = {}
        for section in self._index()[0]:
            parts = section.key.split(separator)
            if self.addressing == "source_path" and len(parts) > 1:
                parts = parts[:-1]          # drop the filename, keep directories
            prefix = separator.join(parts[:depth]) or "."
            by_prefix.setdefault(prefix, []).append(section.line_count)
        return tuple(
            Group(prefix, len(sizes), sum(sizes)) for prefix, sizes in by_prefix.items()
        )

    def section(self, key: str) -> Section:
        """
        Return one section by exact key.

        Args:
            key: An exact key from `keys()`.

        Returns:
            Section: The addressed span.

        Raises:
            KeyError: When the key is not in the index. The message offers the
                closest `find()` matches, because these keys are long enough
                that a near miss is the likely failure.
        """
        sections, by_key = self._index()
        if key in by_key:
            return by_key[key]
        near = [s.key for s in self.find(key)][:5]
        hint = f"; did you mean {near}" if near else ""
        raise KeyError(
            f"{key!r} is not a section of {self.title!r} "
            f"({len(sections)} sections, addressed by "
            f"{self.addressing}){hint}"
        )

    def get(self, key: str) -> str:
        """
        Return the full text of one section.

        Purpose:
            The target slice. This is the normal way to read a section that
            fits in one look; use `reader()` when it does not.

        Args:
            key: An exact key from `keys()`.

        Returns:
            str: The section's lines, joined.

        Raises:
            KeyError: When the key is not in the index.
            RuntimeError: When the document is unavailable, so a refused
                document can never be mistaken for an empty one.
        """
        self._require_available()
        span = self.section(key)
        # `Section` ranges are 1-based inclusive, as the source index states
        # them and as the repo's `path:start-end` citation convention reads.
        # The reader indexes lines from 0. Convert here, once, rather than
        # leaking a second numbering scheme into the query surface.
        return self._doc().lines(span.start_line - 1, span.line_count)

    def cite(self, key: str, *, line: Optional[int] = None) -> str:
        """
        Return a `document:start-end` citation for a section.

        Purpose:
            This repository cites evidence as `path:start_line-end_line`. The
            numbers are already in the index, but formatting them by hand on
            every claim is exactly the kind of friction that ends with an agent
            citing nothing.

        Args:
            key: An exact section key.
            line: Optional single line to cite instead of the whole span - pass
                a `SearchHit.first_line` to cite the match rather than the
                section containing it.

        Returns:
            str: e.g. `src_graph.md:3518-3596`, or `src_graph.md:4752`.

        Raises:
            KeyError: When the key is not in the index.
        """
        span = self.section(key)
        document = str(self._entry["document_file"]) or self.name
        if line is not None:
            return f"{document}:{line}"
        return f"{document}:{span.start_line}-{span.end_line}"

    def reader(
            self,
            key: Optional[str] = None,
            *,
            line_target: int = 50,
            char_target: int = 8_192,
    ) -> AgentTextReader:
        """
        Return a private cursor over one section, or the whole document.

        Purpose:
            A section is not automatically small - the graph document's largest
            runs to hundreds of lines. This gives the same bounded, resumable
            read at section scale that the document-level reader gives at
            document scale, so there is no size at which the caller is forced
            back to a raw string.

        Contract:
            The cursor is the caller's alone; the indexed text behind it is
            shared and never copied. Positioned at the section's first line and
            NOT bounded at its last - a caller may read past the end into the
            following section, which is deliberate: sections are adjacent
            context, not walls.

        Args:
            key: Section to start at, or None to start at the document's top.
            line_target: Lines per read, 2-100.
            char_target: Characters per read; whichever binds first wins.

        Returns:
            AgentTextReader: A cursor owned solely by the caller.

        Raises:
            KeyError: When the key is not in the index.
            RuntimeError: When the document is unavailable.
            ValueError: When a budget is outside `ReaderPolicy` bounds.
        """
        self._require_available()
        cursor = self._doc().reader(
            line_target=line_target, char_target=char_target
        )
        if key is not None:
            cursor.seek_line(self.section(key).start_line - 1)
        return cursor

    def stream(
            self,
            key: str,
            *,
            line_target: int = 50,
            char_target: int = 8_192,
    ) -> Iterator[TextChunk]:
        """
        Yield one section in bounded chunks, stopping at its end.

        Purpose:
            The generator form the reader does not give on its own: `reader()`
            runs to the end of the DOCUMENT, this stops at the end of the
            SECTION. An agent asking for one section wants one section.

        Contract:
            Chunks never extend past the section's last line; the final chunk
            is trimmed to fit. Lazy - nothing is read until iterated, and
            abandoning the generator costs nothing.

        Args:
            key: An exact key from `keys()`.
            line_target: Lines per chunk, 2-100.
            char_target: Characters per chunk.

        Yields:
            TextChunk: Successive spans of the section.

        Raises:
            KeyError: When the key is not in the index.
            RuntimeError: When the document is unavailable.
        """
        span = self.section(key)
        cursor = self.reader(key, line_target=line_target, char_target=char_target)
        while not cursor.exhausted and cursor.current_line < span.end_line:
            remaining = span.end_line - cursor.current_line
            if remaining < cursor.line_target:
                cursor.set_targets(line_target=max(2, remaining))
            chunk = cursor.read()
            if not chunk.text:
                break
            yield chunk

    def head(self, lines: int = 50) -> TextChunk:
        """Return the document's opening lines."""
        self._require_available()
        return self._doc().head(lines)

    def tail(self, lines: int = 50) -> TextChunk:
        """Return the document's closing lines."""
        self._require_available()
        return self._doc().tail(lines)

    def verify(self) -> bool:
        """
        Re-check the shipped text against the proof its index claimed.

        Purpose:
            The build verified the source pair. This verifies the SHIPPED
            payload, which is a different claim - it catches a corrupted wheel,
            a bad merge into a generated module, or a hand-edit of emitted
            code. `src_graph_usage.md` refuses to slice an unverified index;
            this is the same refusal, available in-process.

        Contract:
            Recomputes the SHA-256 of the payload. Costs a full hash of the
            document, so it is a deliberate call, never implicit on read.

        Returns:
            bool: True when the payload matches its recorded digest. Always
                False for an unavailable document - there is nothing to verify.
        """
        if not self.available:
            return False
        import hashlib

        text = self._doc().render_markdown()
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return digest == self.content_sha256

    def _require_available(self) -> None:
        """
        Raise when this document did not ship with content.

        Raises:
            RuntimeError: Always, when unavailable, carrying the build-time
                reason so the caller learns WHY rather than seeing nothing.
        """
        if not self.available:
            raise RuntimeError(
                f"{self.title!r} is not available: "
                f"{self.reason or 'not captured at build time'}"
            )

    def __contains__(self, key: object) -> bool:
        """Return whether an exact section key is present."""
        return key in self._index()[1]

    def __len__(self) -> int:
        """Return the number of sections."""
        return len(self._index()[0])

    def __iter__(self) -> Iterator[Section]:
        """Iterate sections in document order."""
        return iter(self._index()[0])

    def __repr__(self) -> str:
        """Return a summary naming the size and addressing of this view."""
        state = "available" if self.available else f"unavailable: {self.reason}"
        return (
            f"<{type(self).__name__} {self.title!r} "
            f"{len(self._index()[0])} sections, {self.line_count} lines, "
            f"addressed by {self.addressing}, {state}>"
        )


class SystemGraphView(SystemDocumentView):
    """
    A document view that is also a walkable graph.

    Purpose:
        Backs `__graph_network__` and `__graph_details__`. Both address the
        same document; this adds the adjacency resolved at build time, so a
        node's neighbours are a dict lookup instead of a parse.

    Contract:
        The adjacency module is imported on FIRST graph access, never at
        construction. A process that imports melder and never walks pays
        nothing for the tables.

        Extractor candidates are absent by design. They over-generate roughly
        8x against a hand-authored graph and are leads, not evidence; they are
        not in the shipped adjacency, so no walk can traverse a guess by
        accident.

    Attributes:
        _adjacency: The lazily imported generated adjacency module.
    """

    __slots__ = ("_adjacency",)

    def __init__(self, entry: Mapping[str, object]) -> None:
        """
        Build a graph view.

        Args:
            entry: The manifest entry describing this graph document.
        """
        super().__init__(entry)
        self._adjacency = None

    def _graph(self) -> object:
        """
        Return the adjacency module, importing it on first use.

        Returns:
            object: The generated adjacency module.
        """
        if self._adjacency is None:
            from melder._build_assets._system_documents.manifest import (
                graph_adjacency_manifest,
            )

            self._adjacency = graph_adjacency_manifest
        return self._adjacency

    @property
    def node_count(self) -> int:
        """Return how many nodes the graph carries."""
        return int(self._graph().NODE_COUNT)

    @property
    def edge_count(self) -> int:
        """Return how many edges the graph carries, candidates excluded."""
        return int(self._graph().EDGE_COUNT)

    @property
    def relations(self) -> Tuple[str, ...]:
        """
        Return every relation name present, sorted.

        Purpose:
            The vocabulary of the graph. An agent filtering a walk needs to
            know what it may filter ON without sampling edges to find out.
        """
        return tuple(self._graph().RELATIONS)

    def node_ids(self) -> Tuple[str, ...]:
        """Return every node id, sorted."""
        return tuple(sorted(self._graph().NODES))

    def node(self, node_id: str) -> Node:
        """
        Return one node by id.

        Args:
            node_id: Fully qualified node id.

        Returns:
            Node: The node record.

        Raises:
            KeyError: When no such node exists, with close matches offered.
        """
        table = self._graph().NODES
        if node_id not in table:
            near = [n for n in sorted(table) if node_id.lower() in n.lower()][:5]
            hint = f"; did you mean {near}" if near else ""
            raise KeyError(f"{node_id!r} is not a node in this graph{hint}")
        source, name, kind, line, unsemantic = table[node_id]
        return Node(node_id, source, name, kind, line, unsemantic)

    def find_nodes(self, needle: str) -> Tuple[Node, ...]:
        """
        Return nodes whose id contains `needle`, case-insensitively.

        Args:
            needle: Substring to match against node ids.

        Returns:
            Tuple[Node, ...]: Matching nodes, sorted by id.
        """
        lowered = needle.lower()
        return tuple(
            self.node(n) for n in sorted(self._graph().NODES) if lowered in n.lower()
        )

    def nodes_in(self, source_path: str) -> Tuple[Node, ...]:
        """
        Return every node defined in one source file.

        Purpose:
            The bridge from a file to its nodes. `source_path` is also this
            document's section key, so a caller holding a section key can
            immediately ask what lives in it.

        Args:
            source_path: Repository-relative path.

        Returns:
            Tuple[Node, ...]: Nodes defined there, ordered by definition line.
        """
        found = [
            self.node(n)
            for n, info in self._graph().NODES.items()
            if info[0] == source_path
        ]
        return tuple(sorted(found, key=lambda node: node.line))

    def node_at(self, source_path: str, line: int) -> Optional[Node]:
        """
        Return the node most likely to enclose a line of source.

        Purpose:
            Closes the loop from a traceback. `conduit.py:412` is otherwise a
            dead end - the graph knows definition lines, so an agent can infer
            the enclosing node by hand, but nothing in the API does it.

        Contract:
            AN INFERENCE, NOT A FACT, and named to admit it. The graph records
            where each node BEGINS, never where it ends, so this returns the
            last node defined at or before `line`. That is right for a line
            inside the last class in a file and WRONG for a line in a
            module-level function that follows one - it will name the class.

            Verify against the source before citing it. Returns None when the
            file has no nodes or every node is defined after the line.

        Args:
            source_path: Repository-relative path, as the index keys it.
            line: 1-based line number in that source file.

        Returns:
            Optional[Node]: The enclosing candidate, or None.
        """
        candidates = [
            node
            for node in self.nodes_in(source_path)
            if node.line and node.line <= line
        ]
        return candidates[-1] if candidates else None

    def edges_from(
            self, node_id: str, *, relation: Optional[str] = None
    ) -> Tuple[Edge, ...]:
        """
        Return edges leaving a node.

        Args:
            node_id: Fully qualified node id.
            relation: Optional relation filter.

        Returns:
            Tuple[Edge, ...]: Outbound edges, empty when the node has none.
        """
        return self._edges(self._graph().OUTBOUND, node_id, relation)

    def edges_to(
            self, node_id: str, *, relation: Optional[str] = None
    ) -> Tuple[Edge, ...]:
        """
        Return edges arriving at a node.

        Purpose:
            Reverse lookup - "what points AT this". Reading the document, this
            is the expensive query: sections carry outbound edges only, so
            answering it by hand means scanning every section. Resolved once at
            build time, it costs the same as the forward direction.

        Args:
            node_id: Fully qualified node id.
            relation: Optional relation filter.

        Returns:
            Tuple[Edge, ...]: Inbound edges, empty when nothing points at it.
        """
        return self._edges(self._graph().INBOUND, node_id, relation)

    def _edges(
            self,
            table: Mapping[str, Tuple[int, ...]],
            node_id: str,
            relation: Optional[str],
    ) -> Tuple[Edge, ...]:
        """
        Resolve edge positions into `Edge` records.

        Args:
            table: `OUTBOUND` or `INBOUND`.
            node_id: The node to look up.
            relation: Optional relation filter.

        Returns:
            Tuple[Edge, ...]: The resolved edges.
        """
        graph = self._graph()
        rows = graph.EDGES
        whys = getattr(graph, "WHY", {})
        # Why-lines justify AUTHORED claims, so they attach only to authored
        # edges. 153 endpoint pairs in this graph carry the same relationship
        # twice - once derived, once authored - and the justification belongs
        # to the authored one. Showing it on the derived twin would suggest a
        # mechanical fact needed an argument, blurring the boundary `origin`
        # exists to keep sharp.
        found = (
            Edge(
                *rows[position],
                why=(
                    whys.get((rows[position][0], rows[position][2]), "")
                    if rows[position][5] == "authored"
                    else ""
                ),
            )
            for position in table.get(node_id, ())
        )
        if relation is not None:
            found = (edge for edge in found if edge.relation == relation)
        return tuple(found)

    def neighbors(
            self,
            node_id: str,
            *,
            direction: str = "out",
            relation: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the node ids one step away.

        Args:
            node_id: Fully qualified node id.
            direction: `out`, `in`, or `both`.
            relation: Optional relation filter.

        Returns:
            Tuple[str, ...]: Neighbour ids, de-duplicated, order preserved.

        Raises:
            ValueError: When `direction` is not one of the three.
        """
        if direction not in ("out", "in", "both"):
            raise ValueError(
                f"direction must be 'out', 'in' or 'both', got {direction!r}"
            )
        found: List[str] = []
        if direction in ("out", "both"):
            found += [e.target for e in self.edges_from(node_id, relation=relation)]
        if direction in ("in", "both"):
            found += [e.source for e in self.edges_to(node_id, relation=relation)]
        return tuple(dict.fromkeys(found))

    def walk(
            self,
            node_id: str,
            *,
            depth: int = 2,
            direction: str = "out",
            relation: Optional[str] = None,
            origin: Optional[str] = None,
    ) -> Iterator[Tuple[int, Edge]]:
        """
        Traverse outward from a node, breadth-first.

        Purpose:
            The walk the whole asset exists for. Yields as it goes, so an agent
            can stop at the first useful hop instead of materialising a
            subgraph it will discard.

        Contract:
            Breadth-first, so shallower relationships arrive first. Every node
            is expanded at most once - the graph has cycles (`borrows` and
            `used_by` run both ways) and an unguarded walk would not terminate.
            An edge to a node outside the graph is still yielded, then not
            expanded; the relationship is real even where the target is not
            described here.

        Args:
            node_id: Node to start from.
            depth: Maximum hops. 1 is immediate neighbours.
            direction: `out`, `in`, or `both`.
            relation: Optional relation filter, applied to every hop.
            origin: Optional trust filter - `authored` or `derived`. Use it to
                walk only mechanical structure, or only authored design.

        Yields:
            Tuple[int, Edge]: Hop number, 1-based, and the edge traversed.

        Raises:
            KeyError: When the starting node is not in the graph.
            ValueError: When `depth` is below 1 or `direction` is invalid.
        """
        if depth < 1:
            raise ValueError(f"depth must be at least 1, got {depth}")
        self.node(node_id)

        seen: Dict[str, bool] = {node_id: True}
        frontier: List[str] = [node_id]
        for hop in range(1, depth + 1):
            following: List[str] = []
            for current in frontier:
                edges: List[Edge] = []
                if direction in ("out", "both"):
                    edges += list(self.edges_from(current, relation=relation))
                if direction in ("in", "both"):
                    edges += list(self.edges_to(current, relation=relation))
                elif direction not in ("out", "both"):
                    raise ValueError(
                        f"direction must be 'out', 'in' or 'both', "
                        f"got {direction!r}"
                    )
                for edge in edges:
                    if origin is not None and edge.origin != origin:
                        continue
                    yield hop, edge
                    other = edge.target if edge.source == current else edge.source
                    if other not in seen:
                        seen[other] = True
                        following.append(other)
            if not following:
                return
            frontier = following

    def impact(
            self,
            node_id: str,
            *,
            depth: int = 2,
            relation: Optional[str] = None,
            origin: Optional[str] = None,
    ) -> Tuple[Impact, ...]:
        """
        Return the FILES affected by changing a node, ranked by proximity.

        Purpose:
            "I am about to change this - what breaks?" is the most common
            reason to walk inbound, and the walk answers it in the wrong
            currency. It yields edges; a caller needs files to open. Deriving
            one from the other by hand every time is the friction this removes.

        Contract:
            Walks INBOUND - dependents, not dependencies - and collapses the
            result per defining file. `hops` carries the shortest distance
            found, so sorting puts direct dependents first; a file reached at
            hop 1 is far more likely to break than one reached at hop 3.

            Nodes outside the described graph are skipped rather than guessed
            at, so the result is only ever files this graph can actually name.

        Args:
            node_id: The node being changed.
            depth: How far to propagate. 1 is direct dependents only.
            relation: Optional relation filter.
            origin: Optional trust filter - `authored` or `derived`.

        Returns:
            Tuple[Impact, ...]: Affected files, nearest first, then by path.

        Raises:
            KeyError: When the node is not in the graph.
            ValueError: When `depth` is below 1.
        """
        table = self._graph().NODES
        nearest: Dict[str, int] = {}
        nodes: Dict[str, Dict[str, bool]] = {}
        counts: Dict[str, int] = {}
        for hop, edge in self.walk(
                node_id, depth=depth, direction="in", relation=relation, origin=origin
        ):
            dependent = edge.source
            if dependent not in table or dependent == node_id:
                continue
            path = table[dependent][0]
            if path not in nearest or hop < nearest[path]:
                nearest[path] = hop
            nodes.setdefault(path, {})[dependent] = True
            counts[path] = counts.get(path, 0) + 1

        found = [
            Impact(path, nearest[path], tuple(sorted(nodes[path])), counts[path])
            for path in nearest
        ]
        return tuple(sorted(found, key=lambda item: (item.hops, item.source)))

    def details_key(self, node_id: str) -> str:
        """
        Return the section key describing a node's defining file.

        Purpose:
            The join. A walk produces node ids; the prose is addressed by
            source path. This converts one into the other, so
            `view.get(view.details_key(node_id))` reads the description of any
            node a walk reached.

        Args:
            node_id: Fully qualified node id.

        Returns:
            str: The section key in the graph document.

        Raises:
            KeyError: When the node is not in the graph.
        """
        return self.node(node_id).source

    def describe(self, node_id: str) -> str:
        """
        Return the document section describing a node's defining file.

        Args:
            node_id: Fully qualified node id.

        Returns:
            str: The section text.

        Raises:
            KeyError: When the node or its section is absent.
            RuntimeError: When the document is unavailable.
        """
        return self.get(self.details_key(node_id))
