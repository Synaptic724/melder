"""S2: managed bind options in bind.py (normalizer, fingerprint part, forwarding). Run from the repository root."""
import pathlib

path = pathlib.Path("src/melder/aether/spellbook/bind/bind.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    """Replace exactly one occurrence of `old`."""
    global text
    count = text.count(old)
    assert count == 1, (count, old[:80])
    text = text.replace(old, new, 1)


replace_once("import hashlib\n", "import hashlib\nimport math\n")
replace_once(
    "from melder.aether.spellbook.existence.existence import Existence\n",
    "from melder.aether.spellbook.existence.existence import Existence\n"
    "from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode\n",
)
replace_once(
    '    _HOOK_NAMES: ClassVar[tuple[str, ...]] = ("bind:pre", "bind:activation", "bind:post")\n',
    '    _HOOK_NAMES: ClassVar[tuple[str, ...]] = ("bind:pre", "bind:activation", "bind:post")\n'
    "    # Managed options (Existence.managed_spell_quantity): the idle cap an elastic binding gets when it names\n"
    "    # none, and the four option names in signature order (a refusal names the ones the binding supplied).\n"
    "    _MANAGED_ELASTIC_DEFAULT_LIMIT: ClassVar[int] = 256\n"
    "    _MANAGED_OPTION_NAMES: ClassVar[tuple[str, ...]] = (\n"
    '        "managed_spell_mode",\n'
    '        "managed_spell_limit",\n'
    '        "managed_spell_timeout_seconds",\n'
    '        "managed_spell_reset_methods",\n'
    "    )\n",
)

MANAGED_PARAMS = (
    "            managed_spell_mode: Optional[Union[ManagedSpellMode, str]] = None,\n"
    "            managed_spell_limit: Optional[int] = None,\n"
    "            managed_spell_timeout_seconds: Optional[float] = None,\n"
    "            managed_spell_reset_methods: Optional[Sequence[str]] = None,\n"
)

# --- Bind.bind: signature, docstring, forwarding -------------------------------------------------------------
replace_once(
    "            resolvable: bool = True,\n"
    "            _lifecycle_hooks: Optional[BindLifecycleHooks] = None,\n"
    "            **kwargs: Any,\n"
    "    ) -> Union[Spell, Any]:\n",
    "            resolvable: bool = True,\n"
    + MANAGED_PARAMS +
    "            _lifecycle_hooks: Optional[BindLifecycleHooks] = None,\n"
    "            **kwargs: Any,\n"
    "    ) -> Union[Spell, Any]:\n",
)
replace_once(
    "            resolvable (bool): Native resolution capability for this Spell version.\n"
    "                False permits descriptive Protocol targets; it does not relax other binding rules.\n"
    "            _lifecycle_hooks: Internal Book-captured callback set, retained through\n",
    "            resolvable (bool): Native resolution capability for this Spell version.\n"
    "                False permits descriptive Protocol targets; it does not relax other binding rules.\n"
    "            managed_spell_mode (Optional[Union[ManagedSpellMode, str]]): Pool policy of an\n"
    "                `Existence.managed_spell_quantity` binding - a member or its name; None means elastic.\n"
    "            managed_spell_limit (Optional[int]): Elastic: the most idle objects kept (default 256).\n"
    "                limited_quantity and queue: the most objects alive at once (required).\n"
    "            managed_spell_timeout_seconds (Optional[float]): How long a queue lease waits for a\n"
    "                release (queue only, required there).\n"
    "            managed_spell_reset_methods (Optional[Sequence[str]]): Names of zero-argument methods of\n"
    "                the class run, in order, on every release. All four options must stay None on any\n"
    "                other existence; `_normalize_managed_options` states every rule.\n"
    "            _lifecycle_hooks: Internal Book-captured callback set, retained through\n",
)
replace_once(
    "                value where that Protocol requires a callable, or resolvable is not a bool,\n"
    "                or `spellframe` is neither None, a string nor a Protocol class.\n"
    "        \"\"\"\n"
    "        self.check_cleaned()\n"
    "        if spell is None:\n",
    "                value where that Protocol requires a callable, or resolvable is not a bool,\n"
    "                or `spellframe` is neither None, a string nor a Protocol class, or a managed\n"
    "                option has the wrong type or targets a non-class.\n"
    "            ValueError: If a managed option is malformed or set on another existence.\n"
    "        \"\"\"\n"
    "        self.check_cleaned()\n"
    "        if spell is None:\n",
)
FORWARD_20 = (
    "                    managed_spell_mode=managed_spell_mode,\n"
    "                    managed_spell_limit=managed_spell_limit,\n"
    "                    managed_spell_timeout_seconds=managed_spell_timeout_seconds,\n"
    "                    managed_spell_reset_methods=managed_spell_reset_methods,\n"
)
FORWARD_16 = FORWARD_20.replace("                    ", "                ")
replace_once(
    "\n                    resolvable=resolvable,\n"
    "                    _lifecycle_hooks=_lifecycle_hooks,\n",
    "\n                    resolvable=resolvable,\n"
    + FORWARD_20 +
    "                    _lifecycle_hooks=_lifecycle_hooks,\n",
)
replace_once(
    "\n                resolvable=resolvable,\n"
    "                _lifecycle_hooks=_lifecycle_hooks,\n",
    "\n                resolvable=resolvable,\n"
    + FORWARD_16 +
    "                _lifecycle_hooks=_lifecycle_hooks,\n",
)

# --- Bind._bind_logic -----------------------------------------------------------------------------------------
replace_once(
    "            resolvable: bool = True,\n"
    "            _lifecycle_hooks: Optional[BindLifecycleHooks] = None,\n"
    "            **kwargs: Any,\n"
    "    ) -> Spell:\n",
    "            resolvable: bool = True,\n"
    + MANAGED_PARAMS +
    "            _lifecycle_hooks: Optional[BindLifecycleHooks] = None,\n"
    "            **kwargs: Any,\n"
    "    ) -> Spell:\n",
)
replace_once(
    "        * Resolves disposal names once in group priority order, hashes the resolved\n"
    "          list, and passes that same list to Spell without another conversion.\n",
    "        * Resolves disposal names once in group priority order, hashes the resolved\n"
    "          list, and passes that same list to Spell without another conversion.\n"
    "        * Validates and normalizes the four managed options once\n"
    "          (`_normalize_managed_options`), after the profile and before the fingerprint;\n"
    "          a managed binding hashes them as one extra part and the Spell keeps them.\n",
)
replace_once(
    "            resolvable (bool): Immutable resolution capability, validated before target reflection.\n"
    "            _lifecycle_hooks: Optional callback set captured by Book for this operation.\n",
    "            resolvable (bool): Immutable resolution capability, validated before target reflection.\n"
    "            managed_spell_mode (Optional[Union[ManagedSpellMode, str]]): Managed pool policy, or None.\n"
    "            managed_spell_limit (Optional[int]): Managed idle cap (elastic) or alive limit, or None.\n"
    "            managed_spell_timeout_seconds (Optional[float]): Queue wait in seconds, or None.\n"
    "            managed_spell_reset_methods (Optional[Sequence[str]]): Reset method names, or None.\n"
    "            _lifecycle_hooks: Optional callback set captured by Book for this operation.\n",
)
replace_once(
    "                - If a class or existing object under a Protocol spellframe\n"
    "                  fails its directly declared public-member check.\n"
    "            ValueError:\n"
    "                - If the binding is otherwise invalid (existence errors, lambda\n"
    "                  without name, etc.).\n",
    "                - If a class or existing object under a Protocol spellframe\n"
    "                  fails its directly declared public-member check.\n"
    "                - If a managed binding targets a non-class, or a managed option\n"
    "                  has the wrong type.\n"
    "            ValueError:\n"
    "                - If the binding is otherwise invalid (existence errors, lambda\n"
    "                  without name, etc.).\n"
    "                - If a managed option is malformed, or set on another existence.\n",
)
replace_once(
    "            fingerprint: str = Bind.sha256_profile(\n"
    "                binding_profile,\n",
    "            # Managed options (Existence.managed_spell_quantity): validated and normalized here, once,\n"
    "            # because they are hashed into a managed spell's id and kept by its Spell; any other\n"
    "            # existence must leave all four unset. Refusals happen before a Spell or index exists.\n"
    "            (\n"
    "                normalized_managed_mode,\n"
    "                normalized_managed_limit,\n"
    "                normalized_managed_timeout,\n"
    "                normalized_managed_reset_methods,\n"
    "            ) = Bind._normalize_managed_options(\n"
    "                spell,\n"
    "                binding_profile,\n"
    "                str(spell_name),\n"
    "                existence,\n"
    "                managed_spell_mode,\n"
    "                managed_spell_limit,\n"
    "                managed_spell_timeout_seconds,\n"
    "                managed_spell_reset_methods,\n"
    "            )\n"
    "            fingerprint: str = Bind.sha256_profile(\n"
    "                binding_profile,\n",
)
replace_once(
    "                disposal_method_names=resolved_disposal_method_names,\n"
    "                resolvable=resolvable,\n"
    "            )\n"
    "            spell_index = SpellIndex(initial_id=fingerprint)\n",
    "                disposal_method_names=resolved_disposal_method_names,\n"
    "                resolvable=resolvable,\n"
    "                managed_spell_mode=normalized_managed_mode,\n"
    "                managed_spell_limit=normalized_managed_limit,\n"
    "                managed_spell_timeout_seconds=normalized_managed_timeout,\n"
    "                managed_spell_reset_methods=normalized_managed_reset_methods,\n"
    "            )\n"
    "            spell_index = SpellIndex(initial_id=fingerprint)\n",
)
replace_once(
    "                implemented_protocols=implemented_protocols,\n"
    "                # Owner ruling 2026-07-19",
    "                implemented_protocols=implemented_protocols,\n"
    "                managed_spell_mode=normalized_managed_mode,\n"
    "                managed_spell_limit=normalized_managed_limit,\n"
    "                managed_spell_timeout_seconds=normalized_managed_timeout,\n"
    "                managed_spell_reset_methods=normalized_managed_reset_methods,\n"
    "                # Owner ruling 2026-07-19",
)

# --- Bind.spell_id_inspector ----------------------------------------------------------------------------------
replace_once(
    "            disposal_method_names: Sequence[str] = (),\n"
    "            resolvable: bool = True,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Compute the canonical spell fingerprint without registering the spell.\n",
    "            disposal_method_names: Sequence[str] = (),\n"
    "            resolvable: bool = True,\n"
    + MANAGED_PARAMS +
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Compute the canonical spell fingerprint without registering the spell.\n",
)
replace_once(
    "            resolvable (bool): Per-version capability; omission preserves the legacy fingerprint.\n"
    "        Contract:\n"
    "            - Builds the same `SpellGeneralProfile` / `SpellBindingProfile`\n",
    "            resolvable (bool): Per-version capability; omission preserves the legacy fingerprint.\n"
    "            managed_spell_mode (Optional[Union[ManagedSpellMode, str]]): Managed pool policy, or None.\n"
    "            managed_spell_limit (Optional[int]): Managed idle cap (elastic) or alive limit, or None.\n"
    "            managed_spell_timeout_seconds (Optional[float]): Queue wait in seconds, or None.\n"
    "            managed_spell_reset_methods (Optional[Sequence[str]]): Reset method names, or None.\n"
    "        Contract:\n"
    "            - Builds the same `SpellGeneralProfile` / `SpellBindingProfile`\n",
)
replace_once(
    "            - Does not register anything into a spellbook or mutate runtime\n"
    "              binding state.\n"
    "\n"
    "        Returns:\n"
    "            str: A unique identifier string (SHA256 hash) for the spell.\n"
    "\n"
    "        Raises:\n"
    "            TypeError: If resolvable is not a bool; checked before target reflection.\n"
    "        \"\"\"\n"
    "        Bind._validate_resolvable(resolvable)\n"
    "        profile = SpellGeneralProfile.create_from_target(spell)\n"
    "        return Bind.sha256_profile(\n"
    "            profile.binding_profile,\n"
    "            spellframe=spellframe,\n"
    "            spell_name=spell_name,\n"
    "            binding_name=binding_name,\n"
    "            existence=existence,\n"
    "            disposal_method_names=tuple(disposal_method_names),\n"
    "            resolvable=resolvable,\n"
    "        )\n",
    "            - Does not register anything into a spellbook or mutate runtime\n"
    "              binding state.\n"
    "            - Normalizes and checks the managed options with bind's own\n"
    "              `_normalize_managed_options`, so a managed fingerprint matches bind's.\n"
    "\n"
    "        Returns:\n"
    "            str: A unique identifier string (SHA256 hash) for the spell.\n"
    "\n"
    "        Raises:\n"
    "            TypeError: If resolvable is not a bool (checked before target reflection), or a\n"
    "                managed option has the wrong type or targets a non-class.\n"
    "            ValueError: If a managed option is malformed or set on another existence.\n"
    "        \"\"\"\n"
    "        Bind._validate_resolvable(resolvable)\n"
    "        profile = SpellGeneralProfile.create_from_target(spell)\n"
    "        # Error messages name the target; the inspector hashes `spell_name` only when given, as bind would.\n"
    "        # The target is caller-supplied, so `getattr` with a default is the external-object exception.\n"
    "        display_name = spell_name if spell_name is not None else getattr(spell, \"__name__\", type(spell).__name__)\n"
    "        (\n"
    "            normalized_managed_mode,\n"
    "            normalized_managed_limit,\n"
    "            normalized_managed_timeout,\n"
    "            normalized_managed_reset_methods,\n"
    "        ) = Bind._normalize_managed_options(\n"
    "            spell,\n"
    "            profile.binding_profile,\n"
    "            str(display_name),\n"
    "            existence,\n"
    "            managed_spell_mode,\n"
    "            managed_spell_limit,\n"
    "            managed_spell_timeout_seconds,\n"
    "            managed_spell_reset_methods,\n"
    "        )\n"
    "        return Bind.sha256_profile(\n"
    "            profile.binding_profile,\n"
    "            spellframe=spellframe,\n"
    "            spell_name=spell_name,\n"
    "            binding_name=binding_name,\n"
    "            existence=existence,\n"
    "            disposal_method_names=tuple(disposal_method_names),\n"
    "            resolvable=resolvable,\n"
    "            managed_spell_mode=normalized_managed_mode,\n"
    "            managed_spell_limit=normalized_managed_limit,\n"
    "            managed_spell_timeout_seconds=normalized_managed_timeout,\n"
    "            managed_spell_reset_methods=normalized_managed_reset_methods,\n"
    "        )\n",
)

# --- Bind.sha256_profile --------------------------------------------------------------------------------------
replace_once(
    "            disposal_method_names: Sequence[str] = (),\n"
    "            resolvable: bool = True,\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Computes the SHA256 hash of a spell's binding profile metadata.\n",
    "            disposal_method_names: Sequence[str] = (),\n"
    "            resolvable: bool = True,\n"
    "            managed_spell_mode: Optional[ManagedSpellMode] = None,\n"
    "            managed_spell_limit: Optional[int] = None,\n"
    "            managed_spell_timeout_seconds: Optional[float] = None,\n"
    "            managed_spell_reset_methods: Sequence[str] = (),\n"
    "    ) -> str:\n"
    "        \"\"\"\n"
    "        Computes the SHA256 hash of a spell's binding profile metadata.\n",
)
replace_once(
    "            - Equal bind signatures produce equal hashes; materially different\n"
    "              signatures should produce different hashes.\n",
    "            - A managed binding (a `managed_spell_mode` is given) appends one last part,\n"
    "              `managed:<mode>:<limit>:<timeout>:<reset names>` (`_managed_fingerprint_part`).\n"
    "              Callers pass normalized values (`_normalize_managed_options`). Without a mode\n"
    "              nothing is appended, so every other binding hashes exactly as before (S2,\n"
    "              2026-10-15).\n"
    "            - Equal bind signatures produce equal hashes; materially different\n"
    "              signatures should produce different hashes.\n",
)
replace_once(
    "        parts.extend(tuple(disposal_method_names))\n"
    "\n"
    "        key = \"::\".join(parts)\n",
    "        parts.extend(tuple(disposal_method_names))\n"
    "\n"
    "        # Managed bindings only: one part carrying the normalized options closes the key.\n"
    "        if managed_spell_mode is not None:\n"
    "            parts.append(\n"
    "                Bind._managed_fingerprint_part(\n"
    "                    managed_spell_mode,\n"
    "                    managed_spell_limit,\n"
    "                    managed_spell_timeout_seconds,\n"
    "                    managed_spell_reset_methods,\n"
    "                )\n"
    "            )\n"
    "\n"
    "        key = \"::\".join(parts)\n",
)

path.write_text(text, encoding="utf-8", newline="\n")
print("bind.py edited")
