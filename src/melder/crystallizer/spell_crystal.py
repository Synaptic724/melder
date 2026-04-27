import threading
from typing import Any, Dict, List, Mapping, Optional, Sequence

from melder.utilities.general_base.cleanable import Cleanable


class SpellCrystal(Cleanable):
    """
    Persisted source-bearing representation for one crystallized spell asset.

    `SpellCrystal` is the smallest stored unit that Crystallizer owns directly.
    It preserves the source/module truth needed to identify, inspect, persist,
    and later restore one spell-backed asset without requiring the live runtime
    object to remain present.

    Contract:
    - `spell_crystal_id` is the stable crystal identity.
    - `source_text` and `source_sha256` describe the current persisted source.
    - import/export/dependency metadata is derived state and may be updated as
      analysis improves.
    - `spell_crystal_active` reflects whether this crystal is currently
      attached to one live spell registration in the process.
    - active runtime metadata is process-local and may be cleared without
      changing the crystal identity.
    - cleanup is deterministic and renders the object unusable afterward.
    """

    def __init__(
            self,
            spell_crystal_id: str,
            module_name: str,
            source_text: str,
            source_sha256: str,
            binding_signature: str,
            source_authority_kind: str,
            target_kind: str,
            target_qualname: str,
            ast_imports: Optional[Sequence[str]] = None,
            ast_from_imports: Optional[Mapping[str, Sequence[str]]] = None,
            export_names: Optional[Sequence[str]] = None,
            internal_dependency_names: Optional[Sequence[str]] = None,
            external_dependency_names: Optional[Sequence[str]] = None,
            physical_file_path: Optional[str] = None,
            materialized_directory_path: Optional[str] = None,
            spell_crystal_active: bool = False,
            active_frame_name: Optional[str] = None,
            active_conduit_name: Optional[str] = None,
            active_spellbook_name: Optional[str] = None,
            active_spell_id: Optional[str] = None,
            active_spell_index_id: Optional[str] = None,
    ) -> None:
        """
        Initialize one persisted crystallized asset record.

        Args:
            spell_crystal_id:
                Stable crystal identifier.
            module_name:
                Canonical module or synthetic module name for the asset.
            source_text:
                Current persisted source representation.
            source_sha256:
                SHA256 fingerprint of `source_text`.
            binding_signature:
                Spell-provided binding-signature string used to reconnect the
                asset to spell registration semantics later.
            source_authority_kind:
                Declares where the authoritative source comes from, such as
                `synthetic` or `physical`.
            target_kind:
                High-level kind for the primary target, such as `class`,
                `function`, or `runtime_object`.
            target_qualname:
                Qualified name of the primary target within the module source.
            ast_imports:
                Direct `import ...` statements discovered by analysis.
            ast_from_imports:
                Mapping of `from module import names` discovered by analysis.
            export_names:
                Exported names or detected public surface names.
            internal_dependency_names:
                Dependency names considered managed/internal to the system.
            external_dependency_names:
                Dependency names considered environment/external support.
            physical_file_path:
                Optional physical module file backing this crystal.
            materialized_directory_path:
                Optional directory path where the source has been materialized.
            spell_crystal_active:
                True when the crystal is currently attached to one live spell
                registration in this process.
            active_frame_name:
                Frame name for the active live registration, if any.
            active_conduit_name:
                Conduit name for the active live registration, if any.
            active_spellbook_name:
                Spellbook name/identity for the active live registration, if
                any.
            active_spell_id:
                SHA256 spell identity for the active registration, if any.
            active_spell_index_id:
                Stable spell-lineage identity for the active registration, if
                any.

        Raises:
            ValueError:
                If any required identity or source field is empty.
        """
        super().__init__()

        if not spell_crystal_id:
            raise ValueError("spell_crystal_id must not be empty.")
        if not module_name:
            raise ValueError("module_name must not be empty.")
        if not source_text:
            raise ValueError("source_text must not be empty.")
        if not source_sha256:
            raise ValueError("source_sha256 must not be empty.")
        if not binding_signature:
            raise ValueError("binding_signature must not be empty.")
        if not source_authority_kind:
            raise ValueError("source_authority_kind must not be empty.")
        if not target_kind:
            raise ValueError("target_kind must not be empty.")
        if not target_qualname:
            raise ValueError("target_qualname must not be empty.")

        self._lock: Optional[threading.RLock] = threading.RLock()

        self._spell_crystal_id: Optional[str] = spell_crystal_id
        self._module_name: Optional[str] = module_name
        self._source_text: Optional[str] = source_text
        self._source_sha256: Optional[str] = source_sha256
        self._binding_signature: Optional[str] = binding_signature
        self._source_authority_kind: Optional[str] = source_authority_kind
        self._target_kind: Optional[str] = target_kind
        self._target_qualname: Optional[str] = target_qualname

        self._ast_imports: Optional[List[str]] = (
            list(ast_imports) if ast_imports is not None else []
        )
        self._ast_from_imports: Optional[Dict[str, List[str]]] = (
            self._copy_from_imports(ast_from_imports)
        )
        self._export_names: Optional[List[str]] = (
            list(export_names) if export_names is not None else []
        )
        self._internal_dependency_names: Optional[List[str]] = (
            list(internal_dependency_names)
            if internal_dependency_names is not None
            else []
        )
        self._external_dependency_names: Optional[List[str]] = (
            list(external_dependency_names)
            if external_dependency_names is not None
            else []
        )

        self._physical_file_path: Optional[str] = physical_file_path
        self._materialized_directory_path: Optional[str] = materialized_directory_path

        self._spell_crystal_active: bool = spell_crystal_active
        self._active_frame_name: Optional[str] = active_frame_name
        self._active_conduit_name: Optional[str] = active_conduit_name
        self._active_spellbook_name: Optional[str] = active_spellbook_name
        self._active_spell_id: Optional[str] = active_spell_id
        self._active_spell_index_id: Optional[str] = active_spell_index_id

    def cleanup(self) -> None:
        """
        Tear down the crystal record and mark it cleaned.

        Cleanup contract:
        - idempotent
        - clears owned metadata collections
        - clears runtime projection metadata
        - drops the lock reference last
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._spell_crystal_id = None
            self._module_name = None
            self._source_text = None
            self._source_sha256 = None
            self._binding_signature = None
            self._source_authority_kind = None
            self._target_kind = None
            self._target_qualname = None
            self._ast_imports = None
            self._ast_from_imports = None
            self._export_names = None
            self._internal_dependency_names = None
            self._external_dependency_names = None
            self._physical_file_path = None
            self._materialized_directory_path = None
            self._spell_crystal_active = False
            self._active_frame_name = None
            self._active_conduit_name = None
            self._active_spellbook_name = None
            self._active_spell_id = None
            self._active_spell_index_id = None
            self._lock = None

    @staticmethod
    def _copy_from_imports(
            ast_from_imports: Optional[Mapping[str, Sequence[str]]],
    ) -> Dict[str, List[str]]:
        """
        Copy `from ... import ...` metadata into an owned mutable structure.

        Args:
            ast_from_imports:
                Optional mapping from module path to imported names.

        Returns:
            Dict[str, List[str]]:
                Deep-copied mapping owned by this crystal instance.
        """
        if ast_from_imports is None:
            return {}
        return {
            module_name: list(import_names)
            for module_name, import_names in ast_from_imports.items()
        }

    @property
    def spell_crystal_id(self) -> str:
        """
        Return the stable crystal identity.

        Returns:
            str:
                Stable `SpellCrystal` identifier.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_crystal_id

    @property
    def module_name(self) -> str:
        """
        Return the canonical module name for this crystal.

        Returns:
            str:
                Synthetic or physical module name for the asset.
        """
        self.check_cleaned()
        with self._lock:
            return self._module_name

    @property
    def source_text(self) -> str:
        """
        Return the current persisted source representation.

        Returns:
            str:
                Current source text owned by this crystal.
        """
        self.check_cleaned()
        with self._lock:
            return self._source_text

    @property
    def source_sha256(self) -> str:
        """
        Return the persisted SHA256 fingerprint of the current source.

        Returns:
            str:
                SHA256 fingerprint for `source_text`.
        """
        self.check_cleaned()
        with self._lock:
            return self._source_sha256

    @property
    def binding_signature(self) -> str:
        """
        Return the persisted binding-signature string.

        Returns:
            str:
                Spell-provided binding signature for restore/rebind flows.
        """
        self.check_cleaned()
        with self._lock:
            return self._binding_signature

    @property
    def source_authority_kind(self) -> str:
        """
        Return the high-level source-authority kind.

        Returns:
            str:
                Authority kind such as `synthetic` or `physical`.
        """
        self.check_cleaned()
        with self._lock:
            return self._source_authority_kind

    @property
    def target_kind(self) -> str:
        """
        Return the primary target classification for this crystal.

        Returns:
            str:
                High-level target kind carried by the crystal.
        """
        self.check_cleaned()
        with self._lock:
            return self._target_kind

    @property
    def target_qualname(self) -> str:
        """
        Return the primary qualified target name for this crystal.

        Returns:
            str:
                Qualified target name used to identify the asset surface.
        """
        self.check_cleaned()
        with self._lock:
            return self._target_qualname

    @property
    def ast_imports(self) -> List[str]:
        """
        Return the direct import-statement metadata for this crystal.

        Returns:
            List[str]:
                Copy of direct `import ...` names discovered by analysis.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._ast_imports)

    @property
    def ast_from_imports(self) -> Dict[str, List[str]]:
        """
        Return the `from ... import ...` metadata for this crystal.

        Returns:
            Dict[str, List[str]]:
                Deep-copied mapping from module path to imported names.
        """
        self.check_cleaned()
        with self._lock:
            return self._copy_from_imports(self._ast_from_imports)

    @property
    def export_names(self) -> List[str]:
        """
        Return the persisted export/public-surface names.

        Returns:
            List[str]:
                Copy of the detected export names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._export_names)

    @property
    def internal_dependency_names(self) -> List[str]:
        """
        Return the managed/internal dependency names for this crystal.

        Returns:
            List[str]:
                Copy of internal dependency names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._internal_dependency_names)

    @property
    def external_dependency_names(self) -> List[str]:
        """
        Return the external/environment dependency names for this crystal.

        Returns:
            List[str]:
                Copy of external dependency names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._external_dependency_names)

    @property
    def physical_file_path(self) -> Optional[str]:
        """
        Return the physical source file path, if one exists.

        Returns:
            Optional[str]:
                Physical file path backing this crystal, if any.
        """
        self.check_cleaned()
        with self._lock:
            return self._physical_file_path

    @property
    def materialized_directory_path(self) -> Optional[str]:
        """
        Return the materialized directory path, if one exists.

        Returns:
            Optional[str]:
                Directory path where the crystal has been materialized, if any.
        """
        self.check_cleaned()
        with self._lock:
            return self._materialized_directory_path

    @property
    def spell_crystal_active(self) -> bool:
        """
        Return whether this crystal is currently active in the live process.

        Returns:
            bool:
                True when one live spell registration currently consumes the
                crystal in this process.
        """
        self.check_cleaned()
        with self._lock:
            return self._spell_crystal_active

    @property
    def active_frame_name(self) -> Optional[str]:
        """
        Return the active frame name, if the crystal is live.

        Returns:
            Optional[str]:
                Active frame name for the live registration.
        """
        self.check_cleaned()
        with self._lock:
            return self._active_frame_name

    @property
    def active_conduit_name(self) -> Optional[str]:
        """
        Return the active conduit name, if the crystal is live.

        Returns:
            Optional[str]:
                Active conduit name for the live registration.
        """
        self.check_cleaned()
        with self._lock:
            return self._active_conduit_name

    @property
    def active_spellbook_name(self) -> Optional[str]:
        """
        Return the active spellbook identity, if the crystal is live.

        Returns:
            Optional[str]:
                Active spellbook name/identity for the live registration.
        """
        self.check_cleaned()
        with self._lock:
            return self._active_spellbook_name

    @property
    def active_spell_id(self) -> Optional[str]:
        """
        Return the active SHA256 spell id, if the crystal is live.

        Returns:
            Optional[str]:
                Active spell identity for the live registration.
        """
        self.check_cleaned()
        with self._lock:
            return self._active_spell_id

    @property
    def active_spell_index_id(self) -> Optional[str]:
        """
        Return the active spell-lineage id, if the crystal is live.

        Returns:
            Optional[str]:
                Active spell index id for the live registration.
        """
        self.check_cleaned()
        with self._lock:
            return self._active_spell_index_id

    def update_source_text(self, source_text: str, source_sha256: str) -> None:
        """
        Replace the persisted source text and hash for this crystal.

        Args:
            source_text:
                Replacement source representation.
            source_sha256:
                SHA256 fingerprint for the replacement source.

        Raises:
            ValueError:
                If either value is empty.
            RuntimeError:
                If the crystal has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if not source_text:
                raise ValueError("source_text must not be empty.")
            if not source_sha256:
                raise ValueError("source_sha256 must not be empty.")

            self._source_text = source_text
            self._source_sha256 = source_sha256

    def update_analysis(
            self,
            ast_imports: Optional[Sequence[str]] = None,
            ast_from_imports: Optional[Mapping[str, Sequence[str]]] = None,
            export_names: Optional[Sequence[str]] = None,
            internal_dependency_names: Optional[Sequence[str]] = None,
            external_dependency_names: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Replace the derived import/export/dependency metadata for this crystal.

        Args:
            ast_imports:
                Replacement direct import list, if provided.
            ast_from_imports:
                Replacement `from ... import ...` mapping, if provided.
            export_names:
                Replacement export/public-surface names, if provided.
            internal_dependency_names:
                Replacement managed/internal dependency names, if provided.
            external_dependency_names:
                Replacement external/environment dependency names, if provided.

        Raises:
            RuntimeError:
                If the crystal has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if ast_imports is not None:
                self._ast_imports = list(ast_imports)
            if ast_from_imports is not None:
                self._ast_from_imports = self._copy_from_imports(ast_from_imports)
            if export_names is not None:
                self._export_names = list(export_names)
            if internal_dependency_names is not None:
                self._internal_dependency_names = list(internal_dependency_names)
            if external_dependency_names is not None:
                self._external_dependency_names = list(external_dependency_names)

    def set_materialization_location(
            self,
            physical_file_path: Optional[str],
            materialized_directory_path: Optional[str],
    ) -> None:
        """
        Update the materialized filesystem location metadata for this crystal.

        Args:
            physical_file_path:
                Physical module file path, if one exists.
            materialized_directory_path:
                Materialized directory location, if one exists.

        Raises:
            RuntimeError:
                If the crystal has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._physical_file_path = physical_file_path
            self._materialized_directory_path = materialized_directory_path

    def activate(
            self,
            frame_name: str,
            conduit_name: str,
            spellbook_name: str,
            spell_id: str,
            spell_index_id: str,
    ) -> None:
        """
        Mark this crystal as actively consumed by one live spell registration.

        Args:
            frame_name:
                Active frame name for the live registration.
            conduit_name:
                Active conduit name for the live registration.
            spellbook_name:
                Active spellbook identity for the live registration.
            spell_id:
                Active SHA256 spell identity.
            spell_index_id:
                Active stable spell-lineage identity.

        Raises:
            ValueError:
                If any required runtime identity value is empty.
            RuntimeError:
                If the crystal has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if not frame_name:
                raise ValueError("frame_name must not be empty.")
            if not conduit_name:
                raise ValueError("conduit_name must not be empty.")
            if not spellbook_name:
                raise ValueError("spellbook_name must not be empty.")
            if not spell_id:
                raise ValueError("spell_id must not be empty.")
            if not spell_index_id:
                raise ValueError("spell_index_id must not be empty.")

            self._spell_crystal_active = True
            self._active_frame_name = frame_name
            self._active_conduit_name = conduit_name
            self._active_spellbook_name = spellbook_name
            self._active_spell_id = spell_id
            self._active_spell_index_id = spell_index_id

    def deactivate(self) -> None:
        """
        Clear the live runtime projection metadata for this crystal.

        Raises:
            RuntimeError:
                If the crystal has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._spell_crystal_active = False
            self._active_frame_name = None
            self._active_conduit_name = None
            self._active_spellbook_name = None
            self._active_spell_id = None
            self._active_spell_index_id = None

    def describe(self) -> Dict[str, Any]:
        """
        Return a persistence-facing snapshot of the crystal state.

        Returns:
            Dict[str, Any]:
                Dictionary snapshot of the current crystal fields.
        """
        self.check_cleaned()
        with self._lock:
            return {
                "spell_crystal_id": self._spell_crystal_id,
                "module_name": self._module_name,
                "source_text": self._source_text,
                "source_sha256": self._source_sha256,
                "binding_signature": self._binding_signature,
                "source_authority_kind": self._source_authority_kind,
                "target_kind": self._target_kind,
                "target_qualname": self._target_qualname,
                "ast_imports": list(self._ast_imports),
                "ast_from_imports": self._copy_from_imports(self._ast_from_imports),
                "export_names": list(self._export_names),
                "internal_dependency_names": list(self._internal_dependency_names),
                "external_dependency_names": list(self._external_dependency_names),
                "physical_file_path": self._physical_file_path,
                "materialized_directory_path": self._materialized_directory_path,
                "spell_crystal_active": self._spell_crystal_active,
                "active_frame_name": self._active_frame_name,
                "active_conduit_name": self._active_conduit_name,
                "active_spellbook_name": self._active_spellbook_name,
                "active_spell_id": self._active_spell_id,
                "active_spell_index_id": self._active_spell_index_id,
            }
