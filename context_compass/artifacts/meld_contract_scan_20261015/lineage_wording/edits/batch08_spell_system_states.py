"""Hand edits, batch 08: dev_ops/spell_system_states/spell_system_states.py (melder_1, 2026-10-18).

SpellSystemStates keeps one SpellSystemState per SpellIndex (keyed by the index id); every "lineage" in its docstrings
and comments means that SpellIndex. Long lines take "index" (unambiguous in this registry, whose verbs are
`register_index` / `unregister_index`) so they stay within 120 characters. Kept: `Meld._ensure_lineage_resolvable`
(121), an identifier.
"""
S = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"

EDITS = [
    (S, 68, "          lineage downstream of the notched one revalidates at its next meld", [
        "          SpellIndex downstream of the notched one revalidates at its next meld",
    ]),
    (S, 79, "        the binding key each lineage was registered under, per-conduit", [
        "        the binding key each SpellIndex was registered under, per-conduit",
    ]),
    (S, 81, "        lineages flagged `SpellState.non_resolvable`.", [
        "        spell indexes flagged `SpellState.non_resolvable`.",
    ]),
    (S, 92, "        Unregistering a lineage notifies `RiskManager` to force validation", [
        "        Unregistering a SpellIndex notifies `RiskManager` to force validation",
    ]),
    (S, 104, "        lineages as one immutable set (`non_resolvable_index_ids`), which", [
        "        spell indexes as one immutable set (`non_resolvable_index_ids`), which",
    ]),
    (S, 130, "        genuinely impacted lineages. The separate collection-dependency and", [
        "        genuinely impacted spell indexes. The separate collection-dependency and",
    ]),
    (S, 205, "        # The binding key of each lineage's selected version (`register_index(binding_key=...)`): the contract key a", [
        "        # The binding key of each index's selected version (`register_index(binding_key=...)`): the contract key a",
    ]),
    (S, 206, "        # SpellContract consumer of that lineage declares, read by the downstream walk (`_mark_dependents_locked`).", [
        "        # SpellContract consumer of that index declares, read by the downstream walk (`_mark_dependents_locked`).",
    ]),
    (S, 209, "        # The lineages whose state carries SpellState.non_resolvable, replaced", [
        "        # The spell indexes whose state carries SpellState.non_resolvable, replaced",
    ]),
    (S, 377, "          lineage refreshes its Book flag with the new flag - a borrower whose", [
        "          SpellIndex refreshes its Book flag with the new flag - a borrower whose",
    ]),
    (S, 379, "        - Keep the published set of flagged lineages in step with the flag", [
        "        - Keep the published set of flagged spell indexes in step with the flag",
    ]),
    (S, 382, "        - Record `binding_key` as the lineage's binding key when one is given;", [
        "        - Record `binding_key` as the SpellIndex's binding key when one is given;",
    ]),
    (S, 385, "          consumers of a lineage through this key, because a consumer declares", [
        "          consumers of a SpellIndex through this key, because a consumer declares",
    ]),
    (S, 386, "          the key, not an edge to the lineage.", [
        "          the key, not an edge to the SpellIndex.",
    ]),
    (S, 405, "                ownership transfer's registrations keep the lineage's key).", [
        "                ownership transfer's registrations keep the SpellIndex's key).",
    ]),
    (S, 409, "                The lineage's live state.", [
        "                The SpellIndex's live state.",
    ]),
    (S, 497, "                # holding this lineage about the changed flag here.", [
        "                # holding this SpellIndex about the changed flag here.",
    ]),
    (S, 520, "                The lineage's live state.", [
        "                The SpellIndex's live state.",
    ]),
    (S, 538, "        Put `index_id` in or out of the published set of flagged lineages; caller holds `_lock`.", [
        "        Put `index_id` in or out of the published set of flagged spell indexes; caller holds `_lock`.",
    ]),
    (S, 541, "            - `member` is whether the lineage's state carries", [
        "            - `member` is whether the SpellIndex's state carries",
    ]),
    (S, 548, "                Spell-index id (the lineage id).", [
        "                Spell-index id (`SpellIndex.id`).",
    ]),
    (S, 550, "                Whether the lineage belongs in the set.", [
        "                Whether the SpellIndex belongs in the set.",
    ]),
    (S, 599, "        Return whether the lineage registered under `index_id` carries `flag`.", [
        "        Return whether the SpellIndex registered under `index_id` carries `flag`.",
    ]),
    (S, 602, "            The per-lineage flag read. It reads the registry rather than a held", [
        "            The per-index flag read. It reads the registry rather than a held",
    ]),
    (S, 603, "            state reference, so a lineage removed meanwhile answers False.", [
        "            state reference, so a SpellIndex removed meanwhile answers False.",
    ]),
    (S, 616, "                Spell-index id (the lineage id).", [
        "                Spell-index id (`SpellIndex.id`).",
    ]),
    (S, 646, "        Return the lineages whose state carries `SpellState.non_resolvable`.", [
        "        Return the spell indexes whose state carries `SpellState.non_resolvable`.",
    ]),
    (S, 654, "            - Exactly the registered lineages whose state carries the flag:", [
        "            - Exactly the registered spell indexes whose state carries the flag:",
    ]),
    (S, 655, "              `register_index` puts a lineage in or out right after it writes the", [
        "              `register_index` puts a SpellIndex in or out right after it writes the",
    ]),
    (S, 657, "              out, so a removed lineage is never in it.", [
        "              out, so a removed SpellIndex is never in it.",
    ]),
    (S, 923, "        Mark for revalidation every lineage downstream of `index_ids`, by registry edge or by contract key.", [
        "        Mark for revalidation every index downstream of `index_ids`, by registry edge or by contract key.",
    ]),
    (S, 926, "            A notch changes what every dependent of the notched lineage resolves: a dependent's plan names the", [
        "            A notch changes what every dependent of the notched index resolves: a dependent's plan names the",
    ]),
    (S, 928, "            notched lineage, so each dependent's next meld rechecks its structure and rebuilds against the", [
        "            notched index, so each dependent's next meld rechecks its structure and rebuilds against the",
    ]),
    (S, 933, "            - The walk starts from the given lineages (the seeds) and follows, from every lineage it reaches,", [
        "            - The walk starts from the given indexes (the seeds) and follows, from every index it reaches,",
    ]),
    (S, 935, "              the SpellContract consumers, in every Spellbook of the frame, of the binding key that lineage was", [
        "              the SpellContract consumers, in every Spellbook of the frame, of the binding key that index was",
    ]),
    (S, 937, "              edge. A lineage with no recorded key is followed by its edges only.", [
        "              edge. A SpellIndex with no recorded key is followed by its edges only.",
    ]),
    (S, 938, "            - A lineage reached by an edge gets `mark_transitively_dirty()` (gated, `impacted_by_dependency`,", [
        "            - An index reached by an edge gets `mark_transitively_dirty()` (gated, `impacted_by_dependency`,",
    ]),
    (S, 943, "              no registered state is passed over. Each lineage is visited once, so a cycle of edges or contracts", [
        "              no registered state is passed over. Each index is visited once, so a cycle of edges or contracts",
    ]),
    (S, 945, "            - Every marked lineage joins the dirty set. `set_validity` publishes a validity only when it", [
        "            - Every marked index joins the dirty set. `set_validity` publishes a validity only when it",
    ]),
    (S, 946, "              changes, so a walk over lineages already gated publishes nothing.", [
        "              changes, so a walk over indexes already gated publishes nothing.",
    ]),
    (S, 950, "                Spell-index ids (lineage ids) whose change starts the walk; empty and None ids are ignored.", [
        "                Spell-index ids whose change starts the walk; empty and None ids are ignored.",
    ]),
    (S, 954, "                The lineage ids this call marked, seeds excluded; empty when nothing is downstream.", [
        "                The spell-index ids this call marked, seeds excluded; empty when nothing is downstream.",
    ]),
    (S, 975, "        Walk downstream of `seeds` and mark every lineage reached; the caller holds `_lock`.", [
        "        Walk downstream of `seeds` and mark every index reached; the caller holds `_lock`.",
    ]),
    (S, 982, "            - Follows reverse edges and the contract consumers of each reached lineage's binding key, across", [
        "            - Follows reverse edges and the contract consumers of each reached index's binding key, across",
    ]),
    (S, 983, "              every Spellbook, visiting each lineage once (see `mark_dependents_for_revalidation`).", [
        "              every Spellbook, visiting each index once (see `mark_dependents_for_revalidation`).",
    ]),
    (S, 984, "            - Marks after the walk, so a lineage's mark knows every way it was reached: the contract mark", [
        "            - Marks after the walk, so an index's mark knows every way it was reached: the contract mark",
    ]),
    (S, 985, "              first, then the edge mark. Seeds are never marked; lineages with no registered state are", [
        "              first, then the edge mark. Seeds are never marked; indexes with no registered state are",
    ]),
    (S, 986, "              skipped; every marked lineage joins `_dirty_indexes`.", [
        "              skipped; every marked index joins `_dirty_indexes`.",
    ]),
    (S, 990, "                Non-empty lineage ids the walk starts from.", [
        "                Non-empty spell-index ids the walk starts from.",
    ]),
    (S, 994, "                The lineage ids marked.", [
        "                The spell-index ids marked.",
    ]),
    (S, 1157, "        - Take the lineage out of the published set of flagged lineages.", [
        "        - Take the SpellIndex out of the published set of flagged spell indexes.",
    ]),
    (S, 1160, "          forget the lineage's binding key.", [
        "          forget the SpellIndex's binding key.",
    ]),
    (S, 1208, "            # A removed lineage is never in the published flagged set.", [
        "            # A removed SpellIndex is never in the published flagged set.",
    ]),
    (S, 1327, "            The per-conduit axis of lineage retirement. `unregister_index` and", [
        "            The per-conduit axis of SpellIndex retirement. `unregister_index` and",
    ]),
    (S, 1734, "            Set[str]: The consumers this call gated (the lineages the walk-on", [
        "            Set[str]: The consumers this call gated (the spell indexes the walk-on",
    ]),
]
