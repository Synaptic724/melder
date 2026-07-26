"""
Record schema versioning for the persistence mesh (owner ruling
2026-07-12: "keep version control in the structures").

Every durable artifact the mesh produces - cached checkpoint items,
formation records, emission-tap envelopes - carries a semantic version
stamp under one shared key. Readers gate on the MAJOR: an artifact
written by a NEWER major than the running code refuses loudly (its shape
is undefined here), while OLDER artifacts (including pre-versioning ones,
which read as "0.0.0") stay readable under the record's own tolerance
lanes (per-key backfill, honest shortfalls).
"""

from typing import ClassVar, Dict, Tuple


class RecordVersion:
    """
    The persistence record's schema version authority.

    Purpose:
        Define the schema version spoken by durable crystallizer artifacts,
        stamp outgoing value payloads, and gate readers before they trust an
        unfamiliar shape.

    Guidance:
        Producers should call `stamp()` only at the durable boundary. Adapters
        must preserve the existing `record_version` field rather than replacing
        it with an adapter version. Readers should call `check_readable()` before
        interpreting payload keys. An older or absent major enters compatibility
        lanes; a newer major is undefined and must refuse.

    Contract:
        - CURRENT is semantic: MAJOR breaks reader shape, MINOR adds
          additive keys (readers ignore unknowns), PATCH documents
          non-shape fixes.
        - Absent stamps read as "0.0.0" (pre-versioning artifacts are the
          oldest possible record - always readable, tolerance lanes own
          the gaps).
        - Static-only surface; never constructed.
        - Version compatibility covers schema shape, not business validity;
          normal validation and preflight still run after the version gate.

    Threading:
        Stateless class operations over caller-owned dictionaries; safe from any
        thread when the supplied payload is not concurrently mutated.

    Lifecycle / Cleanup:
        None. This class owns no runtime state or external resource.

    Registration:
        MELDER KERNEL - guarded (internal manifest). A static-only version
        authority: never constructed, never user-held, never a bind target. access=internal.

    Subsystem Context:
        The schema-version authority for THE RECORD's durable artifacts. It stamps
        outgoing value payloads (cached items, formation records, tap envelopes) at the
        durable boundary and gates readers at `from_cached_item` / load before they trust
        an unfamiliar shape; `PersistenceCrystal` and `AssetManagementSystem` call it there.

    System Context:
        Crystallizer layer of the boot order (position 2, after
        Aether|AetherUtilitySystem). MAJOR-version gating is what keeps the persistence
        format forward-safe across restores: a newer-major artifact refuses rather than
        being misread, and an absent stamp reads as the oldest ("0.0.0") into the tolerance
        lanes - the discipline that lets recorded worlds outlive the code version that
        sealed them.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. The persistence record's schema version authority. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    CURRENT: ClassVar[str] = "1.0.0"
    KEY: ClassVar[str] = "record_version"

    @staticmethod
    def stamp(payload: Dict[str, object]) -> Dict[str, object]:
        """
        Stamp one outgoing artifact payload with the current version.

        Contract:
            Mutates and returns the same dictionary. Existing version text is
            overwritten with `CURRENT`; use only while producing a new artifact,
            never while proxying an artifact created by another runtime.

        Args:
            payload:
                The outgoing artifact dictionary.

        Returns:
            Dict[str, object]: The same payload, stamped.
        """
        payload[RecordVersion.KEY] = RecordVersion.CURRENT
        return payload

    @staticmethod
    def of(payload: Dict[str, object]) -> str:
        """
        Return one payload's recorded version.

        Args:
            payload:
                Any artifact payload.

        Returns:
            str: The stamped version, or "0.0.0" for pre-versioning
            artifacts (absent/blank stamps).
        """
        recorded = payload.get(RecordVersion.KEY)
        return str(recorded) if recorded else "0.0.0"

    @staticmethod
    def parse(version_text: str) -> Tuple[int, int, int]:
        """
        Parse one semantic version string into comparable parts.

        Contract:
            Reads at most the first three dot-separated components. Missing
            minor/patch components become zero; extra components are ignored.
            Every present component must be an integer.

        Args:
            version_text:
                Semantic version text such as `MAJOR.MINOR.PATCH`.

        Returns:
            Tuple[int, int, int]: (major, minor, patch).

        Raises:
            ValueError: If a present part is not an integer.
        """
        parts = str(version_text).split(".")
        numbers = [int(part) for part in parts[:3]]
        while len(numbers) < 3:
            numbers.append(0)
        return numbers[0], numbers[1], numbers[2]

    @staticmethod
    def check_readable(
            payload: Dict[str, object],
            artifact_label: str,
    ) -> None:
        """
        Refuse artifacts written by a NEWER major than this code speaks.

        Purpose:
            The single schema read gate used before rehydration. Same/older
            majors and pre-versioning `0.0.0` pass into ordinary tolerance and
            validation lanes; a newer major refuses with an upgrade instruction.
            Minor and patch differences never refuse at this gate because they
            are additive/documentary by contract.

        Args:
            payload:
                The artifact payload about to be read.
            artifact_label:
                Teach-grade context for the refusal ("cached checkpoint
                {id}", "formation {name}", ...).

        Returns:
            None.

        Raises:
            ValueError: If the payload's major is newer than CURRENT's,
                or its stamp does not parse.
        """
        recorded = RecordVersion.of(payload)
        recorded_major = RecordVersion.parse(recorded)[0]
        current_major = RecordVersion.parse(RecordVersion.CURRENT)[0]
        if recorded_major > current_major:
            raise ValueError(
                "{0} was written by record version {1}, newer than this "
                "code's {2} - reading it here is undefined; upgrade "
                "melder before loading this record.".format(
                    artifact_label, recorded, RecordVersion.CURRENT
                )
            )
