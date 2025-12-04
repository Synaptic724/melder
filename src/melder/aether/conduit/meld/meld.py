from threading import RLock
from typing import Optional, Dict, Any, Callable, List

from melder.aether.conduit.meld.meld_context.meld_context import MeldContext
from melder.aether.conduit.meld.meld_runtime.meld_runtime import MeldRuntime
from melder.utilities.general_base.cleanable import Cleanable
# Melder Imports
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces.interfaces import (
    ISpellbook,
    ISpell,
    IMeld,
    ILesserCreations,
    ICreations, ISpellIndex,
)
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.spellbook.existence.existence import Existence

# Creations types
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError


class Meld(Cleanable):
    """
    ## 🪄 Meld: Spell Activation and Dependency Resolution

    Meld is the **conduit-level entry point** for *activating* spells (components/dependencies)
    within a specific `Conduit`. It handles the full lifecycle of spell resolution,
    creation reuse, hook execution, and registration.

    It implements the core dependency injection logic, mediating between the
    `Spellbook` (which defines the components) and the `Creations` manager (which
    holds the instantiated objects/components).

    The primary method is `meld()`.

    ### High-Level Activation Flow

    The `meld()` process follows these steps:

    1.  **Resolve Spell:** Identifies the target `ISpell` object using its ID or a
        `(spellframe, binding_name)` lookup key.
    2.  **Apply Overrides:** Attaches any per-call `spell_override` metadata to the Spell.
    3.  **Execute Pre-Cast Hooks:** Runs hooks that execute *before* instance resolution.
    4.  **Attempt Reuse:** Checks the `Creations` manager for an existing instance
        based on the Spell's `Existence` (e.g., `unique`, `unique_per_conduit`).
    5.  **Instantiate/Register (if needed):**
        * If no instance is found, dispatches to a spell-type specific path (e.g.,
            for `EXISTING_CREATION` spells) to obtain a new instance.
        * Registers the new instance with the `Creations` manager based on its
            `Existence` mode.
    6.  **Execute Activation Hooks:** Runs hooks that operate on the newly resolved/reused
        instance, passing the instance as a context argument.
    7.  **Execute Post-Cast Hooks:** Runs hooks that execute *after* activation.
    8.  **Return Instance:** Returns the final, resolved instance.
    """

    def __init__(
            self,
            creations: ILesserCreations | ICreations,
            spellbook: ISpellbook
    ) -> None:
        """
        Initialize the Meld component with references to the component store,
        spellbook lookup maps, and the DAG-based meld runtime.

        Args:
            creations:
                The local component instance manager (either `Creations` for a
                full Conduit or `LesserCreations` for a LesserConduit).
            spellbook:
                The registry of all known spell configurations. Meld keeps
                direct references to the internal `ConcurrentDict` instances
                to perform fast, thread-safe lookups.
        """
        super().__init__()

        self._lock = RLock()
        self._cleaned: bool = False

        # Spellbook references (used for resolution)
        self._owned_spells: Dict[ISpellIndex, ISpell] = spellbook._spells
        self._contracted_spells: Dict[str, Dict[ISpellIndex, ISpell]] = (
            spellbook._contracted_spells
        )

        self._lookup_owned_spells: Dict[tuple, ISpellIndex] = spellbook._lookup_spells
        self._lookup_contracted_spells: Dict[str, Dict[tuple, ISpellIndex]] = (
            spellbook._lookup_contracted_spells
        )

        # Conduit-local instantiation manager (Creations or LesserCreations)
        self._creations = creations

        # DAG-based runtime that will actually execute the DI graph for
        # factory-style spells (class / method / lambda).
        self._runtime: MeldRuntime = MeldRuntime()

        # Optional hook map pulled from Configuration (via Conduit).
        self._meld_hooks: Optional[Dict[str, list[Callable[..., Any]]]] = None


    def cleanup(self) -> None:
        """
        Cleanup the Meld instance to prevent further use and release references
        to spell configurations, creations manager, and the meld runtime.

        This should be called when the owning `Conduit` is being shut down.

        Behaviour:
            - Marks the instance as cleaned.
            - Clears references to spellbook maps and creations.
            - Cleans up and drops the internal `MeldRuntime` instance.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            # Clear spellbook references
            self._owned_spells = None
            self._contracted_spells = None
            self._lookup_owned_spells = None
            self._lookup_contracted_spells = None

            # Clear creations reference
            self._creations = None

            # Tear down the runtime if present
            if self._runtime is not None:
                try:
                    self._runtime.cleanup()
                except Exception:
                    # Runtime cleanup should never blow up conduit teardown.
                    pass
                self._runtime = None

            if self._meld_hooks is not None:
                self._meld_hooks.clear()
                self._meld_hooks = None


    # region Context Manager
    def __enter__(self):
        """
        Acquire the internal lock for thread-safe operations within a context.

        Returns:
            Meld: The instance itself.
        """
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Release the internal lock upon context manager exit.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_value: Exception value.
            traceback: Exception traceback.

        Returns:
            None.
        """
        self._lock.release()
    # endregion Context Manager
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

                When provided without an explicit ``spell`` or ``spellframe``, this is
                treated as the **logical name key** used by the resolution pipeline.
                In other words, ``meld(spell_name=\"MyService\")`` becomes equivalent
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

                Semantics:
                - `dict`  → treated as keyword-style overrides (param_name → value).
                - `list` / `tuple` → treated as positional overrides, stored under
                  a special internal key (e.g. `"__args__"`).

                This data is **not** written onto the Spell itself; it is intended
                to be consumed by the runtime / engine layer for this specific
                meld invocation.

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
                ID resolution, unsupported Creations manager, or attempting to
                meld a broken spell).
        """
        with self._lock:
            # Basic contract: we need at least *one* identity source.
            if spell is None and spellframe is None and spell_name is None:
                raise ValueError(
                    "[MELD] meld(...) requires at least one of "
                    "`spell_name`, `spell`, or `spellframe`."
                )

            # 1) Normalize per-call overrides into a stable dict shape.
            override_map = self._normalize_spell_override(spell_override)

            # 2) Resolve the spell object from the Spellbook / SpellIndex.
            target_spell = self._resolve_spell(
                spell=spell,
                spell_name=spell_name,
                spellframe=spellframe,
                binding_name=binding_name,
            )

            # 1.5) SpellSystemState / SpellValidity gate + lazy revalidation.
            self._ensure_lineage_resolvable(target_spell)

            # 3) Defensive guard: never attempt to meld a broken spell.
            if target_spell.is_broken:
                raise RuntimeError(
                    f"[MELD] Cannot meld broken spell: {target_spell}."
                )

            # 4) Respect SpellSystemState / SpellValidity gate (if DevOps is wired).
            self._gated_validation_required(target_spell)

            # 5) Execute pre-cast hooks (no instance context yet).
            self._execute_hooks(target_spell.pre_hooks, "pre_cast")

            # 6) Try to reuse an existing creation based on Existence + creations type.
            instance = self._get_existing_creation(target_spell)

            # 7) If no existing instance, construct a new one via the spell-type path
            #    and register it into the appropriate creations bucket.
            if instance is None:
                instance = self._meld_by_spell_type(target_spell, override_map)
                self._register_spell(target_spell, instance)
                # Activation hooks fire only when the instance is newly created.
                self._execute_activation_hooks(target_spell.activation_hooks, instance)

            # 8) Execute post-cast hooks (still no arguments for now).
            self._execute_hooks(target_spell.post_hooks, "post_cast")

            # 9) Return the resolved instance.
            return instance

    def _ensure_lineage_resolvable(self, spell: ISpell) -> None:
        """
        Internal

        Enforce SpellSystemState / SpellValidity gating **and** perform a
        single lazy revalidation for UNKNOWN / GATED lineages.

        Behaviour:

        - If there is no SpellSystemState:
            → no-op here; we rely on `spell.is_broken` later in `meld(...)`.

        - If validity is VALID:
            → no-op; allow meld to proceed.

        - If validity is UNKNOWN or GATED:
            → run the per-spell phases (1–4) via `spell.run_all_phases()`.
              Then:
                * if `spell.is_broken` → mark INVALID and raise
                  SpellbookValidationError.
                * else → if the lineage did not move to VALID, raise
                  SpellbookValidationError.

          After this call, the lineage should no longer be UNKNOWN/GATED. If it
          is, that is treated as a validation failure.

        - If validity is INVALID or DISABLED:
            → raise SpellbookValidationError immediately.
        """
        state = spell.system_state
        if state is None:
            # No DevOps gate wired; let existing `is_broken` guard handle it.
            return

        # Fast path / immediate failure for invalid/disabled etc.
        if not self._gated_validation_required(spell):
            return

        # At this point we know: state is not None and validity ∈ {unknown, gated}.
        spell.run_all_phases()

        # If the crafter thinks it's broken, we hard-pin to invalid and bail.
        if spell.is_broken:
            state.set_validity(SpellValidity.invalid)
            raise SpellbookValidationError([spell])

        # Re-read state in case your validation pipeline swapped the object
        # or mutated validity.
        refreshed_state = spell.system_state

        # One chance: after revalidation, the lineage must be VALID.
        if refreshed_state is None or refreshed_state.validity is not SpellValidity.valid:
            raise SpellbookValidationError([spell])


    def _gated_validation_required(self, spell: ISpell) -> bool:
        """
        Internal

        Decide whether this spell's lineage needs a **lazy revalidation**
        pass before we attempt to meld it.

        Semantics:

        - If no SpellSystemState is attached → False
          (DevOps / change-control not wired; Meld falls back to Spell flags).

        - SpellValidity.valid   → False  (safe to resolve as-is).
        - SpellValidity.unknown → True   (first-pass revalidation needed).
        - SpellValidity.gated   → True   (structural / contract / mutation gate).
        - SpellValidity.invalid / disabled → raise SpellbookValidationError.

        This method does **not** run validation; it only answers:
        “Should we try to revalidate this lineage now?”
        """
        state = spell.system_state
        if state is None:
            # No DevOps wiring; nothing for us to do at this layer.
            return False

        validity = state.validity

        if validity is SpellValidity.valid:
            return False

        if validity is SpellValidity.unknown or validity is SpellValidity.gated:
            return True

        # invalid / disabled → hard block, no attempt to resolve
        if validity is SpellValidity.invalid or validity is SpellValidity.disabled:
            raise SpellbookValidationError([spell])

        # Extremely defensive: any future enum value → treat as not resolvable.
        raise SpellbookValidationError([spell])



    def _normalize_spell_override(
            self,
            spell_override: Optional[dict | list | tuple]
    ) -> Optional[dict[str, Any]]:
        """
        Normalize the ``spell_override`` input into a consistent dictionary format.

        The **override payload** is intended to represent *per-call* constructor
        / factory overrides for a given meld operation. This helper converts the
        user-facing shapes into a uniform internal representation that can be
        consumed by the Meld runtime / engine layer.

        Supported input shapes
        ----------------------

        * ``None``:
            - No overrides are supplied; returns ``None``.

        * ``dict``:
            - Treated as keyword-style overrides:
              ``{"param_name": value, "other_param": other_value}``.
            - A shallow copy is created to avoid accidental mutation of the
              caller's dictionary.

        * ``list`` / ``tuple``:
            - Treated as **positional argument** overrides.
            - These are stored under the special key ``"__args__"`` so that the
              engine can distinguish them from keyword overrides:
              ``{"__args__": [arg0, arg1, ...]}``.

        Any more sophisticated interpretation (e.g. mixing positional and keyword
        semantics, or nested override structures) can be layered on later, but the
        MVP is deliberately simple and explicit.

        Args:
            spell_override:
                The raw override payload supplied by the caller. Must be one of:
                ``None``, ``dict``, ``list``, or ``tuple``.

        Returns:
            Optional[dict[str, Any]]:
                A normalized dictionary representation of the overrides, or
                ``None`` if no overrides were supplied.

        Raises:
            TypeError:
                If ``spell_override`` is not one of the supported shapes.
        """
        if spell_override is None:
            return None

        if isinstance(spell_override, dict):
            # Shallow copy to avoid side-effects if the caller mutates
            # their dictionary after passing it into meld(...).
            return dict(spell_override)

        if isinstance(spell_override, (list, tuple)):
            # MVP positional override support: caller is explicitly saying
            # "treat these as *args for the constructor/factory".
            return {"__args__": list(spell_override)}

        raise TypeError(
            "[MELD] spell_override must be a dict, list, or tuple."
        )



    # ----------------------------------------------------------------------
    # Resolution helpers
    # ----------------------------------------------------------------------

    def _create_meld_context(
            self,
            spell: ISpell,
            overrides: Optional[dict[str, Any]],
    ) -> MeldContext:
        """
        Internal

        Create a per-call :class:`MeldContext` for a single meld operation.

        The context binds together:
            - The root spell to be constructed.
            - The current Conduit’s creations manager.
            - Any normalized per-call overrides (constructor/factory args).

        This object is passed into the `MeldRuntime` / `MeldEngine` stack and
        is cleaned up immediately after the engine finishes.

        Args:
            spell:
                The root `ISpell` being melded.
            overrides:
                Normalized per-call overrides produced by
                :meth:`_normalize_spell_override`, or ``None`` if no overrides
                were supplied.

        Returns:
            MeldContext:
                A freshly constructed context for this meld invocation.
        """
        # Positional construction keeps us insulated from minor signature changes
        # in MeldContext as long as (root_spell, creations, overrides) stay first.
        return MeldContext(root_spell=spell, overrides=overrides)


    def _resolve_spell(
            self,
            *,
            spell: Any | None,
            spell_name: str | None,
            spellframe: Any | None,
            binding_name: str | None,
    ) -> ISpell:
        """
        Internal

        Resolve an ``ISpell`` using either:

        1. A direct ``spell_id`` string (SHA256 fingerprint), or
        2. A logical identity tuple derived from
           ``(spellframe | spell, binding_name)``.

        This is the main entry point used by ``meld()``; it delegates to
        more specific helpers for each resolution strategy.

        Args:
            spell:
                If a string, treated as the canonical ``spell_id``.
                Otherwise treated as a class/function/instance used when
                deriving the logical spell key.
            spell_name:
                Optional explicit spell name to use when deriving the
                logical identity key. Used only if ``spell`` is not a string.
            spellframe:
                Optional spellframe / Protocol / interface used as part of
                the DI identity. If ``None``, the spell’s own type/name is
                used by the normalization helper.
            binding_name:
                Optional binding name to discriminate multiple spells
                registered under the same spellframe.

        Returns:
            ISpell:
                The resolved spell configuration object.

        Raises:
            KeyError:
                If no spell can be resolved for the provided inputs.
            RuntimeError:
                If the Spellbook maps are internally inconsistent (e.g.
                a lookup key resolves to a SpellIndex that has no
                corresponding spell object).
        """
        # 1) string spell → treated as spell_id (SHA)
        if isinstance(spell, str):
            return self._resolve_spell_by_id(spell)

        # 2) Everything else → (frame_key, binding_key) path

        # Decide what we use as "spell" for name-based resolution:
        # - if we have a concrete spell object (class/function), use that
        # - else if we have a spell_name string, use that
        # - else spell remains None and spellframe must be non-None
        spell_for_name = spell
        if spell_for_name is None and spell_name is not None:
            spell_for_name = spell_name

        frame_key, bind_key = SpellInputUtils.normalize_spell_key(
            spell=spell_for_name,
            spellframe=spellframe,
            binding_name=binding_name,
        )

        lookup_key = (frame_key, bind_key)
        return self._resolve_spell_by_lookup_key(lookup_key)

    def _resolve_spell_by_id(self, spell_id: str) -> ISpell:
        """
        Internal

        Resolve an ``ISpell`` by its canonical ``spell_id`` (SHA256).

        This performs a linear scan over the local and contracted spell
        maps. It is intended for cases where the caller has an exact
        fingerprint and does not care about logical identity keys.

        Args:
            spell_id:
                The SHA256 fingerprint associated with the spell.

        Returns:
            ISpell:
                The resolved spell configuration object.

        Raises:
            KeyError:
                If no spell with the given ``spell_id`` exists in either
                the local or contracted spell maps.
        """
        # Local spells
        if self._owned_spells is not None:
            for candidate in self._owned_spells.values():
                if candidate.spell_id == spell_id:
                    return candidate

        # Contracted spells (per-conduit maps)
        if self._contracted_spells is not None:
            for spell_map in self._contracted_spells.values():
                for candidate in spell_map.values():
                    if candidate.spell_id == spell_id:
                        return candidate

        raise KeyError(f"[MELD] No spell found with spell_id: {spell_id}")

    def _resolve_spell_by_lookup_key(
            self,
            lookup_key: tuple[str, str],
    ) -> ISpell:
        """
        Internal

        Resolve an ``ISpell`` by its logical identity key:

            (frame_key, binding_name)

        The lookup proceeds in two phases:

        1. Check the local Spellbook lookup map.
        2. Check each contracted-conduit lookup map.

        This method orchestrates both lookups and is responsible for
        raising a ``KeyError`` when no spell can be found.

        Args:
            lookup_key:
                A tuple ``(frame_key, binding_name)`` produced by
                ``SpellInputUtils.normalize_spell_key`` or
                ``SpellInputUtils.make_spell_key_from_parts``.

        Returns:
            ISpell:
                The resolved spell configuration object.

        Raises:
            KeyError:
                If no spell can be resolved for the given key in either
                the local or contracted spell maps.
            RuntimeError:
                If a ``SpellIndex`` is found for the key, but the
                associated spell object is missing from the expected map.
        """
        frame_key, bind_key = lookup_key

        # 1) Local lookup
        local_spell = self._resolve_local_by_lookup_key(lookup_key)
        if local_spell is not None:
            return local_spell

        # 2) Contracted lookup
        contracted_spell = self._resolve_contracted_by_lookup_key(lookup_key)
        if contracted_spell is not None:
            return contracted_spell

        # 3) Not found anywhere
        raise KeyError(
            f"[MELD] No spell found for frame='{frame_key}', binding='{bind_key}'."
        )

    def _resolve_local_by_lookup_key(
            self,
            lookup_key: tuple[str, str],
    ) -> Optional[ISpell]:
        """
        Internal

        Attempt to resolve an ``ISpell`` from the **local** Spellbook maps
        using a logical identity key.

        Args:
            lookup_key:
                The logical identity key ``(frame_key, binding_name)``.

        Returns:
            Optional[ISpell]:
                The resolved spell object if found locally, otherwise
                ``None``.

        Raises:
            RuntimeError:
                If a ``SpellIndex`` is found in the local lookup map but
                the owned spell map is unavailable or does not contain
                the corresponding spell object.
        """
        if self._lookup_owned_spells is None:
            return None

        spell_index = self._lookup_owned_spells.get(lookup_key)
        if spell_index is None:
            return None

        if self._owned_spells is None:
            raise RuntimeError(
                "[MELD] Local lookup map resolved a SpellIndex, but the "
                "owned spell map is not available."
            )

        result = self._owned_spells.get(spell_index)
        if result is None:
            raise RuntimeError(
                f"[MELD] Local SpellIndex {spell_index} resolved for key "
                f"{lookup_key}, but no spell object found."
            )

        return result

    def _resolve_contracted_by_lookup_key(
            self,
            lookup_key: tuple[str, str],
    ) -> Optional[ISpell]:
        """
        Internal

        Attempt to resolve an ``ISpell`` from **contracted** Spellbook maps
        using a logical identity key.

        This iterates over all peer conduits known to this Meld instance
        and consults their per-conduit lookup maps.

        Args:
            lookup_key:
                The logical identity key ``(frame_key, binding_name)``.

        Returns:
            Optional[ISpell]:
                The resolved spell object if found among contracted
                spells, otherwise ``None``.

        Raises:
            RuntimeError:
                If a contracted lookup map resolves a ``SpellIndex`` but:
                  * the global contracted spell map is unavailable, or
                  * there is no spell map for that conduit ID, or
                  * the spell map does not contain a spell object for
                    the resolved ``SpellIndex``.
        """
        if self._lookup_contracted_spells is None:
            return None

        # If contracted lookup maps exist, we expect contracted spell maps
        # to exist as well. We only enforce this when we actually find a hit.
        for conduit_id, lookup_map in self._lookup_contracted_spells.items():
            spell_index = lookup_map.get(lookup_key)
            if spell_index is None:
                continue

            if self._contracted_spells is None:
                raise RuntimeError(
                    f"[MELD] Contracted lookup map exists for conduit "
                    f"'{conduit_id}' but contracted spell map is not available."
                )

            spell_map = self._contracted_spells.get(conduit_id)
            if spell_map is None:
                raise RuntimeError(
                    f"[MELD] Contracted lookup map exists for conduit "
                    f"'{conduit_id}' but no contracted spell map is present."
                )

            result = spell_map.get(spell_index)
            if result is None:
                raise RuntimeError(
                    f"[MELD] SpellIndex {spell_index} resolved for key "
                    f"{lookup_key} in conduit '{conduit_id}', but no "
                    f"spell object found."
                )

            return result

        return None

    @staticmethod
    def _execute_hooks(hooks: List[Callable], phase: str) -> None:
        """
        Execute lifecycle hooks (e.g., pre-cast, post-cast) that do **not** take
        an instance context (zero-argument callables).

        Args:
            hooks (List[Callable]): The list of functions to execute.
            phase (str): The name of the lifecycle phase (for error reporting).

        Returns:
            None.

        Raises:
            HookExecutionError: Wraps any exception raised by a hook during execution.
        """
        for hook in hooks:
            try:
                hook()
            except Exception as e:
                hook_name = getattr(hook, "__name__", repr(hook))
                raise HookExecutionError(phase, hook_name, e) from e

    @staticmethod
    def _execute_activation_hooks(hooks: List[Callable], instance: Any) -> None:
        """
        Execute activation hooks, passing the resolved component instance as context.

        Each activation hook is expected to accept at least one positional
        argument: the instance being activated.

        Args:
            hooks (List[Callable]): The list of functions to execute.
            instance (Any): The resolved component instance.

        Returns:
            None.

        Raises:
            HookExecutionError: Wraps any exception raised by a hook during execution.
        """
        for hook in hooks:
            try:
                hook(instance)
            except Exception as e:
                hook_name = getattr(hook, "__name__", repr(hook))
                raise HookExecutionError("activation", hook_name, e) from e

    # ----------------------------------------------------------------------
    # Existing creation reuse
    # ----------------------------------------------------------------------
    def _get_existing_creation(self, spell: ISpell) -> Optional[Any]:
        """
        Attempts to retrieve a cached instance from the `Creations` manager
        based on the spell's `Existence` lifecycle mode.

        Args:
            spell (ISpell): The resolved Spell configuration object.

        Returns:
            Optional[Any]: The existing component instance if found and reuse is
                           permitted by the Existence mode, otherwise **None**.
        """
        creations = self._creations
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id

        # Existence.many means always fresh, never reuse
        if existence is Existence.many:
            return None

        # --- Check Normal Conduit Creations (Creations) ---
        if isinstance(creations, Creations):
            if existence is Existence.unique:
                creation = creations._unique.get(spell_id)
                return creation.value if creation is not None else None

            if existence is Existence.unique_per_conduit:
                creation = creations._unique_per_scope.get(spell_id)
                return creation.value if creation is not None else None

            if existence is Existence.unique_per_conduit_cluster:
                creation = creations._unique_per_cluster.get(spell_id)
                return creation.value if creation is not None else None

            if existence is Existence.unique_per_conduit_lineage:
                creation = creations._unique_per_lineage.get(spell_id)
                return creation.value if creation is not None else None

            if existence is Existence.unique_per_spell_space:
                # Not wired yet; no reuse semantics defined.
                return None

            # Defensive fallback
            return None

        # --- Check Lesser Conduit Creations (LesserCreations) ---
        if isinstance(creations, LesserCreations):
            if existence is Existence.unique_per_conduit:
                creation = creations._unique_per_scope.get(spell_id)
                return creation.value if creation is not None else None
            # Delegate frame-level singletons to parent creations when available.
            parent_creations = getattr(creations, "_parent_creations", None)
            if isinstance(parent_creations, Creations):
                if existence is Existence.unique:
                    found = parent_creations._unique.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_conduit_cluster:
                    found = parent_creations._unique_per_cluster.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_conduit_lineage:
                    found = parent_creations._unique_per_lineage.get(spell_id)
                    return found.value if found is not None else None
                if existence is Existence.unique_per_spell_space:
                    # Not implemented; no reuse.
                    return None
            # Existence.many is handled above. Other unique modes are delegated or unsupported.
            return None

        # Unknown creations manager type; no reuse possible
        return None

    # ----------------------------------------------------------------------
    # Spell-type–aware dispatch and registration
    # ----------------------------------------------------------------------
    def _meld_by_spell_type(
            self,
            spell: ISpell,
            overrides: Optional[dict[str, Any]],
    ) -> Any:
        """
        Obtain a new component instance based on the Spell's canonical `SpellType`.

        Behaviour:

            * EXISTING_CREATION*:
                  Returns the pre-created object stored on the spell and relies
                  on `_register_spell` to cache it into the creations manager.

            * Class / method / lambda spells:
                  Delegate to the DAG-based `MeldRuntime` / `MeldEngine` stack
                  using a per-call `MeldContext` seeded with `overrides`.

            * Anything else:
                  Raises a `RuntimeError` indicating an unsupported SpellType.

        Args:
            spell:
                The resolved Spell configuration object.
            overrides:
                Normalized per-call overrides (or ``None``), as produced by
                :meth:`_normalize_spell_override`.

        Returns:
            Any:
                The newly resolved component instance.

        Raises:
            RuntimeError:
                - If the spell is an existing-creation spell with no backing
                  `user_created_object`.
                - If the meld runtime is not configured.
                - If the SpellType is unsupported.
            MeldExecutionError:
                Propagated from `MeldRuntime.execute` if DI or construction fails.
        """
        stype = spell.spell_type

        # 1) Existing Creation: the instance already exists on the spell and
        #    must never be constructed via the runtime.
        if spell.is_existing_creation:
            instance = spell.user_created_object
            if instance is None:
                raise RuntimeError(
                    "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                    f"(spell_id={spell.spell_id})."
                )
            return instance

        # 2) Factory-style spells must go through the runtime.
        if self._runtime is None:
            raise RuntimeError("[MELD] MeldRuntime is not configured on this Meld instance.")

        if spell.is_class_spell or spell.is_method_spell or spell.is_lambda_spell:
            context = self._create_meld_context(spell, overrides)
            try:
                return self._runtime.execute(context)
            finally:
                # Make sure we always tear down the context, even if the runtime
                # raises a MeldExecutionError or another exception.
                try:
                    context.cleanup()
                except Exception:
                    pass

        # 3) Anything else is currently unsupported.
        raise RuntimeError(f"[MELD] Unsupported SpellType encountered: {stype}")


# ----------------------------------------------------------------------
# Registration Helpers (New Structure)
# ----------------------------------------------------------------------
    def _register_spell(self, spell: ISpell, instance: Any) -> None:
        """
        Registers a newly obtained component instance with the Creations system,
        adhering to the spell's `Existence` mode.

        This method acts as a dispatcher, calling the correct helper based on the
        type of the Conduit's creations manager (`Creations` vs `LesserCreations`).

        Args:
            spell (ISpell): The resolved Spell configuration object.
            instance (Any): The newly created component instance.

        Returns:
            None.

        Raises:
            NotImplementedError: Propagated from `_register_to_creations`.
            RuntimeError: Propagated from helpers, or raised if the creations manager
                          type itself is unsupported.
        """
        creations = self._creations

        # --- Dispatch based on Creations Manager Type ---

        # Normal conduit: full Creations manager
        if isinstance(creations, Creations):
            self._register_to_creations(spell, instance)
            return

        # LesserConduit: LesserCreations manager
        if isinstance(creations, LesserCreations):
            self._register_to_lesser_creations(spell, instance)
            return

        # Unknown creations manager type
        raise RuntimeError(
            f"[MELD] Unsupported creations manager type: {type(creations).__name__}"
        )

    def _register_to_creations(self, spell: ISpell, instance: Any) -> None:
        """
        Handles registration for the full Creations manager (used by a normal Conduit).

        It registers the new instance based on all supported Existence modes,
        including unique, unique_per_conduit, many, cluster, and lineage.

        Args:
            spell (ISpell): The resolved Spell configuration object.
            instance (Any): The newly created component instance.

        Returns:
            None.

        Raises:
            NotImplementedError: For Existence.unique_per_spell_space, which is
                                 configured but not yet implemented for registration.
            RuntimeError: If an unsupported Existence mode is encountered for
                          the Creations manager.
        """
        creations: ICreations = self._creations  # Type narrowed by caller
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id

        if existence is Existence.unique:
            creations.add_unique(spell_id, instance)
            return

        if existence is Existence.unique_per_conduit:
            creations.add_unique_per_scope(spell_id, instance)
            return

        if existence is Existence.many:
            creations.add_many(spell_id, instance)
            return

        if existence is Existence.unique_per_conduit_cluster:
            creations.add_unique_per_cluster(spell_id, instance)
            return

        if existence is Existence.unique_per_conduit_lineage:
            creations.add_unique_per_lineage(spell_id, instance)
            return

        if existence is Existence.unique_per_spell_space:
            raise NotImplementedError(
                "[MELD] Registration for Existence.unique_per_spell_space is not yet implemented."
            )

        # Fallback for any unsupported mode in Creations
        raise RuntimeError(
            f"[MELD] Unsupported Existence '{existence}' for spell_id={spell_id} "
            f"in Creations."
        )


    def _register_to_lesser_creations(self, spell: ISpell, instance: Any) -> None:
        """
        Handles registration for the LesserCreations manager (used by a LesserConduit).

        This manager only supports a limited set of existence modes:
        `unique_per_conduit` and `many`.

        Args:
            spell (ISpell): The resolved Spell configuration object.
            instance (Any): The newly created component instance.

        Returns:
            None.

        Raises:
            RuntimeError: If an Existence mode other than `unique_per_conduit` or
                          `many` is attempted in a LesserConduit context.
        """
        creations: ILesserCreations = self._creations  # Type narrowed by caller
        existence: Existence = spell.existence
        spell_id: str = spell.spell_id

        if existence is Existence.unique_per_conduit:
            creations.add_unique_per_scope(spell_id, instance)
            return

        if existence is Existence.many:
            creations.add_many(spell_id, instance)
            return

        # Delegate frame-level lifetimes to the parent creations when available.
        parent_creations = getattr(creations, "_parent_creations", None)
        if isinstance(parent_creations, Creations):
            if existence is Existence.unique:
                parent_creations.add_unique(spell_id, instance)
                return
            if existence is Existence.unique_per_conduit_cluster:
                parent_creations.add_unique_per_cluster(spell_id, instance)
                return
            if existence is Existence.unique_per_conduit_lineage:
                parent_creations.add_unique_per_lineage(spell_id, instance)
                return
            if existence is Existence.unique_per_spell_space:
                raise NotImplementedError(
                    "[MELD] Registration for Existence.unique_per_spell_space is not yet implemented."
                )

        # LesserConduits only support a subset of existence modes locally
        raise RuntimeError(
            f"[MELD] Existence '{existence}' is not supported for registration "
            f"in LesserConduits (spell_id={spell_id})."
        )
