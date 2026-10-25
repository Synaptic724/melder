"""Release-note entry for D-10 at the notch (melder_0, 2026-10-25; 0.2.8270).

Targeted edits to release_docs/next_version_release.md, refusing to write if the note moved under it: the header to
0.2.8270, one new section before "## Packaging and documentation", one Packaging bullet before the rebuild line (every
other bullet, melder_2's included, kept as it is), and the rebuild line's version. Usage: --check | --apply
"""
import pathlib
import sys

NOTE = pathlib.Path.home() / "mnt/melder_private/release_docs/next_version_release.md"
OLD_HEADER = "# Melder 0.2.8269\n"
NEW_HEADER = "# Melder 0.2.8270\n"
PACKAGING = "\n## Packaging and documentation\n"
OLD_REBUILD = "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8269.\n"
NEW_REBUILD = "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8270.\n"

SECTION = '''
## Codegen rooms under the safe, hybrid and precision profiles refuse `open`

Code an agent runs in a codegen room is checked against the codegen profile of the frame it names before it runs.
Through 0.2.8269 no profile stopped the `open` builtin, so room code under every profile read and wrote any file the
process could reach - under `safe` too, whose posture says it denies writes - and `hybrid` also admitted
`import pathlib`, whose `Path.write_text` writes files.

**Breaking change:** under the `safe`, `hybrid` and `precision` profiles - `precision` on its own or as the overlay
on another profile - room code that calls `open` is refused at validation, and nothing runs:

```python
# command_system: the command surface of a codegen room (rift.space.command_system) whose Rift is linked to the
# frame "ops", and the codegen profile of "ops" is safe.
result = command_system.execute_codegen("handle = open('notes.txt', 'w')\\nhandle.write('x')", frame_name="ops")
result["accepted"]              # False: nothing is written
result["validation_issues"][0]  # "Builtin 'open' is not allowed in this codegen mode."
```

Code that only names it (`reader = open`) is refused with "Name 'open' is not available in the codegen namespace.",
and `open` is no longer among the room's runtime builtins. A request naming a frame the room holds no codegen
projection for runs under the safe posture, which denies `open` as well. Under `hybrid`, `import pathlib` is refused
with "Import root 'pathlib' is not allowed in this codegen mode.": `pathlib`, like `io` and `os`, is now on the
`permissive` import list only. Room code that must read or write files runs under the `permissive` or `full_access`
profile, whose file posture stays open by design.

What stays the same: `permissive` and `full_access` keep `open`, `io`, `os` and `pathlib`; every other builtin and
import root of each profile is unchanged; a `builtin_names` allow rule in a frame's codegen capability override still
allows `open` for that frame; and nothing cached or recorded changes. These checks run in the room's own process:
they are policy and defence in depth, not isolation.
'''

BULLET = (
    "- The packaged system documents (`melder.__architecture__`, `melder.__components__`) and the packaged graph"
    " describe\n"
    "  each codegen profile's file posture - `open` on the deny list `safe`, `hybrid` and `precision` share, `io`,"
    " `os` and\n"
    "  `pathlib` on the `permissive` import list only, and the safe posture of a request naming a frame with no"
    " codegen\n"
    "  projection - and the packaged test documents describe the new tests; each profile's docstring states its file\n"
    "  posture. The code-map extent of `codegen_system.py` is remeasured, and line citations into it remapped.\n"
)


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        raise SystemExit(__doc__)
    raw = NOTE.read_bytes()
    if b"\r" in raw:
        raise SystemExit("CR in the note")
    text = raw.decode("utf-8")
    if not text.startswith(OLD_HEADER):
        raise SystemExit("header is not " + OLD_HEADER.strip())
    for needle in (PACKAGING, OLD_REBUILD):
        if text.count(needle) != 1:
            raise SystemExit("expected once: " + needle.strip())
    if "refuse `open`" in text:
        raise SystemExit("section already present")
    text = NEW_HEADER + text[len(OLD_HEADER):]
    text = text.replace(PACKAGING, SECTION + PACKAGING, 1)
    text = text.replace(OLD_REBUILD, BULLET + NEW_REBUILD, 1)
    for number, line in enumerate(text.splitlines(), 1):
        if len(line) > 120:
            raise SystemExit("line {0} is {1} chars".format(number, len(line)))
    print("lines:", len(text.splitlines()))
    if sys.argv[1] == "--apply":
        if NOTE.read_bytes() != raw:
            raise SystemExit("RACE release note")
        NOTE.write_bytes(text.encode("utf-8"))
        print("applied")


if __name__ == "__main__":
    main()
