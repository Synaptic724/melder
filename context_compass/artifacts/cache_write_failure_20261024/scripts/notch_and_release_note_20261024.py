"""Notch to 0.2.8266 and add the release-note entry (melder_0, 2026-10-24; F5).

Reads `__version__` at this moment and refuses anything but 0.2.8265 (another landing first would move this
lane's version everywhere it is written). The release note gets its header, one `##` section before
`## Packaging and documentation`, a packaging bullet before the rebuild line, and the rebuild line's version.
All-or-nothing: anchors match once, lines fit 120 characters, no CR, and a file that changed since it was read
refuses the pass. Usage: notch_and_release_note_20261024.py --check | --apply
"""
import pathlib
import sys

ROOT = pathlib.Path.home() / "mnt/melder_private"
VERSION = ROOT / "src/melder/__version__.py"
NOTE = ROOT / "release_docs/next_version_release.md"
OLD, NEW = "0.2.8265", "0.2.8266"

SECTION = """\
## A cache file that cannot be saved no longer fails a meld

Melder keeps each root conduit's compiled creation plans in a cache file (`<conduit>.meldercache`, in the package's
`__melder_cache__` folder) so a later conjure can skip compilation. A meld that staged new plans - the first meld of
a spell compiled at that meld, such as one bound after `conjure` - saved the file before it returned, and a save the
operating system refused was raised from the meld after its object had been built: on Windows `PermissionError:
[WinError 5] Access is denied` while another program held the file open (a real-time virus scanner or an indexer,
for example), on any platform for a read-only cache folder or a full disk. A `unique` built that way came back from
the next meld, but a `many` was lost to its caller, a managed lease never went back to its pool, and while the
refusal lasted every meld of the Spellbook raised.

The cache file is now best-effort, as a missing or unreadable one already was (it only makes the cache cold):

- A save the operating system refuses raises nothing. The meld returns its object, the cache stays in memory for
  the next save, and the refusal is logged once per cache file at WARNING - later refusals of that file at DEBUG:

```text
Could not save the creation-cache bundle '.../__melder_cache__/__conjure_cache__/<frame>/<conduit>.meldercache':
[WinError 5] Access is denied: ... Melds are not affected and the cache stays in memory for the next save. To
persist it, make the cache folder writable (on Windows, also exclude it from real-time scanning), or turn caching
off for the frame with with_system_caching_enabled(False). Later refused saves of this bundle log at DEBUG.
```

- On Windows a refused rename of the file is retried for about 100 ms before the save counts as refused.
- Each process and thread writes a temp file of its own (`<conduit>.meldercache.<pid>.<thread id>.tmp`) and a
  failed save removes it, so no `<conduit>.meldercache.tmp` is left behind, and two processes that share a frame
  and conduit name never write into one temp file.

**Breaking change:** `Spell.emit_cache_file()` returns `False` when the operating system refuses the save (the
refusal is logged), where it raised the `OSError`. `True` still means the file was written, and `False` also means
caching is off for the spell or nothing was staged since the last save; code that caught `OSError` around the call
can check the result instead.

What stays the same: the cache file's format and generation (23), when and where Melder saves it, and every other
public signature. A save that fails for any reason other than an operating-system error still raises.

## Packaging and documentation
"""

PACKAGING = f"""\
- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph describe
  the best-effort cache save - the result of a refused save, the per-writer temp file, the Windows rename retry and
  the one WARNING per cache file - and `Spell.emit_cache_file()`'s `False`; the code-map extents of
  `caching_system.py`, `spellbook.py` and `spell.py` are remeasured, and their line citations remapped.
- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for {NEW}.
"""


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        sys.exit(f"ANCHOR {label}: found {count}")
    for line in new.split("\n"):
        if len(line) > 120:
            sys.exit(f"WIDTH {label}: {len(line)}: {line}")
    return text.replace(old, new)


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    apply = sys.argv[1] == "--apply"
    version_text = VERSION.read_text(encoding="utf-8")
    note_text = NOTE.read_text(encoding="utf-8")
    if f'__version__ = "{OLD}"' not in version_text:
        sys.exit("__version__ is not " + OLD + "; another landing came first - re-plan the number")
    new_version = once(version_text, f'__version__ = "{OLD}"', f'__version__ = "{NEW}"', "version")
    new_note = once(note_text, f"# Melder {OLD}\n\n**Unreleased**\n", f"# Melder {NEW}\n\n**Unreleased**\n", "header")
    new_note = once(new_note, "## Packaging and documentation\n", SECTION, "section")
    new_note = once(new_note, f"- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for {OLD}.\n",
                    PACKAGING, "packaging")
    for text in (new_version, new_note):
        if "\r" in text:
            sys.exit("CR")
    print("version", OLD, "->", NEW, "; release note", len(note_text.splitlines()), "->", len(new_note.splitlines()),
          "lines")
    if not apply:
        print("checked; nothing written")
        return
    if VERSION.read_text(encoding="utf-8") != version_text or NOTE.read_text(encoding="utf-8") != note_text:
        sys.exit("RACE: a file changed since it was read; nothing written")
    VERSION.write_text(new_version, encoding="utf-8", newline="\n")
    NOTE.write_text(new_note, encoding="utf-8", newline="\n")
    print("wrote", VERSION.relative_to(ROOT), "and", NOTE.relative_to(ROOT))


if __name__ == "__main__":
    main()
