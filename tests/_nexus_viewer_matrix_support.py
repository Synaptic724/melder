from typing import Dict, Optional, Sequence, Tuple

from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.nexus.acl.frame_acl_compiled_access_surface import (
    CompiledFrameACLAccessSurface,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.frame_descriptor.conduit_descriptor_payload import (
    ConduitDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.conduit_record import ConduitRecord
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.frame_descriptor.spell_descriptor_payload import (
    SpellDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.spell_record import SpellRecord
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.aether.nexus.rift.projection.command_projection import CommandProjection
from melder.aether.nexus.rift.projection.frame_projection_set import FrameProjectionSet
from melder.aether.nexus.rift.projection.view_projection import ViewProjection
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.spellbook.configuration.system_state import SystemState
from melder.spellbook.existence.existence import Existence


class ViewerProjectionRiftDouble:
    """
    Minimal Rift-like projection owner for direct viewer tests.

    Purpose:
        Let direct `FrameViewer` fixtures follow the live ownership model
        without requiring a full `Rift` runtime object.
    """

    def __init__(
            self,
            projection_sets_by_frame_name: Dict[str, FrameProjectionSet],
            *,
            rift_id: str = "test-rift",
            selected_contract_names_by_frame_name: Optional[
                Dict[str, Dict[str, str]]
            ] = None,
    ) -> None:
        self._projection_sets_by_frame_name = dict(projection_sets_by_frame_name)
        self._id = rift_id
        self._selected_contract_names_by_frame_name = (
            dict(selected_contract_names_by_frame_name)
            if selected_contract_names_by_frame_name is not None
            else {
                frame_name: {
                    "view": "default",
                    "command": "default",
                    "codegen": "default",
                }
                for frame_name in self._projection_sets_by_frame_name.keys()
            }
        )

    @property
    def id(self) -> str:
        return self._id

    def list_assigned_frame_names(self) -> Tuple[str, ...]:
        return tuple(sorted(self._projection_sets_by_frame_name.keys()))

    def _get_required_frame_projection_set(self, frame_name: str) -> FrameProjectionSet:
        try:
            return self._projection_sets_by_frame_name[frame_name]
        except KeyError as exc:
            raise ValueError(
                "Frame '{0}' was not found.".format(frame_name)
            ) from exc

    def _get_required_view_projection(self, frame_name: str) -> ViewProjection:
        return self._get_required_frame_projection_set(frame_name).view_projection

    def _get_required_command_projection(self, frame_name: str) -> CommandProjection:
        return self._get_required_frame_projection_set(frame_name).command_projection

    def _get_required_codegen_projection(self, frame_name: str) -> CodegenProjection:
        return self._get_required_frame_projection_set(frame_name).codegen_projection

    def _build_frame_viewer_metadata(self) -> Dict[str, object]:
        assigned_frame_names = self.list_assigned_frame_names()
        selected_contract_names_by_frame_name = dict(
            self._selected_contract_names_by_frame_name
        )
        return {
            "frame_count": len(assigned_frame_names),
            "available_view_count": len(assigned_frame_names),
            "rift_id": self._id,
            "frame_link_contract_ids_by_frame_name": {
                frame_name: "{0}-contract".format(frame_name)
                for frame_name in assigned_frame_names
            },
            "assigned_frame_names": assigned_frame_names,
            "selected_contract_names_by_frame_name": (
                selected_contract_names_by_frame_name
            ),
            "acl_selection_by_frame_name": selected_contract_names_by_frame_name,
            "contract_names_by_frame_name": selected_contract_names_by_frame_name,
            "default_grouping": "frame",
            "default_detail_level": "detailed",
        }


def build_spell_record_key(frame_name: str, spell_index: int) -> Tuple[str, str]:
    """
    Build the canonical spell record key for one matrix spell.

    Args:
        frame_name:
            Stable frame name used by the matrix fixture.
        spell_index:
            One-based spell ordinal inside the frame fixture.

    Returns:
        Tuple[str, str]: `(origin_spellbook_id, spell_id)` record key.
    """
    return (
        "{0}-spellbook".format(frame_name),
        "{0}-spell-{1}".format(frame_name, spell_index),
    )


def build_descriptor(
        frame_name: str,
        *,
        spell_payload_types: Sequence[str] = ("general",),
        conduit_count: int = 1,
        conduit_peer_ids_by_index: Optional[Dict[int, Tuple[str, ...]]] = None,
        visible_root_conduit_names: Optional[Tuple[str, ...]] = None,
        spellframe_values: Optional[Sequence[Optional[str]]] = None,
        permission_values: Optional[Sequence[Permissions]] = None,
        existence_values: Optional[Sequence[Existence]] = None,
        spellbook_ids: Optional[Sequence[str]] = None,
        include_detail_dunders: bool = False,
) -> FrameDescriptor:
    """
    Build one descriptor fixture with configurable conduits and spells.

    Args:
        frame_name:
            Stable frame name for the descriptor fixture.
        spell_payload_types:
            Published spell payload types to attach in order.
        conduit_count:
            Number of conduits to create.
        conduit_peer_ids_by_index:
            Optional conduit-index -> peer-id tuple map.
        visible_root_conduit_names:
            Optional visible conduit names for the frame payload summary.
        spellframe_values:
            Optional spellframe values aligned to `spell_payload_types`.
        permission_values:
            Optional permission values aligned to `spell_payload_types`.
        existence_values:
            Optional existence values aligned to `spell_payload_types`.
        spellbook_ids:
            Optional origin spellbook ids aligned to `spell_payload_types`.
        include_detail_dunders:
            Whether detailed payloads should include explicit dunder member and
            method names.

    Returns:
        FrameDescriptor: Populated descriptor fixture.
    """
    descriptor = FrameDescriptor(frame_name)
    root_conduit_ids = tuple(
        "{0}-conduit-{1}".format(frame_name, current_index)
        for current_index in range(1, conduit_count + 1)
    )
    named_root_conduits = tuple(
        (
            root_conduit_id,
            (
                visible_root_conduit_names[current_index - 1]
                if visible_root_conduit_names is not None
                else "root_{0}".format(current_index)
            ),
        )
        for current_index, root_conduit_id in enumerate(root_conduit_ids, start=1)
    )
    descriptor.set_frame_overview(
        FrameRecord(
            nexus_label="default",
            nexus_version="0.0.1",
            frame_name=frame_name,
            frame_id="{0}-frame".format(frame_name),
            config_origin_spellbook_id="{0}-spellbook".format(frame_name),
            payload=FrameDescriptorPayload(
                system_state=SystemState.dynamic,
                ai_native_enabled=True,
                rift_enabled=True,
                root_conduit_count=len(root_conduit_ids),
                root_conduit_ids=root_conduit_ids,
                named_root_conduits=named_root_conduits,
                conduit_cloud_entry_count=len(named_root_conduits),
                conduit_cloud_names=tuple(
                    conduit_name
                    for _, conduit_name in named_root_conduits
                ),
                cluster_count=0,
                cluster_names=tuple(),
            ),
        )
    )
    for conduit_index in range(1, conduit_count + 1):
        conduit_id = "{0}-conduit-{1}".format(frame_name, conduit_index)
        if conduit_peer_ids_by_index is not None:
            peer_ids = conduit_peer_ids_by_index.get(conduit_index, tuple())
        else:
            peer_ids = tuple(
                current_conduit_id
                for current_conduit_id in root_conduit_ids
                if current_conduit_id != conduit_id
            )
        descriptor.upsert_conduit_record(
            ConduitRecord(
                nexus_label="default",
                nexus_version="0.0.1",
                conduit_id=conduit_id,
                root_conduit_id=conduit_id,
                frame_name=frame_name,
                origin_spellbook_id="{0}-spellbook".format(frame_name),
                payload=ConduitDescriptorPayload(
                    conduit_name="root_{0}".format(conduit_index),
                    conduit_state=ConduitState.normal,
                    policy=Policies.default,
                    peer_conduit_ids=peer_ids,
                ),
            )
        )
    for spell_index, payload_type in enumerate(spell_payload_types, start=1):
        spellframe_value = (
            spellframe_values[spell_index - 1]
            if spellframe_values is not None
            else None
        )
        permission_value = (
            permission_values[spell_index - 1]
            if permission_values is not None
            else Permissions.create
        )
        existence_value = (
            existence_values[spell_index - 1]
            if existence_values is not None
            else Existence.unique
        )
        spellbook_id = (
            spellbook_ids[spell_index - 1]
            if spellbook_ids is not None
            else "{0}-spellbook".format(frame_name)
        )
        record_key = build_spell_record_key(frame_name, spell_index)
        if spellbook_ids is not None:
            record_key = (
                spellbook_id,
                "{0}-spell-{1}".format(frame_name, spell_index),
            )
        class_profile = (
            {"methods": ["run", "cleanup"]}
            if payload_type == "detailed"
            else None
        )
        instance_members = (
            {"state": {"type": "str"}}
            if payload_type == "detailed"
            else {}
        )
        if payload_type == "detailed" and include_detail_dunders:
            class_profile = {
                "members": {
                    "__dict__": {"kind": "attribute"},
                    "state": {"kind": "attribute"},
                },
                "methods": {
                    "__enter__": {"signature": "() -> Self"},
                    "run": {"signature": "() -> None"},
                },
            }
            instance_members = {
                "__dict__": {"type": "dict", "is_dunder": True},
                "state": {"type": "str", "is_dunder": False},
            }
        descriptor.upsert_spell_record(
            SpellRecord(
                nexus_label="default",
                nexus_version="0.0.1",
                origin_spellbook_id=record_key[0],
                frame_name=frame_name,
                owner_conduit_id=root_conduit_ids[(spell_index - 1) % conduit_count],
                spell_id=record_key[1],
                    spell_index_id="{0}-lineage-{1}".format(frame_name, spell_index),
                spell_name="{0}Spell{1}".format(frame_name.title(), spell_index),
                spellframe=spellframe_value,
                binding_name="{0}_spell_{1}".format(frame_name, spell_index),
                permissions=permission_value,
                existence=existence_value,
                payload=SpellDescriptorPayload(
                    payload_type=payload_type,
                    binding_payload={"kind": "class", "spell_index": spell_index},
                    resolution_payload={"requirements": [spell_index]},
                    class_profile=class_profile,
                    callable_profile=(
                        {"signature": "() -> None"}
                        if payload_type == "detailed"
                        else None
                    ),
                    metadata={"frame": frame_name, "spell_index": spell_index},
                    instance_members=instance_members,
                    dynamic_access=(
                        {"has_getattr": False, "has_setattr": True}
                        if payload_type == "detailed"
                        else {}
                    ),
                ),
            )
        )
    return descriptor


def build_surface(
        frame_name: str,
        configuration: FrameACLConfiguration,
        *,
        frame_payload_fields: Tuple[str, ...] = ("system_state", "rift_enabled"),
        visible_conduit_ids: Optional[Tuple[str, ...]] = None,
        visible_spell_keys: Optional[Tuple[Tuple[str, str], ...]] = None,
        conduit_sections_by_id: Optional[Dict[str, Tuple[str, ...]]] = None,
        spell_sections_by_key: Optional[Dict[Tuple[str, str], Tuple[str, ...]]] = None,
) -> CompiledFrameACLAccessSurface:
    """
    Build one compiled ACL surface fixture.

    Args:
        frame_name:
            Stable frame name.
        configuration:
            ACL configuration that owns the surface.
        frame_payload_fields:
            Visible frame payload fields.
        visible_conduit_ids:
            Optional visible conduit ids.
        visible_spell_keys:
            Optional visible spell record keys.
        conduit_sections_by_id:
            Optional conduit-section visibility map.
        spell_sections_by_key:
            Optional spell-section visibility map.

        Returns:
            CompiledFrameACLAccessSurface: Compiled surface fixture.
    """
    return CompiledFrameACLAccessSurface(
        frame_name=frame_name,
        configuration_id=configuration.configuration_id,
        view_profile_name=configuration.view_configuration.profile_name,
        view_profile_version=configuration.view_configuration.profile_version,
        codegen_profile_name=configuration.codegen_configuration.profile_name,
        codegen_profile_version=configuration.codegen_configuration.profile_version,
        allowed_kinds=("frame", "conduit", "spell"),
        allowed_commands=("query",),
        frame_payload_fields=frame_payload_fields,
        visible_conduit_ids=visible_conduit_ids or tuple(),
        visible_spell_keys=visible_spell_keys or tuple(),
        visible_spell_index_ids=tuple(
            sorted(
                {
                    spell_id
                    for _, spell_id in (visible_spell_keys or tuple())
                }
            )
        ),
        conduit_payload_sections_by_id=conduit_sections_by_id or {},
        spell_payload_sections_by_key=spell_sections_by_key or {},
        metadata={"visible_spell_count": len(visible_spell_keys or tuple())},
    )


def build_viewer(
        frame_name: str,
        *,
        spell_payload_types: Sequence[str] = ("general",),
        conduit_count: int = 1,
        visible_conduit_ids: Optional[Tuple[str, ...]] = None,
        visible_spell_keys: Optional[Tuple[Tuple[str, str], ...]] = None,
        conduit_sections_by_id: Optional[Dict[str, Tuple[str, ...]]] = None,
        spell_sections_by_key: Optional[Dict[Tuple[str, str], Tuple[str, ...]]] = None,
        frame_payload_fields: Tuple[str, ...] = ("system_state", "rift_enabled"),
        spellframe_values: Optional[Sequence[Optional[str]]] = None,
        permission_values: Optional[Sequence[Permissions]] = None,
        existence_values: Optional[Sequence[Existence]] = None,
        spellbook_ids: Optional[Sequence[str]] = None,
        include_detail_dunders: bool = False,
) -> FrameViewer:
    """
    Build one matrix-style `FrameViewer` fixture.

    Args:
        frame_name:
            Stable frame name.
        spell_payload_types:
            Published spell payload types to include.
        conduit_count:
            Number of conduits to include.
        visible_conduit_ids:
            Optional visible conduit ids.
        visible_spell_keys:
            Optional visible spell record keys.
        conduit_sections_by_id:
            Optional conduit-section visibility map.
        spell_sections_by_key:
            Optional spell-section visibility map.
        frame_payload_fields:
            Visible frame payload fields.
        spellframe_values:
            Optional spellframe values aligned to `spell_payload_types`.
        permission_values:
            Optional permission values aligned to `spell_payload_types`.
        existence_values:
            Optional existence values aligned to `spell_payload_types`.
        spellbook_ids:
            Optional origin spellbook ids aligned to `spell_payload_types`.
        include_detail_dunders:
            Whether detailed payloads should include explicit dunder member and
            method names.

    Returns:
        FrameViewer: Matrix-style viewer fixture.
    """
    descriptor = build_descriptor(
        frame_name,
        spell_payload_types=spell_payload_types,
        conduit_count=conduit_count,
        spellframe_values=spellframe_values,
        permission_values=permission_values,
        existence_values=existence_values,
        spellbook_ids=spellbook_ids,
        include_detail_dunders=include_detail_dunders,
    )
    configuration = FrameACLConfiguration.create_default(frame_name)
    compiled_surface = build_surface(
        frame_name,
        configuration,
        frame_payload_fields=frame_payload_fields,
        visible_conduit_ids=visible_conduit_ids,
        visible_spell_keys=visible_spell_keys,
        conduit_sections_by_id=conduit_sections_by_id,
        spell_sections_by_key=spell_sections_by_key,
    )
    projection_set = FrameProjectionSet(
        frame_name=frame_name,
        view_projection=ViewProjection(
            frame_name=frame_name,
            frame_descriptor=descriptor,
            frame_acl_configuration=configuration,
            compiled_access_surface=compiled_surface,
            metadata={"surface": "view"},
        ),
        command_projection=CommandProjection(
            frame_name=frame_name,
            frame_descriptor=descriptor,
            frame_acl_configuration=Nexus._clone_frame_acl_configuration(
                configuration,
                reason="test_command_projection_clone",
            ),
            compiled_access_surface=Nexus._clone_compiled_access_surface(
                compiled_surface
            ),
            metadata={"surface": "command"},
        ),
        codegen_projection=CodegenProjection(
            frame_name=frame_name,
            frame_descriptor=descriptor,
            frame_acl_configuration=Nexus._clone_frame_acl_configuration(
                configuration,
                reason="test_codegen_projection_clone",
            ),
            compiled_access_surface=Nexus._clone_compiled_access_surface(
                compiled_surface
            ),
            metadata={"surface": "codegen"},
        ),
        metadata={"source": "test_build_viewer"},
    )
    return FrameViewer(
        rift=ViewerProjectionRiftDouble({frame_name: projection_set}),
        default_view_frame_name=frame_name,
    )


def build_projection_backed_viewer_from_state(
        frame_name: str,
        descriptor: FrameDescriptor,
        configuration: FrameACLConfiguration,
        compiled_surface: CompiledFrameACLAccessSurface,
) -> FrameViewer:
    """
    Build one `FrameViewer` directly from one prepared frame state bundle.

    Args:
        frame_name:
            Hosted frame name.
        descriptor:
            Prepared frame descriptor.
        configuration:
            Prepared frame ACL configuration.
        compiled_surface:
            Prepared compiled access surface.

    Returns:
        FrameViewer: Projection-backed viewer for the prepared frame state.
    """
    projection_set = FrameProjectionSet(
        frame_name=frame_name,
        view_projection=ViewProjection(
            frame_name=frame_name,
            frame_descriptor=descriptor,
            frame_acl_configuration=configuration,
            compiled_access_surface=compiled_surface,
            metadata={"surface": "view"},
        ),
        command_projection=CommandProjection(
            frame_name=frame_name,
            frame_descriptor=descriptor,
            frame_acl_configuration=Nexus._clone_frame_acl_configuration(
                configuration,
                reason="test_command_projection_clone",
            ),
            compiled_access_surface=Nexus._clone_compiled_access_surface(
                compiled_surface
            ),
            metadata={"surface": "command"},
        ),
        codegen_projection=CodegenProjection(
            frame_name=frame_name,
            frame_descriptor=descriptor,
            frame_acl_configuration=Nexus._clone_frame_acl_configuration(
                configuration,
                reason="test_codegen_projection_clone",
            ),
            compiled_access_surface=Nexus._clone_compiled_access_surface(
                compiled_surface
            ),
            metadata={"surface": "codegen"},
        ),
        metadata={"source": "test_projection_backed_viewer_from_state"},
    )
    return FrameViewer(
        rift=ViewerProjectionRiftDouble({frame_name: projection_set}),
        default_view_frame_name=frame_name,
    )


def build_multi_frame_viewer(
        frame_names: Sequence[str],
        *,
        descriptor_kwargs_by_frame_name: Optional[Dict[str, Dict[str, object]]] = None,
        surface_kwargs_by_frame_name: Optional[Dict[str, Dict[str, object]]] = None,
) -> FrameViewer:
    """
    Build one multi-frame `FrameViewer` fixture.

    Args:
        frame_names:
            Hosted frame names to include.
        descriptor_kwargs_by_frame_name:
            Optional descriptor-builder kwargs keyed by frame name.
        surface_kwargs_by_frame_name:
            Optional compiled-surface kwargs keyed by frame name.

    Returns:
        FrameViewer: Multi-frame viewer fixture.
    """
    projection_sets_by_frame_name = {}
    for frame_name in frame_names:
        descriptor_kwargs = (
            descriptor_kwargs_by_frame_name.get(frame_name, {})
            if descriptor_kwargs_by_frame_name is not None
            else {}
        )
        descriptor = build_descriptor(
            frame_name,
            **descriptor_kwargs,
        )
        configuration = FrameACLConfiguration.create_default(frame_name)
        surface_kwargs = (
            surface_kwargs_by_frame_name.get(frame_name, {})
            if surface_kwargs_by_frame_name is not None
            else {}
        )
        compiled_surface = build_surface(
            frame_name,
            configuration,
            **surface_kwargs,
        )
        projection_sets_by_frame_name[frame_name] = FrameProjectionSet(
            frame_name=frame_name,
            view_projection=ViewProjection(
                frame_name=frame_name,
                frame_descriptor=descriptor,
                frame_acl_configuration=configuration,
                compiled_access_surface=compiled_surface,
                metadata={"surface": "view"},
            ),
            command_projection=CommandProjection(
                frame_name=frame_name,
                frame_descriptor=descriptor,
                frame_acl_configuration=Nexus._clone_frame_acl_configuration(
                    configuration,
                    reason="test_command_projection_clone",
                ),
                compiled_access_surface=Nexus._clone_compiled_access_surface(
                    compiled_surface
                ),
                metadata={"surface": "command"},
            ),
            codegen_projection=CodegenProjection(
                frame_name=frame_name,
                frame_descriptor=descriptor,
                frame_acl_configuration=Nexus._clone_frame_acl_configuration(
                    configuration,
                    reason="test_codegen_projection_clone",
                ),
                compiled_access_surface=Nexus._clone_compiled_access_surface(
                    compiled_surface
                ),
                metadata={"surface": "codegen"},
            ),
            metadata={"source": "test_build_multi_frame_viewer"},
        )
    return FrameViewer(
        rift=ViewerProjectionRiftDouble(projection_sets_by_frame_name),
        default_view_frame_name=frame_names[0] if len(frame_names) > 0 else None,
    )
