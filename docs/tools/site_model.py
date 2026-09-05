"""Value-only declarations shared by documentation source generators."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Page:
    """Stable document identity, display title, authored source, and one navigation parent."""

    identifier: str
    title: str
    source: str
    parent: str


@dataclass(frozen=True)
class Asset:
    """Mapping of one selected canonical file to a generated public asset path."""

    source: str
    target: str
