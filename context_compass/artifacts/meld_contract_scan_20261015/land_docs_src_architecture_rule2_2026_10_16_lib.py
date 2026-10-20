"""The long-line-aware exact-text apply shared by the rule-2 docs scripts (melder_1, 2026-10-16)."""
from apply_lib import one  # the lane's exact-text replacement


def apply(root, rel, steps, check_only):
    """Like apply_lib.apply, but a new line may pass 120 characters when it holds one unbreakable token
    (an EVIDENCE path citation), as the documentation standard allows; other long lines are refused."""
    path = root / rel
    raw = path.read_bytes().decode("utf-8")
    crlf = raw.count("\r\n") > 0 and raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    for a, b in steps:
        for line in b.splitlines():
            body = line.strip()
            for prefix in ("EVIDENCE:", "- "):
                if body.startswith(prefix):
                    body = body[len(prefix):].strip()
            if len(line) > 120 and len(body.split()) != 1:
                raise SystemExit(f"{rel}: new prose line longer than 120 characters ({len(line)}): {line!r}")
        text = one(text, a, b, rel)
    if not check_only:
        path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(("checked " if check_only else "applied ") + rel + (" (CRLF kept)" if crlf else ""))
