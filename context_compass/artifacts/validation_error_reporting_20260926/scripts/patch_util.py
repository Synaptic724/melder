"""Exact, line-normalized block replacement shared by the September-plan apply scripts.

Each old block must match the stated number of times (ignoring CR). Replaced lines keep the
dominant line ending of the block they replace, so mixed CRLF/LF files keep their endings.
"""
import pathlib
from collections import Counter


def replace_block(path: pathlib.Path, old: str, new: str, count: int = 1) -> None:
    """Replace `count` exact occurrences of the line block `old` with `new` in `path`."""
    raw = path.read_bytes().decode("utf-8")
    lines = raw.splitlines(keepends=True)
    norm = [line.rstrip("\r\n") for line in lines]
    old_lines = old.split("\n")
    n = len(old_lines)
    hits = [i for i in range(len(norm) - n + 1) if norm[i:i + n] == old_lines]
    if len(hits) != count:
        raise SystemExit(f"{path}: expected {count} match(es), found {len(hits)}:\n{old_lines[0]}")
    for i in reversed(hits):
        endings = Counter(lines[j][len(norm[j]):] for j in range(i, i + n))
        ending = endings.most_common(1)[0][0] or "\n"
        last_ending = lines[i + n - 1][len(norm[i + n - 1]):]
        new_lines = [text + ending for text in new.split("\n")]
        new_lines[-1] = new.split("\n")[-1] + last_ending
        lines[i:i + n] = new_lines
    path.write_bytes("".join(lines).encode("utf-8"))
    print(f"patched {path.name} ({count})")


def append_block(path: pathlib.Path, text: str) -> None:
    """Append `text` (LF-authored) to `path` using the file's dominant line ending."""
    raw = path.read_bytes().decode("utf-8")
    crlf = raw.count("\r\n")
    ending = "\r\n" if crlf > raw.count("\n") - crlf else "\n"
    if not raw.endswith(("\n", "\r\n")):
        raw += ending
    raw += text.replace("\n", ending)
    path.write_bytes(raw.encode("utf-8"))
    print(f"appended {path.name}")


def create_file(path: pathlib.Path, text: str) -> None:
    """Create a new LF file; refuse to overwrite an existing one."""
    if path.exists():
        raise SystemExit(f"{path} already exists")
    path.write_bytes(text.encode("utf-8"))
    print(f"created {path.name}")
