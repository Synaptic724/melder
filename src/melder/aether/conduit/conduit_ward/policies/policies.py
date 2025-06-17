#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

from enum import Enum, auto

class Policies(Enum):
    """
    Defines conduit policy behaviors within the conduit ward system.

    These policies control how a conduit grants spell access, inherits behavior,
    and evaluates permissions.

    Available Policies:

    If system mode is 'automatic':
    - automatic: 🔒 Disables outbound linking.
                 ✅ Accepts inbound links from lesser conduits only.
                 🔁 Defers access decisions to static whitelist metadata.

    If system mode is 'dynamic':
    - dynamic: 🔓 Enables runtime access evaluation and linking.
               🧠 Supports dynamic permission handlers and spell-level logic.

    - whitelist_all: ✅ Grants access to all local spells.
                     ⛔ Ignores `meta["whitelist"]` flags.
                     🔒 Dynamic mode only.

    - block_all: ⛔ Denies all access by default.
                 ✅ Only allows spells explicitly marked with `meta["whitelist"] = True`.
                 🔒 Dynamic mode only.

    - lesser_conduit: 🪶 Applies to delegated lesser conduits.
                      🔗 Does not evaluate policies; inherits access from parent structure.
                      🚫 Cannot link or modify spellbook.
                      🧼 Used as a passive scope only.
    """
    automatic = auto()
    dynamic = auto()
    whitelist_all = auto()
    block_all = auto()
    lesser_conduit = auto()
