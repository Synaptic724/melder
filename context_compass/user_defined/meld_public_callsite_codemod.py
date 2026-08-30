"""Migrate public Meld call sites to human, machine-ID, and override syntax."""

import argparse
import pathlib
from typing import List, Optional, Sequence

import libcst as cst
from libcst.helpers import get_full_name_for_node


class MeldCallsiteTransformer(cst.CSTTransformer):
    """
    Rewrite public meld calls without touching internal Meld doors.

    Contract:
        Converts `spell_name=` to human `spell=` and syntactically identifiable
        ID arguments to `spell_id=`. Renames public `spell_override=` calls to
        `override=` while retaining internal Meld-door terminology. Command
        surfaces retain their distinct identity inputs but receive the public
        override-keyword migration.
    """

    def __init__(self) -> None:
        """Initialize the per-file change counter."""
        self.change_count: int = 0

    @staticmethod
    def _receiver_name(call: cst.Call) -> Optional[str]:
        """Return a simple dotted receiver name when LibCST can resolve one."""
        if not isinstance(call.func, cst.Attribute):
            return None
        return get_full_name_for_node(call.func.value)

    @staticmethod
    def _is_internal_receiver(receiver_name: Optional[str]) -> bool:
        """Return whether a call targets an internal Meld or command facade."""
        if receiver_name is None:
            return False
        final = receiver_name.rsplit(".", 1)[-1]
        return final in {
            "meld",
            "_meld",
            "conduit_meld",
            "spellspace_meld",
            "command",
            "command_system",
        }

    @staticmethod
    def _is_internal_meld_receiver(receiver_name: Optional[str]) -> bool:
        """Return whether a call targets an internal runtime Meld door."""
        if receiver_name is None:
            return False
        final = receiver_name.rsplit(".", 1)[-1]
        return final in {
            "meld",
            "_meld",
            "conduit_meld",
            "spellspace_meld",
        }

    @staticmethod
    def _is_id_expression(expression: cst.BaseExpression) -> bool:
        """Recognize explicit ID variables/attributes and test ID literals."""
        if isinstance(expression, cst.Name):
            lowered = expression.value.lower()
            return (
                lowered in {"id", "sid"}
                or lowered.startswith("id_")
                or lowered.endswith("_id")
                or lowered.endswith("_sid")
            )
        if isinstance(expression, cst.Attribute):
            lowered = expression.attr.value.lower()
            return lowered == "id" or lowered.startswith("id_") or lowered.endswith("_id")
        if isinstance(expression, cst.SimpleString):
            try:
                value = expression.evaluated_value
            except Exception:
                return False
            if not isinstance(value, str):
                return False
            lowered = value.lower()
            return len(value) == 64 or "spell-id" in lowered or lowered.startswith("sha-")
        if isinstance(expression, cst.Subscript):
            container = get_full_name_for_node(expression.value)
            if container is None:
                return False
            lowered = container.rsplit(".", 1)[-1].lower()
            return (
                lowered == "ids"
                or lowered.endswith("_ids")
                or lowered.endswith("id_map")
                or lowered.endswith("ids_by_name")
            )
        return False

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        """Rewrite one eligible public `.meld(...)` call."""
        if not isinstance(updated_node.func, cst.Attribute):
            return updated_node
        if updated_node.func.attr.value != "meld":
            return updated_node
        receiver_name = self._receiver_name(updated_node)
        identity_rewrite_enabled = not self._is_internal_receiver(receiver_name)
        override_rewrite_enabled = not self._is_internal_meld_receiver(receiver_name)

        keyword_names = {
            argument.keyword.value
            for argument in updated_node.args
            if isinstance(argument.keyword, cst.Name)
        }
        if "spell_name" in keyword_names and "spell" in keyword_names:
            identity_rewrite_enabled = False

        changed = False
        rewritten: List[cst.Arg] = []
        for position, argument in enumerate(updated_node.args):
            keyword = argument.keyword.value if isinstance(argument.keyword, cst.Name) else None
            replacement = argument
            if keyword == "spell_override" and override_rewrite_enabled:
                replacement = argument.with_changes(keyword=cst.Name("override"))
                changed = True
            elif identity_rewrite_enabled and keyword == "spell_name":
                replacement = argument.with_changes(keyword=cst.Name("spell"))
                changed = True
            elif (
                    identity_rewrite_enabled
                    and keyword == "spell"
                    and self._is_id_expression(argument.value)
            ):
                replacement = argument.with_changes(keyword=cst.Name("spell_id"))
                changed = True
            elif keyword == "spell_id" and isinstance(argument.equal, cst.AssignEqual):
                if (
                        argument.equal.whitespace_before.value
                        or argument.equal.whitespace_after.value
                ):
                    replacement = argument.with_changes(
                        equal=cst.AssignEqual(
                            whitespace_before=cst.SimpleWhitespace(""),
                            whitespace_after=cst.SimpleWhitespace(""),
                        )
                    )
                    changed = True
            elif (
                    identity_rewrite_enabled
                    and position == 0
                    and keyword is None
                    and self._is_id_expression(argument.value)
            ):
                replacement = argument.with_changes(
                    keyword=cst.Name("spell_id"),
                    equal=cst.AssignEqual(
                        whitespace_before=cst.SimpleWhitespace(""),
                        whitespace_after=cst.SimpleWhitespace(""),
                    ),
                )
                changed = True
            rewritten.append(replacement)

        if not changed:
            return updated_node
        self.change_count += 1
        return updated_node.with_changes(args=tuple(rewritten))


def candidate_files(roots: Sequence[pathlib.Path]) -> List[pathlib.Path]:
    """Return sorted Python candidates while excluding generated build assets."""
    paths: List[pathlib.Path] = []
    for root in roots:
        for path in root.rglob("*.py"):
            if "_build_assets" in path.parts and (
                    "payloads" in path.parts or "manifest" in path.parts
            ):
                continue
            paths.append(path)
    return sorted(set(paths))


def migrate(path: pathlib.Path, apply: bool) -> int:
    """Transform one file and optionally write the changed source in place."""
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    source = raw.decode("utf-8-sig")
    try:
        module = cst.parse_module(source)
    except cst.ParserSyntaxError:
        return 0
    transformer = MeldCallsiteTransformer()
    updated = module.visit(transformer)
    if transformer.change_count and apply:
        encoded = updated.code.encode("utf-8")
        if has_bom:
            encoded = b"\xef\xbb\xbf" + encoded
        path.write_bytes(encoded)
    return transformer.change_count


def main() -> int:
    """Dry-run or apply the deterministic public meld call-site migration."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    # Product source wrappers are reviewed and patched manually. The mechanical
    # lane is intentionally limited to repository-owned tests and curriculum.
    roots = [pathlib.Path("tests"), pathlib.Path("UX_and_AIX_experiences")]
    changed_files = 0
    changed_calls = 0
    for path in candidate_files(roots):
        count = migrate(path, args.apply)
        if not count:
            continue
        changed_files += 1
        changed_calls += count
        print(f"{count:4d}  {path.as_posix()}")
    mode = "APPLY" if args.apply else "CHECK"
    print(f"{mode}: {changed_calls} call(s) across {changed_files} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
