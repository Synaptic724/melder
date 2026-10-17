"""
Edit engine for the spell_id lookup fix (fix #1 of
TASK-2026-10-16-recheck_contract_consumers_when_provider_changes).

Every edit is verified before anything is written:
- a method block is found with `ast` by its qualified name and must hash (SHA256 of its lines,
  LF-joined, plus a final LF) to the value recorded from the 0.2.8251 tree;
- every other edit is an anchor that must occur exactly once in the file's text at that point.
Line endings are preserved per file: a CRLF file is edited as LF text and written back as CRLF.
Each edited file must still parse. Nothing is written when any check fails, or with check=True.
"""
import ast
import hashlib
import pathlib
from typing import Dict, List, Tuple


class EditEngine:
    """Apply verified block and anchor edits to a tree, all or nothing."""

    def __init__(self, root: pathlib.Path, since: str) -> None:
        self.root = root
        self.since = since
        self.blocks: Dict[str, List[Tuple[str, str, str]]] = {}
        self.anchors: Dict[str, List[Tuple[str, str]]] = {}

    def block(self, rel: str, qualname: str, sha: str, new_text: str) -> None:
        self.blocks.setdefault(rel, []).append((qualname, sha, new_text))

    def anchor(self, rel: str, old: str, new: str) -> None:
        self.anchors.setdefault(rel, []).append((old, new))

    @staticmethod
    def _find_block(text: str, qualname: str) -> Tuple[int, int]:
        tree = ast.parse(text)
        nodes = tree.body
        node = None
        for part in qualname.split("."):
            found = None
            for candidate in nodes:
                if isinstance(candidate, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and candidate.name == part:
                    found = candidate
                    break
            if found is None:
                raise SystemExit(f"FAIL block not found: {qualname}")
            node = found
            nodes = found.body
        start = node.decorator_list[0].lineno if node.decorator_list else node.lineno
        return start, node.end_lineno

    def _sub(self, text: str) -> str:
        return text.replace("@@SINCE@@", self.since)

    def run(self, check: bool) -> None:
        results: Dict[str, bytes] = {}
        for rel in sorted(set(self.blocks) | set(self.anchors)):
            path = self.root / rel
            raw = path.read_bytes()
            crlf = b"\r\n" in raw
            text = raw.decode("utf-8")
            if crlf:
                text = text.replace("\r\n", "\n")
                if "\r" in text:
                    raise SystemExit(f"FAIL mixed line endings: {rel}")
            lines = text.split("\n")
            spans = []
            for qualname, sha, new_text in self.blocks.get(rel, []):
                start, end = self._find_block(text, qualname)
                block = "\n".join(lines[start - 1:end]) + "\n"
                got = hashlib.sha256(block.encode("utf-8")).hexdigest()
                if got != sha:
                    raise SystemExit(f"FAIL block hash {rel} {qualname}: {got}")
                spans.append((start, end, self._sub(new_text)))
            for start, end, new_text in sorted(spans, reverse=True):
                new_lines = new_text.rstrip("\n").split("\n")
                lines[start - 1:end] = new_lines
            text = "\n".join(lines)
            for old, new in self.anchors.get(rel, []):
                old = self._sub(old)
                count = text.count(old)
                if count != 1:
                    raise SystemExit(f"FAIL anchor count {count} in {rel}: {old[:90]!r}")
                text = text.replace(old, self._sub(new))
            if "@@SINCE@@" in text:
                raise SystemExit(f"FAIL unsubstituted placeholder in {rel}")
            ast.parse(text)
            out = text.replace("\n", "\r\n") if crlf else text
            results[rel] = out.encode("utf-8")
            print(f"ok {rel} blocks={len(spans)} anchors={len(self.anchors.get(rel, []))} crlf={crlf}")
        if check:
            print("check only: nothing written")
            return
        for rel, data in results.items():
            (self.root / rel).write_bytes(data)
        print(f"written {len(results)} files")
