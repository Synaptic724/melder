"""Release note for the aether_conduit_lookup_api lane: header 0.2.78 -> 0.2.79 and one section.

Usage: python apply_release_note.py <repository root>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_util import replace_block

NOTE = os.path.join(sys.argv[1], "release_docs/0.2.77.md")

HEADER_OLD = "# Melder 0.2.78\n\n**Unreleased**\n"
HEADER_NEW = "# Melder 0.2.79\n\n**Unreleased**\n"

ANCHOR = "## Override payload values reach the provider as the objects you gave\n"
SECTION = '''## Aether finds any conduit by name or id; root-only lookups carry root names

`Aether.get_conduit_by_name` now finds every named scope in a frame - a named root, or a lesser created
with `create_lesser_conduit(name=...)` at any depth - and `Aether.get_conduit_by_id` finds any live
conduit, anonymous lessers included:

```python
root = book.conjure(name="app")
request = root.create_lesser_conduit(name="request")
job = request.create_lesser_conduit()

aether = Aether()
assert aether.get_conduit_by_name("request") is request
assert aether.get_conduit_by_id(job.id) is job
```

Before, both answered over root conduits only, so `get_conduit_by_name("request")` raised "not found"
while the frame's `ConduitCloud` returned the scope.

- **Breaking change: the root-only lookups are renamed, with no aliases.** `list_conduit_ids`,
  `list_conduit_names`, `count_conduits`, `has_conduit_id`, `has_conduit_name` and
  `find_conduit_id_by_name` are now `list_root_conduit_ids`, `list_root_conduit_names`,
  `count_root_conduits`, `has_root_conduit_id`, `has_root_conduit_name` and
  `find_root_conduit_id_by_name`; the old names raise `AttributeError`. Root-only lookups by name and
  by id are `get_root_conduit_by_name` and `get_root_conduit_by_id`.
- **`get_conduit_by_name` and `get_conduit_by_id` keep their names and cover more.** Every root still
  resolves to the same object. Code that relied on a lesser's name or id raising "not found" should use
  the root lookups.
- **Lookups stay per frame.** Every lookup takes `aetheric_frame_name`, a string that defaults to
  `"default"`; a scope in another frame is found by naming that frame. A frame given as anything but a
  string, such as `None`, now raises `TypeError` instead of a misleading "does not exist" error.
- **Errors name the frame.** A miss reads `Conduit with name 'request' not found in frame 'default'.`,
  followed by what the lookup covers; the usual cause is a scope that lives in another frame.
- **Returned and cleaned scopes do not resolve.** A lesser returned to its pool leaves both lookups. The
  reference you get is borrowed and does not keep the scope alive.
- **`ConduitCloud.list_conduits()`** returns one frame's named conduits as a tuple:
  `Aether().get_conduit_cloud().list_conduits()`.
- **Id lookups tolerate scopes coming and going.** The walk behind `get_conduit_by_id`, which the room
  commands of the same name also use, reads snapshots, so a lesser returning to its pool on another thread
  can no longer make it fail with `dictionary changed size during iteration` on free-threaded Python.
- **Room commands are unchanged.** The Nexus room commands and viewer methods of the same names keep
  their behaviour and access control.

'''

print("header:", replace_block(NOTE, HEADER_OLD, HEADER_NEW))
print("section:", replace_block(NOTE, ANCHOR, SECTION + ANCHOR))
