from abc import ABC, abstractmethod

from domain.journal import JournalEntry
from domain.partner import Partner, PartnerType


class PartnerRepository(ABC):
    @abstractmethod
    def add(self, partner: Partner) -> Partner: ...

    @abstractmethod
    def get_by_id(self, partner_id: int) -> Partner | None: ...

    @abstractmethod
    def list_all(self) -> list[Partner]: ...

    @abstractmethod
    def list_by_type(self, partner_type: PartnerType) -> list[Partner]: ...


class JournalRepository(ABC):
    @abstractmethod
    def add(self, entry: JournalEntry) -> JournalEntry: ...

    @abstractmethod
    def list_all(self) -> list[JournalEntry]: ...
