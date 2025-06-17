#    Copyright [2025] [Mark Thomas Geleta]
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0

import uuid

#meld() = resolver
#conduit() = scope
#bind() = registration
#seal() = dispose
#
# prehooks, activation hooks, posthooks
# -------------------------
# object class for metadata pertaining to state creation
# i.e when a state creates an object we monkeypatch meld_state = meld_dataobject
#
# this would help extensively with debugging
#
# it would be an opt in feature
#
# we want to include scope UUID
# scope creation time
# object UUID
# object creation time
#---------------------------------
