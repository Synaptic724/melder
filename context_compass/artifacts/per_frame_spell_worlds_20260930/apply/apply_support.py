"""
Byte-faithful edit helpers for the per_frame_spell_worlds lane's apply scripts.

The repository mixes CRLF and LF files (and a few files mix both). Every edit is written in LF form here and applied
in the line-ending style of the block it replaces, so untouched lines keep their bytes. An anchor must match exactly
once; anything else aborts before a byte is written.
"""
import difflib
import pathlib
from typing import Dict, List


class ApplySession:
    """Collect edits for one tree, verify every anchor, then write all files at once."""

    def __init__(self, root: str) -> None:
        """Bind the session to one repository root (the device tree or the VM mirror)."""
        self.root: pathlib.Path = pathlib.Path(root)
        self.texts: Dict[str, str] = {}
        self.originals: Dict[str, str] = {}
        self.created: List[str] = []

    def _load(self, relative: str) -> str:
        """Return the current (possibly already edited) text of one file."""
        if relative not in self.texts:
            self.texts[relative] = (self.root / relative).read_bytes().decode("utf-8")
            self.originals[relative] = self.texts[relative]
        return self.texts[relative]

    @staticmethod
    def _variants(block: str) -> List[str]:
        """Return the CRLF and LF spellings of one LF-written block."""
        crlf = block.replace("\n", "\r\n")
        return [crlf, block] if crlf != block else [block]

    def replace(self, relative: str, old: str, new: str) -> None:
        """Replace one LF-written block, matching and writing in the file's own style at that spot."""
        text = self._load(relative)
        for variant in self._variants(old):
            count = text.count(variant)
            if count == 1:
                replacement = new.replace("\n", "\r\n") if "\r\n" in variant else new
                self.texts[relative] = text.replace(variant, replacement, 1)
                return
            if count > 1:
                raise AssertionError(f"{relative}: anchor matches {count} times")
        raise AssertionError(f"{relative}: anchor not found: {old[:120]!r}")

    def insert_after(self, relative: str, anchor: str, addition: str) -> None:
        """Insert an LF-written block right after one anchor."""
        self.replace(relative, anchor, anchor + addition)

    def insert_before(self, relative: str, anchor: str, addition: str) -> None:
        """Insert an LF-written block right before one anchor."""
        self.replace(relative, anchor, addition + anchor)

    def append(self, relative: str, addition: str) -> None:
        """Append an LF-written block at the end of one file, in CRLF when the file already ends in CRLF."""
        text = self._load(relative)
        if not text.endswith("\n"):
            raise AssertionError(f"{relative}: does not end with a newline")
        block = addition.replace("\n", "\r\n") if text.endswith("\r\n") else addition
        self.texts[relative] = text + block

    def long_added_lines(self, limit: int = 120) -> List[str]:
        """Return every added line longer than `limit` (unbreakable single-token lines excepted)."""
        found: List[str] = []
        for relative, text in self.texts.items():
            before = self.originals.get(relative, "").replace("\r\n", "\n").split("\n")
            after = text.replace("\r\n", "\n").split("\n")
            for line in difflib.unified_diff(before, after, n=0, lineterm=""):
                if not line.startswith("+") or line.startswith("+++"):
                    continue
                body = line[1:]
                if len(body) > limit and len(body.split()) > 1:
                    found.append(f"{relative}: {len(body)}: {body[:80]}")
        return found

    def create(self, relative: str, text: str) -> None:
        """Stage a NEW file (LF); refuses to overwrite an existing path."""
        if (self.root / relative).exists() or relative in self.texts:
            raise AssertionError(f"{relative}: already exists")
        self.texts[relative] = text
        self.created.append(relative)

    def write(self) -> List[str]:
        """Write every staged file; return the relative paths written."""
        for relative, text in self.texts.items():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(text.encode("utf-8"))
        return sorted(self.texts)
