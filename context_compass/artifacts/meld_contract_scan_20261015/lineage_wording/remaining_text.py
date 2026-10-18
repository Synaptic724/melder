"""List every line of the given .py files where "lineage" still appears inside a string or comment (melder_1, 2026-10-18).

Read-only. Tokenizes each file and prints `path:line: text` for STRING (docstrings and other literals) and COMMENT
tokens; identifiers are not listed. Used after each hand-edit batch to confirm that only the kept occurrences remain
(scope-tree uses, parameter names in Args lines, `__slots__` names, runtime message text).

Usage: python remaining_text.py <path.py> [<path.py> ...]
"""
import io
import re
import sys
import tokenize


def main() -> None:
    """Print the remaining string/comment lines that mention lineage, per file, with a count."""
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8", newline="") as handle:
            source = handle.read().replace("\r\n", "\n")
        rows = []
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type not in (tokenize.STRING, tokenize.COMMENT):
                continue
            for offset, text in enumerate(token.string.split("\n")):
                if re.search("lineage", text, re.IGNORECASE):
                    rows.append((token.start[0] + offset, text.strip()))
        print(f"== {path}: {len(rows)}")
        for line, text in rows:
            print(f"{path}:{line}: {text}")


if __name__ == "__main__":
    main()
