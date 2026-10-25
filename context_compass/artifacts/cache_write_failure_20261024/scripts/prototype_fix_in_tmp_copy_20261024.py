"""Throwaway prototype of fix directions 1 and 2, applied to a /tmp COPY of the tree only (melder_0, 2026-10-24).

Not a change to the repository: it rewrites /tmp/m0_mq/regress/src so the regression tests of
TASK-2026-10-24-cache_file_write_failure_fails_meld can be shown to pass once the save tolerates the OS, and so the
existing tests' reaction to that contract can be measured before the fix is planned. The real fix waits for the
owner's go and goes through the patch docs.

The prototype: `CachingSystem.emit()` returns a bool and never raises OSError - the temp file is named per writer
(pid and thread), a refused rename is retried on Windows only, a failed save removes its temp file, logs a warning
and returns False; `Spellbook._emit_cache_file_if_required` returns what `emit()` returned and leaves the flag
cleared after an OS refusal (any other exception keeps today's restore-and-raise).
"""
import pathlib
import sys

COPY = pathlib.Path("/tmp/m0_mq/regress/src/melder")


def edit(rel: str, pairs: list) -> None:
    path = COPY / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if text.count(old) != 1:
            sys.exit(f"ANCHOR {rel}: {old[:70]!r} found {text.count(old)}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
    print("prototyped", path)


def main() -> None:
    if not str(COPY).startswith("/tmp/"):
        sys.exit("refusing: the prototype edits the /tmp copy only")
    edit("utilities/caching_system/caching_system.py", [
        ("import logging\nimport marshal\nimport sys\nimport threading\n",
         "import logging\nimport marshal\nimport os\nimport sys\nimport threading\nimport time\n"),
        ("    BUNDLE_SUFFIX: ClassVar[str] = \".meldercache\"\n",
         "    BUNDLE_SUFFIX: ClassVar[str] = \".meldercache\"\n"
         "    REPLACE_ATTEMPTS: ClassVar[int] = 5\n"
         "    REPLACE_RETRY_DELAY_SECONDS: ClassVar[float] = 0.01\n"),
        ("    def emit(self) -> None:\n", "    def emit(self) -> bool:\n"),
        ("        with self._lock:\n            self._write_current_cache_to_disk_locked()\n",
         "        with self._lock:\n            return self._write_current_cache_to_disk_locked()\n"),
        ("    def _write_current_cache_to_disk_locked(self) -> None:\n",
         "    def _write_current_cache_to_disk_locked(self) -> bool:\n"),
        ("        serialized_cache_data = marshal.dumps(cache_data)\n"
         "        bundle_path = self._bundle_path\n"
         "        bundle_path.parent.mkdir(parents=True, exist_ok=True)\n"
         "        temp_bundle_path = bundle_path.with_suffix(\n"
         "            self.BUNDLE_SUFFIX + \".tmp\"\n"
         "        )\n"
         "        temp_bundle_path.write_bytes(serialized_cache_data)\n"
         "        temp_bundle_path.replace(bundle_path)\n"
         "        self._cache_data = cache_data\n",
         "        serialized_cache_data = marshal.dumps(cache_data)\n"
         "        bundle_path = self._bundle_path\n"
         "        temp_bundle_path = bundle_path.with_name(\n"
         "            f\"{bundle_path.name}.{os.getpid()}.{threading.get_ident()}.tmp\"\n"
         "        )\n"
         "        try:\n"
         "            bundle_path.parent.mkdir(parents=True, exist_ok=True)\n"
         "            temp_bundle_path.write_bytes(serialized_cache_data)\n"
         "            self._replace_bundle_locked(temp_bundle_path, bundle_path)\n"
         "        except OSError as error:\n"
         "            try:\n"
         "                temp_bundle_path.unlink(missing_ok=True)\n"
         "            except OSError:\n"
         "                pass\n"
         "            self._logger.warning(\n"
         "                f\"Could not save the creation-cache bundle '{bundle_path}': {error}.\",\n"
         "                \"_write_current_cache_to_disk_locked\",\n"
         "            )\n"
         "            return False\n"
         "        self._cache_data = cache_data\n"
         "        return True\n"
         "\n"
         "    def _replace_bundle_locked(self, temp_bundle_path: Path, bundle_path: Path) -> None:\n"
         "        attempts = self.REPLACE_ATTEMPTS if sys.platform == \"win32\" else 1\n"
         "        for attempt in range(1, attempts + 1):\n"
         "            try:\n"
         "                temp_bundle_path.replace(bundle_path)\n"
         "                return\n"
         "            except PermissionError:\n"
         "                if attempt == attempts:\n"
         "                    raise\n"
         "                time.sleep(self.REPLACE_RETRY_DELAY_SECONDS * attempt)\n"),
    ])
    edit("aether/spellbook/spellbook.py", [
        ("        try:\n"
         "            self._get_or_create_caching_system().emit()\n"
         "            return True\n"
         "        except Exception:\n",
         "        try:\n"
         "            return self._get_or_create_caching_system().emit()\n"
         "        except Exception:\n"),
    ])


if __name__ == "__main__":
    main()
