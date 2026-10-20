"""melder_0, 2026-10-18: remap the system documents' numeric citations into the files S1 and S2 changed.

For each `src/melder/<file>:<lines>` citation outside a document's `## Context / Handoff Summary` (history stays as
written), every line number is mapped from the pristine 0.2.8256 file to the landed one through difflib's opcodes: a
line in an unchanged block maps exactly; a line in a changed or deleted block is FLAGGED, left as it is, and reported
for a hand edit. All or nothing: `--write` writes only when nothing is flagged, unless `--allow-flagged` is given.

    python3 remap_s1s2_citations.py --old /tmp/m0_mq/bench_before [--write] [--allow-flagged]
"""
import argparse
import difflib
import pathlib
import re
import sys
from typing import Dict, List, Optional, Tuple

REPO = pathlib.Path.home() / "mnt/melder_private"
DOCS = ("src_architecture.md", "src_components.md", "tests_architecture.md", "tests_components.md")


class Remapper:
    """Map cited line numbers of changed files from the old tree to the repository's."""

    CITE = re.compile(r"(src/melder/[\w/]+\.py):(\d+(?:\s*-\s*\d+)?(?:,\s*\d+(?:\s*-\s*\d+)?)*)")

    def __init__(self, old_root: pathlib.Path) -> None:
        self.old_root = old_root
        self.maps: Dict[str, Optional[List[Optional[int]]]] = {}
        self.flags: List[str] = []
        self.changes: List[str] = []

    def line_map(self, path: str) -> Optional[List[Optional[int]]]:
        """Old line (1-based index) -> new line, or None inside a changed block; None when the file is unchanged."""
        if path in self.maps:
            return self.maps[path]
        old_file = self.old_root / path
        new_file = REPO / path
        if not old_file.exists() or not new_file.exists():
            self.maps[path] = None
            return None
        old = old_file.read_bytes().decode("utf-8").splitlines()
        new = new_file.read_bytes().decode("utf-8").splitlines()
        if old == new:
            self.maps[path] = None
            return None
        mapping: List[Optional[int]] = [None] * (len(old) + 1)
        for tag, i1, i2, j1, _j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
            if tag == "equal":
                for offset in range(i2 - i1):
                    mapping[i1 + offset + 1] = j1 + offset + 1
        self.maps[path] = mapping
        return mapping

    def remap_spec(self, path: str, spec: str, where: str) -> str:
        mapping = self.line_map(path)
        if mapping is None:
            return spec

        def one(number: str) -> str:
            value = int(number)
            mapped = mapping[value] if value < len(mapping) else None
            if mapped is None:
                self.flags.append(f"{where}: {path}:{spec} - line {value} is in a changed block")
                return number
            return str(mapped)

        return re.sub(r"\d+", lambda m: one(m.group(0)), spec)

    def remap_doc(self, name: str) -> Tuple[str, str]:
        path = REPO / "context_compass/system_docs" / name
        text = path.read_bytes().decode("utf-8")
        head, marker, tail = text.partition("\n## Context / Handoff Summary\n")
        lines = head.split("\n")
        for index, line in enumerate(lines):
            def replace(match: "re.Match[str]") -> str:
                new_spec = self.remap_spec(match.group(1), match.group(2), f"{name}:{index + 1}")
                if new_spec != match.group(2):
                    self.changes.append(f"{name}:{index + 1}: {match.group(1)}:{match.group(2)} -> {new_spec}")
                return match.group(1) + ":" + new_spec
            lines[index] = self.CITE.sub(replace, line)
        return text, "\n".join(lines) + marker + tail


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-flagged", action="store_true")
    args = parser.parse_args()
    remapper = Remapper(pathlib.Path(args.old))
    results = {name: remapper.remap_doc(name) for name in DOCS}
    print("\n".join(remapper.changes) or "no change")
    print("FLAGGED:\n" + "\n".join(remapper.flags) if remapper.flags else "FLAGGED: none")
    if not args.write:
        return
    if remapper.flags and not args.allow_flagged:
        sys.exit("flagged citations; nothing written")
    for name, (old_text, new_text) in results.items():
        if old_text != new_text:
            (REPO / "context_compass/system_docs" / name).write_bytes(new_text.encode("utf-8"))
            print("wrote", name)


if __name__ == "__main__":
    main()
