from typing import TYPE_CHECKING, Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.nexus.acl.frame_acl_compiled_access_surface import (
        CompiledFrameACLAccessSurface,
    )
    from melder.nexus.acl.frame_acl_configuration import FrameACLConfiguration
    from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor

from melder.utilities.general_base.cleanable import Cleanable


class ViewProjection(Cleanable):
    """
    Consumer-shaped view projection for one targeted frame.

    Purpose:
        Hold the descriptor truth, assembled ACL snapshot, and compiled access
        surface needed by the viewer layer without forcing command/codegen to
        consume the same object.

    Contract:
        - Owns one detached ACL configuration and one detached compiled access
          surface.
        - References one live frame descriptor without owning descriptor
          cleanup.
        - Cleanup only tears down owned projection state.

    Threading:
        Replaced wholesale on refresh rather than mutated in place, so a
        consumer mid-operation continues against a coherent snapshot.

    Registration:
        MELDER KERNEL - guarded. Compiled by the ACL layer and stored as Rift
        projection state.

    Subsystem Context:
        The view member of the projection triple, bundled with its siblings in
        a `FrameProjectionSet`. It carries descriptor truth, the assembled ACL
        snapshot, and the compiled access surface for the viewer layer.

    System Context:
        Three consumer-shaped projections rather than one shared object is the
        design, and the reason is coupling: forcing command and codegen to consume the viewer's object would couple every consumer to the viewer's shape, so a change made for one would ripple into all three.
        Owning a DETACHED ACL configuration snapshot is what makes the
        projection a stable answer. Reading live ACL state per question would
        let permissions shift mid-operation, which is exactly what the refresh
        barrier - block, drain, swap, reopen - exists to prevent.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Consumer-shaped view projection for one targeted frame. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_frame_name",
        "_frame_descriptor",
        "_frame_acl_configuration",
        "_compiled_access_surface",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            frame_descriptor: FrameDescriptor,
            frame_acl_configuration: FrameACLConfiguration,
            compiled_access_surface: CompiledFrameACLAccessSurface,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize one view projection.

        Args:
            frame_name:
                Target frame name.
            frame_descriptor:
                Descriptor truth for the frame.
            frame_acl_configuration:
                Detached ACL configuration snapshot for this projection.
            compiled_access_surface:
                Detached compiled access surface for this projection.
            metadata:
                Optional projection metadata.

        Returns:
            None.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._frame_name: str = frame_name
        self._frame_descriptor: FrameDescriptor = frame_descriptor
        self._frame_acl_configuration: FrameACLConfiguration = frame_acl_configuration
        self._compiled_access_surface: CompiledFrameACLAccessSurface = compiled_access_surface
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently cleanup owned projection state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self._compiled_access_surface is not None:
            self._compiled_access_surface.cleanup()
        if self._frame_acl_configuration is not None:
            self._frame_acl_configuration.cleanup()
        self._metadata.clear()

        del self._frame_name
        del self._frame_descriptor
        del self._frame_acl_configuration
        del self._compiled_access_surface
        del self._metadata

    @property
    def frame_name(self) -> str:
        """Return the target frame name."""
        self.check_cleaned()
        return self._frame_name

    @property
    def frame_descriptor(self) -> FrameDescriptor:
        """Return the live frame descriptor reference."""
        self.check_cleaned()
        return self._frame_descriptor

    @property
    def frame_acl_configuration(self) -> FrameACLConfiguration:
        """Return the detached ACL configuration snapshot."""
        self.check_cleaned()
        return self._frame_acl_configuration

    @property
    def compiled_access_surface(self) -> CompiledFrameACLAccessSurface:
        """Return the detached compiled access surface."""
        self.check_cleaned()
        return self._compiled_access_surface

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached metadata copy."""
        self.check_cleaned()
        return dict(self._metadata)
