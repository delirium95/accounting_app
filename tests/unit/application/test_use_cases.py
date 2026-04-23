from datetime import date
from decimal import Decimal

import pytest

from application.commands import (
    AddPartnerCommand,
    PostBillCommand,
    PostCustomerPaymentCommand,
    PostInvoiceCommand,
    PostVendorPaymentCommand,
)
from application.use_cases import (
    AddPartner,
    PostCustomerInvoice,
    PostCustomerPayment,
    PostVendorBill,
    PostVendorPayment,
)
from domain.accounts import ACCOUNTS_RECEIVABLE
from domain.partner import PartnerType
from tests.fakes.repositories import InMemoryJournalRepository, InMemoryPartnerRepository


def _repos() -> tuple[InMemoryJournalRepository, InMemoryPartnerRepository]:
    return InMemoryJournalRepository(), InMemoryPartnerRepository()


def _add_customer(partner_repo: InMemoryPartnerRepository, name: str = "Acme Corp"):
    return AddPartner(partner_repo).execute(AddPartnerCommand(name=name, partner_type="customer"))


def _add_vendor(partner_repo: InMemoryPartnerRepository, name: str = "OfficeMax"):
    return AddPartner(partner_repo).execute(AddPartnerCommand(name=name, partner_type="vendor"))


# --- AddPartner ---

def test_add_customer_assigns_id() -> None:
    _, partner_repo = _repos()
    partner = AddPartner(partner_repo).execute(AddPartnerCommand(name="Acme", partner_type="customer"))
    assert partner.id is not None
    assert partner.is_customer


def test_add_vendor_assigns_id() -> None:
    _, partner_repo = _repos()
    partner = AddPartner(partner_repo).execute(AddPartnerCommand(name="OfficeMax", partner_type="vendor"))
    assert partner.id is not None
    assert partner.is_vendor


def test_add_partner_empty_name_raises() -> None:
    with pytest.raises(Exception):
        AddPartnerCommand(name="  ", partner_type="customer")


# --- PostCustomerInvoice ---

def test_post_invoice_creates_balanced_entry() -> None:
    journal_repo, partner_repo = _repos()
    customer = _add_customer(partner_repo)

    entry = PostCustomerInvoice(journal_repo, partner_repo).execute(
        PostInvoiceCommand(partner_id=customer.id, amount=Decimal("1500.00"), date=date(2025, 3, 1), description="Inv #1")
    )

    assert entry.is_balanced
    assert entry.id is not None


def test_post_invoice_rejects_vendor_partner() -> None:
    journal_repo, partner_repo = _repos()
    vendor = _add_vendor(partner_repo)

    with pytest.raises(ValueError, match="customer"):
        PostCustomerInvoice(journal_repo, partner_repo).execute(
            PostInvoiceCommand(partner_id=vendor.id, amount=Decimal("100"), date=date(2025, 3, 1), description="Bad")
        )


def test_post_invoice_rejects_unknown_partner() -> None:
    journal_repo, partner_repo = _repos()
    with pytest.raises(ValueError, match="not found"):
        PostCustomerInvoice(journal_repo, partner_repo).execute(
            PostInvoiceCommand(partner_id=999, amount=Decimal("100"), date=date(2025, 3, 1), description="Bad")
        )


def test_post_invoice_rejects_zero_amount() -> None:
    with pytest.raises(Exception):
        PostInvoiceCommand(partner_id=1, amount=Decimal("0"), date=date(2025, 3, 1), description="Bad")


# --- PostCustomerPayment ---

def test_post_customer_payment_reduces_ar() -> None:
    journal_repo, partner_repo = _repos()
    customer = _add_customer(partner_repo)

    PostCustomerInvoice(journal_repo, partner_repo).execute(
        PostInvoiceCommand(partner_id=customer.id, amount=Decimal("1000"), date=date(2025, 3, 1), description="Inv")
    )
    PostCustomerPayment(journal_repo, partner_repo).execute(
        PostCustomerPaymentCommand(partner_id=customer.id, amount=Decimal("600"), date=date(2025, 3, 10), description="Pmt")
    )

    entries = journal_repo.list_all()
    ar_debit = sum(l.debit for e in entries for l in e.lines if l.account_code == ACCOUNTS_RECEIVABLE)
    ar_credit = sum(l.credit for e in entries for l in e.lines if l.account_code == ACCOUNTS_RECEIVABLE)
    assert ar_debit - ar_credit == Decimal("400")


# --- PostVendorBill ---

def test_post_bill_creates_balanced_entry() -> None:
    journal_repo, partner_repo = _repos()
    vendor = _add_vendor(partner_repo)

    entry = PostVendorBill(journal_repo, partner_repo).execute(
        PostBillCommand(partner_id=vendor.id, amount=Decimal("250.00"), date=date(2025, 3, 5), description="Supplies")
    )

    assert entry.is_balanced
    assert entry.id is not None


def test_post_bill_rejects_customer_partner() -> None:
    journal_repo, partner_repo = _repos()
    customer = _add_customer(partner_repo)

    with pytest.raises(ValueError, match="vendor"):
        PostVendorBill(journal_repo, partner_repo).execute(
            PostBillCommand(partner_id=customer.id, amount=Decimal("100"), date=date(2025, 3, 5), description="Bad")
        )


# --- PostVendorPayment ---

def test_post_vendor_payment_creates_balanced_entry() -> None:
    journal_repo, partner_repo = _repos()
    vendor = _add_vendor(partner_repo)

    PostVendorBill(journal_repo, partner_repo).execute(
        PostBillCommand(partner_id=vendor.id, amount=Decimal("300"), date=date(2025, 3, 5), description="Bill")
    )
    entry = PostVendorPayment(journal_repo, partner_repo).execute(
        PostVendorPaymentCommand(partner_id=vendor.id, amount=Decimal("300"), date=date(2025, 3, 15), description="Paid")
    )

    assert entry.is_balanced


# --- Reports (basic smoke via in-memory) ---

def test_pnl_reflects_posted_invoices_and_bills() -> None:
    from application.reports import PnLQuery
    journal_repo, partner_repo = _repos()
    customer = _add_customer(partner_repo)
    vendor = _add_vendor(partner_repo)

    PostCustomerInvoice(journal_repo, partner_repo).execute(
        PostInvoiceCommand(partner_id=customer.id, amount=Decimal("2000"), date=date(2025, 3, 1), description="Inv")
    )
    PostVendorBill(journal_repo, partner_repo).execute(
        PostBillCommand(partner_id=vendor.id, amount=Decimal("500"), date=date(2025, 3, 5), description="Bill")
    )

    report = PnLQuery(journal_repo).execute()
    assert report.revenue == Decimal("2000")
    assert report.expenses == Decimal("500")
    assert report.net_income == Decimal("1500")


def test_partner_balances_reflect_invoices_and_payments() -> None:
    from application.reports import PartnerLedgerQuery
    journal_repo, partner_repo = _repos()
    customer = _add_customer(partner_repo)

    PostCustomerInvoice(journal_repo, partner_repo).execute(
        PostInvoiceCommand(partner_id=customer.id, amount=Decimal("1000"), date=date(2025, 3, 1), description="Inv")
    )
    PostCustomerPayment(journal_repo, partner_repo).execute(
        PostCustomerPaymentCommand(partner_id=customer.id, amount=Decimal("400"), date=date(2025, 3, 10), description="Pmt")
    )

    balances = PartnerLedgerQuery(journal_repo, partner_repo).balances()
    customer_balance = next(b for b in balances if b.partner_id == customer.id)
    assert customer_balance.balance == Decimal("600")
