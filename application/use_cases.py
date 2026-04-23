from application.commands import (
    AddPartnerCommand,
    PostBillCommand,
    PostCustomerPaymentCommand,
    PostInvoiceCommand,
    PostVendorPaymentCommand,
)
from domain.exceptions import InvalidPartnerTypeError, PartnerNotFoundError
from domain.interfaces import JournalRepository, PartnerRepository
from domain.journal import JournalEntry
from domain.partner import Partner, PartnerType
from domain.posting import PostingRules


class AddPartner:
    def __init__(self, repo: PartnerRepository) -> None:
        self._repo = repo

    def execute(self, cmd: AddPartnerCommand) -> Partner:
        partner = Partner(id=None, name=cmd.name, type=PartnerType(cmd.partner_type))
        return self._repo.add(partner)


class PostCustomerInvoice:
    def __init__(self, journal_repo: JournalRepository, partner_repo: PartnerRepository) -> None:
        self._journal = journal_repo
        self._partners = partner_repo

    def execute(self, cmd: PostInvoiceCommand) -> JournalEntry:
        partner = self._partners.get_by_id(cmd.partner_id)
        if partner is None:
            raise PartnerNotFoundError(cmd.partner_id)
        if not partner.is_customer:
            raise InvalidPartnerTypeError(expected="customer", actual=partner.type.value)
        entry = PostingRules.customer_invoice(
            partner_id=cmd.partner_id,
            amount=cmd.amount,
            entry_date=cmd.date,
            description=cmd.description,
        )
        return self._journal.add(entry)


class PostCustomerPayment:
    def __init__(self, journal_repo: JournalRepository, partner_repo: PartnerRepository) -> None:
        self._journal = journal_repo
        self._partners = partner_repo

    def execute(self, cmd: PostCustomerPaymentCommand) -> JournalEntry:
        partner = self._partners.get_by_id(cmd.partner_id)
        if partner is None:
            raise PartnerNotFoundError(cmd.partner_id)
        if not partner.is_customer:
            raise InvalidPartnerTypeError(expected="customer", actual=partner.type.value)
        entry = PostingRules.customer_payment(
            partner_id=cmd.partner_id,
            amount=cmd.amount,
            entry_date=cmd.date,
            description=cmd.description,
        )
        return self._journal.add(entry)


class PostVendorBill:
    def __init__(self, journal_repo: JournalRepository, partner_repo: PartnerRepository) -> None:
        self._journal = journal_repo
        self._partners = partner_repo

    def execute(self, cmd: PostBillCommand) -> JournalEntry:
        partner = self._partners.get_by_id(cmd.partner_id)
        if partner is None:
            raise PartnerNotFoundError(cmd.partner_id)
        if not partner.is_vendor:
            raise InvalidPartnerTypeError(expected="vendor", actual=partner.type.value)
        entry = PostingRules.vendor_bill(
            partner_id=cmd.partner_id,
            amount=cmd.amount,
            entry_date=cmd.date,
            description=cmd.description,
        )
        return self._journal.add(entry)


class PostVendorPayment:
    def __init__(self, journal_repo: JournalRepository, partner_repo: PartnerRepository) -> None:
        self._journal = journal_repo
        self._partners = partner_repo

    def execute(self, cmd: PostVendorPaymentCommand) -> JournalEntry:
        partner = self._partners.get_by_id(cmd.partner_id)
        if partner is None:
            raise PartnerNotFoundError(cmd.partner_id)
        if not partner.is_vendor:
            raise InvalidPartnerTypeError(expected="vendor", actual=partner.type.value)
        entry = PostingRules.vendor_payment(
            partner_id=cmd.partner_id,
            amount=cmd.amount,
            entry_date=cmd.date,
            description=cmd.description,
        )
        return self._journal.add(entry)
