"""
TIER: intermediate (11)
GOAL: Permissions are LINKING vocabulary (owner ruling): read / create /
      block govern what LINKED conduits may do with your bindings in
      dynamic worlds - they are not a local-meld concept at all.
      read = resolve-only across links; create implies read; block
      stops sharing entirely.
SURFACE EXERCISED: md.Permissions.read
"""
import melder as md


class PublishedConfig:
    value = "frozen"


def main() -> None:
    book = md.Spellbook()
    prebuilt = PublishedConfig()
    book.bind(spell=prebuilt, existence="unique",
              permissions="read")
    conduit = book.conjure()

    held = conduit.meld(spell=prebuilt)
    assert held is prebuilt
    print("read permission: resolve works, instance handed back untouched")
    print("vocabulary: read < create (create implies read); block stops sharing")


if __name__ == "__main__":
    main()
