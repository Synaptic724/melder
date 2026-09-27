from .provider import Dependency

class Consumer:
    def build(self) -> str:
        return Dependency().read()
