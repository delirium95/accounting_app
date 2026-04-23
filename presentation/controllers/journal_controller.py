from domain.interfaces import JournalRepository, PartnerRepository
from domain.journal import JournalEntry
from presentation.base import BaseController


class JournalController(BaseController):
    def __init__(self, journal_repo: JournalRepository, partner_repo: PartnerRepository) -> None:
        self._journal_repo = journal_repo
        self._partner_repo = partner_repo

    def list_entries(self) -> list[JournalEntry]:
        return self._journal_repo.list_all()

    def partner_map(self) -> dict[int, str]:
        return {p.id: p.name for p in self._partner_repo.list_all()}
