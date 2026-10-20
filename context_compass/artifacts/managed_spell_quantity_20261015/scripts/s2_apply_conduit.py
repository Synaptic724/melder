"""S2: Conduit.bind / bind_inactive forward the managed options. Run from the repository root."""
import pathlib

path = pathlib.Path("src/melder/aether/conduit/conduit.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    """Replace exactly one occurrence of `old`."""
    global text
    count = text.count(old)
    assert count == 1, (count, old[:80])
    text = text.replace(old, new, 1)


replace_once(
    "    from melder.aether.spellbook.spell import Spell\n"
    "    from melder.aether.spellbook.bind.spell_index import SpellIndex\n",
    "    from melder.aether.spellbook.spell import Spell\n"
    "    from melder.aether.spellbook.bind.spell_index import SpellIndex\n"
    "    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n",
)
PARAMS = (
    "            managed_spell_mode: Optional[Union[ManagedSpellMode, str]] = None,\n"
    "            managed_spell_limit: Optional[int] = None,\n"
    "            managed_spell_timeout_seconds: Optional[float] = None,\n"
    "            managed_spell_reset_methods: Optional[Sequence[str]] = None,\n"
)
ARGS_DOC = (
    "            managed_spell_mode (Optional[Union[ManagedSpellMode, str]]):\n"
    "                Pool policy of an `Existence.managed_spell_quantity` binding (elastic by default),\n"
    "                forwarded unchanged to Spellbook, which validates it with the other three.\n"
    "            managed_spell_limit (Optional[int]):\n"
    "                elastic: the most idle objects kept (default 256); limited_quantity and queue: the\n"
    "                most objects alive at once (required).\n"
    "            managed_spell_timeout_seconds (Optional[float]):\n"
    "                queue only, required there: how long a lease waits for a release.\n"
    "            managed_spell_reset_methods (Optional[Sequence[str]]):\n"
    "                Zero-argument methods of the class run, in order, on every release. The four managed\n"
    "                options must stay None on any other existence.\n"
)
FORWARD = (
    "            managed_spell_mode=managed_spell_mode,\n"
    "            managed_spell_limit=managed_spell_limit,\n"
    "            managed_spell_timeout_seconds=managed_spell_timeout_seconds,\n"
    "            managed_spell_reset_methods=managed_spell_reset_methods,\n"
)

# bind
replace_once(
    "            profile: str = \"general\",\n"
    "            resolvable: bool = True,\n"
    "            **kwargs: Any,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Bind a spell into the Spellbook for future instantiation and dependency injection.\n",
    "            profile: str = \"general\",\n"
    "            resolvable: bool = True,\n"
    + PARAMS +
    "            **kwargs: Any,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Bind a spell into the Spellbook for future instantiation and dependency injection.\n",
)
replace_once(
    "            resolvable (bool):\n"
    "                Native per-version resolution capability, forwarded unchanged to Spellbook.\n"
    "                Defaults to True; False retains existing binding and lifetime rules.\n"
    "            **kwargs:\n"
    "                Optional lifecycle hooks and related bind-time metadata.\n",
    "            resolvable (bool):\n"
    "                Native per-version resolution capability, forwarded unchanged to Spellbook.\n"
    "                Defaults to True; False retains existing binding and lifetime rules.\n"
    + ARGS_DOC +
    "            **kwargs:\n"
    "                Optional lifecycle hooks and related bind-time metadata.\n",
)
replace_once(
    "            TypeError:\n"
    "                If invalid hook types or a non-bool resolvable value are provided.\n"
    "\n"
    "        \"\"\"\n",
    "            TypeError:\n"
    "                If invalid hook types or a non-bool resolvable value are provided, a managed\n"
    "                option has the wrong type, or a managed binding targets a non-class.\n"
    "            ValueError:\n"
    "                If a managed option is malformed or set on another existence.\n"
    "\n"
    "        \"\"\"\n",
)
replace_once(
    "            profile=profile,\n"
    "            resolvable=resolvable,\n"
    "            permissions=permissions,\n"
    "            **kwargs,\n"
    "        )\n",
    "            profile=profile,\n"
    "            resolvable=resolvable,\n"
    "            permissions=permissions,\n"
    + FORWARD +
    "            **kwargs,\n"
    "        )\n",
)

# bind_inactive
replace_once(
    "            profile: str = \"general\",\n"
    "            resolvable: bool = True,\n"
    "            **kwargs: Any,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Public API\n"
    "\n"
    "        Stage a spell as an INACTIVE member of an existing owned `spell_index`,\n",
    "            profile: str = \"general\",\n"
    "            resolvable: bool = True,\n"
    + PARAMS +
    "            **kwargs: Any,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Public API\n"
    "\n"
    "        Stage a spell as an INACTIVE member of an existing owned `spell_index`,\n",
)
replace_once(
    "            resolvable (bool):\n"
    "                Native capability of this parked version, forwarded unchanged to Spellbook.\n"
    "                Defaults to True and is independent of active index selection.\n"
    "            **kwargs:\n"
    "                Optional lifecycle hooks (pre/activation/post).\n",
    "            resolvable (bool):\n"
    "                Native capability of this parked version, forwarded unchanged to Spellbook.\n"
    "                Defaults to True and is independent of active index selection.\n"
    + ARGS_DOC +
    "                A parked managed version keeps its own options.\n"
    "            **kwargs:\n"
    "                Optional lifecycle hooks (pre/activation/post).\n",
)
replace_once(
    "            TypeError:\n"
    "                If resolvable is not a bool or Bind rejects the target.\n"
    "        \"\"\"\n",
    "            TypeError:\n"
    "                If resolvable is not a bool or Bind rejects the target (a managed option of\n"
    "                the wrong type or a managed non-class included).\n"
    "            ValueError:\n"
    "                If a managed option is malformed or set on another existence.\n"
    "        \"\"\"\n",
)
replace_once(
    "            profile=profile,\n"
    "            resolvable=resolvable,\n"
    "            **kwargs,\n"
    "        )\n"
    "        # The new inactive member joined `spell_index`;",
    "            profile=profile,\n"
    "            resolvable=resolvable,\n"
    + FORWARD +
    "            **kwargs,\n"
    "        )\n"
    "        # The new inactive member joined `spell_index`;",
)
path.write_text(text, encoding="utf-8", newline="\n")
print("conduit.py edited")
