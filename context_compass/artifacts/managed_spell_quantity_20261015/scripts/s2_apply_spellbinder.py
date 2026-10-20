"""S2: SpellBinder.as_managed_spell_quantity. Run from the repository root."""
import pathlib

path = pathlib.Path("src/melder/aether/spellbook/spellbinder.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    """Replace exactly one occurrence of `old`."""
    global text
    count = text.count(old)
    assert count == 1, (count, old[:80])
    text = text.replace(old, new, 1)


replace_once(
    "from typing import TYPE_CHECKING, Any\n"
    "\n"
    "if TYPE_CHECKING:\n"
    "    from melder.aether.spellbook.spell import Spell\n",
    "from collections.abc import Sequence\n"
    "from typing import TYPE_CHECKING, Any, Optional, Union\n"
    "\n"
    "if TYPE_CHECKING:\n"
    "    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n"
    "    from melder.aether.spellbook.spell import Spell\n",
)
replace_once(
    "            **kwargs:\n"
    "                Passthrough bind-time keyword arguments, including lifecycle hooks.\n",
    "            **kwargs:\n"
    "                Passthrough bind-time keyword arguments, including lifecycle hooks and\n"
    "                the managed options (`managed_spell_mode`, `managed_spell_limit`,\n"
    "                `managed_spell_timeout_seconds`, `managed_spell_reset_methods`).\n",
)
anchor = (
    "        self.check_cleaned()\n"
    "        with self._lock:\n"
    "            self._require_spellbook()\n"
    "            self._existence = Existence.unique_per_spell_space\n"
    "        return self\n"
)
replace_once(
    anchor,
    anchor
    + "\n"
    "    def as_managed_spell_quantity(\n"
    "            self,\n"
    "            mode: Optional[Union[ManagedSpellMode, str]] = None,\n"
    "            *,\n"
    "            limit: Optional[int] = None,\n"
    "            timeout_seconds: Optional[float] = None,\n"
    "            reset_methods: Optional[Sequence[str]] = None,\n"
    "    ) -> SpellBinder:\n"
    "        \"\"\"\n"
    "        Configures the spell as **Managed** (objects leased from a pool the root owns).\n"
    "\n"
    "        **Behaviour:**\n"
    "        - A meld, or an injection into a constructor, takes an idle object from the spell's pool or builds\n"
    "          one when the mode allows; the holder gives it back with `ReleaseManagedSpell.release(obj)`.\n"
    "        - `mode`: elastic (default; always builds, keeps up to `limit` idle objects, default 256),\n"
    "          limited_quantity (at most `limit` alive, refuses at the limit) or queue (at most `limit` alive,\n"
    "          waits up to `timeout_seconds` for a release, then refuses).\n"
    "\n"
    "        **Use Case:**\n"
    "        - Objects that are expensive to build and cheap to reset (loggers, buffers, connections).\n"
    "\n"
    "        Contract:\n"
    "            - Sets the existence to `Existence.managed_spell_quantity` and stages the four options under\n"
    "              their bind names (`managed_spell_mode`, `managed_spell_limit`,\n"
    "              `managed_spell_timeout_seconds`, `managed_spell_reset_methods`) in the passthrough payload,\n"
    "              replacing any staged earlier; `finalize()` sends them to `Spellbook.bind`, where Bind\n"
    "              validates them. Values are staged as given.\n"
    "            - A later `as_unique()` (or any other existence) keeps the staged options, so `finalize()`\n"
    "              refuses them through Bind unless every option is None.\n"
    "\n"
    "        Args:\n"
    "            mode: A `ManagedSpellMode` member or its name; None means elastic.\n"
    "            limit: elastic: the most idle objects kept; limited_quantity and queue: the most objects\n"
    "                alive at once (required there).\n"
    "            timeout_seconds: queue only, required there: how long a lease waits for a release.\n"
    "            reset_methods: Names of zero-argument methods of the class run, in order, on every release.\n"
    "\n"
    "        Raises:\n"
    "            RuntimeError: If the binder has been cleaned or its Spellbook weak reference is dead.\n"
    "\n"
    "        Returns:\n"
    "            SpellBinder: This binder, for fluent chaining. Call finalize() to submit the\n"
    "                assembled registration to the Spellbook.\n"
    "        \"\"\"\n"
    "        self.check_cleaned()\n"
    "        with self._lock:\n"
    "            self._require_spellbook()\n"
    "            self._existence = Existence.managed_spell_quantity\n"
    "            self._kwargs[\"managed_spell_mode\"] = mode\n"
    "            self._kwargs[\"managed_spell_limit\"] = limit\n"
    "            self._kwargs[\"managed_spell_timeout_seconds\"] = timeout_seconds\n"
    "            self._kwargs[\"managed_spell_reset_methods\"] = reset_methods\n"
    "        return self\n",
)
path.write_text(text, encoding="utf-8", newline="\n")
print("spellbinder.py edited")
