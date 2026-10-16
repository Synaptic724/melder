"""S2: the managed options on Spell (slots, constructor, properties, cleanup). Run from the repository root."""
import pathlib

path = pathlib.Path("src/melder/aether/spellbook/spell.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    """Replace exactly one occurrence of `old`."""
    global text
    count = text.count(old)
    assert count == 1, (count, old[:80])
    text = text.replace(old, new, 1)


replace_once(
    "    from melder.aether.spellbook.spellbook import Spellbook\n"
    "    from melder.utilities.synchronization.creation_gate import CreationGate\n",
    "    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n"
    "    from melder.aether.spellbook.spellbook import Spellbook\n"
    "    from melder.utilities.synchronization.creation_gate import CreationGate\n",
)
replace_once(
    "    - Resolution capability is fixed per bound version and exposed by the\n"
    "      read-only resolvable property, independently of activity and compilation state.\n",
    "    - Resolution capability is fixed per bound version and exposed by the\n"
    "      read-only resolvable property, independently of activity and compilation state.\n"
    "    - The managed options of an `Existence.managed_spell_quantity` binding (mode, limit,\n"
    "      queue timeout, reset method names) are fixed per bound version the same way, as\n"
    "      Bind normalized and hashed them, and exposed by read-only properties.\n",
)
replace_once(
    '        "implemented_protocols",\n'
    '        "_removal_lock",\n'
    "    ]\n",
    '        "implemented_protocols",\n'
    '        "_removal_lock",\n'
    '        "_managed_spell_mode",\n'
    '        "_managed_spell_limit",\n'
    '        "_managed_spell_timeout_seconds",\n'
    '        "_managed_spell_reset_methods",\n'
    "    ]\n",
)
replace_once(
    "            implemented_protocols: tuple[type, ...] = (),\n"
    "            **kwargs: Any,\n"
    "    ) -> None:\n",
    "            implemented_protocols: tuple[type, ...] = (),\n"
    "            managed_spell_mode: Optional[ManagedSpellMode] = None,\n"
    "            managed_spell_limit: Optional[int] = None,\n"
    "            managed_spell_timeout_seconds: Optional[float] = None,\n"
    "            managed_spell_reset_methods: tuple[str, ...] = (),\n"
    "            **kwargs: Any,\n"
    "    ) -> None:\n",
)
replace_once(
    "            implemented_protocols (tuple[type, ...]): The Protocol(s) Bind structurally checked\n"
    "                this spell against: `(spellframe,)` for a contract frame, else empty.\n",
    "            implemented_protocols (tuple[type, ...]): The Protocol(s) Bind structurally checked\n"
    "                this spell against: `(spellframe,)` for a contract frame, else empty.\n"
    "            managed_spell_mode (Optional[ManagedSpellMode]): The pool policy of a managed binding,\n"
    "                as Bind normalized it; None on any other existence.\n"
    "            managed_spell_limit (Optional[int]): Elastic idle cap, or the most objects alive for\n"
    "                limited_quantity and queue; None on any other existence.\n"
    "            managed_spell_timeout_seconds (Optional[float]): Queue wait in seconds; None otherwise.\n"
    "            managed_spell_reset_methods (tuple[str, ...]): Reset method names, run in order on every\n"
    "                release; empty when none were named or the spell is not managed.\n",
)
replace_once(
    "        self._resolvable: bool = resolvable\n",
    "        self._resolvable: bool = resolvable\n"
    "        # Managed options (Existence.managed_spell_quantity): normalized by Bind and hashed into spell_id,\n"
    "        # read-only per-version policy like `_resolvable`; None / None / None / () on any other existence.\n"
    "        # The spell's pool is composed from them when its owner store is stamped (S3).\n"
    "        self._managed_spell_mode: Optional[ManagedSpellMode] = managed_spell_mode\n"
    "        self._managed_spell_limit: Optional[int] = managed_spell_limit\n"
    "        self._managed_spell_timeout_seconds: Optional[float] = managed_spell_timeout_seconds\n"
    "        self._managed_spell_reset_methods: tuple[str, ...] = managed_spell_reset_methods\n",
)
replace_once(
    "            del self._resolvable\n"
    "            del self._mutation_override\n",
    "            del self._resolvable\n"
    "            del self._managed_spell_mode\n"
    "            del self._managed_spell_limit\n"
    "            del self._managed_spell_timeout_seconds\n"
    "            del self._managed_spell_reset_methods\n"
    "            del self._mutation_override\n",
)
replace_once(
    "        self.check_cleaned()\n"
    "        return self._resolvable\n",
    "        self.check_cleaned()\n"
    "        return self._resolvable\n"
    "\n"
    "    @property\n"
    "    def managed_spell_mode(self) -> Optional[ManagedSpellMode]:\n"
    "        \"\"\"\n"
    "        Return the pool policy of this managed version.\n"
    "\n"
    "        Contract:\n"
    "            Set once at bind (default elastic for a managed binding) and part of the spell id. No live\n"
    "            setter; changing it takes another binding.\n"
    "\n"
    "        Returns:\n"
    "            Optional[ManagedSpellMode]: The mode, or None when the spell is not\n"
    "            `Existence.managed_spell_quantity`.\n"
    "\n"
    "        Raises:\n"
    "            RuntimeError: If this Spell has been cleaned.\n"
    "        \"\"\"\n"
    "        self.check_cleaned()\n"
    "        return self._managed_spell_mode\n"
    "\n"
    "    @property\n"
    "    def managed_spell_limit(self) -> Optional[int]:\n"
    "        \"\"\"\n"
    "        Return the limit of this managed version.\n"
    "\n"
    "        Contract:\n"
    "            elastic: the most idle objects its pool keeps (default 256). limited_quantity and queue: the\n"
    "            most objects alive at once, idle plus out. Set once at bind and part of the spell id.\n"
    "\n"
    "        Returns:\n"
    "            Optional[int]: The limit, or None when the spell is not managed.\n"
    "\n"
    "        Raises:\n"
    "            RuntimeError: If this Spell has been cleaned.\n"
    "        \"\"\"\n"
    "        self.check_cleaned()\n"
    "        return self._managed_spell_limit\n"
    "\n"
    "    @property\n"
    "    def managed_spell_timeout_seconds(self) -> Optional[float]:\n"
    "        \"\"\"\n"
    "        Return how long a queue lease of this version waits for a release.\n"
    "\n"
    "        Contract:\n"
    "            Set once at bind for the queue mode and part of the spell id; always None for elastic and\n"
    "            limited_quantity, which never wait.\n"
    "\n"
    "        Returns:\n"
    "            Optional[float]: Seconds, or None.\n"
    "\n"
    "        Raises:\n"
    "            RuntimeError: If this Spell has been cleaned.\n"
    "        \"\"\"\n"
    "        self.check_cleaned()\n"
    "        return self._managed_spell_timeout_seconds\n"
    "\n"
    "    @property\n"
    "    def managed_spell_reset_methods(self) -> tuple[str, ...]:\n"
    "        \"\"\"\n"
    "        Return the reset method names of this managed version.\n"
    "\n"
    "        Contract:\n"
    "            Zero-argument methods of the class, run in this order on every release before the object\n"
    "            is leased again. Set once at bind and part of the spell id.\n"
    "\n"
    "        Returns:\n"
    "            tuple[str, ...]: The names; empty when none were named or the spell is not managed.\n"
    "\n"
    "        Raises:\n"
    "            RuntimeError: If this Spell has been cleaned.\n"
    "        \"\"\"\n"
    "        self.check_cleaned()\n"
    "        return self._managed_spell_reset_methods\n",
)
path.write_text(text, encoding="utf-8", newline="\n")
print("spell.py edited")
