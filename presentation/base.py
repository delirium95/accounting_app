from abc import ABC, abstractmethod

from domain.interfaces import JournalRepository, PartnerRepository


class BaseController(ABC):
    def __init__(self, journal_repo: JournalRepository, partner_repo: PartnerRepository) -> None:
        self._journal_repo = journal_repo
        self._partner_repo = partner_repo


class BaseView(ABC):
    @abstractmethod
    def render(self) -> None: ...
