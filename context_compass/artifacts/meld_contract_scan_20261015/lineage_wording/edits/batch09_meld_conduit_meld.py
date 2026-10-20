"""Hand edits, batch 09: conduit/meld/meld.py and conduit/meld/conduit_meld.py (melder_1, 2026-10-18).

meld.py: the gate's state reads (`_ensure_lineage_resolvable`, `_may_compile`, `_is_stale`) and the catch-up
(`_refresh_stale_dependencies`, `_iter_planned_dependencies`, `_current_in_pool`, `_refresh_dependency_structure`)
read the SpellSystemState of a spell's SpellIndex; "lineage" there means that SpellIndex. 2156 called a spell_id
"the current lineage id". Kept (scope tree): 166 (`unique_per_conduit_lineage`), 353 (the lineage-root store), 1297
(lesser-lineage cases), 1852 (lineage-wide hook changes). Identifiers keep their names.
conduit_meld.py: every use is the `unique_per_conduit_lineage` store selection (scope tree) except 755 and 915, which
mean spells scoped to a spellspace request. The runtime labels "lineage root conduit" and "lineage_root" stay.
spellspace_meld.py is all scope tree and is not edited.
"""
M = "src/melder/aether/conduit/meld/meld.py"
C = "src/melder/aether/conduit/meld/conduit_meld.py"

EDITS = [
    (M, 176, "        lazy phases when a lineage's validity is UNKNOWN or GATED. Contract", [
        "        lazy phases when a SpellIndex's validity is UNKNOWN or GATED. Contract",
    ]),
    (M, 956, "        - rerun structural phases when the lineage is unknown or gated; for a", [
        "        - rerun structural phases when its SpellIndex is unknown or gated; for a",
    ]),
    (M, 1224, '        "Is this lineage eligible to continue as-is, or must meld force a', [
        '        "Is this SpellIndex eligible to continue as-is, or must meld force a',
    ]),
    (M, 1235, "            SpellbookValidationError: If the lineage is already in a hard-fail", [
        "            SpellbookValidationError: If the SpellIndex is already in a hard-fail",
    ]),
    (M, 1363, "            - True when the lineage has no registered state, or is `unknown` or", [
        "            - True when its SpellIndex has no registered state, or is `unknown` or",
    ]),
    (M, 1366, "            - For a `valid` lineage, True exactly when its effective verdict for", [
        "            - For a `valid` SpellIndex, True exactly when its effective verdict for",
    ]),
    (M, 1369, "            - False otherwise: an `invalid`, `disabled` or `cleaned` lineage or", [
        "            - False otherwise: an `invalid`, `disabled` or `cleaned` SpellIndex or",
    ]),
    (M, 1400, "        Report whether a dependency's structure is stale: its lineage is", [
        "        Report whether a dependency's structure is stale: its SpellIndex is",
    ]),
    (M, 1404, "            - A registered lineage that is `gated` or `unknown` needs phases 1-4", [
        "            - A registered SpellIndex that is `gated` or `unknown` needs phases 1-4",
    ]),
    (M, 1428, "        Refresh the structure of every stale lineage the spell's plan expands,", [
        "        Refresh the structure of every stale dependency the spell's plan expands,",
    ]),
    (M, 1438, "            refused. The catch-up reruns phases 1-4 of each stale lineage first", [
        "            refused. The catch-up reruns phases 1-4 of each stale dependency first",
    ]),
    (M, 1439, "            and resets that lineage's own plan, so it rebuilds at its own next", [
        "            and resets that dependency's own plan, so it rebuilds at its own next",
    ]),
    (M, 1449, "              dependency is walked through, not refreshed: a stale lineage", [
        "              dependency is walked through, not refreshed: a stale dependency",
    ]),
    (M, 1492, "        lineages select now, as Phase 8 expands them.", [
        "        indexes select now, as Phase 8 expands them.",
    ]),
    (M, 1503, "            - Each dependency is taken to the version its lineage selects now", [
        "            - Each dependency is taken to the version its SpellIndex selects now",
    ]),
    (M, 1507, "            - May return one lineage twice (two sockets naming it); the caller's", [
        "            - May return one dependency twice (two sockets naming it); the caller's",
    ]),
    (M, 1516, "            spell_system_states: The frame's lineage registry.", [
        "            spell_system_states: The frame's SpellIndex state registry.",
    ]),
    (M, 1562, "        Return the active Spell of the lineage a version id belongs to, from the", [
        "        Return the active Spell of the SpellIndex a version id belongs to, from the",
    ]),
    (M, 1567, "              lineage (`get_by_spell_id`; a notch adds the incoming id and keeps", [
        "              SpellIndex (`get_by_spell_id`; a notch adds the incoming id and keeps",
    ]),
    (M, 1568, "              the old one), so a superseded id leads to the lineage's current", [
        "              the old one), so a superseded id leads to the index's current",
    ]),
    (M, 1575, "            spell_system_states: The frame's lineage registry.", [
        "            spell_system_states: The frame's SpellIndex state registry.",
    ]),
    (M, 1580, "            Optional[Spell]: The lineage's active Spell in the Book, or None.", [
        "            Optional[Spell]: The SpellIndex's active Spell in the Book, or None.",
    ]),
    (M, 1590, "        uses a plan built before its lineage went stale.", [
        "        uses a plan built before its SpellIndex went stale.",
    ]),
    (M, 1599, "            - Broken after the rerun: pins the lineage `invalid`, as the gate", [
        "            - Broken after the rerun: pins its SpellIndex `invalid`, as the gate",
    ]),
    (M, 1622, "            dependency: A stale lineage's active Spell, found by the walk.", [
        "            dependency: The active Spell of a stale SpellIndex, found by the walk.",
    ]),
    (M, 2156, "        exact current lineage id and do not need logical frame/binding", [
        "        exact current spell_id and do not need logical frame/binding",
    ]),
    (C, 755, "            - Rejects spellspace-request lineages on the conduit-facing door.", [
        "            - Rejects spellspace-scoped spells on the conduit-facing door.",
    ]),
    (C, 915, "            - Rejects spellspace-request lineages on the conduit-facing door", [
        "            - Rejects spellspace-scoped spells on the conduit-facing door",
    ]),
]
