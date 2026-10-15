"""
TASK-2026-10-15-describe_notch_borrower_follow_as_feature, owner-directed addition (chat 2026-10-15: "make this
front and center at the top of SRC_Architecture explaining what ... this is for holistically ... this is NOT a di
container"): open src_architecture with "What Melder Is (Read This First)" and move the Runtime Model under it.
Docs only. LF, no new non-ASCII characters, every anchor matched once. Run from the repository root.
"""
import pathlib

path = pathlib.Path("context_compass/system_docs/src_architecture.md")
raw = path.read_bytes().decode("utf-8")
assert "\r\n" not in raw
text = raw

start = text.index("## Runtime Model: Structure Is the Contract\n")
end = text.index("## Entrypoints and Runtime Guardrails\n")
old_section = text[start:end]
assert old_section.count("## Runtime Model: Structure Is the Contract\n") == 1
text = text[:start] + text[end:]

old_opening = """Owner ruling (2026-10-14). Melder is a runtime that agents work inside, not a container that owns every object it
hands out. An agent loads its world into the Python runtime and iterates there: it binds a tool, melds it in a
conduit, tries it, binds a new version and notches to the one it wants, tears scopes down, records the blueprint and
builds the next thing - sometimes the subsystem it is working in. Codegen is iterative, so the iteration happens in
the runtime, not outside it.
"""
assert old_section.count(old_opening) == 1
body = old_section.replace("## Runtime Model: Structure Is the Contract\n", "### Runtime Model: Structure Is the Contract\n")
body = body.replace(old_opening, "Owner ruling (2026-10-14). Melder is a runtime that agents work inside, not a container that owns every object it\n"
                                 "hands out.\n")
body = body.rstrip("\n") + "\n\n" + (
    "Do not judge Melder by DI-container rules - one live instance per type, every object torn down with its scope, the\n"
    "newest version replacing the old. Old versions staying alive, objects left pending after a transfer or a contract\n"
    "change, and a borrower rebuilding after a notch are features. Read the code path before calling anything a bug,\n"
    "and ask the owner when the intent is unclear.\n\n")

top = """## What Melder Is (Read This First)

Melder is not a DI container. The beginner docs start with `bind`, `conjure` and `meld`, so it looks like one:
dependency injection is the first thing a new user touches, and it is one capability of Melder, not what Melder is.
Melder is a runtime that agents live in and build in (owner, 2026-10-15). Read every other section of this document,
and judge every behaviour of the code, through this picture.

### How Melder Is Used

- Agents load their world into the Python runtime and work inside it. They bind objects as spells, meld them in
  conduits, try them, change them, bind new versions and notch to the one they want, tear scopes down, record the
  blueprint and build the next thing. The iteration happens in the runtime, not outside it.
- Many agents work at once, each in its own conduits, sharing through links, contracts and clusters and handing
  work to each other by ownership transfer. Several agents can iterate on the same object: each notch moves the
  active version, the borrowers linked to the index follow it and rebuild, and nobody's existing objects are taken
  away. After five or ten versions the subsystem converges on the object the agents want.
- Versions are first-class. A spell index holds a lineage of versions and a notch only moves which one is active.
  MutationResearch records the versions (lanes, nodes, history), compositions pin specific member versions
  together, and the creation stores key objects by version id, so a `unique` spell can have one live object per
  version - several singletons at once, by design.
- Agents can build the subsystem they are sitting in: codegen rooms (Nexus, Rift, RiftSpace) run agent-written code
  against the live world under ACL profiles, and MutationResearch keeps the history of what changed.

"""
h1 = "# Src Architecture (C4)\n\n"
assert text.startswith(h1)
text = h1 + top + body + text[len(h1):]

old_updated = "- Updated: 2026-10-14\n"
assert text.count(old_updated) == 1
text = text.replace(old_updated, "- Updated: 2026-10-15\n")

handoff_anchor = "## Context / Handoff Summary\n\n"
assert text.count(handoff_anchor) == 1
text = text.replace(handoff_anchor, handoff_anchor + (
    "2026-10-15 what Melder is (documentation only, owner-directed): the document opens with \"What Melder Is (Read\n"
    "This First)\" - Melder is not a DI container but a runtime agents live and build in: many agents iterate on the\n"
    "same objects through versions, borrowers follow a notch, versions coexist (MutationResearch, compositions, one\n"
    "`unique` object per version), and agents build the subsystem they are in. The Runtime Model moved under it, with\n"
    "the rule not to judge the code by DI-container rules.\n\n"))

assert sum(ord(c) > 127 for c in text) == sum(ord(c) > 127 for c in raw)
for i, line in enumerate(text.splitlines(), 1):
    if i < 60 and len(line) > 120:
        raise SystemExit(f"line {i} too long: {len(line)}")
path.write_bytes(text.encode("utf-8"))
print("src_architecture", len(raw.splitlines()), "->", len(text.splitlines()))
