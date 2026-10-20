"""S2 turn-in: the running release note at 0.2.8242 (header, the managed section's bind options, packaging)."""
import pathlib

path = pathlib.Path("release_docs/next_version_release.md")
text = path.read_text(encoding="utf-8")


def swap(old: str, new: str) -> None:
    """Replace one exact passage of the note; refuse when it is missing or repeated."""
    global text
    count = text.count(old)
    assert count == 1, (count, old[:90])
    text = text.replace(old, new, 1)


swap("# Melder 0.2.8241\n", "# Melder 0.2.8242\n")

swap(
    "an argument the bind pipeline takes itself (`spell`, `existence`, `profile`, `spell_id` and the rest, 24 in all)\n"
    "raises `TypeError` naming every such key.",
    "an argument the bind pipeline takes itself (`spell`, `existence`, `profile`, `spell_id` and the rest, 28 in all,\n"
    "the four `managed_spell_*` options among them) raises `TypeError` naming every such key.",
)

swap(
    "lease reuses it. 0.2.8241 adds the member and its place in Melder's lifetime rules; the bind options, the pool, the\n"
    "release call and leasing through a meld follow, and until they land a managed binding cannot be melded.\n",
    "lease reuses it. 0.2.8241 added the member and its place in Melder's lifetime rules and 0.2.8242 adds its bind\n"
    "options; the pool, the release call and leasing through a meld follow, and until they land a managed binding\n"
    "cannot be melded.\n",
)

swap(
    "  depend on a managed one.\n"
    "\n"
    "What stays the same: the six existing members keep their values, order and rules, and no spell id changes.\n",
    "  depend on a managed one.\n"
    "\n"
    "A managed binding takes four keyword options on `Spellbook.bind` and `bind_inactive`, `Conduit.bind` and\n"
    "`bind_inactive`, `scan_bind` and `SpellBinder` (`as_managed_spell_quantity(mode, limit=..., timeout_seconds=...,\n"
    "reset_methods=...)`), and the Spell keeps them (0.2.8242):\n"
    "\n"
    "```python\n"
    "class Parser:\n"
    "    def reset(self) -> None: ...\n"
    "\n"
    "\n"
    "book.bind(\n"
    "    spell=Parser,\n"
    "    existence=\"managed_spell_quantity\",\n"
    "    managed_spell_mode=\"queue\",           # a name, or a ManagedSpellMode member\n"
    "    managed_spell_limit=8,                 # at most 8 parsers alive at once\n"
    "    managed_spell_timeout_seconds=2.5,     # a lease waits up to 2.5 s for one to come back\n"
    "    managed_spell_reset_methods=[\"reset\"],  # run on every release, in order\n"
    ")\n"
    "```\n"
    "\n"
    "- `managed_spell_mode`: `elastic` (the default) always builds when no idle object is waiting and keeps up to\n"
    "  `managed_spell_limit` idle objects (default 256); `limited_quantity` refuses at `managed_spell_limit` objects\n"
    "  alive; `queue` waits for a release, up to `managed_spell_timeout_seconds`, then refuses. The enum is\n"
    "  `ManagedSpellMode` (`melder.aether.spellbook.existence.managed_spell_mode`).\n"
    "- `managed_spell_limit` is required for `limited_quantity` and `queue`; `managed_spell_timeout_seconds` is\n"
    "  required for `queue` and refused for the other two modes.\n"
    "- `managed_spell_reset_methods` names zero-argument methods of the class.\n"
    "- `spell.managed_spell_mode`, `managed_spell_limit`, `managed_spell_timeout_seconds` and\n"
    "  `managed_spell_reset_methods` read them back (the default limit filled in); other spells answer None, None,\n"
    "  None and `()`.\n"
    "- Each option is part of a managed spell's id, so changing one binds a new version.\n"
    "\n"
    "`bind` refuses, before anything is registered and with a message that says what to change: a `managed_spell_*`\n"
    "option on another existence (`ValueError`); a managed binding of a function, method, lambda or existing object\n"
    "(`TypeError`: the pool builds instances of a class); an unknown mode; a limit that is not an int of at least 1, or\n"
    "is missing where required; a timeout where it does not apply, missing in `queue`, or not a positive finite number;\n"
    "and reset names that are not a list or tuple of method names of the class.\n"
    "\n"
    "The Crystallizer records a managed spell's options, and restore and the spell-index graft bind it with them, so\n"
    "it comes back with its own id. Records are stamped 4.2.0 (they were 4.1.0): only a managed spell's record gains\n"
    "the four keys, a 4.1 reader ignores them, and 4.1 records restore as before.\n"
    "\n"
    "What stays the same: the six existing members keep their values, order and rules; no other binding's spell id,\n"
    "Spell values or record changes; and `inspect.signature` and `typing.get_type_hints` still read the bind methods.\n",
)

swap(
    "- The internal-bind guard manifest holds 623 entries at 0.2.8238 (622 at 0.2.8227): `HolderDisposalEntry`, the\n"
    "  record that keeps a slotted object's `many` children with it, joined.\n"
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8241.\n",
    "- The internal-bind guard manifest holds 624 entries at 0.2.8242 (622 at 0.2.8227): `HolderDisposalEntry`, the\n"
    "  record that keeps a slotted object's `many` children with it, joined at 0.2.8238, and `ManagedSpellMode` at\n"
    "  0.2.8242.\n"
    "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8242.\n",
)

path.write_text(text, encoding="utf-8", newline="\n")
print("release note updated")
