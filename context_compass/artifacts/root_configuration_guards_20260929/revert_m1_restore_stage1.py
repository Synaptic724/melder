"""Withdraw the restore stage-1 pre-check from M1 (melder_0, 2026-09-29). Executed once; kept as the record.

Why: the AetherCrystal payload records only the logger half of the Aether configuration
(channel_logger_activation_enabled and two presence flags), never process_wide_unique_spell_ids, so
AetherConfiguration.from_recorded_payload always rebuilds the default regime (True). A live Aether that stage 1
may configure (`configured` False) has always sealed the default too, because the first frame installs
AetherConfiguration().with_defaults() when nothing was configured. Stage 1 therefore never meets a regime mismatch
and the pre-check added by apply_m1_sealed_regime.py would be dead code; it is removed again, leaving
restore_engine.py identical to 0.2.8208 apart from line endings.
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
DOC = '''            - A live world whose spell-id regime is already sealed (frames
              exist) keeps it: a recorded configuration with a different
              `process_wide_unique_spell_ids` is reported as
              `live_aether_regime_sealed_recorded_payload_skipped` and not
              applied (0.2.8209; Aether refuses it anyway).
'''
BODY = '''        live_configuration = aether.configuration
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
'''
path = ROOT / "crystallizer/crystal_loader_system/restore_engine.py"
raw = path.read_bytes()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
assert text.count(DOC) == 1 and text.count(BODY) == 1
text = text.replace(DOC, "", 1).replace(BODY, "", 1)
path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
print("withdrawn")
