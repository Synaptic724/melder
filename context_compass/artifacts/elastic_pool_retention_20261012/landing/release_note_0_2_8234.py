"""
Add the 0.2.8234 entry to release_docs/next_version_release.md (CRLF), bump its header and rebuild line, and notch
src/melder/__version__.py to 0.2.8234 (keeps each file's endings).

Usage: python release_note_0_2_8234.py <repo root>
"""
import pathlib
import sys

SECTION = """## Lesser conduits and spellspaces past 20 are kept and reused, then let go when quiet

The pools behind `create_lesser_conduit()` and `enter_spellspace()` now keep what a burst needed. Each conduit's
spellspace pool and each root's lesser-conduit pool still always keep 20 idle shells; when more than 20 were out at
once, the extra shells now stay pooled when they come back (up to 256 per pool) instead of being destroyed, so the next
burst reuses them instead of building new lesser conduits and spellspaces. Once no burst has needed a new shell for 30
minutes, the pool lets the extras go a step at a time (10% every 10 minutes) until it is back to 20.

In melder_gauntlet past 20 threads the old pools rebuilt and destroyed up to 11 lesser conduits per iteration on a
2-core machine; they now build each one once. At 1 to 3 threads nothing changes (measured within noise), and returning
a shell while 20 or fewer are idle costs what it did.

`prewarm_lesser_conduits(count)` and `prewarm_spellspaces(count)` now keep up to 256 shells (they were capped at 20);
shells above 20 decay like a burst's.

For subclasses of `AbstractElasticPool`: while a miss happened within `settle_time_seconds`, a return raises the
target to the idle count it sees (up to `max_idle`); after that the target falls by `decay_percent_per_interval` of
its stretched value every `decay_interval_seconds`, with the steps of a quiet period applied at the next return, and
the oldest surplus is destroyed outside the pool lock. `stretch_percent` is now headroom over that count and defaults
to 0 (it was the growth per miss, default 200). A pool built with `max_idle == baseline_idle` behaves as before. No
signature changes, and `describe()` keeps its keys.

What stays the same: the number of live shells is never capped (a miss always builds), a returning shell is cleaned
before it is pooled, and a released spellspace still refuses `meld` and `purge`.

"""


def main() -> int:
    root = pathlib.Path(sys.argv[1])
    note = root / "release_docs/next_version_release.md"
    raw = note.read_bytes().decode("utf-8")
    assert raw.count("\r\n") == raw.count("\n")
    text = raw.replace("\r\n", "\n")
    pairs = [
        ("# Melder 0.2.8233\n", "# Melder 0.2.8234\n"),
        ("## Packaging and documentation\n", SECTION + "## Packaging and documentation\n"),
        ("- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8233.\n",
         "- The packaged system documents describe the elastic retention of the kernel pools: the sizes, the stretch\n"
         "  under pressure, the timed decay and the prewarm ceiling.\n"
         "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8234.\n"),
    ]
    for old, new in pairs:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    for line in text.split("\n"):
        assert len(line) <= 120 or line.startswith("|"), line
    note.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))

    version = root / "src/melder/__version__.py"
    vraw = version.read_bytes().decode("utf-8")
    assert vraw.count('__version__ = "0.2.8233"') == 1
    version.write_bytes(vraw.replace('__version__ = "0.2.8233"', '__version__ = "0.2.8234"').encode("utf-8"))
    print("release note and notch done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
