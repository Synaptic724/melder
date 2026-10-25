"""Apply M1 of the cache-save fix to caching_system.py (melder_0, 2026-10-24; the owner's go, Note 21).

Anchored read-modify-write: every anchor must match exactly once or nothing is written. The change makes
`CachingSystem.emit()` best-effort (bool, never OSError), names the temp file per writer, retries a refused rename on
Windows only and logs the first refused save of a bundle at WARNING, later ones at DEBUG (patch
cache_save_best_effort_2026_10_24, component_patch_caching_system.md and code_description_patch_caching_system.md).
"""
import pathlib
import sys

PATH = pathlib.Path.home() / "mnt/melder_private/src/melder/utilities/caching_system/caching_system.py"


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        sys.exit(f"ANCHOR {label}: found {count}")
    return text.replace(old, new)


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    original = text
    text = once(text, "import logging\nimport marshal\nimport sys\nimport threading\n",
                "import logging\nimport marshal\nimport os\nimport sys\nimport threading\nimport time\n", "imports")
    text = once(text, "        - `emit()` writes the current in-memory dict to disk.\n", """\
        - `emit()` writes the current in-memory dict to disk and returns True,
          or returns False when the operating system refuses the save (a
          read-only folder, a full disk, or on Windows a rename onto a bundle
          another handle holds open). A save is best-effort, like the bundle
          itself: a refused save is logged (WARNING the first time for this
          bundle, DEBUG after), removes its own temp file, never touches the
          bundle on disk and keeps every staged payload in memory for the
          next save; it never raises OSError. Each writer saves through its
          own temp file, `<conduit>.meldercache.<pid>.<thread id>.tmp`, so two
          processes sharing a frame and conduit name never share one.
""", "contract emit")
    text = once(text, """\
        - Does not rely on OS-level file locks as the primary coordination
          mechanism inside one process.
""", """\
        - Does not rely on OS-level file locks as the primary coordination
          mechanism inside one process.
        - On Windows (`RETRY_REFUSED_RENAME`) a rename refused with
          PermissionError is retried under that lock, up to
          `REPLACE_ATTEMPTS` attempts with a short growing sleep (about
          100 ms in all), so this instance's other calls may wait that long.
""", "threading")
    text = once(text, """\
        - Owns the in-memory cache dictionary and logger wrapper.
        - Does not automatically delete cache files during cleanup.
""", """\
        - Owns the in-memory cache dictionary and logger wrapper.
        - Remembers whether a refused save was already logged
          (`_refused_save_logged`); cleanup deletes it with the other owned
          slots.
        - Does not automatically delete cache files during cleanup.
""", "lifecycle")
    text = once(text, '    BUNDLE_SUFFIX: ClassVar[str] = ".meldercache"\n', '''\
    BUNDLE_SUFFIX: ClassVar[str] = ".meldercache"
    # Windows refuses a rename onto a file another handle holds open without
    # FILE_SHARE_DELETE - an on-access scanner or an indexer reading the bundle
    # just written - with PermissionError [WinError 5]; such a holder usually
    # lets go within milliseconds, so the save retries the rename there. POSIX
    # renames never refuse for sharing, so elsewhere a refusal (a read-only
    # folder) is final at once. Class-level so a test can set them.
    RETRY_REFUSED_RENAME: ClassVar[bool] = sys.platform == "win32"
    REPLACE_ATTEMPTS: ClassVar[int] = 5
    REPLACE_RETRY_DELAY_SECONDS: ClassVar[float] = 0.01
''', "class vars")
    text = once(text, '        "_cache_data",\n        "_logger",\n    ]\n',
                '        "_cache_data",\n        "_refused_save_logged",\n        "_logger",\n    ]\n', "slots")
    text = once(text, """\
            - Derives the bundle path as
              `<cache_root>/<frame_name>/<conduit_name>.meldercache` and LOADS the
              cache from disk during construction; a corrupt or version-
              mismatched bundle is treated as a cold cache, not an error.
""", """\
            - Derives the bundle path as
              `<cache_root>/<frame_name>/<conduit_name>.meldercache` and LOADS the
              cache from disk during construction; a corrupt or version-
              mismatched bundle is treated as a cold cache, not an error.
            - Starts with no refused save logged, so the first refused save of
              this bundle logs at WARNING.
""", "init contract")
    text = once(text, """\
            / f"{conduit_name}{self.BUNDLE_SUFFIX}"
        )
""", """\
            / f"{conduit_name}{self.BUNDLE_SUFFIX}"
        )
        # Set by the first refused save so later ones log at DEBUG: one WARNING
        # per bundle, however long a refusal (a read-only folder) lasts.
        self._refused_save_logged: bool = False
""", "init field")
    text = once(text, """\
            del self._cache_data
            del self._bundle_path
""", """\
            del self._cache_data
            del self._bundle_path
            del self._refused_save_logged
""", "cleanup")
    text = once(text, '''\
    def emit(self) -> None:
        """
        Write the current in-memory cache dict to disk.

        Contract:
            - Serializes under the instance lock and persists atomically (temp
              file then `replace`), so a crash mid-write never leaves a torn
              bundle. Creates the frame folder if absent.

        Returns:
            None.
        """
        with self._lock:
            self._write_current_cache_to_disk_locked()
''', '''\
    def emit(self) -> bool:
        """
        Write the current in-memory cache dict to disk, best-effort.

        Purpose:
            Persist the bundle so a later conjure can skip compilation. The
            bundle is an accelerator - a missing or unreadable one only makes
            the cache cold - so a save the operating system refuses is
            reported, never raised: no meld, conjure or explicit save fails
            because a cache file could not be written.

        Contract:
            - Serializes under the instance lock and persists atomically: the
              envelope goes to this writer's temp file
              (`<conduit>.meldercache.<pid>.<thread id>.tmp`), which is then
              renamed onto the bundle, so a crash or a refusal mid-write never
              leaves a torn bundle. Creates the frame folder if absent.
            - On Windows a rename refused with PermissionError is retried
              (`RETRY_REFUSED_RENAME`, `REPLACE_ATTEMPTS`,
              `REPLACE_RETRY_DELAY_SECONDS`); a refusal that outlasts the
              retries, and any OSError of the folder, the temp write or the
              rename, makes the save refused.
            - A refused save removes its own temp file, leaves the bundle on
              disk as it was, keeps every staged payload in memory for the
              next save and logs the refusal: WARNING with the bundle path,
              the error and the remedies the first time for this bundle,
              DEBUG after.

        Threading / Concurrency:
            - Holds the instance lock for the whole save, retries included.

        Returns:
            bool:
                True when the bundle was written; False when the operating
                system refused the save.

        Raises:
            Exception:
                Any non-OSError exception of the serialization or the write
                propagates unchanged; none is expected.
        """
        with self._lock:
            return self._write_current_cache_to_disk_locked()
''', "emit")
    text = once(text, "    def _write_current_cache_to_disk_locked(self) -> None:\n",
                "    def _write_current_cache_to_disk_locked(self) -> bool:\n", "write signature")
    text = once(text, '''\
        Contract:
            - Caller must already hold the instance lock.
            - Writes to a temp file and atomically replaces the final file.
            - Persists the release stamped when this envelope was created or
              accepted; never assigns a new release to retained old payloads.

        Returns:
            None.
        """
        cache_data = {
''', '''\
        Contract:
            - Caller must already hold the instance lock.
            - Writes this writer's temp file and atomically replaces the final
              file with it (`_replace_bundle_locked`); only that rename changes
              the bundle on disk.
            - Persists the release stamped when this envelope was created or
              accepted; never assigns a new release to retained old payloads.
            - Replaces `_cache_data` with the written envelope only after the
              rename. An OSError of the folder, the temp write or the rename
              removes the temp file this save started
              (`_discard_temp_bundle_locked`), logs the refusal
              (`_log_refused_save_locked`) and leaves `_cache_data`, with every
              staged payload, as it was.

        Returns:
            bool:
                True when the bundle was written; False when the operating
                system refused the save.
        """
        cache_data = {
''', "write docstring")
    text = once(text, """\
        serialized_cache_data = marshal.dumps(cache_data)
        bundle_path = self._bundle_path
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        temp_bundle_path = bundle_path.with_suffix(
            self.BUNDLE_SUFFIX + ".tmp"
        )
        temp_bundle_path.write_bytes(serialized_cache_data)
        temp_bundle_path.replace(bundle_path)
        self._cache_data = cache_data
""", '''\
        serialized_cache_data = marshal.dumps(cache_data)
        temp_bundle_path = self._temp_bundle_path()
        # Set just before the temp write, so a refusal of the folder never
        # tries to remove a temp file this save did not start.
        temp_started = False
        try:
            self._bundle_path.parent.mkdir(parents=True, exist_ok=True)
            temp_started = True
            temp_bundle_path.write_bytes(serialized_cache_data)
            self._replace_bundle_locked(temp_bundle_path)
        except OSError as error:
            if temp_started:
                self._discard_temp_bundle_locked(temp_bundle_path)
            self._log_refused_save_locked(error)
            return False
        self._cache_data = cache_data
        return True

    def _temp_bundle_path(self) -> Path:
        """
        Return the temp file this writer saves through, beside the bundle.

        Contract:
            - `<bundle name>.<pid>.<thread id>.tmp` in the bundle's folder:
              unique per process and thread, so two processes saving one
              bundle (a frame and conduit name shared in one install) never
              write into one temp file, and a refused save removes only its
              own.

        Returns:
            Path:
                This writer's temp-file path.
        """
        bundle_path = self._bundle_path
        return bundle_path.with_name(
            f"{bundle_path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
        )

    def _replace_bundle_locked(self, temp_bundle_path: Path) -> None:
        """
        Rename this writer's temp file onto the bundle, retrying a sharing refusal on Windows.

        Purpose:
            Windows refuses a rename onto a file another handle holds open
            without FILE_SHARE_DELETE (an on-access scanner, an indexer, a
            reader in another process) with PermissionError [WinError 5], and
            that holder usually lets go within milliseconds.

        Contract:
            - Caller must already hold the instance lock.
            - Always attempts the rename once. While `RETRY_REFUSED_RENAME` is
              True (Windows), a PermissionError is retried up to
              `REPLACE_ATTEMPTS` attempts in all, sleeping
              `REPLACE_RETRY_DELAY_SECONDS` times the attempt number between
              them; while it is False (every other platform) the first refusal
              is final.
            - Any other OSError is final at once.

        Args:
            temp_bundle_path:
                This writer's temp file, already written.

        Returns:
            None.

        Raises:
            PermissionError:
                The rename was refused on its last attempt.
            OSError:
                Any other rename failure, on its first attempt.
        """
        attempt = 1
        while True:
            try:
                temp_bundle_path.replace(self._bundle_path)
                return
            except PermissionError:
                if not self.RETRY_REFUSED_RENAME or attempt >= self.REPLACE_ATTEMPTS:
                    raise
            time.sleep(self.REPLACE_RETRY_DELAY_SECONDS * attempt)
            attempt += 1

    def _discard_temp_bundle_locked(self, temp_bundle_path: Path) -> None:
        """
        Remove this writer's temp file after a refused save.

        Contract:
            - Caller must already hold the instance lock.
            - A temp file already gone is fine (`missing_ok=True`).
            - An OSError while removing it (on Windows the holder that refused
              the rename may hold the temp file too) is logged at WARNING with
              the leftover path and never raised: the file holds nothing the
              cache needs, and the next save writes a fresh one.

        Args:
            temp_bundle_path:
                This writer's temp file.

        Returns:
            None.
        """
        try:
            temp_bundle_path.unlink(missing_ok=True)
        except OSError as error:
            self._logger.warning(
                f"Could not remove the temp cache file '{temp_bundle_path}' after a refused save: "
                f"{error}. It holds nothing the cache needs and can be deleted.",
                "_discard_temp_bundle_locked",
            )

    def _log_refused_save_locked(self, error: OSError) -> None:
        """
        Log one refused save: WARNING the first time for this bundle, DEBUG after.

        Contract:
            - Caller must already hold the instance lock, which serializes
              `_refused_save_logged`.
            - The message names the bundle and the error, says that melds are
              not affected and that the cache stays in memory for the next
              save, and gives the remedies.

        Args:
            error:
                The OSError that refused the save.

        Returns:
            None.
        """
        message = (
            f"Could not save the creation-cache bundle '{self._bundle_path}': {error}. "
            "Melds are not affected and the cache stays in memory for the next save. "
            "To persist it, make the cache folder writable (on Windows, also exclude it from "
            "real-time scanning), or turn caching off for the frame with "
            "with_system_caching_enabled(False)."
        )
        if self._refused_save_logged:
            self._logger.debug(message, "emit")
            return
        self._refused_save_logged = True
        self._logger.warning(message + " Later refused saves of this bundle log at DEBUG.", "emit")
''', "write body")
    if "\r" in text:
        sys.exit("CR")
    compile(text, str(PATH), "exec")
    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("wrote", PATH.name, len(original.splitlines()), "->", len(text.splitlines()), "lines")


if __name__ == "__main__":
    main()
