#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

from enum import Enum, auto

class Existence(Enum):
    """
    Enum representing the existence/lifecycle pattern of a service in Melder.
    """
    unique = auto()               # Single instance across all of Aether
    unique_per_conduit = auto()    # One instance per conduit
    many = auto()                  # New instance every time
    unique_per_conduit_cluster = auto()  # One instance per conduit cluster, users can cluster conduits into their own desired groups owned by the aether
    unique_per_conduit_lineage = auto()  # One instance per conduit lineage, a lineage is a tree of conduits from child to parent

    # Spell spaces are locations or a boundry created by a conduit for a quick scope, these boundrys are semaphored zones where spells can be cast, specifically just the initations and resets are locked otherwise its
    # location where can quickly cast spells without having to worry about the state of the conduit, this is useful for spells that need to be cast in a specific location or context and fast disposals
    unique_per_spell_space = auto()  # One instance per spell space, a spell space is a boundry where spells can be cast, "create spell space, close spell space" is a common pattern
    unique_per_spell_space_refresh = auto()  # One instance per spell space, but reset on each spell space reset, this is useful for spells that need to be re-initialized on each spell space reset

    def __str__(self):
        return self.name
