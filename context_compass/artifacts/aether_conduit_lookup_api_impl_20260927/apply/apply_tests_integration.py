"""Step 4d of the aether_conduit_lookup_api lane: integration, component and benchmark call sites.

Every site looks up a ROOT (a conjured or restored root), so each moves to the root-named lookup with
unchanged behaviour.

Usage: python apply_tests_integration.py <tree root>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edit_util import replace_block

ROOT = sys.argv[1]


def path(relative: str) -> str:
    return os.path.join(ROOT, relative)


CORE = path("tests/integration/melder/aether/test_aether_integration_core.py")
ERRORS = path("tests/integration/melder/aether/test_aether_integration_error_paths.py")
FRAMES = path("tests/integration/melder/aether/test_aether_integration_frames.py")
SNAPSHOT = path("tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_parity.py")
NON_RESOLVABLE = path("tests/integration/melder/aether/test_non_resolvable_graph_replay.py")
DISPOSAL = path("tests/integration/melder/crystallizer/test_ordered_disposal_replay.py")
GAUNTLET = path("benchmarks/testing_other_di/test_gauntlet_melder_lane_parity.py")

EDITS = [
    (CORE, '''        - get_conduit_by_id returns the owning conduit.
        - get_conduit_by_name returns the owning conduit.
''', '''        - _get_root_conduit_by_id returns the owning root conduit.
        - _get_root_conduit_by_name returns the owning root conduit.
''', 1),
    (CORE, '''        assert aether._get_conduit_by_id(conduit.id, frame_name) is conduit
        assert aether._get_conduit_by_name("root", frame_name) is conduit
''', '''        assert aether._get_root_conduit_by_id(conduit.id, frame_name) is conduit
        assert aether._get_root_conduit_by_name("root", frame_name) is conduit
''', 1),
    (CORE, '''            aether._get_conduit_by_name("missing", frame_name)
''', '''            aether._get_root_conduit_by_name("missing", frame_name)
''', 1),
    (CORE, '''            aether._get_conduit_by_id("missing-id", frame_name)
''', '''            aether._get_root_conduit_by_id("missing-id", frame_name)
''', 1),
    (ERRORS, '''        - _get_conduit_by_id raises ValueError for missing frames.
        - _get_conduit_by_name raises ValueError for missing frames.
''', '''        - _get_root_conduit_by_id raises ValueError for missing frames.
        - _get_root_conduit_by_name raises ValueError for missing frames.
''', 1),
    (ERRORS, '''        aether._get_conduit_by_id("id", "missing-frame")
''', '''        aether._get_root_conduit_by_id("id", "missing-frame")
''', 1),
    (ERRORS, '''        aether._get_conduit_by_name("name", "missing-frame")
''', '''        aether._get_root_conduit_by_name("name", "missing-frame")
''', 1),
    (FRAMES, '''        assert Aether().get_conduit_by_name("root-b", "frame-b") is conduit_b
''', '''        assert Aether().get_root_conduit_by_name("root-b", "frame-b") is conduit_b
''', 1),
    (FRAMES, '''        aether._get_conduit_by_id(conduit_id, frame_name)
''', '''        aether._get_root_conduit_by_id(conduit_id, frame_name)
''', 1),
    (SNAPSHOT, '''    restored = Aether().get_conduit_by_name("root", aetheric_frame_name=FRAME)
''', '''    restored = Aether().get_root_conduit_by_name("root", aetheric_frame_name=FRAME)
''', 1),
    (NON_RESOLVABLE, '''    conduit = Aether().get_conduit_by_name("root", "recorded")
''', '''    conduit = Aether().get_root_conduit_by_name("root", "recorded")
''', 1),
    # Two sites (indent 4 and 12): the pattern matches inside both lines, so replace both at once.
    (DISPOSAL, '''conduit = Aether().get_conduit_by_name("disposal-root", "disposal-source")
''', '''conduit = Aether().get_root_conduit_by_name("disposal-root", "disposal-source")
''', 2),
    (DISPOSAL, '''            restored = Aether().get_conduit_by_name("borrower", "disposal-grant")
''', '''            restored = Aether().get_root_conduit_by_name("borrower", "disposal-grant")
''', 1),
    (GAUNTLET, '''    conduit = Aether().get_conduit_by_name(_LaneNames.CONDUIT, _LaneNames.FRAME)
''', '''    conduit = Aether().get_root_conduit_by_name(_LaneNames.CONDUIT, _LaneNames.FRAME)
''', 1),
]

for target, old, new, count in EDITS:
    print(os.path.relpath(target, ROOT), replace_block(target, old, new, count))
