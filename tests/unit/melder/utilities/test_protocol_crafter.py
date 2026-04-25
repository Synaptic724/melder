from pathlib import Path
from uuid import uuid4

import pytest

from melder.utilities.ai_native_support_tools.protocol_crafter import (
    ProtocolCrafter,
)


class _BaseExample:
    """Base example docstring."""

    base_attr: int

    def base_method(self, value: str) -> bool:
        """Return whether the base method accepted the string."""
        return bool(value)


class _Example(_BaseExample):
    """Example docstring."""

    class_attr: str

    def __init__(self) -> None:
        self.instance_attr = 3

    def child_method(self, amount: int) -> str:
        """Return the child method result."""
        return str(amount)


def _build_temp_interface_file() -> Path:
    """
    Create one workspace-local temporary interface path for this test module.

    Returns:
        Path: Temporary interface-file path under the test tree.
    """
    temp_directory = Path("tests/unit/melder/utilities/_protocol_crafter_tmp")
    temp_directory.mkdir(parents=True, exist_ok=True)
    return temp_directory / "{0}.py".format(uuid4().hex)


def test_protocol_crafter_crafts_protocol_code_from_class() -> None:
    """
    Verify protocol generation mirrors class docs, annotations, and methods.

    Returns:
        None.
    """
    crafter = ProtocolCrafter()

    protocol_code = crafter.craft_protocol_code(_Example)

    assert "@runtime_checkable" in protocol_code
    assert "class I_Example(Protocol):" in protocol_code
    assert "Example docstring." in protocol_code
    assert "class_attr: str" in protocol_code
    assert "def child_method(self, amount: int) -> str:" in protocol_code
    assert "Return the child method result." in protocol_code
    assert "        ..." in protocol_code


def test_protocol_crafter_can_include_inheritance() -> None:
    """
    Verify inherited members are included only when requested.

    Returns:
        None.
    """
    crafter = ProtocolCrafter()

    protocol_code = crafter.craft_protocol_code(
        _Example,
        include_inheritance=True,
    )

    assert "base_attr: int" in protocol_code
    assert "def base_method(self, value: str) -> bool:" in protocol_code


def test_protocol_crafter_can_mirror_instance_attributes() -> None:
    """
    Verify instance input mirrors current instance-state attributes.

    Returns:
        None.
    """
    crafter = ProtocolCrafter()

    protocol_code = crafter.craft_protocol_code(_Example())

    assert "instance_attr: int" in protocol_code


def test_protocol_crafter_adds_protocol_to_interface_file() -> None:
    """
    Verify protocol blocks append cleanly into an interface file.

    Returns:
        None.
    """
    crafter = ProtocolCrafter()
    interface_file = _build_temp_interface_file()
    try:
        interface_file.write_text(
            "from typing import Protocol, runtime_checkable\n\n",
            encoding="utf-8",
        )
        protocol_code = crafter.craft_protocol_code(_Example)

        updated_text = crafter.add_protocol_to_interface_file(
            interface_file,
            protocol_code,
        )

        assert "class I_Example(Protocol):" in updated_text
        assert interface_file.read_text(encoding="utf-8") == updated_text
    finally:
        if interface_file.exists():
            interface_file.unlink()

def test_protocol_crafter_remove_protocol_from_interface_file() -> None:
    """
    Verify protocol block removal strips the named protocol cleanly.

    Returns:
        None.
    """
    crafter = ProtocolCrafter()
    interface_file = _build_temp_interface_file()
    try:
        interface_file.write_text(
            "\n".join(
                [
                    "from typing import Protocol, runtime_checkable",
                    "",
                    "@runtime_checkable",
                    "class IKeep(Protocol):",
                    '    """Keep protocol."""',
                    "    ...",
                    "",
                    "@runtime_checkable",
                    "class I_Example(Protocol):",
                    '    """Example protocol."""',
                    "    value: int",
                    "",
                    "    def run(self) -> str:",
                    '        """Run."""',
                    "        ...",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        updated_text = crafter.remove_protocol_from_interface_file(
            interface_file,
            "I_Example",
        )

        assert "class I_Example(Protocol):" not in updated_text
        assert "class IKeep(Protocol):" in updated_text
        assert interface_file.read_text(encoding="utf-8") == updated_text
    finally:
        if interface_file.exists():
            interface_file.unlink()

def test_protocol_crafter_rejects_duplicate_append() -> None:
    """
    Verify append rejects protocol names already present in the file.

    Returns:
        None.
    """
    crafter = ProtocolCrafter()
    interface_file = _build_temp_interface_file()
    try:
        protocol_code = crafter.craft_protocol_code(_Example)
        interface_file.write_text(protocol_code, encoding="utf-8")

        with pytest.raises(ValueError, match="already exists"):
            crafter.add_protocol_to_interface_file(interface_file, protocol_code)
    finally:
        if interface_file.exists():
            interface_file.unlink()
