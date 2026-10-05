# commandops shapes, live (VM, 3.14t GIL off) - run 1 (2026-09-27T22:57Z)

| root (commandops shape) | specializer | ns/meld by name | py | C |
| --- | --- | ---: | ---: | ---: |
| Worker | off | 853 | 6 | 10 |
| WorkerNoDisposal | off | 251 | 4 | 2 |
| ContextRoot | off | 1219 | 6 | 14 |
| ContextRootNoDisposal | off | 531 | 4 | 6 |
| Spectrum (unique, warm) | off | 164 | | |
| Config (existing object) | off | 141 | | |
| Worker | on | 844 | 6 | 9 |
| WorkerNoDisposal | on | 277 | 4 | 1 |
| ContextRoot | on | 1124 | 6 | 9 |
| ContextRootNoDisposal | on | 676 | 4 | 1 |
| Spectrum (unique, warm) | on | 172 | | |
| Config (existing object) | on | 136 | | |

# run 2 (2026-09-27T23:35Z, same script after the typing pass; VM noise is +-20% between runs)

| root (commandops shape) | specializer | ns/meld by name | py | C |
| --- | --- | ---: | ---: | ---: |
| Worker | off | 650 | 6 | 10 |
| WorkerNoDisposal | off | 247 | 4 | 2 |
| ContextRoot | off | 1175 | 6 | 14 |
| ContextRootNoDisposal | off | 534 | 4 | 6 |
| Spectrum (unique, warm) | off | 171 | | |
| Config (existing object) | off | 141 | | |
| Worker | on | 646 | 6 | 9 |
| WorkerNoDisposal | on | 239 | 4 | 1 |
| ContextRoot | on | 977 | 6 | 9 |
| ContextRootNoDisposal | on | 642 | 4 | 1 |
| Spectrum (unique, warm) | on | 180 | | |
| Config (existing object) | on | 149 | | |
