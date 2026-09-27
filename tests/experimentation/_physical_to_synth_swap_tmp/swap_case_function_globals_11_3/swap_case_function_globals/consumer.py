from .provider import Dependency

def build() -> str:
    return Dependency().read()
