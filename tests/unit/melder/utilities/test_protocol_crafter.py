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


def _build_temp_source_file(source_text: str) -> Path:
    """
    Create one workspace-local temporary source path for protocol-crafter tests.

    Args:
        source_text: Python source text to write into the temporary file.

    Returns:
        Path: Temporary source-file path under the test tree.
    """
    temp_directory = Path("tests/unit/melder/utilities/_protocol_crafter_tmp")
    temp_directory.mkdir(parents=True, exist_ok=True)
    source_file = temp_directory / "{0}.py".format(uuid4().hex)
    source_file.write_text(source_text, encoding="utf-8")
    return source_file


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


def test_protocol_crafter_can_write_protocol_module_from_source_file() -> None:
    """
    Verify AST-backed source generation writes a full protocol module.

    Returns:
        None.
    """
    crafter = ProtocolCrafter()
    source_file = _build_temp_source_file(
        "\n".join(
                [
                    "class Example:",
                    '    """Example docstring."""',
                    "    name: str",
                    "    _secret: int",
                    "",
                    "    def __init__(self, enabled: bool, label: str | None = None) -> None:",
                    "        self.enabled = enabled",
                    "        self.label = label",
                    "        self._private = 1",
                    "",
                    "    def chain(self, value: int, label: str | None = None) -> \"Example\":",
                    '        """Return the fluent chain result."""',
                    "        return self",
                    "",
                    "    def _helper(self) -> None:",
                '        """Private helper."""',
                "        return None",
                "",
            ]
        )
        + "\n"
    )
    output_directory = Path("tests/unit/melder/utilities/_protocol_crafter_tmp")
    output_file = output_directory / "iexample.py"
    try:
        written_path = crafter.write_protocol_module_from_source_file(
            source_file,
            "Example",
            output_directory,
        )
        generated_text = written_path.read_text(encoding="utf-8")

        assert written_path == output_file
        assert generated_text.startswith(
            "from typing import Optional, Protocol, runtime_checkable\n\n"
        )
        assert "class IExample(Protocol):" in generated_text
        assert "Example docstring." in generated_text
        assert "name: str" in generated_text
        assert "enabled: bool" in generated_text
        assert "label: Optional[str]" in generated_text
        assert "_secret" not in generated_text
        assert "_private" not in generated_text
        assert "def chain(self, value: int, label: Optional[str] = None) -> 'IExample':" in generated_text
        assert '        """\n        Return the fluent chain result.\n        """' in generated_text
        assert "def _helper" not in generated_text
    finally:
        if source_file.exists():
            source_file.unlink()
        if output_file.exists():
            output_file.unlink()


def test_protocol_crafter_can_write_joined_protocol_module() -> None:
    """
    Verify joined generation keeps only the shared class surface.

    Returns:
        None.
    """
    crafter = ProtocolCrafter()
    source_file = _build_temp_source_file(
        "\n".join(
            [
                "class Alpha:",
                "    name: str",
                "    only_alpha: int",
                "",
                "    def shared(self, value: int) -> str:",
                '        """Return the shared string."""',
                "        return str(value)",
                "",
                "    def chain(self, enabled: bool = False) -> \"Alpha\":",
                '        """Return the fluent instance."""',
                "        return self",
                "",
                "    def mismatch(self, value: int) -> None:",
                '        """Alpha mismatch."""',
                "        return None",
                "",
                "class Beta:",
                "    name: str",
                "    only_beta: int",
                "",
                "    def shared(self, value: int) -> str:",
                '        """Return the shared string."""',
                "        return str(value)",
                "",
                "    def chain(self, enabled: bool = False) -> \"Beta\":",
                '        """Return the fluent instance."""',
                "        return self",
                "",
                "    def mismatch(self, value: int) -> None:",
                '        """Beta mismatch."""',
                "        return None",
                "",
                "class Gamma:",
                "    name: str",
                "    only_gamma: int",
                "",
                "    def shared(self, value: int) -> str:",
                '        """Return the shared string."""',
                "        return str(value)",
                "",
                "    def chain(self, enabled: bool = False) -> \"Gamma\":",
                '        """Return the fluent instance."""',
                "        return self",
                "",
                "    def mismatch(self, value: str) -> None:",
                '        """Gamma mismatch."""',
                "        return None",
                "",
            ]
        )
        + "\n"
    )
    output_directory = Path("tests/unit/melder/utilities/_protocol_crafter_tmp")
    output_file = output_directory / "icommonthing.py"
    try:
        written_path = crafter.write_joined_protocol_module(
            [
                (source_file, "Alpha"),
                (source_file, "Beta"),
                (source_file, "Gamma"),
            ],
            "ICommonThing",
            output_directory,
        )
        generated_text = written_path.read_text(encoding="utf-8")

        assert written_path == output_file
        assert generated_text.startswith(
            "from typing import Protocol, runtime_checkable\n\n"
        )
        assert "class ICommonThing(Protocol):" in generated_text
        assert "name: str" in generated_text
        assert "only_alpha" not in generated_text
        assert "only_beta" not in generated_text
        assert "only_gamma" not in generated_text
        assert "def shared(self, value: int) -> str:" in generated_text
        assert "def chain(self, enabled: bool = False) -> 'ICommonThing':" in generated_text
        assert "def mismatch" not in generated_text
    finally:
        if source_file.exists():
            source_file.unlink()
        if output_file.exists():
            output_file.unlink()
