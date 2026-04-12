import threading
from typing import Any, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aether import Aether
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.rift.frame_link.frame_link import FrameLink
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class CommandSystem(Cleanable):
    """
    Internal

    Room-local command surface for controlled getters and explicit execution.

    Purpose:
        Provide the first command-oriented layer above the viewer/workstation
        split without owning discovery or persistence itself.

    Contract:
        - Uses `RiftSpace` selected target ids plus the attached viewer for
          selected-target getters.
        - Enforces compiled command ACL state on selected-target and direct
          fetch paths before exposing frame/conduit/spell runtime objects.
        - Uses the owned workstation for active-target attribute/method getters
          and method execution.
        - Does not store results itself. Callers that want persistence must
          bind returned values into the workstation explicitly.
        - Leaves already-bound workstation objects outside post-bind ACL
          policing; command ACLs gate access before bind.

    Lifecycle:
        Owned by one `RiftSpace`. Cleanup drops references to the owning room
        and workstation but does not clean those children itself.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_command_system_id",
        "_owner_space_id",
        "_lock",
        "_space",
        "_workstation",
    ]
    _aether = Aether()

    def __init__(self, *, space: Any, workstation: Any) -> None:
        """
        Internal

        Initialize one room-local command system.

        Args:
            space:
                Owning `RiftSpace`.
            workstation:
                Room-local workstation owned by the same space.

        Returns:
            None.

        Raises:
            TypeError:
                If `space` or `workstation` is None.
        """
        super().__init__()
        if space is None:
            raise TypeError("space cannot be None.")
        if workstation is None:
            raise TypeError("workstation cannot be None.")
        self._command_system_id: str = IDBuilder.create_id()
        self._owner_space_id: str = space.space_id
        self._lock: threading.RLock = threading.RLock()
        self._space: Any = space
        self._workstation: Any = workstation

    def cleanup(self) -> None:
        """
        Internal

        Idempotently clear command-system-owned references.

        Contract:
            - Safe to call more than once.
            - Clears only command-system-owned references.
            - Does not cleanup the owning `RiftSpace` or its workstation,
              because those remain owned by the room itself.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._owner_space_id = None
            self._space = None
            self._workstation = None
            self._command_system_id = None
        self._lock = None

    @property
    def command_system_id(self) -> str:
        """
        Return the stable command-system identifier.

        Returns:
            str: Stable command-system id.
        """
        self.check_cleaned()
        with self._lock:
            return self._command_system_id

    @property
    def owner_space_id(self) -> str:
        """
        Return the owning room identifier.

        Returns:
            str: Owning `RiftSpace` id.
        """
        self.check_cleaned()
        with self._lock:
            return self._owner_space_id

    def get_selected_target_link(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> FrameLink:
        """
        Return the single selected viewer target link for one frame.

        Contract:
            - Requires the selected-target set to contain exactly one target in
              the resolved frame.
            - Re-resolves the live viewer target list and returns the matching
              `FrameLink` instead of caching links locally.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            FrameLink: The selected target link.

        Raises:
            ValueError:
                If no selected target exists, the selected set is ambiguous, or
                command ACL denies access to the resolved target.
        """
        self.check_cleaned()
        with self._lock:
            selected_frame_name, selected_target_ids = self._resolve_selected_target_ids(
                frame_name=frame_name
            )
            if len(selected_target_ids) == 0:
                raise ValueError(
                    "RiftSpace has no selected target in frame '{0}'.".format(
                        selected_frame_name
                    )
                )
            if len(selected_target_ids) > 1:
                raise ValueError(
                    "RiftSpace selected target set is ambiguous in frame '{0}'.".format(
                        selected_frame_name
                    )
                )
            viewer = self._space.get_required_frame_viewer()
            for frame_link in viewer.execute_method(
                    "list_targets",
                    frame_name=selected_frame_name,
            ):
                if frame_link.link_id == selected_target_ids[0]:
                    self._assert_selected_target_command_enabled(frame_link)
                    return frame_link
            raise ValueError(
                "Selected target '{0}' was not found in frame '{1}'.".format(
                    selected_target_ids[0],
                    selected_frame_name,
                )
            )

    def get_selected_target_record(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the descriptor-backed record for the single selected viewer target.

        Contract:
            - Resolves the selected target through the viewer first.
            - Returns the corresponding frame overview, conduit record, or
              spell record depending on target kind.
            - Raises instead of fabricating a fallback for unsupported target
              kinds.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Selected frame/conduit/spell record.

        Raises:
            ValueError:
                If no selected target exists or the selected target kind is not
                supported, or command ACL denies access to the target.
        """
        self.check_cleaned()
        with self._lock:
            selected_target = self.get_selected_target_link(frame_name=frame_name)
            viewer = self._space.get_required_frame_viewer()
            if selected_target.source_kind == "frame":
                descriptor = viewer._get_required_frame_descriptor(
                    selected_target.frame_name
                )
                if descriptor.frame_overview is None:
                    raise ValueError(
                        "Frame '{0}' has no published frame overview.".format(
                            selected_target.frame_name
                        )
                    )
                return descriptor.frame_overview
            if selected_target.source_kind == "conduit":
                _, conduit_record = viewer._get_required_conduit_record(
                    selected_target.source_id,
                    frame_name=selected_target.frame_name,
                )
                return conduit_record
            if selected_target.source_kind == "spell":
                _, spell_record = viewer._get_required_spell_record(
                    selected_target.source_id,
                    frame_name=selected_target.frame_name,
                )
                return spell_record
            raise ValueError(
                "Unsupported selected target kind '{0}'.".format(
                    selected_target.source_kind
                )
            )

    def get_selected_target_runtime_object(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return the live runtime object for the single selected viewer target.

        Args:
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live frame handle, conduit object, or spell object.

        Raises:
            ValueError:
                If the selected target kind is unsupported or command ACL
                denies access to the resolved target.
        """
        self.check_cleaned()
        with self._lock:
            selected_target = self.get_selected_target_link(frame_name=frame_name)
            if selected_target.source_kind == "frame":
                descriptor = self._space.get_required_frame_viewer()._get_required_frame_descriptor(
                    selected_target.frame_name
                )
                if descriptor.frame_handle is None:
                    raise ValueError(
                        "Frame '{0}' has no live frame handle.".format(
                            selected_target.frame_name
                        )
                    )
                return descriptor.frame_handle
            if selected_target.source_kind == "conduit":
                return self.get_conduit_object_by_id(
                    selected_target.source_id,
                    frame_name=selected_target.frame_name,
                )
            if selected_target.source_kind == "spell":
                return self.get_spell_object_by_source_id(
                    selected_target.source_id,
                    frame_name=selected_target.frame_name,
                )
            raise ValueError(
                "Unsupported selected target kind '{0}'.".format(
                    selected_target.source_kind
                )
            )

    def get_conduit_object_by_id(
            self,
            conduit_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live conduit object by id, including lesser-conduit fallback.

        Args:
            conduit_id:
                Conduit id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit object.

        Raises:
            ValueError:
                If the conduit is not published in the selected frame or
                command ACL denies conduit access.
        """
        self.check_cleaned()
        with self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_frame_command_enabled(resolved_frame_name)
            self._assert_conduit_command_enabled(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            try:
                return self._aether._get_conduit_by_id(
                    conduit_id,
                    resolved_frame_name,
                )
            except ValueError:
                frame = self._get_required_runtime_frame(resolved_frame_name)
                for root_conduit in frame._conduits.values():
                    conduit_ward = root_conduit._conduit_ward
                    if conduit_ward is None:
                        continue
                    lesser_conduit = conduit_ward._get_lesser_conduit(conduit_id)
                    if lesser_conduit is not None:
                        return lesser_conduit
                raise ValueError(
                    "Conduit id '{0}' was not found in frame '{1}'.".format(
                        conduit_id,
                        resolved_frame_name,
                    )
                )

    def get_conduit_object_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live root/normal conduit object by name.

        Args:
            conduit_name:
                Conduit name to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live conduit object.

        Raises:
            ValueError:
                If the conduit name is not published in the selected frame,
                resolves ambiguously, or command ACL denies access.
        """
        self.check_cleaned()
        with self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_frame_command_enabled(resolved_frame_name)
            conduit_id = self._get_required_published_conduit_id_by_name(
                conduit_name,
                frame_name=resolved_frame_name,
            )
            self._assert_conduit_command_enabled(
                conduit_id,
                frame_name=resolved_frame_name,
            )
            return self._aether._get_conduit_by_name(
                conduit_name,
                resolved_frame_name,
            )

    def get_spell_object_by_source_id(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live spell object using a published spell source id.

        Args:
            spell_source_id:
                Published spell source id in `spellbook_id:spell_id` form.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live spell object.

        Raises:
            ValueError:
                If the spell source id is not published in the selected frame
                or command ACL denies spell access.
        """
        self.check_cleaned()
        with self._lock:
            viewer = self._space.get_required_frame_viewer()
            resolved_frame_name, spell_record = viewer._get_required_spell_record(
                spell_source_id,
                frame_name=frame_name,
            )
            return self.get_spell_object_by_index_id(
                spell_record.spell_index_id,
                frame_name=resolved_frame_name,
            )

    def get_spell_object_by_index_id(
            self,
            spell_index_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live spell object by stable spell index id.

        Args:
            spell_index_id:
                Stable SpellIndex lineage id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live spell object.

        Raises:
            ValueError:
                If the spell lineage is not published in the selected frame or
                command ACL denies spell access.
        """
        self.check_cleaned()
        with self._lock:
            if not spell_index_id:
                raise ValueError("spell_index_id cannot be empty.")
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_frame_command_enabled(resolved_frame_name)
            self._assert_spell_command_enabled(
                spell_index_id,
                frame_name=resolved_frame_name,
            )
            viewer = self._space.get_required_frame_viewer()
            descriptor = viewer._get_required_frame_descriptor(resolved_frame_name)
            matching_spell_records = [
                spell_record
                for spell_record in descriptor.spell_records_by_key.values()
                if spell_record.spell_index_id == spell_index_id
            ]
            if len(matching_spell_records) == 0:
                raise ValueError(
                    "Spell index id '{0}' was not found in frame '{1}'.".format(
                        spell_index_id,
                        resolved_frame_name,
                    )
                )
            for spell_record in matching_spell_records:
                owner_conduit_id = spell_record.owner_conduit_id
                if not owner_conduit_id:
                    continue
                owner_conduit = self.get_conduit_object_by_id(
                    owner_conduit_id,
                    frame_name=resolved_frame_name,
                )
                spell = owner_conduit.get_spell_by_index_id(spell_index_id)
                if spell is not None:
                    return spell
            raise ValueError(
                "Spell index id '{0}' was not found in the owner spellbooks for frame '{1}'.".format(
                    spell_index_id,
                    resolved_frame_name,
                )
            )

    def get_spell_object_by_id(
            self,
            spell_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> object:
        """
        Return one live spell object by current spell id.

        Args:
            spell_id:
                Current spell id to resolve.
            frame_name:
                Optional frame name. When omitted, the room default frame is
                used.

        Returns:
            object: Live spell object.

        Raises:
            ValueError:
                If the spell is not published in the selected frame or command
                ACL denies spell access.
        """
        self.check_cleaned()
        with self._lock:
            resolved_frame_name = self._resolve_runtime_frame_name(frame_name)
            self._assert_frame_command_enabled(resolved_frame_name)
            spell_index_id = self._get_required_published_spell_index_id_by_spell_id(
                spell_id,
                frame_name=resolved_frame_name,
            )
            self._assert_spell_command_enabled(
                spell_index_id,
                frame_name=resolved_frame_name,
            )
            owner_conduit = self._aether._get_conduit_by_spell_id(
                spell_id,
                resolved_frame_name,
            )
            spellbook = owner_conduit._spellbook
            if spellbook is None:
                raise ValueError(
                    "Owner conduit for spell '{0}' has no spellbook.".format(spell_id)
                )
            for spell_index, spell in spellbook._spells.items():
                if spell_index.has_version(spell_id):
                    return spell
            raise ValueError(
                "Spell id '{0}' was not found in the owner spellbook.".format(spell_id)
            )

    def get_target_attribute(self, attribute_name: str) -> object:
        """
        Return one attribute value from the current workstation target.

        Args:
            attribute_name:
                Attribute name to retrieve from the active target.

        Returns:
            object: Retrieved attribute value.

        Raises:
            ValueError:
                If `attribute_name` is empty.
            AttributeError:
                If the target does not expose the requested attribute.
        """
        self.check_cleaned()
        with self._lock:
            if not attribute_name:
                raise ValueError("attribute_name cannot be empty.")
            target = self._workstation.get_target()
            return getattr(target, attribute_name)

    def get_target_method(self, method_name: str) -> object:
        """
        Return one method/callable from the current workstation target.

        Args:
            method_name:
                Method name to retrieve from the active target.

        Returns:
            object: Bound callable from the target.

        Raises:
            ValueError:
                If `method_name` is empty.
            AttributeError:
                If the target does not expose the requested method.
            RuntimeError:
                If the resolved attribute is not callable.
        """
        self.check_cleaned()
        with self._lock:
            if not method_name:
                raise ValueError("method_name cannot be empty.")
            target = self._workstation.get_target()
            method = getattr(target, method_name)
            if not callable(method):
                raise RuntimeError(
                    "Target attribute '{0}' is not callable.".format(method_name)
                )
            return method

    def execute_target_method(
            self,
            method_name: str,
            *args: Any,
            bind_as_name: Optional[str] = None,
            bind_as_store: str = "objects",
            **kwargs: Any
    ) -> object:
        """
        Execute one method on the current workstation target.

        Args:
            method_name:
                Method name to execute on the active target.
            *args:
                Positional arguments passed to the method.
            bind_as_name:
                Optional workstation binding name for the return value.
            bind_as_store:
                Store to use when binding the return value.
            **kwargs:
                Keyword arguments passed to the method.

        Returns:
            object: Method return value.
        """
        self.check_cleaned()
        with self._lock:
            method = self.get_target_method(method_name)
            result = method(*args, **kwargs)
            if bind_as_name is not None:
                self._bind_result(
                    bind_as_name=bind_as_name,
                    bind_as_store=bind_as_store,
                    value=result,
                )
            return result

    def _resolve_selected_target_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, Tuple[str, ...]]:
        """
        Resolve one frame name and its selected target ids.

        Args:
            frame_name:
                Optional explicit frame name.

        Returns:
            Tuple[str, Tuple[str, ...]]: Resolved frame name and selected ids.
        """
        viewer = self._space.get_required_frame_viewer()
        selected_frame_name = frame_name or viewer.default_view_frame_name
        if selected_frame_name is None:
            raise ValueError("RiftSpace has no default selected frame.")
        return (
            selected_frame_name,
            tuple(self._space.list_selected_target_ids(frame_name=selected_frame_name)),
        )

    def _assert_selected_target_command_enabled(
            self,
            frame_link: FrameLink,
    ) -> None:
        """
        Enforce command ACL on one selected viewer target.

        Contract:
            - Applies command ACL only to selected-target access paths.
            - Resolves spell targets through published descriptor truth so
              spell gating stays on stable lineage identity.
            - Leaves unsupported target kinds to the public callers so they
              retain the existing kind-specific error behavior.

        Args:
            frame_link:
                Selected viewer target link being resolved.

        Returns:
            None.

        Raises:
            ValueError:
                If command ACL denies access to the selected frame, conduit, or
                spell target.
        """
        if frame_link.source_kind == "frame":
            self._assert_frame_command_enabled(frame_link.frame_name)
            return
        if frame_link.source_kind == "conduit":
            self._assert_frame_command_enabled(frame_link.frame_name)
            self._assert_conduit_command_enabled(
                frame_link.source_id,
                frame_name=frame_link.frame_name,
            )
            return
        if frame_link.source_kind == "spell":
            self._assert_frame_command_enabled(frame_link.frame_name)
            viewer = self._space.get_required_frame_viewer()
            _, spell_record = viewer._get_required_spell_record(
                frame_link.source_id,
                frame_name=frame_link.frame_name,
            )
            self._assert_spell_command_enabled(
                spell_record.spell_index_id,
                frame_name=frame_link.frame_name,
            )

    def _assert_frame_command_enabled(self, frame_name: str) -> None:
        """
        Enforce frame-level command access for one hosted frame.

        Args:
            frame_name:
                Hosted frame whose command gate should be checked.

        Returns:
            None.

        Raises:
            ValueError:
                If the frame does not enable command access.
        """
        compiled_access_surface = self._get_required_compiled_access_surface(frame_name)
        if compiled_access_surface.command_frame_enabled:
            return
        raise ValueError(
            "Command access is disabled for frame '{0}'.".format(frame_name)
        )

    def _assert_conduit_command_enabled(
            self,
            conduit_id: str,
            *,
            frame_name: str,
    ) -> None:
        """
        Enforce conduit-level command access for one published conduit id.

        Args:
            conduit_id:
                Published conduit id being resolved.
            frame_name:
                Hosted frame the conduit belongs to.

        Returns:
            None.

        Raises:
            ValueError:
                If the conduit is not command-enabled in the target frame.
        """
        compiled_access_surface = self._get_required_compiled_access_surface(frame_name)
        if conduit_id in compiled_access_surface.enabled_conduit_ids:
            return
        raise ValueError(
            "Command access to conduit '{0}' is disabled in frame '{1}'.".format(
                conduit_id,
                frame_name,
            )
        )

    def _assert_spell_command_enabled(
            self,
            spell_index_id: str,
            *,
            frame_name: str,
    ) -> None:
        """
        Enforce spell-level command access for one stable spell lineage id.

        Args:
            spell_index_id:
                Stable spell lineage id being resolved.
            frame_name:
                Hosted frame the spell belongs to.

        Returns:
            None.

        Raises:
            ValueError:
                If the spell lineage is not command-enabled in the target
                frame.
        """
        compiled_access_surface = self._get_required_compiled_access_surface(frame_name)
        if spell_index_id in compiled_access_surface.enabled_spell_index_ids:
            return
        raise ValueError(
            "Command access to spell lineage '{0}' is disabled in frame '{1}'.".format(
                spell_index_id,
                frame_name,
            )
        )

    def _get_required_published_conduit_id_by_name(
            self,
            conduit_name: str,
            *,
            frame_name: str,
    ) -> str:
        """
        Return the published conduit id matching one conduit name.

        Contract:
            - Resolves against published descriptor truth, not runtime conduit
              registries.
            - Raises on missing or ambiguous published matches.

        Args:
            conduit_name:
                Published conduit name to resolve.
            frame_name:
                Hosted frame to query.

        Returns:
            str: Published conduit id for the named conduit.

        Raises:
            ValueError:
                If the conduit name is empty, missing, or ambiguous.
        """
        if not conduit_name:
            raise ValueError("conduit_name cannot be empty.")
        viewer = self._space.get_required_frame_viewer()
        descriptor = viewer._get_required_frame_descriptor(frame_name)
        matching_conduit_ids = [
            conduit_record.conduit_id
            for conduit_record in descriptor.conduit_records_by_id.values()
            if conduit_record.payload.conduit_name == conduit_name
        ]
        if len(matching_conduit_ids) == 0:
            raise ValueError(
                "Conduit name '{0}' was not found in frame '{1}'.".format(
                    conduit_name,
                    frame_name,
                )
            )
        if len(matching_conduit_ids) > 1:
            raise ValueError(
                "Conduit name '{0}' is ambiguous in frame '{1}'.".format(
                    conduit_name,
                    frame_name,
                )
            )
        return matching_conduit_ids[0]

    def _get_required_published_spell_index_id_by_spell_id(
            self,
            spell_id: str,
            *,
            frame_name: str,
    ) -> str:
        """
        Return the stable spell lineage id matching one published spell id.

        Contract:
            - Resolves through published descriptor truth so ACL checks stay on
              stable lineage identity.
            - Accepts multiple matching records only when they collapse to one
              lineage id.

        Args:
            spell_id:
                Current published spell id to resolve.
            frame_name:
                Hosted frame to query.

        Returns:
            str: Stable published spell lineage id.

        Raises:
            ValueError:
                If the spell id is empty, missing, or ambiguous across
                published lineages.
        """
        if not spell_id:
            raise ValueError("spell_id cannot be empty.")
        viewer = self._space.get_required_frame_viewer()
        descriptor = viewer._get_required_frame_descriptor(frame_name)
        matching_spell_index_ids = {
            spell_record.spell_index_id
            for spell_record in descriptor.spell_records_by_key.values()
            if spell_record.spell_id == spell_id
        }
        if len(matching_spell_index_ids) == 0:
            raise ValueError(
                "Spell id '{0}' was not found in frame '{1}'.".format(
                    spell_id,
                    frame_name,
                )
            )
        if len(matching_spell_index_ids) > 1:
            raise ValueError(
                "Spell id '{0}' is ambiguous in frame '{1}'.".format(
                    spell_id,
                    frame_name,
                )
            )
        return next(iter(matching_spell_index_ids))

    def _get_required_compiled_access_surface(
            self,
            frame_name: str,
    ) -> CompiledFrameACLAccessSurface:
        """
        Return the compiled ACL access surface for one hosted frame.

        Args:
            frame_name:
                Hosted frame whose compiled ACL surface is required.

        Returns:
            CompiledFrameACLAccessSurface:
                Compiled frame ACL access surface for the target frame.

        Raises:
            ValueError:
                If the attached viewer does not host the requested frame.
        """
        viewer = self._space.get_required_frame_viewer()
        return viewer._get_required_compiled_access_surface(frame_name)

    def _bind_result(
            self,
            *,
            bind_as_name: str,
            bind_as_store: str,
            value: object,
    ) -> None:
        """
        Bind a returned value back into the workstation.

        Contract:
            - Routes binding into exactly one workstation store.
            - Raises for unsupported stores instead of silently discarding the
              value.

        Args:
            bind_as_name:
                Binding name for the returned value.
            bind_as_store:
                Target workstation store.
            value:
                Value to bind.

        Returns:
            None.
        """
        if bind_as_store == "objects":
            self._workstation.bind_object(bind_as_name, value)
            return
        if bind_as_store == "attributes":
            self._workstation.bind_attribute(bind_as_name, value)
            return
        if bind_as_store == "methods":
            self._workstation.bind_method(bind_as_name, value)
            return
        raise ValueError(
            "Unsupported workstation store '{0}'.".format(bind_as_store)
        )

    def _resolve_runtime_frame_name(
            self,
            frame_name: Optional[str],
    ) -> str:
        """
        Resolve the runtime frame name for direct Aether-backed getters.

        Args:
            frame_name:
                Optional explicit frame name.

        Returns:
            str: Resolved runtime frame name.
        """
        viewer = self._space.get_required_frame_viewer()
        resolved_frame_name = frame_name or viewer.default_view_frame_name
        if resolved_frame_name is None:
            raise ValueError("RiftSpace has no default selected frame.")
        return resolved_frame_name

    def _get_required_runtime_frame(self, frame_name: str) -> object:
        """
        Return one live Aether frame by name or raise.

        Args:
            frame_name:
                Runtime frame name to resolve.

        Returns:
            object: Live `AethericFrame`.
        """
        try:
            return self._aether._aetheric_frames[frame_name]
        except KeyError as exc:
            raise ValueError(
                "Aetheric frame '{0}' does not exist.".format(frame_name)
            ) from exc
