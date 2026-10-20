"""Blast-radius digest (melder_0, 2026-10-18; mirror only, never in the repository's src/).

The code digest v2 prototype with decision B layered on: installed third-party classes, metaclasses and functions
are named `<qualified> <dist>==<version>`, an installed third-party object `ext:<qualified> <dist>==<version>
<repr without addresses>`. One instance serves the whole process under a lock (probe only).
"""
import functools
import importlib.metadata
import inspect
import pathlib
import site
import sys
import sysconfig
import threading
import types
from typing import Any, Optional

from _br_digest_v2 import CodeDigest


class BlastRadiusDigest(CodeDigest):
    """CodeDigest plus decision B; module locations and versions memoized per instance."""

    TAG = "v5-code"

    def __init__(self) -> None:
        super().__init__()
        roots = set()
        for key in ("purelib", "platlib"):
            path = sysconfig.get_paths().get(key)
            if path:
                roots.add(str(pathlib.Path(path).resolve()))
        for path in list(site.getsitepackages()) + [site.getusersitepackages()]:
            roots.add(str(pathlib.Path(path).resolve()))
        self._site_roots = tuple(sorted(roots))
        self._third_party_memo: dict = {}
        self._version_memo: dict = {}
        self._distributions: Optional[dict] = None

    def _is_third_party_module(self, module: Optional[str]) -> bool:
        if module is None or self._is_library_module(module) or module == "melder" or module.startswith("melder."):
            return False
        cached = self._third_party_memo.get(module)
        if cached is not None:
            return cached
        loaded = sys.modules.get(module)
        file = getattr(loaded, "__file__", None) if loaded is not None else None
        result = False
        if file:
            resolved = str(pathlib.Path(file).resolve())
            result = any(resolved.startswith(root + "/") for root in self._site_roots)
        self._third_party_memo[module] = result
        return result

    def _version(self, module: str) -> str:
        top = module.split(".")[0]
        cached = self._version_memo.get(top)
        if cached is not None:
            return cached
        text = "?==?"
        try:
            text = f"{top}=={importlib.metadata.version(top)}"
        except importlib.metadata.PackageNotFoundError:
            if self._distributions is None:
                self._distributions = importlib.metadata.packages_distributions()
            names = self._distributions.get(top) or []
            if names:
                try:
                    text = f"{names[0]}=={importlib.metadata.version(names[0])}"
                except importlib.metadata.PackageNotFoundError:
                    text = "?==?"
        self._version_memo[top] = text
        return text

    def _named(self, value: Any) -> str:
        module = getattr(value, "__module__", None) or "?"
        return self._qualified(value) + " " + self._version(module)

    def target_encoding(self, target: Any) -> str:
        if inspect.isclass(target) and self._is_third_party_module(getattr(target, "__module__", None)):
            return "class " + self._named(target)
        if isinstance(target, types.FunctionType) and self._is_third_party_module(target.__module__):
            return "function " + self._named(target)
        if not inspect.isclass(target) and not isinstance(target, types.FunctionType) \
                and self._is_third_party_module(getattr(type(target), "__module__", None)):
            return "object ext:" + self._named(type(target)) + " " + self.ADDRESS.sub("", repr(target))
        return super().target_encoding(target)

    def class_digest(self, cls: type, path: set) -> str:
        if self._is_third_party_module(getattr(cls, "__module__", None)):
            return "named:" + self._named(cls)
        return super().class_digest(cls, path)

    def _namespace_digest(self, cls: type, path: set) -> str:
        if self._is_third_party_module(getattr(cls, "__module__", None)):
            return "named:" + self._named(cls)
        return super()._namespace_digest(cls, path)

    def encode(self, value: Any, path: set, owner: Optional[type]) -> str:
        if isinstance(value, types.FunctionType) and self._is_third_party_module(value.__module__):
            return "fn:" + self._named(value)
        if not inspect.isclass(value) and not isinstance(value, (types.FunctionType, types.ModuleType)) \
                and self._is_third_party_module(getattr(type(value), "__module__", None)):
            try:
                text = repr(value)
            except Exception:
                text = "<unrepr-able>"
            return "ext:" + self._named(type(value)) + " " + self.ADDRESS.sub("", text)
        return super().encode(value, path, owner)


class SharedDigest:
    """Process-wide probe instance, serialized by one lock."""

    LOCK = threading.Lock()
    DIGEST = BlastRadiusDigest()

    @staticmethod
    def spell_id(target: Any) -> str:
        with SharedDigest.LOCK:
            try:
                return SharedDigest.DIGEST.spell_id(target)
            except RecursionError:
                return SharedDigest.DIGEST._sha("v5-code repr " + SharedDigest.DIGEST._qualified(type(target)) + " "
                                                + SharedDigest.DIGEST.ADDRESS.sub("", repr(target)))


class MirrorBinding:
    """S2 in the mirror: a binding hash from a Spell's binding fields (probe only; the patch's BindingManifest)."""

    @staticmethod
    def spellframe_text(spellframe: Any) -> str:
        if spellframe is None:
            return ""
        if isinstance(spellframe, str):
            return spellframe
        return f"{getattr(spellframe, '__module__', '?')}.{getattr(spellframe, '__qualname__', '?')}"

    @staticmethod
    def binding_hash(spell: Any) -> str:
        import hashlib
        key = getattr(spell, "_key", None)
        fields = [
            ("key", repr(key)),
            ("spellframe", repr(MirrorBinding.spellframe_text(getattr(spell, "spellframe", None)))),
            ("spellframe_kind", repr(getattr(getattr(spell, "spellframe_kind", None), "name", None))),
            ("binding_name", repr(getattr(spell, "binding_name", None))),
            ("existence", repr(getattr(getattr(spell, "existence", None), "name", None))),
            ("disposal_method_names", repr(tuple(getattr(spell, "disposal_method_names", None) or ()))),
            ("resolvable", repr(getattr(spell, "_resolvable", None))),
            ("managed_spell_mode", repr(getattr(getattr(spell, "_managed_spell_mode", None), "name",
                                                getattr(spell, "_managed_spell_mode", None)))),
            ("managed_spell_limit", repr(getattr(spell, "_managed_spell_limit", None))),
            ("managed_spell_timeout_seconds", repr(getattr(spell, "_managed_spell_timeout_seconds", None))),
            ("managed_spell_reset_methods", repr(tuple(getattr(spell, "_managed_spell_reset_methods", None) or ()))),
        ]
        text = "v1-binding\n" + "\n".join(f"{name}={value}" for name, value in fields)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
