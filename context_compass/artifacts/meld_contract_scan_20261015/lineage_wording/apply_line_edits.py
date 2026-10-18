"""Apply hand-written line edits to repository files, safely (melder_1, 2026-10-18).

Every edit is written by hand in an edits module (EDITS = [(path, line, old, new_lines), ...]): `old` is the exact
current text of that line (no line ending) and `new_lines` the hand-written replacement lines. Nothing is searched or
swapped: each edit names its own file, line and text. The script refuses a file with mixed line endings, an edit
whose line does not match exactly, two edits of one line, or a replacement line over 120 characters; it keeps each
file's line ending, applies bottom-up so line numbers stay valid, and reads every file back. --check prints the
unified diff and writes nothing.

Usage (from the repository root): python apply_line_edits.py <edits_module.py> --check|--apply
"""
import difflib
import importlib.util
import pathlib
import sys


def load_edits(module_path: pathlib.Path) -> list:
    """Import the edits module and return its EDITS list (no bytecode is written beside it)."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("edits_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.EDITS


def ending_of(raw: bytes, path: str) -> str:
    """Return the file's line ending, refusing a file that mixes CRLF and LF."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    if crlf == 0:
        return "\n"
    if crlf == lf:
        return "\r\n"
    raise SystemExit(f"{path}: mixed line endings ({crlf} CRLF of {lf}) - refusing")


def main() -> None:
    """Validate every edit, then print diffs (--check) or write and read back (--apply)."""
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit("usage: apply_line_edits.py <edits_module.py> --check|--apply")
    edits = load_edits(pathlib.Path(sys.argv[1]))
    by_file: dict = {}
    for path, line, old, new_lines in edits:
        by_file.setdefault(path, []).append((line, old, new_lines))
    total = 0
    for path, file_edits in by_file.items():
        file_path = pathlib.Path(path)
        raw = file_path.read_bytes()
        ending = ending_of(raw, path)
        text = raw.decode("utf-8")
        lines = text.split(ending)
        seen = set()
        for line, old, new_lines in file_edits:
            if line in seen:
                raise SystemExit(f"{path}:{line}: edited twice - refusing")
            seen.add(line)
            if lines[line - 1] != old:
                raise SystemExit(f"{path}:{line}: text differs - refusing\n  file: {lines[line - 1]!r}\n  edit: {old!r}")
            for new_line in new_lines:
                if len(new_line) > 120:
                    raise SystemExit(f"{path}:{line}: replacement over 120 chars - refusing: {new_line!r}")
        updated = list(lines)
        for line, old, new_lines in sorted(file_edits, key=lambda item: -item[0]):
            updated[line - 1:line] = list(new_lines)
        new_text = ending.join(updated)
        diff = difflib.unified_diff(lines, updated, fromfile=path, tofile=path, lineterm="", n=1)
        print("\n".join(diff))
        total += len(file_edits)
        if sys.argv[2] == "--apply":
            file_path.write_bytes(new_text.encode("utf-8"))
            if file_path.read_bytes() != new_text.encode("utf-8"):
                raise SystemExit(f"{path}: read-back mismatch")
    print(f"{len(by_file)} files, {total} edits", "applied and read back" if sys.argv[2] == "--apply" else "(check only)")


if __name__ == "__main__":
    main()
