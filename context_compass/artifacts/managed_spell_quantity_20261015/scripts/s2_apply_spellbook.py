"""S2: the managed options on Spellbook.bind / bind_inactive. Run from the repository root."""
import pathlib

path = pathlib.Path("src/melder/aether/spellbook/spellbook.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    """Replace exactly one occurrence of `old`."""
    global text
    count = text.count(old)
    assert count == 1, (count, old[:80])
    text = text.replace(old, new, 1)


replace_once(
    "    ClassVar,\n"
    "    Optional,\n"
    ")\n",
    "    ClassVar,\n"
    "    Optional,\n"
    "    Union,\n"
    ")\n",
)
replace_once(
    "    from melder.aether.conduit.conduit import Conduit\n"
    "    from melder.crystallizer.crystallizer import Crystallizer\n",
    "    from melder.aether.conduit.conduit import Conduit\n"
    "    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n"
    "    from melder.crystallizer.crystallizer import Crystallizer\n",
)

PARAMS = (
    "            managed_spell_mode: Optional[Union[ManagedSpellMode, str]] = None,\n"
    "            managed_spell_limit: Optional[int] = None,\n"
    "            managed_spell_timeout_seconds: Optional[float] = None,\n"
    "            managed_spell_reset_methods: Optional[Sequence[str]] = None,\n"
)
FORWARD = (
    "                    managed_spell_mode=managed_spell_mode,\n"
    "                    managed_spell_limit=managed_spell_limit,\n"
    "                    managed_spell_timeout_seconds=managed_spell_timeout_seconds,\n"
    "                    managed_spell_reset_methods=managed_spell_reset_methods,\n"
)
ARGS_DOC = (
    "            managed_spell_mode (Optional[Union[ManagedSpellMode, str]]):\n"
    "                Pool policy of an `Existence.managed_spell_quantity` binding: elastic (default),\n"
    "                limited_quantity or queue - a ManagedSpellMode member or its name.\n"
    "            managed_spell_limit (Optional[int]):\n"
    "                elastic: the most idle objects kept (default 256); limited_quantity and queue: the\n"
    "                most objects alive at once (required). An int >= 1.\n"
    "            managed_spell_timeout_seconds (Optional[float]):\n"
    "                queue only, required there: how long a lease waits for a release before it raises.\n"
    "            managed_spell_reset_methods (Optional[Sequence[str]]):\n"
    "                Names of zero-argument methods of the class run, in order, on every release.\n"
    "                The four managed options must stay None on any other existence; all four are part\n"
    "                of a managed spell's id.\n"
)

# bind_inactive -------------------------------------------------------------------------------------------------
replace_once(
    "            disposal_method_names: Sequence[str] | None = None,\n"
    "            profile: str = \"general\",\n"
    "            resolvable: bool = True,\n"
    "            **kwargs: Any,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Public API\n"
    "\n"
    "        Bind a spell as an INACTIVE member of an existing owned `spell_index`.\n",
    "            disposal_method_names: Sequence[str] | None = None,\n"
    "            profile: str = \"general\",\n"
    "            resolvable: bool = True,\n"
    + PARAMS +
    "            **kwargs: Any,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Public API\n"
    "\n"
    "        Bind a spell as an INACTIVE member of an existing owned `spell_index`.\n",
)
replace_once(
    "            resolvable (bool):\n"
    "                Native capability of this parked version, independent of index selection.\n"
    "                Defaults to True; False retains existing naming and lifecycle restrictions.\n"
    "            **kwargs:\n"
    "                Optional lifecycle hooks (pre/activation/post).\n",
    "            resolvable (bool):\n"
    "                Native capability of this parked version, independent of index selection.\n"
    "                Defaults to True; False retains existing naming and lifecycle restrictions.\n"
    + ARGS_DOC +
    "                A parked managed version keeps its own options.\n"
    "            **kwargs:\n"
    "                Optional lifecycle hooks (pre/activation/post).\n",
)
replace_once(
    "            TypeError:\n"
    "                If resolvable is not a bool or the target violates Bind admission rules.\n"
    "            HookExecutionError:\n"
    "                A Book bind callback failed. Activation failure cleans its\n"
    "                unpublished allocation; post failure does not undo registration.\n",
    "            TypeError:\n"
    "                If resolvable is not a bool or the target violates Bind admission rules,\n"
    "                including a managed option of the wrong type or a managed non-class.\n"
    "            ValueError:\n"
    "                If a managed option is malformed or set on another existence.\n"
    "            HookExecutionError:\n"
    "                A Book bind callback failed. Activation failure cleans its\n"
    "                unpublished allocation; post failure does not undo registration.\n",
)

# bind ----------------------------------------------------------------------------------------------------------
replace_once(
    "            disposal_method_names: Sequence[str] | None = None,\n"
    "            profile: str = \"general\",\n"
    "            resolvable: bool = True,\n"
    "            **kwargs: Any,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Bind a spell into the Spellbook for future instantiation and dependency\n",
    "            disposal_method_names: Sequence[str] | None = None,\n"
    "            profile: str = \"general\",\n"
    "            resolvable: bool = True,\n"
    + PARAMS +
    "            **kwargs: Any,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Bind a spell into the Spellbook for future instantiation and dependency\n",
)
# (The Args entries go before the **kwargs entry of Spellbook.bind's docstring.)
marker = (
    "            **kwargs:\n"
    "                Optional application-object lifecycle hooks, executed during Meld\n"
)
replace_once(marker, ARGS_DOC + marker)
replace_once(
    "                lambda, or an existing object instance.\n"
    "                Also raised when resolvable is not a bool.\n",
    "                lambda, or an existing object instance.\n"
    "                Also raised when resolvable is not a bool, when a managed option has the\n"
    "                wrong type, or when a managed binding targets a non-class.\n"
    "            ValueError:\n"
    "                If a managed option is malformed or set on another existence.\n",
)

# Both bodies forward the options right after `resolvable=resolvable,` in the Bind call.
old_forward = (
    "                    profile=profile,\n"
    "                    resolvable=resolvable,\n"
    "                    _lifecycle_hooks=bind_hooks,\n"
)
assert text.count(old_forward) == 2, text.count(old_forward)
text = text.replace(
    old_forward,
    "                    profile=profile,\n"
    "                    resolvable=resolvable,\n"
    + FORWARD +
    "                    _lifecycle_hooks=bind_hooks,\n",
)
path.write_text(text, encoding="utf-8", newline="\n")
print("spellbook.py edited")
