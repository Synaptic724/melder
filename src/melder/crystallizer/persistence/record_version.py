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
        One place that says what version the record speaks, stamps it
        into outgoing artifacts, and answers the only question readers
        need: "may this payload be read here?".

    Contract:
        - CURRENT is semantic: MAJOR breaks reader shape, MINOR adds
          additive keys (readers ignore unknowns), PATCH documents
          non-shape fixes.
        - Absent stamps read as "0.0.0" (pre-versioning artifacts are the
          oldest possible record - always readable, tolerance lanes own
          the gaps).
        - Static-only surface; never constructed.
    """

    CURRENT: ClassVar[str] = "1.0.0"
    KEY: ClassVar[str] = "record_version"

    @staticmethod
    def stamp(payload: Dict[str, object]) -> Dict[str, object]:
        """
        Stamp one outgoing artifact payload with the current version.

        Args:
            payload:
                The artifact dict being built (mutated in place for
                builder ergonomics).

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

        Args:
            version_text:
                "MAJOR.MINOR.PATCH" (missing parts read as 0).

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
            The single read gate: rehydration and reload lanes call this
            before trusting a payload's shape. Older majors (and
            pre-versioning "0.0.0") pass - the record's tolerance lanes
            own their gaps; a newer major is undefined here and refuses
            with the upgrade instruction.

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
