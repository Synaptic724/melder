"""Line-ending-preserving block replacement for the aether_conduit_lookup_api lane (melder_0)."""


def replace_block(path: str, old: str, new: str, count: int = 1) -> str:
    """Replace `old` with `new` in `path`, matching CRLF first, then LF; write the file back in bytes.

    The replacement uses the same line ending as the matched block, so a CRLF file stays CRLF and a
    mixed file keeps its existing endings outside the block. Raises SystemExit when the block is absent
    or matches a number of times other than `count`.
    """
    with open(path, "rb") as handle:
        data = handle.read().decode("utf-8")
    for eol in ("\r\n", "\n"):
        if new.replace("\n", eol) in data and new.replace("\n", eol) != old.replace("\n", eol):
            return "already applied"
    for eol in ("\r\n", "\n"):
        old_eol = old.replace("\n", eol)
        new_eol = new.replace("\n", eol)
        found = data.count(old_eol)
        if found:
            if found != count:
                raise SystemExit(f"{path}: expected {count} match(es), found {found}")
            data = data.replace(old_eol, new_eol)
            with open(path, "wb") as handle:
                handle.write(data.encode("utf-8"))
            return "CRLF" if eol == "\r\n" else "LF"
    raise SystemExit(f"{path}: block not found")
