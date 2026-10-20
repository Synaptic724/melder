"""melder_0, 2026-10-18: the anchored, all-or-nothing source applier for S1 and S2 of
EPIC-2026-10-18-spell_identity_is_the_code.

The same edit lists apply to the /tmp working mirror (built and tested there first) and, after melder_1's hand-back of
spell.py and spellbook.py, to the repository. Every `old` text must occur exactly once in its file; a file's line
endings are kept (structural_snapshot.py is CRLF in the working tree); new modules are copied from the staged folder.
Nothing is written unless every edit of every file matched.
"""
import pathlib
import shutil
import sys
from typing import Dict, List, Tuple


class Applier:
    """Stage edits per file, then write them all or none."""

    STAGED = pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/staged"

    def __init__(self, root: pathlib.Path, backup: pathlib.Path) -> None:
        self.root = root
        self.backup = backup
        self.texts: Dict[str, str] = {}
        self.newline: Dict[str, str] = {}
        self.copies: List[str] = []
        self.counts: Dict[str, int] = {}
        self.errors: List[str] = []
        self.originals: Dict[str, str] = {}
        # Files whose working-tree copy mixes CRLF and LF lines (an earlier writer's LF lines in a CRLF file): the
        # caller names the ending to write them with, else a mixed file is refused.
        self.normalize_mixed: Dict[str, str] = {}

    def _load(self, rel: str) -> str:
        if rel not in self.texts:
            raw = (self.root / rel).read_bytes().decode("utf-8")
            self.newline[rel] = "\r\n" if "\r\n" in raw else "\n"
            if self.newline[rel] == "\r\n" and raw.count("\r\n") != raw.count("\n"):
                if rel in self.normalize_mixed:
                    self.newline[rel] = self.normalize_mixed[rel]
                    print(f"mixed line endings in {rel}: written with {self.newline[rel]!r}")
                else:
                    self.errors.append(f"MIXED line endings in {rel}")
            self.texts[rel] = raw.replace("\r\n", "\n")
            self.originals[rel] = self.texts[rel]
        return self.texts[rel]

    def edit(self, rel: str, pairs: List[Tuple[str, str]], label: str) -> None:
        """Replace each `old` (exactly once) by `new` in one file, in order."""
        text = self._load(rel)
        for index, (old, new) in enumerate(pairs):
            count = text.count(old)
            if count != 1:
                self.errors.append(f"ANCHOR {label}#{index} in {rel}: found {count}: {old[:70]!r}")
                continue
            text = text.replace(old, new)
            self.counts[rel] = self.counts.get(rel, 0) + 1
        self.texts[rel] = text

    def cut(self, rel: str, start: str, end: str, replacement: str, label: str) -> None:
        """Replace the text from `start` (exactly once) up to, not including, `end` (exactly once, after it)."""
        text = self._load(rel)
        if text.count(start) != 1 or text.count(end) != 1:
            self.errors.append(f"CUT {label} in {rel}: start {text.count(start)}, end {text.count(end)}")
            return
        begin = text.index(start)
        finish = text.index(end)
        if finish <= begin:
            self.errors.append(f"CUT {label} in {rel}: end before start")
            return
        removed = text[begin:finish].count("\n")
        self.texts[rel] = text[:begin] + replacement + text[finish:]
        self.counts[rel] = self.counts.get(rel, 0) + 1
        print(f"cut {label}: {removed} line(s) from {rel}")

    def copy(self, rel: str) -> None:
        """Copy a new module from the staged folder to the same relative path under the root."""
        if not (self.STAGED / rel).exists():
            self.errors.append(f"STAGED missing: {rel}")
        self.copies.append(rel)

    def commit(self, check: bool) -> None:
        """Write everything, or report and exit without writing when an edit failed or `check` is set."""
        for rel, text in self.texts.items():
            before = set(self.originals[rel].split("\n"))
            for number, line in enumerate(text.split("\n"), 1):
                if len(line) > 120 and line not in before:
                    self.errors.append(f"WIDTH {rel}:{number}: {len(line)}")
        if self.errors:
            print("\n".join(self.errors))
            sys.exit(f"{len(self.errors)} problem(s); nothing written")
        for rel in sorted(self.texts):
            print(f"{'would edit' if check else 'edit'} {rel}: {self.counts.get(rel, 0)} replacement(s)")
        for rel in self.copies:
            print(f"{'would copy' if check else 'copy'} {rel}")
        if check:
            return
        self.backup.mkdir(parents=True, exist_ok=True)
        for rel, text in self.texts.items():
            path = self.root / rel
            shutil.copy2(path, self.backup / (rel.replace("/", "__") + ".pre"))
            path.write_bytes(text.replace("\n", self.newline[rel]).encode("utf-8"))
        for rel in self.copies:
            shutil.copy2(self.STAGED / rel, self.root / rel)
        print("written")
