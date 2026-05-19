from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple

from mypy_extensions import mypyc_attr

# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
class TargetSpecKind(Enum):
    """
    Internal

    Represents the three supported targeting modes for overrides:

    * PATH -> explicit param path: "a>b>c".
    * UNIQUE -> unique-by-name wildcard: "*repo".
    * BROADCAST -> broadcast-by-name wildcard: "**logger".
    """
    __melder_internal__ = _mrg.sentinel
    PATH = auto()
    UNIQUE = auto()
    BROADCAST = auto()

@mypyc_attr(native_class=True)
@dataclass(frozen=True, slots=True)
class TargetSpec:
    """
    Internal

    Parsed representation of a single override target key.

    Attributes:
        kind:
            The targeting mode (: class:`TargetSpecKind`).

        path:
            The param path segments for PATH specs (e.g. ("orchestrator", "repo")).
            None for UNIQUE / BROADCAST.

        param_name:
            The parameter name used for UNIQUE / BROADCAST specs (e.g. ``"logger"``).
            "None" for PATH specs.
    """
    __melder_internal__ = _mrg.sentinel
    kind: TargetSpecKind
    path: Tuple[str, ...] | None = None
    param_name: str | None = None

    @staticmethod
    def parse(raw: str) -> "TargetSpec":
        """
        Parse a raw override key into a: class:`TargetSpec`.

        Supported forms:

        * PATH:
            ""timeout"", ""orchestrator>order_service>repo""

        * UNIQUE:
            ""*repo"", ""*logger""

        * BROADCAST:
            ""**repo"", ""**logger""
        """
        if raw is None:
            raise ValueError("Override key must not be None.")

        text = raw.strip()
        if not text:
            raise ValueError("Override key must not be empty or whitespace.")

        # Broadcast-by-name: **param
        if text.startswith("**"):
            param_name = text[2:].strip()
            if not param_name:
                raise ValueError(f"Broadcast override key '{raw}' is missing a parameter name.")
            return TargetSpec(
                kind=TargetSpecKind.BROADCAST,
                path=None,
                param_name=param_name,
            )

        # Unique-by-name: *param
        if text.startswith("*"):
            param_name = text[1:].strip()
            if not param_name:
                raise ValueError(f"Unique override key '{raw}' is missing a parameter name.")
            return TargetSpec(
                kind=TargetSpecKind.UNIQUE,
                path=None,
                param_name=param_name,
            )

        # Param path: a>b>c
        segments = [segment.strip() for segment in text.split(">") if segment.strip()]
        if not segments:
            raise ValueError(f"Path override key '{raw}' did not contain any segments.")

        return TargetSpec(
            kind=TargetSpecKind.PATH,
            path=tuple(segments),
            param_name=None,
        )
