"""Apply the door-held root-guard edit to site_plan_lowering.py in a tree (argv[1] = tree root)."""
import pathlib, sys
root = pathlib.Path(sys.argv[1])
p = root / "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py"
t = p.read_bytes().decode("utf-8")

def rep(old: str, new: str) -> None:
    global t
    assert t.count(old) == 1, (t.count(old), old[:100])
    t = t.replace(old, new)

# 1. SitePlanLowering class docstring: Threading.
rep("""    Threading:
        Compile-time only; emitted plans take the same locks as the normal lane.

    Registration:
        MELDER KERNEL - internal; never bound as a spell.

    Subsystem Context:
        Used by `SitePlanOverrideRuntime` (shared_assets).
""", """    Threading:
        Compile-time only; emitted plans take the same locks as the normal lane,
        with one exception (2026-09-26, 0.2.73): the normal plan emitted for a
        `door_route_key` of "unique_per_conduit" or "spellspace" whose root has
        that route's existence builds its root without taking the root's slot
        guard, because the route door that calls it already holds that same
        guard across the call. See `SitePlanEmission`.

    Registration:
        MELDER KERNEL - internal; never bound as a spell.

    Subsystem Context:
        Used by `SitePlanOverrideRuntime` (shared_assets).
""")

# 2. emit signature, docstring and call.
rep("""            arity: int,
            normal_mode: bool = False,
    ) -> Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:
        \"\"\"
        Emit one key-set plan: `def _site_plan_executor(meld, ov) -> instance`.
""", """            arity: int,
            normal_mode: bool = False,
            door_route_key: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any], Tuple[SitePlanStep, ...]]:
        \"\"\"
        Emit one key-set plan: `def _site_plan_executor(meld, ov) -> instance`.
""")
rep("""            normal_mode: Emit the `(meld)` normal-lane form; requires a
                resolution with no winners and no conflicts, and arity 0.

        Raises:
            RuntimeError: When the root step is missing from `steps`, or
                `normal_mode` is asked for a key set that supplies anything.
""", """            normal_mode: Emit the `(meld)` normal-lane form; requires a
                resolution with no winners and no conflicts, and arity 0.
            door_route_key: Normal mode only. The route key of the
                CreationContext doors that call this plan (they hold that
                route's build lock across the call), or None when a caller may
                not hold it. For "unique_per_conduit" and "spellspace" with a
                root of the matching existence, the root site takes no guard of
                its own (see `SitePlanEmission`); anything else keeps it.

        Raises:
            RuntimeError: When the root step is missing from `steps`,
                `normal_mode` is asked for a key set that supplies anything, or
                `door_route_key` is given outside normal mode.
""")
rep("""        if normal_mode and (resolution.winners or resolution.conflicts or arity):
            raise RuntimeError("A normal-mode plan is only emitted for a key set that supplies nothing.")
""", """        if normal_mode and (resolution.winners or resolution.conflicts or arity):
            raise RuntimeError("A normal-mode plan is only emitted for a key set that supplies nothing.")
        if door_route_key is not None and not normal_mode:
            raise RuntimeError("A door route key applies only to the normal-mode plan.")
""")
rep("""            arity=arity,
            normal_mode=normal_mode,
        )
        try:
            return emission.render()
""", """            arity=arity,
            normal_mode=normal_mode,
            door_route_key=door_route_key,
        )
        try:
            return emission.render()
""")

# 3. SitePlanEmission class docstring: the miss bullet.
rep("""        - A miss function takes `(meld, ov, c{i}, [instance_results], [args],
          v...)`: the outer values its sites read, in step order. It builds the
          sites placed inside it first, then takes the site's build guard for
          recheck, construction and publication only, and returns the site's
          value. So a plan never holds a build lock while another site's
          constructor runs (today's locking; design risk R2 retired
          2026-09-26); a cold race may build and drop the loser's children, as
          the straight-line lowering does.
""", """        - A miss function takes `(meld, ov, c{i}, [instance_results], [args],
          v...)`: the outer values its sites read, in step order. It builds the
          sites placed inside it first, then takes the site's build guard for
          recheck, construction and publication only, and returns the site's
          value. So a plan never holds a build lock while another site's
          constructor runs (today's locking; design risk R2 retired
          2026-09-26); a cold race may build and drop the loser's children, as
          the straight-line lowering does.
        - Door-held root (2026-09-26, 0.2.73): in normal mode with a
          `door_route_key` from `DOOR_HELD_ROOT_EXISTENCE` and a root of that
          existence, the root's miss takes no guard. The route door that calls
          the plan holds the root's slot guard from its recheck until the plan
          returns; the plan's root store read (`meld._conduit_creations` or
          `meld._spellspace_creations`, each assigned once per Meld) yields the
          same store and so the same guard, and a second take would only
          re-enter it. The root miss still rechecks after building its
          children, so a same-thread nested meld that published the root
          meanwhile is returned. The children's constructors run under the
          door's root guard, as they did when the plan re-entered it. Every
          other site, root and key-set plan keeps its guard.
""")

# 4. SitePlanEmission: class constant, slots, __init__, cleanup.
rep("""    __slots__ = Cleanable.__slots__ + [
        "_steps",
        "_site_graph",
        "_winners",
""", """    # Door route key -> the root existence whose normal-plan root miss relies on
    # the calling door's slot guard. Both routes read their store from a Meld
    # attribute assigned once in `Meld.__init__`; lineage (repointed at link and
    # upgrade), cluster (store re-resolved per call) and unique (Spell lock in
    # the door) are deliberately absent.
    DOOR_HELD_ROOT_EXISTENCE: ClassVar[Dict[str, Existence]] = {
        "unique_per_conduit": Existence.unique_per_conduit,
        "spellspace": Existence.unique_per_spell_space,
    }

    __slots__ = Cleanable.__slots__ + [
        "_steps",
        "_site_graph",
        "_winners",
""")
rep("""        "_miss_lines",
        "_context_params",
    ]
""", """        "_miss_lines",
        "_context_params",
        "_root_guard_held_by_door",
    ]
""")
rep("""            arity: int,
            normal_mode: bool = False,
    ) -> None:
        \"\"\"
        Prepare emission state; nothing is emitted until `render`.
""", """            arity: int,
            normal_mode: bool = False,
            door_route_key: Optional[str] = None,
    ) -> None:
        \"\"\"
        Prepare emission state; nothing is emitted until `render`.
""")
rep("""            normal_mode: Emit `(meld)` signatures without `ov` (the caller has
                checked that the key set supplies nothing).

        Returns:
            None.
        \"\"\"
""", """            normal_mode: Emit `(meld)` signatures without `ov` (the caller has
                checked that the key set supplies nothing).
            door_route_key: Normal mode only: the route key of the doors that
                call this plan, or None. Decides whether the root's miss relies
                on the door's guard (see the class contract).

        Returns:
            None.
        \"\"\"
""")
rep("""        # Leading parameters of the plan and of every miss.
        self._context_params: Tuple[str, ...] = ("meld",) if normal_mode else ("meld", "ov")
""", """        # Leading parameters of the plan and of every miss.
        self._context_params: Tuple[str, ...] = ("meld",) if normal_mode else ("meld", "ov")
        # True when the calling door holds the root's slot guard across the plan
        # call (normal mode, eligible route, matching root existence).
        held_existence: Optional[Existence] = None
        if normal_mode and door_route_key is not None:
            held_existence = self.DOOR_HELD_ROOT_EXISTENCE.get(door_route_key)
        root_existence = next(
            step.existence for step in steps if step.instance_key == root_instance_key
        )
        self._root_guard_held_by_door: bool = (
            held_existence is not None and root_existence is held_existence
        )
""")
rep("""        del self._miss_lines
        del self._context_params
""", """        del self._miss_lines
        del self._context_params
        del self._root_guard_held_by_door
""")

# 5. _emit_miss.
rep("""    def _emit_miss(self, index: int, step: SitePlanStep, sid_name: str) -> None:
        \"\"\"
        Emit `_miss{index}`: children, then guard, recheck (P2 when pinned), construction, publication.

        Contract:
            The sites placed inside the miss are built before the guard is taken,
            so the guard covers only this site's recheck, construction and
            publication, as every build lock does in the straight-line lowering.
            A user constructor never runs under another site's build lock.
        \"\"\"
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
        parameters = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
        lines = self._miss_lines
        lines.append(f"def _miss{index}({parameters}):")
        lines.extend(self._unresolved_check_lines(index, "    "))
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
""", """    def _emit_miss(self, index: int, step: SitePlanStep, sid_name: str) -> None:
        \"\"\"
        Emit `_miss{index}`: children, then guard, recheck (P2 when pinned), construction, publication.

        Contract:
            The sites placed inside the miss are built before the guard is taken,
            so the guard covers only this site's recheck, construction and
            publication, as every build lock does in the straight-line lowering.
            Within the plan, a user constructor never runs under another site's
            build lock.
            Door-held root (0.2.73): when this is the root's miss and
            `_root_guard_held_by_door` is set, the `with` line is omitted and the
            recheck, construction and publication run at the miss's top level.
            The calling door holds this same slot guard for the whole call (see
            the class contract), so nothing else changes: the recheck still
            follows the children, and publication is the same statement.
        \"\"\"
        spell_name = f"spells[{index}]"
        store = f"c{index}"
        supplied = self._supplied_names(step)
        children: List[str] = []
        uses_many_store = self._emit_context(index, "    ", children)
        guarded = not (index == self._root_index and self._root_guard_held_by_door)
        body_indent = "        " if guarded else "    "
        inner_indent = body_indent + "    "
        inner: List[str] = []
        self._emit_construct(index, step, self._direct[index], supplied, inner_indent, inner)
        if step.spell.has_disposal_methods:
            disposal_name = self._bind(f"dm{index}", step.spell.disposal_method_names)
            inner.append(
                f"{inner_indent}{store}.add_creation({sid_name}, v{index}, "
                f"has_disposal_methods=True, disposal_methods={disposal_name})"
            )
        else:
            inner.append(f"{inner_indent}{store}._creations[{sid_name}] = v{index}")
        parameters = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
        lines = self._miss_lines
        lines.append(f"def _miss{index}({parameters}):")
        lines.extend(self._unresolved_check_lines(index, "    "))
        if uses_many_store:
            lines.extend(self._many_store_prologue("    "))
        lines.extend(children)
        if guarded:
            lines.append(f"    with {self._guard(step, store, sid_name, spell_name)}:")
        lines.append(f"{body_indent}v{index} = {store}._creations.get({sid_name})")
        if supplied:
            lines.append(f"{body_indent}if v{index} is not None:")
            lines.append(f"{body_indent}    _raise_existing_override({spell_name}, root_spell_id)")
        lines.append(f"{body_indent}if v{index} is None:")
        lines.extend(inner)
        lines.append(f"{body_indent}return v{index}")
""")
p.write_bytes(t.encode("utf-8"))
print("site_plan_lowering.py edited")
