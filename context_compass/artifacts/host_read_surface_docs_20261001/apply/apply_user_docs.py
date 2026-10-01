"""
Add the frame lookups and read accessors (0.2.8208) to docs/intermediate/scopes.md.

Usage: python apply_user_docs.py <repository root>
The anchor must match exactly once (in the line-ending style of that spot); nothing is written otherwise.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

ROOT = sys.argv[1]
DOC = "docs/intermediate/scopes.md"
s = ApplySession(ROOT)
s.insert_after(
    DOC,
    "anonymous. The root-only lookups carry root names, such as\n`get_root_conduit_by_name`.\n",
    "\n"
    "Frames have lookups of their own that never create anything (0.2.8208):\n"
    "`Aether().find_frame(\"ops\")` returns the live frame or `None`,\n"
    "`Aether().get_frame(\"ops\")` raises `ValueError` when it is missing, and\n"
    "`Aether().list_frame_names()` lists the live frames in the order they were\n"
    "created. The frame-scoped calls above create the default frame when it is\n"
    "missing; these never do, not even for \"default\". A frame you find is borrowed,\n"
    "so its owner can still clean it. For checks before you hand a configuration\n"
    "over: `frame.shared_spellbook_configuration` is the configuration Spellbooks in\n"
    "that frame adopt when the frame shares one, `job.spellbook` is the Spellbook a\n"
    "conduit resolves through, `SpellbookConfiguration.aether_frame` and `frozen`\n"
    "report a configuration's frame and whether it is settled, and\n"
    "`AethericFrameConfiguration.frozen` does the same for a frame's posture. None\n"
    "of them changes anything.\n",
)
long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written)
