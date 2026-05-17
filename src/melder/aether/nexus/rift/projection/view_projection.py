from typing import Any, Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
    """

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
            frame_descriptor: Any,
            frame_acl_configuration: Any,
            compiled_access_surface: Any,
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
        self._frame_descriptor: Any = frame_descriptor
        self._frame_acl_configuration: Any = frame_acl_configuration
        self._compiled_access_surface: Any = compiled_access_surface
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """Idempotently cleanup owned projection state."""
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
    def frame_descriptor(self) -> Any:
        """Return the live frame descriptor reference."""
        self.check_cleaned()
        return self._frame_descriptor

    @property
    def frame_acl_configuration(self) -> Any:
        """Return the detached ACL configuration snapshot."""
        self.check_cleaned()
        return self._frame_acl_configuration

    @property
    def compiled_access_surface(self) -> Any:
        """Return the detached compiled access surface."""
        self.check_cleaned()
        return self._compiled_access_surface

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached metadata copy."""
        self.check_cleaned()
        return dict(self._metadata)
