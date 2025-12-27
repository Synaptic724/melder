import threading
from typing import Any, Optional, Tuple
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellSymbolicDependency(Cleanable):
    """
    Phase 2 representation of a **single constructor socket** for a spell.

    Conceptually:

        “For spell version V, parameter P has DI shape X and wants type T
        (or SpellMap M).”

    This is a *symbolic* socket, not yet tied to concrete spell IDs. Later phases
    (local frame / DAG builder) will interpret these sockets against the Spellbook.

    Identity
    --------
    ``spell_id`` here is the **versioned identity** of the owning spell:

        ``spell.spell_index.current``

    Fields
    ------
    spell_id:
        Versioned identity (string) of the owning spell.

    param_name:
        Parameter name on the call target.

    position:
        0-based positional index of the parameter in the signature.

    di_shape:
        High-level DI shape from :class:`ParameterDIShape`.

    is_optional:
        True if the parameter is logically optional from a DI perspective
        (e.g., Optional/T|None, or has a default).

    target_annotation:
        For SINGLE/COLLECTION shapes, the annotation (or element annotation)
        used as the DI key in later phases (class, Protocol, string, etc.).
        For PLAIN shapes, this records the raw annotation (often a builtin
        type or None) for diagnostics and override targeting.

    is_collection:
        True if this dependency represents a collection-of-implementations
        requirement (e.g., ``list[IMyHandler]``).

    spellmap_default:
        For SPELLMAP_DEFAULT shape, the original :class:`SpellMap` default
        instance attached to the parameter.

    contract_key:
        For SPELL_CONTRACT and MUTATION_CONTRACT shapes, the canonical
        ``(frame_key, binding_key)`` derived from the contract object.

    contract_late_binding:
        For MUTATION_CONTRACT shapes, whether the contract declares
        late binding semantics. For all other shapes, this is None.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_id",
        "_param_name",
        "_position",
        "_di_shape",
        "_is_optional",
        "_target_annotation",
        "_is_collection",
        "_spellmap_default",
        "_contract_key",
        "_contract_late_binding",
    ]

    def __init__(
            self,
            *,
            spell_version_id: str,
            param_name: str,
            position: int,
            di_shape: ParameterDIShape,
            is_optional: bool,
            target_annotation: Any,
            is_collection: bool,
            spellmap_default: Any = None,
            contract_key: Optional[Tuple[str, str]] = None,
            contract_late_binding: Optional[bool] = None,
    ) -> None:
        super().__init__()

        if not spell_version_id:
            raise ValueError("spell_version_id must be a non-empty string.")
        if not param_name:
            raise ValueError("param_name must be a non-empty string.")

        self._lock: threading.RLock = threading.RLock()

        # Stored as _spell_id for backwards compatibility; semantically this is
        # the *version id* (SpellIndex.current).
        self._spell_id: str = spell_version_id
        self._param_name: str = param_name
        self._position: int = position
        self._di_shape: ParameterDIShape = di_shape
        self._is_optional: bool = is_optional
        self._target_annotation: Any = target_annotation
        self._is_collection: bool = is_collection
        self._spellmap_default: Any = spellmap_default
        self._contract_key: Optional[Tuple[str, str]] = contract_key
        self._contract_late_binding: Optional[bool] = contract_late_binding

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this dependency edge.

        This only drops references; it does not affect any external graph
        or Spellbook state.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._spell_id = None
            self._param_name = None
            self._position = -1
            self._di_shape = None
            self._is_optional = False
            self._target_annotation = None
            self._is_collection = False
            self._spellmap_default = None
            self._contract_key = None
            self._contract_late_binding = None
            self._cleaned = True

        self._lock = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def spell_id(self) -> str:
        """
        Versioned identity of the owning spell (SpellIndex.current).
        """
        self.check_cleaned()
        return self._spell_id

    @property
    def param_name(self) -> str:
        """
        Parameter name on the call target.
        """
        self.check_cleaned()
        return self._param_name

    @property
    def position(self) -> int:
        """
        0-based positional index in the call target's signature.
        """
        self.check_cleaned()
        return self._position

    @property
    def di_shape(self) -> ParameterDIShape:
        """
        High-level DI shape (SINGLE, COLLECTION, SPELLMAP_DEFAULT).
        """
        self.check_cleaned()
        return self._di_shape

    @property
    def is_optional(self) -> bool:
        """
        True if the parameter is logically optional from a DI perspective.
        """
        self.check_cleaned()
        return self._is_optional

    @property
    def target_annotation(self) -> Any:
        """
        Effective DI target annotation (or element annotation for collections).

        May be:
            * A concrete class
            * A Protocol/interface type
            * A string (to be resolved later)
            * None for SpellMap-default-based dependencies
        """
        self.check_cleaned()
        return self._target_annotation

    @property
    def is_collection(self) -> bool:
        """
        True if this dependency represents a collection-of-implementations DI
        requirement (e.g., list[IMyHandler]).
        """
        self.check_cleaned()
        return self._is_collection

    @property
    def spellmap_default(self) -> Any:
        """
        If ``di_shape`` is SPELLMAP_DEFAULT, this holds the default SpellMap
        instance; otherwise this is None.
        """
        self.check_cleaned()
        return self._spellmap_default

    @property
    def contract_key(self) -> Optional[Tuple[str, str]]:
        """
        Canonical ``(frame_key, binding_key)`` for contract sockets.

        For SPELL_CONTRACT and MUTATION_CONTRACT shapes, this is derived from
        the contract descriptor. For all other shapes, this is None.
        """
        self.check_cleaned()
        return self._contract_key

    @property
    def contract_late_binding(self) -> Optional[bool]:
        """
        Late-binding flag for mutation contracts.

        Returns:
            Optional[bool]:
                True/False for MUTATION_CONTRACT sockets, otherwise None.
        """
        self.check_cleaned()
        return self._contract_late_binding
