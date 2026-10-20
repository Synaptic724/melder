"""S5: Conduit.managed_spell_meld (meld plus a lease) and its import."""
import pathlib
import sys

TARGET = pathlib.Path("src/melder/aether/conduit/conduit.py")

EDITS = [
    (
        '''from melder.aether.conduit.creations.cluster_creations import ClusterCreations
''',
        '''from melder.aether.conduit.creations.cluster_creations import ClusterCreations
from melder.aether.conduit.creations.managed_spell_lease import ManagedSpellLease
''',
    ),
    (
        '''    # Machine identity remains explicit at the public boundary via `spell_id=`;
    # this facade forwards it positionally into the internal ID fast lane.

    def purge(
''',
        '''    # Machine identity remains explicit at the public boundary via `spell_id=`;
    # this facade forwards it positionally into the internal ID fast lane.

    def managed_spell_meld(
            self,
            spell: Optional[Union[str, object]] = None,
            *,
            spell_id: Optional[str] = None,
            spellframe: Optional[Union[str, object]] = None,
            binding_name: Optional[str] = None,
            override: Optional[Union[dict, list, tuple]] = None,
    ) -> ManagedSpellLease[Any]:
        """
        Public API

        Meld one managed spell and return its object as a lease that gives it back.

        Purpose:
            The meld-plus-release form of `Existence.managed_spell_quantity`
            (managed_spell_quantity S5, 2026-10-15):
            `with conduit.managed_spell_meld(Logger) as logger:` leases a pooled
            object and puts it back when the block exits, as
            `ReleaseManagedSpell().release(logger)` would.

        Contract:
            - Takes `meld`'s inputs - a SpellName string, a class, `spell_id=`,
              or a spellframe/binding address - and resolves the target as
              `meld` does. A target of any other existence is refused before
              anything is melded or leased.
            - The pool is the resolved version's pool in its owner root's store,
              read before the meld; a version with no owner store, or a store
              without that pool, is refused with the missing-pool error.
            - The object comes from a meld of the resolved version by id: an
              idle object, else one built into a place the pool reserves
              (limited_quantity and queue apply their mode there).
            - The lease releases once (`release()`, or the end of the `with`
              block, which never suppresses the block's exception). Nothing
              releases it otherwise: an object never released holds its place
              until its root is torn down.
            - With `override`, keys on the managed spell's own parameters build
              a fresh object the pool never counted; the lease still puts it
              into the pool when released, as releasing any object of the class
              does.

        Args:
            spell:
                A SpellName string, or the managed class.
            spell_id:
                The managed version id; exclusive with `spell`.
            spellframe:
                Optional spellframe used for resolution.
            binding_name:
                Optional binding name used for resolution.
            override:
                Optional override payload passed to the meld.

        Returns:
            ManagedSpellLease:
                The leased object (`.object`, or the `with` target) and its pool.

        Raises:
            ValueError:
                When both `spell` and `spell_id` are given, no identity is
                given, or the target is not `Existence.managed_spell_quantity`.
            TypeError:
                When `spell_id` is not a string.
            KeyError:
                When no spell resolves.
            MeldExecutionError:
                When the version has no pool to lease from; the pool's
                ManagedSpellExhaustedError (limited_quantity at its limit, queue
                at its timeout); anything the meld raises.
            RuntimeError:
                When the conduit is cleaned, or the pool was torn down with its
                root.
        """
        if self._cleaned:
            self.check_cleaned()
        if spell is not None and spell_id is not None:
            raise ValueError("managed_spell_meld accepts either `spell` or `spell_id`, not both.")
        if spell_id is not None and type(spell_id) is not str:
            raise TypeError(f"managed_spell_meld `spell_id` must be a string; got {type(spell_id).__name__}.")
        internal_spell = spell
        internal_spell_name = None
        if spell_id is not None:
            internal_spell = spell_id
        elif isinstance(spell, str):
            internal_spell = None
            internal_spell_name = spell
        target = self._meld._resolve_spell(
            spell=internal_spell,
            spell_name=internal_spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
        )
        existence = target.existence
        if existence is not Existence.managed_spell_quantity:
            raise ValueError(
                f"managed_spell_meld leases a managed spell; '{target.spell_name}' is {existence.name}. "
                "Meld it with meld(), or bind it with existence=Existence.managed_spell_quantity."
            )
        try:
            pool = target._owner_creations.get_managed_quantity(target.spell_id)
        except AttributeError:
            # No owner store (the version was never stamped), or a store retired with its root.
            pool = None
        if pool is None:
            # Imported here, as the other cold-path imports of this module are:
            # the lowering's helpers own the one missing-pool message.
            from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_lowering import (
                SitePlanRuntimeHelpers,
            )

            SitePlanRuntimeHelpers.raise_missing_managed_pool(target)
        obj = self.meld(spell_id=target.spell_id, override=override)
        return ManagedSpellLease(obj, pool)

    def purge(
''',
    ),
]


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    for old, new in EDITS:
        if text.count(old) != 1:
            print("NOT UNIQUE", text.count(old), old[:80])
            return 1
        text = text.replace(old, new)
    TARGET.write_text(text, encoding="utf-8", newline="")
    print("conduit edited")
    return 0


if __name__ == "__main__":
    sys.exit(main())
