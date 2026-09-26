"""Add the shared-context rebuild section to release_docs/next_version_release.md (anchored insert).

Usage: python release_note.py <repo_root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from patch_util import replace_block

note = pathlib.Path(sys.argv[1]) / "release_docs/next_version_release.md"
replace_block(note,
'''## Automatic creation-cache refresh after a Melder update''',
'''## Melding a shared spell while another conduit revalidates it no longer fails

In dynamic worlds a spell shared between conduits (through links, contracts or clusters) has one
compiled plan and one creation context. The first time a conduit melds such a spell, Melder
revalidates it for that conduit and rebuilds the plan. A thread melding the same spell at that
moment could fail with `RuntimeError: Cannot build CreationContext before spell_codegen_creation
exists`, or with an `AttributeError` because the context was cleaned while it was in use. The
failure was intermittent and depended on thread timing.

A rebuild now pauses new melds of that spell, waits for the melds already running to finish,
rebuilds, and then lets them continue with the new plan. Melds of other spells are not affected.

- **No API change.** Revalidation runs exactly as before; only its interaction with running melds
  changes.
- **Warm melds are unaffected.** Measured within noise; automatic worlds take no new path.
- **A meld can wait briefly** while another conduit rebuilds the same spell, typically the first
  meld through a new link, contract or cluster.
- **A failed context build is reported, not waited on.** Threads that were waiting for it raise
  with the original cause instead of waiting forever.
- **No creation-cache rebuild.** Compiled plans are unchanged, so existing caches stay valid.
- **Limitation:** a constructor that melds its own spell through a conduit that must first rebuild
  that spell waits on itself and fails after 30 seconds.

## Automatic creation-cache refresh after a Melder update''')
