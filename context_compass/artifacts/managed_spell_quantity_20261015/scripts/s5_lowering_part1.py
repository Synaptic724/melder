"""Edits 1-6 of the S5 lowering change (imports, helpers, emission state)."""
EDITS = []

EDITS.append((
'''if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
''',
'''if TYPE_CHECKING:
    from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
    from melder.aether.spellbook.spell import Spell
''',
))

EDITS.append((
'''        Hold the cold-path helpers a plan reads from its namespace: the
        generic construct with supplied values, the P2 refusal, the
        unresolved-input refusal and the equal-rank conflict guard. None of
        them runs on a direct-call step.
''',
'''        Hold the cold-path helpers a plan reads from its namespace: the
        generic construct with supplied values, the P2 refusal, the
        unresolved-input refusal and the equal-rank conflict guard. None of
        them runs on a direct-call step. Plans with a leasing managed site
        also read the lease returns and the missing-pool refusal
        (managed_spell_quantity S5, 2026-10-15); every other plan binds none
        of the three.
''',
))

EDITS.append((
'''        access: internal. Generic construct with supplied values, P2 refusal and the E1
        conflict guard for emitted key-set plans.
    """
''',
'''        access: internal. Generic construct with supplied values, P2 refusal, the E1
        conflict guard, and the managed lease returns and missing-pool refusal for emitted
        key-set plans.
    """
''',
))

EDITS.append((
'''        raise MeldExecutionError(
            spell_id=root_spell_id,
            spell_name=root_spell_name,
            message="Failed to apply overrides.",
            inner=conflict,
        ) from conflict


class SitePlanLowering:
''',
'''        raise MeldExecutionError(
            spell_id=root_spell_id,
            spell_name=root_spell_name,
            message="Failed to apply overrides.",
            inner=conflict,
        ) from conflict

    @staticmethod
    def return_leases(
            error: BaseException,
            leases: Tuple[Tuple[ManagedSpellQuantity, Any], ...],
    ) -> None:
        """
        Put back the objects a plan leased for a holder that was never built (F9).

        Purpose:
            Called from the `except BaseException` of a lease group: the holder's
            construction region (a later lease's build, the construction, a
            pinned refusal, the publication) raised after some of its leases
            were taken. Melder gives back what it leased for an object that does
            not exist; leases already passed to a built object are the holder's.

        Contract:
            - Every `(pool, object)` pair whose object is not None goes back
              through `pool.put_back` (the pool's resets run). None marks a lease
              the group never took (a class spell's construction never yields
              None) and is skipped.
            - A put-back that raises (a pool torn down meanwhile, a raising
              reset) becomes one note on `error` - "Returning an object leased
              from managed spell '<name>' failed: <failure>" - and the remaining
              pairs still go back. Nothing new is raised; the caller re-raises
              `error`.

        Args:
            error: The exception propagating from the holder's region.
            leases: The group's `(pool, object)` pairs in lease order.

        Returns:
            None.
        """
        for pool, obj in leases:
            if obj is None:
                continue
            try:
                pool.put_back(obj)
            except Exception as failure:
                # Best effort on an exception path: report on the propagating
                # error instead of replacing it.
                error.add_note(
                    f"Returning an object leased from managed spell '{pool.spell_name}' failed: {failure}"
                )

    @staticmethod
    def return_unused_leases(leases: Tuple[Tuple[ManagedSpellQuantity, Any], ...]) -> None:
        """
        Put back the leases of a shared holder whose cold race another meld won.

        Purpose:
            A shared consumer's miss leases its managed dependencies before its
            build guard. When the recheck under the guard finds the holder
            already published, the plan returns that holder and gives these
            leases back.

        Contract:
            - Every pair goes back through `pool.put_back`, even after one fails.
            - Failures are raised once all were tried, as one ExceptionGroup
              "Returning objects leased for a construction another meld finished
              first failed" of RuntimeErrors ("Returning an object leased from
              managed spell '<name>' failed: <failure>"), each chained from its
              failure.

        Args:
            leases: The `(pool, object)` pairs taken for the holder; every object is set.

        Raises:
            ExceptionGroup: When any put-back raised.

        Returns:
            None.
        """
        failures: List[Exception] = []
        for pool, obj in leases:
            try:
                pool.put_back(obj)
            except Exception as failure:
                error = RuntimeError(
                    f"Returning an object leased from managed spell '{pool.spell_name}' failed: {failure}"
                )
                error.__cause__ = failure
                failures.append(error)
        if failures:
            raise ExceptionGroup(
                "Returning objects leased for a construction another meld finished first failed",
                failures,
            )

    @staticmethod
    def raise_missing_managed_pool(spell: Spell) -> None:
        """
        Raise the named error for a managed site whose pool cannot be read.

        Contract:
            Called by a per-creation pool read
            (`spells[i]._owner_creations._managed_quantities[sid]`) that raised
            AttributeError or KeyError: the version has no owner store (never
            stamped, or its owner root's store was torn down) or its store holds
            no pool under the id. Nothing was leased or built for the site.

        Args:
            spell: The managed spell.

        Raises:
            MeldExecutionError: Always.
        """
        raise MeldExecutionError(
            spell_id=spell.spell_id,
            spell_name=spell.spell_name,
            node_id=spell.spell_id,
            message=(
                f"Managed spell '{spell.spell_name}' has no pool to lease from: its owner root was torn down, "
                "or this version was never given one (a version staged with bind_inactive before conjure and "
                "notched in after it). Meld it through a live root, or stage the version after conjure."
            ),
        )


class SitePlanLowering:
''',
))

EDITS.append((
'''        - Emission is a pure function of its inputs; the returned source names
          no identities, so equal shapes share one code object.

    Threading:
        Compile-time only; emitted plans take the same locks as the normal lane,
''',
'''        - Emission is a pure function of its inputs; the returned source names
          no identities, so equal shapes share one code object.
        - A `managed_spell_quantity` step is leased from its pool, one site per
          path (managed_spell_quantity S5, 2026-10-15): see "Managed sites" in
          `SitePlanEmission`.

    Threading:
        Compile-time only; emitted plans take the same locks as the normal lane,
''',
))

EDITS.append((
'''        the plan builds its root without taking the root's slot
        guard, because the route door that calls it already holds that same
        guard across the call. See `SitePlanEmission`.
''',
'''        the plan builds its root without taking the root's slot
        guard, because the route door that calls it already holds that same
        guard across the call. See `SitePlanEmission`. A managed site's warm
        lease takes no lock; its miss takes only its pool's leaf lock (in
        `reserve`, `abandon` and `adopt`), never across user code.
''',
))

EDITS[-1] = (
'''        guard, because the route door that calls it already holds that same
        guard across the call. See `SitePlanEmission`.
''',
'''        guard, because the route door that calls it already holds that same
        guard across the call. See `SitePlanEmission`. A managed site's warm
        lease takes no lock; its miss takes only its pool's leaf lock (in
        `reserve`, `abandon` and `adopt`), never across user code.
''',
)
