import io
import os
import re
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import TextIO

from mypyc.build import mypycify
from setuptools import Extension, find_packages, setup


class MypycStrictLevel:
    def __init__(self) -> None:
        self._allowed_levels = {
            "0",
            "1",
            "2",
            "3",
            "4",
        }

    def resolve(self) -> str:
        if len(sys.argv) > 1 and sys.argv[1] in self._allowed_levels:
            strict_level = sys.argv[1]
            del sys.argv[1]

            return strict_level

        strict_level = os.environ.get("MYPYC_STRICT_LEVEL", "1")

        if strict_level not in self._allowed_levels:
            raise ValueError(
                "MYPYC_STRICT_LEVEL must be one of: 0, 1, 2, 3, 4"
            )

        return strict_level


class MypycBuild:
    def __init__(self, source_root: str, package_root: str) -> None:
        self._source_root = Path(source_root)
        self._package_root = self._source_root / package_root
        self._strict_level = MypycStrictLevel().resolve()

    @property
    def strict_level(self) -> str:
        return self._strict_level

    def collect_python_modules(self) -> list[str]:
        modules: list[str] = []

        for path in self._package_root.rglob("*.py"):
            if "tests" in path.parts:
                continue

            if "__pycache__" in path.parts:
                continue

            modules.append(str(path))

        return modules

    def collect_level_zero_args(self) -> list[str]:
        return [
            "--show-error-codes",
            "--show-column-numbers",
        ]

    def collect_level_one_args(self) -> list[str]:
        return [
            "--disallow-untyped-defs",
            "--check-untyped-defs",
            "--warn-return-any",
            "--warn-no-return",
            "--warn-redundant-casts",
            "--warn-unused-ignores",
            "--show-error-codes",
            "--show-column-numbers",
        ]

    def collect_level_two_args(self) -> list[str]:
        return [
            "--strict",
            "--warn-unreachable",
            "--strict-equality",
            "--strict-equality-for-none",
            "--warn-redundant-casts",
            "--warn-unused-ignores",
            "--warn-return-any",
            "--warn-no-return",
            "--show-error-codes",
            "--show-column-numbers",
        ]

    def collect_level_three_args(self) -> list[str]:
        return [
            "--strict",
            "--warn-unreachable",
            "--strict-equality",
            "--strict-equality-for-none",

            "--disallow-any-unimported",
            "--disallow-any-decorated",
            "--disallow-any-explicit",
            "--disallow-any-generics",

            "--warn-redundant-casts",
            "--warn-unused-ignores",
            "--warn-return-any",
            "--warn-no-return",

            "--enable-error-code=redundant-self",
            "--enable-error-code=redundant-expr",
            "--enable-error-code=possibly-undefined",
            "--enable-error-code=truthy-bool",
            "--enable-error-code=truthy-iterable",
            "--enable-error-code=ignore-without-code",
            "--enable-error-code=unused-awaitable",
            "--enable-error-code=explicit-override",

            "--show-error-codes",
            "--show-error-code-links",
            "--show-column-numbers",
        ]

    def collect_level_four_args(self) -> list[str]:
        return [
            "--strict",
            "--warn-unreachable",
            "--strict-equality",
            "--strict-equality-for-none",

            "--disallow-any-unimported",
            "--disallow-any-expr",
            "--disallow-any-decorated",
            "--disallow-any-explicit",
            "--disallow-any-generics",

            "--disallow-untyped-calls",
            "--disallow-untyped-defs",
            "--disallow-incomplete-defs",
            "--disallow-untyped-decorators",
            "--check-untyped-defs",

            "--no-implicit-reexport",

            "--warn-redundant-casts",
            "--warn-unused-ignores",
            "--warn-return-any",
            "--warn-no-return",

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

            "--show-error-codes",
            "--show-error-code-links",
            "--show-column-numbers",
        ]

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

        raise ValueError(
            "MYPYC_STRICT_LEVEL must be one of: 0, 1, 2, 3, 4"
        )

    def collect_mypyc_args(self) -> list[str]:
        args = self.collect_strict_args()
        args.extend(self.collect_python_modules())

        print(f"Using MYPYC strict level: {self._strict_level}")

        return args


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
                return mypycify(
                    args,
                    opt_level="3",
                    debug_level="0",
                    strip_asserts=True,
                    multi_file=False,
                    separate=False,
                )

        except SystemExit:
            self._print_report()
            raise

        except BaseException:
            self._print_report()
            raise

        finally:
            output = self._collect_output()

            if output:
                self._print_report()


build = MypycBuild(
    source_root="src",
    package_root="melder",
)

reporter = MypycReporter(
    strict_level=build.strict_level,
)

setup(
    name="melder",
    packages=find_packages("src"),
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