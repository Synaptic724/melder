from typing import Any, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    CallableBindingProfile,
    ClassBindingProfile,
    InstanceBindingProfile,
    OtherBindingProfile,
    SpellBindingProfile,
)
from melder.utilities.general_base.cleanable import Cleanable


def _sanitize_binding_profile(
        binding_profile: SpellBindingProfile,
) -> Dict[str, Any]:
    """
    Convert a binding profile into a descriptor-safe mapping.

    Args:
        binding_profile:
            Live binding profile to sanitize.

    Returns:
        Dict[str, Any]: Sanitized binding payload with runtime object refs removed.
    """
    payload: Dict[str, Any] = {
        "kind": getattr(binding_profile.kind, "name", None),
    }

    if isinstance(binding_profile, ClassBindingProfile):
        payload.update({
            "name": binding_profile.name,
            "qualname": binding_profile.qualname,
            "module": binding_profile.module,
            "bases": list(binding_profile.bases),
            "mro": list(binding_profile.mro),
            "annotations": dict(binding_profile.annotations),
            "origin_file": binding_profile.origin_file,
            "origin_line": binding_profile.origin_line,
            "source_preview": binding_profile.source_preview,
            "is_dataclass": binding_profile.is_dataclass,
            "decorated": binding_profile.decorated,
            "method_names": list(binding_profile.method_names),
        })
    elif isinstance(binding_profile, CallableBindingProfile):
        payload.update({
            "name": binding_profile.name,
            "qualname": binding_profile.qualname,
            "module": binding_profile.module,
            "object_id": binding_profile.object_id,
            "type_name": binding_profile.type_name,
            "repr_string": binding_profile.repr_string,
            "signature": binding_profile.signature,
            "parameters": list(binding_profile.parameters),
            "builtin_module": binding_profile.builtin_module,
            "extension_module": binding_profile.extension_module,
            "lambda_function": binding_profile.lambda_function,
            "abstract": binding_profile.abstract,
        })
    elif isinstance(binding_profile, InstanceBindingProfile):
        payload.update({
            "type_name": binding_profile.type_name,
            "module": binding_profile.module,
            "repr_string": binding_profile.repr_string,
        })
    elif isinstance(binding_profile, OtherBindingProfile):
        payload.update({
            "type_name": binding_profile.type_name,
            "module": binding_profile.module,
            "repr_string": binding_profile.repr_string,
        })

    return payload


class SpellDescriptorPayload(Cleanable):
    """
    Descriptor-safe published spell payload.

    Purpose:
        Store the rich spell-facing payload on `SpellRecord` without carrying
        live runtime object references.

    Contract:
        - `profile_name` preserves the originating spell profile family.
        - `profile_version` preserves the originating spell profile contract version.
        - `binding_payload` is sanitized and contains no `original_object`.
        - Rich spell-facing detail fields are preserved when available.
        - Cleanup is idempotent and clears all owned payload references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "profile_name",
        "profile_version",
        "binding_payload",
        "resolution_payload",
        "class_profile",
        "callable_profile",
        "metadata",
        "instance_members",
        "dynamic_access",
    ]

    def __init__(
            self,
            *,
            profile_name: str,
            binding_payload: Dict[str, Any],
            resolution_payload: Any,
            class_profile: Optional[Any] = None,
            callable_profile: Optional[Any] = None,
            metadata: Optional[Dict[str, Any]] = None,
            instance_members: Optional[Dict[str, Any]] = None,
            dynamic_access: Optional[Dict[str, bool]] = None,
            profile_version: str = "0.0.1",
    ) -> None:
        """
        Initialize one descriptor-safe spell payload.

        Args:
            profile_name:
                Source spell profile family name.
            profile_version:
                Source spell profile contract version.
            binding_payload:
                Sanitized bind-time payload.
            resolution_payload:
                Resolution payload when available.
            class_profile:
                Optional class inspector payload.
            callable_profile:
                Optional callable inspector payload.
            metadata:
                Optional metadata mapping.
            instance_members:
                Optional instance-member mapping.
            dynamic_access:
                Optional dynamic access flags.

        Returns:
            None.
        """
        super().__init__()
        if not profile_name:
            raise ValueError("profile_name cannot be empty.")
        if not profile_version:
            raise ValueError("profile_version cannot be empty.")
        self.profile_name = profile_name
        self.profile_version = profile_version
        self.binding_payload = dict(binding_payload)
        self.resolution_payload = resolution_payload
        self.class_profile = class_profile
        self.callable_profile = callable_profile
        self.metadata = dict(metadata) if metadata is not None else {}
        self.instance_members = dict(instance_members) if instance_members is not None else {}
        self.dynamic_access = dict(dynamic_access) if dynamic_access is not None else {}

    @classmethod
    def from_spell_profile(
            cls,
            profile_name: str,
            profile_version: str,
            binding_profile: SpellBindingProfile,
            *,
            resolution_payload: Any,
            class_profile: Optional[Any] = None,
            callable_profile: Optional[Any] = None,
            metadata: Optional[Dict[str, Any]] = None,
            instance_members: Optional[Dict[str, Any]] = None,
            dynamic_access: Optional[Dict[str, bool]] = None,
    ) -> "SpellDescriptorPayload":
        """
        Build one descriptor-safe payload from spell profile parts.

        Args:
            profile_name:
                Source spell profile family name.
            profile_version:
                Source spell profile contract version.
            binding_profile:
                Live binding profile to sanitize.
            resolution_payload:
                Resolution payload to preserve.
            class_profile:
                Optional class inspector payload.
            callable_profile:
                Optional callable inspector payload.
            metadata:
                Optional metadata mapping.
            instance_members:
                Optional instance-member mapping.
            dynamic_access:
                Optional dynamic access flags.

        Returns:
            SpellDescriptorPayload: Descriptor-safe payload.
        """
        return cls(
            profile_name=profile_name,
            profile_version=profile_version,
            binding_payload=_sanitize_binding_profile(binding_profile),
            resolution_payload=resolution_payload,
            class_profile=class_profile,
            callable_profile=callable_profile,
            metadata=metadata,
            instance_members=instance_members,
            dynamic_access=dynamic_access,
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the payload.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if isinstance(self.binding_payload, dict):
            self.binding_payload.clear()
        if isinstance(self.metadata, dict):
            self.metadata.clear()
        if isinstance(self.instance_members, dict):
            self.instance_members.clear()
        if isinstance(self.dynamic_access, dict):
            self.dynamic_access.clear()
        self.profile_name = None
        self.profile_version = None
        self.binding_payload = None
        self.resolution_payload = None
        self.class_profile = None
        self.callable_profile = None
        self.metadata = None
        self.instance_members = None
        self.dynamic_access = None
