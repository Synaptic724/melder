"""melder_0, 2026-10-18: shared helpers for S1 and S2's system-document passes (code-map remeasure, wrapped text).

`DocsRecord` is a `cc_record.Record` whose code-map helper re-measures an entry from the repository's file (its
`end_line` and `loc` by `splitlines()`, `verified_at` now) and appends a note, wrapped within 120 characters.
"""
import pathlib
import re
import sys
import textwrap
from typing import List, Optional

from cc_record import Record


class DocsRecord(Record):
    """A staged pass over system documents."""

    ARCH = "system_docs/src_architecture.md"
    COMP = "system_docs/src_components.md"
    TESTS_ARCH = "system_docs/tests_architecture.md"
    TESTS_COMP = "system_docs/tests_components.md"

    @staticmethod
    def check_width(block: str, label: str) -> None:
        """`Record.check_width`, but a line holding one unbreakable token (a long path) may pass 120 characters."""
        for line in block.split("\n"):
            if len(line) > 120 and " " in line.strip() and "context_compass/" not in line \
                    and not line.startswith("| ") and not line.startswith("|---"):
                sys.exit(f"WIDTH {label}: {len(line)}: {line}")

    @classmethod
    def line_count(cls, path: str) -> int:
        return len((cls.REPO / path).read_bytes().decode("utf-8").splitlines())

    @staticmethod
    def wrap(text: str, first: str, rest: str) -> str:
        """Wrap prose to 116 characters a line: `first` prefixes the first line, `rest` the others."""
        lines = textwrap.wrap(text, width=116 - len(rest), break_long_words=False, break_on_hyphens=False)
        out = [first + lines[0]] + [rest + line for line in lines[1:]]
        for line in out:
            if len(line) > 120 and "src/" not in line:
                sys.exit(f"WRAP too long: {line}")
        return "\n".join(out)

    def remeasure(self, rel: str, path: str, note: Optional[str], count: Optional[int] = None) -> bool:
        """
        Re-measure the code-map entry of `path` in `rel` (False when the document has none) and append `note`.

        `count` replaces the measured line count when the file on disk is not yet the landed one (a generated asset
        the last-step rebuild rewrites).
        """
        text = self.read(rel)
        head = f"- path: `{path}`\n"
        if text.count(head) == 0:
            return False
        if text.count(head) != 1:
            sys.exit(f"ENTRY {path} in {rel}: {text.count(head)}")
        start = text.index(head)
        lines = text[start:].split("\n")
        end = 1
        while end < len(lines) and lines[end].startswith("  "):
            end += 1
        block = lines[:end]
        if count is None:
            count = self.line_count(path)
        for index, line in enumerate(block):
            if line.startswith("  end_line: "):
                block[index] = f"  end_line: {count}"
            elif line.startswith("  loc: "):
                block[index] = f"  loc: {count}"
            elif line.startswith("  verified_at: "):
                block[index] = f"  verified_at: {self.now}"
        if note:
            note_rows = [i for i, line in enumerate(block) if line.startswith("  note: ")]
            if note_rows:
                last = len(block) - 1
                joined = block[last] + " " + note
                if len(joined) <= 118:
                    block[last] = joined
                else:
                    block.append(self.wrap(note, "    ", "    "))
            else:
                block.append(self.wrap(note, "  note: ", "    "))
        new_text = text[:start] + "\n".join(block + lines[end:])
        self.stage(rel, new_text)
        return True

    def add_entry_after(self, rel: str, after_path: str, path: str, note: str) -> None:
        """Insert a measured code-map entry for `path` right after the entry of `after_path`."""
        text = self.read(rel)
        head = f"- path: `{after_path}`\n"
        if text.count(head) != 1:
            sys.exit(f"ANCHOR ENTRY {after_path} in {rel}: {text.count(head)}")
        if f"- path: `{path}`\n" in text:
            sys.exit(f"ENTRY EXISTS {path} in {rel}")
        start = text.index(head)
        lines = text[start:].split("\n")
        end = 1
        while end < len(lines) and lines[end].startswith("  "):
            end += 1
        count = self.line_count(path)
        entry = [f"- path: `{path}`", "  start_line: 1", f"  end_line: {count}", f"  loc: {count}",
                 f"  verified_at: {self.now}", self.wrap(note, "  note: ", "    ")]
        self.stage(rel, text[:start] + "\n".join(lines[:end] + entry + lines[end:]))
