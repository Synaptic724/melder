"""Line-block replacement that ignores each line's CR/LF spelling (for mixed-ending files). melder_0, 2026-09-27."""
import sys

assert sys.version_info >= (3, 14), "run with the 3.14 venv"


def replace_lines(path: str, old: str, new: str, count: int = 1) -> str:
    """Replace whole-line block `old` with `new`, matching lines without their line endings.

    Each replacement line takes the line ending of the first matched line. Returns 'applied' or
    'already applied'; raises SystemExit when the block matches a different number of times.
    """
    with open(path, "rb") as handle:
        data = handle.read().decode("utf-8")
    lines = data.splitlines(keepends=True)
    old_lines = old.split("\n")[:-1] if old.endswith("\n") else old.split("\n")
    new_lines = new.split("\n")[:-1] if new.endswith("\n") else new.split("\n")

    def find(block):
        hits = []
        for i in range(len(lines) - len(block) + 1):
            if all(lines[i + k].rstrip("\r\n") == block[k] for k in range(len(block))):
                hits.append(i)
        return hits

    matches = find(old_lines)
    if not matches and find(new_lines):
        return "already applied"
    if len(matches) != count:
        raise SystemExit(f"{path}: expected {count} match(es) of {old_lines[0]!r}, found {len(matches)}")
    for i in reversed(matches):
        eol = "\r\n" if lines[i].endswith("\r\n") else "\n"
        lines[i:i + len(old_lines)] = [line + eol for line in new_lines]
    with open(path, "wb") as handle:
        handle.write("".join(lines).encode("utf-8"))
    return "applied"
