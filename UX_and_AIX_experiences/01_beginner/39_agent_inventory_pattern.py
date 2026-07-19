"""
TIER: beginner (39) - the AIX seat
GOAL: An agent classifying the library itself - walk md.__all__ and
      sort every name into callable vocabulary vs types vs errors vs
      metadata, producing the machine-readable inventory an agent
      builds before its first bind.
SURFACE EXERCISED: md.__all__, the whole root namespace, issubclass checks
"""
import melder as md


def main() -> None:
    groups: dict[str, list[str]] = {
        "errors": [], "enums": [], "classes": [], "functions": [],
        "metadata": [],
    }
    for name in md.__all__:
        obj = getattr(md, name)
        if name.startswith("__"):
            groups["metadata"].append(name)
        elif isinstance(obj, type) and issubclass(obj, BaseException):
            groups["errors"].append(name)
        elif isinstance(obj, type) and hasattr(obj, "__members__"):
            groups["enums"].append(name)
        elif isinstance(obj, type):
            groups["classes"].append(name)
        else:
            groups["functions"].append(name)

    for group, names in groups.items():
        print(f"{group:10s} ({len(names):2d}):", ", ".join(sorted(names)[:6]),
              "..." if len(names) > 6 else "")
    assert len(groups["errors"]) == 9
    assert "scan_bind" in groups["functions"]
    print("agent inventory complete:", sum(map(len, groups.values())), "names classified")


if __name__ == "__main__":
    main()
