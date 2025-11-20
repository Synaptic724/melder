from threading import RLock
from typing import Optional, Dict, Any, NamedTuple, Callable, List, Union

# Melder Imports
from melder.utilities.data_structures.concurrent_dict import ConcurrentDict
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.utilities.interfaces.interfaces import (
    IConduit,
    ISpellbook,
    ISpell,
    IMeld,
    ILesserCreations,
    ICreations, ISpellIndex,
)
from melder.utilities.custom_exceptions.hook_execution_error import HookExecutionError
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence

# Creations types
from melder.aether.conduit.creations.creations import Creations
from melder.aether.conduit.creations.lesser_creations import LesserCreations


class Meld(IMeld):
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

    def __init__(self, creations: ILesserCreations | ICreations, spellbook: ISpellbook):
        """
        Initializes the Meld component with references to the component store
        and the configuration registry.

        Args:
            creations (ILesserCreations | ICreations):
                The local component instance manager (either `Creations` for a
                full Conduit or `LesserCreations` for a LesserConduit).
            spellbook (ISpellbook):
                The registry of all known spell configurations, whose internal
                ConcurrentDicts are referenced here for thread-safe lookups.
        """
        super().__init__()
        # Internal lock for thread-safe state management (e.g., during cleanup)
        self._lock = RLock()
        self._cleaned = False  # Track cleanup state

        # Spellbook references (used for resolution)
        # These are direct references to the ConcurrentDicts in the Spellbook
        self._owned_spells: ConcurrentDict[ISpellIndex, ISpell] = spellbook._spells
        self._contracted_spells: ConcurrentDict[str, ConcurrentDict[ISpellIndex, ISpell]] = spellbook._contracted_spells

        self._lookup_owned_spells: ConcurrentDict[tuple, ISpellIndex] = spellbook._lookup_spells
        self._lookup_contracted_spells: ConcurrentDict[str, ConcurrentDict[tuple, ISpellIndex]] = spellbook._lookup_contracted_spells


        # Conduit-local instantiation manager (Creations or LesserCreations)
        self._creations = creations

    def cleanup(self) -> None:
        """
        Cleanup the Meld instance to prevent further modifications and release
        references to the spell configurations and creations manager.

        This should be called when the owning `Conduit` is being shut down.

        Args:
            None.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            # Clear references
            self._owned_spells = None
            self._contracted_spells = None
            self._lookup_owned_spells = None
            self._lookup_contracted_spells = None
            self._creations = None

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
            spell: str | object | None = None,
            *,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Optional[Any]:
        """
        Entry point for resolving and activating a spell (component) within this Conduit.

        This method orchestrates the full lifecycle: resolution, reuse, instantiation,
        hook execution, and registration.

        Args:
            spell (str | object | None):
                The primary spell identifier.
                - If a **string**, treated as the unique `spell_id`.
                - If an **object** (e.g., a class), used with `spellframe`
                  and `binding_name` to form the DI identity key.
            spellframe (str | object | None):
                Optional Spellframe / Protocol / class used as the primary DI identity.
                Often redundant if `spell` is the class/protocol itself.
            binding_name (str | None):
                Optional binding name, used alongside `spell` or `spellframe` to create
                a unique lookup key.
            spell_override (dict | list | tuple | None):
                Optional override payload attached to the Spell's metadata (under the
                key `"spell_override"`) for downstream strategy layers to consume.

        Returns:
            Optional[Any]:
                The resolved component instance (either reused or newly created).

        Raises:
            KeyError: If the spell cannot be resolved by the provided inputs.
            NotImplementedError: If the spell type (e.g., class-based DI) or existence
                                 mode is not yet supported for construction/registration.
            HookExecutionError: If a pre-cast, activation, or post-cast hook fails.
            RuntimeError: For unexpected internal state issues (e.g., missing object
                          after ID resolution, unsupported Creations manager, or
                          missing `existing_object`).
        """
        with self._lock:
            # 1) Resolve the spell object from the Spellbook
            target_spell = self._resolve_spell(spell, spellframe, binding_name)

            # 2) Attach override metadata (if any)
            self._apply_override(target_spell, spell_override)

            # 3) Execute pre-cast hooks (no instance yet)
            self._execute_hooks(target_spell.pre_hooks, "pre_cast")

            # 4) Try to reuse an existing creation based on Existence + creations type
            instance = self._get_existing_creation(target_spell)

            # 5) If no existing instance, go through spell-type path and then register
            if instance is None:
                instance = self._meld_by_spell_type(target_spell)
                # Once we have an instance, register it into the proper creations bucket
                self._register_spell(target_spell, instance)
                # 6) Execute activation hooks with instance context only if instance is new
                self._execute_activation_hooks(target_spell.activation_hooks, instance)

            # 7) Execute post-cast hooks (still no arguments for now)
            self._execute_hooks(target_spell.post_hooks, "post_cast")

            # 8) Return the resolved instance
            return instance

    # ----------------------------------------------------------------------
    # Resolution helpers
    # ----------------------------------------------------------------------
    def _resolve_spell(
            self,
            spell: Any,
            spellframe: Any,
            binding_name: Optional[str],
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
        # ------------------------------------------------------------------
        # 1) Resolution by spell_id (string)
        # ------------------------------------------------------------------
        if isinstance(spell, str):
            return self._resolve_spell_by_id(spell)

        # ------------------------------------------------------------------
        # 2) Resolution by (spellframe / spell, binding_name)
        # ------------------------------------------------------------------
        frame_key, bind_key = SpellInputUtils.normalize_spell_key(
            spell=spell,
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
    def _apply_override(spell: ISpell, override: Optional[Union[dict, list, tuple]]) -> None:
        """
        Attaches the user-provided override payload to the spell's metadata.

        Args:
            spell (ISpell): The resolved Spell configuration object.
            override (Optional[Union[dict, list, tuple]]): The payload to attach.

        Returns:
            None.
        """
        if override is not None:
            # Metadata is exposed as a mutable dictionary on the Spell interface
            spell.metadata["spell_override"] = override

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

            # Existence.many is handled above. Other unique modes are not relevant
            # for a LesserConduit's scope.
            return None

        # Unknown creations manager type; no reuse possible
        return None

    # ----------------------------------------------------------------------
    # Spell-type–aware dispatch and registration
    # ----------------------------------------------------------------------
    def _meld_by_spell_type(self, spell: ISpell) -> Any:
        """
        Obtain a new component instance based on the Spell's canonical `SpellType`.

        Args:
            spell (ISpell): The resolved Spell configuration object.

        Returns:
            Any: The newly resolved component instance.

        Raises:
            NotImplementedError: For spell types requiring DI/constructor resolution
                                 (e.g., `SPELL` for class construction or `METHOD`).
            RuntimeError: For unknown or unsupported SpellTypes.
        """
        stype = spell.spell_type

        # Existing Creation: The instance is already defined in the spell
        if stype in (
                SpellType.EXISTING_CREATION,
                SpellType.EXISTING_CREATION_WITH_SPELLFRAME,
                SpellType.EXISTING_CREATION_WITH_BINDING_NAME_WITH_SPELLFRAME,
        ):
            raise RuntimeError("[MELD] Cannot meld existing creations, please register the spell as a direct spell reference.")

        # Class-based Spells: Requires full DI resolution (Not Implemented)
        if stype in (
                SpellType.SPELL,
                SpellType.SPELL_WITH_SPELLFRAME,
                SpellType.SPELL_WITH_BINDING_NAME,
                SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
        ):
            raise NotImplementedError(
                "[MELD] Class-based spell melding is not yet implemented."
            )

        # Method-based Spells: Requires full DI resolution (Not Implemented)
        if stype in (
                SpellType.METHOD,
                SpellType.METHOD_WITH_BINDING_NAME,
                SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
        ):
            raise NotImplementedError(
                "[MELD] Method-based spell melding is not yet implemented."
            )

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

        # LesserConduits only support a subset of existence modes
        raise RuntimeError(
            f"[MELD] Existence '{existence}' is not supported for registration "
            f"in LesserConduits (spell_id={spell_id})."
        )