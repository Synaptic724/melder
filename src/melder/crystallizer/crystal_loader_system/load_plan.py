"""
Declarative load plan for one mediated boot transaction (V3 unfold identity).

A LoadPlan answers "what does this restore need, at what scope?" BEFORE
anything activates: the profile, the source (checkpoint chain or formation
window), window count, and per-kind key counts - inspectable truth the
mediator builds and the engine consumes.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S4.
"""

from typing import Any, Dict, List, Optional

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

    Registration:
        MELDER KERNEL - guarded (internal manifest). A single-use value carrier
        `LoadAdmission` builds; not user-constructed or bound. access=internal.

    Subsystem Context:
        The declarative unit of THE UNFOLD: built by the `LoadAdmission` plane, fed to exactly
        one `RestoreEngine` run, then cleaned by the loader. It carries the detached replay
        `chain` plus identity/scope facts; `describe()` exposes counts and identity, never
        payload dumps, so a caller can inspect a load before it happens.

    System Context:
        Crystallizer layer (position 2). Its `scope` (`world` | `conduit` | `frame`) is the
        admission adjudication key that drives scope-aware verdict views; the carried windows
        are DETACHED replay payloads, never live runtime objects, which is what lets a load be
        inspected and gated before anything is built.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Value carrier describing one planned load. Melder kernel machinery: "
        "read it to understand the runtime, do not drive it directly."
    )

    __slots__ = (
        "_scope",
        "_profile_name",
        "_source_label",
        "_checkpoint_ids",
        "_chain",
        "_kind_key_counts",
        "_target_frame_name",
        "_skip_existing",
    )

    def __init__(
            self,
            *,
            scope: str,
            profile_name: str,
            source_label: str,
            checkpoint_ids: List[str],
            chain: List[Dict[str, object]],
            target_frame_name: Optional[str] = None,
            skip_existing: bool = False,
    ) -> None:
        """
        Initialize one declarative load plan.

        Contract:
            Copies the checkpoint-id list and outer chain list. The window
            dictionaries are already detached feedstock supplied by admission
            and are intentionally not deep-copied again. Per-kind counts come
            from distinct `(kind, key)` journal entries across all windows;
            payloads without journal rows do not inflate the summary.

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
            target_frame_name:
                Retarget provenance (S1 load-scope maturity): when the
                admission plane rewrote the window's frame identity, this
                carries the frame name the load now aims at. None = the
                recorded identity was kept. Descriptive only - the rewrite
                already happened in the DETACHED window before the plan
                was built.
            skip_existing:
                When True, host-collision blockers were downgraded to
                "skipped_existing" at admission and the engine runs its
                skip lanes (unnamed conjure fallback, cluster reuse).

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
        self._target_frame_name: Optional[str] = target_frame_name
        self._skip_existing: bool = bool(skip_existing)

    def cleanup(self) -> None:
        """
        Idempotently release the carried plan fields.

        Contract:
            Terminal for this plan; deletes only value feedstock and metadata.
            It owns no record, engine, or live runtime object.

        Returns:
            None.

        Threading:
            Called by the owning loader thread after execution or failure.

        Lifecycle / Cleanup:
            The loader cleans the plan in `finally`, including when admission
            or replay raises.
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
        del self._target_frame_name
        del self._skip_existing

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
            The returned list is the plan's carried list, not another copy,
            because the single-use engine consumes that exact feedstock.
            This property is an internal loader boundary: mutating it changes
            what execution will see. User-facing inspection belongs to
            `describe()`, which intentionally omits payload bodies.

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

    @property
    def target_frame_name(self) -> Optional[str]:
        """
        Return the retarget provenance (None = recorded identity kept).

        Returns:
            Optional[str]: The frame name this load was rewritten to aim
            at, or None when no retarget happened.
        """
        self.check_cleaned()
        return self._target_frame_name

    @property
    def skip_existing(self) -> bool:
        """
        Return whether host collisions downgrade to skip lanes.

        Returns:
            bool: True when the engine should run its skip lanes instead
            of the admission plane refusing on host-collision blockers.
        """
        self.check_cleaned()
        return self._skip_existing

    def describe(self) -> Dict[str, Any]:
        """
        Return the plan's inspectable summary (counts, never payloads).

        Contract:
            Returns fresh outer containers for checkpoint ids and kind counts.
            Replay journals and payload bodies are deliberately excluded, so
            inspection cannot mutate engine feedstock.

        Returns:
            Dict[str, Any]:
                {"scope", "profile_name", "source_label", "window_count",
                 "checkpoint_ids", "kind_key_counts", "target_frame_name",
                 "skip_existing"}.
        """
        self.check_cleaned()
        return {
            "scope": self._scope,
            "profile_name": self._profile_name,
            "source_label": self._source_label,
            "window_count": len(self._chain),
            "checkpoint_ids": list(self._checkpoint_ids),
            "kind_key_counts": dict(self._kind_key_counts),
            "target_frame_name": self._target_frame_name,
            "skip_existing": self._skip_existing,
        }
