"""M3: a dynamic conjure refused by the active-Crystallizer configuration discipline is refused BEFORE the frame
posture is settled, so the refusal leaves the frame as it was (melder_0, 2026-09-30).

Adds Spellbook._effective_conjure_mode (pure prediction of settlement) and
Spellbook._refuse_recorded_conjure_after_mutable_binds (the discipline check, moved out of the transaction window
with its comment). conjure() runs the check on the predicted mode before settling; the window keeps the same check
on the settled mode, which only fires if another Book settled the shared frame in between. Line endings kept.
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])

SETTLE_DOC_OLD = '''            - SETTLED world (posture frozen/explicit): every conjure
              INHERITS the world's mode; the flag never polices - dynamic-
              only operations fail later at their own gates, on purpose.
        Args:
            dynamic (bool): The caller's requested mode (settlement input
'''
SETTLE_DOC_NEW = '''            - SETTLED world (posture frozen/explicit): every conjure
              INHERITS the world's mode; the flag never polices - dynamic-
              only operations fail later at their own gates, on purpose.
            - `_effective_conjure_mode` predicts this result WITHOUT settling
              so `conjure()` can refuse before settlement (0.2.8211); the two
              must stay in lockstep.
        Args:
            dynamic (bool): The caller's requested mode (settlement input
'''

HELPERS_ANCHOR = '''        return frame_configuration.system_state is SystemState.dynamic

    def conjure(
'''
HELPERS_NEW = '''        return frame_configuration.system_state is SystemState.dynamic

    def _effective_conjure_mode(self, dynamic: bool) -> bool:
        """
        Internal

        Predict the conjure mode `_settle_or_inherit_conjure_mode(dynamic)`
        would produce, without settling anything (0.2.8211).

        Purpose:
            `conjure()` refuses a conjure the recorded-world configuration
            discipline forbids BEFORE the frame posture is settled, so a
            refusal leaves the frame exactly as it was. That check needs the
            mode settlement would produce; this is that mode.

        Contract:
            - PURE: reads the frame posture and mutates nothing.
            - Missing posture -> the caller's flag (settlement returns it
              unchanged and `check_system_state` refuses later).
            - Unfrozen posture and dynamic=True -> True (settlement would
              settle the world dynamic).
            - Otherwise -> whether the posture's `system_state` is dynamic
              (the world's mode is inherited, as in settlement).
            - Mirrors `_settle_or_inherit_conjure_mode` branch for branch;
              the two must stay in lockstep.

        Threading:
            Unsynchronized reads of the frame posture. Another Book settling
            the same frame between this prediction and settlement can make
            the prediction stale; the transaction window re-checks the
            settled mode, so the discipline still holds.

        Args:
            dynamic (bool): The caller's requested mode.

        Returns:
            bool: The effective mode settlement would produce.
        """
        frame_configuration = self._aetheric_frame_configuration
        if frame_configuration is None:
            return dynamic
        if dynamic and not frame_configuration._frozen:
            return True
        return frame_configuration.system_state is SystemState.dynamic

    def _refuse_recorded_conjure_after_mutable_binds(self, dynamic: bool) -> None:
        """
        Internal

        Refuse a dynamic conjure in a recorded world (active Crystallizer)
        when binds ran while this Book's configuration was still mutable.

        Contract:
            - Raises only when `dynamic` is True, at least one bind preceded
              configuration finalization, and the Crystallizer is active.
              Automatic-mode worlds and worlds without an active Crystallizer
              are exempt, so non-recorded runtimes stay byte-identical.
            - Mutates nothing; on refusal it logs one ERROR line and raises.
            - `conjure()` calls it with the PREDICTED mode before settlement
              (0.2.8211), so a refusal leaves the frame posture untouched and
              a later automatic conjure in that frame is not forced dynamic.
              The transaction window calls it again with the SETTLED mode;
              that second call only fires if another Book settled the shared
              frame in between.

        Threading:
            Reads the early-bind count and the Crystallizer flag under the
            Spellbook lock, which callers take only after the CONJURE
            transaction claimed the Book (embargo-then-lock order); binds need
            the spellbook INTENT that transaction excludes, so the count
            cannot move during a conjure.

        Args:
            dynamic (bool): The effective conjure mode (predicted or settled).

        Returns:
            None.

        Raises:
            RuntimeError: When the discipline is violated; the message names
                how many spells were bound early and how to fix it.
        """
        with self._lock:
            # Dynamic-mode configuration discipline (crystallizer worlds):
            # a recorded world must not be born from binds that ran while
            # the configuration was still mutable -- the profile record and
            # default bootstrap would durably persist config-incoherent
            # bind truth. Automatic mode and crystallizer-off worlds are
            # exempt so non-recorded runtimes stay byte-identical.
            if (
                    dynamic
                    and self._binds_before_configuration_count > 0
                    and self._crystallizer.activated
            ):
                early_bind_count = self._binds_before_configuration_count
                self._logger.error(
                    f"conjure refused: {early_bind_count} bind(s) preceded configuration "
                    "finalization in a dynamic crystallizer world",
                    "conjure",
                )
                raise RuntimeError(
                    "[SPELLBOOK] Dynamic-mode conjure with an active Crystallizer requires the \\n"
                    f"SpellbookConfiguration to be finalized BEFORE the first bind. {early_bind_count} spell(s) \\n"
                    "were bound while the configuration was still mutable, so the recorded world \\n"
                    "(profiles, checkpoints, the default bootstrap) would persist binds that ran \\n"
                    "against unsettled configuration. Fix: build and finalize the configuration \\n"
                    "first, pass it to the Spellbook before binding, then conjure. Automatic-mode \\n"
                    "worlds and worlds without an active Crystallizer are not affected."
                )

    def conjure(
'''

CONJURE_DOC_OLD = '''        Raises:
            RuntimeError: If this Spellbook has already conjured a Conduit (only one is allowed).
            RuntimeError: If dynamic-only policies are used when `system_state` is "automatic" or when `dynamic` is False.
            ValueError: If the configuration fails validation or the policy string is invalid.
'''
CONJURE_DOC_NEW = '''        Raises:
            RuntimeError: If this Spellbook has already conjured a Conduit (only one is allowed).
            RuntimeError: If dynamic-only policies are used when `system_state` is "automatic" or when `dynamic` is False.
            RuntimeError: If the conjure would run dynamic while the Crystallizer is active and spells were
                bound before this Spellbook's configuration was finalized. Refused BEFORE the frame posture
                is settled (0.2.8211): the frame is left as it was, so an unsettled frame stays unsettled
                and a later automatic conjure there still runs automatic.
            ValueError: If the configuration fails validation or the policy string is invalid.
'''

CONJURE_BODY_OLD = '''        try:
            return self._conjure_within_transaction_window(
                policy=policy,
                dynamic=self._settle_or_inherit_conjure_mode(dynamic),
'''
CONJURE_BODY_NEW = '''        try:
            # Refuse the recorded-world configuration discipline on the mode
            # settlement WOULD produce, before settling: a refused conjure
            # must not leave its frame settled dynamic (0.2.8211).
            self._refuse_recorded_conjure_after_mutable_binds(
                self._effective_conjure_mode(dynamic)
            )
            return self._conjure_within_transaction_window(
                policy=policy,
                dynamic=self._settle_or_inherit_conjure_mode(dynamic),
'''

WINDOW_DOC_OLD = '''            - Passes `validation_warnings` to the creation system unchanged; only
              the public `conjure()` supplies it.
        Threading:
'''
WINDOW_DOC_NEW = '''            - Passes `validation_warnings` to the creation system unchanged; only
              the public `conjure()` supplies it.
            - Re-checks the recorded-world configuration discipline on the
              SETTLED mode. `conjure()` already refused it on the predicted
              mode before settlement (0.2.8211); this call only fires if
              another Book settled the shared frame in between.
        Threading:
'''

WINDOW_BODY_OLD = '''        self._conjure_dynamic_hint = dynamic
        with self._lock:
            # Dynamic-mode configuration discipline (crystallizer worlds):
            # a recorded world must not be born from binds that ran while
            # the configuration was still mutable -- the profile record and
            # default bootstrap would durably persist config-incoherent
            # bind truth. Automatic mode and crystallizer-off worlds are
            # exempt so non-recorded runtimes stay byte-identical.
            if (
                    dynamic
                    and self._binds_before_configuration_count > 0
                    and self._crystallizer.activated
            ):
                early_bind_count = self._binds_before_configuration_count
                self._logger.error(
                    f"conjure refused: {early_bind_count} bind(s) preceded configuration "
                    "finalization in a dynamic crystallizer world",
                    "conjure",
                )
                raise RuntimeError(
                    "[SPELLBOOK] Dynamic-mode conjure with an active Crystallizer requires the \\n"
                    f"SpellbookConfiguration to be finalized BEFORE the first bind. {early_bind_count} spell(s) \\n"
                    "were bound while the configuration was still mutable, so the recorded world \\n"
                    "(profiles, checkpoints, the default bootstrap) would persist binds that ran \\n"
                    "against unsettled configuration. Fix: build and finalize the configuration \\n"
                    "first, pass it to the Spellbook before binding, then conjure. Automatic-mode \\n"
                    "worlds and worlds without an active Crystallizer are not affected."
                )
            if self._conjured:
'''
WINDOW_BODY_NEW = '''        self._conjure_dynamic_hint = dynamic
        with self._lock:
            # Dynamic-mode configuration discipline (crystallizer worlds), on
            # the SETTLED mode. conjure() refused it on the predicted mode
            # before settlement; this only fires if another Book settled the
            # shared frame between that prediction and settlement.
            self._refuse_recorded_conjure_after_mutable_binds(dynamic)
            if self._conjured:
'''

path = ROOT / "aether/spellbook/spellbook.py"
raw = path.read_bytes()
crlf_count = raw.count(b"\r\n")
lf_count = raw.count(b"\n")
assert crlf_count in (0, lf_count), "mixed line endings: {0} CRLF of {1}".format(crlf_count, lf_count)
text = raw.decode("utf-8").replace("\r\n", "\n")
for old, new in (
        (SETTLE_DOC_OLD, SETTLE_DOC_NEW),
        (HELPERS_ANCHOR, HELPERS_NEW),
        (CONJURE_DOC_OLD, CONJURE_DOC_NEW),
        (CONJURE_BODY_OLD, CONJURE_BODY_NEW),
        (WINDOW_DOC_OLD, WINDOW_DOC_NEW),
        (WINDOW_BODY_OLD, WINDOW_BODY_NEW),
):
    assert text.count(old) == 1, old[:80]
    text = text.replace(old, new, 1)
out = text.replace("\n", "\r\n") if crlf_count else text
path.write_bytes(out.encode("utf-8"))
print("patched spellbook.py ({0})".format("CRLF" if crlf_count else "LF"))
