from domain.interfaces import JournalRepository, PartnerRepository
from domain.journal import JournalEntry
from domain.partner import Partner, PartnerType


class InMemoryPartnerRepository(PartnerRepository):
    def __init__(self) -> None:
        self._store: list[Partner] = []
        self._next_id = 1

    def add(self, partner: Partner) -> Partner:
        saved = partner.model_copy(update={"id": self._next_id})
        self._store.append(saved)
        self._next_id += 1
        return saved

    def get_by_id(self, partner_id: int) -> Partner | None:
        return next((p for p in self._store if p.id == partner_id), None)

    def list_all(self) -> list[Partner]:
        return list(self._store)

    def list_by_type(self, partner_type: PartnerType) -> list[Partner]:
        return [p for p in self._store if p.type == partner_type]


class InMemoryJournalRepository(JournalRepository):
    def __init__(self) -> None:
        self._store: list[JournalEntry] = []
        self._next_id = 1

    def add(self, entry: JournalEntry) -> JournalEntry:
        saved = entry.model_copy(update={"id": self._next_id})
        self._store.append(saved)
        self._next_id += 1
        return saved

    def list_all(self) -> list[JournalEntry]:
        return list(self._store)
