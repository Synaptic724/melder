"""S2b-1: nested shared misses (design v2 L1/L3, B2) in the key-set plan lowering - anchored edits.

Usage: python apply_s2b1_edits.py <tree_root> [--check]

Edits shared_assets/site_plan_lowering.py only: SitePlanEmission places kept steps (top level or inside one shared
site's miss), emits an inline hit read plus an out-of-line `_miss{i}` per shared site, and threads a `lines` target
through `_emit_construct`. Each anchor must match exactly once (either line ending) or nothing is written.
Engine: apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from apply_s3b1_edits import _apply_one

LOWERING = "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"

LOWERING_DOC_OLD = '''        The shared lowering of design v2 for the override lane: given the
        lane's no-overrides steps and one resolved key set, emit straight-line
        Python that builds only the demanded steps and reads supplied values by
        literal key (`ov["a"]`, `args[0]`).
'''
LOWERING_DOC_NEW = '''        The shared lowering of design v2 for the override lane: given the
        lane's no-overrides steps and one resolved key set, emit Python that
        builds only the demanded steps and reads supplied values by literal key
        (`ov["a"]`, `args[0]`). A shared site is an inline hit read plus an
        out-of-line miss function, and the sites only it needs are built inside
        that miss, so a stored shared site's children are never built (S2b-1,
        design L1/L3, B2).
'''

EMISSION_DOC_OLD = '''        - Dict mode (`instance_results`) is emitted only when a generic step
          needs dependency values by instance key.
'''
EMISSION_DOC_NEW = '''        - Dict mode (`instance_results`) is emitted only when a generic step
          needs dependency values by instance key; misses then receive the dict
          and record their sites in it.
        - Placement (2026-09-26): every kept step lives at top level or inside
          exactly one shared site's `_miss{i}`. The root is top level; a many
          site lives where its one consumer is built (inside the consumer's miss
          when the consumer is shared); a shared site lives at the lowest context
          common to all its consumers; a shared site with a winning override is
          pinned to top level so its P2 refusal and build are exactly today's.
          Within a context steps keep the family's providers-first order.
        - A miss function takes `(meld, ov, c{i}, [instance_results], [args],
          v...)`: the outer values its sites read, in step order. It builds the
          sites placed inside it first, then takes the site's build guard for
          recheck, construction and publication only, and returns the site's
          value. So a plan never holds a build lock while another site's
          constructor runs (today's locking; design risk R2 retired
          2026-09-26); a cold race may build and drop the loser's children, as
          the straight-line lowering does.
'''

SLOTS_OLD = '''        "_uses_many_store",
    ]
'''
SLOTS_NEW = '''        "_direct",
        "_dict_mode",
        "_shared",
        "_home",
        "_children",
        "_miss_value_params",
        "_root_index",
        "_miss_lines",
    ]
'''

INIT_OLD = '''        self._uses_many_store: bool = False
'''
INIT_NEW = '''        # Placement state; filled by `render` (`_place`).
        self._direct: List[bool] = []
        self._dict_mode: bool = False
        self._shared: List[bool] = [step.existence is not Existence.many for step in steps]
        self._home: Dict[int, Optional[int]] = {}
        self._children: Dict[Optional[int], List[int]] = {}
        self._miss_value_params: Dict[int, Tuple[int, ...]] = {}
        self._root_index: int = -1
        self._miss_lines: List[str] = []
'''

CLEANUP_OLD = '''        del self._uses_many_store
'''
CLEANUP_NEW = '''        self._miss_lines.clear()
        del self._direct
        del self._dict_mode
        del self._shared
        del self._home
        del self._children
        del self._miss_value_params
        del self._root_index
        del self._miss_lines
'''

TAIL_START = "    def render(self) -> Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:\n"
TAIL_STOP = "    @staticmethod\n    def _route(existence: Existence, spell_name: str) -> str:\n"

TAIL_NEW = '''    def render(self) -> Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:
        """
        Emit the plan and return `(source, namespace, masked steps)`.

        Contract:
            The source defines one `_miss{i}` per kept shared site, then the plan
            `def _site_plan_executor(meld, ov)`; all of it is exec'd into the
            returned namespace. Placement is computed first (see `_place`).

        Returns:
            Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]: See `SitePlanLowering.emit`.
        """
        self._direct = [self._is_direct(step) for step in self._steps]
        self._dict_mode = not all(self._direct)
        self._place()
        body = self._lines
        if self._arity > 0:
            body.append('    args = ov["__args__"]')
        sites = self._site_graph.sites
        for number, (site_index, param_name, winner, other) in enumerate(self._conflicts):
            target_name = self._bind(f"cf{number}", f"{sites[site_index].spell_id}.{param_name}")
            body.append(
                f"    _conflict_guard(ov[{winner!r}], ov[{other!r}], {target_name}, "
                "root_spell_id, root_spell_name)"
            )
        if self._dict_mode:
            body.append("    instance_results = {}")
        uses_many_store = self._emit_context(None, "    ", body)
        body.append(f"    return {self._local_by_key[self._root_instance_key]}")
        # Constants are read as globals of the plan's namespace; see the class contract.
        source_lines = list(self._miss_lines)
        source_lines.append(f"def {SitePlanLowering.PLAN_FUNCTION_NAME}(meld, ov):")
        if uses_many_store:
            source_lines.extend(self._many_store_prologue("    "))
        source_lines.extend(body)
        return "\\n".join(source_lines) + "\\n", self._namespace, tuple(self._masked)

    def _bind(self, name: str, value: Any) -> str:
        """
        Bind one plan constant into the namespace, which is the plan's globals.
        """
        self._namespace[name] = value
        return name

    def _place(self) -> None:
        """
        Place every kept step at top level (None) or inside one shared site's miss.

        Contract:
            - Steps are visited consumers before providers (reverse step order).
              The root and every shared site with a winning override are top
              level. Any other step lives at the lowest context common to its
              consumers, where a shared consumer's context is its own miss and a
              many consumer's context is where that consumer lives.
            - A consumer reads a provider through each non-supplied parameter's
              dependency keys, exactly the operands `_operand` emits.
            - Then each shared site's outer values are computed bottom-up: the
              direct operands of the steps built inside its miss (and of its own
              construction) that live outside it, plus what its nested misses need.

        Raises:
            RuntimeError: When a dependency key has no kept step, or a provider
                does not precede its consumer (the family order is providers-first).

        Returns:
            None.
        """
        steps = self._steps
        index_by_key = {step.instance_key: index for index, step in enumerate(steps)}
        providers_by_consumer: List[List[int]] = []
        consumers: List[List[int]] = [[] for _ in steps]
        for consumer, step in enumerate(steps):
            providers = self._direct_providers(step, index_by_key)
            for provider in providers:
                if provider >= consumer:
                    raise RuntimeError(
                        f"Key-set plan step {provider} does not precede its consumer {consumer}."
                    )
                consumers[provider].append(consumer)
            providers_by_consumer.append(providers)
        root_index = index_by_key[self._root_instance_key]
        home: Dict[int, Optional[int]] = {}
        for index in range(len(steps) - 1, -1, -1):
            if index == root_index or (self._shared[index] and self._supplied_names(steps[index])):
                home[index] = None
                continue
            contexts = [
                consumer if self._shared[consumer] else home[consumer] for consumer in consumers[index]
            ]
            home[index] = self._common_context(contexts, home)
        children: Dict[Optional[int], List[int]] = {}
        for index in range(len(steps)):
            children.setdefault(home[index], []).append(index)
        value_params: Dict[int, Tuple[int, ...]] = {}
        for index in range(len(steps)):
            if not self._shared[index]:
                continue
            inside = children.get(index, [])
            needed = set()
            for member in inside:
                # A nested shared site builds inside its own miss: only what that
                # miss needs from outside passes through here.
                if self._shared[member]:
                    needed.update(value_params[member])
                elif self._direct[member]:
                    needed.update(providers_by_consumer[member])
            if self._direct[index]:
                needed.update(providers_by_consumer[index])
            needed.difference_update(inside)
            needed.discard(index)
            value_params[index] = tuple(sorted(needed))
        self._home = home
        self._children = children
        self._miss_value_params = value_params
        self._root_index = root_index

    def _direct_providers(self, step: SitePlanStep, index_by_key: Dict[SiteInstanceKey, int]) -> List[int]:
        """
        Return the kept step indexes one step reads through its non-supplied parameters.

        Raises:
            RuntimeError: When a dependency key has no kept step.
        """
        supplied = self._supplied_names(step)
        providers: List[int] = []
        for param_name, dependency_keys in step.dependency_resolution_order:
            if param_name in supplied:
                continue
            for key in dependency_keys:
                provider = index_by_key.get(key)
                if provider is None:
                    raise RuntimeError(
                        f"Key-set plan dependency {key!r} of {step.instance_key!r} has no kept step."
                    )
                providers.append(provider)
        return providers

    @staticmethod
    def _common_context(
            contexts: List[Optional[int]],
            home: Dict[int, Optional[int]],
    ) -> Optional[int]:
        """
        Return the lowest context common to `contexts` (None is top level).

        Contract:
            A miss context's parent is its site's home. Top level wins as soon as
            one context is top level; no contexts at all is top level too.
        """
        if not contexts or None in contexts:
            return None
        chains: List[List[int]] = []
        for context in contexts:
            chain: List[int] = []
            current: Optional[int] = context
            while current is not None:
                chain.append(current)
                current = home[current]
            chains.append(chain)
        others = [set(chain) for chain in chains[1:]]
        for candidate in chains[0]:
            if all(candidate in other for other in others):
                return candidate
        return None

    def _miss_arguments(self, index: int) -> List[str]:
        """
        Return the parameter/argument names after `(meld, ov, c{i})` for one miss.

        Contract:
            `instance_results` in dict mode, `args` for the root when `__args__` is
            supplied, then the outer values in step order.
        """
        names: List[str] = []
        if self._dict_mode:
            names.append("instance_results")
        if self._arity > 0 and index == self._root_index:
            names.append("args")
        names.extend(f"v{value}" for value in self._miss_value_params[index])
        return names

    def _emit_context(self, context: Optional[int], indent: str, lines: List[str]) -> bool:
        """
        Emit the steps placed in one context (top level or one miss body) into `lines`.

        Returns:
            bool: True when a disposal-bearing many step here reads `many_store`.
        """
        uses_many_store = False
        for index in self._children.get(context, []):
            step = self._steps[index]
            if self._shared[index]:
                self._emit_shared_hit(index, step, indent, lines)
            elif self._emit_many(index, step, indent, lines):
                uses_many_store = True
            if self._dict_mode:
                key_name = self._bind(f"key{index}", step.instance_key)
                lines.append(f"{indent}instance_results[{key_name}] = v{index}")
        return uses_many_store

    def _emit_many(self, index: int, step: SitePlanStep, indent: str, lines: List[str]) -> bool:
        """
        Emit one many step: construction, then disposal registration in the innermost scope.

        Returns:
            bool: True when the step registers through `many_store`.
        """
        self._emit_construct(index, step, self._direct[index], self._supplied_names(step), indent, lines)
        if not step.spell.has_disposal_methods:
            return False
        sid_name = self._bind(f"sid{index}", step.spell.spell_id)
        disposal_name = self._bind(f"dm{index}", step.spell.disposal_method_names)
        lines.append(
            f"{indent}many_store.add_many_creations({sid_name}, v{index}, "
            f"has_disposal_methods=True, disposal_methods={disposal_name})"
        )
        return True

    def _emit_shared_hit(self, index: int, step: SitePlanStep, indent: str, lines: List[str]) -> None:
        """
        Emit one shared site where it lives: store read, P2 when pinned, miss call; then its miss.
        """
        spell_name = f"spells[{index}]"
        store = f"c{index}"
        sid_name = self._bind(f"sid{index}", step.spell.spell_id)
        lines.append(f"{indent}{store} = {self._route(step.existence, spell_name)}")
        lines.append(f"{indent}v{index} = {store}._creations.get({sid_name})")
        if self._supplied_names(step):
            lines.append(f"{indent}if v{index} is not None:")
            lines.append(f"{indent}    _raise_existing_override({spell_name}, root_spell_id)")
        arguments = ", ".join(["meld", "ov", store] + self._miss_arguments(index))
        lines.append(f"{indent}if v{index} is None:")
        lines.append(f"{indent}    v{index} = _miss{index}({arguments})")
        self._emit_miss(index, step, sid_name)

    def _emit_miss(self, index: int, step: SitePlanStep, sid_name: str) -> None:
        """
        Emit `_miss{index}`: children, then guard, recheck (P2 when pinned), construction, publication.

        Contract:
            The sites placed inside the miss are built before the guard is taken,
            so the guard covers only this site's recheck, construction and
            publication, as every build lock does in the straight-line lowering.
            A user constructor never runs under another site's build lock.
        """
        spell_name = f"spells[{index}]"
        store = f"c{index}"
        supplied = self._supplied_names(step)
        children: List[str] = []
        uses_many_store = self._emit_context(index, "    ", children)
        inner: List[str] = []
        self._emit_construct(index, step, self._direct[index], supplied, "            ", inner)
        if step.spell.has_disposal_methods:
            disposal_name = self._bind(f"dm{index}", step.spell.disposal_method_names)
            inner.append(
                f"            {store}.add_creation({sid_name}, v{index}, "
                f"has_disposal_methods=True, disposal_methods={disposal_name})"
            )
        else:
            inner.append(f"            {store}._creations[{sid_name}] = v{index}")
        parameters = ", ".join(["meld", "ov", store] + self._miss_arguments(index))
        lines = self._miss_lines
        lines.append(f"def _miss{index}({parameters}):")
        if uses_many_store:
            lines.extend(self._many_store_prologue("    "))
        lines.extend(children)
        lines.append(f"    with {self._guard(step, store, sid_name, spell_name)}:")
        lines.append(f"        v{index} = {store}._creations.get({sid_name})")
        if supplied:
            lines.append(f"        if v{index} is not None:")
            lines.append(f"            _raise_existing_override({spell_name}, root_spell_id)")
        lines.append(f"        if v{index} is None:")
        lines.extend(inner)
        lines.append(f"        return v{index}")

    @staticmethod
    def _many_store_prologue(indent: str) -> List[str]:
        """
        Return the innermost-scope store selection for disposal-bearing many steps.
        """
        return [
            f"{indent}many_store = meld._spellspace_creations",
            f"{indent}if many_store is None:",
            f"{indent}    many_store = meld._conduit_creations",
        ]

'''

CONSTRUCT_OLD = '''            supplied: FrozenSet[str],
            indent: str,
    ) -> None:
        """
        Emit the construction of kept step `index` into `v{index}`.
'''
CONSTRUCT_NEW = '''            supplied: FrozenSet[str],
            indent: str,
            lines: List[str],
    ) -> None:
        """
        Emit the construction of kept step `index` into `v{index}`, appending to `lines`.
'''
CONSTRUCT_LINES_OLD = '''        lines = self._lines
        local = f"v{index}"
        if not direct:
'''
CONSTRUCT_LINES_NEW = '''        local = f"v{index}"
        if not direct:
'''

EDITS = [
    ("replace", LOWERING_DOC_OLD, LOWERING_DOC_NEW),
    ("replace", EMISSION_DOC_OLD, EMISSION_DOC_NEW),
    ("replace", SLOTS_OLD, SLOTS_NEW),
    ("replace", INIT_OLD, INIT_NEW),
    ("replace", CLEANUP_OLD, CLEANUP_NEW),
    ("cut", TAIL_START, TAIL_STOP),
    ("replace", TAIL_STOP, TAIL_NEW + TAIL_STOP),
    ("replace", CONSTRUCT_OLD, CONSTRUCT_NEW),
    ("replace", CONSTRUCT_LINES_OLD, CONSTRUCT_LINES_NEW),
]


def main() -> None:
    """Check every edit, then write (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    path = root / LOWERING
    data = path.read_bytes().decode("utf-8")
    for edit in EDITS:
        data = _apply_one(data, edit, LOWERING)
    compile(data, LOWERING, "exec")
    for stale in ("_uses_many_store", "self._lines.append", "def _emit_step(", "def _emit_shared_step("):
        if stale in data:
            raise SystemExit(f"stale reference left: {stale}")
    if not check:
        path.write_bytes(data.encode("utf-8"))
    print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
