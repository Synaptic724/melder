from melder import Spellbook

class ExternalService:
    pass

class Worker:
    def __init__(self, service: ExternalService) -> None:
        self.service = service

book = Spellbook()
definition_id = book.bind(spell=ExternalService, existence="unique", resolvable=False)
book.bind(spell=Worker, existence="many")
conduit = book.conjure()
try:
    service = ExternalService()
    worker = conduit.meld(Worker, override={"service": service})
    assert worker.service is service
finally:
    conduit.permanent_cleanup()
