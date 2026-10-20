"""D3 handover documentation (0.2.8239 -> 0.2.8240). Run: python <this file> <tree root> [--src-only].

Owner direction 2026-10-14 (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, D3 task Notes): a transfer hands over
stewardship, not a working setup; the new owner binds the dependencies it needs and builds its own version while the
old owner cleans up. Wording follows probe_transfer_handover.py (runs/probe_transfer_handover_0_2_8239_gil*.txt).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edit_tool

ROOT = pathlib.Path(sys.argv[1])
SRC_ONLY = "--src-only" in sys.argv[2:]
CONDUIT = str(ROOT / "src/melder/aether/conduit/conduit.py")
VERSION = str(ROOT / "src/melder/__version__.py")
NOTE = str(ROOT / "release_docs/next_version_release.md")
OWNERSHIP = str(ROOT / "docs/intermediate/ownership.md")

print("conduit", edit_tool.apply(CONDUIT, [
    (
        "            - Existing instances follow `move_creations` (below). A transfer\n"
        "              never disposes anything.\n",
        "            - Existing instances follow `move_creations` (below). A transfer\n"
        "              never disposes anything.\n"
        "            - A transfer hands over stewardship, not a working setup. The\n"
        "              spells the transferred spell depends on stay with this conduit\n"
        "              unless `include_dependencies` moves the direct ones, so the\n"
        "              target can start out broken: a moved instance keeps the\n"
        "              dependencies it was built with, and this conduit's teardown\n"
        "              disposes the ones it owns while the moved instance still holds\n"
        "              them. That is expected in a runtime agents iterate in. The\n"
        "              target purges what it does not want, binds the dependencies it\n"
        "              needs (a meld that must build the spell without them raises\n"
        "              `UnresolvedInputError` naming each missing input) and melds its\n"
        "              own version, while this conduit cleans up its own scope.\n",
    ),
    (
        "            include_dependencies: If True, transfer owned dependencies as well.\n",
        "            include_dependencies: If True, also transfer each direct dependency\n"
        "                this conduit owns, with the same options, so the target\n"
        "                receives those spells (and, with `move_creations`, their\n"
        "                instances) instead of depending on this conduit for them.\n",
    ),
]))
print("version", edit_tool.apply(VERSION, [('__version__ = "0.2.8239"\n', '__version__ = "0.2.8240"\n')]))
if SRC_ONLY:
    raise SystemExit(0)
print("note", edit_tool.apply(NOTE, [
    ("# Melder 0.2.8239\n", "# Melder 0.2.8240\n"),
    (
        "To keep the old behaviour, pass `move_creations=False`; the transfer report's `options` show the value used.\n",
        "To keep the old behaviour, pass `move_creations=False`; the transfer report's `options` show the value used.\n"
        "\n"
        "A transfer hands over stewardship, not a working setup, and the docstring and the ownership guide now say so\n"
        "(0.2.8240). The spells the transferred spell depends on stay with the old owner unless `include_dependencies=True`\n"
        "moves the direct ones, so the new owner can start out broken: the moved objects keep the dependencies they were\n"
        "built with, and the old owner's teardown disposes the ones it owns while the moved objects still hold them. That\n"
        "is expected in a runtime agents iterate in. The new owner purges what it does not want, binds the dependencies it\n"
        "needs - a meld that must build the spell without them raises `UnresolvedInputError` naming each missing input -\n"
        "and melds its own version, while the old owner cleans up its own scope.\n",
    ),
]))
print("ownership", edit_tool.apply(OWNERSHIP, [(
    "inspects the report, and resolves from the new home. Read that report when\n"
    "diagnosing a transfer; sharing and moving ownership have different lifecycle\n"
    "consequences.\n",
    "inspects the report, and resolves from the new home. Read that report when\n"
    "diagnosing a transfer; sharing and moving ownership have different lifecycle\n"
    "consequences.\n"
    "\n"
    "A transfer hands over stewardship, not a working setup. The spells the\n"
    "transferred spell depends on stay with the old owner unless\n"
    "`include_dependencies=True` moves the direct ones, so expect the new owner to\n"
    "start out broken once the old owner tears down: its moved objects can hold\n"
    "dependencies that were just disposed. That is normal in a runtime agents\n"
    "iterate in. The new owner purges what it does not want, binds the dependencies\n"
    "it needs (a meld without them raises `UnresolvedInputError` naming each\n"
    "missing input) and builds its own version, while the old owner cleans up\n"
    "after itself.\n",
)]))
