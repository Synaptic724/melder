"""Hand edits, batch 07: dev_ops/risk_manager/risk_manager.py (CRLF) (melder_1, 2026-10-18).

RiskManager tracks risk per SpellIndex id (structural) and per SpellIndex id or `spell:<id>` key (resolution), and
excludes the indexes the registry flags `non_resolvable`; every "lineage" in its docstrings means that SpellIndex.
Kept: the `__slots__` names "lineages" (67) and "_lineage_conduits" (179), which are attribute names, and every
identifier (`lineage_id`, `lineage_key`, `_resolve_lineage_id`, ...); the Args lines keep the parameter names.
"""
K = "src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py"

EDITS = [
    (K, 23, "    - which lineages the conduit currently knows about", [
        "    - which spell indexes the conduit currently knows about",
    ]),
    (K, 24, "    - which of those lineages are structurally risky", [
        "    - which of those spell indexes are structurally risky",
    ]),
    (K, 47, "        this package is built around. Which lineages a conduit KNOWS ABOUT", [
        "        this package is built around. Which spell indexes a conduit KNOWS ABOUT",
    ]),
    (K, 53, "        one merged risky-lineage set - is what preserves the distinction at the", [
        "        one merged risky-index set - is what preserves the distinction at the",
    ]),
    (K, 80, "        - Starts with empty lineage and risk sets.", [
        "        - Starts with empty spell-index and risk sets.",
    ]),
    (K, 102, '    "Does this conduit currently own or see any lineage whose state means meld', [
        '    "Does this conduit currently own or see any SpellIndex whose state means meld',
    ]),
    (K, 106, "    - structural risk is tracked by lineage id", [
        "    - structural risk is tracked by SpellIndex id",
    ]),
    (K, 107, "    - resolution risk is tracked by conduit-local lineage or spell id key", [
        "    - resolution risk is tracked by conduit-local SpellIndex id or spell id key",
    ]),
    (K, 110, "      set holds a key that is not excluded; a lineage whose state carries", [
        "      set holds a key that is not excluded; a SpellIndex whose state carries",
    ]),
    (K, 135, "        per-lineage and per-conduit verdicts; this class folds many verdicts", [
        "        per-SpellIndex and per-conduit verdicts; this class folds many verdicts",
    ]),
    (K, 142, "        relevant lineage is risky would be a scan; a single spellbook-level", [
        "        relevant SpellIndex is risky would be a scan; a single spellbook-level",
    ]),
    (K, 148, "        than merely fast. A never-validated lineage is indistinguishable from a", [
        "        than merely fast. A never-validated SpellIndex is indistinguishable from a",
    ]),
    (K, 153, "        (lineage, conduit) pair, so one conduit's gated lineage must not mark a", [
        "        (SpellIndex, conduit) pair, so one conduit's gated SpellIndex must not mark a",
    ]),
    (K, 155, "        lineage id instead.", [
        "        SpellIndex id instead.",
    ]),
    (K, 157, '        validation gating - removing a lineage must never leave a stale "valid"', [
        '        validation gating - removing a SpellIndex must never leave a stale "valid"',
    ]),
    (K, 159, "        The one exclusion is declared, not inferred. A lineage whose selected", [
        "        The one exclusion is declared, not inferred. A SpellIndex whose selected",
    ]),
    (K, 192, "                SpellSystemStates registry used to resolve lineage ids and", [
        "                SpellSystemStates registry used to resolve SpellIndex ids and",
    ]),
    (K, 198, "        - Starts with empty conduit-state and lineage-to-conduit indexes.", [
        "        - Starts with empty conduit-state and index-to-conduit maps.",
    ]),
    (K, 228, "        - Clears conduit and lineage indexes before dropping the", [
        "        - Clears the conduit and index-to-conduit maps before dropping the",
    ]),
    (K, 299, "        Remove conduit tracking and clear lineage mappings.", [
        "        Remove conduit tracking and clear its index-to-conduit mappings.",
    ]),
    (K, 303, "        - Removes the conduit from every lineage-to-conduit reverse index it", [
        "        - Removes the conduit from every index-to-conduit reverse map it",
    ]),
    (K, 337, "        - Adds the spell lineage to the conduit risk state.", [
        "        - Adds the spell's SpellIndex to the conduit risk state.",
    ]),
    (K, 363, "        - Removes the spell lineage from the conduit risk state.", [
        "        - Removes the spell's SpellIndex from the conduit risk state.",
    ]),
    (K, 365, "          lineage.", [
        "          SpellIndex.",
    ]),
    (K, 402, "        Update risk when structural validity changes for a lineage.", [
        "        Update risk when structural validity changes for a SpellIndex.",
    ]),
    (K, 405, "        - Updates all conduits currently referencing the lineage.", [
        "        - Updates all conduits currently referencing the SpellIndex.",
    ]),
    (K, 407, "          registered that lineage.", [
        "          registered that SpellIndex.",
    ]),
    (K, 412, "            lineage_id: Lineage identifier whose structural validity changed.", [
        "            lineage_id: SpellIndex id whose structural validity changed.",
    ]),
    (K, 439, "        - Treats resolution risk as conduit-local even when the same lineage is", [
        "        - Treats resolution risk as conduit-local even when the same SpellIndex is",
    ]),
    (K, 441, "        - Prefers lineage id tracking when the current spell id can be folded", [
        "        - Prefers SpellIndex id tracking when the current spell id can be folded",
    ]),
    (K, 442, "          back onto a known lineage; otherwise falls back to a spell-version key.", [
        "          back onto a known SpellIndex; otherwise falls back to a spell-version key.",
    ]),
    (K, 468, "        Track one spell's lineage in a conduit's risk bucket without refreshing the Book flag.", [
        "        Track one spell's SpellIndex in a conduit's risk bucket without refreshing the Book flag.",
    ]),
    (K, 474, "            - Adds the lineage to the bucket and to the lineage-to-conduit index,", [
        "            - Adds the SpellIndex to the bucket and to the index-to-conduit map,",
    ]),
    (K, 476, "              recomputes the lineage's structural and resolution risk from the", [
        "              recomputes the SpellIndex's structural and resolution risk from the",
    ]),
    (K, 479, "              is missing, the spell has no lineage (cleaned), or the conduit has", [
        "              is missing, the spell has no SpellIndex (cleaned), or the conduit has",
    ]),
    (K, 484, "            spell: Spell whose lineage is tracked.", [
        "            spell: Spell whose SpellIndex is tracked.",
    ]),
    (K, 487, "            bool: True when the bucket tracked the lineage, so a refresh is due.", [
        "            bool: True when the bucket tracked the SpellIndex, so a refresh is due.",
    ]),
    (K, 536, "        Resolve the stable lineage id for a spell, if available.", [
        "        Resolve the stable SpellIndex id for a spell, if available.",
    ]),
    (K, 541, "            Optional[str]: Lineage id or None if unavailable.", [
        "            Optional[str]: SpellIndex id or None if unavailable.",
    ]),
    (K, 549, "        Resolve a lineage id from a current spell_id.", [
        "        Resolve a SpellIndex id from a current spell_id.",
    ]),
    (K, 553, "        lineage.", [
        "        SpellIndex.",
    ]),
    (K, 558, "            Optional[str]: Lineage id or None if unavailable.", [
        "            Optional[str]: SpellIndex id or None if unavailable.",
    ]),
    (K, 575, "                spell is cleaned, or SpellValidity.unknown when no lineage state", [
        "                spell is cleaned, or SpellValidity.unknown when no SpellIndex state",
    ]),
    (K, 620, "        Update the structural-risk set for one conduit/lineage pair.", [
        "        Update the structural-risk set for one conduit/SpellIndex pair.",
    ]),
    (K, 624, "            lineage_id: Lineage identifier to mark risky or safe.", [
        "            lineage_id: SpellIndex id to mark risky or safe.",
    ]),
    (K, 646, "        lineage can be structurally fine but still need conduit-local", [
        "        SpellIndex can be structurally fine but still need conduit-local",
    ]),
    (K, 651, "            lineage_key: Lineage id or spell id key for tracking.", [
        "            lineage_key: SpellIndex id or spell id key for tracking.",
    ]),
    (K, 669, "        excluded - a `spell:<id>` key, or a lineage whose registered state does", [
        "        excluded - a `spell:<id>` key, or a SpellIndex whose registered state does",
    ]),
    (K, 674, "            - The risk sets are read, never changed: a flagged lineage stays in", [
        "            - The risk sets are read, never changed: a flagged SpellIndex stays in",
    ]),
    (K, 677, "              published set of flagged lineages is read outside it, with no lock", [
        "              published set of flagged spell indexes is read outside it, with no lock",
    ]),
    (K, 707, "        A lineage whose registered state carries `SpellState.non_resolvable` is", [
        "        A SpellIndex whose registered state carries `SpellState.non_resolvable` is",
    ]),
    (K, 711, "        the gate. A `spell:<id>` key (a verdict not folded onto a lineage) and a", [
        "        the gate. A `spell:<id>` key (a verdict not folded onto a SpellIndex) and a",
    ]),
    (K, 712, "        lineage with no registered state (removed, and not yet dropped by", [
        "        SpellIndex with no registered state (removed, and not yet dropped by",
    ]),
    (K, 715, "        The registry publishes the flagged lineages as one immutable set", [
        "        The registry publishes the flagged spell indexes as one immutable set",
    ]),
    (K, 726, "            every key is a flagged lineage.", [
        "            every key is a flagged SpellIndex.",
    ]),
]
