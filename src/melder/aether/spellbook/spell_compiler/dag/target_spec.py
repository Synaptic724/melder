from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple, ClassVar



# Melder Imports
class TargetSpecKind(Enum):
    """
    Internal

    Represents the three supported targeting modes for overrides:

    * PATH -> explicit param path: "a>b>c".
    * UNIQUE -> unique-by-name wildcard: "*repo".
    * BROADCAST -> broadcast-by-name wildcard: "**logger".

    Registration:
        MELDER KERNEL - guarded. A compiler classification enum; not a
        user-bindable value.

    Subsystem Context:
        Paired with `TargetSpec`, which parses a raw override key into one of these
        modes.

    System Context:
        Phase 3 (DAG) override targeting of the conjure/meld pipeline.
    """
    __ast_helper_access__ = "internal"
    __agent_purpose__ = (
        "access: internal. Override-targeting mode: PATH (a>b>c param path), UNIQUE (*name), "
        "BROADCAST (**name). Classifies how an override key targets DAG sockets."
    )
    PATH = auto()
    UNIQUE = auto()
    BROADCAST = auto()


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

    Registration:
        MELDER KERNEL - guarded (ClassVar sentinel). A frozen value dataclass, so it
        is not a bindable service in any case.

    Subsystem Context:
        The parsed form of an override key in the `dag` package; its `kind` is a
        `TargetSpecKind`, and `TargetSpec.parse(raw)` is the only constructor.

    System Context:
        Phase 3 (DAG) override targeting - it resolves which socket(s) a meld
        override applies to.
    """
    # Unannotated on purpose: an annotated class var could be misread as a
    # dataclass field on some Python versions; unannotated attrs never are.
    __ast_helper_access__ = "internal"
    __agent_purpose__ = (
        "access: internal. Parsed override target key: kind (TargetSpecKind) plus path (PATH "
        "segments) or param_name (UNIQUE/BROADCAST). Built by TargetSpec.parse(raw)."
    )
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
