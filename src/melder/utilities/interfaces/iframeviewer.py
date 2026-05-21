from contextlib import contextmanager
from typing import Any, Iterator, List, Optional, Protocol, Tuple, runtime_checkable
import threading

from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor
from melder.utilities.interfaces.iconduitrecord import IConduitRecord
from melder.utilities.interfaces.ispellrecord import ISpellRecord
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IFrameViewer(ICleanable, Protocol):
    """
    Interface for the public Rift-backed frame viewer host.
    """

    def list_frame_names(self) -> List[str]:
        """
        Return the hosted frame names currently visible through this viewer.
        """
        ...

    def get_view_frame(self, frame_name: Optional[str] = None) -> object:
        """
        Return the frame-scoped helper for one hosted frame.
        """
        ...

    def get_view_multiframe(self) -> object:
        """
        Return the cross-frame helper surface for this viewer host.
        """
        ...

    _rift: Any

    @property
    def _lock(self) -> threading.RLock:
        """
        Return the shared viewer lock used by borrowed helper surfaces.
        """
        ...

    def _get_required_frame_descriptor(self, frame_name: str) -> FrameDescriptor:
        """
        Return one hosted frame descriptor for the requested frame name.
        """
        ...

    @contextmanager
    def _entered_view_action(self, *, action_name: str) -> Any:
        """
        Enter one viewer action-hook scope for a borrowed helper surface.
        """
        ...

    def _get_frame_names_for_query(
            self,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the concrete frame names selected for one viewer query.
        """
        ...

    def _iter_conduit_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[IConduitRecord]:
        """
        Yield descriptor-owned conduit records for the selected frame scope.
        """
        ...

    def _iter_spell_records(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> Iterator[ISpellRecord]:
        """
        Yield descriptor-owned spell records for the selected frame scope.
        """
        ...

    def _build_spell_source_id(self, spell_record: ISpellRecord) -> str:
        """
        Build one published spell source id from a spell record.
        """
        ...

    def _normalize_spellframe_value(self, spellframe: object) -> Optional[str]:
        """
        Return one stable string view of a spellframe value.
        """
        ...

    def _get_required_spell_record(
            self,
            spell_source_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ISpellRecord]:
        """
        Return the resolved frame name plus one required spell record.
        """
        ...

