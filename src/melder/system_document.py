"""
Top-level hardcopy system document object for agent-facing Melder surfaces.
"""

import json
from typing import ClassVar
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only, never imported at runtime
    from melder.utilities.ai_native_support_tools.agent_text_reader import (
        AgentTextReader,
        IndexedText,
        TextChunk,
    )



class StaticSystemDocument:
    """

    Purpose:
        Represent one packaged hardcopy system document object that can be
        queried directly by agents at the package root.

    Responsibilities:
        - Carry one minified JSON hardcopy string for one named document.
        - Validate at construction that the hardcopy exposes the markdown
          payload key `m`.
        - Expose the raw hardcopy through `render_json()` and the extracted
          markdown through `render_markdown()`.
        - Publish an explicit agent-purpose string and AST helper access level.

    Contract:
        - Stores one minified JSON hardcopy string.
        - Exposes the minified JSON directly via `render_json()`.
        - Exposes the markdown payload extracted from that JSON via
          `render_markdown()`.
        - Publishes public AST helper access and an explicit agent purpose.
        - Construction is total: an instance either validates and exists, or
          `__init__` raises. There is no partially-built state.

    Owned State:
        - `_document_name`: stable runtime document-object name.
        - `_document_json`: the original minified JSON hardcopy.
        - `_document_markdown`: the markdown payload extracted from that JSON.

    Threading:
        Immutable after construction and therefore safe to share across threads
        without synchronization. No locks are held or required. This matters on
        free-threaded builds, where these objects are read concurrently by any
        agent that imports the package.

    Lifecycle / Cleanup:
        Import-time object with no cleanup contract. Instances are created at
        module import by the packaged hardcopy modules and live for the process
        lifetime. Deliberately NOT `Cleanable`: there is nothing to release, and
        subclassing the cleanup base would add a teardown contract this carrier
        does not need.

    Registration:
        MELDER KERNEL. Melder constructs these objects itself at import; asking Melder
        to inject one is a category error.

    Subsystem Context:
        This is the carrier type for the package-root document surfaces. Four
        module-level instances are built from it - `__architecture__`,
        `__components__`, `__graph_network__`, and `__graph_details__` - and
        those four modules are its only constructors. It has no siblings and
        hands off to nothing; it is a terminal value object that the package
        root publishes.

    System Context:
        Sits entirely outside the runtime graph and before it in time. These
        documents answer at import, ahead of the `Aether()` substrate boot, and
        are queryable WITHOUT conjuring a conduit - which is the entire point:
        an agent orients itself on system structure before it has a Spellbook, a
        Conduit, or any live object world. Nothing here participates in binding,
        resolution, or cleanup.

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. Immutable packaged hardcopy of a system document. Read
        `melder.__architecture__`, `__components__`, `__graph_network__`, `__graph_details__` to
        orient inside the runtime without leaving the process.
    """

    __slots__ = [
        "_document_name",
        "_document_json",
        "_document_markdown",
        "_indexed",
    ]

    def __init__(
            self,
            *,
            document_name: str,
            document_json: str,
            agent_purpose: Optional[str] = None,
    ) -> None:
        """
        Initialize one top-level hardcopy system document object.

        Contract:
            - Validates that the JSON hardcopy contains the markdown payload
              key `m`.
            - Stores only the stable document name, original minified JSON, and
              extracted markdown string.
            - Accepts `agent_purpose` for forward-compatibility with the
              packaged document modules, but this first cut does not persist it
              on the instance because agent-purpose stays class-level here.
            - Validation happens before any field is assigned, so a raising
              construction leaves no partially-populated instance behind.

        Args:
            document_name:
                Stable runtime document-object name. Must be non-empty.
            document_json:
                Minified JSON hardcopy for the document. Must be non-empty and
                must parse to an object exposing string key `m`.
            agent_purpose:
                Optional explicit agent-purpose string. Currently accepted and
                discarded; see the class `Registration` notes and the owning
                story for the open decision on persisting it per instance.

        Returns:
            None.

        Raises:
            ValueError:
                If the name/json is empty or the JSON payload does not expose
                string key `m`.
            json.JSONDecodeError:
                If `document_json` is not parseable JSON. Propagated unwrapped
                from `json.loads` so the caller sees the exact parse position.

        Threading:
            No shared state is touched; construction is independent per
            instance.
        """
        if not document_name:
            raise ValueError("document_name cannot be empty.")
        if not document_json:
            raise ValueError("document_json cannot be empty.")
        parsed_document = json.loads(document_json)
        markdown_text = parsed_document.get("m")
        if not isinstance(markdown_text, str):
            raise ValueError("document_json must contain string key 'm'.")
        self._document_name = document_name
        self._document_json = document_json
        self._document_markdown = markdown_text
        # Built on FIRST bounded read, never at construction. These four
        # documents are imported by `melder/__init__.py` at package scope, so
        # anything done here is paid by every `import melder` - including by the
        # majority of processes that never ask a document anything. Indexing is
        # cheap but not free, and the payloads are the largest things melder
        # ships, so the cost is deferred to the first caller who wants paging.
        self._indexed: Optional["IndexedText"] = None
        _ = agent_purpose

    @classmethod
    def from_markdown(
            cls,
            *,
            document_name: str,
            markdown_text: str,
            agent_purpose: Optional[str] = None,
    ) -> "StaticSystemDocument":
        """
        Build a document from markdown that is already a string.

        Purpose:
            The build asset emits document text as a Python string literal, so
            it arrives already parsed by the interpreter. Re-wrapping 1.6 MB of
            markdown in a JSON envelope only to `json.loads` it back out would
            be a megabyte-scale round trip to learn something already known.

        Contract:
            Same total-construction guarantee as `__init__` - validates before
            assigning, so a raising call leaves no half-built instance. The JSON
            envelope is still synthesised lazily by `render_json()` for callers
            that want it; nobody pays for it who does not ask.

        Args:
            document_name: Stable runtime document-object name, non-empty.
            markdown_text: The document text. May be empty for a document that
                did not ship, which is a real state, not a failure.
            agent_purpose: Accepted for symmetry; not persisted.

        Returns:
            StaticSystemDocument: The constructed document.

        Raises:
            ValueError: If `document_name` is empty or `markdown_text` is not
                a string.
        """
        if not document_name:
            raise ValueError("document_name cannot be empty.")
        if not isinstance(markdown_text, str):
            raise ValueError("markdown_text must be a string.")
        built = cls.__new__(cls)
        built._document_name = document_name
        built._document_json = ""
        built._document_markdown = markdown_text
        built._indexed = None
        _ = agent_purpose
        return built

    @property
    def document_name(self) -> str:
        """
        Return the stable runtime document-object name.

        Contract:
            Never empty; validated non-empty at construction and immutable
            thereafter.

        Returns:
            str: Stable runtime document-object name.
        """
        return self._document_name

    def render_json(self) -> str:
        """
        Return the minified JSON hardcopy for this document object.

        Purpose:
            Give an agent the raw packaged payload when it wants to parse
            structure rather than read prose.

        Contract:
            Returns the exact string supplied at construction; no re-encoding,
            no reformatting. Guaranteed parseable, since construction already
            parsed it once.

        Returns:
            str: Minified JSON document hardcopy.
        """
        if not self._document_json:
            self._document_json = json.dumps(
                {"m": self._document_markdown}, separators=(",", ":")
            )
        return self._document_json

    def render_markdown(self) -> str:
        """
        Return the markdown payload stored inside the minified JSON hardcopy.

        Purpose:
            Give an agent the human/agent-readable document body directly,
            without requiring it to know the hardcopy envelope shape.

        Contract:
            Returns the value of key `m`, extracted and validated as a string at
            construction. May be a placeholder string for documents whose
            hardcopy has not yet been populated.

        Returns:
            str: Markdown payload extracted from the hardcopy JSON.
        """
        return self._document_markdown

    def _indexed_text(self) -> "IndexedText":
        """
        Return this document's line index, building it on first use.

        Contract:
            Import is INSIDE the method for the same reason the index is lazy:
            `melder/__init__.py` imports all four documents at package scope, so
            a module-scope import here would put the reader on the boot path of
            every process.

            Not locked. Two threads racing first access both build an index over
            the same immutable string and assign equivalent objects, so the race
            is benign and a lock would add contention to a path that settles
            after one call.

        Returns:
            IndexedText: The shared, immutable index over this document.
        """
        if self._indexed is None:
            from melder.utilities.ai_native_support_tools.agent_text_reader import (
                IndexedText,
            )

            self._indexed = IndexedText(self._document_markdown)
        return self._indexed

    @property
    def line_count(self) -> int:
        """
        Return the document's line count.

        Purpose:
            Let an agent size a read BEFORE committing any context to it.

        Returns:
            int: Total lines in the markdown payload.
        """
        return self._indexed_text().line_count

    @property
    def char_count(self) -> int:
        """
        Return the document's character count.

        Returns:
            int: Total characters in the markdown payload.
        """
        return self._indexed_text().char_count

    def reader(
            self,
            *,
            line_target: int = 50,
            char_target: int = 8_192,
    ) -> "AgentTextReader":
        """
        Return a private, resumable cursor over this document.

        Purpose:
            THE intended way to consume a system document. `render_markdown()`
            hands back the entire payload in one call, which for a populated
            document is the whole point of failure - this returns exactly the
            budget the caller asked for and reports whether more remains.

        Contract:
            Each caller gets its OWN cursor; the indexed document behind it is
            shared and never copied, so many agents may read one document
            concurrently without a lock. Budgets are validated against
            `ReaderPolicy` - `line_target` must be 2-100.

        Args:
            line_target: Lines per read.
            char_target: Characters per read; whichever budget binds first wins.

        Returns:
            AgentTextReader: A cursor owned solely by the caller.

        Raises:
            ValueError: If either budget is outside its documented bounds.
        """
        return self._indexed_text().reader(
            line_target=line_target, char_target=char_target
        )

    def head(self, lines: int = 50, *, chars: Optional[int] = None) -> "TextChunk":
        """
        Return the opening lines of this document.

        Purpose:
            The cheapest orientation available: read the top of the architecture
            document to learn what it covers before deciding to page the rest.

        Args:
            lines: How many leading lines (2-100).
            chars: Optional character cap.

        Returns:
            TextChunk: The leading span, with `has_more` set when more remains.
        """
        return self._indexed_text().head(lines, chars=chars)

    def tail(self, lines: int = 50, *, chars: Optional[int] = None) -> "TextChunk":
        """
        Return the closing lines of this document.

        Args:
            lines: How many trailing lines (2-100).
            chars: Optional character cap.

        Returns:
            TextChunk: The trailing span.
        """
        return self._indexed_text().tail(lines, chars=chars)

    def lines(self, start: int, count: int) -> str:
        """
        Return a contiguous run of lines by index.

        Contract:
            Clamps at the end rather than raising, so reading past the last line
            returns what exists. Random access for a caller that already knows
            where it wants to look.

        Args:
            start: Zero-based first line, inclusive.
            count: How many lines.

        Returns:
            str: The requested lines.
        """
        return self._indexed_text().lines_text(start, count)
