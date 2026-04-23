from application.commands import AddPartnerCommand
from application.use_cases import AddPartner
from domain.interfaces import PartnerRepository
from domain.partner import Partner, PartnerType
from presentation.base import BaseController


class PartnerController(BaseController):
    def __init__(self, partner_repo: PartnerRepository) -> None:
        self._repo = partner_repo
        self._add_partner = AddPartner(partner_repo)

    def add(self, name: str, partner_type: str) -> Partner:
        return self._add_partner.execute(AddPartnerCommand(name=name, partner_type=partner_type))

    def list_all(self) -> list[Partner]:
        return self._repo.list_all()

    def list_customers(self) -> list[Partner]:
        return self._repo.list_by_type(PartnerType.CUSTOMER)

    def list_vendors(self) -> list[Partner]:
        return self._repo.list_by_type(PartnerType.VENDOR)
