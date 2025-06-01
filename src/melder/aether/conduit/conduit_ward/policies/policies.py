from enum import Enum, auto

class Policies(Enum):
    """
    Defines conduit policy behaviors within the conduit ward system.

    These policies control how a conduit grants spell access, inherits behavior,
    and evaluates permissions from other conduits or its parent.

    Available Policies:

    If system mode automatic is enabled the below policies are available:
    - automatic: 🔒 Disables linking from normal conduits.
                 ✅ Allows linking from lesser conduits only.
                 🔁 Delegates access resolution to the parent or source.


    If system mode dynamic is enabled the below policies are available:
    - dynamic: 🔓 Enables custom runtime evaluation and linking.
               🧠 Users may inject a handler function for access decisions.
               🎯 Required for advanced behaviors like selective linking.

    - whitelist_all: ✅ Grants access to all **local** spells in the conduit,
                     ⛔ Ignores spell-level `meta["whitelist"]` flags.
                     🔒 Only allowed when policy is `dynamic`.

    - block_all: ⛔ Denies all access by default.
                 ✅ Allows only spells explicitly marked with `meta["whitelist"] = True`.
                 📌 Applies only to **local** spells.
                 🔒 Only allowed when policy is `dynamic`.

    - delegate: 🔗 Forwards all access checks to another conduit.
                🪶 Used to create a special conduit that only has linking capability.
                📭 Can be created to contain no spells, only links to other conduits.
    """
    automatic = auto()
    dynamic = auto()
    whitelist_all = auto()
    block_all = auto()
    delegate = auto()
