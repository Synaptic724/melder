from typing import TYPE_CHECKING, Optional, Dict, Any, Callable, ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.existence.existence import Existence

if TYPE_CHECKING:
    from melder.aether.conduit.creations.conduit_creations import ConduitCreations
    from melder.aether.conduit.creations.creations import Creations
    from melder.aether.conduit.creations.cluster_creations import ClusterCreations
    from melder.aether.conduit.spell_space.spell_space import SpellSpace
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook


class SpellSpaceMeld(Meld):
    """
    Concrete spellspace-facing meld front door.

    Purpose:
        Own the spellspace-specific entry semantics and route
        `unique_per_spell_space` work onto spellspace-owned storage directly.

    Contract:
        - Holds the owning spellspace object directly.
        - Holds both spellspace-owned creations and owner-conduit creations.
        - Leaves shared lookup, validation, and compiler logic on abstract
          `Meld`.
        - Routes `unique_per_spell_space` work into spellspace-local storage.
        - Routes conduit-owned or broader-lived existences through owner
          conduit or spell-owned shared storage as appropriate.

    Owned State:
        Only the spellspace object and two cached ids (`_spellspace`,
        `_spellspace_id`, `_owner_conduit_id`). Every creation store, including
        the spellspace scope store, is constructed and cleaned on the base
        `Meld`.

    Threading:
        Inherits the base door's concurrency posture, including the
        epoch-guarded fast-door registry.

    Lifecycle / Cleanup:
        Bound to one `SpellSpace`; it becomes unusable when that spellspace is
        reset or cleaned. Its stores are torn down by the base.

    Registration:
        MELDER KERNEL - guarded. Constructed by the owning `SpellSpace`; never
        user-instantiated and never bindable.

    Subsystem Context:
        The second of the two concrete doors over abstract `Meld`, paired with
        `ConduitMeld`. This is the ONLY door that can serve
        `unique_per_spell_space`, which is exactly why `ConduitMeld` refuses
        those spells instead of improvising a scope.

    System Context:
        This door exists because spellspace scope is the one Melder lifetime
        that is narrower than a conduit and is entered and exited explicitly.
        It holds BOTH the spellspace-local store and a reference to the owner
        conduit's store, and that dual grip is the point: a request-scoped
        instance must die with the spellspace, while a `unique_per_conduit`
        dependency resolved during that same request must NOT - it belongs to
        the conduit and has to outlive the request that happened to construct
        it. Routing every existence through one store would collapse that
        distinction and turn conduit-lived services into per-request garbage.
        Scope is enforced upstream too: `SpellSpace` may only meld while it is
        the ACTIVE spellspace for its conduit, and `reset()` clears
        spellspace-scoped instances and bumps the version rather than reusing
        stale ones.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    # The shared stores (`_conduit_creations` / `_root_creations` /
    # `_cluster_creations`) and the spellspace scope store
    # (`_spellspace_creations`) live on the base `Meld`. This door adds only the
    # spellspace object and the cached ids.
    __slots__ = [
        "_spellspace",
        "_spellspace_id",
        "_owner_conduit_id",
    ]

    def __init__(
            self,
            *,
            spellspace: "SpellSpace",
            spellspace_creations: "Creations",
            conduit_creations: "ConduitCreations",
            root_creations: "ConduitCreations",
            cluster_creations: "ClusterCreations",
            spellbook: "Spellbook",
            conduit_id: Optional[str] = None,
            resolution_conduit_id: Optional[str] = None,
            dynamic_environment: bool = False,
            meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = None,
    ) -> None:
        """
        Initialize one spellspace-facing meld front door.

        Purpose:
            Bind one explicit request-local spellspace surface onto the shared
            meld runtime core without exposing conduit spellspace-stack logic to
            callers that already hold the spellspace object directly.

        Contract:
            - Captures both the spellspace-local creations registry and the
              owner-conduit creations registry.
            - Captures the owner conduit's lineage-root store so
              `unique_per_conduit_lineage` melds resolved from inside the
              spellspace land in the owner conduit's lineage root (a spellspace
              is not a lineage root itself); the door is handed this store at
              runtime.
            - References the owner conduit's cluster facade (owned by the
              conduit meld, not by this spellspace) so
              `unique_per_conduit_cluster` melds resolved from inside the
              spellspace resolve into the same elected-leader store the owner
              conduit's cluster elected; a spellspace created after election
              still sees the filled facade through this shared reference.
            - Caches the owning spellspace id and owner conduit id for later
              live-creation diagnostics.
            - Reuses the shared spellbook/lookup surfaces owned by `Meld`.
        """
        super().__init__(
            spellbook=spellbook,
            conduit_id=conduit_id,
            resolution_conduit_id=resolution_conduit_id,
            dynamic_environment=dynamic_environment,
            meld_hooks=meld_hooks,
            conduit_creations=conduit_creations,
            root_creations=root_creations,
            cluster_creations=cluster_creations,
            spellspace_creations=spellspace_creations,
        )
        self._spellspace = spellspace
        self._spellspace_id = spellspace.id
        self._owner_conduit_id = spellspace.owner_conduit_id

    def cleanup(self) -> None:
        """
        Release spellspace-facing state.

        The shared stores and the spellspace scope store live on the base
        `Meld`, which drops them under its own lock; this door only releases the
        spellspace object and the cached ids it added.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            super().cleanup()
            del self._spellspace
            del self._spellspace_id
            del self._owner_conduit_id

    def meld(
            self,
            spell: str | object | None = None,
            *,
            spell_name: str | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Optional[Any]:
        """
        Entry point for resolving and activating a spell (component) within this Conduit.

        This method orchestrates the full lifecycle: resolution, reuse, instantiation,
        hook execution, and registration.

        Call shape:
            `spell` is the only positional parameter, so the dominant warm
            pattern is the cheapest possible call: `meld(spell_id)` passes
            one positional argument with no keyword marshaling and routes
            straight into the id-string fast lane below. All other entry
            modes are keyword-only.

        Args:
            spell (str | object | None):
                The primary spell identifier (first positional parameter).
                - If a **string**, treated as the unique `spell_id` (typically the
                  SHA256 structural fingerprint for the SpellIndex).
                - If an **object** (e.g., a class or function), used together with
                  `spellframe` and `binding_name` to form the DI identity key via the
                  `SpellInputUtils` normalization helpers.
            spell_name (str):
                spell_name of the spell to meld (keyword-only).

                When provided without an explicit spell or spellframe, this is
                treated as the **logical name key** used by the resolution pipeline.
                In other words, meld(spell_name=\"MyService\") becomes equivalent
                to a name-based lookup driven by the Spellbook / SpellIndex mappings.
            spellframe (str | object | None):
                Optional Spellframe / Protocol / class used as the primary DI identity.
                Often redundant if `spell` is the class/protocol itself. Spellframes
                act as grouping keys (interfaces, protocol frames, string categories)
                under which multiple spells may be bound.
            binding_name (str | None):
                Optional binding name, used alongside `spell` or `spellframe` to create
                a unique lookup key within a given frame. If omitted, the default
                binding (e.g. `"__default__"`) is used internally.
            spell_override (dict | list | tuple | None):
                Optional override payload attached to the meld call. This payload
                represents **per-call overrides** (constructor arguments, factory
                inputs, etc.) and is normalized into a dictionary by
                :meth:`_normalize_spell_override`.
                The payload is rejected when the resolved spell disables
                override-capable runtime posture.

        Returns:
            Optional[Any]:
                The resolved component instance (either reused or newly created)
                after all pre-/activation-/post-hooks have executed.

        Contract:
            - Routes `unique_per_spell_space` through the spellspace-local
              creations registry owned by this request object.
            - Routes `unique_per_conduit` and `many` through the injected
              owner-conduit creations registry.
            - Routes broader-lived existences through spell-owned shared
              `owner_creations`.
            - Does not depend on the conduit's active spellspace stack once the
              caller already holds this explicit spellspace front door.
            - Warm id-string melds may take the guarded fast meld door: after
              one successful normal-lane meld in non-dynamic, no-hooks,
              no-override posture, later identical requests execute through a
              memoized `(spell, context, epoch)` entry validated per call
              by live guards (hook state, context-switch state, context
              identity, validation/resolution flags), with the executor read
              per hit through the live context slot so phase-11 hot-swapped
              doors are always honored. Any guard miss falls back to this
              normal lane and rebuilds the entry on success, so fast-lane
              results are always identical to normal-lane results.

        Raises:
            ValueError:
                If none of `spell_name`, `spell`, or `spellframe` are provided.
            KeyError:
                If the spell cannot be resolved by the provided inputs.
            NotImplementedError:
                If the spell type (e.g., class-based DI) or existence mode is not
                yet supported for construction/registration.
            HookExecutionError:
                If a pre-cast, activation, or post-cast hook fails.
            RuntimeError:
                For unexpected internal state issues (e.g., missing object after
                ID resolution, unsupported Creations manager, attempting to
                meld a broken spell, or passing `spell_override` to a spell
                that has overrides disabled).
        """
        # 1) Resolve the spell object from the Spellbook / SpellIndex.
        target_spell: Optional[Spell] = None
        fast_door_key: Optional[str] = None
        if isinstance(spell, str):
            if spell_override is None:
                # Fast meld door: success-only memoized warm lane for id-string
                # melds. Every guard below is a live read of state maintained by
                # existing invalidation chokepoints, so a hit has zero staleness
                # window; any failed guard falls through to the normal lane,
                # which rebuilds the entry in place after it succeeds.
                fast_entry = self._fast_meld_doors.get(spell)
                if fast_entry is not None:
                    (
                        door_spell,
                        captured_context,
                        captured_epoch,
                    ) = fast_entry
                    fast_executor = None
                    try:
                        # Guard ladder (live reads only):
                        # - meld-hooks map read live because it is shared by
                        #   reference and may be mutated in place
                        # - the door epoch replaces the old per-flag reads
                        #   (hook gate, switch fast_state, resolution flag):
                        #   every spell-level invalidation chokepoint bumps
                        #   `Spell._door_epoch`, so one int compare covers
                        #   them with one shared-object hop instead of three
                        # - context identity covers context replacement (all
                        #   replacement funnels through
                        #   Spell._cleanup_creation_context, which also bumps)
                        # - the spellbook-wide validation flag stays a live
                        #   read: it is not a per-spell chokepoint
                        if (
                            not self._meld_hooks
                            and door_spell._door_epoch == captured_epoch
                            and door_spell._creation_context is captured_context
                            and not self._spellbook._spellbook_validation_required
                        ):
                            # The executor slot is read through the live
                            # context PER HIT, never captured in the entry:
                            # phase-11 hydration hot-swaps this slot in place
                            # on first execution (cold door -> hot door), and
                            # a captured reference would pin the cold-door
                            # wrapper forever.
                            fast_executor = (
                                captured_context._no_overrides_instance_executor
                            )
                    except AttributeError:
                        # Lifecycle-ambiguous read: a cleaned spell/switch/
                        # context has deleted slots. Treat as a guard miss so
                        # the normal lane produces the canonical error or
                        # rebuilds.
                        fast_executor = None
                    if fast_executor is not None:
                        # Instance-only door: no (instance, created)
                        # tuple on the warm fast lane.
                        instance = fast_executor(self)
                        if self._spellbook._cache_emit_required:
                            self._spellbook._emit_cache_file_if_required()
                        return instance
            fast_door_key = spell
            # Hot path: inline the dominant spell-id-pool hit so warm id-string
            # melds resolve with one dict read instead of one helper frame.
            target_spell = self._spell_id_pool.get(spell)
            if target_spell is None:
                target_spell = self._resolve_spell_by_id(spell)
        else:
            input_resolution_cache = self._input_resolution_cache
            cache_key = (spell_name, spell, spellframe, binding_name)
            try:
                cached_spell_id = input_resolution_cache.get(cache_key)
            except TypeError:
                # Unhashable spell/spellframe input: SKIP the cache entirely
                # (id-reuse aliasing fix, 2026-07-12). Raw id() keys outlive
                # their objects - address reuse could serve a dead entry's
                # resolution to a different object. Resolve uncached.
                cache_key = None
                cached_spell_id = None
            if cached_spell_id is not None:
                target_spell = self._spell_id_pool.get(cached_spell_id)
                if target_spell is None:
                    try:
                        target_spell = self._resolve_spell_by_id(cached_spell_id)
                    except KeyError:
                        target_spell = None
            if target_spell is None:
                target_spell = self._resolve_spell(
                    spell=spell,
                    spell_name=spell_name,
                    spellframe=spellframe,
                    binding_name=binding_name,
                )
                if cache_key is not None:
                    if len(input_resolution_cache) >= self._max_resolution_cache_size:
                        input_resolution_cache.pop(
                            next(iter(input_resolution_cache)),
                            None,
                        )
                    input_resolution_cache[cache_key] = target_spell.spell_id
        # 2) Caller overrides replace the stored mutation override payload.
        # Hot path: read the owned slot directly instead of paying the
        # `mutation_override` property descriptor per meld.
        if spell_override is None:
            override_map = target_spell._mutation_override
        else:
            override_map = self._normalize_spell_override(spell_override)

        # 3) SpellSystemState / SpellValidity gate + lazy revalidation.
        if self._spellbook._spellbook_validation_required:
            self._ensure_lineage_resolvable(target_spell)
        if target_spell.resolution_required:
            self._ensure_runtime_resolution_ready(target_spell)

        meld_hooks = self._meld_hooks
        spell_hooks_enabled = target_spell._hooks_enabled
        # Captured BEFORE execution: if any invalidation chokepoint bumps the
        # epoch while this meld is executing, the entry built below carries
        # the pre-bump value, so the next fast-door attempt misses and
        # rebuilds instead of trusting a stale posture.
        door_epoch_at_entry = target_spell._door_epoch
        if not (meld_hooks or spell_hooks_enabled):
            if target_spell._creation_context_switch.fast_state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = target_spell._get_or_build_creation_context()
            if creation_context is None:
                raise RuntimeError("Spell returned no live CreationContext.")
            # Hot path: in non-dynamic mode dispatch the phase-11 runtime door
            # directly so the no-hooks lane skips the `execute_no_hooks`
            # wrapper frame. The executor reference is read through the live
            # context on this normal-lane pass; the only place it is retained
            # is the guarded fast-door entry built below, whose per-call
            # context-identity guard prevents a recompiled/cleaned context
            # from ever serving a stale executor.
            if creation_context._dynamic_environment:
                instance = creation_context.execute_no_hooks(
                    self,
                    override_map,
                )
            elif override_map is None:
                instance = creation_context._no_overrides_instance_executor(
                    self,
                )
                if fast_door_key is not None:
                    # Success-only fast-door memoization. This arm is exactly
                    # the fast-lane posture (non-dynamic, no hooks, no
                    # override payload), and execution above just succeeded,
                    # so the entry is built from proven-live collaborators.
                    # The executor is deliberately NOT stored: phase-11
                    # hydration hot-swaps the context executor slots in place
                    # on first execution, so the fast lane re-reads the slot
                    # per hit through the captured context. Reaching here with
                    # an existing entry means a guard missed; the write below
                    # is the in-place rebuild.
                    self._fast_meld_doors[fast_door_key] = (
                        target_spell,
                        creation_context,
                        door_epoch_at_entry,
                    )
            else:
                instance = creation_context._overrides_executor(
                    self,
                    override_map,
                )[0]
            # Hot path: inline the staged-cache flag check; the emit helper is
            # only entered when an emit is actually pending.
            if self._spellbook._cache_emit_required:
                self._spellbook._emit_cache_file_if_required()

            # 7) Return the resolved instance.
            return instance
        else:
            # 1) Execute pre-cast hooks (no instance context yet).
            self._execute_hooks(target_spell._pre_hooks, "pre_cast")
            self._fire_meld_hooks("on_meld_pre_resolve", target_spell)

            if target_spell._creation_context_switch.fast_state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = target_spell._get_or_build_creation_context()
            if creation_context is None:
                raise RuntimeError("Spell returned no live CreationContext.")
            instance, created = creation_context.execute(
                self,
                override_map,
            )

            if created:
                # Activation hooks fire only when the instance is newly created.
                self._execute_activation_hooks(target_spell._activation_hooks, instance)
                self._fire_meld_hooks("on_meld_activation", target_spell, instance)

            # 2) Execute post-cast hooks (still no arguments for now).
            self._execute_hooks(target_spell._post_hooks, "post_cast")
            self._fire_meld_hooks("on_meld_post_resolve", target_spell)
            if self._spellbook._cache_emit_required:
                self._spellbook._emit_cache_file_if_required()

            # 3) Return the resolved instance.
            return instance

    # Note: a dedicated `meld_id(spell_id, /)` fast entry briefly existed on
    # this door. It was removed in favor of the single `meld(...)` API:
    # `spell` rides the positional seat, so `meld(spell_id)` is the supported
    # minimal-arity warm call shape and reaches the same fast lane above.

    def meld_existing_spell(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> Any:
        """
        Return an already-live object for one resolved spell or fail.

        Purpose:
            Provide a cold-path reuse-only runtime operation that resolves
            spell identity the same way `meld(...)` does but never creates.

        Contract:
            - Reuses the same spell identity inputs accepted by `meld(...)`.
            - Never enters any creation path.
            - Returns one already-live object or raises.
            - Supports only lifecycles that can resolve to one deterministic
              existing object.
            - Reads spellspace-local storage for `unique_per_spell_space`.
            - Reads owner-conduit storage for conduit-owned existences.
            - Reads spell-owned shared `owner_creations` for broader-lived
              existences.

        Args:
            spell_name:
                Optional logical spell name for name-based resolution.
            spell:
                Optional spell id string or spell object used for resolution.
            spellframe:
                Optional spellframe / protocol / frame key used for
                resolution.
            binding_name:
                Optional binding name used for lookup-key resolution.

        Returns:
            Any: Existing live runtime object for the resolved spell.

        Raises:
            ValueError:
                If the spell is not currently live.
            RuntimeError:
                If the spell lifecycle does not support unambiguous
                existing-object retrieval.
        """
        target_spell: Optional[Spell] = None
        if isinstance(spell, str):
            target_spell = self._resolve_spell_by_id(spell)
        else:
            input_resolution_cache = self._input_resolution_cache
            cache_key = (spell_name, spell, spellframe, binding_name)
            try:
                cached_spell_id = input_resolution_cache.get(cache_key)
            except TypeError:
                # Unhashable spell/spellframe input: SKIP the cache entirely
                # (id-reuse aliasing fix, 2026-07-12). Raw id() keys outlive
                # their objects - address reuse could serve a dead entry's
                # resolution to a different object. Resolve uncached.
                cache_key = None
                cached_spell_id = None
            if cached_spell_id is not None:
                target_spell = self._spell_id_pool.get(cached_spell_id)
                if target_spell is None:
                    try:
                        target_spell = self._resolve_spell_by_id(cached_spell_id)
                    except KeyError:
                        target_spell = None
            if target_spell is None:
                target_spell = self._resolve_spell(
                    spell=spell,
                    spell_name=spell_name,
                    spellframe=spellframe,
                    binding_name=binding_name,
                )
                if cache_key is not None:
                    if len(input_resolution_cache) >= self._max_resolution_cache_size:
                        input_resolution_cache.pop(
                            next(iter(input_resolution_cache)),
                            None,
                        )
                    input_resolution_cache[cache_key] = target_spell.spell_id

        if target_spell.is_existing_creation:
            if target_spell.user_created_object is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(target_spell.spell_id)
                )
            return target_spell.user_created_object

        existence = target_spell.existence
        spell_id = target_spell.spell_id
        if existence is Existence.many:
            raise RuntimeError(
                "meld_existing_spell is not supported for Existence.many."
            )

        if existence is Existence.unique_per_conduit:
            creation = self._conduit_creations.get_creation(spell_id)
            if creation is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            return creation

        if existence is Existence.unique_per_spell_space:
            creation = self._spellspace_creations.get_creation(spell_id)
            if creation is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            return creation

        if existence in {
            Existence.unique,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
        }:
            # Only `unique` resolves into the binding owner's _owner_creations.
            # cluster/lineage live in the meld-supplied store (elected leader /
            # lineage-root), mirroring the front-door store selection.
            if existence is Existence.unique:
                store = target_spell._owner_creations
            elif existence is Existence.unique_per_conduit_lineage:
                store = self._root_creations
            else:  # unique_per_conduit_cluster
                store = (
                    self._cluster_creations.resolved_store()
                    if (
                        self._cluster_creations is not None
                        and self._cluster_creations.is_active()
                    )
                    else None
                )
            if store is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            creation = store.get_creation(spell_id)
            if creation is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            return creation

        raise RuntimeError(
            "meld_existing_spell is unsupported for existence '{0}'.".format(
                existence.name
            )
        )

    def describe_live_creation_status(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> Dict[str, object]:
        """
        Return structured live-creation status for one resolved spell.

        Purpose:
            Provide a richer no-create status payload over the same lookup path
            used by `has_live_creation(...)` and `meld(...)`.

        Contract:
            - Uses the same root identity inputs as `meld(...)`.
            - Reuses the same spell-resolution helpers used by the meld path.
            - Inspects current live runtime storage only.
            - Never creates, registers, or mutates runtime objects.
            - Reports the query conduit context explicitly so callers know the
              result is scoped to the current conduit and, where relevant, its
              active spellspace or shared owner-creation path.
            - Answers from spellspace-local, owner-conduit, or shared-owner
              storage according to the resolved spell's existence semantics.

        Args:
            spell_name:
                Optional logical spell name for name-based resolution.
            spell:
                Optional spell id string or spell object used for resolution.
            spellframe:
                Optional spellframe / protocol / frame key used for
                resolution.
            binding_name:
                Optional binding name used for lookup-key resolution.

        Returns:
            Dict[str, object]: Structured live-creation status payload.

        Raises:
            ValueError:
                If none of `spell_name`, `spell`, or `spellframe` are
                provided.
            KeyError:
                If the spell cannot be resolved by the provided inputs.
            RuntimeError:
                If the probe encounters an unsupported or inconsistent runtime
                storage state.
        """
        target_spell = self._resolve_spell(
            spell=spell,
            spell_name=spell_name,
            spellframe=spellframe,
            binding_name=binding_name,
        )
        return self._describe_spell_live_creation_status(target_spell)


    def _describe_spell_live_creation_status(self, spell: Spell) -> Dict[str, object]:
        """
        Return structured live-creation status for one resolved spell.

        Purpose:
            Interpret the resolved spell's existence semantics against the
            current runtime storage state without creating anything.

        Contract:
            - `unique_per_spell_space` reads from spellspace-local storage.
            - `unique_per_conduit` and `many` read from owner-conduit storage.
            - broader shared existences read from spell-owned
              `owner_creations`.
            - Reports both `query_conduit_id` and `active_spellspace_id` so the
              caller can distinguish request-local versus broader scope state.

        Args:
            spell:
                Resolved spell object whose live creation state should be
                checked.

        Returns:
            Dict[str, object]: Structured status payload for the resolved
            spell.

        Raises:
            RuntimeError:
                If the spell advertises an unsupported or inconsistent
                existence/storage relationship.
        """
        query_conduit_id = self._conduit_id
        if spell.is_existing_creation:
            return {
                "is_live": spell.user_created_object is not None,
                "spell_id": spell.spell_id,
                "spell_name": spell.spell_name,
                "existence": spell.existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": "existing_creation",
                "storage_owner_conduit_id": None,
                "active_spellspace_id": None,
                "creation_count": 1 if spell.user_created_object is not None else 0,
            }

        existence = spell.existence
        spell_id = spell.spell_id
        if existence is Existence.many:
            creation_bucket = self._conduit_creations.get_creation(spell_id)
            creation_count = (
                len(creation_bucket)
                if isinstance(creation_bucket, list)
                else 0
            )
            return {
                "is_live": creation_count > 0,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": "owner_conduit_many",
                "storage_owner_conduit_id": self._owner_conduit_id,
                "active_spellspace_id": None,
                "creation_count": creation_count,
            }

        if existence is Existence.unique_per_conduit:
            creation = self._conduit_creations.get_creation(spell_id)
            return {
                "is_live": creation is not None,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": "owner_conduit",
                "storage_owner_conduit_id": self._owner_conduit_id,
                "active_spellspace_id": self._spellspace_id,
                "creation_count": 1 if creation is not None else 0,
            }

        if existence is Existence.unique_per_spell_space:
            creation = self._spellspace_creations.get_creation(spell_id)
            return {
                "is_live": creation is not None,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": "spellspace",
                "storage_owner_conduit_id": self._owner_conduit_id,
                "active_spellspace_id": self._spellspace_id,
                "creation_count": 1 if creation is not None else 0,
            }

        if existence in {
            Existence.unique,
            Existence.unique_per_conduit_cluster,
            Existence.unique_per_conduit_lineage,
        }:
            # Only `unique` lives in the binding owner's _owner_creations.
            # cluster/lineage live in the meld-supplied store (elected leader /
            # lineage-root); a cluster with no elected leader is simply not live.
            if existence is Existence.unique:
                store = spell._owner_creations
                storage_scope_kind = "owner_creations"
                storage_owner_conduit_id = spell._owner_conduit_id
            elif existence is Existence.unique_per_conduit_lineage:
                store = self._root_creations
                storage_scope_kind = "lineage_root"
                storage_owner_conduit_id = None
            else:  # unique_per_conduit_cluster
                store = (
                    self._cluster_creations.resolved_store()
                    if (
                        self._cluster_creations is not None
                        and self._cluster_creations.is_active()
                    )
                    else None
                )
                storage_scope_kind = "cluster_leader"
                storage_owner_conduit_id = None
            creation = (
                store.get_creation(spell_id) if store is not None else None
            )
            return {
                "is_live": creation is not None,
                "spell_id": spell_id,
                "spell_name": spell.spell_name,
                "existence": existence.name,
                "query_conduit_id": query_conduit_id,
                "storage_scope_kind": storage_scope_kind,
                "storage_owner_conduit_id": storage_owner_conduit_id,
                "active_spellspace_id": None,
                "creation_count": 1 if creation is not None else 0,
            }

        raise RuntimeError(
            "Unsupported existence '{0}' for live creation probe.".format(
                existence,
            )
        )
