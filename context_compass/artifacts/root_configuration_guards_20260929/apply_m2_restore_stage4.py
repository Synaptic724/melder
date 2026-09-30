"""M2 follow-through: restore stage 4 deactivates an active Nexus before activating the reloaded
configuration, because M2 makes an active Nexus refuse reconfiguration (melder_0, 2026-09-30).
Stage 3 (MutationResearch) already does the same. Line endings of the target are preserved."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])

DOC_OLD = '''            - The folded lifecycle state is later-wins truth: a final
              "disabled" replays enable-then-disable (both acts are the
              recorded history); a final "cleaned" skips the rebuild with
              an honest report (the world sealed AFTER its Nexus died).

        Returns:
            None.
        """
        if self._nexus_payload is None:
            return
'''
DOC_NEW = '''            - The folded lifecycle state is later-wins truth: a final
              "disabled" replays enable-then-disable (both acts are the
              recorded history); a final "cleaned" skips the rebuild with
              an honest report (the world sealed AFTER its Nexus died).
            - A Nexus that is ALREADY active (a live-world load) is
              deactivated first: an active Nexus refuses reconfiguration
              (0.2.8210), and a world-scope load replaces the world, so the
              deactivation is a truthful recorded act - exactly as stage 3
              does for MutationResearch.

        Returns:
            None.
        """
        if self._nexus_payload is None:
            return
'''

CODE_OLD = '''        nexus = Nexus()
        nexus.activate(configuration)
        if self._nexus_state_name == "disabled":
'''
CODE_NEW = '''        nexus = Nexus()
        # Live-world loads (LoadGate authority spans make them real): an
        # ALREADY active Nexus refuses reconfiguration, and a world-scope
        # load REPLACES the world - deactivate first (a truthful recorded
        # act, as stage 3 does for MutationResearch), then activate the
        # reloaded configuration.
        if nexus.activated:
            nexus.deactivate()
        nexus.activate(configuration)
        if self._nexus_state_name == "disabled":
'''

path = ROOT / "crystallizer/crystal_loader_system/restore_engine.py"
raw = path.read_bytes()
crlf_count = raw.count(b"\r\n")
lf_count = raw.count(b"\n")
assert crlf_count in (0, lf_count), "mixed line endings: {0} CRLF of {1}".format(crlf_count, lf_count)
text = raw.decode("utf-8").replace("\r\n", "\n")
for old, new in ((DOC_OLD, DOC_NEW), (CODE_OLD, CODE_NEW)):
    assert text.count(old) == 1, old[:70]
    text = text.replace(old, new, 1)
out = text.replace("\n", "\r\n") if crlf_count else text
path.write_bytes(out.encode("utf-8"))
print("patched restore_engine.py stage 4 ({0})".format("CRLF" if crlf_count else "LF"))
