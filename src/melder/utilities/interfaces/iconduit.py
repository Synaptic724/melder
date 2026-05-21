from typing import TYPE_CHECKING, Any, ContextManager, Dict, Iterable, Optional, Protocol, Tuple, runtime_checkable
import threading
from types import ModuleType, TracebackType
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconfiguration import IConfiguration
from melder.utilities.interfaces.isafelogger import ISafeLogger
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.synchronization.creation_gate import CreationGate
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)
from melder.utilities.interfaces.ispellbook import ISpellbook

if TYPE_CHECKING:
    from melder.aether.conduit.creations.creations import Creations
    from melder.aether.conduit.meld.meld import Meld

@runtime_checkable
class IConduit(ICleanable, Protocol):
    """
    A Conduit is a modular graph node that behaves like a scope and a factory.

    It can spawn lesser Conduits, link to other Conduits if dynamic mode is enabled,
    and manage the lifecycle of services registered inside itself.
    """
    # Instance-level core attributes (1:1 with Conduit)
    _lock: threading.RLock
    _id: str
    _name: Optional[str]
    __dynamic_environment__: bool
    _aetheric_frame_name: str
    _aetheric_frame: Any
    _spellbook: ISpellbook
    _nexus: Any
    _root_conduit_id: str

    _configuration: 'IConfiguration'
    _logger: 'ISafeLogger'
    _nexus_publish_enabled: bool

    _conduit_state: 'ConduitState'
    _creations: Creations
    _meld: Meld
    _creation_gate: 'CreationGate'
    _creation_gate_controller: 'CreationGateController'

    _conduit_ward: Any

    # ------------------------------------------------------------------
    # Logger configuration
    # ------------------------------------------------------------------

    def _configure_logger(self, logger: Any) -> Any:
        """
        Internal

        Configures the logger for this Conduit.

        Args:
            logger (Any): The explicit logger instance, if one was supplied.
        Returns:
            SafeLogger: The configured SafeLogger instance.
        """
        ...

    def _configure_conduit_state(self) -> None:
        """
        Internal

        Configures the conduit state based on the provided configuration.

        Raises:
            RuntimeError: If normal conduit registration fails.
        """
        ...

    def _register_to_creations(self, spell: ISpell, instance: Any) -> None:
        """
        Register one user-created object into the conduit-owned creations
        manager.
        """
        ...

    def _set_creation_gate_controller_for_lineage(self) -> None:
        """
        Rebind this conduit's creation-gate controller to the current root lineage.
        """
        ...

    # ------------------------------------------------------------------
    # Cleanup and Disposal
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Public API

        Clean up this conduit and all of its lesser conduits.

        Prevents further operation, releases internal references,
        and unregisters from the Aether.
        """
        ...

    def has_live_creation(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> bool:
        """
        Public API

        Resolve a spell through the same identity path as `meld(...)`, but
        only report whether a live creation already exists.

        This method must not create or register new objects.
        """
        ...

    def describe_live_creation_status(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> Dict[str, object]:
        """
        Public API

        Resolve a spell through the same identity path as `meld(...)`, but
        return structured live-creation status for this conduit's query
        context without creating anything new.
        """
        ...

    # ------------------------------------------------------------------
    # Context Management
    # ------------------------------------------------------------------
    def __enter__(self) -> 'IConduit':
        """
        Public API

        Enter the conduit coordination context.

        Returns:
            IConduit: The current conduit instance.
        """
        ...

    def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        """
        Public API

        Exit the conduit coordination context.

        Args:
            exc_type: The exception type, if any.
            exc_value: The exception value, if any.
            traceback: The traceback object, if any.
        """
        ...

    # ------------------------------------------------------------------
    # Logger resolution
    # ------------------------------------------------------------------
    def _resolve_logger_from_config(self, configuration: 'IConfiguration') -> 'ISafeLogger':
        """
        Resolve the logger for this conduit from the provided configuration.

        Args:
            configuration (IConfiguration): The locked system configuration.

        Returns:
            SafeLogger: The resolved SafeLogger instance.
        """
        ...

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Public API

        Return a debug-oriented representation of this conduit instance.
        """
        ...

    def snapshot_state(self) -> Dict[str, Any]:
        """
        Public API

        Build a read-only snapshot of the Conduit state.

        Purpose:
            Provide a stable view of conduit metadata and Spellbook registries
            while transactions may be in-flight.
        Contract:
            - Returns detached copies of metadata and Spellbook snapshot data.
            - Includes a snapshot id for observability.
        Returns:
            Dict[str, Any]: Snapshot payload with conduit metadata and a
            Spellbook snapshot.
        """
        ...

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def id(self) -> str:
        """
        Public API

        Return the unique identifier of this conduit.
        """
        ...

    @property
    def name(self) -> Optional[str]:
        """
        Public API

        Return the human-readable name of this conduit if one has been assigned.
        """
        ...

    @name.setter
    def name(self, name: str) -> None:
        """
        Public API

        Assign a human-readable name to this conduit when naming is still allowed.

        Raises:
            RuntimeError: If the Conduit name is already set.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Configuration
    # ------------------------------------------------------------------
    def _apply_configuration_flags(self) -> None:
        """
        Internal

        Sets the environment mode for this Conduit based on the configuration
        instance passed.
        """
        ...

    def _add_root_conduit(self) -> None:
        """
        Internal

        Add this normal conduit into the current frame's root-conduit state.

        Raises:
            ValueError: If the conduit id or name already exists in the frame.
        """
        ...

    def _remove_root_conduit(self) -> None:
        """
        Internal

        Remove this normal conduit from the current frame's root-conduit state.

        Raises:
            ValueError: If the conduit is not present in the frame.
        """
        ...

    def _creations_configuration(self, configuration: 'IConfiguration') -> Creations:
        """
        Internal

        Returns the current creations configuration for this Conduit.

        Args:
            configuration (IConfiguration): The locked system configuration.

        Returns:
            Creations: The creation manager for this conduit.

        Raises:
            RuntimeError: If the Conduit state is unknown.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Management
    # ------------------------------------------------------------------
    def upgrade_to_normal(
            self,
            name: str,
            *,
            hooks: dict[str, Any] | None = None,
    ) -> None:
        """
        Public API

        Upgrades this Conduit from a lesser to a **normal** state.

        This process allows the conduit to create its own links through the Aether system.
        It effectively forks this conduit into a new tree, retaining its children and
        creation data, and establishes new links with the parent. Only a normal conduit
        can access the Spellbook to bind new spells.

        Please name the conduit if your intention is to add it to the Conduit Cloud.

        Args:
            name (str): An optional name to assign to the upgraded conduit.
            hooks (dict[str, Any] | None, optional): Optional hooks to configure the conduit's behaviour.

        Raises:
            RuntimeError: If the dynamic environment is not enabled.
            RuntimeError: If the current conduit state is not 'lesser'.
        """
        ...

    def set_new_policy(self, policy: str) -> None:
        """
        Public API

        Sets a new policy for this Conduit. This is only allowed in dynamic mode.

        Args:
            policy (str): The new policy to set, governing linking behaviour.

        Raises:
            RuntimeError: If dynamic environment is not enabled.
        """
        ...

    def create_lesser_conduit(self, logger: Any | None = None) -> 'IConduit':
        """
        Public API

        Creates a **lesser Conduit** (child node) attached to this Conduit.

        The lesser conduit inherits the parent's Spellbook and Configuration but is restricted
        in its ability to establish external links or register new spells.

        Returns:
            IConduit: The newly created lesser Conduit instance.

        Raises:
            RuntimeError: If the parent Conduit is cleaned.
        """
        ...

    def get_active_spellspace(self) -> Optional["ISpellSpace"]:
        """
        Return the currently active spellspace for this conduit, if any.

        Returns:
            Optional[ISpellSpace]: Active spellspace or None.
        """
        ...

    def _unregister_spellspace(self, space: "ISpellSpace") -> None:
        """
        Internal

        Remove one spellspace from this conduit's active/runtime tracking.

        Args:
            space: Spellspace being detached from the conduit.

        Returns:
            None.
        """
        ...
    # ------------------------------------------------------------------
    # Spellbook Management API
    # ------------------------------------------------------------------
    def _add_spells_to_aether(self) -> None:
        """
        Internal

        Adds this Conduit's local spell lineages (SpellIndex keys) into the shared
        Aether world's registry.

        Aether is responsible for mapping individual version IDs inside each
        SpellIndex to the owning conduit.

        Raises:
            RuntimeError: If Aether is not initialized.
        """
        ...

    def get_conduit_by_spell_id(
            self,
            spell_id: str,
            aetheric_frame_name: str = "default",
    ) -> Optional['IConduit']:
        """
        Public API

        Retrieves the conduit that has registered a spell with the given spell_id.

        This method queries the Aether to find the original source conduit for a specific spell ID.

        Args:
            spell_id (str): The unique identifier of the spell.
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[IConduit]: The conduit that registered the spell, or None if not found.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def check_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> bool:
        """
        Public API

        Checks if a spell with the given spell_id exists within the global Aether registry.

        Args:
            spell_id (str): The unique identifier of the spell to check (version SHA).
            aetheric_frame_name (str): The Aetheric Frame to search within. Defaults to "default".

        Returns:
            bool: True if the spell exists in the Aether, False otherwise.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_spell_by_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Optional[ISpell]:
        """
        Public API

        Retrieves a spell object by its unique version identifier (spell_id) from the
        spellbook of its owner.

        The method:
          1) Uses Aether to locate the owning conduit.
          2) Searches that conduit's spellbook for a SpellIndex whose lineage contains
             this version ID.
          3) Returns the corresponding ISpell instance if found.

        Args:
            spell_id (str): The unique version identifier of the spell (SHA256).
            aetheric_frame_name (str): The aetheric frame to check against. Defaults to "default".

        Returns:
            Optional[ISpell]: The spell object if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def find_contracted_spell(self, spell_id: str) -> Optional[ISpell]:
        """
        Internal

        Locate a contracted spell by its version spell_id across all peer
        conduits in this Spellbook.

        Args:
            spell_id (str): The unique version ID (SHA) of the spell to find.

        Returns:
            Optional[ISpell]: The contracted spell instance, or None if not found.
        """
        ...

    def get_spell_by_index_id(self, spell_index_id: str) -> Optional[ISpell]:
        """
        Public API

        Retrieves a spell object by its stable SpellIndex lineage id.

        Returns:
            Optional[ISpell]: The spell object if found, otherwise None.
        """
        ...

    def find_spell_id(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[str]:
        """
        Public API

        Finds a spell's current version ID (SHA256 spell_id) using its logical identifiers.

        This now uses:
          1) Spellbook.find_spell_index(...) to locate the SpellIndex lineage.
          2) Spellbook._find_spell(SpellIndex) to retrieve the ISpell.
          3) Returns spell.spell_id (the current head version for that lineage).

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[str]: The current SHA256 identifier of the spell.

        Raises:
            ValueError: If the spell is not found in the spellbook.
        """
        ...

    def find_spell_key(self, spellframe: str, spell_name: str, binding_name: str) -> Optional[tuple]:
        """
        Public API

        Finds a spell's primary lookup key using its logical identifiers.

        The key is typically a tuple used for internal retrieval within the spellbook.

        Args:
            spellframe (str): The logical namespace or grouping label.
            spell_name (str): The name of the spell class or function.
            binding_name (str): The secondary key to distinguish the spell.

        Returns:
            Optional[tuple]: The spell's key (frame, name, binding_name) tuple.

        Raises:
            ValueError: If the spell is not found in the spellbook.
        """
        ...

    def inspect_spell(self, spell: Any, aetheric_frame: str = "default") -> Optional[str]:
        """
        Public API

        Inspects any object to determine if it is a valid, registered spell in the Aether Registry.

        This method uses the Spellbook's internal reflection to identify the spell.

        Args:
            spell (Any): The class, function, or object instance to inspect.
            aetheric_frame (str): The Aetheric Frame to search within. Defaults to "default".

        Returns:
            Optional[str]: The SHA256 unique ID of the spell if found, otherwise None.
        """
        ...

    def describe_spells_in_conduit(self) -> list[dict[str, Any]]:
        """
        Return a user-facing dump of spell-targeting details visible through
        this conduit's Spellbook.
        """
        ...

    def bind(
            self,
            *,
            spell: Any,
            existence: str | Existence,
            permissions: str = "create",
            spellframe: Any = None,
            binding_name: Optional[str] = None,
            profile: str = "general",
            **kwargs: Any,
    ) -> str:
        """
        Binds a spell into the Spellbook for future instantiation and dependency injection.

        The `bind()` method registers a class, function, or object into Melder's system,
        associating it with a lifecycle (`Existence`), a permission policy, and optional metadata.
        Once bound, the spell becomes available for resolution and casting within its conduit
        or across systems (depending on permissions).

        Binding overview:
            - Profiles the spell via reflection.
            - Computes a unique SHA256 `spell_id`.
            - Stores the spell in the internal spell registry.
            - Assigns its lookup key via `(spellframe, binding_name)`.
            - Applies lifecycle and permission policies.
            - Optionally attaches lifecycle hooks.

        Permissions (access control to other conduits):
            - `"read"`:
                Allows other conduits to use the spell but not create new instances.
                Useful for shared utilities or resources.

            - `"create"` (default):
                Allows other conduits to both use and create instances from this spell.

            - `"block"`:
                Completely blocks access to the spell from other conduits.
                Only the owning conduit can use or instantiate it.

        Existence (spell lifecycle):
            Determines how the spell instance is managed (singleton, transient, etc.).
            Use `Existence.unique`, `Existence.many`, etc., for fine-grained control.

        Spellframe (optional):
            Logical namespace or grouping label.
            Often corresponds to a shared interface, protocol, or feature group.

        Binding name (optional):
            Secondary key used to distinguish different versions or roles of the same type.
            Useful when multiple spells are bound under the same interface.

        Lifecycle hooks (optional `**kwargs`):
            - `pre_hooks`: `list[Callable]`
                Executed before the spell is constructed or cast.
                Can be used for validation, preparation, or logging.

            - `activation_hooks`: `list[Callable]`
                Executed during spell construction. Useful for modifying dependencies
                or adapting runtime context.

            - `post_hooks`: `list[Callable]`
                Executed after the spell has been cast. Often used for initialization,
                analytics, or final injection steps.

            All hooks must be callables.

        Args:
            spell (Any): The class, function, or object to bind into the spellbook.
            existence (Existence): The lifecycle scope for this spell.
            permissions (str): Permission level exposed to other conduits ("read",
                "create", "block").
            spellframe (Optional[Any]): Logical interface or category for grouping.
            binding_name (Optional[str]): Name key to distinguish this spell among
                others in its frame.
            profile (str): The profile to use for reflection and metadata.
            **kwargs:
                - pre_hooks (Optional[list[Callable]]): Hooks executed before casting.
                - activation_hooks (Optional[list[Callable]]): Hooks executed during
                  casting/construction.
                - post_hooks (Optional[list[Callable]]): Hooks executed after casting
                  or construction.

        Returns:
            str: The unique SHA256 `spell_id` associated with the bound spell.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If the Conduit is not a 'normal' conduit (only normal conduits
                can bind spells).
            RuntimeError: If no binding transaction is active for this Spellbook.
            RuntimeError: If the spell is already bound in the registry.
            TypeError: If invalid hook types are provided.
        """
        ...

    def scan(self, module: ModuleType) -> list[str]:
        """
        Public API

        Scan a module for `scan_bind`-decorated objects and bind them into this
        Conduit's Spellbook.

        This is a module-only scan: it does not traverse packages or import
        submodules. Any object marked with `scan_bind` must originate from the
        scanned module, otherwise the scan fails.

        Args:
            module (ModuleType): The module to scan for decorated spell targets.
        Returns:
            list[str]: Spell IDs bound during the scan, in module dict order.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If no binding transaction is active for this Spellbook.
            TypeError: If `module` is not a module or metadata is invalid.
            ValueError: If the module does not own a decorated object.
            RuntimeError: Propagated from Spellbook.bind on binding errors.
        """
        ...

    def begin_transaction(
            self,
            transaction_type: "ChangeTransactionType | str",
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable["IConduit"]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Public API

        Begin a change-control transaction for this Conduit.

        Purpose:
            Admit a mutation request through the ChangeControlManager and,
            for bind transactions, open the binding transaction window.
        Contract:
            - Only normal conduits may begin change-control transactions.
            - Admission is serialized by the ChangeControlOrchestrator.
            - Bind transactions open the binding transaction window.
            - Link transactions must explicitly include the local conduit and peers.
            - Link, transfer, mutation, and cluster link require dynamic mode.
        Args:
            transaction_type:
                Transaction type enum or string value (e.g. "bind", "link").
            conduit_ids:
                Optional list of conduits participating in non-link requests.
                Link transactions require explicit conduit objects.
            conduits:
                Optional list of conduit objects participating in the request.
                For link transactions, include the local conduit and peers.
            scope_keys:
                Optional normalized scope keys for conflict checks.
            scope_hashes:
                Optional normalized scope hashes for conflict checks.
            binding_keys:
                Optional binding keys are affected by the request.
            contract_keys:
                Optional contract keys are affected by the request.
            metadata:
                Optional structured metadata for diagnostics.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
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

        End the active change-control transaction for this Conduit.

        Purpose:
            Finalize an admitted change-control request and release any
            implicit embargo state tracked by the ChangeControlManager.
        Contract:
            - Only normal conduits may end change-control transactions.
            - Raises if no change transaction is active.
        Args:
            transaction_type:
                Optional transaction type assertion for safety checks.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If no change transaction is active.
            RuntimeError: If transaction_type does not match the active request.
            ValueError: If transaction_type is invalid.
            TypeError: If transaction_type has an invalid type.
        """
        ...

    def begin_binding_transaction(self) -> None:
        """
        Public API

        Begin a binding transaction for this Conduit.

        Purpose:
            Enable binding operations (bind/scan) through this Conduit.
        Contract:
            - Only normal conduits may begin a binding transaction.
            - Binding transactions must be explicitly ended.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If a binding transaction is already active.
        """
        ...

    def end_binding_transaction(self) -> None:
        """
        Public API

        End the active binding transaction for this Conduit.

        Purpose:
            Disable binding operations until a new transaction is started.
        Contract:
            - Only normal conduits may end a binding transaction.
            - The transaction must be active when ending.
        Returns:
            None.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If no binding transaction is active.
        """
        ...

    def transaction(
            self,
            transaction_type: ChangeTransactionType | str,
            *,
            conduit_ids: Optional[Iterable[str]] = None,
            conduits: Optional[Iterable["IConduit"]] = None,
            scope_keys: Optional[Iterable[str]] = None,
            scope_hashes: Optional[Iterable[str]] = None,
            binding_keys: Optional[Iterable[Tuple[str, str]]] = None,
            contract_keys: Optional[Iterable[Tuple[str, str, str]]] = None,
            metadata: Optional[Dict[str, Any]] = None,
    ) -> ContextManager["IConduit"]:
        """
        Public API

        Context-managed change-control transaction for this Conduit.
        """
        ...

    def binding_transaction(self) -> ContextManager["IConduit"]:
        """
        Public API

        Context-managed binding transaction for this Conduit.

        Contract:
            - Starts a binding transaction on entry.
            - Ends the transaction on exit, even if an exception is raised.
            - Only normal conduits may enter this context.
        Returns:
            ContextManager[IConduit]:
                Context manager yielding the current Conduit instance.
        Raises:
            RuntimeError: If the Conduit is cleaned or not normal.
            RuntimeError: If a binding transaction is already active.
        """
        ...

    def get_spell_permissions(self, spell_id: str) -> Optional[str]:
        """
        Public API

        Get the permissions for a spell by its version spell_id, **within this
        conduit's own spellbook**.

        This returns the access level ("read", "create", "block") defined when the
        spell was bound.

        Args:
            spell_id (str): Version SHA256 identifier of the spell.

        Returns:
            Optional[str]: The permissions associated with the spell's binding.

        Raises:
            RuntimeError: If the spell with the given ID is not found in the spellbook.
        """
        ...

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
        Public API

        Direct spell activation facade for this Conduit.

        At the Conduit boundary, `meld` supports multiple root entry modes.
        Callers may resolve by:

        - `spell` as a **string** (treated as the canonical spell_id), or
        - `spell` as a **spell object** (class/function), or
        - `spellframe` as a **frame/protocol** (or string frame key), or
        - `spell_name` as a **logical name key** (string).

        These inputs are normalized and delegated to the underlying `Meld`
        instance, which resolves a concrete spell_id via SpellInputUtils.

        Resolution, reuse, and lifecycle behaviour are delegated to
        the underlying "Meld" instance.

        Args:
            spell_name:
                Logical spell name (string). When provided without an explicit
                `spell` or `spellframe`, this is treated as the name-based key
                for resolution (via SpellInputUtils normalization).
            spell:
                Primary spell identifier. If a string, this is treated as the
                unique spell_id (typically the SHA256 version ID). If an
                object (class/function), it participates in key normalization.
            spellframe:
                Optional spellframe / protocol / string frame key used for
                resolution. If provided, it becomes the primary frame key.
            binding_name:
                Optional binding name (string) associated with the
                spell. Used as the binding key during resolution.
            spell_override:
                Optional per-call override payload (dict / list / tuple)
                passed through to "Meld.meld" for constructor/factory
                argument overrides.

        Returns:
            Any:
                The resolved component instance (reused or newly
                created) as returned by "Meld.meld".

        Raises:
            RuntimeError:
                - If the Conduit has been cleaned.
                - If the underlying "Meld" instance is missing.
            ValueError:
                - If none of `spell_name`, `spell`, or `spellframe` are provided.
            TypeError:
                - If `spell_name` is not a string when provided.
                - If `binding_name` is not a string when provided.
            KeyError:
                Propagated from "Meld.meld" when a spell_id cannot be
                resolved.
            NotImplementedError:
                Propagated from "Meld.meld" for spell types or
                existence modes not yet implemented.
            HookExecutionError:
                Propagated from "Meld.meld" if hook execution fails.
        """
        ...

    def meld_existing_spell(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
    ) -> Any:
        """
        Public API

        Return an already-existing live object for one resolved spell.

        Args:
            spell_name:
                Logical spell name (string). When provided without an explicit
                `spell` or `spellframe`, this is treated as the name-based key
                for resolution.
            spell:
                Primary spell identifier as spell id string or spell object.
            spellframe:
                Optional spellframe / protocol / string frame key used for
                resolution.
            binding_name:
                Optional binding name associated with the spell.

        Returns:
            Any:
                Existing live runtime object for the resolved spell.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Ward API
    # ------------------------------------------------------------------
    def link(self, target_conduit: 'IConduit') -> bool:
        """
        Public API

        Attempts to establish a link between this Conduit and a `target_conduit`.

        Linking is only allowed if the world is in dynamic mode. This process initiates a contract
        relationship between the two conduits based on the current policy.

        Args:
            target_conduit (IConduit): The target Conduit to link to.

        Returns:
            bool: True if the linking process succeeds.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If a dynamic environment is not enabled.
            TypeError: If `target_conduit` is not an `IConduit` instance.
            RuntimeError: If the target conduit does not have a valid creation context.
        """
        ...

    def sever_link(self, target_conduit: 'IConduit') -> bool:
        """
        Public API

        Sever the link and the corresponding spell contracts between this Conduit and its target Conduit.

        This method validates the link's existence, ensures it can be severed according to policy,
        and removes the link and all contracted spells. This is intended for public use to dissolve a relationship.

        Args:
            target_conduit (IConduit): The target Conduit whose link to sever.

        Returns:
            bool: True if the link was successfully severed.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If a dynamic environment is not enabled.
        """
        ...

    def get_links(self) -> list['IConduit']:
        """
        Public API

        Return all active peer links associated with this conduit.

        This list excludes links to lesser (child) conduits.

        Returns:
            list[IConduit]: Linked peer conduits.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If a dynamic environment is not enabled.
        """
        ...

    def get_lesser_conduit(self, conduit_id: str) -> Optional['IConduit']:
        """
        Public API

        Return one specific lesser conduit (child) by id.

        Args:
            conduit_id (str): The ID of the lesser conduit to retrieve.

        Returns:
            Optional[IConduit]: The linked lesser conduit if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_initiated_conduit(self, conduit_id: str) -> Optional['IConduit']:
        """
        Public API

        Retrieves the conduit that this conduit has initiated a contract *toward*.

        This method uses the internal index to resolve an outbound connection,
        where this conduit was the **initiator** of the contract.

        Args:
            conduit_id (str): The ID of the target conduit this conduit linked to.

        Returns:
            Optional[IConduit]: The target conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_provider_conduit(self, conduit_id: str) -> Optional['IConduit']:
        """
        Public API

        Retrieves the conduit that initiated a contract *to this* conduit.

        This method uses the internal index to resolve an inbound connection,
        where another conduit linked to this one as the **provider**.

        Args:
            conduit_id (str): The ID of the source conduit that linked to this one.

        Returns:
            Optional[IConduit]: The source conduit if the link exists, otherwise None.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_initiated_conduits(self) -> list['IConduit']:
        """
        Public API

        Return all conduits that this conduit has initiated contracts toward.

        This is useful for understanding the dependencies and relationships initiated by this conduit.

        Returns:
            list[IConduit]: Outbound-linked conduits.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def get_provider_conduits(self) -> list['IConduit']:
        """
        Public API

        Return all conduits that have initiated contracts to this conduit.

        These are the conduits that depend on this one for contracted spells.

        Returns:
            list[IConduit]: Inbound provider conduits.

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    def cleanup_lesser_conduits(self) -> None:
        """
        Public API

        Clean up all lesser conduits (children) linked to this conduit.

        This prevents further operations on lesser conduits and is typically used when the parent
        is cleaning or undergoing a major state change (e.g., upgrade).

        Raises:
            RuntimeError: If the Conduit is cleaned.
        """
        ...

    # ------------------------------------------------------------------
    # Conduit Resolution Validation API
    # ------------------------------------------------------------------
    def get_resolution_state(self) -> Optional[ConduitResolutionState]:
        """
        Public API

        Return the per-conduit resolution state for this conduit.

        Purpose:
            Expose conduit-scoped Phase 5-7 validity and diagnostics without
            running validation.
        Contract:
            - Does not mutate or revalidate; returns existing state only.
            - Lesser conduits resolve state via their root conduit id.
            - Returns None when no resolution state has been recorded.
        Returns:
            Optional[IConduitResolutionState]:
                Resolution state for this conduit (or its root), if present.
        Raises:
            RuntimeError: If the conduit is cleaned or the root conduit is unavailable.
            RuntimeError: If the Spellbook is not available on this conduit.
        Threading:
            Implementations should resolve identity under conduit locks and
            rely on SpellSystemStates for state-level synchronization.
        """
        ...

    def validate_resolution(self, *, refresh_structural: bool = True) -> Optional[ConduitResolutionState]:
        """
        Public API

        Run structural and conduit-scoped resolution validation, then return the state.

        Purpose:
            Provide an explicit preflight validation hook after linking or
            contracting spells so callers can confirm readiness.
        Contract:
            - When refresh_structural is True, runs structural phases (1-4) first.
            - Always runs resolution phases (5-7) for this conduit scope.
            - Returns the conduit-scoped resolution state after validation.
        Args:
            refresh_structural:
                Whether to run structural validation before conduit validation.
        Returns:
            Optional[IConduitResolutionState]:
                Resolution state for this conduit (or its root), if present.
        Raises:
            RuntimeError: If the conduit is cleaned or the root conduit is unavailable.
            RuntimeError: If the Spellbook or SpellSystemStates are unavailable.
            SpellbookValidationError:
                Propagated if structural or resolution validation fails.
        Threading:
            Implementations should avoid holding conduit locks while executing
            phase pipelines to prevent long-held lock contention.
        """
        ...

    # ------------------------------------------------------------------
    # Spell Contracting API
    # ------------------------------------------------------------------
    def _qualify_contracts(self) -> None:
        """
        Internal

        Performs checks to ensure the conduit is in a state capable of managing spell contracts.

        Raises:
            RuntimeError: If the Conduit is cleaned.
            RuntimeError: If the Conduit is not a 'normal' conduit.
            RuntimeError: If a dynamic environment is not enabled.
        """
        ...

    def add_spell_to_contract(
            self,
            *,
            spell: Optional[ISpell] = None,
            spell_id: Optional[str] = None,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: Any = None,
            root_spell_id: str | None = None,
            link_dependencies: bool = False,
    ) -> bool | None:
        """
        Public API

        Establishes a single spell contract between this conduit and another target conduit.

        This allows one conduit to borrow or grant a specific spell, identified either by object or ID,
        to/from a peer conduit. The contract defines the permissions under which the spell can be used.

        You must provide either a `spell` object or a `spell_id`. The target conduit must be specified
        either directly or resolved via its ID and aetheric frame. Contract mutations require an
        active link transaction that includes both conduits.

        Args:
            spell (ISpell, optional): The spell object to contract.
            spell_id (str, optional): The unique ID of the spell to contract.
            conduit (IConduit, optional): The target conduit to contract with.
            conduit_id (str, optional): The str of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level granted for this spell (default is "create").
            aetheric_frame (str): Optional frame override is used to locate the target conduit.
            reason (Any, optional): Optional reason for the contract.
            link_dependencies (bool, optional): Whether to link dependencies for the contract.
            root_spell_id (str, optional): The root spell ID for the contract.

        Returns:
            bool | None: True if the contract was created, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def add_spells_to_contract(
            self,
            spell_ids: list[str],
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
            reason: Any = None,
            link_dependencies: bool = False,
    ) -> dict:
        """
        Public API

        Establishes multiple spell contracts with another conduit in a single operation.

        Allows you to bulk-grant or bulk-borrow spells by specifying a list of spell IDs. Each spell
        will be contracted using the same permission level.

        Args:
            spell_ids (list[str]): List of spell IDs to contract.
            conduit (IConduit, optional): The target conduit to contract with.
            conduit_id (str, optional): The id of the target conduit (used if `conduit` is not provided).
            permissions (str): The permission level is granted for all spells (default is "create").
            aetheric_frame (str): Optional frame override is used to locate the target conduit.
            reason (Any, optional): Optional reason for the contract.
            link_dependencies (bool, optional): Whether to link dependencies for the contract.

        Returns:
            dict: Dictionary of `spell_id` -> success boolean for each attempted contract.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def remove_spell_from_contract(
            self,
            *,
            spell: Optional[ISpell] = None,
            spell_id: Optional[str] = None,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            root_spell_id: str | None = None,
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Public API

        Removes a single spell contract between this conduit and another.

        Either the `spell` or `spell_id` can be provided to specify the contract to dissolve.
        Once removed, the spell is no longer accessible across the link.

        Args:
            spell (ISpell, optional): The spell object to remove.
            spell_id (str, optional): The unique ID of the spell to remove.
            conduit (IConduit, optional): The target conduit involved in the contract.
            conduit_id (str, optional): id of the target conduit (used if `conduit` not provided).
            root_spell_id (str, optional): If provided, only removes the source reference for this root.
            aetheric_frame (str): Optional frame override to resolve the target conduit.

        Returns:
            bool | None: True if the spell was successfully removed from the contract, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def remove_spells_from_contract(
            self,
            *,
            spell_ids: Optional[list[str]] = None,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            root_spell_id: str | None = None,
            aetheric_frame: str = "default",
    ) -> dict:
        """
        Public API

        Removes multiple spells from an existing contract with a target conduit.

        Useful for bulk cleanup or revocation when retiring behaviours or permissions.

        Args:
            spell_ids (list[str], optional): List of spell IDs to remove.
            conduit (IConduit, optional): Target conduit object.
            conduit_id (str, optional): str of target conduit (used if `conduit` is not provided).
            root_spell_id (str, optional): If provided, only removes the source reference for this root.
            aetheric_frame (str): Optional frame override.

        Returns:
            dict: Dictionary of `spell_id` -> success boolean for each removal attempt.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def remove_root_from_contracts(self, *, root_spell_id: str, conduit: Optional['IConduit'] = None,
                                   conduit_id: Optional[str] = None, aetheric_frame: str = "default") -> dict:
        """
        Public API

        Removes a root spell_id (and any dependency Details attributed to it) from one
        contract or all contracts. Orphaned Details trigger contracted spell removal;
        empty contracts are severed.

        Contract mutations require an active link transaction that includes the
        borrower and the peer conduits involved in the contract cleanup.
        """
        ...

    def add_spell_to_contract_with_dependencies(
            self,
            *,
            spell: Optional[ISpell] = None,
            spell_id: Optional[str] = None,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            permissions: str = "create",
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Public API helper

        Adds a spell to a contract and automatically links its dependencies
        (recursively) using the same permission level (downgraded to read when needed).
        """
        ...

    def _remove_all_spells_from_contract(
            self,
            *,
            conduit: Optional['IConduit'] = None,
            conduit_id: Optional[str] = None,
            aetheric_frame: str = "default",
    ) -> bool | None:
        """
        Public API

        Dissolves **all** spell contracts between this conduit and the specified target.

        All borrowed and granted spells in the active contract will be severed, effectively
        resetting the spell relationship between the two conduits.

        Args:
            conduit (IConduit, optional): Target conduit object.
            conduit_id (str, optional): str of target conduit (used if `conduit` is not provided).
            aetheric_frame (str): Optional frame override.

        Returns:
            bool | None: True if all spells were successfully removed, False otherwise. None if an internal error occurs.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
            RuntimeError: If no active link transaction is present for this contract mutation.
        """
        ...

    def get_all_spells_in_contracts(
            self,
            validate: bool = True,
    ) -> Optional[dict[str, list[Tuple[str, ISpell]]]]:
        """
        Public API

        Retrieves all active spells that this conduit has access to through its contracts (i.e., borrowed spells).

        Walks all current spell contracts and collects the spell IDs and objects that are currently
        borrowed from other conduits. Optionally validates contracts before collecting data.

        Args:
            validate (bool): If True, performs contract consistency validation before returning data.

        Returns:
            Optional[dict[str, list[Tuple[str, ISpell]]]]: Dictionary mapping peer conduit ids to lists of (spell_id, ISpell) tuples,
            or None if no contracts exist.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `validate` is not a boolean.
        """
        ...

    def get_spell_in_contracts(self, spell_id: str) -> Optional[tuple[str, ISpell]]:
        """
        Public API

        Searches all known contracts to find the origin of a specific contracted spell.

        Looks for a specific spell by ID and returns the str of the conduit it's contracted from
        along with the spell object, if found.

        Args:
            spell_id (str): The unique ID of the spell.

        Returns:
            Optional[tuple[str, ISpell]]: Tuple of (`conduit_id`, `spell`) if found, otherwise None.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `spell_id` is not a string.
        """
        ...

    def get_spells_in_contract_by_conduit(
            self,
            conduit_id: str,
    ) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a specific peer conduit, identified by id.

        Returns a detailed list of all spells that this conduit currently accesses or has granted
        through its relationship with the specified peer.

        Args:
            conduit_id (str): id of the target peer conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `ISpell`) tuples or None
            if not found. When a contract exists but contains no spells, inbound/outbound lists are empty.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `conduit_id` is not a str.
        """
        ...

    def get_spells_in_contract_by_conduit_name(
            self,
            conduit_name: str,
    ) -> dict[str, list[tuple[str, ISpell]]] | None:
        """
        Public API

        Retrieves all spell contracts associated with a peer conduit identified by name.

        Performs resolution using a human-readable name instead of str.

        Args:
            conduit_name (str): Name of the peer conduit.

        Returns:
            dict[str, list[tuple[str, ISpell]]] | None: Dictionary of `spell_id` -> (`spell_id`, `ISpell`) tuples or None if not found.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
            TypeError: If `conduit_name` is not a string.
        """
        ...

    def get_contracted_conduits(self) -> list[Tuple[str, 'IConduit']] | None:
        """
        Public API

        Return all conduits that have an active spell contract with this conduit.

        Each returned conduit represents a peer in the current dynamic spell network.

        Returns:
            list[tuple[str, IConduit]] | None:
                List of "(conduit_id, conduit)" tuples, or "None" when no
                contracts exist.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
        """
        ...

    def _describe_contract(self, conduit_id: str) -> dict:
        """
        Public API

        Return a detailed diagnostic summary of one contract by conduit id.

        This method inspects the contract associated with the provided `conduit_id` and returns metadata
        including the peer conduit's name, the number of active spells involved, and permission levels.
        Primarily used for debugging, introspection, and UI inspection tools.

        Args:
            conduit_id (str): str of the peer conduit whose contract you wish to examine.

        Returns:
            dict: Contract metadata payload, including spells and permissions.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
        """
        ...

    def validate_contracts_and_define(self) -> dict[str, bool]:
        """
        Public API

        Validate all known contracts attached to this conduit.

        This performs a deep validation pass, ensuring both sides list the same spells, permissions are symmetrical,
        and all referenced spells are valid.

        Returns:
            dict[str, bool]:
                Mapping of contract ids to validation results.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
        """
        ...

    def validate_received_contracts(self) -> bool:
        """
        Public API

        Perform a high-level validation check across all contracts involving this conduit.

        Aggregates the results of `_validate_contracts_and_define` to determine whether every connected
        contract is structurally valid and symmetrical.

        Returns:
            bool: True if all active contracts pass validation, False otherwise.

        Raises:
            RuntimeError: If the Conduit fails, contract qualification checks (cleaned, not normal, not dynamic).
        """
        ...

    # ------------------------------------------------------------------
    # Mutation Research
    # ------------------------------------------------------------------


from melder.utilities.interfaces.ispellspace import ISpellSpace
