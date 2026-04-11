"""
Top-level hardcopy system document object for agent-facing Melder surfaces.
"""

import json
from typing import Optional


class StaticSystemDocument:
    """
    Purpose:
        Represent one packaged hardcopy system document object that can be
        queried directly by agents at the package root.

    Contract:
        - Stores one minified JSON hardcopy string.
        - Exposes the minified JSON directly via `render_json()`.
        - Exposes the markdown payload extracted from that JSON via
          `render_markdown()`.
        - Publishes public AST helper access and an explicit agent purpose.

    Lifecycle:
        Immutable after initialization; no cleanup contract is required.
    """

    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Top-level hardcopy system document object for Melder "
        "agent onboarding and architecture querying."
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

        Args:
            document_name:
                Stable runtime document-object name.
            document_json:
                Minified JSON hardcopy for the document.
            agent_purpose:
                Optional explicit agent-purpose string. When omitted, a public
                generic purpose is synthesized.

        Returns:
            None.

        Raises:
            ValueError:
                If the name/json is empty or the JSON payload does not expose
                string key `m`.
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

        Returns:
            str: Stable runtime document-object name.
        """
        return self._document_name

    def render_json(self) -> str:
        """
        Return the minified JSON hardcopy for this document object.

        Returns:
            str: Minified JSON document hardcopy.
        """
        return self._document_json

    def render_markdown(self) -> str:
        """
        Return the markdown payload stored inside the minified JSON hardcopy.

        Returns:
            str: Markdown payload extracted from the hardcopy JSON.
        """
        return self._document_markdown
