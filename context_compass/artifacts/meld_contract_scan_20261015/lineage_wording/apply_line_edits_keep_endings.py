"""Apply hand-written one-for-one line edits to files with mixed line endings (melder_1, 2026-10-18).

The owner's ruling of 2026-10-18 ("Yes, keep each ending") allows editing SpellIndex lines in files whose lines mix
CRLF and LF. This variant of apply_line_edits.py takes the same EDITS module shape but only one-for-one
replacements: each edited line keeps its own terminator, and every other line keeps its bytes. It refuses an edit
whose line does not match exactly, two edits of one line, a replacement of more or fewer than one line, or a
replacement over 120 characters; it reads every file back and checks that only the edited lines changed. --check
prints the unified diff and writes nothing.

Usage (from the repository root): python apply_line_edits_keep_endings.py <edits_module.py> --check|--apply
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


def split_terminator(line: str) -> tuple:
    """Return (content, terminator) for one line kept with its ending."""
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def main() -> None:
    """Validate every edit, then print diffs (--check) or write, read back and compare (--apply)."""
    if len(sys.argv) != 3 or sys.argv[2] not in ("--check", "--apply"):
        raise SystemExit("usage: apply_line_edits_keep_endings.py <edits_module.py> --check|--apply")
    edits = load_edits(pathlib.Path(sys.argv[1]))
    by_file: dict = {}
    for path, line, old, new_lines in edits:
        by_file.setdefault(path, []).append((line, old, new_lines))
    total = 0
    for path, file_edits in by_file.items():
        file_path = pathlib.Path(path)
        text = file_path.read_bytes().decode("utf-8")
        lines = text.splitlines(keepends=True)
        updated = list(lines)
        seen = set()
        for line, old, new_lines in file_edits:
            if line in seen:
                raise SystemExit(f"{path}:{line}: edited twice - refusing")
            seen.add(line)
            if len(new_lines) != 1:
                raise SystemExit(f"{path}:{line}: only one-for-one replacements - refusing")
            if len(new_lines[0]) > 120:
                raise SystemExit(f"{path}:{line}: replacement over 120 chars - refusing: {new_lines[0]!r}")
            content, ending = split_terminator(lines[line - 1])
            if content != old:
                raise SystemExit(f"{path}:{line}: text differs - refusing\n  file: {content!r}\n  edit: {old!r}")
            updated[line - 1] = new_lines[0] + ending
        diff = difflib.unified_diff(
            [split_terminator(x)[0] for x in lines], [split_terminator(x)[0] for x in updated],
            fromfile=path, tofile=path, lineterm="", n=1,
        )
        print("\n".join(diff))
        total += len(file_edits)
        if sys.argv[2] == "--apply":
            new_text = "".join(updated)
            file_path.write_bytes(new_text.encode("utf-8"))
            back = file_path.read_bytes().decode("utf-8").splitlines(keepends=True)
            if back != updated:
                raise SystemExit(f"{path}: read-back mismatch")
            changed = [i + 1 for i, (a, b) in enumerate(zip(lines, back)) if a != b]
            if len(back) != len(lines) or sorted(changed) != sorted(seen):
                raise SystemExit(f"{path}: lines other than the edited ones changed: {changed}")
    print(f"{len(by_file)} files, {total} edits", "applied and read back" if sys.argv[2] == "--apply" else "(check only)")


if __name__ == "__main__":
    main()
