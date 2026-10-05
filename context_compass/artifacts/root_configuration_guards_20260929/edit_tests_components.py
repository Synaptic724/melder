"""Doc pass for the root configuration guards (M1-M4) in tests_components.md (melder_0, 2026-09-30): the six new
test files join their clusters and the code map, and test_nexus.py's extent is remeasured. LF, exact anchors."""
import pathlib
import sys

DOC = pathlib.Path(sys.argv[1])
STAMP = sys.argv[2]


def entry(path: str, loc: int) -> str:
    """Return one code-map entry with a measured extent."""
    return ("- path: `{0}`\n  start_line: 1\n  end_line: {1}\n  loc: {1}\n  verified_at: {2}\n"
            .format(path, loc, STAMP))


EDITS = [
    ("""  missing runtime frame keeps its frame error), and one room memory per top-level public call
Key Files (C1):
- `tests/unit/melder/aether/test_nexus.py`
""", """  missing runtime frame keeps its frame error), and one room memory per top-level public call
- the value snapshot the four root configurations expose (`get_configuration_dictionary()`, 0.2.8212): exact
  properties, independence, equality, lifecycle states and the cleaned refusal
Key Files (C1):
- `tests/unit/melder/aether/test_nexus.py`
- `tests/unit/melder/aether/test_root_configuration_value_snapshots.py` (root configuration snapshots, 2026-09-30)
"""),
    ("""  handle refuses meld and purge; a space released or destroyed inside its own block exits cleanly)
Key Files (C1):
""", """  handle refuses meld and purge; a space released or destroyed inside its own block exits cleanly)
- root configuration guards: Aether's sealed spell-id regime refusing another regime once a frame exists
  (0.2.8209), and an active Nexus refusing another configuration until deactivated (0.2.8210)
Key Files (C1):
"""),
    ("""- `tests/component/melder/aether/conduit/test_spellspace_component_lease_release.py`

### Subcomponent: Crystallizer Component Cluster
""", """- `tests/component/melder/aether/conduit/test_spellspace_component_lease_release.py`
- `tests/component/melder/aether/test_aether_sealed_regime_guard_component.py` (sealed regime, 2026-09-30)
- `tests/component/melder/aether/test_nexus_active_reconfiguration_guard_component.py` (active Nexus, 2026-09-30)

### Subcomponent: Crystallizer Component Cluster
"""),
    ("""- the conduit cache bundle rebuilt from each non-full-hit conjure, and spell ids
  that agree across two fresh interpreters
""", """- the conduit cache bundle rebuilt from each non-full-hit conjure, and spell ids
  that agree across two fresh interpreters
- a dynamic conjure refused by the recorded-world configuration discipline leaving its frame unsettled, and
  the predicted conjure mode agreeing with settlement for every posture and flag (0.2.8211)
"""),
    ("""- `tests/component/melder/spellbook/test_spell_id_process_stability.py` (spell ids in two fresh interpreters, 2026-09-26)
""", """- `tests/component/melder/spellbook/test_spell_id_process_stability.py` (spell ids in two fresh interpreters, 2026-09-26)
- `tests/component/melder/spellbook/test_conjure_refusal_leaves_frame_unsettled_component.py` (refusal before settlement, 2026-09-30)
"""),
    ("""- crystallization of really bound spells (root module name and kind, targets,
  direct dependencies, describe snapshot) and the synthetic-module cases through
  the hosted crystallizer
Key Files (C1):
- `tests/integration/melder/crystallizer/test_spell_crystal_integration.py`
- `tests/integration/melder/crystallizer/test_synthetic_module_integration.py`
""", """- crystallization of really bound spells (root module name and kind, targets,
  direct dependencies, describe snapshot) and the synthetic-module cases through
  the hosted crystallizer
- restores into live worlds: a world whose first frame sealed the Aether regime (0.2.8209), and a live active
  Nexus replaced by the recorded policy through deactivate-first, recorded "disabled" included (0.2.8210)
Key Files (C1):
- `tests/integration/melder/crystallizer/test_spell_crystal_integration.py`
- `tests/integration/melder/crystallizer/test_synthetic_module_integration.py`
- `tests/integration/melder/crystallizer/test_restore_sealed_aether_regime_integration.py` (2026-09-30)
- `tests/integration/melder/crystallizer/test_restore_over_active_nexus_integration.py` (2026-09-30)
"""),
    # Code map.
    ("""- path: `tests/unit/melder/aether/test_nexus.py`
  start_line: 1
  end_line: 6368
  loc: 6368
  verified_at: 2026-09-26T22:11:36Z
""", entry("tests/unit/melder/aether/test_nexus.py", 6377)
        + entry("tests/unit/melder/aether/test_root_configuration_value_snapshots.py", 197)),
    ("""- path: `tests/component/melder/aether/conduit/test_spellspace_component_lease_release.py`
  start_line: 1
  end_line: 317
  loc: 317
  verified_at: 2026-09-27T23:41:28Z
""", """- path: `tests/component/melder/aether/conduit/test_spellspace_component_lease_release.py`
  start_line: 1
  end_line: 317
  loc: 317
  verified_at: 2026-09-27T23:41:28Z
""" + entry("tests/component/melder/aether/test_aether_sealed_regime_guard_component.py", 121)
        + entry("tests/component/melder/aether/test_nexus_active_reconfiguration_guard_component.py", 160)),
    ("""- path: `tests/integration/melder/crystallizer/test_spell_crystal_integration.py`
  start_line: 1
  end_line: 215
  loc: 215
  verified_at: 2026-09-26T22:11:36Z
""", """- path: `tests/integration/melder/crystallizer/test_spell_crystal_integration.py`
  start_line: 1
  end_line: 215
  loc: 215
  verified_at: 2026-09-26T22:11:36Z
""" + entry("tests/integration/melder/crystallizer/test_restore_sealed_aether_regime_integration.py", 121)
        + entry("tests/integration/melder/crystallizer/test_restore_over_active_nexus_integration.py", 136)),
    ("""- path: `tests/component/melder/spellbook/test_spell_id_process_stability.py`
  start_line: 1
  end_line: 111
  loc: 111
  verified_at: 2026-09-26T22:11:36Z
""", """- path: `tests/component/melder/spellbook/test_spell_id_process_stability.py`
  start_line: 1
  end_line: 111
  loc: 111
  verified_at: 2026-09-26T22:11:36Z
""" + entry("tests/component/melder/spellbook/test_conjure_refusal_leaves_frame_unsettled_component.py", 148)),
    ("""- Created: 2026-01-22
- Updated: 2026-09-28
""", """- Created: 2026-01-22
- Updated: 2026-09-30
"""),
    ("""## Context / Handoff Summary

""", """## Context / Handoff Summary

2026-09-30 root configuration guards (0.2.8209-0.2.8212): six new files - root configuration value snapshots
(unit), the sealed Aether regime and the active-Nexus refusal (component), the conjure refusal before
settlement with its prediction table (component), and restores into live worlds over a sealed regime and over
an active Nexus (integration). Two `test_nexus.py` rows that re-activated the live Nexus with another policy as
setup now deactivate it first; what they assert is unchanged. The test-file extents are measured.

"""),
]

text = DOC.read_bytes().decode("utf-8")
assert "\r\n" not in text
for old, new in EDITS:
    assert text.count(old) == 1, (text.count(old), old[:90])
    text = text.replace(old, new, 1)
DOC.write_bytes(text.encode("utf-8"))
print("edited", DOC.name, len(text.splitlines()), "lines")
