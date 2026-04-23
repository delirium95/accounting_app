from datetime import date
from decimal import Decimal

from domain.accounts import ACCOUNTS_PAYABLE, ACCOUNTS_RECEIVABLE, CASH, EXPENSE, REVENUE
from domain.posting import PostingRules


def test_customer_invoice_debits_ar_credits_revenue() -> None:
    entry = PostingRules.customer_invoice(
        partner_id=1, amount=Decimal("1000.00"), entry_date=date(2025, 1, 15), description="Invoice #1"
    )

    assert entry.is_balanced
    ar = next(l for l in entry.lines if l.account_code == ACCOUNTS_RECEIVABLE)
    rev = next(l for l in entry.lines if l.account_code == REVENUE)
    assert ar.debit == Decimal("1000.00")
    assert ar.credit == Decimal(0)
    assert rev.credit == Decimal("1000.00")
    assert rev.debit == Decimal(0)


def test_customer_payment_debits_cash_credits_ar() -> None:
    entry = PostingRules.customer_payment(
        partner_id=1, amount=Decimal("500.00"), entry_date=date(2025, 1, 20), description="Payment from Acme"
    )

    assert entry.is_balanced
    cash = next(l for l in entry.lines if l.account_code == CASH)
    ar = next(l for l in entry.lines if l.account_code == ACCOUNTS_RECEIVABLE)
    assert cash.debit == Decimal("500.00")
    assert ar.credit == Decimal("500.00")


def test_vendor_bill_debits_expense_credits_ap() -> None:
    entry = PostingRules.vendor_bill(
        partner_id=2, amount=Decimal("200.00"), entry_date=date(2025, 1, 10), description="Office supplies"
    )

    assert entry.is_balanced
    exp = next(l for l in entry.lines if l.account_code == EXPENSE)
    ap = next(l for l in entry.lines if l.account_code == ACCOUNTS_PAYABLE)
    assert exp.debit == Decimal("200.00")
    assert ap.credit == Decimal("200.00")


def test_vendor_payment_debits_ap_credits_cash() -> None:
    entry = PostingRules.vendor_payment(
        partner_id=2, amount=Decimal("200.00"), entry_date=date(2025, 1, 25), description="Pay supplier"
    )

    assert entry.is_balanced
    ap = next(l for l in entry.lines if l.account_code == ACCOUNTS_PAYABLE)
    cash = next(l for l in entry.lines if l.account_code == CASH)
    assert ap.debit == Decimal("200.00")
    assert cash.credit == Decimal("200.00")


def test_all_entries_carry_partner_id_on_partner_account() -> None:
    invoice = PostingRules.customer_invoice(
        partner_id=7, amount=Decimal("300"), entry_date=date(2025, 2, 1), description="Test"
    )
    ar_line = next(l for l in invoice.lines if l.account_code == ACCOUNTS_RECEIVABLE)
    assert ar_line.partner_id == 7
