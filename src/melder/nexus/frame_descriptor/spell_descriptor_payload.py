import threading
from typing import Any, Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
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

    Contract:
        - Produces a plain data mapping suitable for publication on Nexus
          records.
        - Drops live runtime-object references and preserves only descriptor
          fields that can safely cross the record boundary.
        - Preserves enough structural detail for downstream viewers to explain
          how the spell was bound without needing the original profile object.

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
        - `payload_type` preserves the published spell payload detail type.
        - `payload_version` preserves the spell payload contract version.
        - `source_profile_name` / `source_profile_version` preserve the
          originating spell-profile provenance when known.
        - `binding_payload` is sanitized and contains no `original_object`.
        - Rich spell-facing detail fields are preserved when available.
        - Cleanup is idempotent and clears all owned payload references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "payload_type",
        "payload_version",
        "source_profile_name",
        "source_profile_version",
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
            payload_type: str,
            binding_payload: Dict[str, Any],
            resolution_payload: Any,
            class_profile: Optional[Any] = None,
            callable_profile: Optional[Any] = None,
            metadata: Optional[Dict[str, Any]] = None,
            instance_members: Optional[Dict[str, Any]] = None,
            dynamic_access: Optional[Dict[str, bool]] = None,
            payload_version: str = "0.0.1",
            source_profile_name: Optional[str] = None,
            source_profile_version: Optional[str] = None,
    ) -> None:
        """
        Initialize one descriptor-safe spell payload.

        Args:
            payload_type:
                Published spell payload detail type.
            payload_version:
                Published spell payload contract version.
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
            source_profile_name:
                Optional originating spell-profile family name.
            source_profile_version:
                Optional originating spell-profile version.
        Contract:
            - Stores the sanitized binding payload by ownership.
            - Copies metadata-style dictionaries so callers cannot retain live
              aliases back into the payload.
            - Preserves optional rich profile/detail payloads as provided
              because they are already descriptor-facing surfaces.
        Raises:
            ValueError:
                If `payload_type` or `payload_version` is empty, or if
                `source_profile_version` is provided without
                `source_profile_name`.
        """
        super().__init__()
        if not payload_type:
            raise ValueError("payload_type cannot be empty.")
        if not payload_version:
            raise ValueError("payload_version cannot be empty.")
        if source_profile_version is not None and source_profile_name is None:
            raise ValueError(
                "source_profile_version requires source_profile_name."
            )
        self._lock: threading.RLock = threading.RLock()
        self.payload_type: str = payload_type
        self.payload_version: str = payload_version
        self.source_profile_name: Optional[str] = source_profile_name
        self.source_profile_version: Optional[str] = source_profile_version
        self.binding_payload: Dict[str, Any] = dict(binding_payload)
        self.resolution_payload: Any = resolution_payload
        self.class_profile: Optional[Any] = class_profile
        self.callable_profile: Optional[Any] = callable_profile
        self.metadata: Dict[str, Any] = dict(metadata) if metadata is not None else {}
        self.instance_members: Dict[str, Any] = dict(instance_members) if instance_members is not None else {}
        self.dynamic_access: Dict[str, bool] = dict(dynamic_access) if dynamic_access is not None else {}

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

        This is the bridge from live spell-examiner/profile data into the
        published Nexus descriptor layer.

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
        Contract:
            - Sanitizes the live binding profile before constructing the
              published payload object.
            - Preserves the source profile family/version so downstream readers
              can explain where the payload contract came from.

        Returns:
            SpellDescriptorPayload: Descriptor-safe payload.
        """
        return cls(
            payload_type=profile_name,
            payload_version=profile_version,
            binding_payload=_sanitize_binding_profile(binding_profile),
            resolution_payload=resolution_payload,
            class_profile=class_profile,
            callable_profile=callable_profile,
            metadata=metadata,
            instance_members=instance_members,
            dynamic_access=dynamic_access,
            source_profile_name=profile_name,
            source_profile_version=profile_version,
        )

    def cleanup(self) -> None:
        """
        Idempotently clear the payload.

        Contract:
            - Safe to call more than once.
            - Clears owned mapping payloads before dropping field references.
            - Leaves future callers to fail through `check_cleaned()`.
            - Runs grouped teardown under the payload-owned instance lock.
        """
        if self._cleaned:
            return
        with self._lock:
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

            del self.payload_type
            del self.payload_version
            del self.source_profile_name
            del self.source_profile_version
            del self.binding_payload
            del self.resolution_payload
            del self.class_profile
            del self.callable_profile
            del self.metadata
            del self.instance_members
            del self.dynamic_access
            del self._lock
