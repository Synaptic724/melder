"""Add the 0.2.8204 section to release_docs/next_version_release.md (CRLF) and move the header and rebuild line.

Run from the repository root. Each anchor must match once; the file is edited as LF and written back as CRLF.
"""
import pathlib

PATH = pathlib.Path("release_docs/next_version_release.md")

SECTION = """## Fixed: a SpellSpace's live-creation probe missed the `many` objects it holds

The no-create probe on a SpellSpace's meld door (`has_live_creation` and `describe_live_creation_status`,
which Melder's diagnostics call on the space's door) now reads `Existence.many` objects from the space's own
store. A `many` with disposal methods melded through a space is kept there - the space's exit disposes it and
the space's `purge` removes it from there - but the probe looked in the owner conduit's store, so it reported
nothing while the space held such objects and counted the conduit's own instead. It now counts the space's,
with `storage_scope_kind` `"spellspace_many"` and the space's id in `active_spellspace_id`.
`Conduit.has_live_creation`, every other lifetime and the meld path are unchanged; the probe still creates
nothing.

## Packaging and documentation
"""

EDITS = [
    ("# Melder 0.2.8203\n", "# Melder 0.2.8204\n"),
    ("## Packaging and documentation\n", SECTION),
    (
        "  version) are corrected.\n"
        "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8203.\n",
        "  version) are corrected.\n"
        "- The packaged system documents also describe which store each meld door's live-creation probe reads, and\n"
        "  the Meld runtime's store-selection text now matches the code for `unique`, lineage and cluster lifetimes.\n"
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

# Follow-up applied after the run above (2026-09-28, a one-off python edit): the section's paragraph was
# reworded and reflowed so that it opens "The no-create probe on the meld door a SpellSpace uses
# (`has_live_creation` and `describe_live_creation_status`) now reads ..."; the first text said "which
# Melder's diagnostics call on the space's door", which overstated its callers (only tests call it today).
