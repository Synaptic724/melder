

from typing import Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class SpellbookCrystal(Cleanable):
    """
    Pure-data digital twin of one Spellbook's configured + binding surface.

    Purpose:
        Carry the persistable truth of one spellbook: which frame it belongs
        to, its frozen SpellbookConfiguration value surface, and the ordered
        binding declaration record. The spellbook twin is the custody host
        for the L3 children (spell crystals and the conduit): they reference
        it by `spellbook_id`, mirroring the runtime where spells bind to the
        spellbook and the conduit is conjured from it.

    Guidance:
        Use this twin as the parent record for spell custody, index membership,
        and the root conduit. `bind_order` determines replay order before
        conjure. `hook_names` are participation markers only: callable bodies do
        not cross persistence, so their presence predicts explicit restore
        shortfalls or application reattachment rather than automatic hydration.
        Resolve the record-local `spellbook_id` through the restore identity map;
        `frame_name` remains the stable parent coordinate.

    Contract:
        - Value payload only; immutable after construction (replace-on-emit).
        - Hook callables are NOT persistable: `hook_names` records their
          presence as replay-required markers so restore can report exactly
          what needs code participation instead of silently dropping hooks.
        - `bind_order` records spell_ids in emission order; restore replays
          binds in this order BEFORE conjuring the conduit (L3 rule).
        - Runtime identities (ULIDs) are RECORD-LOCAL: they express edges
          and log correlation within the recorded session only. Restore
          translates them to fresh identities (never reuses them), and
          seal fingerprinting normalizes them out so identical worlds
          compare identical across boots.

    Threading:
        Immutable-after-init; the owning PersistenceProfile serializes
        replacement.

    Lifecycle / Cleanup:
        Owned by exactly one `PersistenceProfile`. Cleanup releases configuration,
        hook markers, and bind-order values only; it never cleans the live
        spellbook, conduit, or bound spells.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_spellbook_id",
        "_frame_name",
        "_configuration_payload",
        "_hook_names",
        "_bind_order",
    ]

    def __init__(
            self,
            spellbook_id: str,
            frame_name: str,
            configuration_payload: Optional[Dict[str, object]] = None,
            hook_names: Optional[List[str]] = None,
            bind_order: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize one spellbook twin from emitted configuration + bind order.

        Args:
            spellbook_id:
                Stable spellbook identity (parent edge key for L3 children).
            frame_name:
                Owning frame's canonical name (parent edge to L1).
            configuration_payload:
                Value-typed mapping of the frozen SpellbookConfiguration
                surface, hooks excluded. None is treated as empty.
            hook_names:
                Names of registered hook slots at emission time; these are
                replay-required markers (callables cannot hydrate).
            bind_order:
                spell_ids in bind emission order; replayed before conjure.

        Returns:
            None.

        Raises:
            ValueError:
                If `spellbook_id` or `frame_name` is empty.
        """
        super().__init__()
        if not spellbook_id:
            raise ValueError(
                "SpellbookCrystal requires a non-empty spellbook_id; "
                "L3 children anchor on it."
            )
        if not frame_name:
            raise ValueError(
                "SpellbookCrystal requires a non-empty frame_name; "
                "the twin tree anchors spellbooks under their frame."
            )
        self._spellbook_id: str = spellbook_id
        self._frame_name: str = frame_name
        self._configuration_payload: Dict[str, object] = (
            dict(configuration_payload) if configuration_payload else {}
        )
        self._hook_names: List[str] = list(hook_names) if hook_names else []
        self._bind_order: List[str] = list(bind_order) if bind_order else []

    def cleanup(self) -> None:
        """
        Release owned fields and mark the twin cleaned.

        Contract:
            - Idempotent; del posture (no tombstones).
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._spellbook_id
        del self._frame_name
        del self._configuration_payload
        del self._hook_names
        del self._bind_order

    @property
    def spellbook_id(self) -> str:
        """
        Return the stable spellbook identity this twin mirrors.

        Returns:
            str:
                Spellbook id (parent edge key for spell crystals + conduit).
        """
        self.check_cleaned()
        return self._spellbook_id

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame's canonical name.

        Returns:
            str:
                Parent frame name (L1 edge).
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def configuration_payload(self) -> Dict[str, object]:
        """
        Return a detached copy of the recorded configuration surface.

        Returns:
            Dict[str, object]:
                Detached mapping of configured property name -> value
                (hooks excluded by contract).
        """
        self.check_cleaned()
        return dict(self._configuration_payload)

    @property
    def hook_names(self) -> List[str]:
        """
        Return the replay-required hook markers recorded at emission.

        Returns:
            List[str]:
                Hook slot names that require code participation at restore.
        """
        self.check_cleaned()
        return list(self._hook_names)

    @property
    def bind_order(self) -> List[str]:
        """
        Return spell_ids in recorded bind order.

        Returns:
            List[str]:
                Ordered spell_ids; restore replays binds in this order.
        """
        self.check_cleaned()
        return list(self._bind_order)

    def describe(self) -> Dict[str, object]:
        """
        Return a detached, serialization-ready snapshot of this twin.

        Returns:
            Dict[str, object]:
                Plain-value payload (the cached-item form for this twin).
        """
        self.check_cleaned()
        return {
            "twin_kind": "spellbook",
            "spellbook_id": self._spellbook_id,
            "frame_name": self._frame_name,
            "configuration_payload": dict(self._configuration_payload),
            "hook_names": list(self._hook_names),
            "bind_order": list(self._bind_order),
        }
