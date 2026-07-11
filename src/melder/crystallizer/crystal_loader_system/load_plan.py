"""
Declarative load plan for one mediated boot transaction (V3 unfold identity).

A LoadPlan answers "what does this restore need, at what scope?" BEFORE
anything activates: the profile, the source (checkpoint chain or formation
window), window count, and per-kind key counts - inspectable truth the
mediator builds and the engine consumes.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S4.
"""

from typing import Any, Dict, List

from melder.utilities.general_base.cleanable import Cleanable


class LoadPlan(Cleanable):
    """
    Value carrier describing one planned load.

    Purpose:
        Make every load declarative: the mediator assembles the detached
        windows plus the identity/scope facts, callers may inspect the
        plan (describe() = counts and identity, never payload dumps), and
        the engine consumes the carried chain.

    Contract:
        - Single-use and thread-confined: built by the LoadAdmission
          plane, fed to exactly one engine run, then cleaned by the
          loader.
        - `scope` is one of `world` | `conduit` | `frame` - the admission
          adjudication key (scope-aware verdict views).
        - The carried `chain` windows are DETACHED replay payloads; the
          plan never holds live runtime objects.

    Threading:
        Thread-confined by contract; no locks.

    Lifecycle / Cleanup:
        cleanup() deletes carried fields (del posture); idempotent.
    """

    __slots__ = (
        "_scope",
        "_profile_name",
        "_source_label",
        "_checkpoint_ids",
        "_chain",
        "_kind_key_counts",
    )

    def __init__(
            self,
            *,
            scope: str,
            profile_name: str,
            source_label: str,
            checkpoint_ids: List[str],
            chain: List[Dict[str, object]],
    ) -> None:
        """
        Initialize one declarative load plan.

        Args:
            scope:
                `world` | `conduit` | `frame` - drives admission
                adjudication.
            profile_name:
                Profile whose truth this load replays.
            source_label:
                Human-facing source identity (target checkpoint ULID or
                `formation-<name>`).
            checkpoint_ids:
                Chain identities in creation order (single synthetic label
                for formation windows).
            chain:
                Detached replay windows ({"journal", "payloads"} each).

        Returns:
            None.

        Raises:
            ValueError: If `scope` is not a recognized load scope.
        """
        super().__init__()
        if scope not in ("world", "conduit", "frame"):
            raise ValueError(
                "scope must be 'world', 'conduit', or 'frame'; got "
                "{0!r}.".format(scope)
            )
        self._scope: str = scope
        self._profile_name: str = profile_name
        self._source_label: str = source_label
        self._checkpoint_ids: List[str] = list(checkpoint_ids)
        self._chain: List[Dict[str, object]] = list(chain)
        # Distinct journaled keys per kind across the chain - the plan's
        # honest "what this load carries" summary (descriptive only; the
        # engine's fold remains the authoritative interpreter).
        seen_kind_keys: Dict[str, set] = {}
        for window in self._chain:
            for journal_entry in list(window.get("journal", [])):
                entry_kind = str(journal_entry[1])
                entry_key = str(journal_entry[2])
                seen_kind_keys.setdefault(entry_kind, set()).add(entry_key)
        self._kind_key_counts: Dict[str, int] = {
            kind: len(keys) for kind, keys in seen_kind_keys.items()
        }

    def cleanup(self) -> None:
        """
        Idempotently release the carried plan fields.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._scope
        del self._profile_name
        del self._source_label
        del self._checkpoint_ids
        del self._chain
        del self._kind_key_counts

    @property
    def scope(self) -> str:
        """
        Return the load scope (`world` | `conduit` | `frame`).

        Returns:
            str: The plan's scope.
        """
        self.check_cleaned()
        return self._scope

    @property
    def profile_name(self) -> str:
        """
        Return the profile whose truth this plan replays.

        Returns:
            str: Profile name.
        """
        self.check_cleaned()
        return self._profile_name

    @property
    def source_label(self) -> str:
        """
        Return the human-facing source identity for this plan.

        Returns:
            str: Target checkpoint ULID or `formation-<name>`.
        """
        self.check_cleaned()
        return self._source_label

    @property
    def checkpoint_ids(self) -> List[str]:
        """
        Return the chain identities in creation order (detached).

        Returns:
            List[str]: Checkpoint ids (or the synthetic formation label).
        """
        self.check_cleaned()
        return list(self._checkpoint_ids)

    @property
    def chain(self) -> List[Dict[str, object]]:
        """
        Return the carried replay windows (engine feedstock).

        Contract:
            The returned list object is the carried one (the engine
            consumes it once); callers other than the mediator should
            treat it as read-only.

        Returns:
            List[Dict[str, object]]: Detached replay windows.
        """
        self.check_cleaned()
        return self._chain

    @property
    def kind_key_counts(self) -> Dict[str, int]:
        """
        Return distinct journaled key counts per kind (detached).

        Returns:
            Dict[str, int]: Kind -> distinct key count.
        """
        self.check_cleaned()
        return dict(self._kind_key_counts)

    def describe(self) -> Dict[str, Any]:
        """
        Return the plan's inspectable summary (counts, never payloads).

        Returns:
            Dict[str, Any]:
                {"scope", "profile_name", "source_label", "window_count",
                 "checkpoint_ids", "kind_key_counts"}.
        """
        self.check_cleaned()
        return {
            "scope": self._scope,
            "profile_name": self._profile_name,
            "source_label": self._source_label,
            "window_count": len(self._chain),
            "checkpoint_ids": list(self._checkpoint_ids),
            "kind_key_counts": dict(self._kind_key_counts),
        }
