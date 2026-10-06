"""M4: add get_configuration_dictionary() to the four root configuration classes (melder_0, 2026-09-29)."""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])


def doc(ret: str, extra: str) -> str:
    return f'''
    def get_configuration_dictionary(self) -> {ret}:
        """
        Return a snapshot of the properties this configuration currently holds.

        Purpose:
            Let a host compare two configurations - for example a policy it was
            handed against the one installed on the root - without reading the
            private property bag.

        Contract:
            - Returns a NEW dict of every property currently set, name to value.
              Changing the returned dict never changes this configuration.
            - Values are the stored objects BY REFERENCE (no deep copy, no
              serialization){extra}
            - Never validates, freezes, activates or emits a recorded twin, and
              works in every lifecycle state until cleanup.

        Threading:
            Taken under the configuration lock, so the snapshot never sees a
            half-applied write.

        Lifecycle / Cleanup:
            Guarded by `check_cleaned()`.

        Raises:
            RuntimeError: If the configuration has been cleaned.

        Returns:
            {ret}: Property name to stored value.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._properties)
'''


BAG = "; a property that was never set is absent, not defaulted."
TARGETS = [
    ("crystallizer/configuration/crystallizer_configuration.py",
     "        self.check_cleaned()\n        return self._properties[key]\n", doc("Dict[str, object]", BAG)),
    ("mutation_research/mutation_configuration.py",
     "        self.check_cleaned()\n        return self._properties[key]\n", doc("Dict[str, object]", BAG)),
    ("nexus/configuration/nexus_configuration.py",
     "        self.check_cleaned()\n        return self._properties[key]\n", doc("Dict[str, object]", BAG)),
    ("aether/aether_configuration.py",
     '            raise TypeError(\n                "process_wide_unique_spell_ids must remain a bool."\n'
     '            )\n        return value\n',
     doc("dict[str, object]", "; all four logger/regime properties are always\n              present.")),
]

for rel, anchor, addition in TARGETS:
    path = ROOT / rel
    raw = path.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.count(anchor) == 1, (rel, text.count(anchor))
    assert "def get_configuration_dictionary" not in text, rel
    text = text.replace(anchor, anchor + addition, 1)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("patched", rel)
