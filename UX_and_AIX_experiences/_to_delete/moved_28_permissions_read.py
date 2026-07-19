"""
TIER: beginner (28)
GOAL: Permissions are the second half of the bind vocabulary - read
      marks a binding resolve-only. Reading works; the printed outcome
      documents what read forbids beyond it.
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
