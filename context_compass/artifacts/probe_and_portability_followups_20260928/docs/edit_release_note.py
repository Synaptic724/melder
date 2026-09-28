"""Move the running release note to 0.2.8205 and add one packaging bullet (CRLF file).

The rebuild line keeps 0.2.8204: the owner waived the asset rebuild for this pass, so the line stays true until
the next rebuild names its own version. Run from the repository root; each anchor must match once.
"""
import pathlib

PATH = pathlib.Path("release_docs/next_version_release.md")
EDITS = [
    ("# Melder 0.2.8204\n", "# Melder 0.2.8205\n"),
    (
        "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8204.\n",
        "- The packaged system documents no longer paste the documentation tooling's commands or cite its files,\n"
        "  which a reader of the packaged copy could not resolve, and the conduit meld door's docstrings now name\n"
        "  the store each lifetime uses and no longer promise an active-spellspace check.\n"
        "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8204.\n",
    ),
]
raw = PATH.read_bytes().decode("utf-8")
assert raw.count("\r\n") == raw.count("\n")
text = raw.replace("\r\n", "\n")
for old, new in EDITS:
    assert text.count(old) == 1, (old[:50], text.count(old))
    text = text.replace(old, new)
for line in text.split("\n"):
    assert len(line) <= 120, line
PATH.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
print("release note updated")
