import inspect
import json
from typing import Any, Dict
# Melder imports
from melder.spellbook.spell_crafter.spell_examiner.inspectors import InspectorUtility
from melder.spellbook.spell_crafter.spell_examiner.inspectors.class_inspector import ClassInspector
from melder.spellbook.spell_crafter.spell_examiner.inspectors.method_inspector import MethodInspector
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles import ClassProfile
from melder.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import MethodProfile

#region SpellExaminer
class SpellExaminer:
    utility = InspectorUtility
    def __init__(
            self,
            obj: Any,
            *,
            show_dunders: bool = False,
            max_repr: int = 120,
    ):
        self.obj = obj
        self.dunders = show_dunders
        self.max_repr = max_repr

    def inspect(self) -> Any:
        if inspect.isclass(self.obj):
            inspector = ClassInspector(self.obj, show_dunders=self.dunders, max_repr=self.max_repr)
            data = inspector.inspect()

            method_profiles: Dict[str, MethodProfile] = {}
            for name, info in data["members"].items():
                if info.get("callable"):
                    try:
                        # Get the actual method reference from the class
                        fn = getattr(self.obj, name)
                        method_data = MethodInspector(fn, max_repr=self.max_repr).inspect()
                        method_profiles[name] = MethodProfile(
                            name=method_data["name"],
                            qualname=method_data["qualname"],
                            module=method_data["module"],
                            id=method_data["id"],
                            type=method_data["type"],
                            repr=method_data["repr"],
                            builtin_mod=method_data["builtin_mod"],
                            extension_mod=method_data["extension_mod"],
                            file=method_data["file"],
                            preview=method_data["preview"],
                            src_offset=method_data["src_offset"],
                            signature=method_data.get("signature"),
                            parameters=method_data.get("parameters", []),
                            uninspectable=method_data.get("uninspectable", False),
                            func=method_data.get("func", False),
                            method=method_data.get("method", False),
                            builtin=method_data.get("builtin", False),
                            classmethod=method_data.get("classmethod", False),
                            staticmethod=method_data.get("staticmethod", False),
                            generator=method_data.get("generator", False),
                            async_gen=method_data.get("async_gen", False),
                            coroutine=method_data.get("coroutine", False),
                            lambda_fn=method_data.get("lambda_fn", False),
                            abstract=method_data.get("abstract", False),
                            closure=method_data.get("closure"),
                            decorated=method_data.get("decorated"),
                            wrapped_repr=method_data.get("wrapped_repr"),
                        )
                    except Exception as e:
                        # fallback if something goes wrong
                        continue

            return ClassProfile(
                name=data["name"],
                qualname=data["qualname"],
                module=data["module"],
                mro=data["mro"],
                bases=data["bases"],
                annotations=data["annotations"],
                protocols=data["protocols"],
                slots=data["slots"],
                origin_file=data["file"],
                origin_line=data["source_line_offset"],
                source_preview=data["source_preview"],
                members=data["members"],  #original dict
                methods=method_profiles,  #structured MethodProfile dict
                is_dataclass=data["is_dataclass"],
                decorated=data["decorated"],
            )

        elif callable(self.obj) and not inspect.isclass(self.obj):
            inspector = MethodInspector(self.obj, max_repr=self.max_repr)
            data = inspector.inspect()
            return MethodProfile(
                name=data["name"],
                qualname=data["qualname"],
                module=data["module"],
                id=data["id"],
                type=data["type"],
                repr=data["repr"],
                builtin_mod=data["builtin_mod"],
                extension_mod=data["extension_mod"],
                file=data["file"],
                preview=data["preview"],
                src_offset=data["src_offset"],
                signature=data.get("signature"),
                parameters=data.get("parameters", []),
                uninspectable=data.get("uninspectable", False),
                func=data.get("func", False),
                method=data.get("method", False),
                builtin=data.get("builtin", False),
                classmethod=data.get("classmethod", False),
                staticmethod=data.get("staticmethod", False),
                generator=data.get("generator", False),
                async_gen=data.get("async_gen", False),
                coroutine=data.get("coroutine", False),
                lambda_fn=data.get("lambda_fn", False),
                abstract=data.get("abstract", False),
                closure=data.get("closure"),
                decorated=data.get("decorated"),
                wrapped_repr=data.get("wrapped_repr"),
            )

        return {
            "object_type": "instance_or_other",
            "repr": self.utility.safe_repr(self.obj, self.max_repr),
            "id": id(self.obj),
            "type": type(self.obj).__name__,
        }

    def to_json(self) -> str:
        result = self.inspect()
        if isinstance(result, (ClassProfile, MethodProfile)):
            return json.dumps(result.__dict__, default=str, indent=2)
        return json.dumps(result, default=str, indent=2)
#endregion
