from domain.interfaces import JournalRepository, PartnerRepository
from domain.journal import JournalEntry
from domain.partner import Partner
from presentation.base import BaseController


class JournalController(BaseController):
    def list_entries(self) -> list[JournalEntry]:
        return self._journal_repo.list_all()

    def partner_map(self) -> dict[int, str]:
        return {p.id: p.name for p in self._partner_repo.list_all()}
