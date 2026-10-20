"""Edits of the S5 lowering change: emission state, placement, unresolved checks."""
EDITS = []

EDITS.append((
'''          door's root guard, as they did when the plan re-entered it. Every
          other site, root and key-set plan keeps its guard.

    Lifecycle / Cleanup:
''',
'''          door's root guard, as they did when the plan re-entered it. Every
          other site, root and key-set plan keeps its guard.
        - Managed sites (managed_spell_quantity S5, 2026-10-15): a
          `managed_spell_quantity` step is LEASING unless a winning key targets
          one of its own parameters, which makes it FRESH: constructed where a
          many step would be, never pooled, counted, registered or adopted (the
          caller's object). A leasing site has its own `_miss{i}` (like a shared
          site) and exactly one consumer, per path; it is not emitted where it
          is placed but in its consumer's lease group, right before the
          consumer's construction region (inside the consumer's miss, after its
          children, when the consumer has one). The lease is an inline
          `pp{i}()` - the pool and its `_idle.pop` bound as plan constants under
          the owner-store rule (automatic owner, owner store set, pool present
          at emission) - or, per creation, a read of
          `spells[i]._owner_creations._managed_quantities[sid{i}]` (a missing
          store or pool raises the named MeldExecutionError) and
          `h{i}._idle.pop()`; an empty pool calls `_miss{i}(meld, [ov,] h{i},
          ...)`. The miss checks unresolved inputs, then `reserve()` (an object
          served returns at once), then builds its children, its own lease group
          and its construction inside `try`, whose handler calls
          `h{i}.abandon(kids{i} or [], exc)` and re-raises. Disposal-bearing many
          children placed in the miss are appended to `kids{i}` as `(v, dm)` and
          adopted with the object (`h{i}.adopt`), never registered in a store. A
          lease group takes its first lease, sets the others to None, then runs
          the rest and the consumer's construction region inside `try`; on any
          exception `_return_leases` puts back what was taken and the error is
          re-raised. For a shared consumer the region is its guard block, which
          returns from inside; a recheck that finds the holder published (a lost
          race) falls through to `_return_unused_leases`. A plan with no managed
          step takes none of these branches and binds none of the three helpers,
          so its source and namespace are unchanged.

    Lifecycle / Cleanup:
''',
))

EDITS.append((
'''        "_context_params",
        "_root_guard_held_by_door",
    ]
''',
'''        "_context_params",
        "_root_guard_held_by_door",
        "_leasing",
        "_fresh",
        "_has_miss",
        "_leases_by_consumer",
    ]
''',
))

EDITS.append((
'''        self._shared: List[bool] = [step.existence is not Existence.many for step in steps]
''',
'''        # Site kinds (managed_spell_quantity S5): shared (slotted existences),
        # many, leasing managed (its own miss, leased per path) and fresh managed
        # (a winning key on its own parameters: built like many, never pooled).
        self._shared: List[bool] = []
        self._leasing: List[bool] = []
        self._fresh: List[bool] = []
        for step in steps:
            existence = step.existence
            managed = existence is Existence.managed_spell_quantity
            fresh = managed and bool(self._supplied_names(step))
            self._shared.append(existence is not Existence.many and not managed)
            self._leasing.append(managed and not fresh)
            self._fresh.append(fresh)
        # Sites built in an out-of-line `_miss{i}`: shared and leasing managed.
        self._has_miss: List[bool] = [
            shared or leasing for shared, leasing in zip(self._shared, self._leasing)
        ]
        self._leases_by_consumer: Dict[int, Tuple[int, ...]] = {}
        if any(self._leasing):
            # Bound only into plans that lease, so every other namespace is unchanged.
            self._namespace["_return_leases"] = SitePlanRuntimeHelpers.return_leases
            self._namespace["_return_unused_leases"] = SitePlanRuntimeHelpers.return_unused_leases
            self._namespace["_raise_missing_managed_pool"] = SitePlanRuntimeHelpers.raise_missing_managed_pool
''',
))

EDITS.append((
'''        del self._shared
        del self._home
''',
'''        del self._shared
        del self._leasing
        del self._fresh
        del self._has_miss
        del self._leases_by_consumer
        del self._home
''',
))

EDITS.append((
'''              inside its miss (and of its own construction) that live outside it,
              plus what its nested misses need.

        Raises:
            RuntimeError: When a dependency key has no kept step, or a provider
                does not precede its consumer (the family order is providers-first).
''',
'''              inside its miss (and of its own construction) that live outside it,
              plus what its nested misses need. A leasing managed site has a miss
              too and is placed by the same rule: with its one consumer, its home
              is that consumer's miss when the consumer has one, else the
              consumer's home. A fresh managed site is placed like a many step.
            - Leases by consumer: each consumer's leasing providers in operand
              order, without repeats (`_leases_by_consumer`).

        Raises:
            RuntimeError: When a dependency key has no kept step, a provider
                does not precede its consumer (the family order is providers-first),
                or a leasing managed step has other than one consumer (managed
                sites are per path).
''',
))

EDITS.append((
'''            if index == root_index or (self._shared[index] and self._supplied_names(steps[index])):
                home[index] = None
                continue
            contexts = [
                consumer if self._shared[consumer] else home[consumer] for consumer in consumers[index]
            ]
''',
'''            if index == root_index or (self._shared[index] and self._supplied_names(steps[index])):
                home[index] = None
                continue
            if self._leasing[index] and len(set(consumers[index])) != 1:
                raise RuntimeError(
                    f"Key-set plan managed step {index} has {len(set(consumers[index]))} consumers; "
                    "a managed site is per path and feeds exactly one."
                )
            contexts = [
                consumer if self._has_miss[consumer] else home[consumer] for consumer in consumers[index]
            ]
''',
))

EDITS.append((
'''        for index in range(len(steps)):
            if not self._shared[index]:
                continue
            inside = children.get(index, [])
            needed = set()
            for member in inside:
                # A nested shared site builds inside its own miss: only what that
                # miss needs from outside passes through here. A generic member
                # reads its providers through its dict literal, so they pass
                # through exactly like a direct member's call operands.
                if self._shared[member]:
''',
'''        for index in range(len(steps)):
            if not self._has_miss[index]:
                continue
            inside = children.get(index, [])
            needed = set()
            for member in inside:
                # A nested shared or leasing site builds inside its own miss: only
                # what that miss needs from outside passes through here. A generic
                # member reads its providers through its dict literal, so they pass
                # through exactly like a direct member's call operands.
                if self._has_miss[member]:
''',
))

EDITS.append((
'''        self._home = home
        self._children = children
        self._miss_value_params = value_params
        self._root_index = root_index
''',
'''        leases_by_consumer: Dict[int, Tuple[int, ...]] = {}
        for consumer, providers in enumerate(providers_by_consumer):
            leased: List[int] = []
            for provider in providers:
                if self._leasing[provider] and provider not in leased:
                    leased.append(provider)
            if leased:
                leases_by_consumer[consumer] = tuple(leased)
        self._home = home
        self._children = children
        self._miss_value_params = value_params
        self._root_index = root_index
        self._leases_by_consumer = leases_by_consumer
''',
))

EDITS.append((
'''            unresolved inputs gets one unconditional raise at the context top,
            before any construction; shared children check in their own miss.
        """
        candidates = [child for child in self._children.get(context, []) if not self._shared[child]]
''',
'''            unresolved inputs gets one unconditional raise at the context top,
            before any construction; shared and leasing managed children check
            in their own miss. A leasing miss checks before `reserve`, so a
            refusal takes no place from the pool.
        """
        candidates = [child for child in self._children.get(context, []) if not self._has_miss[child]]
''',
))
