"""Correct ConduitMeld's docstrings about which store each lifetime uses (docstrings only, no behaviour).

Edits src/melder/aether/conduit/meld/conduit_meld.py (CRLF). Run from the repository root; each anchor must
match exactly once.
"""
import pathlib

PATH = pathlib.Path("src/melder/aether/conduit/meld/conduit_meld.py")

EDITS = [
    (  # class contract
        "        - Uses spell-owned shared owner-creations for broad-lived existences\n"
        "          such as `unique`, `unique_per_conduit_cluster`, and\n"
        "          `unique_per_conduit_lineage`.\n",
        "        - Uses the shared store each broad-lived existence names: the Spell\n"
        "          owner's `owner_creations` for `unique`, the lineage-root store\n"
        "          (`_root_creations`) for `unique_per_conduit_lineage`, and the elected\n"
        "          leader's store (`_cluster_creations.resolved_store()`) for\n"
        "          `unique_per_conduit_cluster`.\n",
    ),
    (  # class System Context
        "        `Existence`. Refusing keeps the scoping model honest: a spellspace-scoped\n"
        "        instance is reachable only through `SpellSpace`, which enforces that it\n"
        "        is the ACTIVE spellspace for the conduit before melding at all.\n"
        "        The store split it does own is the ordinary case: caller-local\n"
        "        existences (`unique_per_conduit`, `many`) use the conduit's own store,\n"
        "        while broader-lived ones (`unique`, `unique_per_conduit_cluster`,\n"
        "        `unique_per_conduit_lineage`) resolve against shared owner storage so\n"
        "        peers in a cluster or lineage genuinely observe the same instance.\n",
        "        `Existence`. Refusing keeps the scoping model honest: a spellspace-scoped\n"
        "        instance is reachable only through a leased `SpellSpace`, which refuses\n"
        "        to meld once it is released to its pool. (Corrected 2026-09-28: this said\n"
        "        the space checks that it is the ACTIVE spellspace; there is no such\n"
        "        check.) The store split it does own is the ordinary case: caller-local\n"
        "        existences (`unique_per_conduit`, `many`) use the conduit's own store,\n"
        "        while broader-lived ones resolve against shared storage - the Spell\n"
        "        owner's store for `unique`, the lineage root's for\n"
        "        `unique_per_conduit_lineage`, the elected leader's for\n"
        "        `unique_per_conduit_cluster` - so peers in a cluster or lineage\n"
        "        genuinely observe the same instance.\n",
    ),
    (  # meld contract
        "            - Routes broader-lived existences through spell-owned shared\n"
        "              `owner_creations`.\n",
        "            - Routes broader-lived existences through their shared stores:\n"
        "              the Spell owner's `owner_creations` for `unique`, the lineage\n"
        "              root for `unique_per_conduit_lineage`, the elected leader for\n"
        "              `unique_per_conduit_cluster`.\n",
    ),
    (  # meld_existing_spell contract
        "            - Reads caller-local conduit storage for `unique_per_conduit` and\n"
        "              shared owner-creations for broader-lived existences.\n",
        "            - Reads caller-local conduit storage for `unique_per_conduit`, the\n"
        "              Spell owner's `owner_creations` for `unique`, the lineage root for\n"
        "              `unique_per_conduit_lineage` and the elected leader for\n"
        "              `unique_per_conduit_cluster` (not live while none is elected).\n",
    ),
    (  # describe_live_creation_status contract
        "            - Reports the query conduit context explicitly so callers know the\n"
        "              result is scoped to the current conduit and, where relevant, its\n"
        "              active spellspace or shared owner-creation path.\n",
        "            - Reports the query conduit context explicitly so callers know\n"
        "              whether the answer came from this conduit's store or a shared\n"
        "              store; `active_spellspace_id` is always None on this door.\n",
    ),
    (  # probe contract
        "            - `many` and `unique_per_conduit` read from caller-local conduit\n"
        "              storage.\n"
        "            - broad-lived existences read from spell-owned shared\n"
        "              `owner_creations`.\n",
        "            - `many` and `unique_per_conduit` read from caller-local conduit\n"
        "              storage; a `many` without disposal methods is never tracked and\n"
        "              reports 0.\n"
        "            - `unique` reads the Spell owner's `owner_creations`;\n"
        "              `unique_per_conduit_lineage` the lineage-root store;\n"
        "              `unique_per_conduit_cluster` the elected leader's store, and is\n"
        "              not live while no leader is elected.\n",
    ),
]

raw = PATH.read_bytes().decode("utf-8")
assert raw.count("\r\n") == raw.count("\n"), "expected a CRLF-only file"
text = raw.replace("\r\n", "\n")
for old, new in EDITS:
    assert text.count(old) == 1, (old[:60], text.count(old))
    text = text.replace(old, new)
    for line in new.split("\n"):
        assert len(line) <= 100, line
PATH.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
print("conduit_meld docstrings corrected")
