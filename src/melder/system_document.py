"""
Top-level hardcopy system document object for agent-facing Melder surfaces.
"""

import json
from typing import ClassVar
from typing import Optional



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
        MELDER KERNEL - carries the registration guard sentinel and therefore
        cannot be registered as a spell through `Spellbook.bind(...)`. Melder
        constructs these objects itself at import; asking Melder to inject one
        is a category error. Note this class is a leaf, not a base, so tagging it
        cannot propagate to user classes through the MRO.

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
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Immutable packaged hardcopy of a system document. Read "
        "`melder.__architecture__`, `__components__`, `__graph_network__`, `__graph_details__` to "
        "orient inside the runtime without leaving the process."
    )
    __slots__ = [
        "_document_name",
        "_document_json",
        "_document_markdown",
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
        _ = agent_purpose

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
