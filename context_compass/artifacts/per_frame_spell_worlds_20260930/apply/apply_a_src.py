"""Part A source (0.2.8213): the regime in force on Aether, in both Aether twins, in the reload lane and in stage 1."""
import sys

from apply_support import ApplySession

session = ApplySession(sys.argv[1])

AETHER = "src/melder/aether/aether.py"
session.insert_after(AETHER, '''        Returns:
            bool: True when a config is installed.
        """
        self.check_cleaned()
        return self._configured
''', '''
    @property
    def process_wide_unique_spell_ids(self) -> bool:
        """
        Return the spell-id regime in force: True when one spell_id may exist only once per process.

        Purpose:
            Say which regime governs this process without reading private state. `configuration` cannot answer it:
            before the first frame it is the policy the next first frame will seal, and after it a first frame may
            have sealed frozen defaults without the root ever being configured. The crystallizer records this value in
            the Aether twin and keys spell custody by it, and a restore uses it to tell whether a recorded regime can
            still be installed.

        Contract:
            - Once any frame exists: the regime the first frame sealed. `configure()` and `activate()` refuse any other
              while frames exist, so the answer cannot change until every frame is gone.
            - Before the first frame: the installed configuration's value (the one the next first frame seals), or
              True when nothing is installed (the default policy a first frame would install).
            - Read-only: installs, freezes and creates nothing.

        Threading:
            Lock-free point-in-time read, like the frame lookups. Frame birth seals the regime before it inserts the
            frame, both under the Aether lock, so a reader that sees a frame also sees the sealed value. The installed
            configuration is read once into a local so a concurrent `configure()` cannot swap it between the check
            and the read.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If Aether has been cleaned.
            TypeError: If the installed configuration's stored regime is no longer a bool (its defensive read).

        Returns:
            bool: True for process-wide spell ids, False for per-frame spell ids.
        """
        self.check_cleaned()
        if self._aetheric_frames:
            return self._process_wide_unique_spell_ids
        configuration = self._configuration
        if configuration is None:
            return True
        return configuration.process_wide_unique_spell_ids
''')

CONFIG = "src/melder/aether/aether_configuration.py"
session.replace(CONFIG, '''        Contract:
            - channel_logger_activation_enabled reloads from the record;
              when absent it falls to the documented default (False) and
              is reported under "missing".
''', '''        Contract:
            - channel_logger_activation_enabled reloads from the record;
              when absent it falls to the documented default (False) and
              is reported under "missing".
            - process_wide_unique_spell_ids (the spell-id regime, recorded
              since record major 4) reloads the same way; when absent (an
              older record) it keeps the default (True) and is reported
              under "missing".
''')
session.replace(CONFIG, '''        else:
            missing.append("channel_logger_activation_enabled")
''', '''        else:
            missing.append("channel_logger_activation_enabled")
        # The regime is a plain recorded value, applied before the freeze
        # below so the reloaded configuration cannot be flipped afterwards.
        if "process_wide_unique_spell_ids" in recorded_payload:
            configuration.set_process_wide_unique_spell_ids(
                bool(recorded_payload["process_wide_unique_spell_ids"])
            )
        else:
            missing.append("process_wide_unique_spell_ids")
''')
session.replace(CONFIG, '''            - Callable-bearing entries record as PRESENCE flags only (a
              record cannot carry live callables); the reload lane reports
              them as code_participation.
            - Replace-on-emit in the profile keeps exactly one root twin.
''', '''            - Callable-bearing entries record as PRESENCE flags only (a
              record cannot carry live callables); the reload lane reports
              them as code_participation.
            - Records the spell-id regime (`process_wide_unique_spell_ids`)
              so a restore can rebuild a per-frame world under per-frame ids.
            - Replace-on-emit in the profile keeps exactly one root twin.
''')
session.replace(CONFIG, '''                            "default_logger_present": (
                                self._properties["default_logger"] is not None
                            ),
                        },
''', '''                            "default_logger_present": (
                                self._properties["default_logger"] is not None
                            ),
                            "process_wide_unique_spell_ids": (
                                self._properties["process_wide_unique_spell_ids"]
                            ),
                        },
''')

UTILITY = "src/melder/aether/aether_utility_system.py"
session.replace(UTILITY, "from typing import Any, ClassVar\n", "from typing import Any, ClassVar, Optional\n")
session.replace(UTILITY, '''        Contract:
            - NO-OP before the crystallizer singleton boots or while it is
              not activated.
            - Callable-bearing entries record as PRESENCE flags only; the
              reload lane reports them as code_participation.

        Returns:
            None.
        """
        # Lazy import: this module sits below the crystallizer in the
''', '''        Contract:
            - NO-OP before the crystallizer singleton boots or while it is
              not activated.
            - Callable-bearing entries record as PRESENCE flags only; the
              reload lane reports them as code_participation.
            - Carries the Aether's spell-id regime in force: this twin
              REPLACES the configuration's own, so without it every logger
              verb would erase the recorded regime. Omitted when no live
              Aether can answer (see `_read_spell_id_regime`); a restore
              then reports it missing.

        Returns:
            None.
        """
        # Lazy import: this module sits below the crystallizer in the
''')
session.replace(UTILITY, '''                        "default_logger_present": (
                            self._default_logger is not None
                        ),
                    }
                crystallizer.emit(
                    AetherCrystal(configuration_payload=payload)
                )
            del crystallizer
''', '''                        "default_logger_present": (
                            self._default_logger is not None
                        ),
                    }
                regime = self._read_spell_id_regime()
                if regime is not None:
                    payload["process_wide_unique_spell_ids"] = regime
                crystallizer.emit(
                    AetherCrystal(configuration_payload=payload)
                )
            del crystallizer

    @staticmethod
    def _read_spell_id_regime() -> Optional[bool]:
        """
        Internal

        Return the Aether's spell-id regime in force, or None when no live Aether can answer.

        Contract:
            - Reads `Aether.process_wide_unique_spell_ids` only while the Aether singleton is initialized and its
              instance is not cleaned. Constructing `Aether()` without an initialized singleton would boot a new
              world, and Aether marks itself cleaned before it tears down frames and the crystallizer while
              `Aether()` keeps returning that instance until teardown ends - a verb called then must not read it.
            - None tells the caller to omit the key; the reload lane then reports it missing.

        Returns:
            Optional[bool]: The regime in force, or None.
        """
        # Lazy import: the Aether module imports this one at module level.
        from melder.aether.aether import Aether

        if not Aether._initialized:
            return None
        aether = Aether()
        if aether.cleaned:
            return None
        return aether.process_wide_unique_spell_ids
''')

RESTORE = "src/melder/crystallizer/crystal_loader_system/restore_engine.py"
session.replace(RESTORE, '''        Contract:
            - A live, already-configured Aether is respected: the recorded
              payload is reported as skipped, never force-applied.
            - Property failures degrade to shortfall entries (the root config
              is advisory for the world structure that follows).
        Returns:
            None.
        """
        if self._aether_payload is None:
            return
        from melder.aether.aether import Aether

        aether = Aether()
        payload = dict(
            self._aether_payload.get("configuration_payload", {})
        )
        if not payload:
            return
        if aether.configured:
''', '''        Contract:
            - A live, already-configured Aether is respected: the recorded
              payload is reported as skipped, never force-applied.
            - The recorded spell-id regime (record major 4) is installed while
              the live regime can still change - no configuration installed
              and no frame born - so the frames stage 5 births seal it.
            - When the live regime is already fixed (a configured Aether, or a
              live frame) and differs from the recorded one, a shortfall names
              both; an unconfigured Aether with frames then installs the
              recorded logger policy under the LIVE regime, so the sealed-regime
              guard never fires from a restore.
            - A payload without the regime (an older record) rebuilds the
              default regime and reports the key missing.
            - Property failures degrade to shortfall entries (the root config
              is advisory for the world structure that follows).
        Returns:
            None.
        """
        if self._aether_payload is None:
            return
        from melder.aether.aether import Aether

        aether = Aether()
        payload = dict(
            self._aether_payload.get("configuration_payload", {})
        )
        if not payload:
            return
        recorded_regime = payload.get("process_wide_unique_spell_ids")
        if aether.configured or aether.list_frame_names():
            # The live regime is fixed: a configured root is respected, and a
            # frame has sealed it. Report a recorded regime that cannot be
            # installed, and rebuild (if at all) under the live one.
            live_regime = aether.process_wide_unique_spell_ids
            if recorded_regime is not None and bool(recorded_regime) != live_regime:
                self._report_recorded_regime_not_in_force(
                    bool(recorded_regime), live_regime
                )
                payload["process_wide_unique_spell_ids"] = live_regime
        if aether.configured:
''')
session.insert_before(RESTORE, '''    def _replay_crystallizer_policy(self) -> None:
''', '''    def _report_recorded_regime_not_in_force(
            self,
            recorded_regime: bool,
            live_regime: bool,
    ) -> None:
        """
        Internal

        File the shortfall for a recorded spell-id regime the live world cannot take.

        Contract:
            - One shortfall on ("aether", "process_wide_unique_spell_ids"), whose reason names both regimes:
              `recorded_per_frame_ids_restored_under_process_wide_ids` or
              `recorded_process_wide_ids_restored_under_per_frame_ids`.
            - Called only when the live regime is fixed and differs from the recorded one.

        Args:
            recorded_regime:
                The recorded `process_wide_unique_spell_ids`.
            live_regime:
                The regime in force in the live world.

        Returns:
            None.
        """
        reason = (
            "recorded_per_frame_ids_restored_under_process_wide_ids"
            if live_regime and not recorded_regime
            else "recorded_process_wide_ids_restored_under_per_frame_ids"
        )
        self._report.add_shortfall(
            "aether", "process_wide_unique_spell_ids", reason
        )

''')

session.replace("src/melder/__version__.py", '__version__ = "0.2.8212"\n', '__version__ = "0.2.8213"\n')

for path in session.write():
    print(path)
