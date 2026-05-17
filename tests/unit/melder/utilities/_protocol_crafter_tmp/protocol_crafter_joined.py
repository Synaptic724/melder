class Alpha:
    name: str
    def chain(self, enabled: bool = False) -> "Alpha":
        return self
class Beta:
    name: str
    def chain(self, enabled: bool = False) -> "Beta":
        return self
class Gamma:
    name: str
    def chain(self, enabled: bool = False) -> "Gamma":
        return self
