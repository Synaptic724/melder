"""
Guard: every annotation in src/melder must evaluate on Python 3.14.

Python 3.14 evaluates annotations only when something reads them, so a broken annotation - a quoted
name joined with `|` such as `"Conduit" | None`, or a type that is never imported - imports cleanly and
fails later inside `inspect.signature`, `typing.get_type_hints`, documentation or DI tooling. These
tests run `tests/_annotation_audit_support.py` over the library and prove the audit itself catches
seeded defects without flagging valid annotations (TYPE_CHECKING-only names, self references,
class-scope names, forward references, PEP 695 parameters).
"""

import json
import pathlib
import subprocess
import sys
import textwrap
from typing import Callable, Dict, List

import pytest

from tests._annotation_audit_support import AnnotationFinding, AnnotationAudit


def _project_root() -> pathlib.Path:
    """Return the repository root (the directory holding `src/` and `tests/`)."""
    return pathlib.Path(__file__).resolve().parents[3]


def _run_dynamic_audit(src_root: pathlib.Path, package: str, tmp_path: pathlib.Path) -> List[Dict[str, object]]:
    """
    Run the dynamic pass in a fresh interpreter and return its findings.

    Contract: the dynamic pass rebinds module globals, so it never runs inside the pytest process.
    """
    out = tmp_path / f"{package}_dynamic_findings.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(_project_root() / "tests" / "_annotation_audit_support.py"),
            str(src_root),
            package,
            "--dynamic-only",
            "--json",
            str(out),
        ],
        cwd=str(_project_root()),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert out.exists(), f"dynamic audit did not run:\n{completed.stdout}\n{completed.stderr}"
    return json.loads(out.read_text(encoding="utf-8"))


def _write_control_package(root: pathlib.Path) -> pathlib.Path:
    """Write the seeded and clean control modules under `root/src/ctrl_annotations` and return `root/src`."""
    package = root / "src" / "ctrl_annotations"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "seeded.py").write_text(textwrap.dedent('''
        from typing import TYPE_CHECKING, Literal, Optional

        if TYPE_CHECKING:
            from decimal import Decimal


        class Engine:
            limit: "Engine" | None = None

            def peer(self, other: "Engine" | None) -> None: ...

            def back(self) -> None | "Engine": ...

            class Inner:
                def f(self, x: int | "Engine") -> None: ...


        module_var: "Decimal" | None = None


        def outer() -> None:
            def inner(x: Optional[Engine] | "Engine") -> None: ...


        def literal_union(mode: Literal["a" | "b"]) -> None: ...


        def in_string(x: "'Engine' | None") -> None: ...


        def undefined(x: Missing) -> None: ...
    '''), encoding="utf-8")
    (package / "clean.py").write_text(textwrap.dedent('''
        from typing import TYPE_CHECKING, Any, ClassVar, List, Literal, Optional, TypeVar

        if TYPE_CHECKING:
            from decimal import Decimal

        T = TypeVar("T")


        class Car:
            Alias: ClassVar[type] = int
            price: Decimal
            maybe: Optional["Car"] = None
            later: Truck

            def peer(self, other: Optional[Car], price: Optional[Decimal] = None) -> Optional[Car]:
                return other

            def uses_class_name(self, value: Alias) -> List["Car"]:
                return []

            def generic(self, item: T, mode: Literal["a", "b"]) -> T:
                local: "NotEvaluated" | None = None
                return item


        class Truck:
            pass


        def factory[U](value: U) -> U:
            return value


        def closure() -> None:
            from decimal import Context

            def inner(ctx: Context) -> Any:
                return ctx
    '''), encoding="utf-8")
    return root / "src"


def _render(findings: List[AnnotationFinding]) -> str:
    """Return findings one per line for assertion messages."""
    return "\n".join(finding.render() for finding in findings)


def test_library_annotations_have_no_static_defects() -> None:
    """
    Purpose: No annotation in src/melder joins a string literal with `|` or names an unbound type.
    Contract: The static pass reports zero findings.
    """
    audit = AnnotationAudit(_project_root() / "src", "melder", static=True, dynamic=False).run()

    assert audit.findings() == [], "\n" + _render(audit.findings())


def test_library_annotations_evaluate_with_type_checking_imports_bound(tmp_path: pathlib.Path) -> None:
    """
    Purpose: Every annotation owner in src/melder evaluates once its TYPE_CHECKING imports are real.
    Contract: The dynamic pass (fresh interpreter) reports zero findings.
    """
    findings = _run_dynamic_audit(_project_root() / "src", "melder", tmp_path)

    assert findings == [], "\n" + "\n".join(json.dumps(finding) for finding in findings)


def test_static_audit_reports_every_seeded_defect(tmp_path: pathlib.Path) -> None:
    """
    Purpose: The static pass catches each defect shape, wherever the annotation sits.
    Contract: Nine seeded defects are reported by kind and owner; the clean module reports nothing.
    """
    src_root = _write_control_package(tmp_path)

    findings = AnnotationAudit(src_root, "ctrl_annotations", static=True, dynamic=False).run().findings()
    reported = sorted((f.kind, f.owner) for f in findings)

    assert all(f.path.endswith("seeded.py") for f in findings), _render(findings)
    assert reported == sorted([
        ("STRING_IN_UNION", "Engine.limit"),
        ("STRING_IN_UNION", "Engine.peer(other)"),
        ("STRING_IN_UNION", "Engine.back(return)"),
        ("STRING_IN_UNION", "Engine.Inner.f(x)"),
        ("STRING_IN_UNION", "module_var"),
        ("STRING_IN_UNION", "outer.inner(x)"),
        ("STRING_IN_UNION", "literal_union(mode)"),
        ("STRING_IN_UNION", "in_string(x)"),
        ("UNDEFINED_NAME", "undefined(x)"),
    ]), _render(findings)


def test_dynamic_audit_reports_evaluation_failures_only_for_seeded_defects(tmp_path: pathlib.Path) -> None:
    """
    Purpose: The dynamic pass confirms the defects that evaluation can reach, and nothing else.
    Contract: Every EVAL_ERROR comes from seeded.py; TYPE_CHECKING-only names in clean.py evaluate.
    """
    src_root = _write_control_package(tmp_path)

    findings = _run_dynamic_audit(src_root, "ctrl_annotations", tmp_path)
    owners = sorted(str(finding["owner"]).rsplit(".", 1)[-1] for finding in findings)

    assert {finding["kind"] for finding in findings} == {"EVAL_ERROR"}
    assert all(str(finding["path"]).endswith("seeded.py") for finding in findings)
    assert owners == sorted(["seeded", "Engine", "peer", "back", "f", "literal_union", "undefined"])


class _Conduit:
    """Stand-in class for the union-shape cases."""


@pytest.mark.parametrize(
    "build",
    [
        pytest.param(lambda: "_Conduit" | None, id='"C" | None'),
        pytest.param(lambda: None | "_Conduit", id='None | "C"'),
        pytest.param(lambda: "A" | "B", id='"A" | "B"'),
        pytest.param(lambda: _Conduit | "_Conduit", id='C | "C"'),
        pytest.param(lambda: int | "_Conduit", id='int | "C"'),
        pytest.param(lambda: list[int] | "_Conduit", id='list[int] | "C"'),
    ],
)
def test_string_union_shapes_raise_when_evaluated(build: Callable[[], object]) -> None:
    """
    Purpose: Pin why STRING_IN_UNION is a defect on the supported interpreter.
    Contract: Evaluating each shape raises TypeError. A `typing.Union` operand (`Optional[X] | "Y"`) is
        deliberately absent: 3.14.7 wraps the string in a ForwardRef while 3.14.0rc2 raised, so its
        runtime outcome is build-dependent. The static pass reports it regardless (the seeded
        `outer.inner(x)` case), because the repository forbids `|` unions and quoted type names.
    """
    with pytest.raises(TypeError):
        build()
