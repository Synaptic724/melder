import ast
import io
import os
import re
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import TextIO

from mypyc.build import mypycify
from setuptools import Extension, find_packages, setup


COMPILED_TOP_LEVEL_DIRECTORIES: set[str] = {
    "blueprints",
    "dag",
    "phases",
    "profiles",
    "spell_examiner",
    "spell_requirements_finder",
    "symbolic_graph",
    "system",
    "topology",
    "validation",
}

EXCLUDED_DIRECTORY_NAMES: set[str] = {
    "tests",
    "__pycache__",
}

SKIPPED_TYPECHECK_MODULES: set[str] = {
    "melder.nexus",
    "melder.crystallizer",
    "melder.mutation_research",
}

FORBIDDEN_CORE_IMPORT_ROOTS: set[str] = {
    "melder.nexus",
    "melder.crystallizer",
    "melder.mutation_research",
}

PACKAGE_EXCLUDE_PATTERNS: list[str] = [
    # If you want these removed from the installed package too, keep these.
    # If you only want them skipped from mypyc compilation but still packaged,
    # set PACKAGE_EXCLUDE_PATTERNS = [].
    "melder.nexus",
    "melder.nexus.*",
    "melder.crystallizer",
    "melder.crystallizer.*",
    "melder.mutation_research",
    "melder.mutation_research.*",
]


class MypycStrictLevel:
    def __init__(self) -> None:
        self._allowed_levels = {
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
        }

    def resolve(self) -> str:
        if len(sys.argv) > 1 and sys.argv[1] in self._allowed_levels:
            strict_level = sys.argv[1]
            del sys.argv[1]

            return strict_level

        strict_level = os.environ.get("MYPYC_STRICT_LEVEL", "1")

        if strict_level not in self._allowed_levels:
            raise ValueError(
                "MYPYC_STRICT_LEVEL must be one of: 0, 1, 2, 3, 4, 5, 6"
            )

        return strict_level


class MypycConfigWriter:
    def __init__(
            self,
            project_root: Path,
            skipped_typecheck_modules: set[str],
    ) -> None:
        self._project_root = project_root
        self._skipped_typecheck_modules = skipped_typecheck_modules
        self._config_path = self._project_root / "build" / "mypy_mypyc_melder.ini"

    @property
    def config_path(self) -> Path:
        return self._config_path

    def write(self) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = [
            "[mypy]",
            "show_error_codes = True",
            "show_column_numbers = True",
            "warn_unused_configs = False",
            "",
        ]

        for module_name in sorted(self._skipped_typecheck_modules):
            lines.extend(
                [
                    f"[mypy-{module_name}]",
                    "follow_imports = skip",
                    "ignore_errors = True",
                    "",
                    f"[mypy-{module_name}.*]",
                    "follow_imports = skip",
                    "ignore_errors = True",
                    "",
                ]
            )

        self._config_path.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )


class MypycBuild:
    def __init__(
            self,
            source_root: str,
            package_root: str,
            compiled_top_level_directories: set[str],
            excluded_directory_names: set[str],
            skipped_typecheck_modules: set[str],
            forbidden_core_import_roots: set[str],
            include_package_root_modules: bool,
    ) -> None:
        self._project_root = Path.cwd()
        self._source_root = Path(source_root)
        self._package_root = self._source_root / package_root
        self._compiled_top_level_directories = compiled_top_level_directories
        self._excluded_directory_names = excluded_directory_names
        self._skipped_typecheck_modules = skipped_typecheck_modules
        self._forbidden_core_import_roots = forbidden_core_import_roots
        self._include_package_root_modules = include_package_root_modules
        self._strict_level = MypycStrictLevel().resolve()

        self._config_writer = MypycConfigWriter(
            project_root=self._project_root,
            skipped_typecheck_modules=self._skipped_typecheck_modules,
        )
        self._config_writer.write()

    @property
    def strict_level(self) -> str:
        return self._strict_level

    @property
    def package_root(self) -> Path:
        return self._package_root

    @property
    def forbidden_core_import_roots(self) -> set[str]:
        return self._forbidden_core_import_roots

    def _common_args(self) -> list[str]:
        return [
            f"--config-file={self._config_writer.config_path}",
            "--show-error-codes",
            "--show-column-numbers",
        ]

    def _strict_base_args(self) -> list[str]:
        return [
            "--disallow-any-generics",
            "--disallow-subclassing-any",
            "--disallow-untyped-calls",
            "--disallow-untyped-defs",
            "--disallow-incomplete-defs",
            "--check-untyped-defs",
            "--disallow-untyped-decorators",
            "--warn-redundant-casts",
            "--warn-unused-ignores",
            "--warn-return-any",
            "--no-implicit-reexport",
            "--strict-equality",
            "--extra-checks",
        ]

    def _optional_error_code_args(self) -> list[str]:
        return [
            "--enable-error-code=redundant-self",
            "--enable-error-code=redundant-expr",
            "--enable-error-code=possibly-undefined",
            "--enable-error-code=truthy-bool",
            "--enable-error-code=truthy-iterable",
            "--enable-error-code=ignore-without-code",
            "--enable-error-code=unused-awaitable",
            "--enable-error-code=explicit-override",
            "--enable-error-code=mutable-override",
            "--enable-error-code=unimported-reveal",
            "--enable-error-code=exhaustive-match",
            "--enable-error-code=deprecated",
        ]

    def _is_excluded_path(self, path: Path) -> bool:
        for part in path.parts:
            if part in self._excluded_directory_names:
                return True

        return False

    def _is_included_top_level_path(self, path: Path) -> bool:
        relative_path = path.relative_to(self._package_root)

        if len(relative_path.parts) == 1:
            return self._include_package_root_modules

        top_level_directory = relative_path.parts[0]

        return top_level_directory in self._compiled_top_level_directories

    def collect_python_modules(self) -> list[str]:
        modules: list[str] = []

        for path in self._package_root.rglob("*.py"):
            if self._is_excluded_path(path):
                continue

            if not self._is_included_top_level_path(path):
                continue

            modules.append(str(path))

        modules.sort()

        return modules

    def collect_level_zero_args(self) -> list[str]:
        return [
            *self._common_args(),
        ]

    def collect_level_one_args(self) -> list[str]:
        return [
            *self._common_args(),
            "--disallow-untyped-defs",
            "--check-untyped-defs",
            "--warn-return-any",
            "--warn-no-return",
            "--warn-redundant-casts",
            "--warn-unused-ignores",
        ]

    def collect_level_two_args(self) -> list[str]:
        return [
            *self._common_args(),
            *self._strict_base_args(),
            "--warn-unreachable",
            "--strict-equality-for-none",
            "--warn-no-return",
        ]

    def collect_level_three_args(self) -> list[str]:
        return [
            *self._common_args(),
            *self._strict_base_args(),
            "--warn-unreachable",
            "--strict-equality-for-none",
            "--warn-no-return",
            "--disallow-any-unimported",
            "--disallow-any-decorated",
            "--disallow-any-explicit",
            "--disallow-any-generics",
            "--enable-error-code=redundant-self",
            "--enable-error-code=redundant-expr",
            "--enable-error-code=possibly-undefined",
            "--enable-error-code=truthy-bool",
            "--enable-error-code=truthy-iterable",
            "--enable-error-code=ignore-without-code",
            "--enable-error-code=unused-awaitable",
            "--enable-error-code=explicit-override",
        ]

    def collect_level_four_args(self) -> list[str]:
        return [
            *self._common_args(),
            *self._strict_base_args(),
            "--warn-unreachable",
            "--strict-equality-for-none",
            "--warn-no-return",
            "--disallow-any-unimported",
            "--disallow-any-expr",
            "--disallow-any-decorated",
            "--disallow-any-explicit",
            "--disallow-any-generics",
            *self._optional_error_code_args(),
            "--show-error-code-links",
        ]

    def collect_level_five_args(self) -> list[str]:
        return self.collect_level_four_args()

    def collect_level_six_args(self) -> list[str]:
        return self.collect_level_four_args()

    def collect_strict_args(self) -> list[str]:
        if self._strict_level == "0":
            return self.collect_level_zero_args()

        if self._strict_level == "1":
            return self.collect_level_one_args()

        if self._strict_level == "2":
            return self.collect_level_two_args()

        if self._strict_level == "3":
            return self.collect_level_three_args()

        if self._strict_level == "4":
            return self.collect_level_four_args()

        if self._strict_level == "5":
            return self.collect_level_five_args()

        if self._strict_level == "6":
            return self.collect_level_six_args()

        raise ValueError(
            "MYPYC_STRICT_LEVEL must be one of: 0, 1, 2, 3, 4, 5, 6"
        )

    def collect_mypyc_args(self) -> list[str]:
        modules = self.collect_python_modules()
        args = self.collect_strict_args()
        args.extend(modules)

        print(f"Using MYPYC strict level: {self._strict_level}")
        print(f"Collected mypyc modules: {len(modules)}")
        print("Compiled top-level directories:")

        for directory_name in sorted(self._compiled_top_level_directories):
            print(f"  {directory_name}")

        print("Excluded directory names:")

        for directory_name in sorted(self._excluded_directory_names):
            print(f"  {directory_name}")

        return args


class MypycPolicyViolation:
    def __init__(
            self,
            file_path: str,
            line_number: int,
            message: str,
    ) -> None:
        self._file_path = file_path
        self._line_number = line_number
        self._message = message

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def line_number(self) -> int:
        return self._line_number

    @property
    def message(self) -> str:
        return self._message


class MypycPolicyReport:
    def __init__(self, strict_level: str, violations: list[MypycPolicyViolation]) -> None:
        self._strict_level = strict_level
        self._violations = violations

    def print_report(self) -> None:
        if not self._violations:
            return

        print("")
        print("")
        print("MYPYC POLICY REPORT")
        print("===================")
        print(f"Strict level:       {self._strict_level}")
        print(f"Policy violations:  {len(self._violations)}")
        print("")

        for violation in self._violations[:200]:
            print(
                f"{violation.file_path}:{violation.line_number}: "
                f"policy-error: {violation.message}"
            )

        if len(self._violations) > 200:
            remaining = len(self._violations) - 200
            print(f"... {remaining} more policy violations omitted")

        print("")
        print("===================")
        print("END MYPYC POLICY REPORT")
        print("===================")
        print("")


class MypycPolicyChecker:
    def __init__(
            self,
            strict_level: str,
            package_root: Path,
            forbidden_core_import_roots: set[str],
    ) -> None:
        self._strict_level = strict_level
        self._package_root = package_root
        self._forbidden_core_import_roots = forbidden_core_import_roots

    def _should_run_import_wall(self) -> bool:
        return self._strict_level in {
            "5",
            "6",
        }

    def _should_run_native_decorator_wall(self) -> bool:
        return self._strict_level == "6"

    def _module_name_from_file(self, file_path: Path) -> str:
        relative_path = file_path.relative_to(self._package_root.parent)
        parts = list(relative_path.parts)
        parts[-1] = parts[-1].removesuffix(".py")

        if parts[-1] == "__init__":
            parts = parts[:-1]

        return ".".join(parts)

    def _import_root_is_forbidden(self, imported_name: str) -> bool:
        for forbidden_root in self._forbidden_core_import_roots:
            if imported_name == forbidden_root:
                return True

            if imported_name.startswith(f"{forbidden_root}."):
                return True

        return False
    def _policy_should_fail(self) -> bool:
        policy_mode = os.environ.get("MYPYC_POLICY_MODE", "").strip().lower()

        if policy_mode in {"soft", "report", "report-only", "0", "false", "no"}:
            return False

        if policy_mode in {"hard", "fail", "1", "true", "yes"}:
            return True

        return self._strict_level == "6"
    def _collect_import_wall_violations(
            self,
            file_path: Path,
            tree: ast.Module,
    ) -> list[MypycPolicyViolation]:
        violations: list[MypycPolicyViolation] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_name = alias.name

                    if self._import_root_is_forbidden(imported_name):
                        violations.append(
                            MypycPolicyViolation(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                message=(
                                    "compiled core imports forbidden subsystem "
                                    f'"{imported_name}"'
                                ),
                            )
                        )

            if isinstance(node, ast.ImportFrom):
                if node.module is None:
                    continue

                imported_name = node.module

                if self._import_root_is_forbidden(imported_name):
                    violations.append(
                        MypycPolicyViolation(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            message=(
                                "compiled core imports forbidden subsystem "
                                f'"{imported_name}"'
                            ),
                        )
                    )

        return violations

    def _class_inherits_any_name(
            self,
            class_node: ast.ClassDef,
            names: set[str],
    ) -> bool:
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                if base.id in names:
                    return True

            if isinstance(base, ast.Attribute):
                if base.attr in names:
                    return True

            if isinstance(base, ast.Subscript):
                value = base.value

                if isinstance(value, ast.Name):
                    if value.id in names:
                        return True

                if isinstance(value, ast.Attribute):
                    if value.attr in names:
                        return True

        return False

    def _class_has_decorator_name(
            self,
            class_node: ast.ClassDef,
            names: set[str],
    ) -> bool:
        for decorator in class_node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in names:
                    return True

            if isinstance(decorator, ast.Call):
                function = decorator.func

                if isinstance(function, ast.Name):
                    if function.id in names:
                        return True

                if isinstance(function, ast.Attribute):
                    if function.attr in names:
                        return True

            if isinstance(decorator, ast.Attribute):
                if decorator.attr in names:
                    return True

        return False

    def _class_has_native_class_true(self, class_node: ast.ClassDef) -> bool:
        for decorator in class_node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            function = decorator.func

            is_mypyc_attr = False

            if isinstance(function, ast.Name):
                is_mypyc_attr = function.id == "mypyc_attr"

            if isinstance(function, ast.Attribute):
                is_mypyc_attr = function.attr == "mypyc_attr"

            if not is_mypyc_attr:
                continue

            for keyword in decorator.keywords:
                if keyword.arg != "native_class":
                    continue

                value = keyword.value

                if isinstance(value, ast.Constant) and value.value is True:
                    return True

        return False

    def _is_native_decorator_exempt_class(self, class_node: ast.ClassDef) -> bool:
        if class_node.name.startswith("_"):
            return True

        if self._class_inherits_any_name(
                class_node=class_node,
                names={
                    "Protocol",
                    "Enum",
                    "IntEnum",
                    "StrEnum",
                    "Flag",
                    "IntFlag",
                    "ABC",
                    "Exception",
                    "BaseException",
                    "TypedDict",
                    "NamedTuple",
                },
        ):
            return True

        if self._class_has_decorator_name(
                class_node=class_node,
                names={
                    "trait",
                    "runtime_checkable",
                },
        ):
            return True

        return False

    def _collect_native_decorator_violations(
            self,
            file_path: Path,
            tree: ast.Module,
    ) -> list[MypycPolicyViolation]:
        violations: list[MypycPolicyViolation] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            if self._is_native_decorator_exempt_class(class_node=node):
                continue

            if self._class_has_native_class_true(class_node=node):
                continue

            violations.append(
                MypycPolicyViolation(
                    file_path=str(file_path),
                    line_number=node.lineno,
                    message=(
                        "concrete compiled core class is missing "
                        "@mypyc_attr(native_class=True)"
                    ),
                )
            )

        return violations

    def check(self, module_paths: list[str]) -> None:
        violations: list[MypycPolicyViolation] = []

        if not self._should_run_import_wall() and not self._should_run_native_decorator_wall():
            return

        for module_path in module_paths:
            file_path = Path(module_path)

            try:
                source = file_path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(file_path))

            except SyntaxError as error:
                violations.append(
                    MypycPolicyViolation(
                        file_path=str(file_path),
                        line_number=error.lineno or 0,
                        message=f"could not parse file for policy checks: {error.msg}",
                    )
                )
                continue

            if self._should_run_import_wall():
                violations.extend(
                    self._collect_import_wall_violations(
                        file_path=file_path,
                        tree=tree,
                    )
                )

            if self._should_run_native_decorator_wall():
                violations.extend(
                    self._collect_native_decorator_violations(
                        file_path=file_path,
                        tree=tree,
                    )
                )

        report = MypycPolicyReport(
            strict_level=self._strict_level,
            violations=violations,
        )
        report.print_report()

        if not violations:
            return

        if self._policy_should_fail():
            print(
                f"MYPYC policy level {self._strict_level} failed "
                f"with {len(violations)} violation(s)."
            )
            raise SystemExit(1)

        print(
            f"MYPYC policy level {self._strict_level} found "
            f"{len(violations)} violation(s), but policy mode is report-only."
        )


class TeeStream:
    def __init__(self, original_stream: TextIO, capture_stream: io.StringIO) -> None:
        self._original_stream = original_stream
        self._capture_stream = capture_stream

    def write(self, text: str) -> int:
        self._capture_stream.write(text)

        return self._original_stream.write(text)

    def flush(self) -> None:
        self._capture_stream.flush()
        self._original_stream.flush()


class MypycError:
    def __init__(
            self,
            file_path: str,
            line_number: int,
            column_number: int | None,
            message: str,
            error_code: str,
    ) -> None:
        self._file_path = file_path
        self._line_number = line_number
        self._column_number = column_number
        self._message = message
        self._error_code = error_code

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def line_number(self) -> int:
        return self._line_number

    @property
    def column_number(self) -> int | None:
        return self._column_number

    @property
    def message(self) -> str:
        return self._message

    @property
    def error_code(self) -> str:
        return self._error_code


class MypycReportParser:
    def __init__(self) -> None:
        self._error_pattern = re.compile(
            r"^(?P<file>.*?\.py):"
            r"(?P<line>\d+):"
            r"(?:(?P<column>\d+):)? "
            r"error: "
            r"(?P<message>.*?)"
            r"(?:  \[(?P<code>[^\]]+)\])?$"
        )

    def parse_errors(self, output: str) -> list[MypycError]:
        errors: list[MypycError] = []

        for line in output.splitlines():
            match = self._error_pattern.match(line)

            if match is None:
                continue

            column_group = match.group("column")
            error_code = match.group("code")

            column_number: int | None = None

            if column_group is not None:
                column_number = int(column_group)

            if error_code is None:
                error_code = "unknown"

            errors.append(
                MypycError(
                    file_path=match.group("file"),
                    line_number=int(match.group("line")),
                    column_number=column_number,
                    message=match.group("message"),
                    error_code=error_code,
                )
            )

        return errors


class MypycErrorReport:
    def __init__(self, strict_level: str, errors: list[MypycError]) -> None:
        self._strict_level = strict_level
        self._errors = errors

    def _count_by_file(self) -> dict[str, int]:
        counts: dict[str, int] = {}

        for error in self._errors:
            if error.file_path not in counts:
                counts[error.file_path] = 0

            counts[error.file_path] += 1

        return counts

    def _count_by_error_code(self) -> dict[str, int]:
        counts: dict[str, int] = {}

        for error in self._errors:
            if error.error_code not in counts:
                counts[error.error_code] = 0

            counts[error.error_code] += 1

        return counts

    def _print_file_summary(self, counts: dict[str, int]) -> None:
        print("")
        print("FILES IMPACTED MOST")
        print("-------------------")

        if not counts:
            print("No impacted files.")
            return

        sorted_items = sorted(
            counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        for file_path, count in sorted_items[:25]:
            print(f"{count:>5}  {file_path}")

    def _print_error_code_summary(self, counts: dict[str, int]) -> None:
        print("")
        print("ERROR CODES")
        print("-----------")

        if not counts:
            print("No error codes.")
            return

        sorted_items = sorted(
            counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        for error_code, count in sorted_items:
            print(f"{count:>5}  [{error_code}]")

    def print_report(self) -> None:
        file_counts = self._count_by_file()
        code_counts = self._count_by_error_code()

        print("")
        print("")
        print("MYPYC ERROR REPORT")
        print("==================")
        print(f"Strict level:       {self._strict_level}")
        print(f"Total errors:       {len(self._errors)}")
        print(f"Files impacted:     {len(file_counts)}")
        print(f"Error code groups:  {len(code_counts)}")

        self._print_file_summary(counts=file_counts)
        self._print_error_code_summary(counts=code_counts)

        print("")
        print("==================")
        print("END MYPYC REPORT")
        print("==================")
        print("")


class MypycReporter:
    def __init__(self, strict_level: str) -> None:
        self._strict_level = strict_level
        self._stdout_capture = io.StringIO()
        self._stderr_capture = io.StringIO()
        self._parser = MypycReportParser()

    def _collect_output(self) -> str:
        return (
                self._stdout_capture.getvalue()
                + "\n"
                + self._stderr_capture.getvalue()
        )

    def _print_report(self) -> None:
        output = self._collect_output()
        errors = self._parser.parse_errors(output=output)
        report = MypycErrorReport(
            strict_level=self._strict_level,
            errors=errors,
        )

        report.print_report()

    def run_mypycify(self, args: list[str]) -> list[Extension]:
        stdout_tee = TeeStream(
            original_stream=sys.stdout,
            capture_stream=self._stdout_capture,
        )
        stderr_tee = TeeStream(
            original_stream=sys.stderr,
            capture_stream=self._stderr_capture,
        )

        try:
            with redirect_stdout(stdout_tee), redirect_stderr(stderr_tee):
                extensions = mypycify(
                    args,
                    opt_level="3",
                    debug_level="0",
                    strip_asserts=True,
                    multi_file=False,
                    separate=False,
                )

                print("")
                print(f"MYPYC GENERATED EXTENSIONS: {len(extensions)}")

                for extension in extensions:
                    print(f"  {extension.name}")

                return extensions

        finally:
            self._print_report()


build = MypycBuild(
    source_root="src/melder/aether/spellbook",
    package_root="spell_compiler",
    compiled_top_level_directories=COMPILED_TOP_LEVEL_DIRECTORIES,
    excluded_directory_names=EXCLUDED_DIRECTORY_NAMES,
    skipped_typecheck_modules=SKIPPED_TYPECHECK_MODULES,
    forbidden_core_import_roots=FORBIDDEN_CORE_IMPORT_ROOTS,
    include_package_root_modules=True,
)

compiled_modules = build.collect_python_modules()

policy_checker = MypycPolicyChecker(
    strict_level=build.strict_level,
    package_root=build.package_root,
    forbidden_core_import_roots=build.forbidden_core_import_roots,
)

policy_checker.check(
    module_paths=compiled_modules,
)

reporter = MypycReporter(
    strict_level=build.strict_level,
)

setup(
    name="melder",
    packages=find_packages(
        "src",
        exclude=PACKAGE_EXCLUDE_PATTERNS,
    ),
    package_dir={"": "src"},
    package_data={
        "melder": [
            "py.typed",
            "**/*.pyi",
        ],
    },
    ext_modules=reporter.run_mypycify(
        args=build.collect_mypyc_args(),
    ),
)
