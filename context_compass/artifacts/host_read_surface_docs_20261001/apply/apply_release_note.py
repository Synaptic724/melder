"""
Add the system-document catch-up for 0.2.8208 to the running release note's Packaging and documentation section.

Usage: python apply_release_note.py <repository root>
No src change, so no notch: the header and the rebuild line keep 0.2.8215. The anchor must match exactly once.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

ROOT = sys.argv[1]
DOC = "release_docs/next_version_release.md"
s = ApplySession(ROOT)
s.insert_before(
    DOC,
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8215.\n",
    "- The packaged system documents describe the frame lookups and read accessors of \"Look up frames without\n"
    "  creating them\" (the Aether, frame registry, frame, posture, Spellbook configuration and conduit entries, a\n"
    "  frame-lookup flow and diagram), and `docs/intermediate/scopes.md` shows them. Line citations those additions\n"
    "  moved, and the stale ones into `aether.py`, are remeasured; the Aether singleton invariant now says that\n"
    "  teardown resets unconditionally and only a failed construction checks identity.\n",
)
long_lines = s.long_added_lines()
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written)
