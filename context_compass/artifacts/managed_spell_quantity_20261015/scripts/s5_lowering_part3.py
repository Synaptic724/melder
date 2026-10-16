"""Edits of the S5 lowering change: context, many, shared miss, the managed emitters."""
EDITS = []

EDITS.append((
'''            The source defines one `_miss{i}` per kept shared site, then the plan
''',
'''            The source defines one `_miss{i}` per kept shared or leasing managed site, then the plan
''',
))

EDITS.append((
'''        Return the parameter/argument names after `(meld, ov, c{i})` for one miss.
''',
'''        Return the parameter/argument names after `(meld, ov, c{i})` (`h{i}` for a leasing site) for one miss.
''',
))

EDITS.append((
'''            plan prologue points at the meld's innermost scope; shared site i's
            miss registers through `c{i}`, the store that site publishes to.

        Args:
            context: None for the plan's top level, else the shared site whose
                miss body is being emitted.
            indent: Indentation of the emitted lines.
            lines: Target line list, appended in place.

        Returns:
            bool: True when a disposal-bearing many step at the top level reads
            `many_store` (the caller then emits the prologue); always False
            for a miss, whose children use its `c{i}` parameter.
        """
        store = "many_store" if context is None else f"c{context}"
        uses_many_store = False
        for index in self._children.get(context, []):
            step = self._steps[index]
            if self._shared[index]:
                self._emit_shared_hit(index, step, indent, lines)
            elif self._emit_many(index, step, indent, lines, store) and context is None:
                uses_many_store = True
        return uses_many_store
''',
'''            plan prologue points at the meld's innermost scope; shared site i's
            miss registers through `c{i}`, the store that site publishes to.
            Inside leasing managed site i's miss it is appended to `kids{i}`
            instead, to be adopted with the object (managed_spell_quantity S5).
            A leasing site is emitted by its consumer's lease group, not where
            it is placed; only a leasing root leases here.

        Args:
            context: None for the plan's top level, else the shared or leasing
                site whose miss body is being emitted.
            indent: Indentation of the emitted lines.
            lines: Target line list, appended in place.

        Returns:
            bool: True when a disposal-bearing many step at the top level reads
            `many_store` (the caller then emits the prologue); always False
            for a miss, whose children use its `c{i}` parameter or `kids{i}`.
        """
        store = "many_store" if context is None else f"c{context}"
        kids_name = self._kids_name(context) if context is not None and self._leasing[context] else None
        uses_many_store = False
        for index in self._children.get(context, []):
            step = self._steps[index]
            if self._shared[index]:
                self._emit_shared_hit(index, step, indent, lines)
            elif self._leasing[index]:
                if index == self._root_index:
                    self._emit_root_lease(index, indent, lines)
            elif self._emit_many(index, step, indent, lines, store, kids_name) and context is None:
                uses_many_store = True
        return uses_many_store
''',
))

EDITS.append((
'''    def _emit_many(self, index: int, step: SitePlanStep, indent: str, lines: List[str], store: str) -> bool:
        """
        Emit one many step: construction, then its disposal registration in `store`.

        Contract:
            A step without disposal methods is constructed and not recorded
            anywhere. A disposal-bearing step is recorded through
            `<store>.register_many(sidN, vN, dmN)` right after construction,
            before any build lock of the context is taken.

        Args:
            index: Kept step index.
            step: The step.
            indent: Indentation of the emitted lines.
            lines: Target line list, appended in place.
            store: The store expression the registration targets - `many_store`
                (the meld's innermost scope) at the top level, `c{i}` inside
                shared site i's miss (the store the holder belongs to).

        Returns:
            bool: True when the step registers (it declares disposal methods).
        """
        self._emit_construct(index, step, self._direct[index], self._supplied_names(step), indent, lines)
        if not step.spell.has_disposal_methods:
            return False
''',
'''    def _emit_many(
            self,
            index: int,
            step: SitePlanStep,
            indent: str,
            lines: List[str],
            store: str,
            kids_name: Optional[str] = None,
    ) -> bool:
        """
        Emit one many (or fresh managed) step: construction, then its disposal registration in `store`.

        Contract:
            A step without disposal methods is constructed and not recorded
            anywhere. A disposal-bearing step is recorded through
            `<store>.register_many(sidN, vN, dmN)` right after construction,
            before any build lock of the context is taken - or, inside a leasing
            managed miss, appended as `(vN, dmN)` to `kids_name`. A fresh
            managed step (a winning key on its own parameters) is recorded
            nowhere: it is the caller's object. The construction runs inside
            the step's lease group when it reads leasing managed sites
            (managed_spell_quantity S5).

        Args:
            index: Kept step index.
            step: The step.
            indent: Indentation of the emitted lines.
            lines: Target line list, appended in place.
            store: The store expression the registration targets - `many_store`
                (the meld's innermost scope) at the top level, `c{i}` inside
                shared site i's miss (the store the holder belongs to).
            kids_name: `kids{i}` inside leasing managed site i's miss, else None.

        Returns:
            bool: True when the step registers in `store`.
        """
        self._emit_leased_region(index, indent, lines, self._construct_region(index, step))
        if self._fresh[index] or not step.spell.has_disposal_methods:
            return False
        if kids_name is not None:
            kids_disposal_name = self._bind(f"dm{index}", step.spell.disposal_method_names)
            lines.append(f"{indent}{kids_name}.append((v{index}, {kids_disposal_name}))")
            return False
''',
))

EDITS.append((
'''            contract); a miss without disposal-bearing children emits no call.
        """
        spell_name = f"spells[{index}]"
        store = f"c{index}"
        supplied = self._supplied_names(step)
        children: List[str] = []
        self._emit_context(index, "    ", children)
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
        adopted = [
            child for child in self._children.get(index, [])
            if not self._shared[child] and self._steps[child].spell.has_disposal_methods
        ]
        if adopted:
            # The children `_emit_many` registered in this store move into the
            # holder's disposal record once it is published (0.2.8238).
            pairs = ", ".join(f"(sid{child}, v{child})" for child in adopted)
            trailing = "," if len(adopted) == 1 else ""
            inner.append(f"{inner_indent}{store}.adopt_children({sid_name}, v{index}, ({pairs}{trailing}))")
        parameters = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
        lines = self._miss_lines
        lines.append(f"def _miss{index}({parameters}):")
        lines.extend(self._unresolved_check_lines(index, "    "))
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
''',
'''            contract); a miss without disposal-bearing children emits no call.
            Leases (managed_spell_quantity S5): when this site reads leasing
            managed sites they are leased after its children and before the
            guard, and the guard block runs inside the lease group's `try`. It
            returns the site from inside once published; any exception puts the
            leases back; a recheck that finds the site already published falls
            out of the block to `_return_unused_leases` and returns that site.
            Without leases the emitted miss is unchanged.
        """
        spell_name = f"spells[{index}]"
        store = f"c{index}"
        supplied = self._supplied_names(step)
        children: List[str] = []
        self._emit_context(index, "    ", children)
        guarded = not (index == self._root_index and self._root_guard_held_by_door)
        leases = self._leases_by_consumer.get(index, ())

        def guard_region(region_indent: str, target: List[str]) -> None:
            # Guard, recheck (P2 when pinned), construction, publication, adoption.
            body_indent = region_indent + "    " if guarded else region_indent
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
            adopted = [
                child for child in self._children.get(index, [])
                if self._is_plain_many(child) and self._steps[child].spell.has_disposal_methods
            ]
            if adopted:
                # The children `_emit_many` registered in this store move into the
                # holder's disposal record once it is published (0.2.8238).
                pairs = ", ".join(f"(sid{child}, v{child})" for child in adopted)
                trailing = "," if len(adopted) == 1 else ""
                inner.append(f"{inner_indent}{store}.adopt_children({sid_name}, v{index}, ({pairs}{trailing}))")
            if leases:
                # Return from inside: falling out of the block means another meld
                # published this site first (a lost cold race).
                inner.append(f"{inner_indent}return v{index}")
            if guarded:
                target.append(f"{region_indent}with {self._guard(step, store, sid_name, spell_name)}:")
            target.append(f"{body_indent}v{index} = {store}._creations.get({sid_name})")
            if supplied:
                target.append(f"{body_indent}if v{index} is not None:")
                target.append(f"{body_indent}    _raise_existing_override({spell_name}, root_spell_id)")
            target.append(f"{body_indent}if v{index} is None:")
            target.extend(inner)
            if not leases:
                target.append(f"{body_indent}return v{index}")

        body: List[str] = self._unresolved_check_lines(index, "    ")
        body.extend(children)
        if self._emit_leased_region(index, "    ", body, guard_region):
            body.append(f"    _return_unused_leases({self._lease_pairs(leases)})")
            body.append(f"    return v{index}")
        parameters = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
        self._miss_lines.append(f"def _miss{index}({parameters}):")
        self._miss_lines.extend(body)

    def _is_plain_many(self, index: int) -> bool:
        """
        Return True for a kept `many` step (not shared, and not a managed site of either kind).
        """
        return not (self._shared[index] or self._leasing[index] or self._fresh[index])

    def _kids_name(self, index: int) -> Optional[str]:
        """
        Return `kids{index}` when leasing site `index`'s miss builds a disposal-bearing many child, else None.
        """
        for child in self._children.get(index, []):
            if self._is_plain_many(child) and self._steps[child].spell.has_disposal_methods:
                return f"kids{index}"
        return None

    def _construct_region(self, index: int, step: SitePlanStep) -> Callable[[str, List[str]], None]:
        """
        Return the emitter of one step's construction (`v{index} = ...`) at the indentation it is given.
        """

        def region(indent: str, lines: List[str]) -> None:
            self._emit_construct(index, step, self._direct[index], self._supplied_names(step), indent, lines)

        return region

    def _emit_leased_region(
            self,
            consumer: int,
            indent: str,
            lines: List[str],
            region: Callable[[str, List[str]], None],
    ) -> bool:
        """
        Emit a consumer's construction region, inside its lease group when it reads leasing sites.

        Contract:
            - Without leases the region is emitted as is (every non-managed plan).
            - With leases m1..mn (operand order): the per-creation pool reads,
              the lease of m1, `v{m2..mn} = None`, then `try:` the remaining
              leases and the region, `except BaseException as exc:
              _return_leases(exc, ((h{m}, v{m}), ...))` and `raise`. Nothing but
              the consumer's other leases runs between a lease and the region,
              and a pool read that raises does so before anything is leased.

        Args:
            consumer: Kept index of the step whose region is emitted.
            indent: Indentation of the group; the region is one level deeper
                inside the `try`.
            lines: Target line list, appended in place.
            region: Emits the region at the indentation it is given.

        Returns:
            bool: True when a lease group was emitted.
        """
        leases = self._leases_by_consumer.get(consumer)
        if not leases:
            region(indent, lines)
            return False
        constant = {lease: self._bind_lease_pool(lease) for lease in leases}
        for lease in leases:
            if not constant[lease]:
                self._emit_pool_read(lease, indent, lines)
        first = leases[0]
        self._emit_lease(first, constant[first], indent, lines)
        for lease in leases[1:]:
            lines.append(f"{indent}v{lease} = None")
        inner = indent + "    "
        lines.append(f"{indent}try:")
        for lease in leases[1:]:
            self._emit_lease(lease, constant[lease], inner, lines)
        region(inner, lines)
        lines.append(f"{indent}except BaseException as exc:")
        lines.append(f"{indent}    _return_leases(exc, {self._lease_pairs(leases)})")
        lines.append(f"{indent}    raise")
        return True

    @staticmethod
    def _managed_pool_constant(step: SitePlanStep) -> Optional[ManagedSpellQuantity]:
        """
        Return the pool bound as a plan constant for one leasing site, or None for the per-creation read.

        Contract:
            The owner-store rule of `_owner_store_constant` (S9): only a provider
            owned by an automatic conduit (`_dynamic_environment` False) whose
            owner store already holds the pool. Such a store cannot move, and a
            pool is replaced under its id only by an ownership transfer's
            restore, which needs a dynamic world. The pool's `_idle` deque is
            assigned once and drained, never swapped, so its bound `pop` stays
            valid; a pool torn down with its root has a drained deque, so a
            constant lease misses and `reserve` raises the pool's own error.

        Args:
            step: The leasing managed step.

        Returns:
            Optional[ManagedSpellQuantity]: The pool, or None.
        """
        spell = step.spell
        if spell._dynamic_environment:
            return None
        owner = spell._owner_creations
        if owner is None:
            return None
        return owner.get_managed_quantity(spell.spell_id)

    def _bind_lease_pool(self, index: int) -> bool:
        """
        Bind one leasing site's version id, and its pool and pop when they are plan constants.

        Returns:
            bool: True when `h{index}` and `pp{index}` are bound (the constant shape).
        """
        step = self._steps[index]
        self._bind(f"sid{index}", step.spell.spell_id)
        pool = self._managed_pool_constant(step)
        if pool is None:
            return False
        self._bind(f"h{index}", pool)
        self._bind(f"pp{index}", pool._idle.pop)
        return True

    @staticmethod
    def _emit_pool_read(index: int, indent: str, lines: List[str]) -> None:
        """
        Emit the per-creation pool read of one leasing site: `h{index}`, or the named missing-pool error.
        """
        lines.append(f"{indent}try:")
        lines.append(f"{indent}    h{index} = spells[{index}]._owner_creations._managed_quantities[sid{index}]")
        lines.append(f"{indent}except (AttributeError, KeyError):")
        lines.append(f"{indent}    _raise_missing_managed_pool(spells[{index}])")

    def _emit_lease(self, index: int, constant: bool, indent: str, lines: List[str]) -> None:
        """
        Emit one lease - the inline pop, else the miss call - and define the site's miss.
        """
        pop = f"pp{index}()" if constant else f"h{index}._idle.pop()"
        arguments = ", ".join(list(self._context_params) + [f"h{index}"] + self._miss_arguments(index))
        lines.append(f"{indent}try:")
        lines.append(f"{indent}    v{index} = {pop}")
        lines.append(f"{indent}except IndexError:")
        lines.append(f"{indent}    v{index} = _miss{index}({arguments})")
        self._emit_leasing_miss(index, self._steps[index])

    def _emit_root_lease(self, index: int, indent: str, lines: List[str]) -> None:
        """
        Emit a leasing root's pool read and lease at the plan top; the plan returns the leased object.
        """
        constant = self._bind_lease_pool(index)
        if not constant:
            self._emit_pool_read(index, indent, lines)
        self._emit_lease(index, constant, indent, lines)

    def _emit_leasing_miss(self, index: int, step: SitePlanStep) -> None:
        """
        Emit `_miss{index}` of one leasing managed site.

        Contract:
            `def _miss{i}(meld, [ov,] h{i}, <outer values>)`: the unresolved-input
            check (before anything is reserved); `v = h.reserve()` and an early
            return of an object it serves; `kids{i} = []` when disposal-bearing
            many children are built inside; then `try:` the children, the site's
            own lease group and its construction, `except BaseException as exc:
            h.abandon(kids or [], exc)` and `raise` (an inner lease group has
            already put its leases back); then `h.adopt(v, kids)` when kids
            exist, and `return v`. `adopt` on a pool torn down meanwhile disposes
            the object and its kids and raises the pool's error.
        """
        pool = f"h{index}"
        kids = self._kids_name(index)
        body: List[str] = self._unresolved_check_lines(index, "    ")
        body.append(f"    v{index} = {pool}.reserve()")
        body.append(f"    if v{index} is not None:")
        body.append(f"        return v{index}")
        if kids is not None:
            body.append(f"    {kids} = []")
        body.append("    try:")
        self._emit_context(index, "        ", body)
        self._emit_leased_region(index, "        ", body, self._construct_region(index, step))
        body.append("    except BaseException as exc:")
        body.append(f"        {pool}.abandon({kids if kids is not None else '[]'}, exc)")
        body.append("        raise")
        if kids is not None:
            body.append(f"    {pool}.adopt(v{index}, {kids})")
        body.append(f"    return v{index}")
        parameters = ", ".join(list(self._context_params) + [pool] + self._miss_arguments(index))
        self._miss_lines.append(f"def _miss{index}({parameters}):")
        self._miss_lines.extend(body)

    @staticmethod
    def _lease_pairs(leases: Tuple[int, ...]) -> str:
        """
        Return the `((h{m}, v{m}), ...)` tuple literal of one lease group.
        """
        pairs = ", ".join(f"(h{lease}, v{lease})" for lease in leases)
        trailing = "," if len(leases) == 1 else ""
        return f"({pairs}{trailing})"
''',
))
