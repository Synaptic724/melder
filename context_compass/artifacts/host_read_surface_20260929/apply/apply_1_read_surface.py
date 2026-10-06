"""Insert the host read surface (host_read_surface_2026_09_29): Aether frame lookups and four read-only accessors.

Additions only. Each block goes before an exact anchor line, with that line's own line ending, so CRLF, LF and
mixed files keep their endings. Refuses to run twice (the new symbols must be absent).
Run from the repository root: python context_compass/artifacts/host_read_surface_20260929/apply/apply_1_read_surface.py
"""
import pathlib

AETHER_BLOCK = '''    def find_frame(self, aetheric_frame_name: str) -> Optional[AethericFrame]:
        """
        Return the registered, live frame with this exact name, or None, without creating any frame.

        Purpose:
            Let a host that creates frames (by constructing Spellbooks) find them again without reading Aether's
            private registry. The frame-scoped calls such as `get_conduit_cloud` and the conduit lookups resolve
            "default" through the lazy creation path, so asking them about a missing "default" creates it and,
            on a world with no frames yet, seals the Aether configuration. This lookup never does either.

        Contract:
            - NONCREATING, "default" included: an absent frame returns None. No frame is created, no plane claim
              is taken, and the Aether configuration is neither installed nor frozen.
            - Exact name match against the frame registry, which holds every frame ("default" is an ordinary
              entry once something has created it).
            - A registered frame that already reads `cleaned` (its cleanup has started but has not yet detached
              it from Aether) returns None, like a detached one.
            - Returns a borrowed reference and grants no lease. Aether owns every frame, and a Nexus removal,
              `AethericFrame.cleanup()` or `Aether.cleanup()` may clean it at any time, after which the reference
              must not be used. A later frame can reuse the name: compare identity (`is`) to tell them apart.
            - `get_frame` raises instead of returning None; `list_frame_names` lists the live names.

        Threading:
            One `dict.get` on the registry, without the Aether lock: a point-in-time answer. Taking no lock keeps
            the lookup off the Aether -> Nexus lock order used while a cleaned frame is detached.

        Args:
            aetheric_frame_name:
                Exact frame name, for example "default" or the name a Spellbook was constructed with.

        Returns:
            Optional[AethericFrame]: The live frame, or None when no live frame has this name.

        Raises:
            TypeError: If `aetheric_frame_name` is not a string.
            RuntimeError: If Aether has been cleaned.
        """
        return self._find_registered_frame(aetheric_frame_name, "find_frame")

    def get_frame(self, aetheric_frame_name: str) -> AethericFrame:
        """
        Return the registered, live frame with this exact name, or raise. Never creates a frame.

        Purpose:
            The raising counterpart of `find_frame`, for callers that expect the frame to exist.

        Contract:
            - Resolves exactly as `find_frame`: noncreating ("default" included), exact name, frames that read
              `cleaned` are absent, and the reference is borrowed with no lease.
            - The not-found message starts with "Aetheric frame '<name>' does not exist.", like the frame errors
              of the conduit lookups, and says how to create the frame or test for it without raising.

        Threading:
            As `find_frame`: one registry read, no lock.

        Args:
            aetheric_frame_name:
                Exact frame name.

        Returns:
            AethericFrame: The live frame.

        Raises:
            TypeError: If `aetheric_frame_name` is not a string.
            ValueError: If no live frame has this name.
            RuntimeError: If Aether has been cleaned.
        """
        frame = self._find_registered_frame(aetheric_frame_name, "get_frame")
        if frame is None:
            message = (
                f"Aetheric frame '{aetheric_frame_name}' does not exist. get_frame never creates a frame: "
                f"constructing a Spellbook with aetheric_frame='{aetheric_frame_name}' creates it, and "
                "find_frame(...) tests for it without raising."
            )
            self._logger.error(message, "get_frame")
            raise ValueError(message)
        return frame

    def list_frame_names(self) -> tuple[str, ...]:
        """
        Return the names of the live frames in the order they were created, without creating any frame.

        Purpose:
            Let a host see which frames exist - for example, whether constructing a Spellbook will create its
            frame or join an existing one - without reading Aether's private registry.

        Contract:
            - NONCREATING: an Aether with no frames returns an empty tuple, and "default" appears only once
              something has created it.
            - Built from one copy of the registry, so the tuple is a snapshot: frames created or cleaned later do
              not change it, and a listed frame may be gone by the time it is used - resolve it with `find_frame`.
            - Frames that already read `cleaned` are left out.
            - Order is registration order.

        Threading:
            One `dict.copy()` of the registry, without the Aether lock; the copy is atomic, so a concurrent frame
            creation cannot interrupt the listing.

        Returns:
            tuple[str, ...]: Live frame names.

        Raises:
            RuntimeError: If Aether has been cleaned.
        """
        self.check_cleaned()
        registry = self._aetheric_frames.copy()
        return tuple(name for name, frame in registry.items() if not frame.cleaned)

    def _find_registered_frame(
            self,
            aetheric_frame_name: str,
            method_name: str,
    ) -> Optional[AethericFrame]:
        """
        Internal

        Validate a frame lookup's name and read the registry without creating anything.

        Contract:
            - Shared by `find_frame` and `get_frame`, so both refuse a non-string name the same way and name the
              public call that received it.
            - Never reaches `_get_existing_frame` or `_ensure_frame`: no creation, no plane claim, no seal.

        Args:
            aetheric_frame_name:
                Name received by the public lookup.
            method_name:
                Name of the public lookup, used in the TypeError message and its log line.

        Returns:
            Optional[AethericFrame]: The live frame, or None.

        Raises:
            TypeError: If `aetheric_frame_name` is not a string.
            RuntimeError: If Aether has been cleaned.
        """
        self.check_cleaned()
        if not isinstance(aetheric_frame_name, str):
            message = (
                f"{method_name}: aetheric_frame_name must be a frame name string such as 'default'; "
                f"got {type(aetheric_frame_name).__name__}."
            )
            self._logger.error(message, "_find_registered_frame")
            raise TypeError(message)
        frame = self._aetheric_frames.get(aetheric_frame_name)
        if frame is None or frame.cleaned:
            return None
        return frame

'''

FRAME_BLOCK = '''    @property
    def shared_spellbook_configuration(self) -> Optional[SpellbookConfiguration]:
        """
        Return the frame-wide shared rich Spellbook configuration, when this frame shares one.

        Purpose:
            Public read of the configuration Spellbooks in this frame adopt while the frame posture shares the rich
            configuration, so a host can compare a configuration against it without reading `_configuration`.

        Contract:
            - Returns the configuration only while `frame_configuration.shared_framewide_spellbook_configuration` is
              True, and None otherwise: the same gate a Spellbook applies before adopting it.
            - Also None while sharing is on but no Spellbook has bound one yet. The first conjuring Spellbook binds
              its frozen configuration; later Spellbooks adopt that object.
            - Returns the live object by reference. The frame owns it and cleans it with the frame; the caller must
              not clean it.

        Threading:
            Unsynchronized reads: the posture flag (read under the posture's own lock), then the bound reference,
            which is set once under the Aether lock and not replaced while the frame lives.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            Optional[SpellbookConfiguration]: The shared configuration, or None.

        Raises:
            RuntimeError: If the frame has been cleaned.
        """
        self.check_cleaned()
        if not self._frame_configuration.shared_framewide_spellbook_configuration:
            return None
        return self._configuration

'''

POSTURE_BLOCK = '''    @property
    def frozen(self) -> bool:
        """
        Return whether this posture has been frozen (settled).

        Contract:
            - False while the posture is mutable; True once `freeze()` has succeeded. Freeze is the settlement point
              of the frame's world: every `with_*` builder refuses after it, and conjure treats an unfrozen posture
              as an unsettled world it may settle.
            - Reading it changes nothing: it never freezes or validates.

        Threading:
            Reads under `self._lock`, the lock `freeze()` holds while it sets the flag.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`; raises after the posture is cleaned.

        Returns:
            bool: True when frozen.
        """
        self.check_cleaned()
        with self._lock:
            return self._frozen

'''

BOOK_CONFIG_BLOCK = '''    @property
    def aether_frame(self) -> str:
        """
        Return the name of the Aether frame this configuration was built for.

        Contract:
            - The `aether_frame` given at construction ("default" when omitted); it never changes.
            - When a Spellbook is handed a configuration and its frame has no shared configuration to adopt, it
              refuses one whose `aether_frame` is not the Spellbook's own frame, so this is the value to compare
              before handing a configuration over.

        Threading:
            Unsynchronized read of a value fixed at construction.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            str: The frame name.

        Raises:
            RuntimeError: If the configuration has been cleaned.
        """
        self.check_cleaned()
        return self._aether_frame

    @property
    def frozen(self) -> bool:
        """
        Return whether this configuration has been frozen.

        Contract:
            - False while properties and hooks can still change; True once `freeze()` (or `finalize()` /
              `build()`) has succeeded. A configuration must be frozen before a Conduit is conjured from it.
            - Reading it changes nothing: it never freezes or validates.

        Threading:
            Reads under `self._lock`, the lock `freeze()` holds while it sets the flag.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Returns:
            bool: True when frozen.

        Raises:
            RuntimeError: If the configuration has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            return self._frozen

'''

CONDUIT_BLOCK = '''    @property
    def spellbook(self) -> Spellbook:
        """
        Public API

        Return the Spellbook this conduit resolves through.

        Contract:
            - A root conduit returns the Spellbook that conjured it, whose `conduit` property returns this root.
              A lesser returns the Spellbook it was built with, its root's. `upgrade_to_normal` rebinds the upgraded
              conduit to its new Spellbook, which this then returns.
            - BORROWED: reading it keeps nothing alive, and the caller cleans the Spellbook only if it owns it.
            - The mirror of `Spellbook.conduit`.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the conduit has been cleaned.

        Returns:
            Spellbook: The borrowed Spellbook.
        """
        self.check_cleaned()
        return self._spellbook

'''

EDITS = [
    ("src/melder/aether/aether.py", "    def list_root_conduit_ids(", 0, AETHER_BLOCK, "def find_frame("),
    ("src/melder/aether/aetheric_frame/aetheric_frame.py", "    def freeze_frame_configuration(", 0, FRAME_BLOCK,
     "def shared_spellbook_configuration("),
    ("src/melder/aether/aetheric_frame/aetheric_frame_configuration.py", "    def system_state(self) -> SystemState:",
     -1, POSTURE_BLOCK, "def frozen("),
    ("src/melder/aether/spellbook/configuration/spellbook_configuration.py",
     "    def set_property(self, key: str, value: Any) -> None:", 0, BOOK_CONFIG_BLOCK, "def aether_frame("),
    ("src/melder/aether/conduit/conduit.py", '    def get_conduit_cloud(self) -> "ConduitCloud":', 0, CONDUIT_BLOCK,
     "def spellbook("),
]

for path, anchor, offset, block, marker in EDITS:
    file = pathlib.Path(path)
    lines = file.read_bytes().decode("utf-8").splitlines(keepends=True)
    if any(marker in line for line in lines):
        raise SystemExit(f"{path}: {marker} already present; refusing to apply twice")
    hits = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == anchor]
    if len(hits) != 1:
        raise SystemExit(f"{path}: anchor found {len(hits)} times")
    at = hits[0] + offset
    if offset == -1 and lines[at].strip() != "@property":
        raise SystemExit(f"{path}: expected @property before the anchor")
    anchor_line = lines[hits[0]]
    ending = "\r\n" if anchor_line.endswith("\r\n") else "\n"
    new = [text + ending for text in block.split("\n")[:-1]]
    lines[at:at] = new
    file.write_bytes("".join(lines).encode("utf-8"))
    print(f"{path}: inserted {len(new)} lines at {at + 1} ({'CRLF' if ending == chr(13) + chr(10) else 'LF'})")
