"""D4/D5 src edits (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, notch 0.2.8238): holder-owned many children.

Creations records a slotted holder's disposal-bearing `many` children with the holder (`HolderDisposalEntry`,
`adopt_children`, one disposal dispatch, extract/restore rows with children); the site-plan miss adopts the children
it registered right after it publishes the holder.
Run from anywhere: python <this file> <tree root>
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edit_tool

ROOT = pathlib.Path(sys.argv[1])
CREATIONS = str(ROOT / "src/melder/aether/conduit/creations/creations.py")
LOWERING = str(ROOT / "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py")

creations_edits = [
    (
        '''        self.entries = entries
        self.methods = methods


StoredDisposalEntry = Tuple[object, List[str]]
StoredDisposalValue = Union[StoredDisposalEntry, ManyDisposalBucket]
''',
        '''        self.entries = entries
        self.methods = methods


class HolderDisposalEntry:
    """
    Cleanup-only record of one slotted holder and the `many` children built for it.

    Purpose:
        Keep a holder's disposal-bearing `many` children with the holder
        (slotted_lifetime_ownership, 0.2.8238). Since 0.2.8235 an emitted miss
        registers each child in the holder's store before it builds the
        holder; once the holder is published, the miss moves those children
        out of their spells' `many` buckets into this record
        (`Creations.adopt_children`). Every store verb keyed by the holder -
        purge, extract/restore for an ownership transfer, whole-store disposal
        - then reaches the children with the holder, through one dict read.

    Contract:
        - `item` is the holder: the object `_creations` holds under the
          holder's spell id.
        - `methods` is the holder Spell's established ordered disposal list,
          retained by reference. It is empty when the holder declares no
          disposal method; the record then exists for the holder's children.
        - `children` lists `(child, child_methods)` pairs in build order;
          `child_methods` is the child Spell's own list, the object its
          `ManyDisposalBucket` carried, retained by reference.
        - A child is in exactly one place: its spell's `many` bucket or one
          holder record, never both.
        - Disposal runs the holder's methods, then each child's, newest child
          first, so a holder whose own disposal uses a child still finds it
          open (`Creations._dispose_holder_entry`).
        - Every field is borrowed. The owning `Creations` store detaches the
          record (cleanup, clear, purge, extract) and disposes from it; the
          record owns nothing and needs no cleanup.

    AGENT_ACCESS: internal
    """

    __slots__ = ("item", "methods", "children")

    def __init__(
            self,
            item: object,
            methods: List[str],
            children: List[Tuple[object, List[str]]],
    ) -> None:
        """
        Bind the holder, its disposal list and its adopted children.

        Args:
            item: The holder object (borrowed).
            methods: The holder Spell's ordered disposal method names (borrowed;
                an empty list when the holder declares none).
            children: `(child, child_methods)` pairs in build order. The list
                object itself is kept.

        Returns:
            None.
        """
        self.item = item
        self.methods = methods
        self.children = children


StoredDisposalEntry = Tuple[object, List[str]]
StoredDisposalValue = Union[StoredDisposalEntry, ManyDisposalBucket, HolderDisposalEntry]
''',
    ),
    (
        '''            bucket, a tuple and a second append per creation). A many key
            therefore carries one disposal declaration: every entry of the
            key is disposal-bearing or none is.
''',
        '''            bucket, a tuple and a second append per creation). A many key
            therefore carries one disposal declaration: every entry of the
            key is disposal-bearing or none is.
          - a slotted holder that adopted `many` children (0.2.8238):
            `spell_id -> HolderDisposalEntry` (the holder, its methods -
            possibly none - and its children with theirs) in place of the
            tuple. Adopted children leave their spell's bucket, so a `many`
            key holds only objects that no holder owns.
''',
    ),
    (
        '''        - `_lock` (the store lock) is a LEAF lock over the two registries. It
          is held only for dict reads and writes: publish of disposal-bearing
          entries, many append, purge detach, extract/restore and whole-store
          swap. It is never held while acquiring another lock and never
          around user code. (A publish without disposal methods is one atomic
          dict store under the caller's build lock; see `add_creation`.)
''',
        '''        - `_lock` (the store lock) is a LEAF lock over the two registries. It
          is held only for dict reads and writes: publish of disposal-bearing
          entries, many append, child adoption, purge detach, extract/restore
          and whole-store swap. It is never held while acquiring another lock
          and never around user code. (A publish without disposal methods is
          one atomic dict store under the caller's build lock; see
          `add_creation`.)
''',
    ),
    (
        '''        within a `many` bucket. Resolution registers a dependency before the
        dependent that holds it, so forward teardown would dispose the
        dependency while a dependent's own disposal method may still need it.
''',
        '''        within a `many` bucket. Resolution registers a dependency before the
        dependent that holds it, so forward teardown would dispose the
        dependency while a dependent's own disposal method may still need it.
        For the same reason a holder's record disposes the holder before the
        children it adopted, newest child first (0.2.8238).
''',
    ),
    (
        '''        Contract:
            - Singleton metadata delegates to `_attempt_cleanup`.
            - Many buckets delegate to `_dispose_many_creations`.
            - Collected failures never prevent trying the next selected object;
''',
        '''        Contract:
            - Singleton metadata delegates to `_attempt_cleanup`.
            - Many buckets delegate to `_dispose_many_creations`.
            - Holder records delegate to `_dispose_holder_entry`: the holder,
              then its adopted children newest-first (0.2.8238). The three-way
              dispatch is inline, as `_dispose_entry` spells it out, so a scope
              exit pays no extra call per record.
            - Collected failures never prevent trying the next selected object;
''',
    ),
    (
        '''        errors: List[Exception] = []
        for value in reversed(disposable_registry.values()):
            if isinstance(value, tuple):
                errors.extend(self._attempt_cleanup(value))
                continue
            if isinstance(value, ManyDisposalBucket):
                errors.extend(self._dispose_many_creations(value))
        return errors

    def slot_guard(self, spell_id: str) -> RLock:
''',
        '''        errors: List[Exception] = []
        for value in reversed(disposable_registry.values()):
            if isinstance(value, tuple):
                errors.extend(self._attempt_cleanup(value))
            elif isinstance(value, ManyDisposalBucket):
                errors.extend(self._dispose_many_creations(value))
            else:
                errors.extend(self._dispose_holder_entry(value))
        return errors

    def _dispose_holder_entry(self, entry: HolderDisposalEntry) -> List[Exception]:
        """
        Dispose one detached holder record: the holder, then its adopted children.

        Purpose:
            Give every retirement keyed by a holder - whole-store disposal and
            purge - one way to take the holder's `many` children with it
            (0.2.8238).

        Contract:
            - Runs the holder's declared methods first (none when its list is
              empty), then each child's methods, newest child first, so a holder
              whose own disposal uses a child still finds it open.
            - Every method of every object runs even after one fails; each
              failure is one chained `RuntimeError` from `_attempt_cleanup`.
            - Does not mutate the record or its borrowed lists and takes no
              lock: the caller detached the record and released its locks.

        Args:
            entry:
                The detached `HolderDisposalEntry`.

        Returns:
            List[Exception]:
                Disposal failures in attempt order; empty when every method
                succeeded.
        """
        errors = self._attempt_cleanup((entry.item, entry.methods))
        for child, methods in reversed(entry.children):
            errors.extend(self._attempt_cleanup((child, methods)))
        return errors

    def _dispose_entry(self, value: StoredDisposalValue) -> List[Exception]:
        """
        Dispose one detached disposal-registry value, whatever its shape.

        Purpose:
            One dispatch over the three record shapes `_disposable_creations`
            holds, for retirements of one record such as purge (0.2.8238).
            Whole-store disposal runs the same dispatch inline in its loop.

        Contract:
            - An `(object, methods)` tuple goes to `_attempt_cleanup`.
            - A `ManyDisposalBucket` goes to `_dispose_many_creations` (newest
              object first).
            - A `HolderDisposalEntry` goes to `_dispose_holder_entry` (the
              holder, then its children newest-first).
            - Takes no lock; the caller detached the value first.

        Args:
            value:
                The detached record.

        Returns:
            List[Exception]:
                Disposal failures in attempt order.
        """
        if isinstance(value, tuple):
            return self._attempt_cleanup(value)
        if isinstance(value, ManyDisposalBucket):
            return self._dispose_many_creations(value)
        return self._dispose_holder_entry(value)

    def slot_guard(self, spell_id: str) -> RLock:
''',
    ),
    (
        '''        if has_disposal_methods and record is None:
            self._disposable_creations[key] = ManyDisposalBucket(
                bucket,
                disposal_methods if disposal_methods is not None else [],
            )
        bucket.append(item)

    def get_creation(self, spell_id: str) -> Optional[Any]:
''',
        '''        if has_disposal_methods and record is None:
            self._disposable_creations[key] = ManyDisposalBucket(
                bucket,
                disposal_methods if disposal_methods is not None else [],
            )
        bucket.append(item)

    def adopt_children(
            self,
            holder_key: str,
            holder: object,
            children: Tuple[Tuple[str, object], ...],
    ) -> None:
        """
        Record a just-published holder's `many` children with the holder.

        Purpose:
            Make a slotted holder own the disposal-bearing `many` children built
            for it (slotted_lifetime_ownership, 0.2.8238). An emitted miss builds
            and registers each child in this store (`register_many`, before the
            holder's build lock), then builds and publishes the holder; right
            after publication, under the holder's build lock, it calls this verb,
            which moves the children out of their spells' `many` buckets into
            the holder's disposal record. Purge, extract/restore and whole-store
            disposal of the holder then take the children with it.

        Contract:
            - Cold path only: one call per holder publication.
            - Does nothing when this store was cleaned, or when the slot no
              longer holds `holder` (a whole-store clear swapped the registries
              after publication, and the children went with that generation).
            - Each `(child_key, child)` is removed by identity from the key's
              live bucket, scanning from the end - the child was appended
              moments ago, so the scan normally stops at once. The key's method
              list is taken from its `ManyDisposalBucket`. A bucket left empty
              is dropped with its record, so a later registration of that key
              starts again at the end of the registry. A child no longer in its
              bucket (a concurrent `many` purge retired it) is skipped.
            - The holder's disposal value becomes a `HolderDisposalEntry`: a
              `(holder, methods)` tuple is replaced in place, keeping its
              registry position; a holder published without disposal methods
              gets a new record with `methods=[]`. With no child found, nothing
              changes.
            - Children registered without disposal methods are never passed in:
              no store tracks them.

        Args:
            holder_key:
                The holder's spell id (its slot in this store).
            holder:
                The holder object just published under `holder_key`.
            children:
                `(child_spell_id, child)` pairs in build order - exactly the
                disposal-bearing `many` children the miss registered here.

        Returns:
            None.

        Threading:
            The caller holds the holder's build lock (its slot guard, or
            `Spell._lock` for `unique`); this verb takes the store lock as a
            leaf, as every registration does, so no lock-order edge is added.
            No user code runs under it.
        """
        with self._lock:
            if self._cleaned or self._creations.get(holder_key) is not holder:
                return
            adopted: List[Tuple[object, List[str]]] = []
            for child_key, child in children:
                record = self._disposable_creations.get(child_key)
                if record is None:
                    continue
                bucket = record.entries
                for index in range(len(bucket) - 1, -1, -1):
                    if bucket[index] is child:
                        del bucket[index]
                        break
                else:
                    continue
                adopted.append((child, record.methods))
                if not bucket:
                    del self._creations[child_key]
                    del self._disposable_creations[child_key]
            if not adopted:
                return
            current = self._disposable_creations.get(holder_key)
            if current is None:
                self._disposable_creations[holder_key] = HolderDisposalEntry(holder, [], adopted)
            elif isinstance(current, HolderDisposalEntry):
                current.children.extend(adopted)
            else:
                self._disposable_creations[holder_key] = HolderDisposalEntry(holder, current[1], adopted)

    def get_creation(self, spell_id: str) -> Optional[Any]:
''',
    ),
    (
        '''            - Disposal uses the recorded methods without rematching or copying
              the Spell-owned method-name list. Many entries run newest-first;
              each object's methods run in their established order.
''',
        '''            - Disposal uses the recorded methods without rematching or copying
              the Spell-owned method-name list. Many entries run newest-first;
              each object's methods run in their established order.
            - A holder's record is detached with the holder, so the `many`
              children it adopted are disposed after it, newest first (0.2.8238);
              the count stays the target's own entries. A `many` target's bucket
              holds only children that no holder adopted, so purging a child
              spell never disposes a child its live holder still uses.
''',
    ),
    (
        '''        errors: List[Exception] = []
        if isinstance(disposal, tuple):
            errors = self._attempt_cleanup(disposal)
        elif isinstance(disposal, ManyDisposalBucket):
            errors = self._dispose_many_creations(disposal)
        # Keep non-disposable objects alive until the removal locks are released.
''',
        '''        errors: List[Exception] = []
        if disposal is not None:
            errors = self._dispose_entry(disposal)
        # Keep non-disposable objects alive until the removal locks are released.
''',
    ),
    (
        '''            - Retains each established method-list reference in the returned
              rows; this in-memory handoff is not a serialization boundary.

        Threading:
            - Performs extraction under `_lock` so the local slot shape stays
              consistent while the payload is detached.
        """
''',
        '''            - Retains each established method-list reference in the returned
              rows; this in-memory handoff is not a serialization boundary.
            - A holder's row carries the children it adopted (0.2.8238):
              `children` lists `{"stored", "disposal_methods"}` rows in build
              order, and a holder without disposal methods of its own is
              `disposable` with an empty `disposal_methods` list, so a restore
              (an ownership transfer's move or its rollback) takes the children
              wherever the holder goes.

        Threading:
            - Performs extraction under `_lock` so the local slot shape stays
              consistent while the payload is detached.
        """
''',
    ),
    (
        '''                stored_value = self._creations.pop(spell_id)
                disposable_entry = (
                    self._disposable_creations.pop(spell_id)
                    if isinstance(disposable_value, tuple)
                    else None
                )
                entry = {
                    "scope": "unique",
                    "disposable": disposable_entry is not None,
                    "stored": stored_value,
                }
                if disposable_entry is not None:
                    entry["disposal_methods"] = disposable_entry[1]
                extracted.append(entry)
''',
        '''                stored_value = self._creations.pop(spell_id)
                disposable_entry = (
                    self._disposable_creations.pop(spell_id)
                    if isinstance(disposable_value, (tuple, HolderDisposalEntry))
                    else None
                )
                entry = {
                    "scope": "unique",
                    "disposable": disposable_entry is not None,
                    "stored": stored_value,
                }
                if isinstance(disposable_entry, HolderDisposalEntry):
                    entry["disposal_methods"] = disposable_entry.methods
                    entry["children"] = [
                        {"stored": child, "disposal_methods": methods}
                        for child, methods in disposable_entry.children
                    ]
                elif disposable_entry is not None:
                    entry["disposal_methods"] = disposable_entry[1]
                extracted.append(entry)
''',
    ),
    (
        '''            - Retains the extracted disposal lists directly, without copying
              their contents or reapplying binding policy.

        Returns:
            None.
        """
        if not creations:
            return
''',
        '''            - Retains the extracted disposal lists directly, without copying
              their contents or reapplying binding policy.
            - A unique row with `children` rebuilds the holder's
              `HolderDisposalEntry` (0.2.8238); rows without it restore exactly
              as before.

        Returns:
            None.
        """
        if not creations:
            return
''',
    ),
    (
        '''                    self._creations[spell_id] = stored_value
                    if is_disposable:
                        self._disposable_creations[spell_id] = (
                            stored_value,
                            disposal_methods if disposal_methods is not None else [],
                        )
                    continue
''',
        '''                    self._creations[spell_id] = stored_value
                    children = entry.get("children")
                    if children is not None:
                        self._disposable_creations[spell_id] = HolderDisposalEntry(
                            stored_value,
                            disposal_methods if disposal_methods is not None else [],
                            [(child["stored"], child["disposal_methods"]) for child in children],
                        )
                    elif is_disposable:
                        self._disposable_creations[spell_id] = (
                            stored_value,
                            disposal_methods if disposal_methods is not None else [],
                        )
                    continue
''',
    ),
]

lowering_edits = [
    (
        '''          `unique_per_spell_space`, the lineage root's, the cluster leader's - so
          a holder's `many` children belong to whatever owns the holder and are
          disposed with that store, never by a narrower scope that happened to
          meld the holder first. Until 0.2.8235 a miss registered them in the
          innermost scope, whose end disposed a child its holder still used.
''',
        '''          `unique_per_spell_space`, the lineage root's, the cluster's team
          store (0.2.8237) - so a holder's `many` children belong to whatever
          owns the holder and are disposed with that store, never by a narrower
          scope that happened to meld the holder first. Until 0.2.8235 a miss
          registered them in the innermost scope, whose end disposed a child
          its holder still used.
        - Child adoption (slotted_lifetime_ownership, 0.2.8238): right after a
          miss publishes its site, still under the site's build lock, it calls
          `c{i}.adopt_children(sid{i}, v{i}, ((sidN, vN), ...))` for exactly
          the children it registered, which moves them from their spells'
          `many` buckets into the holder's disposal record. Purge, an ownership
          transfer's move and disposal of the holder then take them with it. A
          lost cold race, a pinned-override refusal or a raising holder
          constructor never reaches the call: those children stay in their
          bucket and are disposed with the store. Only misses with
          disposal-bearing children gain the line; every `_site_plan_executor`
          body is unchanged.
''',
    ),
    (
        '''            miss therefore needs no innermost-scope prologue. A losing thread in
            a cold race has registered its children there too, and they stay
            until that store is disposed.
        """
''',
        '''            miss therefore needs no innermost-scope prologue. A losing thread in
            a cold race has registered its children there too, and they stay
            until that store is disposed.
            Adoption (0.2.8238): after publication, inside the guard and the
            miss branch, `c{index}.adopt_children(...)` hands exactly those
            registered children to the holder's disposal record (see the class
            contract); a miss without disposal-bearing children emits no call.
        """
''',
    ),
    (
        '''        else:
            inner.append(f"{inner_indent}{store}._creations[{sid_name}] = v{index}")
        parameters = ", ".join(list(self._context_params) + [store] + self._miss_arguments(index))
''',
        '''        else:
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
''',
    ),
]

print("creations", edit_tool.apply(CREATIONS, creations_edits))
print("lowering", edit_tool.apply(LOWERING, lowering_edits))
