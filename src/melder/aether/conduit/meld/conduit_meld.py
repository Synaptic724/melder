from typing import TYPE_CHECKING, Optional, Dict, Any, Callable, ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.conduit.meld.meld import Meld
from melder.aether.spellbook.existence.existence import Existence

if TYPE_CHECKING:
    from melder.aether.conduit.creations.conduit_creations import ConduitCreations
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.spell import Spell


class ConduitMeld(Meld):
    """
    Concrete conduit-facing meld front door.

    Purpose:
        Own the conduit-caller runtime storage surface while reusing the shared
        lookup, validation, and compiler logic in the abstract `Meld` base.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = [
        "_creations",
    ]

    def __init__(
            self,
            *,
            creations: "ConduitCreations",
            spellbook: "Spellbook",
            conduit_id: Optional[str] = None,
            resolution_conduit_id: Optional[str] = None,
            dynamic_environment: bool = False,
            meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = None,
    ) -> None:
        """
        Initialize one conduit-facing meld front door.
        """
        super().__init__(
            spellbook=spellbook,
            conduit_id=conduit_id,
            resolution_conduit_id=resolution_conduit_id,
            dynamic_environment=dynamic_environment,
            meld_hooks=meld_hooks,
        )
        self._creations = creations

    def cleanup(self) -> None:
        """
        Release conduit-facing creations state after shared Meld cleanup.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            super().cleanup()
            del self._creations

    def meld(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Optional[Any]:
        """
        Entry point for resolving and activating a spell (component) within this Conduit.

        This method orchestrates the full lifecycle: resolution, reuse, instantiation,
        hook execution, and registration.

        Args:
            spell_name (str):
                spell_name of the spell to meld

                When provided without an explicit spell or spellframe, this is
                treated as the **logical name key** used by the resolution pipeline.
                In other words, meld(spell_name=\"MyService\") becomes equivalent
                to a name-based lookup driven by the Spellbook / SpellIndex mappings.
            spell (str | object | None):
                The primary spell identifier.
                - If a **string**, treated as the unique `spell_id` (typically the
                  SHA256 structural fingerprint for the SpellIndex).
                - If an **object** (e.g., a class or function), used together with
                  `spellframe` and `binding_name` to form the DI identity key via the
                  `SpellInputUtils` normalization helpers.
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
        if isinstance(spell, str):
            target_spell = self._resolve_spell_by_id(spell)
        else:
            input_resolution_cache = self._input_resolution_cache
            cache_key = (spell_name, spell, spellframe, binding_name)
            try:
                cached_spell_id = input_resolution_cache.get(cache_key)
            except TypeError:
                cache_key = (
                    spell_name,
                    id(spell),
                    id(spellframe),
                    binding_name,
                )
                cached_spell_id = input_resolution_cache.get(cache_key)
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
                if len(input_resolution_cache) >= self._max_resolution_cache_size:
                    input_resolution_cache.pop(
                        next(iter(input_resolution_cache)),
                        None,
                    )
                input_resolution_cache[cache_key] = target_spell.spell_id
            if target_spell.requires_spellspace_request:
                raise RuntimeError(
                    f"Spell {target_spell.spell_id} must be built from a spellspace."
                )
        # 2) Normalize per-call overrides into a stable dict shape.
        if spell_override is None:
            override_map = None
        else:
            override_map = self._normalize_spell_override(spell_override)

        # 3) SpellSystemState / SpellValidity gate + lazy revalidation.
        if self._spellbook._spellbook_validation_required:
            self._ensure_lineage_resolvable(target_spell)
        if target_spell.resolution_required:
            self._ensure_runtime_resolution_ready(target_spell)

        creations = self._creations
        meld_hooks = self._meld_hooks
        spell_hooks_enabled = target_spell._hooks_enabled

        if not (meld_hooks or spell_hooks_enabled):
            if target_spell._creation_context_switch.state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = target_spell._get_or_build_creation_context()
            if creation_context is None:
                raise RuntimeError("Spell returned no live CreationContext.")
            if override_map is None:
                execute_no_hooks_no_overrides_compiled = (
                    creation_context._execute_no_hooks_no_overrides_compiled
                )
                instance = execute_no_hooks_no_overrides_compiled(creations)
            else:
                execute_no_hooks_overrides_compiled = (
                    creation_context._execute_no_hooks_overrides_compiled
                )
                instance = execute_no_hooks_overrides_compiled(
                    creations,
                    override_map,
                )

            # 7) Return the resolved instance.
            return instance
        else:
            # 1) Execute pre-cast hooks (no instance context yet).
            self._execute_hooks(target_spell._pre_hooks, "pre_cast")
            self._fire_meld_hooks("on_meld_pre_resolve", target_spell)

            if target_spell._creation_context_switch.state >= 2:
                creation_context = target_spell._creation_context
            else:
                creation_context = target_spell._get_or_build_creation_context()
            if creation_context is None:
                raise RuntimeError("Spell returned no live CreationContext.")
            if override_map is None:
                execute_hooks_no_overrides_compiled = (
                    creation_context._execute_hooks_no_overrides_compiled
                )
                instance, created = execute_hooks_no_overrides_compiled(
                    creations
                )
            else:
                execute_hooks_overrides_compiled = (
                    creation_context._execute_hooks_overrides_compiled
                )
                instance, created = execute_hooks_overrides_compiled(
                    creations,
                    override_map,
                )

            if created:
                # Activation hooks fire only when the instance is newly created.
                self._execute_activation_hooks(target_spell._activation_hooks, instance)
                self._fire_meld_hooks("on_meld_activation", target_spell, instance)

            # 2) Execute post-cast hooks (still no arguments for now).
            self._execute_hooks(target_spell._post_hooks, "post_cast")
            self._fire_meld_hooks("on_meld_post_resolve", target_spell)

            # 3) Return the resolved instance.
            return instance
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
                cache_key = (
                    spell_name,
                    id(spell),
                    id(spellframe),
                    binding_name,
                )
                cached_spell_id = input_resolution_cache.get(cache_key)
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
        caller_creations = self._creations

        if existence is Existence.many:
            raise RuntimeError(
                "meld_existing_spell is not supported for Existence.many."
            )

        if existence is Existence.unique_per_conduit:
            creation = caller_creations.get_creation(spell_id)
            if creation is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            return creation

        if existence is Existence.unique_per_spell_space:
            spellspace = caller_creations.get_active_spellspace()
            if spellspace is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            creation = caller_creations.get_spellspace_creation(
                spellspace.id,
                spell_id,
            )
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
            owner_creations = target_spell._owner_creations
            if owner_creations is None:
                raise ValueError(
                    "Spell '{0}' is not live.".format(spell_id)
                )
            creation = owner_creations.get_creation(spell_id)
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
        target_spell = self._resolve_spell_for_live_creation_probe(
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
        )
        return self._describe_spell_live_creation_status(target_spell)
