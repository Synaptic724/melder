"""Apply M2 of the cache-save fix to spellbook.py and spell.py (melder_0, 2026-10-24; the owner's go, Note 21).

Anchored read-modify-write: every anchor must match exactly once in its file or nothing is written.
`Spellbook._emit_cache_file_if_required` returns what `CachingSystem.emit()` returned (a refused save is False and
leaves the flag cleared; any other error still restores the flag and propagates); the docstrings of it,
`Spellbook._emit_cache_file` and `Spell.emit_cache_file` say when each returns False (patch
cache_save_best_effort_2026_10_24, component_patch_spellbook_cache_save.md).
"""
import pathlib
import sys

ROOT = pathlib.Path.home() / "mnt/melder_private/src/melder/aether/spellbook"
SPELLBOOK = ROOT / "spellbook.py"
SPELL = ROOT / "spell.py"


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        sys.exit(f"ANCHOR {label}: found {count}")
    return text.replace(old, new)


def spellbook(text: str) -> str:
    text = once(text, """\
        Contract:
            - Returns early when no new cache was staged since the last emit.
            - Emits at most once per staged operation window.
            - Restores the emit-required flag when file emission fails so a
              later caller can retry.

        Returns:
            bool:
                True when a cache file emit occurred, otherwise False.
        \"\"\"
""", """\
        Contract:
            - Returns early when no new cache was staged since the last emit.
            - Emits at most once per staged operation window: the flag is
              cleared under the Book lock before the save.
            - A save the operating system refuses is not an error (the bundle
              is an accelerator): `CachingSystem.emit()` logs it and returns
              False, the flag stays cleared - no meld retries the save or
              waits on it - and the payloads stay staged in memory, so the
              next staging or conjure saves them. Every meld door calls this
              after building its object, so a refused save never fails a
              meld.
            - Any other exception from the save restores the emit-required
              flag, so a later caller can retry, and propagates: it would be
              a Melder defect, not an I/O refusal.

        Returns:
            bool:
                True when the cache file was written; False when nothing was
                staged since the last save or the operating system refused the
                save.
        \"\"\"
""", "if_required docstring")
    text = once(text, """\
        try:
            self._get_or_create_caching_system().emit()
            return True
        except Exception:
""", """\
        try:
            return self._get_or_create_caching_system().emit()
        except Exception:
""", "if_required body")
    text = once(text, """\
        Contract:
            - Returns early when the spell cache policy bit is disabled.
            - Requires the spell to belong to this Spellbook.
            - Emits the current `CachingSystem` in-memory state to disk.

        Args:
            spell:
                Spell requesting the Spellbook-owned cache file emit.

        Returns:
            bool:
                True when the cache file was emitted, otherwise False.
        \"\"\"
""", """\
        Contract:
            - Returns early when the spell cache policy bit is disabled.
            - Requires the spell to belong to this Spellbook.
            - Saves the current `CachingSystem` in-memory state through
              `_emit_cache_file_if_required`, so it writes only when cache was
              staged since the last save, and a save the operating system
              refuses returns False (logged by the cache utility) instead of
              raising.

        Args:
            spell:
                Spell requesting the Spellbook-owned cache file emit.

        Returns:
            bool:
                True when the cache file was written; False when caching is
                off for the spell, nothing was staged since the last save, or
                the save was refused.

        Raises:
            RuntimeError:
                If the spell does not belong to this Spellbook.
        \"\"\"
""", "emit_cache_file docstring")
    return text


def spell(text: str) -> str:
    return once(text, """\
        Emit the Spellbook-owned cache file for this spell's current cache state.

        Purpose:
            Provide one spell-facing entrypoint for forcing the current
            Spellbook-owned in-memory cache state to disk.

        Contract:
            - Returns early when spell-level cache policy is disabled.
            - Delegates the real file emit to the owning Spellbook.
            - Requires the spell to still have a live owning Spellbook.

        Returns:
            bool:
                True when the Spellbook cache file was emitted, otherwise False.
""", """\
        Emit the Spellbook-owned cache file for this spell's current cache state.

        Purpose:
            Provide one spell-facing entrypoint for saving the current
            Spellbook-owned in-memory cache state to disk.

        Contract:
            - Returns early when spell-level cache policy is disabled.
            - Delegates the real file emit to the owning Spellbook, which
              writes only when cache was staged since its last save.
            - Requires the spell to still have a live owning Spellbook.
            - A save the operating system refuses (a read-only cache folder,
              a full disk, or on Windows a bundle another handle holds open)
              does not raise: the Spellbook's cache utility logs it, the
              staged cache stays in memory for the next save, and this call
              returns False.

        Returns:
            bool:
                True when the Spellbook cache file was written; False when
                caching is off, nothing was staged since the last save, or the
                save was refused.
""", "spell emit_cache_file docstring")


def main() -> None:
    staged = {}
    for path, edit in ((SPELLBOOK, spellbook), (SPELL, spell)):
        text = edit(path.read_text(encoding="utf-8"))
        if "\r" in text:
            sys.exit(f"CR {path.name}")
        compile(text, str(path), "exec")
        staged[path] = text
    for path, text in staged.items():
        before = len(path.read_text(encoding="utf-8").splitlines())
        path.write_text(text, encoding="utf-8", newline="\n")
        print("wrote", path.name, before, "->", len(text.splitlines()), "lines")


if __name__ == "__main__":
    main()
