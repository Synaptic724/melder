from typing import Any, Dict, Iterable, List, Mapping, Optional, Protocol, Tuple, runtime_checkable
from types import ModuleType
from melder.spellbook.existence.existence import Existence
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellindex import ISpellIndex

@runtime_checkable
class ISpellbook(ICleanable, Protocol):
    """
    Interface for a **Spellbook**: the central authority for spell definitions,
    bindings, configuration, and contract-based sharing.

    This interface reflects the *SpellIndex-native* implementation:

    * Local and contracted spells are keyed by `SpellIndex`.
    * Version SHAs are tracked via `SpellIndex._versions` plus:
        - `_spell_versions`  (local)
        - `_contracted_versions` (per-conduit)
    * Current spell_id maps are maintained for owned and contracted spells.

    The Spellbook participates in:
      * Local binding + lifecycle (`bind`, `Existence`)
      * Cross-conduit contracts (via ConduitWard/Contract)
      * Aether frame configuration and global registry
      * Conduit conjuration (execution scope)
    """

    # ------------------------------------------------------------------
    # Core backing fields (shape only; concrete types live in impl)
    # ------------------------------------------------------------------
    _lookup_contracted_spells: Optional[Any]
    _lookup_spells: Optional[Any]
    _contracted_spells: Optional[Any]
    _contracted_versions: Optional[Any]
    _contracted_spells_by_id: Optional[Any]
    _spells: Optional[Any]
    _spell_versions: Optional[Any]
    _spells_by_id: Optional[Any]
    _bind: Optional[Any]
    _id: str
    _aetheric_frame: Optional[str]
    _configuration: 'Optional[IConfiguration]'
    _spell_id_pool: Optional[Any]

    # Spell Validator
    _spell_validator: 'SpellValidationSystem'
    _spell_system_states: "ISpellSystemStates"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def spells(self) -> Mapping[ISpellIndex, ISpell]:
        """
        Public API

        Returns a read-only view of the **local spells** registered
        in this Spellbook.

        This provides safe introspection of the local registry without
        allowing external mutation.

        Returns:
            Mapping[SpellIndex, ISpell]:
                An immutable map of `SpellIndex` -> spell object.
        """
        ...

    @property
    def contracted_spells(self) -> Mapping[str, Mapping[ISpellIndex, ISpell]]:
        """
        Public API

        Returns a per-conduit read-only view of all **borrowed** spells.

        Each peer conduit ID maps to its own immutable
        `SpellIndex -> ISpell` map.

        Returns:
            Mapping[str, Mapping[SpellIndex, ISpell]]:
                Immutable map of peer Conduit ID -> immutable map of
                borrowed spells.
        """
        ...

    def snapshot_state(self) -> Dict[str, Any]:
        """
        Public API

        Build a read-only snapshot of Spellbook state.

        Purpose:
            Provide a stable view of local and contracted spell registries while
            transactions may be in-flight.
        Contract:
            - Returns detached copies of internal maps; mutating the snapshot
              does not affect the Spellbook registries.
            - Includes a snapshot id for observability.
        Returns:
            Dict[str, Any]: Snapshot payload containing local/contracted maps
            and lookup caches.
        """
        ...

    # ------------------------------------------------------------------
    # Binding / inspection / lookup API
    # ------------------------------------------------------------------
    def bind(
            self,
            spell: Any,
            existence: str | Existence,
            *,
            permissions: str = "create",
            spellframe: Any = None,
            binding_name: Any = None,
            profile: str = "general",
            **kwargs: Any,
    ) -> str:
        """
        Public API

        Binds a spell into the Spellbook for future instantiation and
        dependency injection.

        This method profiles the spell, computes a unique SHA256 ID,
        stores it locally, and assigns lifecycle + permission policies.

        Binding requires an active binding transaction. Use
        ``begin_transaction("bind")`` (or ``begin_binding_transaction()``)
        before binding and ``end_binding_transaction()`` once registration
        is complete.

        Permissions (access control to other conduits):
            - ``"read"``:
                Other conduits may *use* the spell but not create
                new instances.
            - ``"create"`` (default):
                Other conduits may both use *and* create instances.
            - ``"block"``:
                Completely blocks access from other conduits; only
                the owning conduit may use it.

        Existence (spell lifecycle):
            Controls how instances are managed (e.g., `Existence.unique`,
            `Existence.many`, etc.).

        Lifecycle hooks (optional ``**kwargs``):
            - ``pre_hooks``:
                List[Callable] executed *before* the spell is constructed.
            - ``activation_hooks``:
                List[Callable] executed *during* spell construction.
            - ``post_hooks``:
                List[Callable] executed *after* the spell has been cast.

        Args:
            spell:
                The class, function, or object to bind.
            existence:
                The lifecycle scope for this spell.
            permissions:
                Permission level exposed to other conduits:
                ``"read"``, ``"create"``, or ``"block"``.
            spellframe:
                Logical interface/namespace or grouping label.
            binding_name:
                Secondary key to distinguish this spell within its frame.
            **kwargs:
                Optional lifecycle hooks: ``pre_hooks``,
                ``activation_hooks``, ``post_hooks``.

        Returns:
            str: The primary SHA256 ``spell_id`` for the head version.

        Raises:
            RuntimeError:
                If a spell with the same ID already exists in the Aether registry.
            RuntimeError:
                If no binding transaction is active for this Spellbook.
            TypeError:
                If any provided hook is not callable.
            ValueError:
                If the ``permissions`` string cannot be converted into a
                valid `Permissions` enum.
        """
        ...


    def scan(self, module: ModuleType) -> list[str]:
        """
        Public API

        Scan a module for `scan_bind`-decorated objects and bind them.

        This is a module-only scan: it does not traverse packages or import
        submodules. Any object marked with `scan_bind` must originate from the
        scanned module, otherwise the scan fails.

        Scanning requires an active binding transaction. Use
        ``begin_transaction("bind")`` (or ``begin_binding_transaction()``)
        before scanning and ``end_binding_transaction()`` once registration
        is complete.

        Args:
            module (ModuleType): The module to scan for decorated spell targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            TypeError: If `module` is not a module or metadata is invalid.
            ValueError: If a decorated object is not owned by the module.
            RuntimeError: If no binding transaction is active for this Spellbook.
            RuntimeError: Propagated from Spellbook.bind on binding errors.
        """
        ...

    def begin_binding_transaction(self) -> None:
        """
        Public API

        Begin a binding transaction for this Spellbook.

        Purpose:
            Enable binding operations (bind/scan) in a controlled transaction window.
        Contract:
            - Only one binding transaction may be active at a time.
            - While active, `bind(...)` and `scan(...)` are allowed.
            - When inactive, `bind(...)` and `scan(...)` raise.
        Returns:
            None.
        Raises:
            RuntimeError: If a binding transaction is already active.
        """
        ...

    def begin_transaction(
            self,
            transaction_type: "ChangeTransactionType | str",
            *,
            conduit_id: Optional[str] = None,
            conduit_ids: Optional[Iterable[str]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Public API

        Begin a change-control transaction for this Spellbook.

        Purpose:
            Admit a mutation request through the ChangeControlManager and,
            for bind transactions, open the binding transaction window.
        Contract:
            - Only one change-control transaction may be active per Spellbook.
            - Admission is serialized by the ChangeControlOrchestrator.
            - Bind transactions open the binding transaction window.
            - Scan is not a transaction type; it must run inside a bind transaction.
        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "bind", "link").
            conduit_id:
                Optional initiator conduit id for logging.
            conduit_ids:
                Optional list of conduits participating in the request.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys affected by the request.
            contract_keys:
                Optional contract keys affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If a change transaction is already active.
            RuntimeError: If binding transaction is already active for bind requests.
            RuntimeError: If change-control admission is denied.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    def end_transaction(
            self,
            transaction_type: "ChangeTransactionType | str | None" = None,
    ) -> None:
        """
        Public API

        End the active change-control transaction for this Spellbook.

        Purpose:
            Finalize an admitted change-control request and release any
            implicit embargo state tracked by the ChangeControlManager.
        Contract:
            - Ends the active request tracked by this Spellbook.
            - Bind transactions close the binding transaction window.
            - Raises if no change transaction is active.
        Args:
            transaction_type:
                Optional transaction type assertion for safety checks.
        Returns:
            None.
        Raises:
            RuntimeError: If no change transaction is active.
            RuntimeError: If transaction_type does not match the active request.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    def end_binding_transaction(self) -> None:
        """
        Public API

        End the active binding transaction for this Spellbook.

        Purpose:
            Disable binding operations until a new transaction is started.
        Contract:
            - Binding transactions must be explicitly closed.
            - When inactive, `bind(...)` and `scan(...)` raise.
        Returns:
            None.
        Raises:
            RuntimeError: If no binding transaction is active.
        """
        ...

    def binding_transaction(self) -> "ISpellbook":
        """
        Public API

        Context-managed binding transaction for this Spellbook.

        Contract:
            - Starts a binding transaction on entry.
            - Ends the transaction on exit, even if an exception is raised.
            - Nested usage raises on begin (transaction already active).
        Returns:
            ISpellbook: The current Spellbook instance.
        Raises:
            RuntimeError: If a binding transaction is already active.
        """
        ...

    def create_binder(
            self,
            *,
            default_existence: Existence = Existence.unique,
            default_permissions: str = "create",
    ) -> 'SpellBinder':
        """
        Public API

        Creates a `SpellBinder` instance that provides an Autofac-style
        fluent syntax on top of `Spellbook.bind(...)`.

        This does *not* introduce a new registration path; it simply
        forwards everything into the existing binding pipeline so all
        reflection, `SpellIndex` construction, `SpellType` classification,
        and validation flows remain exactly the same.

        Example:
            binder = spellbook.create_binder()

            binder.bind(MyService) \\
                  .as_unique() \\
                  .under_spellframe(IMyServiceProtocol) \\
                  .named("primary") \\
                  .with_permissions("create") \\
                  .finalize()

            # Reuse the same binder for another spell:
            binder.bind(OtherService, existence=Existence.many).finalize()

        Args:
            default_existence (Existence):
                Default lifecycle scope for fluent registrations started via
                this binder.

            default_permissions (str):
                Default permissions for fluent registrations (e.g. "create").

        Returns:
            SpellBinder:
                A reusable fluent registration helper bound to this Spellbook.
        """
        ...

    def inspect_spell(self, spell: Any, aetheric_frame: str = "default") -> Optional[str]:
        """
        Public API

        Inspects an object instance to determine its unique SHA256 ID,
        then checks if that ID is registered anywhere in the Aether
        Registry for the given frame.

        Args:
            spell:
                The object to inspect (class, function, or instance).
            aetheric_frame:
                The Aether frame to check against.

        Returns:
            Optional[str]:
                The spell_id if the spell is registered in the Aether,
                otherwise ``None``.
        """
        ...

    def describe_spells_in_spellbook(self) -> list[dict[str, Any]]:
        """
        Return a user-facing dump of spell targeting details currently visible
        through this Spellbook.
        """
        ...

    def find_spell_by_id(self, spell_id: str) -> Optional[ISpell]:
        """
        Finds a spell by its unique identifier within the spellbook.

        Args:
            spell_id: The identifier of the spell to find.

        Returns:
            Optional[ISpell]: The spell if found, otherwise None.
        """
        ...

    def describe_spells_in_spellbook(self) -> list[dict[str, Any]]:
        """
        Return a user-facing dump of spell targeting details currently visible
        through this Spellbook.
        """
        ...

    def find_spell_index(
            self,
            spellframe: str,
            spell_name: str,
            binding_name: str,
    ) -> Optional[ISpellIndex]:
        """
        Public API

        Finds a spell's **SpellIndex** using its
        logical identifiers.

        Lookup order:
            1. Local spells
            2. Contracted (borrowed) spells

        Args:
            spellframe:
                Logical namespace or grouping label.
            spell_name:
                Name of the spell class or function.
            binding_name:
                Secondary key used to distinguish this spell.

        Returns:
            Optional[SpellIndex]:
                The SpellIndex associated with this spell.

        Raises:
            RuntimeError:
                If the spell is not found locally or in any contracted
                spellbook.
        """
        ...

    def find_spell_key(
            self,
            spellframe: str,
            spell_name: str,
            binding_name: str,
    ) -> Optional[Tuple[str, str]]:
        """
        Public API

        Finds a spell's **primary lookup key** using its logical
        identifiers.

        The search checks local spells first, then contracted spells.

        Args:
            spellframe:
                Logical namespace or grouping label.
            spell_name:
                Name of the spell class or function.
            binding_name:
                Secondary key to distinguish this spell.

        Returns:
            Optional[tuple[str, str]]:
                The normalized lookup key
                ``(frame_or_name, binding_name_or_default)`` if found.

        Raises:
            RuntimeError:
                If the key cannot be found (local or contracted).
        """
        ...

    def get_spell_by_index_id(
            self,
            spell_index_id: str,
    ) -> Optional[ISpell]:
        """
        Public API

        Resolve a spell by its stable SpellIndex id.

        Returns:
            Optional[ISpell]:
                Matching local or contracted spell when found.
        """
        ...

    def get_spell_permissions(self, spell_index: ISpellIndex) -> Optional[str]:
        """
        Public API

        Retrieves the access permissions for a **locally** registered spell.

        Args:
            spell_index:
                The SpellIndex of the spell.

        Returns:
            Optional[str]:
                The permissions name (``"read"``, ``"create"``, or
                ``"block"``) for this spell.

        Raises:
            RuntimeError:
                If the spell with the given index is not found in the
                local spellbook.
        """
        ...

    # ------------------------------------------------------------------
    # Internal local/contracted lookup + version cache API
    # ------------------------------------------------------------------
    def _find_spell(self, spell_index: ISpellIndex) -> Optional[ISpell]:
        """
        Internal

        Locates a **local** spell by its `SpellIndex`.

        Args:
            spell_index:
                The SpellIndex of the spell to find.

        Returns:
            Optional[ISpell]:
                The spell object if found, else ``None``.
        """
        ...

    def _find_contracted_spell(self, spell_index: ISpellIndex) -> Optional[ISpell]:
        """
        Internal

        Locates a **contracted** spell by its `SpellIndex` by searching
        across all peer conduit maps.

        Args:
            spell_index:
                The SpellIndex of the contracted spell.

        Returns:
            Optional[ISpell]:
                The spell object if found.

        Raises:
            RuntimeError:
                If the contracted spell cannot be found in any peer
                contract map.
        """
        ...

    def _find_spell_count(self) -> int:
        """
        Internal

        Returns the total number of **locally registered** spells.

        Returns:
            int: Count of local spells.
        """
        ...

    def _find_contracted_spell_count(self) -> int:
        """
        Internal

        Returns the number of **peer conduits** this spellbook currently
        has contracts with (i.e., how many contracted spell maps exist).

        Returns:
            int: Number of active contract links (peer conduits).
        """
        ...

    def _check_all_spells(self) -> None:
        """
        Internal

        Performs a system check to verify that no locally bound spell
        version ID is already registered in the global Aether registry
        for this frame.

        Raises:
            RuntimeError:
                If any spell version is already present in Aether for
                this frame.
        """
        ...

    def _refresh_local_spell_versions(self) -> None:
        """
        Internal

        Rebuilds the local version cache (`_spell_versions`) from the
        current set of `SpellIndex` keys in `_spells`.

        Useful after bulk mutation or research operations that may have
        changed the version lists on `SpellIndex` instances.
        """
        ...

    def _refresh_contracted_spell_versions(self) -> None:
        """
        Internal

        Rebuilds the per-conduit contracted version caches
        (`_contracted_versions`) from the current `_contracted_spells`
        structure.

        After this runs:
            * Each `conduit_id` in `_contracted_spells` will have a
              corresponding `Set[str]` in `_contracted_versions`
              containing **all version IDs** (SHA256) for that
              conduit's spells.
        """
        ...

    def _refresh_all_spell_versions(self) -> None:
        """
        Internal

        Convenience method to refresh **both** local and contracted spell
        version caches in a single call.

        Calls:
            * ``_refresh_local_spell_versions()``
            * ``_refresh_contracted_spell_versions()``
        """
        ...

    # ------------------------------------------------------------------
    # spell_id map helpers (internal)
    # ------------------------------------------------------------------
    def _register_owned_spell_id(self, spell_id: str, spell: ISpell) -> None:
        """
        Internal

        Register the current spell_id mapping for an owned spell.

        Args:
            spell_id:
                Current version id for the spell.
            spell:
                Owned spell instance.

        Raises:
            RuntimeError:
                If the spell_id map is missing or the id collides.
        """
        ...

    def _update_owned_spell_id(self, old_id: str, new_id: str, spell: ISpell) -> None:
        """
        Internal

        Update the owned spell_id mapping after a SpellIndex version change.

        Args:
            old_id:
                Previous version id for the spell index.
            new_id:
                New version id for the spell index.
            spell:
                Owned spell instance.

        Raises:
            RuntimeError:
                If the old id is missing or the new id collides.
        """
        ...

    def _register_contracted_spell_id(
            self,
            conduit_id: str,
            spell_id: str,
            spell: ISpell,
    ) -> None:
        """
        Internal

        Register the current spell_id mapping for a contracted spell.

        Args:
            conduit_id:
                Peer conduit id for the contract.
            spell_id:
                Current version id for the spell.
            spell:
                Contracted spell instance.

        Raises:
            RuntimeError:
                If the contracted map is missing or the id collides.
        """
        ...

    def _update_contracted_spell_id(
            self,
            conduit_id: str,
            old_id: str,
            new_id: str,
            spell: ISpell,
    ) -> None:
        """
        Internal

        Update the contracted spell_id mapping after a SpellIndex version change.

        Args:
            conduit_id:
                Peer conduit id for the contract.
            old_id:
                Previous version id for the spell index.
            new_id:
                New version id for the spell index.
            spell:
                Contracted spell instance.

        Raises:
            RuntimeError:
                If the old id is missing or the new id collides.
        """
        ...

    def _unregister_contracted_spell_id(
            self,
            conduit_id: str,
            spell_id: str,
            spell: ISpell,
    ) -> None:
        """
        Internal

        Remove a contracted spell_id mapping for the given conduit.

        Args:
            conduit_id:
                Peer conduit id for the contract.
            spell_id:
                Current version id for the spell.
            spell:
                Contracted spell instance.

        Raises:
            RuntimeError:
                If the id is missing from the contracted map.
        """
        ...

    # ------------------------------------------------------------------
    # Contract / link API (used by ConduitWard / Contract)
    # ------------------------------------------------------------------
    def _find_contracted_spell_by_id(
            self,
            spell_id: str,
            conduit_id: str,
    ) -> Optional[ISpell]:
        """
        Internal

        Resolves a contracted spell by its **version SHA** using the
        Spellbook's local copies of contracted spells.

        Each contracted spell's `SpellIndex` contains all known versions,
        so this can be resolved purely from local SpellIndex data.

        Args:
            spell_id:
                The version SHA of the spell.
            conduit_id:
                The contracting peer conduit ID.

        Returns:
            Optional[ISpell]:
                The resolved spell if found, otherwise ``None``.
        """
        ...

    def _create_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Initializes the internal storage maps for a **new contract link**
        with a peer conduit.

        Ensures that:
            * `_contracted_spells[conduit_id]`
            * `_lookup_contracted_spells[conduit_id]`
            * `_contracted_versions[conduit_id]`
            * `_contracted_spells_by_id[conduit_id]`

        are created **atomically** and remain in a consistent state.

        Args:
            conduit_id:
                The ID of the peer conduit to create the contract
                structure for.

        Raises:
            RuntimeError:
                If the contract structure is present in some maps but not
                all (inconsistent state).
        """
        ...

    def _remove_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Removes the internal storage maps for a **dissolved** contract
        link with a peer conduit.

        This removes all three maps in lockstep:

            * `_contracted_spells[conduit_id]`
            * `_lookup_contracted_spells[conduit_id]`
            * `_contracted_versions[conduit_id]`
            * `_contracted_spells_by_id[conduit_id]`

        Args:
            conduit_id:
                The ID of the peer conduit whose contract structure
                should be removed.

        Raises:
            RuntimeError:
                If the contract structure is present in some maps but not
                all (inconsistent cleanup).
        """
        ...

    def _add_contracted_spell(self, spell: ISpell, conduit_id: str) -> None:
        """
        Internal

        Adds a specific spell (borrowed from a peer) into the
        **contracted spells** registry and updates the key + version
        caches for the given conduit, plus the spell_id map.

        Args:
            spell:
                The spell object to add.
            conduit_id:
                The ID of the peer conduit this spell was contracted
                from.
        """
        ...

    def _remove_contracted_spell(self, spell_id: str, conduit_id: str) -> None:
        """
        Internal

        Removes a specific contracted spell from the internal registry,
        identified by its **version SHA** and peer conduit.

        Steps:
            * Locate `SpellIndex` whose versions contain `spell_id`.
            * Remove from `_contracted_spells[conduit_id]`.
            * Remove from `_lookup_contracted_spells[conduit_id]`.
            * Remove all versions for this SpellIndex from
              `_contracted_versions[conduit_id]`.
            * Remove from `_contracted_spells_by_id[conduit_id]`.

        Args:
            spell_id:
                The version SHA of the spell to remove.
            conduit_id:
                The ID of the peer conduit the spell was contracted from.

        Raises:
            RuntimeError:
                If the conduit maps do not exist or the target version
                cannot be found.
        """
        ...

    def _clear_contracted_spells_for_conduit(self, conduit_id: str) -> None:
        """
        Internal

        Clears **all spells** associated with a contracted conduit, while
        retaining the contract structure, clearing its id map, and
        zeroing its version cache.

        Args:
            conduit_id:
                The ID of the peer conduit whose contracted spells are
                to be cleared.

        Raises:
            RuntimeError:
                If no contracted spell maps exist for the given conduit.
        """
        ...

    def _sever_link_contract(self, conduit_id: str) -> None:
        """
        Internal

        Fully severs the link contract for a given conduit ID:

            1. Calls ``_clear_contracted_spells_for_conduit(conduit_id)``
               to zero out spells.
            2. Calls ``_remove_link_contract(conduit_id)`` to remove the
               underlying contract structure.

        Args:
            conduit_id:
                The ID of the peer conduit whose contract is to be
                severed.
        """
        ...

    # ------------------------------------------------------------------
    # Configuration / Aether frame API
    # ------------------------------------------------------------------
    def is_configuration_locked(self) -> bool:
        """
        Public API

        Indicates whether this Spellbook's configuration has been
        **frozen** (locked) for its Aether frame.

        Returns:
            bool: ``True`` if locked, ``False`` otherwise.
        """
        ...

    def configure_aether_frame(
            self,
            *,
            system_state: Optional[str],
            disposal: Optional[bool],
            disposal_method_names: Optional[List[str]],
    ) -> None:
        """
        Public API

        Consolidated setup for this Spellbook's **Aether frame**:

          1. Apply provided configuration properties.
          2. Validate + freeze configuration.
          3. Bind the configuration to the Aether.

        Once frozen during this call, the configuration becomes
        immutable.

        Args:
            system_state:
                System mode (e.g. ``"automatic"`` or ``"dynamic"``).
            disposal:
                Enables automatic resource disposal when conduits are
                cleaned.
            disposal_method_names:
                Method names to invoke on created objects during
                disposal.

        Raises:
            RuntimeError:
                If configuration is already locked/cleaned.
            KeyError:
                If an unknown configuration key is provided.
            ValueError:
                If configuration fails validation.
        """
        ...
