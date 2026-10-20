"""S2: scan_bind declares the managed options; ScanBindMetadata stores them; a scan replays them."""
import pathlib

path = pathlib.Path("src/melder/aether/spellbook/bind/scan.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    """Replace exactly one occurrence of `old`."""
    global text
    count = text.count(old)
    assert count == 1, (count, old[:80])
    text = text.replace(old, new, 1)


replace_once(
    "if TYPE_CHECKING:\n"
    "    from melder.aether.spellbook.spellbook import Spellbook\n",
    "if TYPE_CHECKING:\n"
    "    from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n"
    "    from melder.aether.spellbook.spellbook import Spellbook\n",
)

# A decoration-time shape check for the reset group, beside the disposal one.
replace_once(
    "def _normalize_spell_metadata(spell_metadata: Mapping[str, Any]) -> dict[str, Any]:\n",
    "def _normalize_managed_reset_methods(\n"
    "        managed_spell_reset_methods: Optional[Sequence[str]],\n"
    ") -> Optional[tuple[str, ...]]:\n"
    "    \"\"\"\n"
    "    Normalize a managed declaration's reset-method group for `scan_bind` metadata storage.\n"
    "\n"
    "    Purpose:\n"
    "        Check the group's shape where it is written and snapshot it, as disposal names are, so the group a\n"
    "        later scan replays is exactly the group written at the decoration site.\n"
    "\n"
    "    Contract:\n"
    "        - Accepts None, list, or tuple values; None means \"no reset methods\".\n"
    "        - Every element must be a `str`. A bare string is refused: Bind would read it per character.\n"
    "        - Returns an immutable tuple in the supplied order. Whether each name is a method of the class,\n"
    "          and every other managed rule, is Bind's check when the module is scanned.\n"
    "\n"
    "    Args:\n"
    "        managed_spell_reset_methods (Optional[Sequence[str]]): Reset method names or None.\n"
    "\n"
    "    Returns:\n"
    "        Optional[tuple[str, ...]]: Tuple of names if provided; otherwise None.\n"
    "\n"
    "    Raises:\n"
    "        TypeError: If the value is not None, a list or a tuple, or holds an element that is not a string.\n"
    "    \"\"\"\n"
    "    if managed_spell_reset_methods is None:\n"
    "        return None\n"
    "    if not isinstance(managed_spell_reset_methods, (list, tuple)):\n"
    "        raise TypeError(\n"
    "            \"managed_spell_reset_methods must be a list or tuple of method-name strings, got \"\n"
    "            f\"{type(managed_spell_reset_methods).__name__}. Wrap a single name in a list: ['reset'].\"\n"
    "        )\n"
    "    for method_name in managed_spell_reset_methods:\n"
    "        if not isinstance(method_name, str):\n"
    "            raise TypeError(\n"
    "                \"managed_spell_reset_methods must be a list or tuple of method-name strings; \"\n"
    "                f\"found an element of type {type(method_name).__name__}.\"\n"
    "            )\n"
    "    return tuple(managed_spell_reset_methods)\n"
    "\n"
    "\n"
    "def _normalize_spell_metadata(spell_metadata: Mapping[str, Any]) -> dict[str, Any]:\n",
)

# ScanBindMetadata --------------------------------------------------------------------------------------------
replace_once(
    "        - Per-target disposal names are stored as a tuple (or None) and replayed\n"
    "          unchanged; Bind resolves them against the Book's candidates.\n",
    "        - Per-target disposal names are stored as a tuple (or None) and replayed\n"
    "          unchanged; Bind resolves them against the Book's candidates.\n"
    "        - The four managed options (`managed_spell_mode`, `managed_spell_limit`,\n"
    "          `managed_spell_timeout_seconds`, `managed_spell_reset_methods`) are stored\n"
    "          as given - the reset group as a tuple (or None) - and replayed unchanged;\n"
    "          Bind validates and normalizes them when the module is scanned.\n",
)
replace_once(
    "        \"resolvable\",\n"
    "        \"disposal_method_names\",\n"
    "        \"spell_metadata\",\n"
    "    )\n",
    "        \"resolvable\",\n"
    "        \"disposal_method_names\",\n"
    "        \"spell_metadata\",\n"
    "        \"managed_spell_mode\",\n"
    "        \"managed_spell_limit\",\n"
    "        \"managed_spell_timeout_seconds\",\n"
    "        \"managed_spell_reset_methods\",\n"
    "    )\n",
)
replace_once(
    "        # Spell.__init__.\n"
    "        \"spell_index\", \"spell_name\", \"spell_type\", \"spell_id\", \"existing_object\",\n"
    "        \"spellbook\", \"spellframe_kind\", \"implemented_protocols\",\n"
    "    })\n",
    "        # Spell.__init__.\n"
    "        \"spell_index\", \"spell_name\", \"spell_type\", \"spell_id\", \"existing_object\",\n"
    "        \"spellbook\", \"spellframe_kind\", \"implemented_protocols\",\n"
    "        # The managed options (Spellbook.bind, Bind, Spell.__init__; scan_bind names them too).\n"
    "        \"managed_spell_mode\", \"managed_spell_limit\", \"managed_spell_timeout_seconds\",\n"
    "        \"managed_spell_reset_methods\",\n"
    "    })\n",
)
replace_once(
    "    disposal_method_names: Optional[tuple[str, ...]]\n"
    "    spell_metadata: Mapping[str, Any]\n",
    "    disposal_method_names: Optional[tuple[str, ...]]\n"
    "    spell_metadata: Mapping[str, Any]\n"
    "    managed_spell_mode: Optional[Union[ManagedSpellMode, str]]\n"
    "    managed_spell_limit: Optional[int]\n"
    "    managed_spell_timeout_seconds: Optional[float]\n"
    "    managed_spell_reset_methods: Optional[tuple[str, ...]]\n",
)
replace_once(
    "            disposal_method_names: Optional[tuple[str, ...]] = None,\n"
    "            spell_metadata: Optional[Mapping[str, Any]] = None,\n"
    "    ) -> None:\n",
    "            disposal_method_names: Optional[tuple[str, ...]] = None,\n"
    "            spell_metadata: Optional[Mapping[str, Any]] = None,\n"
    "            managed_spell_mode: Optional[Union[ManagedSpellMode, str]] = None,\n"
    "            managed_spell_limit: Optional[int] = None,\n"
    "            managed_spell_timeout_seconds: Optional[float] = None,\n"
    "            managed_spell_reset_methods: Optional[tuple[str, ...]] = None,\n"
    "    ) -> None:\n",
)
replace_once(
    "            spell_metadata (Optional[Mapping[str, Any]]): Validated application\n"
    "                metadata, or None for none.\n",
    "            spell_metadata (Optional[Mapping[str, Any]]): Validated application\n"
    "                metadata, or None for none.\n"
    "            managed_spell_mode (Optional[Union[ManagedSpellMode, str]]): Managed pool\n"
    "                policy as declared, or None.\n"
    "            managed_spell_limit (Optional[int]): Managed limit as declared, or None.\n"
    "            managed_spell_timeout_seconds (Optional[float]): Queue wait as declared, or None.\n"
    "            managed_spell_reset_methods (Optional[tuple[str, ...]]): Normalized reset group,\n"
    "                or None.\n",
)
replace_once(
    "            MappingProxyType(dict(spell_metadata) if spell_metadata is not None else {}),\n"
    "        )\n",
    "            MappingProxyType(dict(spell_metadata) if spell_metadata is not None else {}),\n"
    "        )\n"
    "        object.__setattr__(self, \"managed_spell_mode\", managed_spell_mode)\n"
    "        object.__setattr__(self, \"managed_spell_limit\", managed_spell_limit)\n"
    "        object.__setattr__(self, \"managed_spell_timeout_seconds\", managed_spell_timeout_seconds)\n"
    "        object.__setattr__(self, \"managed_spell_reset_methods\", managed_spell_reset_methods)\n",
)
replace_once(
    "            f\"disposal_method_names={self.disposal_method_names!r}, \"\n"
    "            f\"spell_metadata_keys={sorted(self.spell_metadata)!r})\"\n",
    "            f\"disposal_method_names={self.disposal_method_names!r}, \"\n"
    "            f\"managed_spell_mode={self.managed_spell_mode!r}, \"\n"
    "            f\"managed_spell_limit={self.managed_spell_limit!r}, \"\n"
    "            f\"managed_spell_timeout_seconds={self.managed_spell_timeout_seconds!r}, \"\n"
    "            f\"managed_spell_reset_methods={self.managed_spell_reset_methods!r}, \"\n"
    "            f\"spell_metadata_keys={sorted(self.spell_metadata)!r})\"\n",
)
replace_once(
    "            - Leaves out the native policy arguments (existence, permissions,\n"
    "              spellframe, binding_name, resolvable, disposal_method_names);\n"
    "              `Scan.scan_module` passes those to `Spellbook.bind` explicitly.\n",
    "            - Leaves out the native policy arguments (existence, permissions,\n"
    "              spellframe, binding_name, resolvable, disposal_method_names and the\n"
    "              four managed options); `Scan.scan_module` passes those to\n"
    "              `Spellbook.bind` explicitly.\n",
)

# scan_bind ----------------------------------------------------------------------------------------------------
replace_once(
    "        resolvable: bool = True,\n"
    "        disposal_method_names: Optional[Sequence[str]] = None,\n"
    "        **spell_metadata: Any,\n"
    ") -> Callable[[Any], Any]:\n",
    "        resolvable: bool = True,\n"
    "        disposal_method_names: Optional[Sequence[str]] = None,\n"
    "        managed_spell_mode: Optional[Union[ManagedSpellMode, str]] = None,\n"
    "        managed_spell_limit: Optional[int] = None,\n"
    "        managed_spell_timeout_seconds: Optional[float] = None,\n"
    "        managed_spell_reset_methods: Optional[Sequence[str]] = None,\n"
    "        **spell_metadata: Any,\n"
    ") -> Callable[[Any], Any]:\n",
)
replace_once(
    "        - Accepts every option `Spellbook.bind` accepts for a target, with the\n"
    "          same defaults: `resolvable`, per-target `disposal_method_names` and\n"
    "          keyword application metadata.",
    "        - Accepts every option `Spellbook.bind` accepts for a target, with the\n"
    "          same defaults: `resolvable`, per-target `disposal_method_names`, the\n"
    "          four managed options and keyword application metadata.",
)
replace_once(
    "            both leave the Book's candidates in force.\n"
    "        **spell_metadata (Any):\n",
    "            both leave the Book's candidates in force.\n"
    "        managed_spell_mode (Optional[Union[ManagedSpellMode, str]]):\n"
    "            Pool policy of an `Existence.managed_spell_quantity` target (elastic by default).\n"
    "        managed_spell_limit (Optional[int]):\n"
    "            elastic: the most idle objects kept (default 256); limited_quantity and queue: the\n"
    "            most objects alive at once (required).\n"
    "        managed_spell_timeout_seconds (Optional[float]):\n"
    "            queue only, required there: how long a lease waits for a release.\n"
    "        managed_spell_reset_methods (Optional[Sequence[str]]):\n"
    "            Zero-argument methods run on every release, as a list or tuple of names (checked\n"
    "            here); the other managed rules are Bind's, at scan time.\n"
    "        **spell_metadata (Any):\n",
)
replace_once(
    "        TypeError: If any hook list is not a list/tuple of callables, if\n"
    "            `disposal_method_names` is not a list/tuple of strings, or if a\n"
    "            metadata key is reserved.\n",
    "        TypeError: If any hook list is not a list/tuple of callables, if\n"
    "            `disposal_method_names` or `managed_spell_reset_methods` is not a\n"
    "            list/tuple of strings, or if a metadata key is reserved.\n",
)
replace_once(
    "    disposal_method_names_tuple = _normalize_disposal_method_names(disposal_method_names)\n",
    "    disposal_method_names_tuple = _normalize_disposal_method_names(disposal_method_names)\n"
    "    managed_spell_reset_methods_tuple = _normalize_managed_reset_methods(managed_spell_reset_methods)\n",
)
replace_once(
    "            disposal_method_names=disposal_method_names_tuple,\n"
    "            spell_metadata=spell_metadata_snapshot,\n"
    "        )\n",
    "            disposal_method_names=disposal_method_names_tuple,\n"
    "            spell_metadata=spell_metadata_snapshot,\n"
    "            managed_spell_mode=managed_spell_mode,\n"
    "            managed_spell_limit=managed_spell_limit,\n"
    "            managed_spell_timeout_seconds=managed_spell_timeout_seconds,\n"
    "            managed_spell_reset_methods=managed_spell_reset_methods_tuple,\n"
    "        )\n",
)

# Scan.scan_module ---------------------------------------------------------------------------------------------
replace_once(
    "            - Every target reaches `Spellbook.bind` with its declared existence,\n"
    "              permissions, spellframe, binding_name, resolvable and\n"
    "              disposal_method_names, plus `ScanBindMetadata.to_bind_kwargs()`\n"
    "              (hook lists, profile and application metadata).\n",
    "            - Every target reaches `Spellbook.bind` with its declared existence,\n"
    "              permissions, spellframe, binding_name, resolvable,\n"
    "              disposal_method_names and the four managed options, plus\n"
    "              `ScanBindMetadata.to_bind_kwargs()` (hook lists, profile and\n"
    "              application metadata).\n",
)
replace_once(
    "                resolvable=metadata.resolvable,\n"
    "                disposal_method_names=metadata.disposal_method_names,\n"
    "                **bind_kwargs,\n"
    "            )\n",
    "                resolvable=metadata.resolvable,\n"
    "                disposal_method_names=metadata.disposal_method_names,\n"
    "                managed_spell_mode=metadata.managed_spell_mode,\n"
    "                managed_spell_limit=metadata.managed_spell_limit,\n"
    "                managed_spell_timeout_seconds=metadata.managed_spell_timeout_seconds,\n"
    "                managed_spell_reset_methods=metadata.managed_spell_reset_methods,\n"
    "                **bind_kwargs,\n"
    "            )\n",
)
path.write_text(text, encoding="utf-8", newline="\n")
print("scan.py edited")
