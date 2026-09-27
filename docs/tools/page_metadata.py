"""Validate editorial descriptions and serialize generated MyST metadata safely.

The formatter owns no resources or shared state. Authored pages keep their own
frontmatter; generated chapters and lessons use these helpers before their body.
"""

import json


class PageMetadata:
    """Provide pure description validation and one-owner MyST frontmatter rendering."""

    @staticmethod
    def description(value: object, owner: str) -> str:
        """Return normalized editorial text, or an empty string for absent metadata.

        Supplied values must be nonempty strings. A malformed value raises
        ValueError naming its owning chapter or lesson before generation writes.
        Whitespace is folded for a single readable HTML description.
        """
        if value is None:
            return ""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Description for {owner} must be a nonempty string when supplied.")
        return " ".join(value.split())

    @staticmethod
    def frontmatter(description: str) -> str:
        """Render one description block, or no block for an absent description.

        The argument is normalized text from description(). JSON string quoting
        is valid YAML and keeps quotes, punctuation and control characters from
        becoming metadata syntax. The caller appends its unchanged page body.
        """
        if not description:
            return ""
        value = json.dumps(description, ensure_ascii=False)
        return f"---\nmyst:\n  html_meta:\n    description: {value}\n---\n\n"
