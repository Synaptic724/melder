"""Step 2 of the aether_conduit_lookup_api lane: the Aether lookup family.

Replaces aether.py lines 1643-1886 (eight root-only lookups) with the frame resolver, the eight *_root_*
lookups, the NAMED get_conduit_by_name, the LIVE get_conduit_by_id and _find_live_conduit; lines 1914-1982
(private helpers) with _get_root_conduit_by_name / _get_root_conduit_by_id; points _get_conduit_by_spell_id
at the root helper; adds Optional to the typing import. Every replaced range is verified line by line first.

Usage: python apply_aether.py <tree root>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(sys.argv[1], "src/melder/aether/aether.py")

with open(PATH, "rb") as handle:
    lines = handle.read().decode("utf-8").split("\r\n")
assert all("\n" not in line for line in lines), "aether.py is expected to be CRLF throughout"


def block(name: str) -> list[str]:
    with open(os.path.join(HERE, name), encoding="utf-8") as handle:
        text = handle.read()
    assert text.endswith("\n")
    return text[:-1].split("\n")


def expect(number: int, text: str) -> None:
    actual = lines[number - 1]
    assert actual == text, f"line {number}: {actual!r} != {text!r}"


# Verify anchors (1-based line numbers of the 0.2.78 file).
expect(6, "from typing import TYPE_CHECKING, Any, ClassVar")
expect(1641, "        return self._ensure_default_frame()")
expect(1642, "")
expect(1643, "    def list_conduit_ids(")
expect(1886, "        return self._get_conduit_by_id(conduit_id, aetheric_frame_name)")
expect(1887, "")
expect(1888, "    def get_conduit_cloud(")
expect(1913, "")
expect(1914, '    def _get_conduit_by_name(self, name: str, aetheric_frame_name: str = "default") -> Conduit:')
expect(1982, '        raise ValueError(f"Conduit with signature {signature} not found.")')
expect(1983, "")
expect(1984, '    def _get_conduit_by_spell_id(self, spell_id: str, aetheric_frame_name: str = "default") -> Conduit:')
expect(2015, "        if conduit_id is not None:")
expect(2016, "            return self._get_conduit_by_id(conduit_id, aetheric_frame_name)")

# Apply bottom-up so earlier line numbers stay valid.
lines[2016 - 1] = "            return self._get_root_conduit_by_id(conduit_id, aetheric_frame_name)"
lines[2015 - 1] = (
    "        # Owners are roots: a lesser scope owns only the lifecycle of what it creates.\r\n"
    "        if conduit_id is not None:"
).replace("\r\n", "\n")
lines[1914 - 1:1982] = block("aether_block_b.txt")
lines[1643 - 1:1886] = block("aether_block_a.txt")
lines[6 - 1] = "from typing import TYPE_CHECKING, Any, ClassVar, Optional"

text = "\r\n".join(lines)
text = text.replace("\n", "\r\n").replace("\r\r\n", "\r\n")
with open(PATH, "wb") as handle:
    handle.write(text.encode("utf-8"))
print("aether.py updated;", text.count("\r\n"), "CRLF lines")
