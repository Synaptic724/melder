"""
Record schema versioning for the persistence mesh (owner ruling
2026-07-12: "keep version control in the structures").

Every durable artifact the mesh produces - cached checkpoint items,
formation records, emission-tap envelopes - carries a semantic version
stamp under one shared key. Readers gate on the MAJOR: an artifact
written by a NEWER major than the running code refuses loudly (its shape
is undefined here), and so does one older than the oldest major the code
reads (`RecordVersion.OLDEST_READABLE_MAJOR`, 5 since 5.0.0), pre-versioning
ones ("0.0.0") included; a major between the two is read under the
record's own tolerance lanes (per-key backfill, honest shortfalls).
"""

from typing import ClassVar, Dict, Tuple


class RecordVersion:
    """
    The persistence record's schema version authority.

    Purpose:
        Define the schema version spoken by durable crystallizer artifacts,
        stamp outgoing value payloads, and gate readers before they trust an
        unfamiliar shape or a record made under rules the code no longer keeps.

    Guidance:
        Producers should call `stamp()` only at the durable boundary. Adapters
        must preserve the existing `record_version` field rather than replacing
        it with an adapter version. Readers should call `check_readable()` before
        interpreting payload keys. A major from `OLDEST_READABLE_MAJOR` up to
        CURRENT's enters compatibility lanes; a newer major is undefined and must
        refuse, and an older one, absent stamps included, is refused too.

    Contract:
        - CURRENT is semantic: MAJOR breaks reader shape or fences a rule older
          records cannot promise, MINOR adds additive keys (readers ignore
          unknowns), PATCH documents non-shape fixes.
        - Absent stamps read as "0.0.0", the oldest possible record. Since
          5.0.0 every major below `OLDEST_READABLE_MAJOR` is refused at the
          read gate, so such a record is refused (the owner's call, 2026-10-25:
          "invalidate all the records").
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
        being misread, and a major below `OLDEST_READABLE_MAJOR` refuses rather than
        replaying a world the running code would not let anyone build (since 5.0.0: an
        index holding versions under two bindings).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. The persistence record's schema version authority. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    # Major 2 fenced non-resolvable capability. Major 3 additionally fences child
    # topology: older loaders would otherwise mistake a lesser row for a Book root.
    # Major 4 fences frame-scoped custody keys ("<spell_id>@<frame>", per-frame
    # spell ids): an older loader would fold one frame's copy over another's.
    # Minor 4.1 adds the spell crystal's frame kind and the Protocol coordinates
    # of a contract frame (`spellframe_kind`, `spellframe_module`,
    # `spellframe_qualname`); 4.0 readers ignore them, and a 4.0 record read by
    # a 4.1 loader rebinds frames by name as before.
    # Minor 4.2 adds a managed spell's options to its spell crystal (`managed_spell_mode`,
    # `managed_spell_limit`, `managed_spell_timeout_seconds`, `managed_spell_reset_methods`), written only
    # for `Existence.managed_spell_quantity`; 4.1 readers ignore them, and a 4.1 record holds no such keys.
    # Minor 4.3 adds the spell crystal's `binding_hash` (EPIC-2026-10-18-spell_identity_is_the_code, S2):
    # the SHA256 of the spell's binding manifest, written for every spell; 4.2 readers ignore it, and a
    # 4.2 record read by a 4.3 loader compares no binding.
    # Major 5 fences the rule that every version of a SpellIndex is bound the way its first version was
    # (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only): a record of an older major could hold an
    # index whose versions are bound at different addresses, which bind_inactive now refuses, so it is not read
    # (the owner's call, 2026-10-25: "notch the cache version and invalidate all the records"). The shape did
    # not change; OLDEST_READABLE_MAJOR is the gate.
    CURRENT: ClassVar[str] = "5.0.0"
    OLDEST_READABLE_MAJOR: ClassVar[int] = 5
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
        Refuse artifacts written by a newer major than this code speaks, or an older one than it reads.

        Purpose:
            The single schema read gate used before rehydration. A major from
            `OLDEST_READABLE_MAJOR` up to CURRENT's passes into ordinary
            tolerance and validation lanes; a newer major refuses with an
            upgrade instruction; an older major - pre-versioning `0.0.0`
            included - refuses with the reason and the remedy, to record the
            world again (since 5.0.0, the owner's call of 2026-10-25). Minor
            and patch differences never refuse at this gate because they are
            additive/documentary by contract.

        Args:
            payload:
                The artifact payload about to be read.
            artifact_label:
                Teach-grade context for the refusal ("cached checkpoint
                {id}", "formation {name}", ...).

        Returns:
            None.

        Raises:
            ValueError: If the payload's major is newer than CURRENT's or
                older than `OLDEST_READABLE_MAJOR`, or its stamp does not parse.
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
        if recorded_major < RecordVersion.OLDEST_READABLE_MAJOR:
            raise ValueError(
                "{0} was written by record version {1}, older than the oldest "
                "this melder reads ({2}.0.0). Since record version 5.0.0 every "
                "version of a SpellIndex is bound the way its first version was, "
                "and a record made before cannot promise that, so it is not read. "
                "Record the world again with this melder - a new checkpoint, "
                "formation or index graft - to keep it.".format(
                    artifact_label, recorded, RecordVersion.OLDEST_READABLE_MAJOR
                )
            )
