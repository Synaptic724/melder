"""M1: refuse an Aether spell-id regime change while frames exist; restore stage 1 reports it (melder_0, 2026-09-29)."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])


def patch(rel: str, edits: list[tuple[str, str]]) -> None:
    path = ROOT / rel
    raw = path.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        assert text.count(old) == 1, (rel, old[:70], text.count(old))
        text = text.replace(old, new, 1)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("patched", rel)


AETHER_CONFIGURE_OLD = '''            - Type-checked: a non-`AetherConfiguration` raises `TypeError`.
            - Replaces any previously installed configuration outright.

        Threading:
            Unsynchronized read; a snapshot only.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(configuration, AetherConfiguration):
            raise TypeError("configuration must be an AetherConfiguration instance.")
        self._configuration = configuration
        self._configured = True
'''
AETHER_CONFIGURE_NEW = '''            - Type-checked: a non-`AetherConfiguration` raises `TypeError`.
            - Replaces any previously installed configuration outright.
            - SEALED REGIME (0.2.8209): while any frame exists the spell-id regime
              was sealed when the first frame was born and is in force; a
              configuration whose `process_wide_unique_spell_ids` differs is
              refused and nothing is installed, so `configuration` can never
              report a regime that does not apply. With no frame, any regime is
              accepted and the next first frame seals it.

        Threading:
            The regime check and the install run under the Aether lock that frame
            birth holds, so a concurrent first frame either seals from this
            configuration or is seen by the check.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the object has been cleaned, or frames exist and the
                configuration's spell-id regime differs from the sealed one.
            TypeError: If `configuration` is not an `AetherConfiguration`.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(configuration, AetherConfiguration):
            raise TypeError("configuration must be an AetherConfiguration instance.")
        with self._lock:
            self._refuse_regime_change_while_frames_exist(configuration)
            self._configuration = configuration
            self._configured = True
'''

AETHER_ACTIVATE_OLD = '''            - Refuses when nothing is configured, so the two failure modes are
              distinct: "not configured" and "configuration not activated".

        Threading:
            State transition applied under the Aether lock.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If Aether is not configured, or the installed
                configuration has not been activated.
            TypeError: If a supplied configuration is not an `AetherConfiguration`.

        Returns:
            None.
        """
        self.check_cleaned()
        if configuration is not None:
            self.configure(configuration)
        if not self._configured or self._configuration is None:
            raise RuntimeError("Aether is not configured.")
        if not self._configuration.activated:
            raise RuntimeError(
                "AetherConfiguration must be activated before activating Aether."
            )
        self._configuration.validate()
'''
AETHER_ACTIVATE_NEW = '''            - Refuses when nothing is configured, so the two failure modes are
              distinct: "not configured" and "configuration not activated".
            - Re-checks the SEALED REGIME (0.2.8209): an installed configuration
              that was still mutable when installed can have its
              `process_wide_unique_spell_ids` changed afterwards, so activation
              refuses it while frames exist exactly as `configure()` would.

        Threading:
            The regime check runs under the Aether lock; the rest of the state
            transition is unchanged.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If Aether is not configured, the installed
                configuration has not been activated, or frames exist and its
                spell-id regime differs from the sealed one.
            TypeError: If a supplied configuration is not an `AetherConfiguration`.

        Returns:
            None.
        """
        self.check_cleaned()
        if configuration is not None:
            self.configure(configuration)
        if not self._configured or self._configuration is None:
            raise RuntimeError("Aether is not configured.")
        if not self._configuration.activated:
            raise RuntimeError(
                "AetherConfiguration must be activated before activating Aether."
            )
        with self._lock:
            self._refuse_regime_change_while_frames_exist(self._configuration)
        self._configuration.validate()
'''

AETHER_HELPER_ANCHOR = '''    def _apply_configuration_to_utility_system(self) -> None:
'''
AETHER_HELPER_NEW = '''    def _refuse_regime_change_while_frames_exist(
            self,
            configuration: AetherConfiguration,
    ) -> None:
        """
        Internal

        Refuse a configuration whose spell-id regime differs from the sealed one.

        Purpose:
            The regime (`_process_wide_unique_spell_ids`) is sealed when the first
            frame is born and never re-read while frames exist, because spell ids
            already registered were allocated under it. A configuration saying
            otherwise would be reported by `configuration` without ever applying.

        Contract:
            - The caller holds the Aether lock, so no frame is born or retired
              between this check and the caller's install or activation.
            - No frame: returns without reading anything - any regime may still
              be installed, and the next first frame seals it.
            - Frames exist: returns only when
              `bool(configuration.process_wide_unique_spell_ids)` equals the
              sealed value; otherwise raises and changes nothing.

        Args:
            configuration: The configuration about to be installed or activated.

        Raises:
            RuntimeError: Frames exist and the configuration's regime differs.
            TypeError: The configuration's stored regime value is not a bool
                (its defensive property refuses it).

        Returns:
            None.
        """
        if not self._aetheric_frames:
            return
        requested = bool(configuration.process_wide_unique_spell_ids)
        sealed = self._process_wide_unique_spell_ids
        if requested != sealed:
            raise RuntimeError(
                "Aether's spell-id regime is sealed while frames exist: "
                f"process_wide_unique_spell_ids is {sealed}. A configuration with "
                f"process_wide_unique_spell_ids={requested} would be reported without "
                "ever applying, so it is refused. Install it before the first "
                "Spellbook creates a frame, or keep "
                f"process_wide_unique_spell_ids={sealed}."
            )

    def _apply_configuration_to_utility_system(self) -> None:
'''

COLLAPSE_OLD = '''            - Installs `AetherConfiguration().with_defaults()` and FREEZES it, so
              the regime cannot be changed afterwards by any path.
'''
COLLAPSE_NEW = '''            - Installs `AetherConfiguration().with_defaults()` and FREEZES it, so
              the regime cannot be changed afterwards by any path. `configure()`
              and `activate()` refuse a configuration with a different regime
              while frames exist (0.2.8209), so the installed configuration
              always reports the regime in force.
'''

patch("aether/aether.py", [
    (AETHER_CONFIGURE_OLD, AETHER_CONFIGURE_NEW),
    (AETHER_ACTIVATE_OLD, AETHER_ACTIVATE_NEW),
    (AETHER_HELPER_ANCHOR, AETHER_HELPER_NEW),
    (COLLAPSE_OLD, COLLAPSE_NEW),
])

RESTORE_DOC_OLD = '''        Contract:
            - A live, already-configured Aether is respected: the recorded
              payload is reported as skipped, never force-applied.
'''
RESTORE_DOC_NEW = '''        Contract:
            - A live, already-configured Aether is respected: the recorded
              payload is reported as skipped, never force-applied.
            - A live world whose spell-id regime is already sealed (frames
              exist) keeps it: a recorded configuration with a different
              `process_wide_unique_spell_ids` is reported as
              `live_aether_regime_sealed_recorded_payload_skipped` and not
              applied (0.2.8209; Aether refuses it anyway).
'''
RESTORE_BODY_OLD = '''        configuration, reload_report = (
            AetherConfiguration.from_recorded_payload(payload)
        )
        for missing_key in reload_report["missing"]:
'''
RESTORE_BODY_NEW = '''        configuration, reload_report = (
            AetherConfiguration.from_recorded_payload(payload)
        )
        live_configuration = aether.configuration
        if (
                aether.list_frame_names()
                and live_configuration is not None
                and live_configuration.process_wide_unique_spell_ids
                != configuration.process_wide_unique_spell_ids
        ):
            # The live regime was sealed by its first frame and ids already
            # registered were allocated under it; the recorded regime cannot
            # apply here, so it is reported instead of installed.
            configuration.cleanup()
            self._report.add_shortfall(
                "aether", "root",
                "live_aether_regime_sealed_recorded_payload_skipped",
            )
            return
        for missing_key in reload_report["missing"]:
'''
patch("crystallizer/crystal_loader_system/restore_engine.py", [
    (RESTORE_DOC_OLD, RESTORE_DOC_NEW),
    (RESTORE_BODY_OLD, RESTORE_BODY_NEW),
])
