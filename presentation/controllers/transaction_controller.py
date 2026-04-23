from datetime import date
from decimal import Decimal

from application.commands import (
    PostBillCommand,
    PostCustomerPaymentCommand,
    PostInvoiceCommand,
    PostVendorPaymentCommand,
)
from application.use_cases import PostCustomerInvoice, PostCustomerPayment, PostVendorBill, PostVendorPayment
from domain.interfaces import JournalRepository, PartnerRepository
from domain.journal import DocumentType, JournalEntry
from presentation.base import BaseController


class TransactionController(BaseController):
    def __init__(self, journal_repo: JournalRepository, partner_repo: PartnerRepository) -> None:
        super().__init__(journal_repo, partner_repo)
        self._post_invoice = PostCustomerInvoice(journal_repo, partner_repo)
        self._post_bill = PostVendorBill(journal_repo, partner_repo)
        self._post_customer_payment = PostCustomerPayment(journal_repo, partner_repo)
        self._post_vendor_payment = PostVendorPayment(journal_repo, partner_repo)

    def post_invoice(self, partner_id: int, amount: Decimal, entry_date: date, description: str) -> JournalEntry:
        return self._post_invoice.execute(
            PostInvoiceCommand(
                partner_id=partner_id,
                amount=amount,
                date=entry_date,
                description=description,
            )
        )

    def post_bill(self, partner_id: int, amount: Decimal, entry_date: date, description: str) -> JournalEntry:
        return self._post_bill.execute(
            PostBillCommand(
                partner_id=partner_id,
                amount=amount,
                date=entry_date,
                description=description,
            )
        )

    def post_customer_payment(self, partner_id: int, amount: Decimal, entry_date: date, description: str) -> JournalEntry:
        return self._post_customer_payment.execute(
            PostCustomerPaymentCommand(
                partner_id=partner_id,
                amount=amount,
                date=entry_date,
                description=description,
            )
        )

    def post_vendor_payment(self, partner_id: int, amount: Decimal, entry_date: date, description: str) -> JournalEntry:
        return self._post_vendor_payment.execute(
            PostVendorPaymentCommand(
                partner_id=partner_id,
                amount=amount,
                date=entry_date,
                description=description,
            )
        )

    def list_invoices(self) -> list[JournalEntry]:
        return [e for e in self._journal_repo.list_all() if e.document_type == DocumentType.CUSTOMER_INVOICE]

    def list_bills(self) -> list[JournalEntry]:
        return [e for e in self._journal_repo.list_all() if e.document_type == DocumentType.VENDOR_BILL]
