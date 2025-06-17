#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

from enum import Enum, auto

class SpellType(Enum):
    """
    Enum for different types of spells.
    """
    #Classes
    NORMAL = auto()
    NORMAL_INTERFACED = auto()
    NAMED = auto()
    NAMED_INTERFACED = auto()
    EXISTING_CLASS = auto()
    EXISTING_INTERFACED_CLASS = auto()

    #Methods
    NORMAL_METHOD = auto()
    NAMED_METHOD = auto()
    NAMED_LAMBDA_METHOD = auto()

    def __str__(self):
        return self.name