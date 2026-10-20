"""Hand edits, batch 06: rift/command_system/command_system.py (CRLF) and crystal_loader_system/restore_engine.py
(melder_1, 2026-10-18).

command_system.py 209 ("their attached lesser lineage") is the conduit scope tree and stays; 1624 means the published
spell indexes a spell_id is looked up across. restore_engine.py: the cluster stage's auto-share re-grants the
shareable spells the cluster records, and a plain contract detail lives with the side that owns the granted spell.
static_command_system.py and graft_runner.py hold no "lineage".
"""
R = "src/melder/nexus/rift/command_system/command_system.py"
E = "src/melder/crystallizer/crystal_loader_system/restore_engine.py"

EDITS = [
    (R, 1624, "                published lineages.", [
        "                published spell indexes.",
    ]),
    (E, 2578, "              lineages; leader election is a runtime act).", [
        "              spells; leader election is a runtime act).",
    ]),
    (E, 2661, "            # Auto-share on member join re-grants shareable lineages;", [
        "            # Auto-share on member join re-grants the shareable spells;",
    ]),
    (E, 2680, '              side that OWNS the lineage ("initiated" via the link-time', [
        '              side that OWNS the spell ("initiated" via the link-time',
    ]),
    (E, 2750, "                # The map holder OWNS the lineage (both detail labels);", [
        "                # The map holder OWNS the spell (both detail labels);",
    ]),
]
